#
# python-bluetooth-mesh - Bluetooth Mesh for Python
#
# Copyright (C) 2019  SILVAIR sp. z o.o.
#
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
#
import bitstring
import enum
import itertools
import math
import operator

from cryptography.exceptions import InvalidTag
from bluetooth_mesh.crypto import aes_cmac, aes_ccm, aes_ecb, ApplicationKey


class BeaconType(enum.Enum):
    UNPROVISIONED_DEVICE = 0x00
    SECURE_NETWORK = 0x01


class SecureNetworkBeacon:
    BEACON_FORMAT = 'pad:6, uint:1, uint:1, bytes:8, uintbe:32'
    BEACON_AUTH_SIZE = 8

    def __init__(self, key_refresh, iv_update, iv_index, network_id):
        self.key_refresh = key_refresh
        self.iv_update = iv_update
        self.iv_index = iv_index
        self.network_id = network_id

    def __str__(self):
        return '<%s: key_refresh=%s, iv_update=%s, ivindex=%d, network_id=%s>' % (
                type(self).__name__,
                self.key_refresh,
                self.iv_update,
                self.iv_index,
                self.network_id.hex())

    def pack(self):
        return self.message + self.auth

    @classmethod
    def unpack(cls, message):
        beacon, auth = message[:-cls.BEACON_AUTH_SIZE], message[-cls.BEACON_AUTH_SIZE:]

        iv_update, key_refresh, network_id, iv_index = \
            bitstring.BitString(beacon).unpack(cls.BEACON_FORMAT)

        return cls(bool(key_refresh),
                   bool(iv_update),
                   iv_index,
                   network_id), auth

    def pack(self, network_key):
        beacon = bitstring.pack(self.BEACON_FORMAT,
                                self.iv_update,
                                self.key_refresh,
                                self.network_id,
                                self.iv_index).bytes
        auth = aes_cmac(network_key.beacon_key, beacon)[:self.BEACON_AUTH_SIZE]
        return beacon, auth

    def verify(self, auth, network_key):
        beacon, _auth = self.pack(network_key)
        return auth == _auth


class Nonce:
    def __init__(self, src, dst, ttl, ctl):
        super().__init__()
        self.src = src
        self.dst = dst
        self.ttl = ttl
        self.ctl = ctl

    def network(self, seq, iv_index):
        return bitstring.pack('uint:8, uint:1, uint:7, uintbe:24, uintbe:16, pad:16, uintbe:32',
                              0x00, self.ctl, self.ttl, seq, self.src, iv_index).bytes

    def application(self, seq, iv_index, szmic=False):
        return bitstring.pack('uint:8, uint:1, pad:7, uintbe:24, uintbe:16, uintbe:16, uintbe:32',
                              0x01, szmic, seq, self.src, self.dst, iv_index).bytes

    def device(self, seq, iv_index, szmic=False):
        return bitstring.pack('uint:8, uint:1, pad:7, uintbe:24, uintbe:16, uintbe:16, uintbe:32',
                              0x02, szmic, seq, self.src, self.dst, iv_index).bytes


class Segment:
    MAX_TRANSPORT_PDU = 15
    SEGMENT_SIZE = 12

    def __init__(self, src, dst, ttl, ctl, payload):
        self.src = src
        self.dst = dst
        self.ttl = ttl
        self.ctl = ctl
        self.payload = payload
        self.nonce = Nonce(self.src, self.dst, self.ttl, self.ctl)

    def get_opcode(self, application_key):
        raise NotImplementedError

    def segments(self, application_key, seq, iv_index, payload):
        opcode = self.get_opcode(application_key)
        seq_zero = seq & 0x1fff
        seg = len(payload) > self.MAX_TRANSPORT_PDU

        if seg:
            segments = list(payload[i:i + self.SEGMENT_SIZE]
                            for i in range(0, len(payload), self.SEGMENT_SIZE))

            seg_n = len(segments) - 1

            for seg_o, segment in enumerate(segments):
                yield bitstring.pack('uint:1, bits:7, pad:1, uint:13, uint:5, uint:5, bytes',
                                     seg, opcode, seq_zero, seg_o, seg_n, segment).bytes
        else:
            yield bitstring.pack('uint:1, bits:7, bytes',
                                 seg, opcode, payload).bytes


class AccessMessage(Segment):
    def __init__(self, src, dst, ttl, payload):
        super().__init__(src, dst, ttl, False, payload)

    def get_opcode(self, application_key):
        akf = isinstance(application_key, ApplicationKey)
        aid = application_key.aid
        return bitstring.pack('uint:1, uint:6', akf, aid)

    def segments(self, application_key, seq, iv_index, szmic=False):
        short_mic_len = len(self.payload) + 4
        long_mic_len = len(self.payload) + 8

        # Use large MIC if it doesn't affect segmentation
        if len(self.payload) >= self.SEGMENT_SIZE and len(self.payload) < 376:
            szmic = szmic or (math.ceil(short_mic_len / self.SEGMENT_SIZE) ==
                              math.ceil(long_mic_len / self.SEGMENT_SIZE))

        akf = isinstance(application_key, ApplicationKey)
        nonce = (self.nonce.application if akf else self.nonce.device)(seq, iv_index, szmic)

        upper_transport_pdu = aes_ccm(application_key.bytes, nonce,
                                      self.payload, b'', 8 if szmic else 4)

        yield from super().segments(application_key, seq, iv_index, payload=upper_transport_pdu)


class ControlMessage(Segment):
    def __init__(self, src, dst, ttl, opcode, payload):
        super().__init__(src, dst, ttl, True, payload)
        self.payload = payload
        self.opcode = opcode

    def get_opcode(self, application_key):
        return bitstring.pack('uint:7', self.opcode)

    def segments(self, application_key, seq, iv_index, szmic=False):
        yield from super().segments(application_key, seq, iv_index, payload=self.payload)


class SegmentAckMessage(ControlMessage):
    def __init__(self, src, dst, ttl, seq_zero, ack_segments, obo=False):
        self.obo = obo
        self.seq_zero = seq_zero
        self.block_ack = bitstring.BitArray(i in ack_segments for i in range(32))

        self.payload = bitstring.pack('uint:1, uint:13, pad:2, bits:32',
                                      self.obo, self.seq_zero,
                                      reversed(self.block_ack)).bytes

        super().__init__(src, dst, ttl, 0x00, self.payload)


class NetworkMessage:
    def __init__(self, message):
        self.message = message

    def pack(self, application_key, network_key, seq, iv_index, *, transport_seq=None):
        nid, encryption_key, privacy_key = network_key.encryption_keys

        # when retrying a segment, use the original sequence number during application
        # encryption, but a newer one on network lever
        if transport_seq is None:
            transport_seq = seq

        for seq, pdu in enumerate(self.message.segments(application_key, transport_seq, iv_index),
                                  start=seq):
            network_pdu = aes_ccm(encryption_key,
                                  self.message.nonce.network(seq, iv_index),
                                  bitstring.pack('uintbe:16, bytes', self.message.dst, pdu).bytes,
                                  b'', 8 if self.message.ctl else 4)

            network_header = bitstring.pack('uint:1, uint:7, uintbe:24, uintbe:16',
                                            self.message.ctl, self.message.ttl, seq,
                                            self.message.src).bytes

            privacy_random = bitstring.pack('pad:40, uintbe:32, bytes:7',
                                            iv_index, network_pdu[:7]).bytes

            pecb = aes_ecb(privacy_key, privacy_random)[:6]

            obfuscated_header = bytes(map(operator.xor, network_header, pecb))

            yield seq, bitstring.pack('uint:1, uint:7, bits, bytes',
                                      iv_index & 1, nid, obfuscated_header, network_pdu).bytes

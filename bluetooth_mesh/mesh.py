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
import operator

from cryptography.exceptions import InvalidTag
from bluetooth_mesh.crypto import aes_cmac, aes_ccm, aes_ccm_decrypt, aes_ecb, ApplicationKey


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


class AccessMessage:
    MAX_TRANSPORT_PDU = 15
    SEGMENT_SIZE = 12

    def __init__(self, src, dst, ttl, payload):
        self.src = src
        self.dst = dst
        self.ttl = ttl
        self.ctl = False
        self.payload = payload

        self.nonce = Nonce(self.src, self.dst, self.ttl, self.ctl)

        self._reassembly = self.__reassembly()
        next(self._reassembly)

    def transport_pdu(self, application_key, seq, iv_index):
        akf = isinstance(application_key, ApplicationKey)
        aid = application_key.aid

        nonce = Nonce(self.src, self.dst, self.ttl, self.ctl)
        nonce = (nonce.application if akf else nonce.device)(seq, iv_index)

        upper_transport_pdu = aes_ccm(application_key.bytes,
                                      nonce,
                                      self.payload)

        seg = len(upper_transport_pdu) > self.MAX_TRANSPORT_PDU

        if seg:
            segments = list(upper_transport_pdu[i:i + self.SEGMENT_SIZE]
                            for i in range(0, len(upper_transport_pdu), self.SEGMENT_SIZE))

            seq_zero = seq & 0x1fff
            seg_n = len(segments) - 1

            for seg_o, segment in enumerate(segments):
                yield seq + seg_o, bitstring.pack('uint:1, uint:1, uint:6, uint:1, uint:13, uint:5, uint:5, bytes',
                                                  seg, akf, aid, False, seq_zero, seg_o, seg_n, segment).bytes
        else:
            yield seq, bitstring.pack('uint:1, uint:1, uint:6, bytes',
                                      seg, akf, aid, upper_transport_pdu).bytes

    def __reassembly(self):
        buf = []
        segment = yield
        while True:
            try:
                szmic, seq_zero, seq_o, seq_n, segment = bitstring.BitString(segment).unpack('uint:1, uint:13, uint:5, uint:5, bytes')
            except ValueError:
                segment = yield None, None, None
                continue

            if seq_o == seq_n:
                buf[seq_o*12:] = segment
                segment = yield szmic, seq_zero, buf[:seq_n * 12 + len(segment) - 4]
            elif seq_o > seq_n:
                segment = yield None, None, None
            else:
                buf[seq_o*12:] = segment
                segment = yield None, None, None
                
    def unpack(self, seq, iv_index, payload, app_keys):
        seg, akf, aid = bitstring.BitString(payload).unpack('uint:1, uint:1, uint:6')
        if akf:
            if seg:
                szmic, seq_zero, packet = self._reassembly.send(payload)
                if not packet:
                    return
            else:
                szmic = 0

            keys = [key for key in app_keys if key.aid == aid]
            if keys:
                app_key = app_keys[0]
                nonce = self.nonce.application(seq, iv_index, szmic)
                try:
                    decrypted = aes_ccm_decrypt(app_key.bytes, nonce, payload[1:], tag_length=8 if szmic else 4)
                    return decrypted
                except InvalidTag:
                    return -1



class NetworkMessage:
    PDU_FORMAT = 'pad:6, uint:1, uint:1, bytes:8, uintbe:32'

    def __init__(self, message):
        self.message = message

    def pack(self, application_key, network_key, seq, iv_index):
        nid, encryption_key, privacy_key = network_key.encryption_keys

        for seq, pdu in self.message.transport_pdu(application_key, seq, iv_index):
            network_pdu = aes_ccm(encryption_key,
                                  self.message.nonce.network(seq, iv_index),
                                  bitstring.pack('uintbe:16, bytes', self.message.dst, pdu).bytes)

            network_header = bitstring.pack('uint:1, uint:7, uintbe:24, uintbe:16',
                                            self.message.ctl, self.message.ttl, seq, self.message.src).bytes

            privacy_random = bitstring.pack('pad:40, uintbe:32, bytes:7',
                                            iv_index, network_pdu[:7]).bytes

            pecb = aes_ecb(privacy_key, privacy_random)[:6]

            obfuscated_header = bytes(map(operator.xor, network_header, pecb))

            yield seq, bitstring.pack('uint:1, uint:7, bits, bytes',
                                      iv_index & 1, nid, obfuscated_header, network_pdu).bytes

    @classmethod
    def unpack(cls, payload, network_keys, local_iv_index):     
        ivi, nid = bitstring.BitString(payload).unpack('uint:1, uint:7')
        keys = [key.encryption_keys for key in network_keys if key.encryption_keys[0] == nid]
        if keys:
            _, encryption_key, privacy_key = keys[0]
            obfuscated = payload[1:7]
            iv_index = local_iv_index if ivi == 0 else local_iv_index - 1
            privacy_plain = bitstring.pack('pad:40, uintbe:32, bytes:7',
                                            iv_index, payload[7:14]).bytes
            pecb = aes_ecb(privacy_key, privacy_plain)[:6]
            deobfuscated = bytes(map(operator.xor, obfuscated, pecb))
            ctl, ttl, seq, src = bitstring.BitString(deobfuscated).unpack('uint:1, uint:7, uintbe:24, uintbe:16')
            net_mic_len = 4 if ctl == 0 else 8
            net_mic, encrypted = payload[-net_mic_len:], payload[7:-net_mic_len]
            nonce = Nonce(src, 0, ttl, ctl)
            try:
                encrypted = aes_ccm_decrypt(encryption_key,
                                        nonce.network(seq, iv_index),
                                        payload[7:],
                                        tag_length=net_mic_len)
            except InvalidTag:
                return
            dst, transport_pdu = bitstring.BitString(encrypted).unpack('uintbe:16, bytes')
            return iv_index, ctl, ttl, seq, src, dst, transport_pdu
        pass
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
import enum
import math
import operator
from uuid import UUID

import bitstring
from crc.crc import Configuration, CrcCalculator

from bluetooth_mesh.crypto import (
    ApplicationKey,
    NetworkKey,
    aes_ccm_decrypt,
    aes_ccm_encrypt,
    aes_cmac,
    aes_ecb,
)
from bluetooth_mesh.provisioning import (
    BearerOpcode,
    ProvisioningBearerControl,
    ProvisioningPDU,
    ProvisioningPDUType,
    TransactionContinuationPDU,
    TransactionPDUSegment,
    TransactionStartPDU,
)


class BeaconType(enum.Enum):
    UNPROVISIONED_DEVICE = 0x00
    SECURE_NETWORK = 0x01


class UnprovisionedDeviceBeacon:
    BEACON_FORMAT = "bytes:16, uint:16, bytes"

    def __init__(self, uuid, oob, uri_hash=None):
        self.uuid = uuid
        self.oob = oob

        if uri_hash and len(uri_hash) != 4:
            raise ValueError("Wrong size of URI hash, expected 4 bytes")

        self.uri_hash = uri_hash

    def __str__(self):
        return "<%s: uuid=%s, oob=%x, uri_hash=%s>" % (
            type(self).__name__,
            self.uuid,
            self.oob,
            self.uri_hash,
        )

    @classmethod
    def unpack(cls, beacon):
        uuid, oob, uri_hash = bitstring.BitString(beacon).unpack(cls.BEACON_FORMAT)

        if uri_hash and len(uri_hash) != 4:
            raise ValueError("Wrong size of URI hash, expected 4 bytes")

        return cls(UUID(bytes=uuid), oob, uri_hash or None)

    def pack(self):
        beacon = bitstring.pack(
            self.BEACON_FORMAT, self.uuid.bytes, self.oob, self.uri_hash or b""
        ).bytes
        return beacon


class SecureNetworkBeacon:
    BEACON_FORMAT = "pad:6, uint:1, uint:1, bytes:8, uintbe:32"
    BEACON_AUTH_SIZE = 8

    def __init__(self, key_refresh, iv_update, iv_index, network_id):
        self.key_refresh = key_refresh
        self.iv_update = iv_update
        self.iv_index = iv_index
        self.network_id = network_id

    def __str__(self):
        return "<%s: key_refresh=%s, iv_update=%s, ivindex=%d, network_id=%s>" % (
            type(self).__name__,
            self.key_refresh,
            self.iv_update,
            self.iv_index,
            self.network_id.hex(),
        )

    @classmethod
    def unpack(cls, message):
        beacon, auth = (
            message[: -cls.BEACON_AUTH_SIZE],
            message[-cls.BEACON_AUTH_SIZE :],
        )

        iv_update, key_refresh, network_id, iv_index = bitstring.BitString(
            beacon
        ).unpack(cls.BEACON_FORMAT)

        return cls(bool(key_refresh), bool(iv_update), iv_index, network_id), auth

    def pack(self, network_key):
        beacon = bitstring.pack(
            self.BEACON_FORMAT,
            self.iv_update,
            self.key_refresh,
            self.network_id,
            self.iv_index,
        ).bytes
        auth = aes_cmac(network_key.beacon_key, beacon)[: self.BEACON_AUTH_SIZE]
        return beacon, auth

    def verify(self, auth, network_key):
        _, _auth = self.pack(network_key)
        return auth == _auth


class Nonce:
    def __init__(self, src, dst, ttl, ctl):
        super().__init__()
        self.src = src
        self.dst = dst
        self.ttl = ttl
        self.ctl = ctl

    def network(self, seq, iv_index):
        return bitstring.pack(
            "uint:8, uint:1, uint:7, uintbe:24, uintbe:16, pad:16, uintbe:32",
            0x00,
            self.ctl,
            self.ttl,
            seq,
            self.src,
            iv_index,
        ).bytes

    def application(self, seq, iv_index, szmic=False):
        return bitstring.pack(
            "uint:8, uint:1, pad:7, uintbe:24, uintbe:16, uintbe:16, uintbe:32",
            0x01,
            szmic,
            seq,
            self.src,
            self.dst,
            iv_index,
        ).bytes

    def device(self, seq, iv_index, szmic=False):
        return bitstring.pack(
            "uint:8, uint:1, pad:7, uintbe:24, uintbe:16, uintbe:16, uintbe:32",
            0x02,
            szmic,
            seq,
            self.src,
            self.dst,
            iv_index,
        ).bytes

    def proxy(self, seq, iv_index):
        return bitstring.pack(
            "uint:8, pad:8, uintbe:24, uintbe:16, uintbe:16, uintbe:32",
            0x03,
            seq,
            self.src,
            self.dst,
            iv_index,
        ).bytes

    def solicitation(self, seq):
        return bitstring.pack(
            "uint:8, pad:8, uintbe:24, uintbe:16, pad:16, uintbe:32",
            0x04,
            seq,
            self.src,
            0,
        ).bytes


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

    def __eq__(self, other):
        if not isinstance(other, Segment):
            raise NotImplementedError
        return (
            self.src == other.src
            and self.dst == other.dst
            and self.ttl == other.ttl
            and self.ctl == other.ctl
            and self.payload == other.payload
        )

    def get_opcode(self, application_key):
        raise NotImplementedError

    def _segments(self, application_key, seq, payload, szmic, seg):
        opcode = self.get_opcode(application_key)
        seq_zero = seq & 0x1FFF
        seg = seg or len(payload) > self.MAX_TRANSPORT_PDU

        if seg:
            segments = list(
                payload[i : i + self.SEGMENT_SIZE]
                for i in range(0, len(payload), self.SEGMENT_SIZE)
            )

            seg_n = len(segments) - 1

            for seg_o, segment in enumerate(segments):
                yield bitstring.pack(
                    "uint:1, bits:7, uint:1, uint:13, uint:5, uint:5, bytes",
                    seg,
                    opcode,
                    szmic,
                    seq_zero,
                    seg_o,
                    seg_n,
                    segment,
                ).bytes
        else:
            yield bitstring.pack("uint:1, bits:7, bytes", seg, opcode, payload).bytes


class AccessMessage(Segment):
    def __init__(self, src, dst, ttl, payload):
        super().__init__(src, dst, ttl, False, payload)

    def get_opcode(self, application_key):
        akf = isinstance(application_key, ApplicationKey)
        aid = application_key.aid
        return bitstring.pack("uint:1, uint:6", akf, aid)

    def segments(self, application_key, seq, iv_index, szmic=False, seg=False):
        short_mic_len = len(self.payload) + 4
        long_mic_len = len(self.payload) + 8

        # Use large MIC if it doesn't affect segmentation
        if len(self.payload) >= self.SEGMENT_SIZE and len(self.payload) < 376:
            szmic = szmic or (
                math.ceil(short_mic_len / self.SEGMENT_SIZE)
                == math.ceil(long_mic_len / self.SEGMENT_SIZE)
            )

        akf = isinstance(application_key, ApplicationKey)
        nonce = (self.nonce.application if akf else self.nonce.device)(
            seq, iv_index, szmic
        )

        upper_transport_pdu = aes_ccm_encrypt(
            application_key.bytes, nonce, self.payload, b"", 8 if szmic else 4
        )

        yield from super()._segments(
            application_key,
            seq,
            payload=upper_transport_pdu,
            szmic=szmic,
            seg=seg,
        )

    @classmethod
    def decrypt(cls, app_key, iv_index, ctl, ttl, seq, src, dst, transport_pdu):
        seg, akf, aid = bitstring.BitString(transport_pdu).unpack(
            "uint:1, uint:1, uint:6"
        )

        # works only for unsegmented messages!
        if seg:
            raise NotImplementedError
        if app_key.aid != aid:
            raise KeyError
        transport_nonce = Nonce(src, dst, ttl, ctl)
        nonce = (transport_nonce.application if akf else transport_nonce.device)(
            seq, iv_index
        )
        decrypted_access = aes_ccm_decrypt(app_key.bytes, nonce, transport_pdu[1:])
        return AccessMessage(src, dst, ttl, decrypted_access)


class ControlMessage(Segment):
    def __init__(self, src, dst, ttl, opcode, payload):
        super().__init__(src, dst, ttl, True, payload)
        self.payload = payload
        self.opcode = opcode

    def get_opcode(self, application_key):
        return bitstring.pack("uint:7", self.opcode)

    def segments(self, application_key, seq, iv_index, szmic=False, seg=False):
        if szmic:
            raise NotImplementedError("Control messages do not support long MIC")

        if seg:
            raise NotImplementedError("Control messages do not support segmentation")

        yield from super()._segments(
            application_key, seq, payload=self.payload, szmic=False, seg=False
        )

    @classmethod
    def decrypt(cls, ttl, src, dst, transport_pdu):
        seg, opcode = bitstring.BitString(transport_pdu).unpack("uint:1, uint:7")

        # works only for unsegmented messages!
        if seg:
            raise NotImplementedError
        return ControlMessage(src, dst, ttl, opcode, transport_pdu[1:])


class ProxyConfigMessage(Segment):
    def __init__(self, src, opcode, payload):
        super().__init__(src, 0x0000, 0x00, True, payload)
        self.payload = payload
        self.opcode = opcode

    def get_opcode(self, application_key):
        return bitstring.pack("uint:7", self.opcode)

    def segments(self, application_key, seq, iv_index, szmic=False, seg=False):
        yield from super()._segments(
            application_key, seq, payload=self.payload, szmic=False, seg=seg
        )

    @classmethod
    def decrypt(cls, src, transport_pdu):
        opcode = transport_pdu[0]
        return ProxyConfigMessage(src, opcode, transport_pdu[1:])


class SolicitationMessage(Segment):
    def __init__(self, src, dst=0):
        super().__init__(src, dst, 0x00, True, bytes())
        self.payload = bytes()
        self.opcode = bytes()

    def get_opcode(self, application_key):
        return bitstring.BitString()

    def segments(self, application_key, seq, iv_index, szmic=False, seg=False):
        yield bytes()

    @classmethod
    def decrypt(cls, src):
        return SolicitationMessage(src)


class SegmentAckMessage(ControlMessage):
    def __init__(self, src, dst, ttl, seq_zero, ack_segments, obo=False):
        self.obo = obo
        self.seq_zero = seq_zero
        self.block_ack = bitstring.BitArray(i in ack_segments for i in range(32))

        self.payload = bitstring.pack(
            "uint:1, uint:13, pad:2, bits:32",
            self.obo,
            self.seq_zero,
            reversed(self.block_ack),
        ).bytes

        super().__init__(src, dst, ttl, 0x00, self.payload)


class NetworkMessage:
    def __init__(self, message: Segment):
        self.message = message

    def pack(
        self,
        application_key,
        network_key,
        seq,
        iv_index,
        *,
        transport_seq=None,
        skip_segments=(),
        seg=False,
    ):
        nid, encryption_key, privacy_key = network_key.encryption_keys

        # when retrying a segment, use the original sequence number during application
        # encryption, but a newer one on network layer
        if transport_seq is None:
            transport_seq = seq

        # remove segments that were ack-ed and encrypt with new network sequence
        segments = list(
            self.message.segments(application_key, transport_seq, iv_index, seg=seg)
        )

        for index in sorted(skip_segments, reverse=True):
            segments.pop(index)

        for seq, pdu in enumerate(segments, start=seq):
            if isinstance(self.message, ProxyConfigMessage):
                nonce = self.message.nonce.proxy(seq, iv_index)
            elif isinstance(self.message, SolicitationMessage):
                assert iv_index == 0x00000000
                nonce = self.message.nonce.solicitation(seq)
            else:
                nonce = self.message.nonce.network(seq, iv_index)
            network_pdu = aes_ccm_encrypt(
                encryption_key,
                nonce,
                bitstring.pack("uintbe:16, bytes", self.message.dst, pdu).bytes,
                b"",
                8 if self.message.ctl else 4,
            )

            network_header = bitstring.pack(
                "uint:1, uint:7, uintbe:24, uintbe:16",
                self.message.ctl,
                self.message.ttl,
                seq,
                self.message.src,
            ).bytes

            privacy_random = bitstring.pack(
                "pad:40, uintbe:32, bytes:7", iv_index, network_pdu[:7]
            ).bytes

            pecb = aes_ecb(privacy_key, privacy_random)[:6]

            obfuscated_header = bytes(map(operator.xor, network_header, pecb))

            yield seq, bitstring.pack(
                "uint:1, uint:7, bits, bytes",
                iv_index & 1,
                nid,
                obfuscated_header,
                network_pdu,
            ).bytes

    @classmethod
    def unpack(
        cls,
        app_key: ApplicationKey,
        net_key: NetworkKey,
        local_iv_index: int,
        network_pdu: bytes,
        proxy=False,
    ):
        # pylint: disable=R0914
        _nid, encryption_key, privacy_key = net_key.encryption_keys
        last_iv, nid, obfuscated_header, encoded_data_mic = bitstring.BitString(
            network_pdu
        ).unpack("uint:1, uint:7, bytes:6, bytes")
        if nid != _nid:
            raise KeyError
        iv_index = (
            local_iv_index if (local_iv_index & 0x01) == last_iv else local_iv_index - 1
        )
        privacy_random = bitstring.pack(
            "pad:40, uintbe:32, bytes:7", iv_index, encoded_data_mic[:7]
        ).bytes

        pecb = aes_ecb(privacy_key, privacy_random)[:6]
        deobfuscated = bytes(map(operator.xor, obfuscated_header, pecb))
        ctl, ttl, seq, src = bitstring.BitString(deobfuscated).unpack(
            "uint:1, uint:7, uintbe:24, uintbe:16"
        )
        net_mic_len = 8 if ctl else 4

        nonce = (
            Nonce(src, 0, ttl, ctl).proxy if proxy else Nonce(src, 0, ttl, ctl).network
        )(seq, iv_index)
        decrypted_net = aes_ccm_decrypt(
            encryption_key, nonce, encoded_data_mic, tag_length=net_mic_len
        )

        dst, transport_pdu = bitstring.BitString(decrypted_net).unpack(
            "uintbe:16, bytes"
        )

        if proxy:
            transport_msg = ProxyConfigMessage.decrypt(src, transport_pdu)
        elif ctl:
            transport_msg = ControlMessage.decrypt(ttl, src, dst, transport_pdu)
        else:
            transport_msg = AccessMessage.decrypt(
                app_key, iv_index, ctl, ttl, seq, src, dst, transport_pdu
            )
        net_message = NetworkMessage(transport_msg)
        return iv_index, seq, net_message


MESH_CRC = Configuration(
    width=8,
    polynomial=0x07,
    init_value=0xFF,
    final_xor_value=0xFF,
    reverse_input=True,
    reverse_output=True,
)

CRC_CALCULATOR = CrcCalculator(configuration=MESH_CRC)


class GenericProvisioningPDU:
    @staticmethod
    def pack(payload):
        if payload["type"] == ProvisioningPDUType.ACK:
            return [b"\x01"]

        if isinstance(payload["type"], BearerOpcode):
            return [
                ProvisioningBearerControl.build(
                    dict(opcode=payload["type"], parameters=payload["parameters"])
                )
            ]

        PDU = ProvisioningPDU.build(obj=payload)

        segments = [PDU[0:20]]
        if len(PDU) > 20:
            segments += [PDU[0 + i : 23 + i] for i in range(20, len(PDU), 23)]

        total_len = len(PDU)
        fcs = CRC_CALCULATOR.calculate_checksum(PDU)

        ret = list()
        ret.append(
            TransactionStartPDU.build(
                dict(
                    last_segment_number=len(segments) - 1,
                    total_length=total_len,
                    frame_check=fcs,
                    data=segments.pop(0),
                )
            )
        )

        for index, segment in enumerate(segments, start=1):
            ret.append(
                TransactionContinuationPDU.build(
                    dict(segment_index=index, data=segment)
                )
            )

        return ret

    @staticmethod
    def unpack(segments):
        if segments[0] == b"\x01":
            return dict(type=ProvisioningPDUType.ACK, parameters=dict())

        parsed = [TransactionPDUSegment.parse(segment) for segment in segments]
        parsed.sort(key=lambda segment: getattr(segment, "segment_index", 0))

        if parsed[0].get("opcode") is not None:
            return dict(type=parsed[0]["opcode"], parameters=parsed[0]["parameters"])

        return ProvisioningPDU.parse(data=b"".join(segment.data for segment in parsed))

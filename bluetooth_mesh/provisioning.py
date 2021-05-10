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
# pylint: disable=W0223

import enum
import struct

import ecdsa
from construct import (
    Adapter,
    BitsInteger,
    BitStruct,
    Bytes,
    Bytewise,
    Const,
    ExprAdapter,
    GreedyBytes,
    Int8ub,
    Int16ub,
    Int32ub,
    Padding,
    Select,
    Struct,
    Switch,
    this,
)

from bluetooth_mesh.crypto import aes_ccm_decrypt, aes_ccm_encrypt, aes_cmac, k1, s1
from bluetooth_mesh.messages.util import BitList, EmbeddedBitStruct, EnumAdapter


class BearerOpcode(enum.IntEnum):
    LINK_OPEN = 0x00
    LINK_ACK = 0x01
    LINK_CLOSE = 0x02


class ProvisioningPDUType(enum.IntEnum):
    INVITE = 0x00
    CAPABILITIES = 0x01
    START = 0x02
    PUBLIC_KEY = 0x03
    INPUT_COMPLETE = 0x04
    CONFIRMATION = 0x05
    RANDOM = 0x06
    DATA = 0x07
    COMPLETE = 0x08
    FAILED = 0x09
    # ACK type is not in specification and is not actually used in constructing the message
    # it is there just to allow consistent packing/unpacking of GenericProvisioningPDU
    ACK = -1


class GenericProvisioningPDUType(enum.IntEnum):
    START = 0x00
    ACK = 0x01
    CONTINUATION = 0x02
    CONTROL = 0x03


class ProvisioningAlgorithm(enum.IntEnum):
    FIPS_P256_EC = 0


class ProvisioningPublicKeyType(enum.IntEnum):
    OOB = 0


class ProvisioningStaticOOBType(enum.IntEnum):
    AVAILABLE = 0


class ProvisioningOutputOOBAction(enum.IntEnum):
    BLINK = 0
    BEEP = 1
    VIBRATE = 2
    OUTPUT_NUMERIC = 3
    OUTPUT_ALPHANUMERIC = 4


class ProvisioningInputOOBAction(enum.IntEnum):
    PUSH = 0
    TWIST = 1
    INPUT_NUMERIC = 2
    INPUT_ALPHANUMERIC = 3


class ProvisioningAuthenticationMethod(enum.IntEnum):
    NONE = 0
    STATIC = 1
    OUTPUT = 2
    INPUT = 3


class ProvisioningErrorCode(enum.IntEnum):
    PROHIBITED = 0
    INVALID_PDU = 1
    INVALID_FORMAT = 2
    UNEXPECTED_PDU = 3
    CONFIRMATION_FAILED = 4
    OUT_OF_RESOURCES = 5
    DECRYPTION_FAILED = 6
    UNEXPECTED_ERROR = 7
    CANNOT_ASSIGN_ADDRESS = 8


class LinkCloseReason(enum.IntEnum):
    SUCCESS = 0x00
    TIMEOUT = 0x01
    FAIL = 0x02


class ProvisioningPublicKeyAdapter(Adapter):
    def _decode(self, obj, content, path):
        value = obj["x"] + obj["y"]
        return ecdsa.VerifyingKey.from_string(value, curve=ecdsa.NIST256p)

    def _encode(self, obj, content, path):
        value = obj.to_string()
        return dict(x=value[:32], y=value[32:])


# fmt: off
ProvisioningInvite = Struct(
    "attention" / Int8ub,
)

ProvisioningCapabilities = Struct(
    "num_elements" / Int8ub,
    "algorithms" / BitList(2, reversed=True),
    "public_key_type" / BitList(1, reversed=True),
    "static_oob_type" / BitList(1, reversed=True),
    "output_oob_size" / Int8ub,
    "output_oob_action" / BitList(2, reversed=True),
    "input_oob_size" / Int8ub,
    "input_oob_action" / BitList(2, reversed=True),
)

ProvisioningStart = Struct(
    "algorithm" / EnumAdapter(Int8ub, ProvisioningAlgorithm),
    "public_key" / ExprAdapter(Int8ub,
                               lambda obj, ctx: bool(obj),
                               lambda obj, ctx: 1 if obj else 0),
    "authentication_method" / EnumAdapter(Int8ub, ProvisioningAuthenticationMethod),
    "authentication_action" / Switch(
        this.authentication_method,
        {
            ProvisioningAuthenticationMethod.NONE: Const(0, Int8ub),
            ProvisioningAuthenticationMethod.STATIC: Const(0, Int8ub),
            ProvisioningAuthenticationMethod.OUTPUT: EnumAdapter(Int8ub, ProvisioningOutputOOBAction),
            ProvisioningAuthenticationMethod.INPUT: EnumAdapter(Int8ub, ProvisioningInputOOBAction),
        },
    ),
    "authentication_size" / Switch(
        this.authentication_method,
        {
            ProvisioningAuthenticationMethod.NONE: Const(0, Int8ub),
            ProvisioningAuthenticationMethod.STATIC: Const(0, Int8ub),
            ProvisioningAuthenticationMethod.OUTPUT: Int8ub,
            ProvisioningAuthenticationMethod.INPUT: Int8ub,
        },
    ),
)

ProvisioningPublicKey = Struct(
    "key" / ProvisioningPublicKeyAdapter(
        Struct(
            "x" / Bytes(32),
            "y" / Bytes(32),
        ),
    ),
)

ProvisioningInputComplete = Struct()

ProvisioningConfirmation = Struct(
    "confirmation" / Bytes(16),
)

ProvisioningRandom = Struct(
    "random" / Bytes(16),
)

ProvisioningData = Struct(
    "encrypted_provisioning_data" / Bytes(25),
    "provisioning_data_mic" / Bytes(8),
)

ProvisioningPayload = Struct(
    "network_key" / Bytes(16),
    "key_index" / Int16ub,
    "flags" / Int8ub,
    "iv_index" / Int32ub,
    "unicast_address" / Int16ub,
)

ProvisioningComplete = Struct(
)

ProvisioningFailed = Struct(
    "error_code" / EnumAdapter(Int8ub, ProvisioningErrorCode)
)

ProvisioningPDU = Struct(
    *EmbeddedBitStruct(
        "_",
        Padding(2),
        "type" / EnumAdapter(BitsInteger(6), ProvisioningPDUType),
    ),
    "parameters" / Switch(
        this.type,
        {
            ProvisioningPDUType.INVITE: ProvisioningInvite,
            ProvisioningPDUType.CAPABILITIES: ProvisioningCapabilities,
            ProvisioningPDUType.START: ProvisioningStart,
            ProvisioningPDUType.PUBLIC_KEY: ProvisioningPublicKey,
            ProvisioningPDUType.INPUT_COMPLETE: ProvisioningInputComplete,
            ProvisioningPDUType.CONFIRMATION: ProvisioningConfirmation,
            ProvisioningPDUType.RANDOM: ProvisioningRandom,
            ProvisioningPDUType.DATA: ProvisioningData,
            ProvisioningPDUType.COMPLETE: ProvisioningComplete,
            ProvisioningPDUType.FAILED: ProvisioningFailed,
        },
        default=GreedyBytes,
    ),
)

LinkOpen = Struct(
    "device_uuid" / Bytes(16)
)

LinkClose = Struct(
    "reason" / EnumAdapter(Int8ub, LinkCloseReason)
)

ProvisioningBearerControl = BitStruct(
    "opcode" / EnumAdapter(BitsInteger(6), BearerOpcode),
    "type" / Const(GenericProvisioningPDUType.CONTROL, BitsInteger(2)),
    "parameters" / Switch(
        this.opcode,
        {
            BearerOpcode.LINK_OPEN: Struct("device_uuid" / Bytewise(Bytes(16))),
            BearerOpcode.LINK_ACK: Struct(),
            BearerOpcode.LINK_CLOSE: Struct("reason" / EnumAdapter(BitsInteger(8), LinkCloseReason))
        },
        default=GreedyBytes,
    ),
)

TransactionStartPDU = Struct(
    *EmbeddedBitStruct(
        "_",
        "last_segment_number" / BitsInteger(6),
        "type" / Const(GenericProvisioningPDUType.START, BitsInteger(2)),
    ),
    "total_length" / Int16ub,
    "frame_check" / Int8ub,
    "data" / GreedyBytes
)

TransactionContinuationPDU = Struct(
    *EmbeddedBitStruct(
        "_",
        "segment_index" / BitsInteger(6),
        "type" / Const(GenericProvisioningPDUType.CONTINUATION, BitsInteger(2)),
    ),
    "data" / GreedyBytes
)

TransactionPDUSegment = Select(
    TransactionStartPDU,
    TransactionContinuationPDU,
    ProvisioningBearerControl
)

ProvisioningMessage = Struct(
    "link_id" / Bytes(4),
    "transaction_id" / Int8ub,
    "data" / GreedyBytes
)
# fmt: on


class ProvisioningEncryption:
    @staticmethod
    def data_encrypt(secret, inputs, data):
        """inputs = confirmation_salt + provisioner_random + device_random"""
        provisioning_salt = s1(inputs)
        provisioning_key = k1(secret, provisioning_salt, b"prsk")
        provisioning_nonce = k1(secret, provisioning_salt, b"prsn")[-13:]

        return aes_ccm_encrypt(provisioning_key, provisioning_nonce, data, tag_length=8)

    @staticmethod
    def data_decrypt(secret, inputs, data, mic=b""):
        """inputs = confirmation_salt + provisioner_random + device_random"""
        provisioning_salt = s1(inputs)
        provisioning_key = k1(secret, provisioning_salt, b"prsk")
        provisioning_nonce = k1(secret, provisioning_salt, b"prsn")[-13:]

        return (
            provisioning_salt,
            aes_ccm_decrypt(
                provisioning_key, provisioning_nonce, data + mic, tag_length=8
            ),
        )

    @staticmethod
    def provisioning_device_key(secret, provisioning_salt):
        return k1(secret, provisioning_salt, b"prdk")

    @staticmethod
    def confirmation_encrypt(secret, inputs, random, auth=None):
        """inputs = invite(attention) + capabilities(without opcode) + start(msg) + provisioner_key + device_key"""
        confirmation_salt = s1(inputs)
        confirmation_key = k1(secret, confirmation_salt, b"prck")

        return (
            confirmation_salt,
            confirmation_key,
            aes_cmac(confirmation_key, random + struct.pack("16s", auth or b"")),
        )

    @staticmethod
    def confirmation_validate(confirmation_key, confirmation, random, auth=None):
        return confirmation == aes_cmac(
            confirmation_key, random + struct.pack("16s", auth or b"")
        )

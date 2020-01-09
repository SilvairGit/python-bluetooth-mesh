import enum
import struct

from construct import (Adapter, BitsInteger, Bytes, BytesInteger, Const,
                       ExprAdapter, GreedyBytes, Int8ub, Int16ub, Int32ub, Padding, Struct,
                       Switch, obj_, this)

import ecdsa
from bluetooth_mesh.messages.util import (BitList, EmbeddedBitStruct,
                                          EnumAdapter, Reversed)
from bluetooth_mesh.crypto import s1, k1, aes_cmac, aes_ccm_decrypt


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
    OUTPUT_NUMERIC = 2
    OUTPUT_ALPHANUMERIC = 3


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
# fmt: on


def provisioning_confirmation(secret, inputs, random, auth=None):
    confirmation_salt = s1(inputs)
    confirmation_key = k1(secret, confirmation_salt, b'prck')

    return confirmation_salt, aes_cmac(confirmation_key, random + struct.pack('16s', auth or b''))


def provisioning_decrypt(secret, confirmation_salt, provisioner_random, device_random, data, mic):
    provisioning_salt = s1(confirmation_salt + provisioner_random + device_random)

    session_key = k1(secret, provisioning_salt, b'prsk')
    session_nonce = k1(secret, provisioning_salt, b'prsn')[-13:]

    return provisioning_salt, aes_ccm_decrypt(session_key, session_nonce, data + mic, tag_length=8)


def provisioning_device_key(secret, provisioning_salt):
    return k1(secret, provisioning_salt, b'prdk')

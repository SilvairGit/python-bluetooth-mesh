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
import ecdsa
import pytest

from bluetooth_mesh.mesh import GenericProvisioningPDU
from bluetooth_mesh.provisioning import (
    BearerOpcode,
    GenericProvisioningPDUType,
    LinkCloseReason,
    ProvisioningAlgorithm,
    ProvisioningAuthenticationMethod,
    ProvisioningBearerControl,
    ProvisioningEncryption,
    ProvisioningInputOOBAction,
    ProvisioningOutputOOBAction,
    ProvisioningPDU,
    ProvisioningPDUType,
    ProvisioningPublicKeyType,
    ProvisioningStaticOOBType,
)

valid = [
    # fmt: off
    pytest.param(
        bytes.fromhex('0010'),
        dict(
            type=ProvisioningPDUType.INVITE,
            parameters=dict(
                attention=16
            )
        ),
        id="invite"
    ),
    pytest.param(
        bytes.fromhex('010100010101080009050002'),
        dict(
            type=ProvisioningPDUType.CAPABILITIES,
            parameters=dict(
                num_elements=1,
                algorithms={ProvisioningAlgorithm.FIPS_P256_EC},
                public_key_type={ProvisioningPublicKeyType.OOB},
                static_oob_type={ProvisioningStaticOOBType.AVAILABLE},
                output_oob_size=8,
                output_oob_action={ProvisioningOutputOOBAction.BLINK,
                                   ProvisioningOutputOOBAction.OUTPUT_NUMERIC},
                input_oob_size=5,
                input_oob_action={ProvisioningInputOOBAction.TWIST},
            )
        ),
        id="capabilities",
    ),
    pytest.param(
        bytes.fromhex('020000000000'),
        dict(
            type=ProvisioningPDUType.START,
            parameters=dict(
                algorithm=ProvisioningAlgorithm.FIPS_P256_EC,
                public_key=False,
                authentication_method=ProvisioningAuthenticationMethod.NONE,
                authentication_action=0,
                authentication_size=0,
            )
        ),
        id="start, no authentication",
    ),
    pytest.param(
        bytes.fromhex('020001020304'),
        dict(
            type=ProvisioningPDUType.START,
            parameters=dict(
                algorithm=ProvisioningAlgorithm.FIPS_P256_EC,
                public_key=True,
                authentication_method=ProvisioningAuthenticationMethod.OUTPUT,
                authentication_action=ProvisioningOutputOOBAction.OUTPUT_NUMERIC,
                authentication_size=4,
            )
        ),
        id="start, output numeric",
    ),
    pytest.param(
        bytes.fromhex('05b38a114dfdca1fe153bd2c1e0dc46ac2'),
        dict(
            type=ProvisioningPDUType.CONFIRMATION,
            parameters=dict(
                confirmation=bytes.fromhex('b38a114dfdca1fe153bd2c1e0dc46ac2'),
            )
        ),
        id="confirmation",
    ),
    pytest.param(
        bytes.fromhex('068b19ac31d58b124c946209b5db1021b9'),
        dict(
            type=ProvisioningPDUType.RANDOM,
            parameters=dict(
                random=bytes.fromhex('8b19ac31d58b124c946209b5db1021b9'),
            )
        ),
        id="random",
    ),
    pytest.param(
        bytes.fromhex('07'
                      'd0bd7f4a89a2ff6222af59a90a60ad58acfe3123356f5cec29'
                      '73e0ec50783b10c7'),
        dict(
            type=ProvisioningPDUType.DATA,
            parameters=dict(
                encrypted_provisioning_data=bytes.fromhex('d0bd7f4a89a2ff6222af59a90a60ad58acfe3123356f5cec29'),
                provisioning_data_mic=bytes.fromhex('73e0ec50783b10c7'),
            )
        ),
        id="data",
    ),
    # fmt: on
]


@pytest.mark.parametrize("encoded,decoded", valid)
def test_build(encoded, decoded):
    result = ProvisioningPDU.build(obj=decoded)
    assert result == encoded


@pytest.mark.parametrize("encoded,decoded", valid)
def test_parse(encoded, decoded):
    result = ProvisioningPDU.parse(data=encoded)
    assert result == decoded


# NOTE: ecdsa.VerifyingKey does not overload __eq__
@pytest.mark.parametrize(
    # fmt: off
    "encoded,decoded",
    [
        pytest.param(
            bytes.fromhex(
                '03'
                '2c31a47b5779809ef44cb5eaaf5c3e43d5f8faad4a8794cb987e9b03745c78dd'
                '919512183898dfbecd52e2408e43871fd021109117bd3ed4eaf8437743715d4f'
            ),
            dict(
                type=ProvisioningPDUType.PUBLIC_KEY,
                parameters=dict(
                    key=ecdsa.VerifyingKey.from_string(
                        bytes.fromhex(
                            '2c31a47b5779809ef44cb5eaaf5c3e43d5f8faad4a8794cb987e9b03745c78dd'
                            '919512183898dfbecd52e2408e43871fd021109117bd3ed4eaf8437743715d4f'
                        ),
                        curve=ecdsa.NIST256p,
                    )
                )
            ),
            id="public key",
        ),
    ]
    # fmt: on
)
def test_parse_key(encoded, decoded):
    result = ProvisioningPDU.parse(data=encoded)
    assert result["type"] == decoded["type"]
    assert result["parameters"]["key"].to_pem() == decoded["parameters"]["key"].to_pem()


def test_confirmation():
    invite = bytes.fromhex("00")
    capabilities = bytes.fromhex("0100010000000000000000")
    start = bytes.fromhex("0000000000")
    provisioner_key = bytes.fromhex(
        "2c31a47b5779809ef44cb5eaaf5c3e43d5f8faad4a8794cb987e9b03745c78dd"
        "919512183898dfbecd52e2408e43871fd021109117bd3ed4eaf8437743715d4f"
    )
    device_key = bytes.fromhex(
        "f465e43ff23d3f1b9dc7dfc04da8758184dbc966204796eccf0d6cf5e16500cc"
        "0201d048bcbbd899eeefc424164e33c201c2b010ca6b4d43a8a155cad8ecb279"
    )
    ecdh_secret = bytes.fromhex(
        "ab85843a2f6d883f62e5684b38e307335fe6e1945ecd19604105c6f23221eb69"
    )
    random = bytes.fromhex("8b19ac31d58b124c946209b5db1021b9")

    auth = None

    salt, key, confirmation = ProvisioningEncryption.confirmation_encrypt(
        ecdh_secret,
        invite + capabilities + start + provisioner_key + device_key,
        random,
        auth,
    )

    assert confirmation == bytes.fromhex("b38a114dfdca1fe153bd2c1e0dc46ac2")


bearer_ctrl = [
    # fmt: off
    pytest.param(
        bytes.fromhex('03 70cf7c9732a345b691494810d2e9cbf4'),
        dict(
            opcode=BearerOpcode.LINK_OPEN,
            parameters=dict(
                device_uuid=bytes.fromhex("70cf7c9732a345b691494810d2e9cbf4")
            ),
            type=GenericProvisioningPDUType.CONTROL
        ),
        id="link open"
    ),
    pytest.param(
        bytes.fromhex('07'),
        dict(
            opcode=BearerOpcode.LINK_ACK,
            parameters=dict(),
            type=GenericProvisioningPDUType.CONTROL
        ),
        id="link ack"
    ),
    pytest.param(
        bytes.fromhex('0b00'),
        dict(
            opcode=BearerOpcode.LINK_CLOSE,
            parameters=dict(
                reason=LinkCloseReason.SUCCESS
            ),
            type=GenericProvisioningPDUType.CONTROL
        ),
        id="link close"
    ),
    # fmt: on
]


@pytest.mark.parametrize("encoded,decoded", bearer_ctrl)
def test_build_provisioning(encoded, decoded):
    result = ProvisioningBearerControl.build(obj=decoded)
    assert result == encoded


@pytest.mark.parametrize("encoded,decoded", bearer_ctrl)
def test_parse_provisioning(encoded, decoded):
    result = ProvisioningBearerControl.parse(data=encoded)
    assert result == decoded


valid = [
    # fmt: off
    pytest.param(
        [bytes.fromhex('03 70cf7c9732a345b691494810d2e9cbf4')],
        dict(
            type=BearerOpcode.LINK_OPEN,
            parameters=dict(
                device_uuid=bytes.fromhex("70cf7c9732a345b691494810d2e9cbf4")
            ),
        ),
        id="link open"
    ),
    pytest.param(
        [bytes.fromhex('00 0002 14 0000')],
        dict(
            type=ProvisioningPDUType.INVITE,
            parameters=dict(
                attention=0
            )
        ),
        id="invite"
    ),
    pytest.param(
        [bytes.fromhex('00 0006 64 020000000000')],
        dict(
            type=ProvisioningPDUType.START,
            parameters=dict(
                algorithm=ProvisioningAlgorithm.FIPS_P256_EC,
                public_key=False,
                authentication_method=ProvisioningAuthenticationMethod.NONE,
                authentication_action=0,
                authentication_size=0,
            )
        ),
        id="start"
    ),
    pytest.param(
        [bytes.fromhex('0400228b 07d0bd7f4a89a2ff6222af59a90a60ad58acfe31'),
         bytes.fromhex('06 23356f5cec2973e0ec50783b10c7')],
        dict(
            type=ProvisioningPDUType.DATA,
            parameters=dict(
                encrypted_provisioning_data=bytes.fromhex('d0bd7f4a89a2ff6222af59a90a60ad58acfe3123356f5cec29'),
                provisioning_data_mic=bytes.fromhex('73e0ec50783b10c7'),
            )
        ),
        id="data",
    ),
    pytest.param(
        [bytes.fromhex('0800411003f465e43ff23d3f1b9dc7dfc04da8758184dbc9'),
         bytes.fromhex('0666204796eccf0d6cf5e16500cc0201d048bcbbd899eeef'),
         bytes.fromhex('0ac424164e33c201c2b010ca6b4d43a8a155cad8ecb279')],
        dict(
            type=ProvisioningPDUType.PUBLIC_KEY,
            parameters=dict(
                key=ecdsa.VerifyingKey.from_string(
                    bytes.fromhex('f465e43ff23d3f1b9dc7dfc04da8758184dbc966204796eccf0d6cf5e16500cc'
                                  '0201d048bcbbd899eeefc424164e33c201c2b010ca6b4d43a8a155cad8ecb279'),
                    curve=ecdsa.NIST256p,
                )
            )
        ),
        id="public key",
    ),
    pytest.param(
        [bytes.fromhex('000011d3068b19ac31d58b124c946209b5db1021b9')],
        dict(
            type=ProvisioningPDUType.RANDOM,
            parameters=dict(
                random=bytes.fromhex('8b19ac31d58b124c946209b5db1021b9')
            )
        ),
        id="random",
    ),
    pytest.param(
        [bytes.fromhex('01')],
        dict(
            type=ProvisioningPDUType.ACK,
            parameters=dict()
        ),
        id="ack",
    )
    # fmt: on
]


@pytest.mark.parametrize("encoded,decoded", valid)
def test_pack_generic(encoded, decoded):
    result = GenericProvisioningPDU.pack(payload=decoded)
    assert result == encoded


@pytest.mark.parametrize("encoded,decoded", valid)
def test_unpack_generic(encoded, decoded):
    result = GenericProvisioningPDU.unpack(segments=encoded)
    assert result == decoded


prov_params = [
    # fmt: off
    pytest.param(
        dict(
            secret=bytes.fromhex('ab85843a2f6d883f62e5684b38e307335fe6e1945ecd19604105c6f23221eb69'),

            confirmation_salt=bytes.fromhex('5faabe187337c71cc6c973369dcaa79a'),
            random_provisioner=bytes.fromhex('8b19ac31d58b124c946209b5db1021b9'),
            random_device=bytes.fromhex('55a2a2bca04cd32ff6f346bd0a0c1a3a'),

            net_key=bytes.fromhex('efb2255e6422d330088e09bb015ed707'),
            net_key_index=b"\x05\x67",
            flags=b"\x00",
            ivindex=b"\x01\x02\x03\x04",
            address=b"\x0b\x0c",

            prov_data=bytes.fromhex('efb2255e6422d330088e09bb015ed707056700010203040b0c'),
            enc_provisioning_data=bytes.fromhex('d0bd7f4a89a2ff6222af59a90a60ad58acfe3123356f5cec29'),
            mic=bytes.fromhex('73e0ec50783b10c7'),
            salt=bytes.fromhex('a21c7d45f201cf9489a2fb57145015b4')
        ),
        id=""
    )
    # fmt: on
]


@pytest.mark.parametrize("params", prov_params)
def test_encrypt_provisioning_data(params):

    prov_data = (
        params["net_key"]
        + params["net_key_index"]
        + params["flags"]
        + params["ivindex"]
        + params["address"]
    )

    assert prov_data == params["prov_data"]

    enc_provisioning_data = ProvisioningEncryption.data_encrypt(
        secret=params["secret"],
        inputs=params["confirmation_salt"]
        + params["random_provisioner"]
        + params["random_device"],
        data=prov_data,
    )

    assert enc_provisioning_data == params["enc_provisioning_data"] + params["mic"]


@pytest.mark.parametrize("params", prov_params)
def test_decrypt_provisioning_data(params):
    enc_provisioning_data = params["enc_provisioning_data"] + params["mic"]

    salt, provisioning_data = ProvisioningEncryption.data_decrypt(
        secret=params["secret"],
        inputs=params["confirmation_salt"]
        + params["random_provisioner"]
        + params["random_device"],
        data=enc_provisioning_data,
    )

    assert provisioning_data == params["prov_data"]
    assert salt == params["salt"]


@pytest.mark.parametrize(
    # fmt :off
    "confirmation_key, confirmation, random, auth",
    [
        pytest.param(
            bytes.fromhex("e31fe046c68ec339c425fc6629f0336f"),
            bytes.fromhex("eeba521c196b52cc2e37aa40329f554e"),
            bytes.fromhex("55a2a2bca04cd32ff6f346bd0a0c1a3a"),
            None,
            id="",
        ),
        pytest.param(
            bytes.fromhex("e31fe046c68ec339c425fc6629f0336f"),
            bytes.fromhex("b38a114dfdca1fe153bd2c1e0dc46ac2"),
            bytes.fromhex("8b19ac31d58b124c946209b5db1021b9"),
            None,
            id="",
        ),
    ]
    # fmt: on
)
def test_confirmation_validate(confirmation_key, confirmation, random, auth):
    assert ProvisioningEncryption.confirmation_validate(
        confirmation_key, confirmation, random, auth
    )


@pytest.mark.parametrize(
    # fmt: off
    "secret, provisioning_salt, device_key",
    [
        pytest.param(
            bytes.fromhex("ab85843a2f6d883f62e5684b38e307335fe6e1945ecd19604105c6f23221eb69"),
            bytes.fromhex("a21c7d45f201cf9489a2fb57145015b4"),
            bytes.fromhex("0520adad5e0142aa3e325087b4ec16d8"),
            id=""
        ),
    ]
    # fmt: on
)
def test_provisioning_device_key(secret, provisioning_salt, device_key):
    assert (
        ProvisioningEncryption.provisioning_device_key(secret, provisioning_salt)
        == device_key
    )

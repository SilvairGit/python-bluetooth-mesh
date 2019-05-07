import pytest

from bluetooth_mesh.messages import AccessMessage


valid = [
    pytest.param(
        bytes.fromhex("04003601030405"),
        {
            "opcode": 0x04,
            "params": {
                "test_id": 0,
                "company_id": 0x0136,
                "fault_array": [0x03, 0x04, 0x05]
            }
        },
        id="1 byte opcode"
    ),
    pytest.param(
        bytes.fromhex("8032013601"),
        {
            "opcode": 0x8032,
            "params": {
                "test_id": 1,
                "company_id": 0x0136
            }
        },
        id="2 byte opcode"
    ),
    pytest.param(
        bytes.fromhex("c0112233"),
        {
            "opcode": 0xc01122,
            "params": bytes([0x33])
        },
        id="3 byte opcode"
    )
]


@pytest.mark.parametrize("encoded,decoded", valid)
def test_build(encoded, decoded):
    result = AccessMessage.build(obj=decoded)
    # print(result)
    assert result == encoded


@pytest.mark.parametrize("encoded,decoded", valid)
def test_parse(encoded, decoded):
    result = AccessMessage.parse(data=encoded)
    # print(result)
    assert result == decoded

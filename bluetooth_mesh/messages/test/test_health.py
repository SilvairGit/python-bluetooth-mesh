import pytest
import construct

from bluetooth_mesh.messages.health import *


valid = [
    pytest.param(
        HealthCurrentStatus,
        bytes.fromhex("043601"),
        {
            "test_id": 4,
            "company_id": 0x0136,
            "fault_array": [],
        },
        id='HealthCurrentStatus - without faults'
    ),
    pytest.param(
        HealthCurrentStatus,
        bytes.fromhex("043601020304"),
        {
            "test_id": 4,
            "company_id": 0x0136,
            "fault_array": [0x02, 0x03, 0x04],
        },
        id='HealthCurrentStatus - with faults'
    ),
    pytest.param(
        HealthFaultGet,
        bytes.fromhex("3601"),
        {
            "company_id": 0x0136,
        },
        id='HealthFaultGet'
    ),
    pytest.param(
        HealthFaultClear,
        bytes.fromhex("3601"),
        {
            "company_id": 0x0136,
        },
        id='HealthFaultClear'
    ),
    pytest.param(
        HealthFaultTest,
        bytes.fromhex("033601"),
        {
            "test_id": 3,
            "company_id": 0x0136,
        },
        id='HealthFaultTest'
    ),
    pytest.param(
        HealthFaultStatus,
        bytes.fromhex("043601"),
        {
            "test_id": 4,
            "company_id": 0x0136,
            "fault_array": [],
        },
        id='HealthCurrentStatus - without faults'
    ),
    pytest.param(
        HealthFaultStatus,
        bytes.fromhex("043601020304"),
        {
            "test_id": 4,
            "company_id": 0x0136,
            "fault_array": [0x02, 0x03, 0x04],
        },
        id='HealthCurrentStatus - with faults'
    ),
    pytest.param(
        HealthPeriodGet,
        bytes.fromhex(""),
        {},
        id='HealthPeriodGet',
    ),
    pytest.param(
        HealthPeriodSet,
        bytes.fromhex("0f"),
        {
            "fast_period_divisor": 15
        },
        id='HealthPeriodSet',
    ),
    pytest.param(
        HealthPeriodStatus,
        bytes.fromhex("06"),
        {
            "fast_period_divisor": 6
        },
        id='HealthPeriodStatus',
    ),
    pytest.param(
        HealthAttentionGet,
        bytes.fromhex(""),
        {},
        id='HealthAttentionGet',
    ),
    pytest.param(
        HealthAttentionSet,
        bytes.fromhex("07"),
        {
            "attention": 7
        },
        id='HealthAttentionSet',
    ),
    pytest.param(
        HealthAttentionStatus,
        bytes.fromhex("06"),
        {
            "attention": 6
        },
        id='HealthAttentionSet',
    ),
]

parse_invalid = [
    pytest.param(
        HealthPeriodSet,
        bytes.fromhex("10"),
        construct.core.ValidationError,
        id="HealthPeriodSet - wrong value"
    ),
]

build_invalid = [
    pytest.param(
        HealthPeriodSet,
        {
            "fast_period_divisor": 16
        },
        construct.core.ValidationError,
        id="HealthPeriodSet - wrong value"
    )
]

@pytest.mark.parametrize("message,encoded,decoded", valid)
def test_build(message, encoded, decoded):
    result = message.build(obj=decoded)
    assert result == encoded


@pytest.mark.parametrize("message,encoded,decoded", valid)
def test_parse(message, encoded, decoded):
    result = message.parse(data=encoded)
    assert result == decoded


@pytest.mark.parametrize("message,encoded,exception", parse_invalid)
def test_parse_invalid(message, encoded, exception):
    with pytest.raises(exception):
        message.parse(data=encoded)


@pytest.mark.parametrize("message,decoded,exception", build_invalid)
def test_build_invalid(message, decoded, exception):
    with pytest.raises(exception):
        message.build(obj=decoded)


def test_build_health_message():
    data = HealthMessage.build(dict(opcode=HealthOpcode.ATTENTION_SET, params=dict(attention=6)))

    assert data == bytes.fromhex('800506')


def test_parse_health_message():
    msg = HealthMessage.parse(bytes.fromhex('800506'))

    assert msg == dict(opcode=HealthOpcode.ATTENTION_SET, params=dict(attention=6))


def test_parse_health_message_bad_opcode():
    with pytest.raises(construct.core.ValidationError):
        HealthMessage.parse(bytes.fromhex('8011'))

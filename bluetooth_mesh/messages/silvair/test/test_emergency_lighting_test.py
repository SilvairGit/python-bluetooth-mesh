from datetime import datetime, timedelta, timezone

import pytest

from bluetooth_mesh.messages.properties import PropertyID
from bluetooth_mesh.messages.silvair.emergency_lighting_test import (
    EmergencyLightingTestServerParams,
    EmergencyLightingTestServerSubOpcode,
    TestExecutionStatus,
)

valid = [
    pytest.param(
        bytes.fromhex("00"),
        EmergencyLightingTestServerSubOpcode.ELT_FUNCTIONAL_TEST_GET,
        {},
    ),
    pytest.param(
        bytes.fromhex("01"),
        EmergencyLightingTestServerSubOpcode.ELT_FUNCTIONAL_TEST_START,
        {},
    ),
    pytest.param(
        bytes.fromhex("02"),
        EmergencyLightingTestServerSubOpcode.ELT_FUNCTIONAL_TEST_STOP,
        {},
    ),
    pytest.param(
        bytes.fromhex("0305040302010608070506"),
        EmergencyLightingTestServerSubOpcode.ELT_FUNCTIONAL_TEST_STATUS,
        dict(
            tai_timestamp=dict(
                date=datetime(
                    2137,
                    3,
                    2,
                    17,
                    2,
                    45,
                    # time_zone_offset is -870min, which is -52200s, but
                    # python encodes that as -1d +34200s
                    tzinfo=timezone(timedelta(days=-1, seconds=34200)),
                ),
                tai_utc_delta=timedelta(seconds=1800),
            ),
            execution_result=dict(
                lamp_fault=False,
                battery_fault=True,
                circuit_fault=True,
                battery_duration_fault=False,
            ),
            execution_status=TestExecutionStatus.DROPPED,
        ),
    ),
    pytest.param(
        bytes.fromhex("030000000000060807050604030201"),
        EmergencyLightingTestServerSubOpcode.ELT_FUNCTIONAL_TEST_STATUS,
        dict(
            tai_timestamp=dict(
                date=datetime(
                    1999,
                    12,
                    30,
                    19,
                    0,
                    tzinfo=timezone(timedelta(days=-1, seconds=34200)),
                ),
                tai_utc_delta=timedelta(seconds=1800),
            ),
            execution_result=dict(
                lamp_fault=False,
                battery_fault=True,
                circuit_fault=True,
                battery_duration_fault=False,
            ),
            execution_status=TestExecutionStatus.DROPPED,
            relative_timestamp=0x01020304,
        ),
    ),
    pytest.param(
        bytes.fromhex("04"),
        EmergencyLightingTestServerSubOpcode.ELT_DURATION_TEST_GET,
        {},
    ),
    pytest.param(
        bytes.fromhex("05"),
        EmergencyLightingTestServerSubOpcode.ELT_DURATION_TEST_START,
        {},
    ),
    pytest.param(
        bytes.fromhex("06"),
        EmergencyLightingTestServerSubOpcode.ELT_DURATION_TEST_STOP,
        {},
    ),
    pytest.param(
        bytes.fromhex("07050403020106080705063412"),
        EmergencyLightingTestServerSubOpcode.ELT_DURATION_TEST_STATUS,
        dict(
            tai_timestamp=dict(
                date=datetime(
                    2137,
                    3,
                    2,
                    17,
                    2,
                    45,
                    tzinfo=timezone(timedelta(days=-1, seconds=34200)),
                ),
                tai_utc_delta=timedelta(seconds=1800),
            ),
            execution_result=dict(
                lamp_fault=False,
                battery_fault=True,
                circuit_fault=True,
                battery_duration_fault=False,
            ),
            execution_status=TestExecutionStatus.DROPPED,
            duration_result=0x1234,
        ),
    ),
    pytest.param(
        bytes.fromhex("0700000000000608070506341204030201"),
        EmergencyLightingTestServerSubOpcode.ELT_DURATION_TEST_STATUS,
        dict(
            tai_timestamp=dict(
                date=datetime(
                    1999,
                    12,
                    30,
                    19,
                    0,
                    tzinfo=timezone(timedelta(days=-1, seconds=34200)),
                ),
                tai_utc_delta=timedelta(seconds=1800),
            ),
            execution_result=dict(
                lamp_fault=False,
                battery_fault=True,
                circuit_fault=True,
                battery_duration_fault=False,
            ),
            execution_status=TestExecutionStatus.DROPPED,
            duration_result=0x1234,
            relative_timestamp=0x01020304,
        ),
    ),
    pytest.param(
        bytes.fromhex("0886FF"),
        EmergencyLightingTestServerSubOpcode.ELT_PROPERTY_GET,
        dict(
            property_id=PropertyID.ELT_DURATION_TEST_RETRY_PERIOD,
        ),
    ),
    pytest.param(
        bytes.fromhex("0986FF04030201"),
        EmergencyLightingTestServerSubOpcode.ELT_PROPERTY_SET,
        dict(
            property_id=PropertyID.ELT_DURATION_TEST_RETRY_PERIOD,
            value=dict(seconds=0x01020304),
        ),
    ),
    pytest.param(
        bytes.fromhex("0A86FF04030201"),
        EmergencyLightingTestServerSubOpcode.ELT_PROPERTY_SET_UNACKNOWLEDGED,
        dict(
            property_id=PropertyID.ELT_DURATION_TEST_RETRY_PERIOD,
            value=dict(seconds=0x01020304),
        ),
    ),
    pytest.param(
        bytes.fromhex("0B86FF04030201"),
        EmergencyLightingTestServerSubOpcode.ELT_PROPERTY_STATUS,
        dict(
            property_id=PropertyID.ELT_DURATION_TEST_RETRY_PERIOD,
            value=dict(seconds=0x01020304),
        ),
    ),
]


@pytest.mark.parametrize("encoded, subopcode, payload", valid)
def test_parse(encoded, subopcode, payload):
    decoded = EmergencyLightingTestServerParams.parse(encoded)
    assert decoded.subopcode == subopcode
    assert decoded.payload == payload


@pytest.mark.parametrize("encoded, subopcode, payload", valid)
def test_build(encoded, subopcode, payload):
    assert (
        EmergencyLightingTestServerParams.build(
            dict(subopcode=subopcode, payload=payload)
        )
        == encoded
    )

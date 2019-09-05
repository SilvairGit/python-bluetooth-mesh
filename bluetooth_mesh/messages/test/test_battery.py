import pytest

from bluetooth_mesh.messages.generic.battery import *


valid = [
    pytest.param(
        b'\x82\x23',
        GenericBatteryOpcode.BATTERY_GET,
        dict(),
        id="BATTERY_GET"),
    pytest.param(
        b'\x82\x24\x32\xb4\x00\x00\xfe\xfe\x00\x62',
        GenericBatteryOpcode.BATTERY_STATUS,
        dict(
            battery_level=50,
            time_to_discharge=0xb4,
            time_to_charge=0xfefe,
            flags=dict(
                battery_presence_flags=GenericBatteryFlagsPresence.BATTERY_PRESENT_NON_REMOVABLE,
                battery_indicator_flags=GenericBatteryFlagsIndicator.BATTERY_CHARGE_CRITICALLY_LOW,
                battery_charging_flags=GenericBatteryFlagsCharging.BATTERY_CHARGEABLE_CHARGING,
                battery_serviceability_flags=GenericBatteryFlagsServiceability.BATTERY_NOT_REQUIRE_SERVICE
            )
        ),
        id="BATTERY_STATUS"),
    pytest.param(
        b'\x82\x24\xff\xbb\xaa\x00\xff\xff\xff\xdb',
        GenericBatteryOpcode.BATTERY_STATUS,
        dict(
            battery_level=None,
            time_to_discharge=0xaabb,
            time_to_charge=None,
            flags=dict(
                battery_presence_flags=GenericBatteryFlagsPresence.BATTERY_PRESENCE_UNKNOWN,
                battery_indicator_flags=GenericBatteryFlagsIndicator.BATTERY_CHARGE_GOOD,
                battery_charging_flags=GenericBatteryFlagsCharging.BATTERY_CHARGEABLE_NOT_CHARGING,
                battery_serviceability_flags=GenericBatteryFlagsServiceability.BATTERY_SERVICEABILITY_UNKNOWN
            )
        ),
        id="BATTERY_STATUS"),
]


@pytest.mark.parametrize("encoded,opcode,data", valid)
def test_parse_valid(encoded, opcode, data):
    assert GenericBatteryMessage.parse(encoded).params == data


@pytest.mark.parametrize("encoded,opcode,data", valid)
def test_build_valid(encoded, opcode, data):
    assert GenericBatteryMessage.build(dict(opcode=opcode, params=data)) == \
        encoded

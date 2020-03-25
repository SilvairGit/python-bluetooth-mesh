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
import pytest

from bluetooth_mesh.messages.generic.battery import *

valid = [
    # fmt: off
    pytest.param(
        b'\x82\x23',
        GenericBatteryOpcode.BATTERY_GET,
        dict(),
        id="BATTERY_GET"
    ),
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
        id="BATTERY_STATUS"
    ),
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
        id="BATTERY_STATUS"
    ),
    # fmt: on
]


@pytest.mark.parametrize("encoded,opcode,data", valid)
def test_parse_valid(encoded, opcode, data):
    assert GenericBatteryMessage.parse(encoded).params == data


@pytest.mark.parametrize("encoded,opcode,data", valid)
def test_build_valid(encoded, opcode, data):
    assert GenericBatteryMessage.build(dict(opcode=opcode, params=data)) == encoded

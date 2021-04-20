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
from enum import IntEnum

from construct import BitsInteger, BitStruct, Int8ul, Int24ul, Struct, this

from bluetooth_mesh.messages.util import DefaultCountValidator, EnumAdapter
from bluetooth_mesh.messages.util import EnumSwitch as Switch
from bluetooth_mesh.messages.util import Opcode, SwitchStruct


class GenericBatteryOpcode(IntEnum):
    GENERIC_BATTERY_GET = 0x8223
    GENERIC_BATTERY_STATUS = 0x8224


class GenericBatteryFlagsPresence(IntEnum):
    BATTERY_NOT_PRESENT = 0b00
    BATTERY_PRESENT_REMOVABLE = 0b01
    BATTERY_PRESENT_NON_REMOVABLE = 0b10
    BATTERY_PRESENCE_UNKNOWN = 0b11


class GenericBatteryFlagsIndicator(IntEnum):
    BATTERY_CHARGE_CRITICALLY_LOW = 0b00
    BATTERY_CHARGE_LOW = 0b01
    BATTERY_CHARGE_GOOD = 0b10
    BATTERY_CHARGE_UNKNOWN = 0b11


class GenericBatteryFlagsCharging(IntEnum):
    BATTERY_NOT_CHARGEABLE = 0b00
    BATTERY_CHARGEABLE_NOT_CHARGING = 0b01
    BATTERY_CHARGEABLE_CHARGING = 0b10
    BATTERY_CHARGING_STATE_UNKNOWN = 0b11


class GenericBatteryFlagsServiceability(IntEnum):
    RFU = 0b00
    BATTERY_NOT_REQUIRE_SERVICE = 0b01
    BATTERY_REQUIRE_SERVICE = 0b10
    BATTERY_SERVICEABILITY_UNKNOWN = 0b11


# fmt: off
BatteryFlags = BitStruct(
    "battery_serviceability_flags" / EnumAdapter(BitsInteger(2),
                                                 GenericBatteryFlagsServiceability),
    "battery_charging_flags" / EnumAdapter(BitsInteger(2),
                                           GenericBatteryFlagsCharging),
    "battery_indicator_flags" / EnumAdapter(BitsInteger(2),
                                            GenericBatteryFlagsIndicator),
    "battery_presence_flags" / EnumAdapter(BitsInteger(2),
                                           GenericBatteryFlagsPresence),
)

GenericBatteryGet = Struct()

GenericBatteryStatus = Struct(
    "battery_level" / DefaultCountValidator(Int8ul),
    "time_to_discharge" / DefaultCountValidator(Int24ul),
    "time_to_charge" / DefaultCountValidator(Int24ul),
    "flags" / BatteryFlags
)

GenericBatteryMessage = SwitchStruct(
    "opcode" / Opcode(GenericBatteryOpcode),
    "params" / Switch(
        this.opcode,
        {
            GenericBatteryOpcode.GENERIC_BATTERY_GET: GenericBatteryGet,
            GenericBatteryOpcode.GENERIC_BATTERY_STATUS: GenericBatteryStatus,
        },
    )
)
# fmt: on

#
# python-bluetooth-mesh - Bluetooth Mesh for Python
#
# Copyright (C) 2022  SILVAIR sp. z o.o.
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

from construct import Int8ul, Struct, this

from bluetooth_mesh.messages.util import EnumAdapter
from bluetooth_mesh.messages.util import EnumSwitch as Switch
from bluetooth_mesh.messages.util import Opcode, SwitchStruct


class GenericPowerOnOffOpcode(IntEnum):
    GENERIC_ON_POWERUP_GET = 0x8211
    GENERIC_ON_POWERUP_STATUS = 0x8212


class GenericPowerOnOffSetupOpcode(IntEnum):
    GENERIC_ON_POWERUP_SET = 0x8213
    GENERIC_ON_POWERUP_SET_UNACKNOWLEDGED = 0x8214


class GenericOnPowerUp(IntEnum):
    GENERIC_ON_POWERUP_OFF = 0x00
    GENERIC_ON_POWERUP_DEFAULT = 0x01
    GENERIC_ON_POWERUP_RESTORE = 0x02


# fmt: off
GenericOnPowerUpGet = Struct()

GenericOnPowerUpSet = Struct(
    "on_power_up" / EnumAdapter(Int8ul, GenericOnPowerUp)
)

GenericOnPowerUpStatus = Struct(
    "on_power_up" / EnumAdapter(Int8ul, GenericOnPowerUp)
)


GenericPowerOnOffMessage = SwitchStruct(
    "opcode" / Opcode(GenericPowerOnOffOpcode),
    "params" / Switch(
        this.opcode,
        {
            GenericPowerOnOffOpcode.GENERIC_ON_POWERUP_GET: GenericOnPowerUpGet,
            GenericPowerOnOffOpcode.GENERIC_ON_POWERUP_STATUS: GenericOnPowerUpStatus,
        },
    ),
)


GenericPowerOnOffSetupMessage = SwitchStruct(
    "opcode" / Opcode(GenericPowerOnOffSetupOpcode),
    "params" / Switch(
        this.opcode,
        {
            GenericPowerOnOffSetupOpcode.GENERIC_ON_POWERUP_SET: GenericOnPowerUpSet,
            GenericPowerOnOffSetupOpcode.GENERIC_ON_POWERUP_SET_UNACKNOWLEDGED: GenericOnPowerUpSet,
        },
    ),
)
# fmt: off

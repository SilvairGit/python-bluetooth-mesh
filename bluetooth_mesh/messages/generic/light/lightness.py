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

from construct import Embedded, Int8ul, Int16ul, Struct, Switch, this

from bluetooth_mesh.messages.config import StatusCodeAdapter
from bluetooth_mesh.messages.generics import (
    OptionalSetParameters,
    TransitionTime,
    TransitionTimeAdapter,
)
from bluetooth_mesh.messages.util import EnumAdapter, NamedSelect, Opcode, SwitchStruct


class LightLightnessOpcode(IntEnum):
    LIGHT_LIGHTNESS_GET = 0x824B
    LIGHT_LIGHTNESS_SET = 0x824C
    LIGHT_LIGHTNESS_SET_UNACKNOWLEDGED = 0x824D
    LIGHT_LIGHTNESS_STATUS = 0x824E
    LIGHT_LIGHTNESS_LINEAR_GET = 0x824F
    LIGHT_LIGHTNESS_LINEAR_SET = 0x8250
    LIGHT_LIGHTNESS_LINEAR_SET_UNACKNOWLEDGED = 0x8251
    LIGHT_LIGHTNESS_LINEAR_STATUS = 0x8252
    LIGHT_LIGHTNESS_LAST_GET = 0x8253
    LIGHT_LIGHTNESS_LAST_STATUS = 0x8254
    LIGHT_LIGHTNESS_DEFAULT_GET = 0x8255
    LIGHT_LIGHTNESS_DEFAULT_STATUS = 0x8256
    LIGHT_LIGHTNESS_RANGE_GET = 0x8257
    LIGHT_LIGHTNESS_RANGE_STATUS = 0x8258

    def __repr__(self):
        return str(self.value)


class LightLightnessSetupOpcode(IntEnum):
    LIGHT_LIGHTNESS_SETUP_DEFAULT_SET = 0x8259
    LIGHT_LIGHTNESS_SETUP_DEFAULT_SET_UNACKNOWLEDGED = 0x825A
    LIGHT_LIGHTNESS_SETUP_RANGE_SET = 0x825B
    LIGHT_LIGHTNESS_SETUP_RANGE_SET_UNACKNOWLEDGED = 0x825C

    def __repr__(self):
        return str(self.value)


# fmt: off
LightLightnessGet = Struct()

LightLightnessDefault = Struct(
    "lightness" / Int16ul
)

LightLightnessStatusMinimal = Struct(
    "present_lightness" / Int16ul
)

LightLightnessStatusOptional = Struct(
    Embedded(LightLightnessStatusMinimal),
    "target_lightness" / Int16ul,
    "remaining_time" / TransitionTimeAdapter(TransitionTime, allow_unknown=True)
)

LightLightnessStatus = NamedSelect(
    optional=LightLightnessStatusOptional,
    minimal=LightLightnessStatusMinimal
)

LightLightnessRange = Struct(
    "range_min" / Int16ul,
    "range_max" / Int16ul,
)

LightLightnessRangeStatus = Struct(
    "status" / StatusCodeAdapter,
    Embedded(LightLightnessRange)
)

LightLightnessSetMinimal = Struct(
    "lightness" / Int16ul,
    "tid" / Int8ul
)

LightLightnessSetOptional = Struct(
    Embedded(LightLightnessSetMinimal),
    Embedded(OptionalSetParameters)
)

LightLightnessSet = NamedSelect(
    optional=LightLightnessSetOptional,
    minimal=LightLightnessSetMinimal
)

LightLightnessMessage = SwitchStruct(
    "opcode" / Opcode(LightLightnessOpcode),
    "params" / Switch(
        this.opcode,
        {
    LightLightnessOpcode.LIGHT_LIGHTNESS_GET: LightLightnessGet,
    LightLightnessOpcode.LIGHT_LIGHTNESS_SET: LightLightnessSet,
    LightLightnessOpcode.LIGHT_LIGHTNESS_SET_UNACKNOWLEDGED: LightLightnessSet,
    LightLightnessOpcode.LIGHT_LIGHTNESS_STATUS: LightLightnessStatus,
    LightLightnessOpcode.LIGHT_LIGHTNESS_LINEAR_GET: LightLightnessGet,
    LightLightnessOpcode.LIGHT_LIGHTNESS_LINEAR_SET: LightLightnessSet,
    LightLightnessOpcode.LIGHT_LIGHTNESS_LINEAR_SET_UNACKNOWLEDGED: LightLightnessSet,
    LightLightnessOpcode.LIGHT_LIGHTNESS_LINEAR_STATUS: LightLightnessStatus,
    LightLightnessOpcode.LIGHT_LIGHTNESS_LAST_GET: LightLightnessGet,
    LightLightnessOpcode.LIGHT_LIGHTNESS_LAST_STATUS: LightLightnessDefault,
    LightLightnessOpcode.LIGHT_LIGHTNESS_DEFAULT_GET: LightLightnessGet,
    LightLightnessOpcode.LIGHT_LIGHTNESS_DEFAULT_STATUS: LightLightnessDefault,
    LightLightnessOpcode.LIGHT_LIGHTNESS_RANGE_GET: LightLightnessGet,
    LightLightnessOpcode.LIGHT_LIGHTNESS_RANGE_STATUS: LightLightnessRangeStatus,
        }
    )
)

LightLightnessSetupMessage = SwitchStruct(
    "opcode" / Opcode(LightLightnessSetupOpcode),
    "params" / Switch(
        this.opcode,
        {
            LightLightnessSetupOpcode.LIGHT_LIGHTNESS_SETUP_DEFAULT_SET: LightLightnessDefault,
            LightLightnessSetupOpcode.LIGHT_LIGHTNESS_SETUP_DEFAULT_SET_UNACKNOWLEDGED: LightLightnessDefault,
            LightLightnessSetupOpcode.LIGHT_LIGHTNESS_SETUP_RANGE_SET: LightLightnessRange,
            LightLightnessSetupOpcode.LIGHT_LIGHTNESS_SETUP_RANGE_SET_UNACKNOWLEDGED: LightLightnessRange,
        }
    )
)
# fmt: on

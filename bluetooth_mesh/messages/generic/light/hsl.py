#
# python-bluetooth-mesh - Bluetooth Mesh for Python
#
# Copyright (C) 2022 Alexander Ozumenko
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


class LightHSLOpcode(IntEnum):
    LIGHT_HSL_GET = 0x826D
    LIGHT_HSL_HUE_GET = 0x826E
    LIGHT_HSL_HUE_SET = 0x826F
    LIGHT_HSL_HUE_SET_UNACKNOWLEDGED = 0x8270
    LIGHT_HSL_HUE_STATUS = 0x8271
    LIGHT_HSL_SATURATION_GET = 0x8272
    LIGHT_HSL_SATURATION_SET = 0x8273
    LIGHT_HSL_SATURATION_SET_UNACKNOWLEDGED = 0x8274
    LIGHT_HSL_SATURATION_STATUS = 0x8275
    LIGHT_HSL_SET = 0x8276
    LIGHT_HSL_SET_UNACKNOWLEDGED = 0x8277
    LIGHT_HSL_STATUS = 0x8278
    LIGHT_HSL_TARGET_GET = 0x8279
    LIGHT_HSL_TARGET_STATUS = 0x827A
    LIGHT_HSL_DEFAULT_GET = 0x827B
    LIGHT_HSL_DEFAULT_STATUS = 0x827C
    LIGHT_HSL_RANGE_GET = 0x827D
    LIGHT_HSL_RANGE_STATUS = 0x827E

    def __repr__(self):
        return str(self.value)


class LightHSLSetupOpcode(IntEnum):
    LIGHT_HSL_SETUP_DEFAULT_SET = 0x827F
    LIGHT_HSL_SETUP_DEFAULT_SET_UNACKNOWLEDGED = 0x8280
    LIGHT_HSL_SETUP_RANGE_SET = 0x8281
    LIGHT_HSL_SETUP_RANGE_SET_UNACKNOWLEDGED = 0x8282

    def __repr__(self):
        return str(self.value)


# fmt: off
LightHSLGet = Struct()

LightHSLDefault = Struct(
    "hsl_lightness" / Int16ul,
    "hsl_hue" / Int16ul,
    "hsl_saturation" / Int16ul
)

LightHSLSetMinimal = Struct(
    Embedded(LightHSLDefault),
    "tid" / Int8ul
)

LightHSLSetOptional = Struct(
    Embedded(LightHSLSetMinimal),
    Embedded(OptionalSetParameters)
)

LightHSLSet = NamedSelect(
    optional=LightHSLSetOptional,
    minimal=LightHSLSetMinimal
)

LightHSLStatusMinimal = Struct(
    Embedded(LightHSLDefault)
)

LightHSLStatusOptional = Struct(
    Embedded(LightHSLStatusMinimal),
    "remaining_time" / TransitionTimeAdapter(TransitionTime, allow_unknown=True)
)

LightHSLStatus = NamedSelect(
    optional=LightHSLStatusOptional,
    minimal=LightHSLStatusMinimal
)

LightHSLHueStatusMinimal = Struct(
    "present_hue" / Int16ul
)

LightHSLHueStatusOptional = Struct(
    Embedded(LightHSLHueStatusMinimal),
    "target_hue" / Int16ul,
    "remaining_time" / TransitionTimeAdapter(TransitionTime, allow_unknown=True)
)

LightHSLHueStatus = NamedSelect(
    optional=LightHSLHueStatusOptional,
    minimal=LightHSLHueStatusMinimal
)

LightHSLHueSetMinimal = Struct(
    "hue" / Int16ul,
    "tid" / Int8ul
)

LightHSLHueSetOptional = Struct(
    Embedded(LightHSLHueSetMinimal),
    Embedded(OptionalSetParameters)
)

LightHSLHueSet = NamedSelect(
    optional=LightHSLHueSetOptional,
    minimal=LightHSLHueSetMinimal
)

LightHSLSaturationStatusMinimal = Struct(
    "present_saturation" / Int16ul
)

LightHSLSaturationStatusOptional = Struct(
    Embedded(LightHSLSaturationStatusMinimal),
    "target_saturation" / Int16ul,
    "remaining_time" / TransitionTimeAdapter(TransitionTime, allow_unknown=True)
)

LightHSLSaturationStatus = NamedSelect(
    optional=LightHSLSaturationStatusOptional,
    minimal=LightHSLSaturationStatusMinimal
)

LightHSLSaturationSetMinimal = Struct(
    "saturation" / Int16ul,
    "tid" / Int8ul
)

LightHSLSaturationSetOptional = Struct(
    Embedded(LightHSLSaturationSetMinimal),
    Embedded(OptionalSetParameters)
)

LightHSLSaturationSet = NamedSelect(
    optional=LightHSLSaturationSetOptional,
    minimal=LightHSLSaturationSetMinimal
)

LightHSLRange = Struct(
    "hue_range_min" / Int16ul,
    "hue_range_max" / Int16ul,
    "saturation_range_min" / Int16ul,
    "saturation_range_max" / Int16ul
)

LightHSLRangeStatus = Struct(
    "status" / StatusCodeAdapter,
    Embedded(LightHSLRange)
)


LightHSLMessage = SwitchStruct(
    "opcode" / Opcode(LightHSLOpcode),
    "params" / Switch(
        this.opcode,
        {
            LightHSLOpcode.LIGHT_HSL_GET: LightHSLGet,
            LightHSLOpcode.LIGHT_HSL_HUE_GET: LightHSLGet,
            LightHSLOpcode.LIGHT_HSL_HUE_SET: LightHSLHueSet,
            LightHSLOpcode.LIGHT_HSL_HUE_SET_UNACKNOWLEDGED: LightHSLHueSet,
            LightHSLOpcode.LIGHT_HSL_HUE_STATUS: LightHSLHueStatus,
            LightHSLOpcode.LIGHT_HSL_SATURATION_GET: LightHSLGet,
            LightHSLOpcode.LIGHT_HSL_SATURATION_SET: LightHSLSaturationSet,
            LightHSLOpcode.LIGHT_HSL_SATURATION_SET_UNACKNOWLEDGED: LightHSLSaturationSet,
            LightHSLOpcode.LIGHT_HSL_SATURATION_STATUS: LightHSLSaturationStatus,
            LightHSLOpcode.LIGHT_HSL_SET: LightHSLSet,
            LightHSLOpcode.LIGHT_HSL_SET_UNACKNOWLEDGED: LightHSLSet,
            LightHSLOpcode.LIGHT_HSL_STATUS: LightHSLStatus,
            LightHSLOpcode.LIGHT_HSL_TARGET_GET: LightHSLGet,
            LightHSLOpcode.LIGHT_HSL_TARGET_STATUS: LightHSLStatus,
            LightHSLOpcode.LIGHT_HSL_DEFAULT_GET: LightHSLGet,
            LightHSLOpcode.LIGHT_HSL_DEFAULT_STATUS: LightHSLDefault,
            LightHSLOpcode.LIGHT_HSL_RANGE_GET: LightHSLGet,
            LightHSLOpcode.LIGHT_HSL_RANGE_STATUS: LightHSLRangeStatus
        },
    )
)


LightHSLSetupMessage = SwitchStruct(
    "opcode" / Opcode(LightHSLSetupOpcode),
    "params" / Switch(
        this.opcode,
        {
            LightHSLSetupOpcode.LIGHT_HSL_SETUP_DEFAULT_SET: LightHSLDefault,
            LightHSLSetupOpcode.LIGHT_HSL_SETUP_DEFAULT_SET_UNACKNOWLEDGED: LightHSLDefault,
            LightHSLSetupOpcode.LIGHT_HSL_SETUP_RANGE_SET: LightHSLRange,
            LightHSLSetupOpcode.LIGHT_HSL_SETUP_RANGE_SET_UNACKNOWLEDGED: LightHSLRange
        },
    )
)
# fmt: on

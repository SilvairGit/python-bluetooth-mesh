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


class LightCTLOpcode(IntEnum):
    LIGHT_CTL_GET = 0x825D
    LIGHT_CTL_SET = 0x825E
    LIGHT_CTL_SET_UNACKNOWLEDGED = 0x825F
    LIGHT_CTL_STATUS = 0x8260
    LIGHT_CTL_TEMPERATURE_GET = 0x8261
    LIGHT_CTL_TEMPERATURE_RANGE_GET = 0x8262
    LIGHT_CTL_TEMPERATURE_RANGE_STATUS = 0x8263
    LIGHT_CTL_TEMPERATURE_SET = 0x8264
    LIGHT_CTL_TEMPERATURE_SET_UNACKNOWLEDGED = 0x8265
    LIGHT_CTL_TEMPERATURE_STATUS = 0x8266
    LIGHT_CTL_TEMPERATURE_DEFAULT_GET = 0x8267
    LIGHT_CTL_TEMPERATURE_DEFAULT_STATUS = 0x8268

    def __repr__(self):
        return str(self.value)


class LightCTLSetupOpcode(IntEnum):
    LIGHT_CTL_SETUP_TEMPERATURE_DEFAULT_SET = 0x8269
    LIGHT_CTL_SETUP_TEMPERATURE_DEFAULT_SET_UNACKNOWLEDGED = 0x826A
    LIGHT_CTL_SETUP_TEMPERATURE_RANGE_SET = 0x826B
    LIGHT_CTL_SETUP_TEMPERATURE_RANGE_SET_UNACKNOWLEDGED = 0x826C

    def __repr__(self):
        return str(self.value)


# fmt: off
LightCTLGet = Struct()

LightCTLDefault = Struct(
    "ctl_lightness" / Int16ul,
    "ctl_temperature" / Int16ul,
    "ctl_delta_uv" / Int16ul
)

LightCTLSetMinimal = Struct(
    Embedded(LightCTLDefault),
    "tid" / Int8ul
)

LightCTLSetOptional = Struct(
    Embedded(LightCTLSetMinimal),
    Embedded(OptionalSetParameters)
)

LightCTLSet = NamedSelect(
    optional=LightCTLSetOptional,
    minimal=LightCTLSetMinimal
)

LightCTLStatusMinimal = Struct(
    "present_ctl_lightness" / Int16ul,
    "present_ctl_temperature" / Int16ul,
)

LightCTLStatusOptional = Struct(
    Embedded(LightCTLStatusMinimal),
    "target_ctl_lightness" / Int16ul,
    "target_ctl_temperature" / Int16ul,
    "remaining_time" / TransitionTimeAdapter(TransitionTime, allow_unknown=True)
)

LightCTLStatus = NamedSelect(
    optional=LightCTLStatusOptional,
    minimal=LightCTLStatusMinimal
)

LightCTLTemperatureStatusMinimal = Struct(
    "present_ctl_temperature" / Int16ul,
    "present_ctl_delta_uv" / Int16ul,
)

LightCTLTemperatureStatusOptional = Struct(
    Embedded(LightCTLTemperatureStatusMinimal),
    "target_ctl_temperature" / Int16ul,
    "target_ctl_delta_uv" / Int16ul,
    "remaining_time" / TransitionTimeAdapter(TransitionTime, allow_unknown=True)
)

LightCTLTemperatureStatus = NamedSelect(
    optional=LightCTLTemperatureStatusOptional,
    minimal=LightCTLTemperatureStatusMinimal
)

LightCTLTemperatureSetMinimal = Struct(
    "ctl_temperature" / Int16ul,
    "ctl_delta_uv" / Int16ul,
    "tid" / Int8ul
)

LightCTLTemperatureSetOptional = Struct(
    Embedded(LightCTLTemperatureSetMinimal),
    Embedded(OptionalSetParameters)
)

LightCTLTemperatureSet = NamedSelect(
    optional=LightCTLTemperatureSetOptional,
    minimal=LightCTLTemperatureSetMinimal
)

LightCTLRange = Struct(
    "range_min" / Int16ul,
    "range_max" / Int16ul,
)

LightCTLRangeStatus = Struct(
    "status" / StatusCodeAdapter,
    Embedded(LightCTLRange)
)


LightCTLMessage = SwitchStruct(
    "opcode" / Opcode(LightCTLOpcode),
    "params" / Switch(
        this.opcode,
        {
            LightCTLOpcode.LIGHT_CTL_GET: LightCTLGet,
            LightCTLOpcode.LIGHT_CTL_SET: LightCTLSet,
            LightCTLOpcode.LIGHT_CTL_SET_UNACKNOWLEDGED: LightCTLSet,
            LightCTLOpcode.LIGHT_CTL_STATUS: LightCTLStatus,
            LightCTLOpcode.LIGHT_CTL_TEMPERATURE_GET: LightCTLGet,
            LightCTLOpcode.LIGHT_CTL_TEMPERATURE_RANGE_GET: LightCTLGet,
            LightCTLOpcode.LIGHT_CTL_TEMPERATURE_RANGE_STATUS: LightCTLRangeStatus,
            LightCTLOpcode.LIGHT_CTL_TEMPERATURE_SET: LightCTLTemperatureSet,
            LightCTLOpcode.LIGHT_CTL_TEMPERATURE_SET_UNACKNOWLEDGED: LightCTLTemperatureSet,
            LightCTLOpcode.LIGHT_CTL_TEMPERATURE_STATUS: LightCTLTemperatureStatus,
            LightCTLOpcode.LIGHT_CTL_TEMPERATURE_DEFAULT_GET: LightCTLGet,
            LightCTLOpcode.LIGHT_CTL_TEMPERATURE_DEFAULT_STATUS: LightCTLDefault,
        },
    )
)


LightCTLSetupMessage = SwitchStruct(
    "opcode" / Opcode(LightCTLSetupOpcode),
    "params" / Switch(
        this.opcode,
        {
            LightCTLSetupOpcode.LIGHT_CTL_SETUP_TEMPERATURE_DEFAULT_SET: LightCTLDefault,
            LightCTLSetupOpcode.LIGHT_CTL_SETUP_TEMPERATURE_DEFAULT_SET_UNACKNOWLEDGED: LightCTLDefault,
            LightCTLSetupOpcode.LIGHT_CTL_SETUP_TEMPERATURE_RANGE_SET: LightCTLRange,
            LightCTLSetupOpcode.LIGHT_CTL_SETUP_TEMPERATURE_RANGE_SET_UNACKNOWLEDGED: LightCTLRange,
        },
    )
)
# fmt: on

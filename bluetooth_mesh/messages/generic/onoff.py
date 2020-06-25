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

from construct import Int8ul, Select, Struct, Switch, this

from bluetooth_mesh.messages.generics import (
    Delay,
    TransitionTime,
    TransitionTimeAdapter,
)
from bluetooth_mesh.messages.util import EnumAdapter, Opcode


class GenericOnOffOpcode(IntEnum):
    ONOFF_GET = 0x8201
    ONOFF_SET = 0x8202
    ONOFF_SET_UNACKNOWLEDGED = 0x8203
    ONOFF_STATUS = 0x8204


# fmt: on
GenericOnOffGet = Struct()

GenericOnOffSetMinimal = Struct("onoff" / Int8ul, "tid" / Int8ul)

GenericOnOffSetOptional = Struct(
    "onoff" / Int8ul,
    "tid" / Int8ul,
    "transition_time" / TransitionTimeAdapter(TransitionTime, allow_unknown=False),
    "delay" / Delay(Int8ul),
)

GenericOnOffSet = Select(GenericOnOffSetOptional, GenericOnOffSetMinimal)

GenericOnOffStatusMinimal = Struct("present_onoff" / Int8ul)

GenericOnOffStatusOptional = Struct(
    "present_onoff" / Int8ul,
    "target_onoff" / Int8ul,
    "remaining_time" / TransitionTimeAdapter(TransitionTime, allow_unknown=True),
)

GenericOnOffStatus = Select(GenericOnOffStatusOptional, GenericOnOffStatusMinimal)


GenericOnOffMessage = Struct(
    "opcode" / Opcode(GenericOnOffOpcode),
    "params"
    / Switch(
        this.opcode,
        {
            GenericOnOffOpcode.ONOFF_GET: GenericOnOffGet,
            GenericOnOffOpcode.ONOFF_SET: GenericOnOffSet,
            GenericOnOffOpcode.ONOFF_SET_UNACKNOWLEDGED: GenericOnOffSet,
            GenericOnOffOpcode.ONOFF_STATUS: GenericOnOffStatus,
        },
    ),
)
# fmt: off

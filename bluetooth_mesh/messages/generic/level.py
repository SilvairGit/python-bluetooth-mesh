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

from construct import Embedded, Int8ul, Int16sl, Int32sl, Struct, this

from bluetooth_mesh.messages.generics import (
    OptionalSetParameters,
    TransitionTime,
    TransitionTimeAdapter,
)
from bluetooth_mesh.messages.util import EnumAdapter
from bluetooth_mesh.messages.util import EnumSwitch as Switch
from bluetooth_mesh.messages.util import NamedSelect, Opcode, SwitchStruct


class GenericLevelOpcode(IntEnum):
    GENERIC_LEVEL_GET = 0x8205
    GENERIC_LEVEL_SET = 0x8206
    GENERIC_LEVEL_SET_UNACKNOWLEDGED = 0x8207
    GENERIC_LEVEL_STATUS = 0x8208
    GENERIC_DELTA_SET = 0x8209
    GENERIC_DELTA_SET_UNACKNOWLEDGED = 0x820A
    GENERIC_MOVE_SET = 0x820B
    GENERIC_MOVE_SET_UNACKNOWLEDGED = 0x820C


# fmt: off
GenericLevelGet = Struct()

GenericLevelSetMinimal = Struct(
    "level" / Int16sl,
    "tid" / Int8ul
)

GenericLevelSetOptional = Struct(
    Embedded(GenericLevelSetMinimal),
    Embedded(OptionalSetParameters)
)

GenericLevelSet = NamedSelect(
    optional=GenericLevelSetOptional,
    minimal=GenericLevelSetMinimal
)

GenericDeltaSetMinimal = Struct(
    "delta_level" / Int32sl,
    "tid" / Int8ul
)

GenericDeltaSetOptional = Struct(
    Embedded(GenericDeltaSetMinimal),
    Embedded(OptionalSetParameters)
)

GenericDeltaSet = NamedSelect(
    optional=GenericDeltaSetOptional,
    minimal=GenericDeltaSetMinimal
)

GenericMoveSetMinimal = Struct(
    "delta_level" / Int16sl,
    "tid" / Int8ul
)

GenericMoveSetOptional = Struct(
    Embedded(GenericMoveSetMinimal),
    Embedded(OptionalSetParameters)
)

GenericMoveSet = NamedSelect(
    optional=GenericMoveSetOptional,
    minimal=GenericMoveSetMinimal
)

GenericLevelStatusMinimal = Struct(
    "present_level" / Int16sl
)

GenericLevelStatusOptional = Struct(
    Embedded(GenericLevelStatusMinimal),
    "target_level" / Int16sl,
    "remaining_time" / TransitionTimeAdapter(TransitionTime, allow_unknown=True)
)

GenericLevelStatus = NamedSelect(
    optional=GenericLevelStatusOptional,
    minimal=GenericLevelStatusMinimal
)

GenericLevelMessage = SwitchStruct(
    "opcode" / Opcode(GenericLevelOpcode),
    "params" / Switch(
        this.opcode,
        {
            GenericLevelOpcode.GENERIC_LEVEL_GET: GenericLevelGet,
            GenericLevelOpcode.GENERIC_LEVEL_SET: GenericLevelSet,
            GenericLevelOpcode.GENERIC_LEVEL_SET_UNACKNOWLEDGED: GenericLevelSet,
            GenericLevelOpcode.GENERIC_LEVEL_STATUS: GenericLevelStatus,
            GenericLevelOpcode.GENERIC_DELTA_SET: GenericDeltaSet,
            GenericLevelOpcode.GENERIC_DELTA_SET_UNACKNOWLEDGED: GenericDeltaSet,
            GenericLevelOpcode.GENERIC_MOVE_SET: GenericMoveSet,
            GenericLevelOpcode.GENERIC_MOVE_SET_UNACKNOWLEDGED: GenericMoveSet,
        },
    )
)
# fmt: on

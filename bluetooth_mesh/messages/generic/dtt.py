#
# python-bluetooth-mesh - Bluetooth Mesh for Python
#
# Copyright (C) 2022  Alexander Ozumenko
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

from bluetooth_mesh.messages.generics import (
    TransitionTime,
    TransitionTimeAdapter,
)
from bluetooth_mesh.messages.util import EnumAdapter
from bluetooth_mesh.messages.util import EnumSwitch as Switch
from bluetooth_mesh.messages.util import Opcode, SwitchStruct


class GenericDTTOpcode(IntEnum):
    GENERIC_DTT_GET = 0x820D
    GENERIC_DTT_SET = 0x820E
    GENERIC_DTT_SET_UNACKNOWLEDGED = 0x820F
    GENERIC_DTT_STATUS = 0x8210


# fmt: off
GenericDTTGet = Struct()

GenericDTTSet = Struct(
    "transition_time" / TransitionTimeAdapter(TransitionTime, allow_unknown=False),
)

GenericDTTStatus = Struct(
    "transition_time" / TransitionTimeAdapter(TransitionTime, allow_unknown=False),
)


GenericDTTMessage = SwitchStruct(
    "opcode" / Opcode(GenericDTTOpcode),
    "params" / Switch(
        this.opcode,
        {
            GenericDTTOpcode.GENERIC_DTT_GET: GenericDTTGet,
            GenericDTTOpcode.GENERIC_DTT_SET: GenericDTTSet,
            GenericDTTOpcode.GENERIC_DTT_SET_UNACKNOWLEDGED: GenericDTTSet,
            GenericDTTOpcode.GENERIC_DTT_STATUS: GenericDTTStatus,
        },
    ),
)
# fmt: on

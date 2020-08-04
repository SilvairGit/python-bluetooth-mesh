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

from construct import Flag, GreedyBytes, Int8ul, Int16ul, Padding, Struct, Switch, this

from bluetooth_mesh.messages.util import EnumAdapter


class FdMessageType(IntEnum):
    NETKEY = 0
    APPKEY = 1


# fmt: off
NetKeyMessageElements = Struct(
    "net_index" / Int16ul,
    "remote" / Flag,
    Padding(17)
)

AppKeyMessageElements = Struct(
    "app_index" / Int16ul,
    "destination" / Int16ul,
    "label" / Int8ul,
    Padding(15)
)


FdMessage = Struct(
    "element" / Int8ul,
    "source" / Int16ul,
    "type" / EnumAdapter(Int8ul, FdMessageType),
    "params" / Switch(
        this.type,
        {
            FdMessageType.NETKEY: NetKeyMessageElements,
            FdMessageType.APPKEY: AppKeyMessageElements,
        },
    ),
    "data" / GreedyBytes,
)
# fmt: on

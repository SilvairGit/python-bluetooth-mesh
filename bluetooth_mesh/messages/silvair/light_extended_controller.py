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
from datetime import timedelta
from enum import IntEnum

from construct import (
    Adapter,
    Const,
    Default,
    Flag,
    Int8ul,
    Int16ul,
    Int24ul,
    Struct,
    Switch,
    this,
)

from bluetooth_mesh.messages.util import EnumAdapter, Opcode


class LightExtendedControllerOpcode(IntEnum):
    OPCODE = 0xF63601


class LightExtendedControllerSubOpcode(IntEnum):
    PROPERTY_GET = 0x00
    PROPERTY_SET = 0x01
    PROPERTY_SET_UNACKNOWLEDGED = 0x01
    PROPERTY_STATUS = 0x03
    BULK_LC_PROPERTY_SET = 0x04
    BULK_LC_PROPERTY_STATUS = 0x05
    BULK_LEC_PROPERTY_SET = 0x06
    BULK_LEC_PROPERTY_STATUS = 0x06
    SYNC_INTEGRAL_GET = 0x08
    SYNC_INTEGRAL_STATUS = 0x09


class LightExtendedControllerProperty(IntEnum):
    AUTO_RESUME_MODE = 0xFF71
    AUTO_RESUME_TIMER = 0xFF72


class AutoResumeTimerAdapter(Adapter):
    def _decode(self, obj, context, path):
        return timedelta(milliseconds=obj)

    def _encode(self, obj, context, path):
        return int(obj.total_seconds() * 1000)


# fmt: off
LightExtendedControllerPropertyValue = Switch(
    this.id,
    {
        LightExtendedControllerProperty.AUTO_RESUME_MODE: Flag,
        LightExtendedControllerProperty.AUTO_RESUME_TIMER: AutoResumeTimerAdapter(Int24ul),
    }
)

LightExtendedControllerPropertyGet = Struct(
    "id" / EnumAdapter(Int16ul, LightExtendedControllerProperty),
)

LightExtendedControllerPropertySet = Struct(
    "id" / EnumAdapter(Int16ul, LightExtendedControllerProperty),
    "value" / LightExtendedControllerPropertyValue,
)

LightExtendedControllerPropertyStatus = Struct(
    "id" / EnumAdapter(Int16ul, LightExtendedControllerProperty),
    "value" / LightExtendedControllerPropertyValue,
)

LightExtendedControllerSyncIntegralStatus = Struct(
    "sync_integral" / Int16ul,
)

LightExtendedControllerPayload = Struct(
    "subopcode" / EnumAdapter(Int8ul, LightExtendedControllerSubOpcode),
    "payload" / Default(Switch(
        this.subopcode,
        {
            LightExtendedControllerSubOpcode.PROPERTY_GET: LightExtendedControllerPropertyGet,
            LightExtendedControllerSubOpcode.PROPERTY_SET: LightExtendedControllerPropertySet,
            LightExtendedControllerSubOpcode.PROPERTY_SET_UNACKNOWLEDGED: LightExtendedControllerPropertySet,
            LightExtendedControllerSubOpcode.PROPERTY_STATUS: LightExtendedControllerPropertyStatus,
            LightExtendedControllerSubOpcode.SYNC_INTEGRAL_STATUS: LightExtendedControllerSyncIntegralStatus,
        },
    ), None)
)

LightExtendedControllerMessage = Struct(
    "opcode" / Const(LightExtendedControllerOpcode.OPCODE, Opcode(LightExtendedControllerOpcode)),
    "params" / LightExtendedControllerPayload
)
# fmt: on

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

from construct import (
    Float32l,
    Float64l,
    GreedyRange,
    Int8sl,
    Int8ul,
    Int16sl,
    Int16ul,
    Int32sl,
    Int32ul,
    Int64sl,
    Int64ul,
    PascalString,
    PrefixedArray,
    Struct,
    this,
)

from bluetooth_mesh.messages.util import EnumAdapter
from bluetooth_mesh.messages.util import EnumSwitch as Switch
from bluetooth_mesh.messages.util import Opcode, SwitchStruct


class DebugV2Opcode(IntEnum):
    SILVAIR_DEBUG_V2 = 0xEB3601


class DebugV2SubOpcode(IntEnum):
    GET = 0x00
    SET = 0x01
    STATUS = 0x02
    CLEAR = 0x03


class DebugV2ParameterTypes(IntEnum):
    GETABLE_PARAMETER_LIST = 0x00
    SETABLE_PARAMETER_LIST = 0x01
    SETTABLE_PARAMETER_TYPE_LIST = 0x02
    CLEARABLE_PARAMETER_LIST = 0x03
    RSSI_THRESHOLD = 0x08
    UPTIME = 0x09
    MESH_RPL_LIST_CONTENT = 0x0A
    TIME_SYNC_MSG_LIST = 0x0B
    FIRST_TIME_SYNC_TIMESTAMP = 0x0C
    LAST_TIME_SYNC_TIME = 0x0D
    LAST_TIME_RECOVERY_TIME = 0x0E
    RECALLED_EVENTS_TIME = 0x0F
    RESET_MONITOR_COUNTERS = 0x10
    TIME_RECOVERY_COUNTER = 0x11
    OCCUPANCY_EVENTS_COUNTER = 0x12
    OCCUPANCY_HISTORY = 0x13
    OCCUPANCY_HISTORY_RESOLUTION = 0x14
    RADIO_STATS_PER_CHANNEL = 0x15
    QUEUES_MONITOR = 0x16
    QUEUES_STATS = 0x17
    UART_ERRORS = 0x18
    UART_MODEL_INSTANCES = 0x19
    APP_THREAD_LATENCY = 0x1A
    IV_INDEX_INFO = 0x1B
    MESH_CACHE_INFO = 0x1C
    EL_ELT_HISTORY = 0x1D
    RRULE_SCHEDULE_REGISTER_SIZE = 0x1E
    RRULE_NEXT_EVENT_TAI = 0x1F
    RRULE_NEXT_EVENT_ENTRIES_ARRAY = 0x20
    LAST_CALLS_OF_RRULE_ENTRIES = 0x21

    NOT_KNOWN_PARAMETER = 0xFF

    @classmethod
    def _missing_(cls, value):
        return DebugV2ParameterTypes.NOT_KNOWN_PARAMETER


class DebugV2DataTypes(IntEnum):
    UINT8 = 0x00
    UINT16 = 0x01
    UINT32 = 0x02
    UINT64 = 0x03
    INT8 = 0x04
    INT16 = 0x05
    INT32 = 0x06
    INT64 = 0x07
    FLOAT = 0x08
    DOUBLE = 0x09
    ENUM = 0x0A
    STRING = 0x0B
    ARRAY = 0x0C
    INVALID = 0xFF


# fmt: off
DebugV2Parameter = SwitchStruct(
    "data_type" / EnumAdapter(Int8ul, DebugV2DataTypes),
    "parameter" / Switch(
        this.data_type,
        {
            DebugV2DataTypes.UINT8: Int8ul,
            DebugV2DataTypes.UINT16: Int16ul,
            DebugV2DataTypes.UINT32: Int32ul,
            DebugV2DataTypes.UINT64: Int64ul,
            DebugV2DataTypes.INT8: Int8sl,
            DebugV2DataTypes.INT16: Int16sl,
            DebugV2DataTypes.INT32: Int32sl,
            DebugV2DataTypes.INT64: Int64sl,
            DebugV2DataTypes.FLOAT: Float32l,
            DebugV2DataTypes.DOUBLE: Float64l,
            DebugV2DataTypes.ENUM: Int8ul,
            DebugV2DataTypes.STRING: PascalString(Int8ul, "utf-8"),
            DebugV2DataTypes.ARRAY: PrefixedArray(Int8ul, Int8ul),
            DebugV2DataTypes.INVALID: Struct()
        }
    )
)

DebugV2SubMessage = Struct(
    "subopcode" / EnumAdapter(Int8ul, DebugV2SubOpcode),
    "parameter_type" / Int8ul,
    "page_number" / Int8ul,
    "payload" / GreedyRange(DebugV2Parameter)
)

DebugV2Message = SwitchStruct(
    "opcode" / Opcode(DebugV2Opcode),
    "params" / Switch(
        this.opcode,
        {
            DebugV2Opcode.SILVAIR_DEBUG_V2: DebugV2SubMessage,
        }
    )
)

# fmt: on

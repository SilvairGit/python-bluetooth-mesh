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
    BitsInteger,
    BitStruct,
    ByteSwapped,
    Bytewise,
    Const,
    Default,
    GreedyRange,
    GreedyString,
    Int8ul,
    Int16ul,
    Int24ub,
    Int32ul,
    PaddedString,
    Padding,
    Select,
    Struct,
    this,
)

from bluetooth_mesh.messages.util import DictAdapter, EnumAdapter
from bluetooth_mesh.messages.util import EnumSwitch as Switch
from bluetooth_mesh.messages.util import Opcode, SwitchStruct


class DebugOpcode(IntEnum):
    SILVAIR_DEBUG = 0xF53601


class DebugSubOpcode(IntEnum):
    RSSI_THRESHOLD_GET = 0x00
    RSSI_THRESHOLD_SET = 0x01
    RSSI_THRESHOLD_STATUS = 0x02
    RADIO_TEST = 0x03
    TIMESLOT_TX_POWER_GET = 0x04
    TIMESLOT_TX_POWER_SET = 0x05
    TIMESLOT_TX_POWER_STATUS = 0x06
    SOFTDEVICE_TX_POWER_GET = 0x07
    SOFTDEVICE_TX_POWER_SET = 0x08
    SOFTDEVICE_TX_POWER_STATUS = 0x09
    UPTIME_GET = 0x0A
    UPTIME_STATUS = 0x0B
    LAST_SW_FAULT_GET = 0x0C
    LAST_SW_FAULT_CLEAR = 0x0D
    LAST_SW_FAULT_STATUS = 0x0E
    SYSTEM_STATS_GET = 0x0F
    SYSTEM_STATS_STATUS = 0x10
    LAST_MALLOC_FAULT_GET = 0x11
    LAST_MALLOC_FAULT_CLEAR = 0x12
    LAST_MALLOC_FAULT_STATUS = 0x13
    LAST_FDS_FAULT_GET = 0x14
    LAST_FDS_FAULT_CLEAR = 0x15
    LAST_FDS_FAULT_STATUS = 0x16
    BYTES_BEFORE_GARBAGE_COLLECTOR_GET = 0x17
    BYTES_BEFORE_GARBAGE_COLLECTOR_STATUS = 0x18
    PROVISIONED_APP_VERSION_GET = 0x19
    PROVISIONED_APP_VERSION_STATUS = 0x1A
    FULL_FIRMWARE_VERSION_GET = 0x1B
    FULL_FIRMWARE_VERSION_STATUS = 0x1C
    IV_INDEX_GET = 0x1D
    IV_INDEX_STATUS = 0x1E
    GARBAGE_COLLECTOR_COUNTER_GET = 0x1F
    GARBAGE_COLLECTOR_COUNTER_STATUS = 0x20
    ARAP_LIST_SIZE_GET = 0x21
    ARAP_LIST_SIZE_STATUS = 0x22
    ARAP_LIST_CONTENT_GET = 0x23
    ARAP_LIST_CONTENT_STATUS = 0x24


# fmt: off
RssiThreshold = Struct(
    "rssi_threshold" / Int8ul
)

RadioTest = Struct(
    "packet_counter" / Int8ul
)

TxPower = Struct(
    "tx_power" / Int8ul
)

UptimeStatus = Struct(
    "uptime" / Int32ul
)

LastFault = Struct(
    "time" / Int32ul,
    "fault" / GreedyString("utf8")
)

SystemStat = Struct(
    "name" / PaddedString(8, "utf8"),
    "high_water_mark" / Int16ul,
    "rfu" / Padding(4),
)

SystemStats = Struct(
    "stats" / DictAdapter(
        GreedyRange(SystemStat),
        key=this.name,
        value=this.high_water_mark
    )
)

GarbageCollector = Struct(
    "bytes_left" / Int16ul
)

AppVersion = Struct(
    "version" / Int16ul
)

FirmwareVersion = Struct(
    "version" / GreedyString("utf8")
)

IvIndex = Struct(
    "ivindex" / Int32ul
)

GarbageCollectorCounter = Struct(
    "counter" / Int16ul
)

ArapSize16 = Struct(
    "capacity" / Int16ul,
    "size" / Int16ul
)

ArapSize8 = Struct(
    "capacity" / Int8ul,
    "size" / Int8ul
)

ArapSize = Select(
    new=ArapSize16,
    old=ArapSize8,
)

ArapContentGet = Struct(
    "page" / Int8ul
)

ArapNode = ByteSwapped(
    BitStruct(
        "sequence" / Bytewise(Int24ub),
        "ivi" / BitsInteger(1),
        "address" / BitsInteger(15),
    )
)

ArapContent = Struct(
    "current_page" / Int8ul,
    "last_page" / Int8ul,
    "nodes" / DictAdapter(
        GreedyRange(ArapNode),
        key=this.address,
        value=[this.ivi, this.sequence]
    )
)

DebugParams = SwitchStruct(
    "subopcode" / EnumAdapter(Int8ul, DebugSubOpcode),
    "payload" / Switch(
        this.subopcode,
        {
            DebugSubOpcode.RSSI_THRESHOLD_SET: RssiThreshold,
            DebugSubOpcode.RSSI_THRESHOLD_STATUS: RssiThreshold,
            DebugSubOpcode.RADIO_TEST: RadioTest,
            DebugSubOpcode.TIMESLOT_TX_POWER_SET: TxPower,
            DebugSubOpcode.TIMESLOT_TX_POWER_STATUS: TxPower,
            DebugSubOpcode.SOFTDEVICE_TX_POWER_SET: TxPower,
            DebugSubOpcode.SOFTDEVICE_TX_POWER_STATUS: TxPower,
            DebugSubOpcode.UPTIME_STATUS: UptimeStatus,
            DebugSubOpcode.LAST_SW_FAULT_STATUS: LastFault,
            DebugSubOpcode.SYSTEM_STATS_STATUS: SystemStats,
            DebugSubOpcode.LAST_MALLOC_FAULT_STATUS: LastFault,
            DebugSubOpcode.LAST_FDS_FAULT_STATUS: LastFault,
            DebugSubOpcode.BYTES_BEFORE_GARBAGE_COLLECTOR_STATUS: GarbageCollector,
            DebugSubOpcode.PROVISIONED_APP_VERSION_STATUS: AppVersion,
            DebugSubOpcode.FULL_FIRMWARE_VERSION_STATUS: FirmwareVersion,
            DebugSubOpcode.IV_INDEX_STATUS: IvIndex,
            DebugSubOpcode.GARBAGE_COLLECTOR_COUNTER_STATUS: GarbageCollectorCounter,
            DebugSubOpcode.ARAP_LIST_SIZE_STATUS: ArapSize,
            DebugSubOpcode.ARAP_LIST_CONTENT_GET: ArapContentGet,
            DebugSubOpcode.ARAP_LIST_CONTENT_STATUS: ArapContent,
        }
    )
)

DebugMessage = SwitchStruct(
    "opcode" / Opcode(DebugOpcode),
    "params" / Switch(
        this.opcode,
        {
            DebugOpcode.SILVAIR_DEBUG: DebugParams,
        }
    )
)
# fmt: on

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

from bluetooth_mesh.messages.util import EnumAdapter
from bluetooth_mesh.messages.util import EnumSwitch as Switch
from bluetooth_mesh.messages.util import NamedSelect, Opcode, SwitchStruct


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
RssiThresholdGet = Struct()

RssiThreshold = Struct(
    "rssi_threshold" / Int8ul
)

RadioTest = Struct(
    "packet_counter" / Int8ul
)

TimeslotTxPowerGet = Struct()

TimeslotTxPowerStatus = Struct(
    "tx_power" / Int8ul
)

SoftdeviceTxPowerGet = Struct()

SoftdeviceTxPowerStatus = Struct(
    "tx_power" / Int8ul
)

UptimeGet = Struct()

UptimeStatus = Struct(
    "uptime" / Int32ul
)

LastSwFaultGet = Struct()

LastSwFaultClear = Struct()

LastSwFaultStatus = Struct(
    "time" / Int32ul,
    "fault" / GreedyString("utf8")
)

SystemStatsGet = Struct()

SystemStat = Struct(
    "name" / PaddedString(8, "utf8"),
    "high_water_mark" / Int32ul,
    "_rfu" / Padding(2)
)

SystemStatsStatus = Struct(
    "stats" / GreedyRange(SystemStat)
)

LastMallocFaultGet = Struct()

LastMallocFaultClear = Struct()

LastMallocFaultStatus = LastSwFaultStatus

LastFdsFaultGet = Struct()

LastFdsFaultClear = Struct()

LastFdsFaultStatus = LastSwFaultStatus

BytesBeforeGarbageCollectorGet = Struct()

BytesBeforeGarbageCollectorStatus = Struct(
    "bytes_left" / Int16ul
)

ProvisionedAppVersionGet = Struct()

ProvisionedAppVersionStatus = Struct(
    "version" / Int16ul
)

FullFirmwareVersionGet = Struct()

FullFirmwareVersionStatus = Struct(
    "version" / GreedyString("utf8")
)

IvIndexGet = Struct()

IvIndexStatus = Struct(
    "ivindex" / Int32ul
)

GarbageCollectorCounterGet = Struct()

GarbageCollectorCounterStatus = Struct(
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

ArapListSizeGet = Struct()

ArapListSizeStatus = NamedSelect(
    new=ArapSize16,
    old=ArapSize8,
)

ArapListContentGet = Struct(
    "page" / Int8ul
)

ArapNode = ByteSwapped(
    BitStruct(
        "sequence" / Bytewise(Int24ub),
        "ivi" / BitsInteger(1),
        "address" / BitsInteger(15),
    )
)

ArapListContentStatus = Struct(
    "current_page" / Int8ul,
    "last_page" / Int8ul,
    "nodes" / GreedyRange(ArapNode)
)

DebugParams = SwitchStruct(
    "subopcode" / EnumAdapter(Int8ul, DebugSubOpcode),
    "payload" / Switch(
        this.subopcode,
        {
            DebugSubOpcode.RSSI_THRESHOLD_GET: RssiThresholdGet,
            DebugSubOpcode.RSSI_THRESHOLD_SET: RssiThreshold,
            DebugSubOpcode.RSSI_THRESHOLD_STATUS: RssiThreshold,
            DebugSubOpcode.RADIO_TEST: RadioTest,
            DebugSubOpcode.TIMESLOT_TX_POWER_GET: TimeslotTxPowerGet,
            DebugSubOpcode.TIMESLOT_TX_POWER_SET: TimeslotTxPowerStatus,
            DebugSubOpcode.TIMESLOT_TX_POWER_STATUS: TimeslotTxPowerStatus,
            DebugSubOpcode.SOFTDEVICE_TX_POWER_GET: SoftdeviceTxPowerGet,
            DebugSubOpcode.SOFTDEVICE_TX_POWER_SET: SoftdeviceTxPowerStatus,
            DebugSubOpcode.SOFTDEVICE_TX_POWER_STATUS: SoftdeviceTxPowerStatus,
            DebugSubOpcode.UPTIME_GET: UptimeGet,
            DebugSubOpcode.UPTIME_STATUS: UptimeStatus,
            DebugSubOpcode.LAST_SW_FAULT_GET: LastSwFaultGet,
            DebugSubOpcode.LAST_SW_FAULT_CLEAR: LastSwFaultClear,
            DebugSubOpcode.LAST_SW_FAULT_STATUS: LastSwFaultStatus,
            DebugSubOpcode.SYSTEM_STATS_GET: SystemStatsGet,
            DebugSubOpcode.SYSTEM_STATS_STATUS: SystemStatsStatus,
            DebugSubOpcode.LAST_MALLOC_FAULT_GET: LastMallocFaultGet,
            DebugSubOpcode.LAST_MALLOC_FAULT_CLEAR: LastMallocFaultClear,
            DebugSubOpcode.LAST_MALLOC_FAULT_STATUS: LastMallocFaultStatus,
            DebugSubOpcode.LAST_FDS_FAULT_GET: LastFdsFaultGet,
            DebugSubOpcode.LAST_FDS_FAULT_CLEAR: LastFdsFaultClear,
            DebugSubOpcode.LAST_FDS_FAULT_STATUS: LastFdsFaultStatus,
            DebugSubOpcode.BYTES_BEFORE_GARBAGE_COLLECTOR_GET: BytesBeforeGarbageCollectorGet,
            DebugSubOpcode.BYTES_BEFORE_GARBAGE_COLLECTOR_STATUS: BytesBeforeGarbageCollectorStatus,
            DebugSubOpcode.PROVISIONED_APP_VERSION_GET: ProvisionedAppVersionGet,
            DebugSubOpcode.PROVISIONED_APP_VERSION_STATUS: ProvisionedAppVersionStatus,
            DebugSubOpcode.FULL_FIRMWARE_VERSION_GET: FullFirmwareVersionGet,
            DebugSubOpcode.FULL_FIRMWARE_VERSION_STATUS: FullFirmwareVersionStatus,
            DebugSubOpcode.IV_INDEX_GET: IvIndexGet,
            DebugSubOpcode.IV_INDEX_STATUS: IvIndexStatus,
            DebugSubOpcode.GARBAGE_COLLECTOR_COUNTER_GET: GarbageCollectorCounterGet,
            DebugSubOpcode.GARBAGE_COLLECTOR_COUNTER_STATUS: GarbageCollectorCounterStatus,
            DebugSubOpcode.ARAP_LIST_SIZE_GET: ArapListSizeGet,
            DebugSubOpcode.ARAP_LIST_SIZE_STATUS: ArapListSizeStatus,
            DebugSubOpcode.ARAP_LIST_CONTENT_GET: ArapListContentGet,
            DebugSubOpcode.ARAP_LIST_CONTENT_STATUS: ArapListContentStatus,
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

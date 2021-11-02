#
# python-bluetooth-mesh - Bluetooth Mesh for Python
#
# Copyright (C) 2021  SILVAIR sp. z o.o.
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
import calendar
import enum
import time
from datetime import datetime, timedelta, timezone

from construct import (
    Adapter,
    BitsInteger,
    BitStruct,
    BytesInteger,
    Construct,
    Container,
    Flag,
    Int8sl,
    Int8ul,
    Int16sl,
    Int16ul,
    Padding,
    StopIf,
    Struct,
    stream_read,
    stream_write,
    this,
)

from bluetooth_mesh.messages.util import EmbeddedBitStruct, EnumAdapter
from bluetooth_mesh.messages.util import EnumSwitch as Switch
from bluetooth_mesh.messages.util import NamedSelect, Opcode, Reversed, SwitchStruct

# fmt: off

SchedulerGet = Struct()

SchedulerStatus = Struct()

SchedulerActionGet = Struct()

SchedulerActionSet = Struct(
    "index" / Int8ul,
    "start" / Struct(
        "year" / Int16ul,
        "month" / Int8ul,
        "day" / Int8ul,
        "hour" / Int8ul,
        "minute" / Int8ul,
        "second" / Int8ul,
    ),
    "recurrence" / Struct(
        "frequency" / Int8ul,
        "skip" / Int8ul,
        "interval" / Int16ul,
    ),
    "by_second" / Int8sl,
    "by_minute" / Int8sl,
    "by_hour" / Int8sl,
    "by_day" / Int8sl,
    "by_month_day" / Int8sl,
    "by_year_day" / Int16sl,
    "by_week_no" / Int8sl,
    "by_month" / Int8sl,
    "by_set_pos" / Int16sl,
)

SchedulerActionStatus = Struct()


class SchedulerOpcode(enum.IntEnum):
    SCHEDULER_GET = 0x8249
    SCHEDULER_STATUS = 0x824a
    SCHEDULER_ACTION_GET = 0x8248
    SCHEDULER_ACTION_STATUS = 0x5f

class SchedulerSetupOpcode(enum.IntEnum):
    SCHEDULER_ACTION_SET = 0x60
    SCHEDULER_ACTION_SET_UNACKNOWLEDGED = 0x61


SchedulerMessage = SwitchStruct(
    "opcode" / Opcode(SchedulerOpcode),
    "params" / Switch(
        this.opcode,
        {
            SchedulerOpcode.SCHEDULER_GET: SchedulerGet,
            SchedulerOpcode.SCHEDULER_STATUS: SchedulerStatus,
            SchedulerOpcode.SCHEDULER_ACTION_GET: SchedulerActionGet,
            SchedulerOpcode.SCHEDULER_ACTION_STATUS: SchedulerActionStatus,
        }
    )
)

SchedulerSetupMessage = SwitchStruct(
    "opcode" / Opcode(SchedulerSetupOpcode),
    "params" / Switch(
        this.opcode,
        {
            SchedulerSetupOpcode.SCHEDULER_ACTION_SET: SchedulerActionSet,
            SchedulerSetupOpcode.SCHEDULER_ACTION_SET_UNACKNOWLEDGED: SchedulerActionSet,
        }
    )
)
# fmt: on

#
# python-bluetooth-mesh - Bluetooth Mesh for Python
#
# Copyright (C) 2022  SILVAIR sp. z o.o.
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
    Embedded,
    GreedyBytes,
    GreedyRange,
    Int8sl,
    Int8ul,
    Int16sl,
    Int16ul,
    Int32ul,
    Optional,
    Prefixed,
    PrefixedArray,
    Struct,
    this,
)

from bluetooth_mesh.messages.util import EnumAdapter
from bluetooth_mesh.messages.util import EnumSwitch as Switch
from bluetooth_mesh.messages.util import NamedSelect, Opcode, SetAdapter, SwitchStruct


class RRuleSchedulerOpcode(IntEnum):
    SILVAIR_RRULE_SCHEDULER = 0xE83601


class RRuleSchedulerSubOpcode(IntEnum):
    RULES_LIST_GET = 0x00
    RULES_LIST_STATUS = 0x01
    REGISTER_MAX_SIZE_GET = 0x02
    REGISTER_MAX_SIZE_STATUS = 0x03
    SCHEDULER_MODE_GET = 0x04
    SCHEDULER_MODE_SET = 0x05
    SCHEDULER_MODE_STATUS = 0x06
    SCHEDULE_REGISTER_ENTRY_GET = 0x07
    SCHEDULE_REGISTER_ENTRY_SET = 0x08
    SCHEDULE_REGISTER_ENTRY_DELETE = 0x09
    SCHEDULE_REGISTER_ENTRY_DELETE_ALL = 0x0A
    SCHEDULE_REGISTER_ENTRY_STATUS = 0x0B
    SCHEDULE_REGISTER_LIST_GET = 0x0C
    SCHEDULE_REGISTER_LIST_STATUS = 0x0D


class SchedulerModes(IntEnum):
    DISABLED = 0x00
    ENABLED = 0x01


class Days(IntEnum):
    PREVIOUS_SUNDAY = -7
    PREVIOUS_SATURDAY = -6
    PREVIOUS_FRIDAY = -5
    PREVIOUS_THURSDAY = -4
    PREVIOUS_WEDNESDAY = -3
    PREVIOUS_TUESDAY = -2
    PREVIOUS_MONDAY = -1
    NEXT_MONDAY = 1
    NEXT_TUESDAY = 2
    NEXT_WEDNESDAY = 3
    NEXT_THURSDAY = 4
    NEXT_FRIDAY = 5
    NEXT_SATURDAY = 6
    NEXT_SUNDAY = 7


class StatusCodes(IntEnum):
    SUCCESS = 0x00
    INVALID_SLOT = 0x01
    INVALID_SLOT_PARAMETERS = 0x02
    INVALID_RULE = 0x03
    INVALID_RULE_VALUE = 0x04
    REGISTER_SIZE_EXCEEDED = 0x05
    STORAGE_FAILURE = 0x06


class RuleIDs(IntEnum):
    FREQ = 0x00
    UNTIL = 0x01
    COUNT = 0x02
    INTERVAL = 0x03
    BYSECOND = 0x04
    BYMINUTE = 0x05
    BYHOUR = 0x06
    BYDAY = 0x07
    BYMONTHDAY = 0x08
    BYYEARDAY = 0x09
    BYWEEKNO = 0x0A
    BYMONTH = 0x0B
    BYSETPOS = 0x0C
    DTSTART = 0x0D
    EXPLICIT_RDATE = 0x0E
    EXCLUSIONS_RDATE = 0x0F


class Freqs(IntEnum):
    SECONDLY = 0x00
    MINUTELY = 0x01
    HOURLY = 0x02
    DAILY = 0x03
    WEEKLY = 0x04
    MONTHLY = 0x05
    YEARLY = 0x06


# fmt: off
Slots = Struct(
    "slot_id" / Int16ul,
    "element" / Int8ul,
    "slot_parameter" / Prefixed(Int8ul, GreedyBytes),
)

DateTime = ByteSwapped(
    BitStruct(
        "second" / BitsInteger(6),
        "minute" / BitsInteger(6),
        "hour" / BitsInteger(5),
        "day" / BitsInteger(5),
        "month" / BitsInteger(4),
        "year" / BitsInteger(14),
    )
)

RuleID = EnumAdapter(Int8ul, RuleIDs)

Freq = EnumAdapter(Int8ul, Freqs)

Day = EnumAdapter(Int8sl, Days)

Rules = Struct(
    "rule_id" / RuleID,
    "rule" / Switch(
        this.rule_id,
        {
            RuleIDs.FREQ: Freq,
            RuleIDs.UNTIL: DateTime,
            RuleIDs.COUNT: Int16ul,
            RuleIDs.INTERVAL: Int16ul,
            RuleIDs.BYSECOND: PrefixedArray(Int8ul, Int8ul),
            RuleIDs.BYMINUTE: PrefixedArray(Int8ul, Int8ul),
            RuleIDs.BYHOUR: PrefixedArray(Int8ul, Int8ul),
            RuleIDs.BYDAY: PrefixedArray(Int8ul, Day),
            RuleIDs.BYMONTHDAY: PrefixedArray(Int8ul, Int8sl),
            RuleIDs.BYYEARDAY: PrefixedArray(Int8ul, Int16sl),
            RuleIDs.BYWEEKNO: PrefixedArray(Int8ul, Int8sl),
            RuleIDs.BYMONTH: Int16ul,
            RuleIDs.BYSETPOS: PrefixedArray(Int8ul, Int16sl),
            RuleIDs.DTSTART: DateTime,
            RuleIDs.EXPLICIT_RDATE: PrefixedArray(Int8ul, DateTime),
            RuleIDs.EXCLUSIONS_RDATE: PrefixedArray(Int8ul, DateTime),
        },
    ),
)

SchedulerRegisterEntry = Struct(
    "array_of_slots" / PrefixedArray(Int8ul, Slots),
    "rules" / GreedyRange(Rules)
)

RulesListGet = Struct()

RulesListStatus = Struct(
    "rule_ids" / SetAdapter(GreedyRange(RuleID))
)

RegisterMaxSizeGet = Struct()

RegisterMaxSizeStatus = Struct(
    "register_max_size" / Int32ul
)

SchedulerModeGet = Struct()

SchedulerModeSet = Struct(
    "scheduler_mode" / EnumAdapter(Int8ul, SchedulerModes)
)

SchedulerModeStatus = SchedulerModeSet

ScheduleRegisterEntryGet = Struct(
    "entry_id" / Int8ul
)

ScheduleRegisterEntrySet = Struct(
    "entry_id" / Int8ul,
    "scheduler_register_entry" / SchedulerRegisterEntry
)

ScheduleRegisterEntryDelete = ScheduleRegisterEntryGet

ScheduleRegisterEntryDeleteAll = Struct()

ScheduleRegisterEntryStatusMinimal = Struct(
    "entry_id" / Int8ul,
    "status" / EnumAdapter(Int8ul, StatusCodes),
)

ScheduleRegisterEntryStatusOptional = Struct(
    Embedded(ScheduleRegisterEntryStatusMinimal),
    "scheduler_register_entry" / SchedulerRegisterEntry,
)

ScheduleRegisterEntryStatus = NamedSelect(
    optional=ScheduleRegisterEntryStatusOptional,
    minimal=ScheduleRegisterEntryStatusMinimal
)

ScheduleRegisterListGet = Struct()

ScheduleRegisterListStatus = Struct(
    "entry_ids" / SetAdapter(GreedyRange(Int8ul))
)

RRuleSchedulerSubMessage = Struct(
    "subopcode" / EnumAdapter(Int8ul, RRuleSchedulerSubOpcode),
    "payload" / Switch(
        this.subopcode,
        {
            RRuleSchedulerSubOpcode.RULES_LIST_GET: RulesListGet,
            RRuleSchedulerSubOpcode.RULES_LIST_STATUS: RulesListStatus,
            RRuleSchedulerSubOpcode.REGISTER_MAX_SIZE_GET: RegisterMaxSizeGet,
            RRuleSchedulerSubOpcode.REGISTER_MAX_SIZE_STATUS: RegisterMaxSizeStatus,
            RRuleSchedulerSubOpcode.SCHEDULER_MODE_GET: SchedulerModeGet,
            RRuleSchedulerSubOpcode.SCHEDULER_MODE_SET: SchedulerModeSet,
            RRuleSchedulerSubOpcode.SCHEDULER_MODE_STATUS: SchedulerModeStatus,
            RRuleSchedulerSubOpcode.SCHEDULE_REGISTER_ENTRY_GET: ScheduleRegisterEntryGet,
            RRuleSchedulerSubOpcode.SCHEDULE_REGISTER_ENTRY_SET: ScheduleRegisterEntrySet,
            RRuleSchedulerSubOpcode.SCHEDULE_REGISTER_ENTRY_DELETE: ScheduleRegisterEntryDelete,
            RRuleSchedulerSubOpcode.SCHEDULE_REGISTER_ENTRY_DELETE_ALL: ScheduleRegisterEntryDeleteAll,
            RRuleSchedulerSubOpcode.SCHEDULE_REGISTER_ENTRY_STATUS: ScheduleRegisterEntryStatus,
            RRuleSchedulerSubOpcode.SCHEDULE_REGISTER_LIST_GET: ScheduleRegisterListGet,
            RRuleSchedulerSubOpcode.SCHEDULE_REGISTER_LIST_STATUS: ScheduleRegisterListStatus,
        },
    ),
)

RRuleSchedulerMessage = SwitchStruct(
    "opcode" / Opcode(RRuleSchedulerOpcode),
    "params" / Switch(
        this.opcode,
        {
            RRuleSchedulerOpcode.SILVAIR_RRULE_SCHEDULER: RRuleSchedulerSubMessage,
        },
    ),
)
# fmt: on

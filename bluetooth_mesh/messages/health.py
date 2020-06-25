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
import enum

from construct import (
    Default,
    ExprValidator,
    GreedyRange,
    Int8ul,
    Int16ul,
    Struct,
    Switch,
    obj_,
    this,
)

from .util import EnumAdapter, Opcode

# fmt: off
FaultTest = Struct(
    "test_id" / Int8ul,
    "company_id" / Int16ul,
)

FaultStatus = Struct(
    "test_id" / Int8ul,
    "company_id" / Int16ul,
    "fault_array" / Default(GreedyRange(Int8ul), [])
)

FastPeriodDivisor = Struct(
    "fast_period_divisor" / ExprValidator(Int8ul, obj_ <= 15)
)

Attention = Struct(
    "attention" / Int8ul
)

CompanyId = Struct(
    "company_id" / Int16ul
)

HealthCurrentStatus = FaultStatus

HealthFaultGet = CompanyId

HealthFaultClear = CompanyId

HealthFaultTest = FaultTest

HealthFaultStatus = FaultStatus

HealthPeriodGet = Struct()

HealthPeriodSet = FastPeriodDivisor

HealthPeriodStatus = FastPeriodDivisor

HealthAttentionGet = Struct()

HealthAttentionSet = Attention

HealthAttentionStatus = Attention
# fmt: off

class HealthOpcode(enum.IntEnum):
    ATTENTION_GET = 0x8004
    ATTENTION_SET = 0x8005
    ATTENTION_SET_UNACKNOWLEDGED = 0x8006
    ATTENTION_STATUS = 0x8007
    CURRENT_STATUS = 0x04
    FAULT_CLEAR = 0x802F
    FAULT_CLEAR_UNACKNOWLEDGED = 0x8030
    FAULT_GET = 0x8031
    FAULT_STATUS = 0x05
    FAULT_TEST = 0x8032
    FAULT_TEST_UNACKNOWLEDGED = 0x8033
    PERIOD_GET = 0x8034
    PERIOD_SET = 0x8035
    PERIOD_SET_UNACKNOWLEDGED = 0x8036
    PERIOD_STATUS = 0x8037


# fmt: off
HealthMessage = Struct(
    "opcode" / Opcode(HealthOpcode),
    "params" / Switch(
        this.opcode,
        {
            HealthOpcode.ATTENTION_GET: HealthAttentionGet,
            HealthOpcode.ATTENTION_SET: HealthAttentionSet,
            HealthOpcode.ATTENTION_SET_UNACKNOWLEDGED: HealthAttentionSet,
            HealthOpcode.ATTENTION_STATUS: HealthAttentionStatus,
            HealthOpcode.CURRENT_STATUS: HealthCurrentStatus,
            HealthOpcode.FAULT_CLEAR: HealthFaultClear,
            HealthOpcode.FAULT_CLEAR_UNACKNOWLEDGED: HealthFaultClear,
            HealthOpcode.FAULT_GET: HealthFaultGet,
            HealthOpcode.FAULT_STATUS: HealthCurrentStatus,
            HealthOpcode.FAULT_TEST: HealthFaultTest,
            HealthOpcode.FAULT_TEST_UNACKNOWLEDGED: HealthFaultTest,
            HealthOpcode.PERIOD_GET: HealthPeriodGet,
            HealthOpcode.PERIOD_SET: HealthPeriodSet,
            HealthOpcode.PERIOD_SET_UNACKNOWLEDGED: HealthPeriodSet,
            HealthOpcode.PERIOD_STATUS: HealthPeriodStatus,
        }
    )
)
# fmt: on

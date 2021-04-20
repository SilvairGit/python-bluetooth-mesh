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
    obj_,
    this,
)

from bluetooth_mesh.messages.util import EnumAdapter
from bluetooth_mesh.messages.util import EnumSwitch as Switch
from bluetooth_mesh.messages.util import Opcode, SwitchStruct

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
    HEALTH_ATTENTION_GET = 0x8004
    HEALTH_ATTENTION_SET = 0x8005
    HEALTH_ATTENTION_SET_UNACKNOWLEDGED = 0x8006
    HEALTH_ATTENTION_STATUS = 0x8007
    HEALTH_CURRENT_STATUS = 0x04
    HEALTH_FAULT_CLEAR = 0x802F
    HEALTH_FAULT_CLEAR_UNACKNOWLEDGED = 0x8030
    HEALTH_FAULT_GET = 0x8031
    HEALTH_FAULT_STATUS = 0x05
    HEALTH_FAULT_TEST = 0x8032
    HEALTH_FAULT_TEST_UNACKNOWLEDGED = 0x8033
    HEALTH_PERIOD_GET = 0x8034
    HEALTH_PERIOD_SET = 0x8035
    HEALTH_PERIOD_SET_UNACKNOWLEDGED = 0x8036
    HEALTH_PERIOD_STATUS = 0x8037


# fmt: off
HealthMessage = SwitchStruct(
    "opcode" / Opcode(HealthOpcode),
    "params" / Switch(
        this.opcode,
        {
            HealthOpcode.HEALTH_ATTENTION_GET: HealthAttentionGet,
            HealthOpcode.HEALTH_ATTENTION_SET: HealthAttentionSet,
            HealthOpcode.HEALTH_ATTENTION_SET_UNACKNOWLEDGED: HealthAttentionSet,
            HealthOpcode.HEALTH_ATTENTION_STATUS: HealthAttentionStatus,
            HealthOpcode.HEALTH_CURRENT_STATUS: HealthCurrentStatus,
            HealthOpcode.HEALTH_FAULT_CLEAR: HealthFaultClear,
            HealthOpcode.HEALTH_FAULT_CLEAR_UNACKNOWLEDGED: HealthFaultClear,
            HealthOpcode.HEALTH_FAULT_GET: HealthFaultGet,
            HealthOpcode.HEALTH_FAULT_STATUS: HealthCurrentStatus,
            HealthOpcode.HEALTH_FAULT_TEST: HealthFaultTest,
            HealthOpcode.HEALTH_FAULT_TEST_UNACKNOWLEDGED: HealthFaultTest,
            HealthOpcode.HEALTH_PERIOD_GET: HealthPeriodGet,
            HealthOpcode.HEALTH_PERIOD_SET: HealthPeriodSet,
            HealthOpcode.HEALTH_PERIOD_SET_UNACKNOWLEDGED: HealthPeriodSet,
            HealthOpcode.HEALTH_PERIOD_STATUS: HealthPeriodStatus,
        }
    )
)
# fmt: on

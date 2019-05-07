import enum

from construct import (
    Int8ul, Int16ul, Int16ub,
    Default, Enum, Struct, Switch,
    GreedyRange, Padding, Default,
    ExprValidator, obj_, this
)

from .util import EnumAdapter, Opcode


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


HealthMessage = Struct(
    "opcode" / EnumAdapter(Opcode, HealthOpcode),
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

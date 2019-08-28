from construct import Int8ul, Int16ul, Select, Struct, Switch, this, Embedded
from enum import IntEnum
from bluetooth_mesh.messages.util import EnumAdapter, Opcode
from bluetooth_mesh.messages.generics import OptionalSetParameters, TransitionTimeAdapter, TransitionTime
from bluetooth_mesh.messages.config import StatusCodeAdapter


class LightCTLOpcode(IntEnum):
    CTL_GET = 0x825D
    CTL_SET = 0x825E
    CTL_SET_UNACKNOWLEDGED = 0x825F
    CTL_STATUS = 0x8260
    CTL_TEMPERATURE_GET = 0x8261
    CTL_TEMPERATURE_RANGE_GET = 0x8262
    CTL_TEMPERATURE_RANGE_STATUS = 0x8263
    CTL_TEMPERATURE_SET = 0x8264
    CTL_TEMPERATURE_SET_UNACKNOWLEDGED = 0x8265
    CTL_TEMPERATURE_STATUS = 0x8266
    CTL_TEMPERATURE_DEFAULT_GET = 0x8267
    CTL_TEMPERATURE_DEFAULT_STATUS = 0x8268


class LightCTLSetupOpcode(IntEnum):
    CTL_TEMPERATURE_DEFAULT_SET = 0x8269
    CTL_TEMPERATURE_DEFAULT_SET_UNACKNOWLEDGED = 0x826A
    CTL_TEMPERATURE_RANGE_SET = 0x826B
    CTL_TEMPERATURE_RANGE_SET_UNACKNOWLEDGED = 0x826C


LightCTLGet = Struct()

LightCTLDefault = Struct(
    "ctl_lightness" / Int16ul,
    "ctl_temperature" / Int16ul,
    "ctl_delta_uv" / Int16ul
)

LightCTLSetMinimal = Struct(
    Embedded(LightCTLDefault),
    "tid" / Int8ul
)

LightCTLSetOptional = Struct(
    Embedded(LightCTLSetMinimal),
    Embedded(OptionalSetParameters)
)

LightCTLSet = Select(
    LightCTLSetOptional,
    LightCTLSetMinimal
)

LightCTLStatusMinimal = Struct(
    "present_ctl_lightness" / Int16ul,
    "present_ctl_temperature" / Int16ul,
)

LightCTLStatusOptional = Struct(
    Embedded(LightCTLStatusMinimal),
    "target_ctl_lightness" / Int16ul,
    "target_ctl_temperature" / Int16ul,
    "remaining_time" / TransitionTimeAdapter(TransitionTime, allow_unknown=True)
)

LightCTLStatus = Select(
    LightCTLStatusOptional,
    LightCTLStatusMinimal
)

LightCTLTemperatureStatusMinimal = Struct(
    "present_ctl_temperature" / Int16ul,
    "present_ctl_delta_uv" / Int16ul,
)

LightCTLTemperatureStatusOptional = Struct(
    Embedded(LightCTLTemperatureStatusMinimal),
    "target_ctl_temperature" / Int16ul,
    "target_ctl_delta_uv" / Int16ul,
    "remaining_time" / TransitionTimeAdapter(TransitionTime, allow_unknown=True)
)

LightCTLTemperatureStatus = Select(
    LightCTLTemperatureStatusOptional,
    LightCTLTemperatureStatusMinimal
)

LightCTLTemperatureSetMinimal = Struct(
    "ctl_temperature" / Int16ul,
    "ctl_delta_uv" / Int16ul,
    "tid" / Int8ul
)

LightCTLTemperatureSetOptional = Struct(
    Embedded(LightCTLTemperatureSetMinimal),
    Embedded(OptionalSetParameters)
)

LightCTLTemperatureSet = Select(
    LightCTLTemperatureSetOptional,
    LightCTLTemperatureSetMinimal
)

LightCTLRange = Struct(
    "range_min" / Int16ul,
    "range_max" / Int16ul,
)

LightCTLRangeStatus = Struct(
    "status" / StatusCodeAdapter,
    Embedded(LightCTLRange)
)


LightCTLMessage = Struct(
    "opcode" / EnumAdapter(Opcode, LightCTLOpcode),
    "params" / Switch(
        this.opcode,
        {
            LightCTLOpcode.CTL_GET: LightCTLGet,
            LightCTLOpcode.CTL_SET: LightCTLSet,
            LightCTLOpcode.CTL_SET_UNACKNOWLEDGED: LightCTLSet,
            LightCTLOpcode.CTL_STATUS: LightCTLStatus,
            LightCTLOpcode.CTL_TEMPERATURE_GET: LightCTLGet,
            LightCTLOpcode.CTL_TEMPERATURE_RANGE_GET: LightCTLGet,
            LightCTLOpcode.CTL_TEMPERATURE_RANGE_STATUS: LightCTLRangeStatus,
            LightCTLOpcode.CTL_TEMPERATURE_SET: LightCTLTemperatureSet,
            LightCTLOpcode.CTL_TEMPERATURE_SET_UNACKNOWLEDGED: LightCTLTemperatureSet,
            LightCTLOpcode.CTL_TEMPERATURE_STATUS: LightCTLTemperatureStatus,
            LightCTLOpcode.CTL_TEMPERATURE_DEFAULT_GET: LightCTLGet,
            LightCTLOpcode.CTL_TEMPERATURE_DEFAULT_STATUS: LightCTLDefault,
        },
    )
)


LightCTLSetupMessage = Struct(
    "opcode" / EnumAdapter(Opcode, LightCTLSetupOpcode),
    "params" / Switch(
        this.opcode,
        {
            LightCTLSetupOpcode.CTL_TEMPERATURE_DEFAULT_SET: LightCTLDefault,
            LightCTLSetupOpcode.CTL_TEMPERATURE_DEFAULT_SET_UNACKNOWLEDGED: LightCTLDefault,
            LightCTLSetupOpcode.CTL_TEMPERATURE_RANGE_SET: LightCTLRange,
            LightCTLSetupOpcode.CTL_TEMPERATURE_RANGE_SET_UNACKNOWLEDGED: LightCTLRange,
        },
    )
)

from construct import Int8ul, Int16ul, Select, Struct, Switch, this, Embedded
from enum import IntEnum
from bluetooth_mesh.messages.util import EnumAdapter, Opcode
from bluetooth_mesh.messages.generics import OptionalSetParameters, TransitionTimeAdapter, TransitionTime
from bluetooth_mesh.messages.config import StatusCodeAdapter


class LightLightnessOpcode(IntEnum):
    LIGHTNESS_GET = 0x824B
    LIGHTNESS_SET = 0x824C
    LIGHTNESS_SET_UNACKNOWLEDGED = 0x824D
    LIGHTNESS_STATUS = 0x824E
    LIGHTNESS_LINEAR_GET = 0x824F
    LIGHTNESS_LINEAR_SET = 0x8250
    LIGHTNESS_LINEAR_SET_UNACKNOWLEDGED = 0x8251
    LIGHTNESS_LINEAR_STATUS = 0x8252
    LIGHTNESS_LAST_GET = 0x8253
    LIGHTNESS_LAST_STATUS = 0x8254
    LIGHTNESS_DEFAULT_GET = 0x8255
    LIGHTNESS_DEFAULT_STATUS = 0x8256
    LIGHTNESS_RANGE_GET = 0x8257
    LIGHTNESS_RANGE_STATUS = 0x8258


class LightLightnessSetupOpcode(IntEnum):
    LIGHTNESS_DEFAULT_SET = 0x8259
    LIGHTNESS_DEFAULT_SET_UNACKNOWLEDGED = 0x825A
    LIGHTNESS_RANGE_SET = 0x825B
    LIGHTNESS_RANGE_SET_UNACKNOWLEDGED = 0x825C


LightLightnessGet = Struct()

LightLightnessDefault = Struct(
    "lightness" / Int16ul
)

LightLightnessStatusMinimal = Struct(
    "present_lightness" / Int16ul
)

LightLightnessStatusOptional = Struct(
    Embedded(LightLightnessStatusMinimal),
    "target_lightness" / Int16ul,
    "remaining_time" / TransitionTimeAdapter(TransitionTime, allow_unknown=True)
)

LightLightnessStatus = Select(
    LightLightnessStatusOptional,
    LightLightnessStatusMinimal
)

LightLightnessRange = Struct(
    "range_min" / Int16ul,
    "range_max" / Int16ul,
)

LightLightnessRangeStatus = Struct(
    "status" / StatusCodeAdapter,
    Embedded(LightLightnessRange)
)

LightLightnessSetMinimal = Struct(
    "lightness" / Int16ul,
    "tid" / Int8ul
)

LightLightnessSetOptional = Struct(
    Embedded(LightLightnessSetMinimal),
    Embedded(OptionalSetParameters)
)

LightLightnessSet = Select(
    LightLightnessSetOptional,
    LightLightnessSetMinimal
)


LightLightnessMessage = Struct(
    "opcode" / EnumAdapter(Opcode, LightLightnessOpcode),
    "params" / Switch(
        this.opcode,
        {
            LightLightnessOpcode.LIGHTNESS_GET: LightLightnessGet,
            LightLightnessOpcode.LIGHTNESS_SET: LightLightnessSet,
            LightLightnessOpcode.LIGHTNESS_SET_UNACKNOWLEDGED: LightLightnessSet,
            LightLightnessOpcode.LIGHTNESS_STATUS: LightLightnessStatus,
            LightLightnessOpcode.LIGHTNESS_LINEAR_GET: LightLightnessGet,
            LightLightnessOpcode.LIGHTNESS_LINEAR_SET: LightLightnessSet,
            LightLightnessOpcode.LIGHTNESS_LINEAR_SET_UNACKNOWLEDGED: LightLightnessSet,
            LightLightnessOpcode.LIGHTNESS_LINEAR_STATUS: LightLightnessStatus,
            LightLightnessOpcode.LIGHTNESS_LAST_GET: LightLightnessGet,
            LightLightnessOpcode.LIGHTNESS_LAST_STATUS: LightLightnessDefault,
            LightLightnessOpcode.LIGHTNESS_DEFAULT_GET: LightLightnessGet,
            LightLightnessOpcode.LIGHTNESS_DEFAULT_STATUS: LightLightnessDefault,
            LightLightnessOpcode.LIGHTNESS_RANGE_GET: LightLightnessGet,
            LightLightnessOpcode.LIGHTNESS_RANGE_STATUS: LightLightnessRangeStatus,
        },
    )
)


LightLightnessSetupMessage = Struct(
    "opcode" / EnumAdapter(Opcode, LightLightnessSetupOpcode),
    "params" / Switch(
        this.opcode,
        {
            LightLightnessSetupOpcode.LIGHTNESS_DEFAULT_SET: LightLightnessDefault,
            LightLightnessSetupOpcode.LIGHTNESS_DEFAULT_SET_UNACKNOWLEDGED: LightLightnessDefault,
            LightLightnessSetupOpcode.LIGHTNESS_RANGE_SET: LightLightnessRange,
            LightLightnessSetupOpcode.LIGHTNESS_RANGE_SET_UNACKNOWLEDGED: LightLightnessRange,
        },
    )
)

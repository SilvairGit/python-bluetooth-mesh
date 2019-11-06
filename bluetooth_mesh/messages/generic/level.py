from construct import Int8ul, Int16sl, Int16ul, Int32sl, Int32ul, Select, Struct, Switch, this, Embedded
from enum import IntEnum
from bluetooth_mesh.messages.util import EnumAdapter, Opcode
from bluetooth_mesh.messages.generics import TransitionTimeAdapter, TransitionTime, OptionalSetParameters


class GenericLevelOpcode(IntEnum):
    LEVEL_GET = 0x8205
    LEVEL_SET = 0x8206
    LEVEL_SET_UNACKNOWLEDGED = 0x8207
    LEVEL_STATUS = 0x8208
    DELTA_SET = 0x8209
    DELTA_SET_UNACKNOWLEDGED = 0x820A
    MOVE_SET = 0x820B
    MOVE_SET_UNACKNOWLEDGED = 0x820C


GenericLevelGet = Struct()

GenericLevelSetMinimal = Struct(
    "level" / Int16sl,
    "tid" / Int8ul
)

GenericLevelSetOptional = Struct(
    Embedded(GenericLevelSetMinimal),
    Embedded(OptionalSetParameters)
)

GenericLevelSet = Select(
    GenericLevelSetOptional,
    GenericLevelSetMinimal
)

GenericDeltaSetMinimal = Struct(
    "delta_level" / Int32sl,
    "tid" / Int8ul
)

GenericDeltaSetOptional = Struct(
    Embedded(GenericDeltaSetMinimal),
    Embedded(OptionalSetParameters)
)

GenericDeltaSet = Select(
    GenericDeltaSetOptional,
    GenericDeltaSetMinimal
)

GenericMoveSetMinimal = Struct(
    "delta_level" / Int16sl,
    "tid" / Int8ul
)

GenericMoveSetOptional = Struct(
    Embedded(GenericMoveSetMinimal),
    Embedded(OptionalSetParameters)
)

GenericMoveSet = Select(
    GenericMoveSetOptional,
    GenericMoveSetMinimal
)

GenericLevelStatusMinimal = Struct(
    "present_level" / Int16sl
)

GenericLevelStatusOptional = Struct(
    Embedded(GenericLevelStatusMinimal),
    "target_level" / Int16sl,
    "remaining_time" / TransitionTimeAdapter(TransitionTime, allow_unknown=True)
)

GenericLevelStatus = Select(
    GenericLevelStatusOptional,
    GenericLevelStatusMinimal
)

GenericLevelMessage = Struct(
    "opcode" / EnumAdapter(Opcode, GenericLevelOpcode),
    "params" / Switch(
        this.opcode,
        {
            GenericLevelOpcode.LEVEL_GET: GenericLevelGet,
            GenericLevelOpcode.LEVEL_SET: GenericLevelSet,
            GenericLevelOpcode.LEVEL_SET_UNACKNOWLEDGED: GenericLevelSet,
            GenericLevelOpcode.LEVEL_STATUS: GenericLevelStatus,
            GenericLevelOpcode.DELTA_SET: GenericDeltaSet,
            GenericLevelOpcode.DELTA_SET_UNACKNOWLEDGED: GenericDeltaSet,
            GenericLevelOpcode.MOVE_SET: GenericMoveSet,
            GenericLevelOpcode.MOVE_SET_UNACKNOWLEDGED: GenericMoveSet,
        },
    )
)

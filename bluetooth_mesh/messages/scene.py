from enum import IntEnum
from construct import Struct, Switch, this, Int16ul, Int8ul, Select, Array, Check, ExprValidator, obj_

from bluetooth_mesh.messages.generics import TransitionTimeAdapter, TransitionTime, Delay
from bluetooth_mesh.messages.util import EnumAdapter, Opcode


class SceneMessageOpcode(IntEnum):
    SCENE_GET = 0x8241
    SCENE_RECALL = 0x8242
    SCENE_RECALL_UNACKNOWLEDGED = 0x8243
    SCENE_STATUS = 0x5E
    SCENE_REGISTER_GET = 0x8244
    SCENE_REGISTER_STATUS = 0x8245
    SCENE_STORE = 0x8246
    SCENE_STORE_UNACKNOWLEDGED = 0x8247
    SCENE_DELETE = 0x829E
    SCENE_DELETE_UNACKNOWLEDGED = 0x829F


class SceneStatusCode(IntEnum):
    SUCCESS = 0x00
    SCENE_REGISTER_FULL = 0x01
    SCENE_NOT_FOUND = 0x02


SceneGet = Struct()

SceneRecallMinimal = Struct(
    "scene_number" / ExprValidator(Int16ul, obj_ > 0),
    "tid" / Int8ul,
)

SceneRecallWithTransition = Struct(
    "scene_number" / ExprValidator(Int16ul, obj_ > 0),
    "tid" / Int8ul,
    "transition_time" / TransitionTimeAdapter(TransitionTime, allow_unknown=False),
    "delay" / Delay(Int8ul),
)

SceneRecall = Select(
    SceneRecallWithTransition,
    SceneRecallMinimal
)

SceneStatusMinimal = Struct(
    "status_code" / EnumAdapter(Int8ul, SceneStatusCode),
    "current_scene" / Int16ul
)

SceneStatusWithTargetScene = Struct(
    "status_code" / EnumAdapter(Int8ul, SceneStatusCode),
    "current_scene" / Int16ul,
    "target_scene" / Int16ul,
    "remaining_time" / TransitionTimeAdapter(TransitionTime, allow_unknown=False),
)

SceneStatus = Select(
    SceneStatusWithTargetScene,
    SceneStatusMinimal
)

SceneRegisterGet = Struct()

SceneRegisterStatus = Struct(
    "status_code" / EnumAdapter(Int8ul, SceneStatusCode),
    "current_scene" / Int16ul,
    "scenes" / Array(16, Int16ul)
)

SceneSetupWithValidation = Struct(
    "scene_number" / ExprValidator(Int16ul, obj_ > 0),
)

SceneSetup = Struct(
    "scene_number" / Int16ul
)

SceneMessage = Struct(
    "opcode" / EnumAdapter(Opcode, SceneMessageOpcode),
    "params" / Switch(
        this.opcode,
        {
            SceneMessageOpcode.SCENE_GET: SceneGet,
            SceneMessageOpcode.SCENE_RECALL: SceneRecall,
            SceneMessageOpcode.SCENE_RECALL_UNACKNOWLEDGED: SceneRecall,
            SceneMessageOpcode.SCENE_STATUS: SceneStatus,
            SceneMessageOpcode.SCENE_REGISTER_GET: SceneRegisterGet,
            SceneMessageOpcode.SCENE_REGISTER_STATUS: SceneRegisterStatus,
            SceneMessageOpcode.SCENE_STORE: SceneSetupWithValidation,
            SceneMessageOpcode.SCENE_STORE_UNACKNOWLEDGED: SceneSetupWithValidation,
            SceneMessageOpcode.SCENE_DELETE: SceneSetup,
            SceneMessageOpcode.SCENE_DELETE_UNACKNOWLEDGED: SceneSetup,

        }
    )
)

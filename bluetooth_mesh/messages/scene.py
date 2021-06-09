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
    Array,
    ExprValidator,
    GreedyRange,
    Int8ul,
    Int16ul,
    Struct,
    obj_,
    this,
)

from bluetooth_mesh.messages.generics import (
    Delay,
    TransitionTime,
    TransitionTimeAdapter,
)
from bluetooth_mesh.messages.util import EnumAdapter
from bluetooth_mesh.messages.util import EnumSwitch as Switch
from bluetooth_mesh.messages.util import NamedSelect, Opcode, SwitchStruct


class SceneOpcode(IntEnum):
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


# fmt: off
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

SceneRecall = NamedSelect(
    optional=SceneRecallWithTransition,
    minimal=SceneRecallMinimal
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

SceneStatus = NamedSelect(
    optional=SceneStatusWithTargetScene,
    minimal=SceneStatusMinimal
)

SceneRegisterGet = Struct()

SceneRegisterStatus = Struct(
    "status_code" / EnumAdapter(Int8ul, SceneStatusCode),
    "current_scene" / Int16ul,
    "scenes" / GreedyRange(Int16ul)
)

SceneSetupWithValidation = Struct(
    "scene_number" / ExprValidator(Int16ul, obj_ > 0),
)

SceneSetup = Struct(
    "scene_number" / Int16ul
)

SceneMessage = SwitchStruct(
    "opcode" / Opcode(SceneOpcode),
    "params" / Switch(
        this.opcode,
        {
            SceneOpcode.SCENE_GET: SceneGet,
            SceneOpcode.SCENE_RECALL: SceneRecall,
            SceneOpcode.SCENE_RECALL_UNACKNOWLEDGED: SceneRecall,
            SceneOpcode.SCENE_STATUS: SceneStatus,
            SceneOpcode.SCENE_REGISTER_GET: SceneRegisterGet,
            SceneOpcode.SCENE_REGISTER_STATUS: SceneRegisterStatus,
            SceneOpcode.SCENE_STORE: SceneSetupWithValidation,
            SceneOpcode.SCENE_STORE_UNACKNOWLEDGED: SceneSetupWithValidation,
            SceneOpcode.SCENE_DELETE: SceneSetup,
            SceneOpcode.SCENE_DELETE_UNACKNOWLEDGED: SceneSetup,

        }
    )
)
# fmt: on

from construct import Int8ul, Select, Struct, Switch, this, Probe
from enum import IntEnum
from bluetooth_mesh.messages.util import EnumAdapter, Opcode
from bluetooth_mesh.messages.generics import Delay, TransitionTimeAdapter, TransitionTime


class GenericOnOffOpcode(IntEnum):
    ONOFF_GET = 0x8201
    ONOFF_SET = 0x8202
    ONOFF_SET_UNACKNOWLEDGED = 0x8203
    ONOFF_STATUS = 0x8204


GenericOnOffGet = Struct()

GenericOnOffSetMinimal = Struct(
    "onoff" / Int8ul,
    "tid" / Int8ul
)

GenericOnOffSetOptional = Struct(
    "onoff" / Int8ul,
    "tid" / Int8ul,
    "transition_time" / TransitionTimeAdapter(TransitionTime, allow_unknown=False),
    "delay" / Delay(Int8ul)
)

GenericOnOffSet = Select(
    GenericOnOffSetOptional,
    GenericOnOffSetMinimal
)

GenericOnOffStatusMinimal = Struct(
    "present_onoff" / Int8ul
)

GenericOnOffStatusOptional = Struct(
    "present_onoff" / Int8ul,
    "target_onoff" / Int8ul,
    "remaining_time" / TransitionTimeAdapter(TransitionTime, allow_unknown=True)
)

GenericOnOffStatus = Select(
    GenericOnOffStatusOptional,
    GenericOnOffStatusMinimal
)


GenericOnOffMessage = Struct(
    "opcode" / EnumAdapter(Opcode, GenericOnOffOpcode),
    "params" / Switch(
        this.opcode,
        {
            GenericOnOffOpcode.ONOFF_GET: GenericOnOffGet,
            GenericOnOffOpcode.ONOFF_SET: GenericOnOffSet,
            GenericOnOffOpcode.ONOFF_SET_UNACKNOWLEDGED: GenericOnOffSet,
            GenericOnOffOpcode.ONOFF_STATUS: GenericOnOffStatus,
        },
    )
)

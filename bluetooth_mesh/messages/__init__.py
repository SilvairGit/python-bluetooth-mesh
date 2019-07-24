from construct import (
    Select, Struct,
    GreedyBytes,
)

from .util import Opcode
from .health import HealthMessage
from .config import ConfigMessage
from .generics import GenericOnOff

AccessMessage = Select(
    HealthMessage,
    ConfigMessage,
    GenericOnOff,
    Struct(
        "opcode" / Opcode,
        "params" / GreedyBytes,
    )
)

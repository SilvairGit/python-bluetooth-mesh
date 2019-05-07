from construct import (
    Select, Struct,
    GreedyBytes,
)

from .util import Opcode
from .health import HealthMessage
from .config import ConfigMessage

AccessMessage = Select(
    HealthMessage,
    ConfigMessage,
    Struct(
        "opcode" / Opcode,
        "params" / GreedyBytes,
    )
)

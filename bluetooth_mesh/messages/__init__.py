from construct import (
    Select, Struct,
    GreedyBytes,
)

from .util import Opcode
from .health import HealthMessage
from .config import ConfigMessage
from .generic import GenericMessage

AccessMessage = Select(
    HealthMessage,
    ConfigMessage,
    GenericMessage,
    Struct(
        "opcode" / Opcode,
        "params" / GreedyBytes,
    )
)

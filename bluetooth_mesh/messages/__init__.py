from construct import (
    Select, Struct,
    GreedyBytes,
)

from .util import Opcode
from .health import HealthMessage
from .config import ConfigMessage
from .generic import GenericMessage
from .scene import SceneMessage
from .sensor import SensorMessage, SensorSetupMessage

Message = Struct(
    "opcode" / Opcode,
    "params" / GreedyBytes,
)

AccessMessage = Select(
    "HealthMessage" / HealthMessage,
    "ConfigMessage" / ConfigMessage,
    "GenericMessage" / GenericMessage,
    "SceneMessage" / SceneMessage,
    "SensorMessage" / SensorMessage,
    "SensorSetupMessage" / SensorSetupMessage,
    "Message" / Message,
)

from construct import GreedyBytes, Select, Struct

from .config import ConfigMessage
from .generic import GenericMessage
from .health import HealthMessage
from .scene import SceneMessage
from .sensor import SensorMessage, SensorSetupMessage
from .util import Opcode

# fmt: off
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
# fmt: on

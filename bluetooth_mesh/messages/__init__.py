from construct import GreedyBytes, Select, Struct

from .config import ConfigMessage
from .generic import GenericMessage
from .health import HealthMessage
from .scene import SceneMessage
from .sensor import SensorMessage, SensorSetupMessage
from .silvair import (
    DebugMessage,
    GatewayConfigMessage,
    NetworkDiagnosticServerMessage,
    NetworkDiagnosticSetupServerMessage,
)
from .util import Opcode

# fmt: off
Message = Struct(
    "opcode" / Opcode,
    "params" / GreedyBytes,
)

AccessMessage = Select(
    "ConfigMessage" / ConfigMessage,
    "DebugMessage"/ DebugMessage,
    "GatewayConfigMessage" / GatewayConfigMessage,
    "GenericMessage" / GenericMessage,
    "HealthMessage" / HealthMessage,
    "NetworkDiagnosticServerMessage" / NetworkDiagnosticServerMessage,
    "NetworkDiagnosticSetupServerMessage" / NetworkDiagnosticSetupServerMessage,
    "SceneMessage" / SceneMessage,
    "SensorMessage" / SensorMessage,
    "SensorSetupMessage" / SensorSetupMessage,

    # this needs to be last
    "Message" / Message,
).compile()
# fmt: on

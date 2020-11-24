import json
from enum import Enum

from construct import (
    Construct,
    Container,
    GreedyBytes,
    ListContainer,
    Select,
    SizeofError,
    Struct,
    stream_read_entire,
    stream_write,
)

from .config import ConfigMessage, ConfigOpcode
from .generic.battery import GenericBatteryMessage, GenericBatteryOpcode
from .generic.level import GenericLevelMessage, GenericLevelOpcode
from .generic.light.ctl import (
    LightCTLMessage,
    LightCTLOpcode,
    LightCTLSetupMessage,
    LightCTLSetupOpcode,
)
from .generic.light.lightness import (
    LightLightnessMessage,
    LightLightnessOpcode,
    LightLightnessSetupMessage,
    LightLightnessSetupOpcode,
)
from .generic.onoff import GenericOnOffMessage, GenericOnOffOpcode
from .health import HealthMessage, HealthOpcode
from .scene import SceneMessage, SceneOpcode
from .sensor import SensorMessage, SensorOpcode, SensorSetupMessage, SensorSetupOpcode
from .silvair.debug import DebugMessage, DebugOpcode
from .silvair.gateway_config_server import (
    GatewayConfigMessage,
    GatewayConfigServerOpcode,
)
from .silvair.light_extended_controller import (
    LightExtendedControllerMessage,
    LightExtendedControllerOpcode,
)
from .silvair.network_diagnostic_server import (
    NetworkDiagnosticServerMessage,
    NetworkDiagnosticServerOpcode,
    NetworkDiagnosticSetupServerMessage,
    NetworkDiagnosticSetupServerOpcode,
)
from .util import Opcode


class _AccessMessage(Construct):
    OPCODES = {
        ConfigOpcode: ConfigMessage,
        DebugOpcode: DebugMessage,
        GatewayConfigServerOpcode: GatewayConfigMessage,
        GenericOnOffOpcode: GenericOnOffMessage,
        GenericBatteryOpcode: GenericBatteryMessage,
        GenericLevelOpcode: GenericLevelMessage,
        LightLightnessOpcode: LightLightnessMessage,
        LightLightnessSetupOpcode: LightLightnessSetupMessage,
        LightCTLOpcode: LightCTLMessage,
        LightCTLSetupOpcode: LightCTLSetupMessage,
        HealthOpcode: HealthMessage,
        NetworkDiagnosticServerOpcode: NetworkDiagnosticServerMessage,
        NetworkDiagnosticSetupServerOpcode: NetworkDiagnosticSetupServerMessage,
        SceneOpcode: SceneMessage,
        SensorOpcode: SensorMessage,
        SensorSetupOpcode: SensorSetupMessage,
        LightExtendedControllerOpcode: LightExtendedControllerMessage,
    }

    def __init__(self):
        super().__init__()
        self._opcodes = {}
        for opcode_class, message in self.OPCODES.items():
            for opcode in opcode_class._value2member_map_.keys():
                self._opcodes[opcode] = opcode_class(opcode), message

    def _parse(self, stream, context, path):
        opcode = Opcode()._parse(stream, context, path)

        try:
            opcode, message = self._opcodes[opcode]
        except KeyError:
            return Container(opcode=opcode, params=stream_read_entire(stream))

        stream.seek(0)
        parsed = message._parse(stream, context, path)
        parsed.opcode = opcode
        return parsed

    def _build(self, obj, stream, context, path):
        opcode = obj["opcode"]

        try:
            opcode, message = self._opcodes[opcode]
        except KeyError:
            Opcode()._build(opcode, stream, context, path)
            stream_write(stream, obj["params"])
            return obj

        return message._build(obj, stream, context, path)

    def _sizeof(self, context, path):
        raise SizeofError

    @classmethod
    def to_json(cls, value):
        if isinstance(value, Container):
            return {
                k: cls.to_json(v) for k, v in value.items() if not k.startswith("_")
            }

        if isinstance(value, ListContainer):
            return [cls.to_json(i) for i in value]

        if isinstance(value, Enum):
            return value.name

        return value


AccessMessage = _AccessMessage()

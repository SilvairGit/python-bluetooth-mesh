from construct import (
    Construct,
    Container,
    GreedyBytes,
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
from .time import TimeMessage, TimeOpcode
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
        TimeOpcode: TimeMessage,
    }

    OPCODE = Opcode()

    def __init__(self):
        super().__init__()
        self._opcodes = {}
        for opcode_class, message in self.OPCODES.items():
            for opcode in opcode_class._value2member_map_.keys():
                self._opcodes[opcode] = opcode_class(opcode), message.compile()

    def _parse(self, stream, context, path):
        opcode = self.OPCODE._parse(stream, context, path)

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
            if isinstance(opcode, str):
                opcode, message = next(
                    v for k, v in self._opcodes.items() if v[0].name == opcode
                )
                obj["opcode"] = opcode
            else:
                opcode, message = self._opcodes[opcode]
        except KeyError:
            Opcode()._build(opcode, stream, context, path)
            stream_write(stream, obj["params"])
            return obj

        return message._build(obj, stream, context, path)

    def _sizeof(self, context, path):
        raise SizeofError


AccessMessage = _AccessMessage()

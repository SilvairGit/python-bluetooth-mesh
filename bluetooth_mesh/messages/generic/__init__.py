from construct import Select

from .onoff import GenericOnOffMessage
from .level import GenericLevelMessage
from .light.ctl import LightCTLMessage, LightCTLSetupMessage
from .light.lightness import LightLightnessMessage, LightLightnessSetupMessage

GenericMessage = Select(
    GenericOnOffMessage,
    GenericLevelMessage,
    LightCTLMessage,
    LightCTLSetupMessage,
    LightLightnessMessage,
    LightLightnessSetupMessage
)

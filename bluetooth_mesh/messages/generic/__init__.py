from construct import Select

from .level import GenericLevelMessage
from .light.ctl import LightCTLMessage, LightCTLSetupMessage
from .light.lightness import LightLightnessMessage, LightLightnessSetupMessage
from .onoff import GenericOnOffMessage
from .dtt import GenericDTTMessage

GenericMessage = Select(
    GenericOnOffMessage,
    GenericLevelMessage,
    GenericDTTMessage,
    LightCTLMessage,
    LightCTLSetupMessage,
    LightLightnessMessage,
    LightLightnessSetupMessage,
)

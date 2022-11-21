from construct import Select

from .level import GenericLevelMessage
from .light.ctl import LightCTLMessage, LightCTLSetupMessage
from .light.lightness import LightLightnessMessage, LightLightnessSetupMessage
from .onoff import GenericOnOffMessage
from .dtt import GenericDTTMessage
from .ponoff import  GenericPowerOnOffMessage, GenericPowerOnOffSetupMessage

GenericMessage = Select(
    GenericOnOffMessage,
    GenericLevelMessage,
    GenericDTTMessage,
    GenericPowerOnOffMessage,
    GenericPowerOnOffSetupMessage,
    LightCTLMessage,
    LightCTLSetupMessage,
    LightLightnessMessage,
    LightLightnessSetupMessage,
)

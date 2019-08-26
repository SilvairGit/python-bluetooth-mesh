from construct import Select

from .onoff import GenericOnOffMessage
from .level import GenericLevelMessage
from .light.ctl import LightCTLMessage
from .light.lightness import LightLightnessMessage

GenericMessage = Select(
    GenericOnOffMessage,
    GenericLevelMessage,
    LightCTLMessage,
    LightLightnessMessage
)

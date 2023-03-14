from construct import Select

from .ctl import LightCTLMessage, LightCTLSetupMessage
from .lightness import LightLightnessMessage,LightLightnessSetupMessage
from .hsl import LightHSLMessage, LightHSLSetupMessage

LightMessage = Select(
    LightCTLMessage,
    LightCTLSetupMessage,
    LightLightnessMessage,
    LightLightnessSetupMessage,
    LightHSLMessage,
    LightHSLSetupMessage,
)

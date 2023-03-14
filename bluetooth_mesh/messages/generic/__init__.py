from construct import Select

from .level import GenericLevelMessage
from .onoff import GenericOnOffMessage
from .dtt import GenericDTTMessage
from .ponoff import  GenericPowerOnOffMessage, GenericPowerOnOffSetupMessage

GenericMessage = Select(
    GenericOnOffMessage,
    GenericLevelMessage,
    GenericDTTMessage,
    GenericPowerOnOffMessage,
    GenericPowerOnOffSetupMessage,
)

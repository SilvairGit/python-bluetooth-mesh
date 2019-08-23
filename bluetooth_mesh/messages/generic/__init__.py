from construct import Select

from .onoff import GenericOnOffMessage
from .level import GenericLevelMessage

GenericMessage = Select(
    GenericOnOffMessage,
    GenericLevelMessage
)

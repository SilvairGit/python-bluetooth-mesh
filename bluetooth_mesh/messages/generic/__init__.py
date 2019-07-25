from construct import Select

from .onoff import GenericOnOffMessage

GenericMessage = Select(
    GenericOnOffMessage
)

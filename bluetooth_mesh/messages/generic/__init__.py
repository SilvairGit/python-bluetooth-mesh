from construct import Select

from .generic_onoff_message import GenericOnOffMessage

GenericMessage = Select(
    GenericOnOffMessage
)

from typing import Any, Mapping, Union
from uuid import UUID

from bluetooth_mesh.application import Element
from bluetooth_mesh.messages.generic.onoff import GenericOnOffOpcode
from bluetooth_mesh.models import Model


class MyModel(Model):
    MODEL_ID = (None, 0x1002)
    OPCODES = [
        GenericOnOffOpcode.ONOFF_SET,
    ]

    def _app_onoff_set(source: int,
                       app_index: int,
                       destination: Union[int, UUID],
                       message: Mapping[str, Any]):
        pass

    def _dev_onoff_set(source: int,
                       net_index: int,
                       message: Mapping[str, Any]):
        pass

    def __init__(self, element: Element):
        super().__init__(element)

        self.app_message_callbacks[GenericOnOffOpcode.ONOFF_SET] \
            .add(self._app_onoff_set)

        self.dev_message_callbacks[GenericOnOffOpcode.ONOFF_SET] \
            .add(self._dev_onoff_set)

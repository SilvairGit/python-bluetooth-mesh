from enum import IntEnum

from bluetooth_mesh.messages.generic.onoff import GenericOnOffOpcode
from bluetooth_mesh.models import Model


class GenericOnOffServer(Model):
    MODEL_ID = (None, 0x1002)
    OPCODES = [
        GenericOnOffOpcode.ONOFF_SET,
        GenericOnOffOpcode.ONOFF_SET_UNACKNOWLEDGED,
        GenericOnOffOpcode.ONOFF_GET,
    ]


MY_VENDOR_ID = 0x0136


class MyVendorModelOpcode(IntEnum):
    FROBNICATOR_GET = 0x0001


class MyVendorModel(Model):
    MODEL_ID = (MY_VENDOR_ID, 0x0001)
    OPCODES = [
        MyVendorModelOpcode.FROBNICATOR_GET,
    ]

#!/usr/bin/python3

import logging
import asyncio
import secrets
from contextlib import suppress
from uuid import UUID
from typing import (Union)

from docopt import docopt

from bluetooth_mesh.utils import ParsedMeshMessage
from bluetooth_mesh.application import Application, Element, Capabilities
from bluetooth_mesh.crypto import ApplicationKey, DeviceKey, NetworkKey
from bluetooth_mesh.messages.properties import PropertyID
from bluetooth_mesh.messages.config import GATTNamespaceDescriptor, StatusCode
from bluetooth_mesh.messages.sensor import SensorOpcode, SensorSetupOpcode
from bluetooth_mesh.models import (
    ConfigClient,
    HealthClient,
)


from bluetooth_mesh.models.generic.onoff import GenericOnOffClient
from bluetooth_mesh.models.generic.level import GenericLevelClient
from bluetooth_mesh.models.generic.dtt import GenericDTTClient
from bluetooth_mesh.models.generic.ponoff import GenericPowerOnOffClient
from bluetooth_mesh.models.sensor import SensorClient
from bluetooth_mesh.models.scene import SceneClient
from bluetooth_mesh.models.light.lightness import LightLightnessClient
from bluetooth_mesh.models.light.ctl import LightCTLClient
from bluetooth_mesh.models.light.hsl import LightHSLClient



G_TIMEOUT = 5

log = logging.getLogger()


class MainElement(Element):
    LOCATION = GATTNamespaceDescriptor.MAIN
    MODELS = [
        ConfigClient,
        HealthClient,
        GenericOnOffClient,
        GenericDTTClient,
        GenericPowerOnOffClient,
        SceneClient,
        GenericLevelClient,
        SensorClient,
        LightLightnessClient,
        LightCTLClient,
        LightHSLClient,
    ]


class SampleApplication(Application):
    COMPANY_ID = 0x0136  # Silvair
    PRODUCT_ID = 0x0001
    VERSION_ID = 1
    ELEMENTS = {
        0: MainElement,
    }
    CAPABILITIES = [Capabilities.OUT_NUMERIC]

    CRPL = 32768
    PATH = "/com/silvair/sample"

    @property
    def iv_index(self):
        return 0


    async def descriptor_get(self, addr, app_index, arguments):
        client = self.elements[0][SensorClient]
        result = await client.descriptor_get([addr], app_index=app_index,
                                                     timeout=G_TIMEOUT)
        print(result[addr])

    async def get(self, addr, app_index, arguments):
        client = self.elements[0][SensorClient]

        addr = int(arguments['-a'], 16)
        property_id = int(arguments['-p'], 16) if arguments['-p'] else None

        result = await client.get([addr], app_index=app_index,
                                  property_id=property_id,
                                  timeout=G_TIMEOUT)
        print(result[addr])

    async def cadence_get(self, addr, app_index, arguments):
        client = self.elements[0][SensorClient]

        addr = int(arguments['-a'], 16)
        property_id = int(arguments['-p'], 16)

        result = await client.cadence_get([addr], app_index=app_index,
                                          property_id=property_id,
                                          timeout=G_TIMEOUT)
        print(result[addr])

    async def cadence_set(self, addr, app_index, arguments):
        client = self.elements[0][SensorClient]

        addr = int(arguments['-a'], 16)
        property_id = int(arguments['-p'], 16)
        fast_cadence_period_divisor = int(arguments['<fast_divisor>'])

        if property_id == PropertyID.PRECISE_TOTAL_DEVICE_ENERGY_USE:
            request = dict(
                sensor_setting_property_id=property_id,
                fast_cadence_period_divisor=fast_cadence_period_divisor,
                status_trigger_type=0,
                status_trigger_delta_down=dict(energy=20.0),
                status_trigger_delta_up=dict(energy=100.5),
                status_min_interval=1024,
                fast_cadence_low=dict(energy=1.6),
                fast_cadence_high=dict(energy=2.0),
            )
        else:
            print("Unsipported PropertyID")
            return

        result = await client.cadence_set([addr], app_index=app_index,
                                         **request,
                                         timeout=G_TIMEOUT)
        print(result)

    async def listen(self, addr, app_index, arguments):
        def receive_status(
            _source: int,
            _app_index: int,
            _destination: Union[int, UUID],
            message: ParsedMeshMessage,
        ):
            print("receive %04x->%04x" % (_source, _destination))
            print(message)

        client = self.elements[0][SensorClient]
        client.app_message_callbacks[SensorOpcode.SENSOR_STATUS].add(receive_status)

        while True:
            await asyncio.sleep(10)


    async def run(self, token, addr, app_index, cmd, arguments):
        async with self:
            self.token_ring.token = token

            await self.connect()

            if cmd == "descriptor_get":
                await self.descriptor_get(addr, app_index, arguments)
            elif cmd == "cadence_get":
                await self.cadence_get(addr, app_index, arguments)
            elif cmd == "cadence_set":
                await self.cadence_set(addr, app_index, arguments)
            elif cmd == "get":
                await self.get(addr, app_index, arguments)
            elif cmd == "listen":
                await self.listen(addr, app_index, arguments)


def main():
    doc = """
    Sensor Client Sample Application

    Usage:
        sensor_client.py [-V] -t <token> -a <address> descriptor_get
        sensor_client.py [-V] -t <token> -a <address> -p <property_id> cadence_get
        sensor_client.py [-V] -t <token> -a <address> -p <property_id> cadence_set <fast_divisor>
        sensor_client.py [-V] -t <token> -a <address> [-p <property_id>] get
        sensor_client.py [-V] -t <token> -a <address> listen
        sensor_client.py [-h | --help]
        sensor_client.py --version

    Options:
        -t <token>              bluetooth-meshd node token
        -a <address>            Local node unicast address
        -p <property_id>        Sensor property id in hex
        -V                      Show verbose messages
        -h --help               Show this screen
        --version               Show version
    """

    arguments = docopt(doc, version='1.0')

    if arguments['-V']:
        logging.basicConfig(level=logging.DEBUG)

    token = int(arguments['-t'], 16)
    addr = int(arguments['-a'], 16)
    app_index = 0
    cmd = None

    if arguments['descriptor_get']:
        cmd = 'descriptor_get'
    elif arguments['cadence_get']:
        cmd = 'cadence_get'
    elif arguments['cadence_set']:
        cmd = 'cadence_set'
    elif arguments['get']:
        cmd = 'get'
    elif arguments['listen']:
        cmd = 'listen'
    else:
        print(doc)
        exit(-1)

    loop = asyncio.get_event_loop()
    app = SampleApplication(loop)

    with suppress(KeyboardInterrupt):
        loop.run_until_complete(app.run(token, addr, app_index, cmd, arguments))


if __name__ == '__main__':
    main()

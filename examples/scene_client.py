#!/usr/bin/python3

import logging
import asyncio
import secrets
from contextlib import suppress
from uuid import UUID

from docopt import docopt

from bluetooth_mesh.application import Application, Element, Capabilities
from bluetooth_mesh.crypto import ApplicationKey, DeviceKey, NetworkKey
from bluetooth_mesh.messages.config import GATTNamespaceDescriptor, StatusCode
from bluetooth_mesh.models import (
    ConfigClient,
    HealthClient,
    SensorClient,
)

from bluetooth_mesh.models.generic.onoff import GenericOnOffClient
from bluetooth_mesh.models.generic.level import GenericLevelClient
from bluetooth_mesh.models.generic.dtt import GenericDTTClient
from bluetooth_mesh.models.generic.ponoff import GenericPowerOnOffClient
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

    async def get(self, addr, app_index, arguments):
        client = self.elements[0][SceneClient]
        result = await client.get([addr], app_index=app_index,
                                  timeout=G_TIMEOUT)
        print(result[addr])

    async def recall(self, addr, app_index, arguments):
        client = self.elements[0][SceneClient]
        scene_number = int(arguments['<number>'])
        transition_time = float(arguments['--transition']) if arguments['--transition'] else 0.0
        result = await client.recall([addr], app_index=app_index,
                                     scene_number=scene_number,
                                     transition_time=transition_time,
                                     timeout=G_TIMEOUT)
        print(result[addr])

    async def recall_unack(self, addr, app_index, arguments):
        client = self.elements[0][SceneClient]
        scene_number = int(arguments['<number>'])
        transition_time = float(arguments['--transition']) if arguments['--transition'] else 0.0
        await client.recall_unack(addr, app_index=app_index,
                                  scene_number=scene_number,
                                  transition_time=transition_time)

    async def register_get(self, addr, app_index, arguments):
        client = self.elements[0][SceneClient]
        result = await client.register_get([addr], app_index=app_index,
                                           timeout=G_TIMEOUT)
        print(result[addr])

    async def store(self, addr, app_index, arguments):
        client = self.elements[0][SceneClient]
        scene_number = int(arguments['<number>'])
        result = await client.store([addr], app_index=app_index,
                                     scene_number=scene_number,
                                     timeout=G_TIMEOUT)
        print(result[addr])

    async def store_unack(self, addr, app_index, arguments):
        client = self.elements[0][SceneClient]
        scene_number = int(arguments['<number>'])
        await client.store_unack(addr, app_index=app_index,
                                 scene_number=scene_number)

    async def delete(self, addr, app_index, arguments):
        client = self.elements[0][SceneClient]
        scene_number = int(arguments['<number>'])
        result = await client.delete([addr], app_index=app_index,
                                     scene_number=scene_number,
                                     timeout=G_TIMEOUT)
        print(result[addr])

    async def delete_unack(self, addr, app_index, arguments):
        client = self.elements[0][SceneClient]
        scene_number = int(arguments['<number>'])
        await client.delete_unack(addr, app_index=app_index,
                                  scene_number=scene_number)


    async def run(self, token, addr, app_index, cmd, arguments):
        async with self:
            self.token_ring.token = token

            await self.connect()

            if cmd == "get":
                await self.get(addr, app_index, arguments)
            elif cmd == "recall":
                await self.recall(addr, app_index, arguments)
            elif cmd == "recall_unack":
                await self.recall_unack(addr, app_index, arguments)
            elif cmd == "register_get":
                await self.register_get(addr, app_index, arguments)
            elif cmd == "store":
                await self.store(addr, app_index, arguments)
            elif cmd == "store_unack":
                await self.store_unack(addr, app_index, arguments)
            elif cmd == "delete":
                await self.delete(addr, app_index, arguments)
            elif cmd == "delete_unack":
                await self.delete_unack(addr, app_index, arguments)


def main():
    doc = """
    Generic On/Off Client Sample Application

    Usage:
        scene_client.py [-V] -t <token> -a <address> get
        scene_client.py [-V] -t <token> -a <address> [--transition=<time>] recall <number>
        scene_client.py [-V] -t <token> -a <address> [--transition=<time>] recall_unack <number>
        scene_client.py [-V] -t <token> -a <address> register_get
        scene_client.py [-V] -t <token> -a <address> store <number>
        scene_client.py [-V] -t <token> -a <address> store_unack <number>
        scene_client.py [-V] -t <token> -a <address> delete <number>
        scene_client.py [-V] -t <token> -a <address> delete_unack <number>
        scene_client.py [-h | --help]
        scene_client.py --version

    Options:
        -t <token>              bluetooth-meshd node token
        -a <address>            Local node unicast address
        <number>                Scene number
        --transition=<time>     Transition time
        -V                      Show verbose messages
        -h --help               Show this screen
        --version               Show version
    """

    arguments = docopt(doc, version='1.0')

    if arguments['-V']:
        logging.basicConfig(level=logging.DEBUG)

    app_index = 0
    cmd = None

    if arguments['get']:
        cmd = 'get'
    elif arguments['recall']:
        cmd = 'recall'
    elif arguments['recall_unack']:
        cmd = 'recall_unack'
    elif arguments['register_get']:
        cmd = 'register_get'
    elif arguments['store']:
        cmd = 'store'
    elif arguments['store_unack']:
        cmd = 'store_unack'
    elif arguments['delete']:
        cmd = 'delete'
    elif arguments['delete_unack']:
        cmd = 'delete_unack'
    else:
        print(doc)
        exit(-1)

    token = int(arguments['-t'], 16)
    addr = int(arguments['-a'], 16)

    loop = asyncio.get_event_loop()
    app = SampleApplication(loop)

    with suppress(KeyboardInterrupt):
        loop.run_until_complete(app.run(token, addr, app_index, cmd, arguments))


if __name__ == '__main__':
    main()

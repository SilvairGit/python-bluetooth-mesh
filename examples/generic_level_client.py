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
        client = self.elements[0][GenericLevelClient]
        result = await client.get([addr], app_index=app_index, timeout=G_TIMEOUT)
        print(result[addr])


    async def set(self, addr, app_index, arguments):
        client = self.elements[0][GenericLevelClient]
        level = -int(arguments['<level>'][2:]) if arguments['<level>'][0:2] == '0-' else int(arguments['<level>'])
        transition_time = float(arguments['--transition']) if arguments['--transition'] else 0.0
        result = await client.set([addr], app_index=app_index,
                                  level=level,
                                  transition_time=transition_time,
                                  timeout=G_TIMEOUT)
        print(result[addr])

    async def set_unack(self, addr, app_index, arguments):
        client = self.elements[0][GenericLevelClient]
        level = -int(arguments['<level>'][2:]) if arguments['<level>'][0:2] == '0-' else int(arguments['<level>'])
        transition_time = float(arguments['--transition']) if arguments['--transition'] else 0.0
        await client.set_unack(addr, app_index=app_index,
                               level=level,
                               transition_time=transition_time)

    async def delta_set(self, addr, app_index, arguments):
        client = self.elements[0][GenericLevelClient]
        level = -int(arguments['<level>'][2:]) if arguments['<level>'][0:2] == '0-' else int(arguments['<level>'])
        transition_time = float(arguments['--transition']) if arguments['--transition'] else 0.0
        result = await client.delta_set([addr], app_index=app_index,
                                        delta_level=level,
                                        transition_time=transition_time,
                                        timeout=G_TIMEOUT)
        print(result[addr])

    async def delta_set_unack(self, addr, app_index, arguments):
        client = self.elements[0][GenericLevelClient]
        level = -int(arguments['<level>'][2:]) if arguments['<level>'][0:2] == '0-' else int(arguments['<level>'])
        transition_time = float(arguments['--transition']) if arguments['--transition'] else 0.0
        await client.delta_set_unack(addr, app_index=app_index,
                                     delta_level=level,
                                     transition_time=transition_time)

    async def move_set(self, addr, app_index, arguments):
        client = self.elements[0][GenericLevelClient]
        level = -int(arguments['<level>'][2:]) if arguments['<level>'][0:2] == '0-' else int(arguments['<level>'])
        transition_time = float(arguments['--transition']) if arguments['--transition'] else 0.0
        result = await client.move_set([addr], app_index=app_index,
                                       delta_level=level,
                                       transition_time=transition_time,
                                       timeout=G_TIMEOUT)
        print(result[addr])

    async def move_set_unack(self, addr, app_index, arguments):
        client = self.elements[0][GenericLevelClient]
        level = -int(arguments['<level>'][2:]) if arguments['<level>'][0:2] == '0-' else int(arguments['<level>'])
        transition_time = float(arguments['--transition']) if arguments['--transition'] else 0.0
        await client.move_set_unack(addr, app_index=app_index,
                                    delta_level=level,
                                    transition_time=transition_time)


    async def run(self, token, addr, app_index, cmd, arguments):
        async with self:
            self.token_ring.token = token

            await self.connect()

            if cmd == "get":
                await self.get(addr, app_index, arguments)
            elif cmd == "set":
                await self.set(addr, app_index, arguments)
            elif cmd == "set_unack":
                await self.set_unack(addr, app_index, arguments)
            elif cmd == "delta_set":
                await self.delta_set(addr, app_index, arguments)
            elif cmd == "delta_set_unack":
                await self.delta_set_unack(addr, app_index, arguments)
            elif cmd == "move_set":
                await self.move_set(addr, app_index, arguments)
            elif cmd == "move_set_unack":
                await self.move_set_unack(addr, app_index, arguments)


def main():
    doc = """
    Generic Level Client Sample Application

    Usage:
        generic_level_client.py [-V] -t <token> -a <address> get
        generic_level_client.py [-V] -t <token> -a <address> [--transition=<time>] set <level>
        generic_level_client.py [-V] -t <token> -a <address> [--transition=<time>] set_unack <level>
        generic_level_client.py [-V] -t <token> -a <address> [--transition=<time>] delta_set <level>
        generic_level_client.py [-V] -t <token> -a <address> [--transition=<time>] delta_set_unack <level>
        generic_level_client.py [-V] -t <token> -a <address> [--transition=<time>] move_set <level>
        generic_level_client.py [-V] -t <token> -a <address> [--transition=<time>] move_set_unack <level>
        generic_level_client.py [-h | --help]
        generic_level_client.py --version

    Options:
        -t <token>              bluetooth-meshd node token
        -a <address>            Local node unicast address
        <level>                 Level value: 0-32768 to 32767
        --transition=<time>     Transition time
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

    if arguments['get']:
        cmd = 'get'
    elif arguments['set']:
        cmd = 'set'
    elif arguments['set_unack']:
        cmd = 'set_unack'
    elif arguments['delta_set']:
        cmd = 'delta_set'
    elif arguments['delta_set_unack']:
        cmd = 'delta_set_unack'
    elif arguments['move_set']:
        cmd = 'move_set'
    elif arguments['move_set_unack']:
        cmd = 'move_set_unack'

    loop = asyncio.get_event_loop()
    app = SampleApplication(loop)

    with suppress(KeyboardInterrupt):
        loop.run_until_complete(app.run(token, addr, app_index, cmd, arguments))


if __name__ == '__main__':
    main()

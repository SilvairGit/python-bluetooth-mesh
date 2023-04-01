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



# Global variables
G_TIMEOUT = 5

log = logging.getLogger()


# Mesh node capabilities declaration
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


# Mesh node application
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
        client = self.elements[0][LightLightnessClient]
        result = await client.get([addr], app_index=app_index, timeout=G_TIMEOUT)
        print(result[addr])

    async def set(self, addr, app_index, arguments):
        client = self.elements[0][LightLightnessClient]
        lightness = int(arguments['<lightness>'])
        transition_time = float(arguments['--transition']) if arguments['--transition'] else 0.0
        result = await client.set([addr],
                                  app_index=app_index,
                                  lightness=lightness,
                                  transition_time=transition_time,
                                  timeout=G_TIMEOUT)
        print(result)

    async def set_unack(self, addr, app_index, arguments):
        client = self.elements[0][LightLightnessClient]
        lightness = int(arguments['<lightness>'])
        transition_time = float(arguments['--transition']) if arguments['--transition'] else 0.0
        await client.set_unack(addr,
                               app_index=app_index,
                               lightness=lightness,
                               transition_time=transition_time)

    async def linear_get(self, addr, app_index, arguments):
        client = self.elements[0][LightLightnessClient]
        result = await client.linear_get([addr], app_index=app_index, timeout=G_TIMEOUT)
        print(result[addr])

    async def linear_set(self, addr, app_index, arguments):
        client = self.elements[0][LightLightnessClient]
        lightness = int(arguments['<lightness>'])
        transition_time = float(arguments['--transition']) if arguments['--transition'] else 0.0
        result = await client.linear_set([addr],
                                         app_index=app_index,
                                         lightness=lightness,
                                         transition_time=transition_time,
                                         timeout=G_TIMEOUT)
        print(result)

    async def linear_set_unack(self, addr, app_index, arguments):
        client = self.elements[0][LightLightnessClient]
        lightness = int(arguments['<lightness>'])
        transition_time = float(arguments['--transition']) if arguments['--transition'] else 0.0
        await client.linear_set_unack(addr,
                                      app_index=app_index,
                                      lightness=lightness,
                                      transition_time=transition_time)

    async def last_get(self, addr, app_index, arguments):
        client = self.elements[0][LightLightnessClient]
        result = await client.last_get([addr], app_index=app_index, timeout=G_TIMEOUT)
        print(result[addr])

    async def default_get(self, addr, app_index, arguments):
        client = self.elements[0][LightLightnessClient]
        result = await client.default_get([addr], app_index=app_index, timeout=G_TIMEOUT)
        print(result[addr])

    async def default_set(self, addr, app_index, arguments):
        client = self.elements[0][LightLightnessClient]
        lightness = int(arguments['<lightness>'])
        result = await client.default_set([addr],
                                          app_index=app_index,
                                          lightness=lightness,
                                          timeout=G_TIMEOUT)
        print(result)

    async def default_set_unack(self, addr, app_index, arguments):
        client = self.elements[0][LightLightnessClient]
        lightness = int(arguments['<lightness>'])
        await client.default_set_unack(addr,
                                       app_index=app_index,
                                       lightness=lightness)

    async def range_get(self, addr, app_index, arguments):
        client = self.elements[0][LightLightnessClient]
        result = await client.range_get([addr], app_index=app_index, timeout=G_TIMEOUT)
        print(result[addr])

    async def range_set(self, addr, app_index, arguments):
        client = self.elements[0][LightLightnessClient]
        lightness_min = int(arguments['<min>'])
        lightness_max = int(arguments['<max>'])
        result = await client.range_set([addr], app_index=app_index,
                                        min_lightness=lightness_min,
                                        max_lightness=lightness_max,
                                        timeout=G_TIMEOUT)
        print(result)

    async def range_set_unack(self, addr, app_index, arguments):
        client = self.elements[0][LightLightnessClient]
        lightness_min = int(arguments['<min>'])
        lightness_max = int(arguments['<max>'])
        await client.range_set_unack(addr, app_index=app_index,
                                     min_lightness=lightness_min,
                                     max_lightness=lightness_max)


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
            elif cmd == "linear_get":
                await self.linear_get(addr, app_index, arguments)
            elif cmd == "linear_set":
                await self.linear_set(addr, app_index, arguments)
            elif cmd == "linear_set_unack":
                await self.linear_set_unack(addr, app_index, arguments)
            elif cmd == "last_get":
                await self.last_get(addr, app_index, arguments)
            elif cmd == "default_get":
                await self.default_get(addr, app_index, arguments)
            elif cmd == "default_set":
                await self.default_set(addr, app_index, arguments)
            elif cmd == "default_set_unack":
                await self.default_set_unack(addr, app_index, arguments)
            elif cmd == "range_get":
                await self.range_get(addr, app_index, arguments)
            elif cmd == "range_set":
                await self.range_set(addr, app_index, arguments)
            elif cmd == "range_set_unack":
                await self.range_set_unack(addr, app_index, arguments)


def main():
    doc = """
    Light Lightness Client Sample Application

    Usage:
        light_lightness_client.py [-V] -t <token> -a <address> get
        light_lightness_client.py [-V] -t <token> -a <address> [--transition=<time>] set <lightness>
        light_lightness_client.py [-V] -t <token> -a <address> [--transition=<time>] set_unack <lightness>
        light_lightness_client.py [-V] -t <token> -a <address> linear_get
        light_lightness_client.py [-V] -t <token> -a <address> [--transition=<time>] linear_set <lightness>
        light_lightness_client.py [-V] -t <token> -a <address> [--transition=<time>] linear_set_unack <lightness>
        light_lightness_client.py [-V] -t <token> -a <address> last_get
        light_lightness_client.py [-V] -t <token> -a <address> default_get
        light_lightness_client.py [-V] -t <token> -a <address> default_set <lightness>
        light_lightness_client.py [-V] -t <token> -a <address> default_set_unack <lightness>
        light_lightness_client.py [-V] -t <token> -a <address> range_get
        light_lightness_client.py [-V] -t <token> -a <address> range_set <min> <max>
        light_lightness_client.py [-V] -t <token> -a <address> range_set_unack <min> <max>
        light_lightness_client.py [-h | --help]
        light_lightness_client.py --version

    Options:
        -t <token>              bluetooth-meshd node token
        -a <address>            Local node unicast address
        --transition=<time>     Transition time
        <lightness>             Lightness value: 0-65535
        <min>, <max>            Minimum and maximum Lightness values
        -h --help               Show this screen.
        -V                      Show verbose messages
        --version               Show version.
    """


    arguments = docopt(doc, version='1.0')

    if arguments['-V']:
        logging.basicConfig(level=logging.DEBUG)

    app_index = 0
    cmd = None

    if arguments['get']:
        cmd = 'get'
    elif arguments['set']:
        cmd = 'set'
    elif arguments['set_unack']:
        cmd = 'set_unack'
    elif arguments['linear_get']:
        cmd = 'linear_get'
    elif arguments['linear_set']:
        cmd = 'linear_set'
    elif arguments['linear_set_unack']:
        cmd = 'linear_set_unack'
    elif arguments['last_get']:
        cmd = 'last_get'
    elif arguments['default_get']:
        cmd = 'default_get'
    elif arguments['default_set']:
        cmd = 'default_set'
    elif arguments['default_set_unack']:
        cmd = 'default_set_unack'
    elif arguments['range_get']:
        cmd = 'range_get'
    elif arguments['range_set']:
        cmd = 'range_set'
    elif arguments['range_set_unack']:
        cmd = 'range_set_unack'
    else:
        print(doc)
        exit(-1);

    token = int(arguments['-t'], 16)
    addr = int(arguments['-a'], 16)

    loop = asyncio.get_event_loop()
    app = SampleApplication(loop)

    with suppress(KeyboardInterrupt):
        loop.run_until_complete(app.run(token, addr, app_index, cmd, arguments))


if __name__ == '__main__':
    main()

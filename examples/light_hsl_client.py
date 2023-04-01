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
G_DELAY = 0.5

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
        client = self.elements[0][LightHSLClient]
        result = await client.get([addr], app_index=app_index, timeout=G_TIMEOUT)
        print(result[addr])

    async def set(self, addr, app_index, arguments):
        client = self.elements[0][LightHSLClient]
        lightness = int(arguments['<lightness>'])
        hue = int(arguments['<hue>'])
        saturation = int(arguments['<saturation>'])
        transition_time = float(arguments['--transition']) if arguments['--transition'] else 0.0
        result = await client.set([addr], app_index=app_index,
                                  hsl_lightness=lightness,
                                  hsl_hue=hue,
                                  hsl_saturation=saturation,
                                  transition_time=transition_time)
        print(result[addr])

    async def set_unack(self, addr, app_index, arguments):
        client = self.elements[0][LightHSLClient]
        lightness = int(arguments['<lightness>'])
        hue = int(arguments['<hue>'])
        saturation = int(arguments['<saturation>'])
        transition_time = float(arguments['--transition']) if arguments['--transition'] else 0.0
        await client.set_unack(addr, app_index=app_index,
                               hsl_lightness=lightness,
                               hsl_hue=hue,
                               hsl_saturation=saturation,
                               transition_time=transition_time)

    async def target_get(self, addr, app_index, arguments):
        client = self.elements[0][LightHSLClient]
        result = await client.target_get([addr], app_index=app_index, timeout=G_TIMEOUT)
        print(result[addr])

    async def hue_get(self, addr, app_index, arguments):
        client = self.elements[0][LightHSLClient]
        result = await client.hue_get([addr], app_index=app_index, timeout=G_TIMEOUT)
        print(result[addr])

    async def hue_set(self, addr, app_index, arguments):
        client = self.elements[0][LightHSLClient]
        hue = int(arguments['<hue>'])
        transition_time = float(arguments['--transition']) if arguments['--transition'] else 0.0
        result = await client.hue_set([addr], app_index=app_index,
                                      hue=hue,
                                      transition_time=transition_time,
                                      timeout=G_TIMEOUT)
        print(result[addr])

    async def hue_set_unack(self, addr, app_index, arguments):
        client = self.elements[0][LightHSLClient]
        hue = int(arguments['<hue>'])
        transition_time = float(arguments['--transition']) if arguments['--transition'] else 0.0
        await client.hue_set_unack(addr, app_index=app_index,
                                   hue=hue,
                                   transition_time=transition_time)


    async def saturation_get(self, addr, app_index, arguments):
        client = self.elements[0][LightHSLClient]
        result = await client.saturation_get([addr], app_index=app_index, timeout=G_TIMEOUT)
        print(result[addr])

    async def saturation_set(self, addr, app_index, arguments):
        client = self.elements[0][LightHSLClient]
        saturation = int(arguments['<saturation>'])
        transition_time = float(arguments['--transition']) if arguments['--transition'] else 0.0
        result = await client.saturation_set([addr], app_index=app_index,
                                             saturation=saturation,
                                             transition_time=transition_time,
                                             timeout=G_TIMEOUT)
        print(result[addr])

    async def saturation_set_unack(self, addr, app_index, arguments):
        client = self.elements[0][LightHSLClient]
        saturation = int(arguments['<saturation>'])
        transition_time = float(arguments['--transition']) if arguments['--transition'] else 0.0
        await client.saturation_set_unack(addr, app_index=app_index,
                                          saturation=saturation,
                                          transition_time=transition_time)



    async def default_get(self, addr, app_index, arguments):
        client = self.elements[0][LightHSLClient]
        result = await client.default_get([addr], app_index=app_index, timeout=G_TIMEOUT)
        print(result[addr])

    async def default_set(self, addr, app_index, arguments):
        client = self.elements[0][LightHSLClient]
        lightness = int(arguments['<lightness>'])
        hue = int(arguments['<hue>'])
        saturation = int(arguments['<saturation>'])
        result = await client.default_set([addr], app_index=app_index,
                                          hsl_lightness=lightness,
                                          hsl_hue=hue,
                                          hsl_saturation=saturation)
        print(result[addr])

    async def default_set_unack(self, addr, app_index, arguments):
        client = self.elements[0][LightHSLClient]
        lightness = int(arguments['<lightness>'])
        hue = int(arguments['<hue>'])
        saturation = int(arguments['<saturation>'])
        await client.default_set_unack(addr, app_index=app_index,
                                       hsl_lightness=lightness,
                                       hsl_hue=hue,
                                       hsl_saturation=saturation)

    async def range_get(self, addr, app_index, arguments):
        client = self.elements[0][LightHSLClient]
        result = await client.range_get([addr], app_index=app_index)
        print(result[addr])

    async def range_set(self, addr, app_index, arguments):
        client = self.elements[0][LightHSLClient]
        hue_min = int(arguments['<hue_min>'])
        hue_max = int(arguments['<hue_max>'])
        saturation_min = int(arguments['<saturation_min>'])
        saturation_max = int(arguments['<saturation_max>'])
        result = await client.range_set([addr], app_index=app_index,
                                        hue_range_min=hue_min,
                                        hue_range_max=hue_max,
                                        saturation_range_min=saturation_min,
                                        saturation_range_max=saturation_max)
        print(result[addr])

    async def range_set_unack(self, addr, app_index, arguments):
        client = self.elements[0][LightHSLClient]
        hue_min = int(arguments['<hue_min>'])
        hue_max = int(arguments['<hue_max>'])
        saturation_min = int(arguments['<saturation_min>'])
        saturation_max = int(arguments['<saturation_max>'])
        await client.range_set_unack(addr, app_index=app_index,
                                     hue_range_min=hue_min,
                                     hue_range_max=hue_max,
                                     saturation_range_min=saturation_min,
                                     saturation_range_max=saturation_max)


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
            elif cmd == "target_get":
                await self.target_get(addr, app_index, arguments)
            elif cmd == "hue_get":
                await self.hue_get(addr, app_index, arguments)
            elif cmd == "hue_set":
                await self.hue_set(addr, app_index, arguments)
            elif cmd == "hue_set_unack":
                await self.hue_set_unack(addr, app_index, arguments)
            elif cmd == "saturation_get":
                await self.saturation_get(addr, app_index, arguments)
            elif cmd == "saturation_set":
                await self.saturation_set(addr, app_index, arguments)
            elif cmd == "saturation_set_unack":
                await self.saturation_set_unack(addr, app_index, arguments)
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
    Light HSL Client Sample Application

    Usage:
        light_hsl_client.py [-V] -t <token> -a <address> get
        light_hsl_client.py [-V] -t <token> -a <address> [--transition=<time>] set <lightness> <hue> <saturation>
        light_hsl_client.py [-V] -t <token> -a <address> [--transition=<time>] set_unack <lightness> <hue> <saturation>
        light_hsl_client.py [-V] -t <token> -a <address> target_get
        light_hsl_client.py [-V] -t <token> -a <address> hue_get
        light_hsl_client.py [-V] -t <token> -a <address> [--transition=<time>] hue_set <hue>
        light_hsl_client.py [-V] -t <token> -a <address> [--transition=<time>] hue_set_unack <hue>
        light_hsl_client.py [-V] -t <token> -a <address> sat_get [<saturation>]
        light_hsl_client.py [-V] -t <token> -a <address> [--transition=<time>] sat_set <saturation>
        light_hsl_client.py [-V] -t <token> -a <address> [--transition=<time>] sat_set_unack <saturation>
        light_hsl_client.py [-V] -t <token> -a <address> default_get
        light_hsl_client.py [-V] -t <token> -a <address> default_set <lightness> <hue> <saturation>
        light_hsl_client.py [-V] -t <token> -a <address> default_set_unack <lightness> <hue> <saturation>
        light_hsl_client.py [-V] -t <token> -a <address> range_get
        light_hsl_client.py [-V] -t <token> -a <address> range_set <hue_min> <hue_max> <saturation_min> <saturation_max>
        light_hsl_client.py [-V] -t <token> -a <address> range_set_unack <hue_min> <hue_max> <saturation_min> <saturation_max>
        light_hsl_client.py [-h | --help]
        light_hsl_client.py --version

    Options:
        -t <token>              bluetooth-meshd node token
        -a <address>            Local node unicast address
        <lightness>             Lightness value: 0-65535
        <hue>                   Hue value: 0-65535
        <saturation>            Saturation value: 0-65535
        --transition=<time>     Transition time
        -V                      Show verbose messages
        -h --help               Show this screen
        --version               Show version
    """

    arguments = docopt(doc, version='1.0')

    if arguments['-V']:
        logging.basicConfig(level=logging.DEBUG)

    cmd = None
    app_index = 0

    if arguments['get']:
        cmd = 'get'
    elif arguments['set']:
        cmd = 'set'
    elif arguments['set_unack']:
        cmd = 'set_unack'
    elif arguments['target_get']:
        cmd = 'target_get'
    elif arguments['hue_get']:
        cmd = 'hue_get'
    elif arguments['hue_set']:
        cmd = 'hue_set'
    elif arguments['hue_set_unack']:
        cmd = 'hue_set_unack'
    elif arguments['sat_get']:
        cmd = 'saturation_get'
    elif arguments['sat_set']:
        cmd = 'saturation_set'
    elif arguments['sat_set_unack']:
        cmd = 'saturation_set_unack'
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

    token = int(arguments['-t'], 16)
    addr = int(arguments['-a'], 16)

    loop = asyncio.get_event_loop()
    app = SampleApplication(loop)

    with suppress(KeyboardInterrupt):
        loop.run_until_complete(app.run(token, addr, app_index, cmd, arguments))


if __name__ == '__main__':
    main()

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
        client = self.elements[0][LightCTLClient]
        result = await client.get([addr], app_index=app_index, timeout=G_TIMEOUT)
        print(result[addr])

    async def set(self, addr, app_index, arguments):
        client = self.elements[0][LightCTLClient]
        lightness = int(arguments['<lightness>'])
        temperature = int(arguments['<temperature>'])
        transition_time = float(arguments['--transition']) if arguments['--transition'] else 0.0
        result = await client.set([addr],
                                   app_index=app_index,
                                   ctl_lightness=lightness,
                                   ctl_temperature=temperature,
                                   ctl_delta_uv=0,
                                   transition_time=transition_time,
                                   timeout=G_TIMEOUT)
        print(result[addr])

    async def set_unack(self, addr, app_index, arguments):
        client = self.elements[0][LightCTLClient]
        lightness = int(arguments['<lightness>'])
        temperature = int(arguments['<temperature>'])
        transition_time = float(arguments['--transition']) if arguments['--transition'] else 0.0
        await client.set_unack(addr,
                               app_index=app_index,
                               ctl_lightness=lightness,
                               ctl_temperature=temperature,
                               ctl_delta_uv=0,
                               transition_time=transition_time)

    async def temperature_get(self, addr, app_index, arguments):
        client = self.elements[0][LightCTLClient]
        result = await client.temperature_get([addr], app_index=app_index, timeout=G_TIMEOUT)
        print(result[addr])

    async def temperature_set(self, addr, app_index, arguments):
        client = self.elements[0][LightCTLClient]
        temperature = int(arguments['<temperature>'])
        transition_time = float(arguments['--transition']) if arguments['--transition'] else 0.0
        result = await client.temperature_set([addr],
                                              app_index=app_index,
                                              ctl_temperature=temperature,
                                              ctl_delta_uv=0,
                                              transition_time=transition_time,
                                              timeout=G_TIMEOUT)
        print(result[addr])

    async def temperature_set_unack(self, addr, app_index, arguments):
        client = self.elements[0][LightCTLClient]
        temperature = int(arguments['<temperature>'])
        transition_time = float(arguments['--transition']) if arguments['--transition'] else 0.0
        await client.temperature_set_unack(addr,
                                           app_index=app_index,
                                           ctl_temperature=temperature,
                                           ctl_delta_uv=0,
                                           transition_time=transition_time)

    async def temperature_range_get(self, addr, app_index, arguments):
        client = self.elements[0][LightCTLClient]
        result = await client.temperature_range_get([addr], app_index=app_index, timeout=G_TIMEOUT)
        print(result[addr])

    async def temperature_range_set(self, addr, app_index, arguments):
        client = self.elements[0][LightCTLClient]
        range_min = int(arguments['<min>'])
        range_max = int(arguments['<max>'])
        result = await client.temperature_range_set([addr],
                                                    app_index=app_index,
                                                    range_min=range_min,
                                                    range_max=range_max,
                                                    timeout=G_TIMEOUT)
        print(result[addr])

    async def temperature_range_set_unack(self, addr, app_index, arguments):
        client = self.elements[0][LightCTLClient]
        range_min = int(arguments['<min>'])
        range_max = int(arguments['<max>'])
        await client.temperature_range_set_unack(addr,
                                     app_index=app_index,
                                     range_min=range_min,
                                     range_max=range_max)

    async def default_get(self, addr, app_index, arguments):
        client = self.elements[0][LightCTLClient]
        result = await client.default_get([addr], app_index=app_index, timeout=G_TIMEOUT)
        print(result[addr])

    async def default_set(self, addr, app_index, arguments):
        client = self.elements[0][LightCTLClient]
        lightness = int(arguments['<lightness>'])
        temperature = int(arguments['<temperature>'])
        result = await client.default_set([addr],
                                          app_index=app_index,
                                          ctl_lightness=lightness,
                                          ctl_temperature=temperature,
                                          ctl_delta_uv=0,
                                          timeout=G_TIMEOUT)
        print(result[addr])

    async def default_set_unack(self, addr, app_index, arguments):
        client = self.elements[0][LightCTLClient]
        lightness = int(arguments['<lightness>'])
        temperature = int(arguments['<temperature>'])
        await client.default_set_unack(addr,
                                       app_index=app_index,
                                       ctl_lightness=lightness,
                                       ctl_temperature=temperature,
                                       ctl_delta_uv=0)


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
            elif cmd == "temperature_get":
                await self.temperature_get(addr, app_index, arguments)
            elif cmd == "temperature_set":
                await self.temperature_set(addr, app_index, arguments)
            elif cmd == "temperature_set_unack":
                await self.temperature_set_unack(addr, app_index, arguments)
            elif cmd == "temperature_range_get":
                await self.temperature_range_get(addr, app_index, arguments)
            elif cmd == "temperature_range_set":
                await self.temperature_range_set(addr, app_index, arguments)
            elif cmd == "temperature_range_set_unack":
                await self.temperature_range_set_unack(addr, app_index, arguments)
            elif cmd == "default_get":
                await self.default_get(addr, app_index, arguments)
            elif cmd == "default_set":
                await self.default_set(addr, app_index, arguments)
            elif cmd == "default_set_unack":
                await self.default_set_unack(addr, app_index, arguments)


def main():
    doc = """
    Light CTL Client Sample Application

    Usage:
        light_ctl_client.py [-V] -t <token> -a <address> get
        light_ctl_client.py [-V] -t <token> -a <address> [--transition=<time>] set <lightness> <temperature> [<delta_uv>]
        light_ctl_client.py [-V] -t <token> -a <address> [--transition=<time>] set_unack <lightness> <temperature> [<delta_uv>]
        light_ctl_client.py [-V] -t <token> -a <address> t_get
        light_ctl_client.py [-V] -t <token> -a <address> [--transition=<time>] t_set <temperature> [<delta_uv>]
        light_ctl_client.py [-V] -t <token> -a <address> [--transition=<time>] t_set_unack <temperature> [<delta_uv>]
        light_ctl_client.py [-V] -t <token> -a <address> t_range_get
        light_ctl_client.py [-V] -t <token> -a <address> t_range_set <min> <max>
        light_ctl_client.py [-V] -t <token> -a <address> t_range_set_unack <min> <max>
        light_ctl_client.py [-V] -t <token> -a <address> default_get
        light_ctl_client.py [-V] -t <token> -a <address> [--transition=<time>] default_set <lightness> <temperature> [<delta_uv>]
        light_ctl_client.py [-V] -t <token> -a <address> [--transition=<time>] default_set_unack <lightness> <temperature> [<delta_uv>]
        light_ctl_client.py [-h | --help]
        light_ctl_client.py --version

    Options:
        -t <token>              bluetooth-meshd node token
        -a <address>            Local node unicast address
        <lightness>             Lightness value: 0-65535
        <temperature>           Temperature value: 800-20000
        <min>, <max>            Minimum and maximum Temperature values
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
    elif arguments['set']:
        cmd = 'set'
    elif arguments['set_unack']:
        cmd = 'set_unack'
    elif arguments['t_get']:
        cmd = 'temperature_get'
    elif arguments['t_set']:
        cmd = 'temperature_set'
    elif arguments['t_set_unack']:
        cmd = 'temperature_set_unack'
    elif arguments['t_range_get']:
        cmd = 'temperature_range_get'
    elif arguments['t_range_set']:
        cmd = 'temperature_range_set'
    elif arguments['t_range_set_unack']:
        cmd = 'temperature_range_set_unack'
    elif arguments['default_get']:
        cmd = 'default_get'
    elif arguments['default_set']:
        cmd = 'default_set'
    elif arguments['default_set_unack']:
        cmd = 'default_set_unack'
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

#
# python-bluetooth-mesh - Bluetooth Mesh for Python
#
# Copyright (C) 2019  SILVAIR sp. z o.o.
#
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
#
import asyncio
import inspect
import itertools
import logging
import os
import shlex
import traceback
from collections import defaultdict
from concurrent import futures
from contextlib import suppress
from datetime import timedelta
from functools import lru_cache, partial
from uuid import UUID

from docopt import DocoptExit, docopt
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.eventloop import use_asyncio_event_loop
from prompt_toolkit.history import FileHistory
from prompt_toolkit.patch_stdout import patch_stdout

from bluetooth_mesh.application import Application, Element
from bluetooth_mesh.apps import get_plugin_manager
from bluetooth_mesh.crypto import DeviceKey, NetworkKey
from bluetooth_mesh.messages.config import (
    GATTNamespaceDescriptor,
    PublishPeriodStepResolution,
)
from bluetooth_mesh.models import (
    ConfigClient,
    ConfigServer,
    DebugClient,
    GatewayConfigClient,
    GenericLevelClient,
    GenericOnOffClient,
    HealthClient,
    LightCTLClient,
    LightExtendedControllerSetupClient,
    LightLightnessClient,
    NetworkDiagnosticClient,
    NetworkDiagnosticSetupClient,
    SceneClient,
)

plugin_manager = get_plugin_manager()


class MeshCompleter(Completer):
    def __init__(self, application):
        self.application = application
        super().__init__()

    def get_completions(self, document, complete_event):
        if not document.is_cursor_at_the_end:
            return

        command = document.text_before_cursor
        if " " not in command:  # try commands
            for cmd in self.application.commands.values():
                if cmd.CMD.startswith(command):
                    yield Completion(cmd.CMD, start_position=-len(command))

        else:
            words = shlex.split(command)
            if command.endswith(" "):  # wo for difference in split and shlex.split
                words.append("")
            if command.startswith(LsCommand.CMD) or "-g" in words:  # try groups
                for group in self.application.network.groups:
                    group_name = group.name or ""

                    if group_name.startswith(words[-1]):
                        if " " in group_name:
                            group_name = '"{}"'.format(group_name)
                        yield Completion(group_name, start_position=-len(words[-1]))

            else:  # try nodes
                for node in {
                    node.uuid.hex[:4] for node in self.application.network.nodes
                }:
                    if node.startswith(words[-1]):
                        yield Completion(node, start_position=-len(words[-1]))


class Command:
    USAGE = """
    Usage:
        %(cmd)s
    """
    CMD = None

    async def __call__(self, application, arguments):
        raise NotImplementedError()

    def get_usage(self, **kwargs):
        return self.USAGE % dict(cmd=self.CMD, **kwargs)

    def __lt__(self, other):
        return self.CMD < other.CMD


class NodeSelectionCommandMixin:
    USAGE = """
    Usage:
        %(cmd)s <uuid>...
        %(cmd)s -g <groups>...

    Options:
        -g --groups

    Use <group>.<index> or <uuid>.<index> to talk to non-primary elements.
    """

    @staticmethod
    def get_addresses(application, arguments):
        uuids = {}
        for uuid_element in arguments.get("<uuid>", []):
            uuid, *element = uuid_element.split(".", maxsplit=1)
            uuids[uuid] = int(element[0]) if element else 0

        groups = {}
        for group_element in arguments.get("<groups>", []):
            group, *element = group_element.split(".", maxsplit=1)
            groups[group] = int(element[0]) if element else 0

        nodes = []
        for node in application.network.nodes:
            offset = uuids.get(node.uuid.hex[:4])
            if offset is not None:
                nodes.append(node.address + offset)

            offset = groups.get(application.network.get_node_group(node))
            if offset is not None:
                nodes.append(node.address + offset)

        return nodes


class LsCommand(Command):
    USAGE = """
    Usage:
        %(cmd)s [options] [<groups>...]

    Options:
        -l --long
    """

    CMD = "ls"

    async def __call__(self, application, arguments):
        groups = arguments["<groups>"]

        if not groups and arguments["--long"]:
            groups = [group.name for group in application.network.groups]

        if groups:
            nodes = defaultdict(list)

            for node in application.network.nodes:
                group = application.network.get_node_group(node)

                if not groups or group in groups:
                    nodes[group].append(node)

            for group, nodes in sorted(nodes.items(), key=lambda n: n[0]):
                yield "{}:".format(group)
                for node in sorted(nodes, key=lambda n: n.uuid):
                    if arguments["--long"]:
                        yield "\t{} {:04x} {}".format(
                            node.uuid, node.address, node.name
                        )
                    else:
                        yield "\t{}".format(node.name)
        else:
            for group in sorted(
                group.name for group in application.network.groups if group.name
            ):
                yield "\t{}".format(group)


class ModelCommandMixin:
    ELEMENT = None
    MODEL = None

    def get_model(self, application):
        return application.elements[self.ELEMENT][self.MODEL]


class AttentionCommand(ModelCommandMixin, Command):
    USAGE = """
    Usage:
        %(cmd)s [options] <uuid>...
        %(cmd)s [options] -g <groups>...

    Options:
        -t --timeout=ATTENTION    Attention timer [default: 5].
        -g --groups
    """

    ELEMENT = 0
    MODEL = HealthClient
    CMD = "attention"

    async def __call__(self, application, arguments):
        model = self.get_model(application)

        attention = int(arguments["--timeout"])

        tasks = []
        if arguments["<uuid>"]:
            tasks = [
                model.attention(node.address, app_index=0, attention=attention)
                for node in application.network.nodes
                if node.uuid.hex[:4] in arguments["<uuid>"]
            ]

        elif arguments["<groups>"]:
            tasks = [
                model.attention_unack(
                    application.network.get_group_address(self.MODEL, name=name),
                    app_index=0,
                    attention=attention,
                )
                for name in arguments["<groups>"]
            ]

        return asyncio.gather(*tasks)


class SceneCommand(ModelCommandMixin, NodeSelectionCommandMixin, Command):
    USAGE = """
    Usage:
        %(cmd)s <uuid>...
        %(cmd)s -g <groups>...
        %(cmd)s -c <scene> [options] <uuid>...
        %(cmd)s -c <scene> [options] -g <groups>...

    Options:
        -c --scene=SCENE    Number of scene to recall.
        -t --transition-time=TRANSITION-TIME    Transition time in seconds [default: 0].
        -g --groups
    """
    ELEMENT = 0
    MODEL = SceneClient
    CMD = "scene"

    async def recall(self, model, application, arguments):
        scene_number = int(arguments["--scene"])
        transition_time = int(arguments["--transition-time"])

        tasks = []
        if arguments["<uuid>"]:
            tasks = [
                model.recall_scene_unack(
                    node.address,
                    app_index=0,
                    scene_number=scene_number,
                    transition_time=transition_time,
                )
                for node in application.network.nodes
                if node.uuid.hex[:4] in arguments["<uuid>"]
            ]

        elif arguments["<groups>"]:
            tasks = [
                model.recall_scene_unack(
                    application.network.get_group_address(self.MODEL, name=name),
                    app_index=0,
                    scene_number=scene_number,
                    transition_time=transition_time,
                )
                for name in arguments["<groups>"]
            ]

        for i in await asyncio.gather(*tasks):
            yield i

    async def get(self, model, application, arguments):
        addresses = self.get_addresses(application, arguments)
        results = await model.get_scene(nodes=addresses, app_index=0)

        for address, data in results.items():
            node = application.network.get_node(address=address)
            group = application.network.get_node_group(node)

            param = str(data["current_scene"]) if data is not None else None
            yield "{} | {}: {}".format(group, node.name, param)

    async def __call__(self, application, arguments):
        model = self.get_model(application)
        method = self.get if arguments["--scene"] is None else self.recall

        async for i in method(model, application, arguments):
            yield i or ""


class ModelGetCommandMixin(ModelCommandMixin, NodeSelectionCommandMixin):
    PARAMETER = None

    def format(self, data):
        return str(data[self.PARAMETER])

    async def __call__(self, application, arguments):
        model = self.get_model(application)
        addresses = self.get_addresses(application, arguments)

        get = getattr(model, "get_{}".format(self.PARAMETER))
        results = await get(addresses, 0)

        for address, data in results.items():
            node = application.network.get_node(address=address)
            group = application.network.get_node_group(node)

            param = self.format(data) if data is not None else None
            yield "{} | {}: {}".format(group, node.name, param)


class DebugCommand(ModelGetCommandMixin, Command):
    ELEMENT = 0
    MODEL = DebugClient


class UptimeCommand(DebugCommand):
    CMD = "uptime"
    PARAMETER = "uptime"

    def format(self, data):
        return str(timedelta(seconds=data["uptime"]))


class FaultCommand(DebugCommand):
    CMD = "fault"
    PARAMETER = "last_sw_fault"

    def format(self, data):
        return "{}, {}".format(data["fault"], timedelta(seconds=data["time"]))


class VersionCommand(DebugCommand):
    CMD = "version"
    PARAMETER = "firmware_version"

    def format(self, data):
        return str(data["version"])


class IvIndexCommand(DebugCommand):
    CMD = "ivindex"
    PARAMETER = "ivindex"


class ArapCommand(DebugCommand):
    CMD = "arap"
    PARAMETER = "arap_content"

    def format(self, data):
        return "\n" + "\n".join(
            "\t{:04x}: {:8d} ivi={:1d}".format(k, v["sequence"], v["ivi"])
            for k, v in data["nodes"].items()
        )


class StatsCommand(DebugCommand):
    CMD = "stats"
    PARAMETER = "system_stats"

    def format(self, data):
        return "\n" + "\n".join(
            "\t{:>10s}: {:5d}".format(k, v) for k, v in data["stats"].items()
        )


class AppVersionCommand(DebugCommand):
    CMD = "app_version"
    PARAMETER = "app_version"

    def format(self, data):
        return str(data["version"])


class ConfigCommand(ModelGetCommandMixin, Command):
    ELEMENT = 0
    MODEL = ConfigClient


class TtlCommand(ConfigCommand):
    CMD = "ttl"
    PARAMETER = "default_ttl"

    def format(self, data):
        return data["TTL"]


class RelayCommand(ConfigCommand):
    CMD = "relay"
    PARAMETER = "relay"

    def format(self, data):
        return "%s <interval: %sms, count: %s>" % (
            data["relay"],
            data["retransmit"]["interval"],
            data["retransmit"]["count"],
        )


class PublicationCommand(ModelCommandMixin, NodeSelectionCommandMixin, Command):
    ELEMENT = 0
    MODEL = ConfigClient
    CMD = "publication"
    USAGE = """
    Usage:
        %(cmd)s -e ELEMENT -m MODEL [options] <uuid>...
        %(cmd)s -e ELEMENT -m MODEL [options] -g <groups>...

    Options:
        -e --element=ELEMENT [default: 0]
        -a --address=ADDRESS
        -k --key-index=KEY_INDEX
        -t --ttl=TTL
        -c --count=COUNT
        -i --interval=INTERVAL
        -m --model=MODEL
    """

    async def __call__(self, application, arguments):
        from bluetooth_mesh import models

        model = self.get_model(application)
        addresses = self.get_addresses(application, arguments)

        for address in addresses:
            node = application.network.get_node(address=address)
            group = application.network.get_node_group(node)
            element_index = int(arguments["--element"])

            if arguments["--key-index"] is not None:
                interval = int(
                    timedelta(seconds=float(arguments["--interval"])).total_seconds()
                    * 1000
                )

                status = await model.set_publication(
                    address,
                    0,
                    element_address=address + element_index,
                    publication_address=int(arguments["--address"], 16),
                    app_key_index=int(arguments["--key-index"]),
                    TTL=int(arguments["--ttl"]),
                    publish_step_resolution=PublishPeriodStepResolution.RESOLUTION_10_S,
                    publish_number_of_steps=6,
                    retransmit_count=int(arguments["--count"]),
                    retransmit_interval=interval,
                    model=getattr(models, arguments["--model"]),
                )
            else:
                status = await model.get_publication(
                    address,
                    0,
                    element_address=address + element_index,
                    model=getattr(models, arguments["--model"]),
                )

            yield "{} | {}: #{} {} addr={:04x}, ttl={} key=#{} period={}, retransmit={}/{}".format(
                group,
                node.name,
                element_index,
                status.model.__name__,
                status.publication_address,
                status.ttl,
                status.app_key_index,
                status.period.total_seconds(),
                status.retransmissions["count"],
                status.retransmissions["interval"].total_seconds(),
            )


class GatewayConfigurationCommand(
    ModelCommandMixin, NodeSelectionCommandMixin, Command
):
    USAGE = (
        """
    Usage:
        %(cmd)s ("""
        "--mtu=MTU | --mac=MAC | --server=HOST:PORT | --reconnect=INTERVAL | "
        "--dns=IP | --ip=IP | --gateway=IP | --netmask=NETMASK | [--get] | "
        "--mtu=MTU --mac=MAC --server=HOST:PORT --reconnect=INTERVAL | "
        "--mtu=MTU --mac=MAC --server=HOST:PORT --reconnect=INTERVAL --dns=IP |"
        "--mtu=MTU --mac=MAC --server=HOST:PORT --reconnect=INTERVAL --dns=IP --ip=IP --netmask=NETMASK --gateway=IP"
        """) <uuid>

        %(cmd)s --mtu=MTU --mac=MAC --server=HOST:PORT --reconnect=INTERVAL <uuid>
        %(cmd)s --mtu=MTU --mac=MAC --server=HOST:PORT --reconnect=INTERVAL --dns=IP <uuid>
        %(cmd)s --mtu=MTU --mac=MAC --server=HOST:PORT --reconnect=INTERVAL --dns=IP --ip=IP --netmask=NETMASK --gateway=IP <uuid>
        %(cmd)s [--get=TYPE] <uuid>
    Options:
        --mtu=MTU               Set MTU size
        --mac=MAC               Set MAC address
        --server=SERVER:PORT    Set server's name nad port
        --reconnect=INTERVAL    Set reconnect interval
        --dns=IP                Set DNS IP address
        --ip=IP                 Set IP address
        --gateway=IP            Set gateway UP address
        --netmask=NETMASK       Set netmask
        --get                   Get current configuration
    """
    )

    CMD = "gateway"
    ELEMENT = 0
    MODEL = GatewayConfigClient

    async def __call__(self, application, arguments):
        model = self.get_model(application)

        # strip'--' prefixes from options and drop Nones
        kwargs = {
            k.lstrip("-"): v
            for k, v in arguments.items()
            if k.startswith("--") and v is not None
        }

        kwargs.pop("get", None)

        if len(kwargs) > 1:
            method = partial(model.configuration_set, **self.parse_args(kwargs))
        elif len(kwargs) > 0:
            ((name, value),) = kwargs.items()
            method = partial(getattr(model, f"{name}_set"), **self.parse_args(kwargs))
        else:
            method = getattr(model, f"configuration_get")

        tasks = [
            method(destination=node.address, net_index=0)
            for node in application.network.nodes
            if node.uuid.hex[:4] in arguments["<uuid>"]
        ]

        results = await asyncio.gather(*tasks)
        self.parse_status_payload(results[0]["params"]["payload"])

    @staticmethod
    def parse_args(args):
        parsed = {}
        for key in args:
            if key in ("mtu", "reconnect", "netmask"):
                parsed[key] = int(args[key])
            if key in ("mac", "dns", "ip", "gateway"):
                parsed[key] = args[key]
            if key in "server":
                # convert HOST:PORT into a Tuple
                host, port = args[key].split(":")
                parsed[key] = (host, int(port))

        return parsed

    @staticmethod
    def parse_status_payload(payload):
        server_addr = payload["server_address"]

        if server_addr == "":
            server_addr = "NONE"

        parsed = (
            "revision: {}\n"
            "mac: {}\n"
            "mtu: {}\n"
            "ip: {}/{}\n"
            "gateway: {}\n"
            "dns: {}\n"
            "server: {}:{}\n"
            "reconnect_interval: {}\n"
            "dhcp: {}\n"
            "status_code: {}".format(
                payload["chip_revision_id"],
                payload["mac_address"],
                payload["mtu_size"],
                payload["ip_address"],
                payload["netmask"],
                payload["gateway_ip_address"],
                payload["dns_ip_address"],
                server_addr,
                payload["server_port_number"],
                payload["reconnect_interval"],
                str(payload["flags"]),
                str(payload["status_code"]),
            )
        )
        print(parsed)


class GatewayPacketsCommand(ModelCommandMixin, NodeSelectionCommandMixin, Command):
    USAGE = """
    Usage:
        %(cmd)s [options] <uuid>

    Options:
        --clear     Clear packet's error counters
    """

    CMD = "packets"
    ELEMENT = 0
    MODEL = GatewayConfigClient

    async def __call__(self, application, arguments):
        model = self.get_model(application)

        if arguments["--clear"]:
            method = partial(model.packets_clear)
        else:
            method = partial(model.packets_get)

        tasks = [
            method(node.address, net_index=0)
            for node in application.network.nodes
            if node.uuid.hex[:4] in arguments["<uuid>"]
        ]

        results = await asyncio.gather(*tasks)
        self.parse_status_packets(results[0]["params"]["payload"])

    @staticmethod
    def parse_status_packets(payload):
        parsed = (
            "rx_errors: {}\n"
            "tx_errors: {}\n"
            "bandwidth: {}\n"
            "connection_state: {}\n"
            "link_status: {}\n"
            "last_error: {}".format(
                payload["total_eth_rx_errors"],
                payload["total_eth_tx_errors"],
                payload["bandwidth"],
                str(payload["connection_state"]["conn_state"]),
                str(payload["connection_state"]["link_status"]),
                str(payload["connection_state"]["last_error"]),
            )
        )
        print(parsed)


class AclCommand(Command):
    USAGE = """
    Usage:
        %(cmd)s 
        %(cmd)s --grant <uuid> [--devkey <devkey> --netkey <netkey>]
        %(cmd)s --revoke <uuid>

    Options:
        -g --grant=<uuid>      Grant
        -d --devkey=<devkey>   Devkey
        -n --netkey=<netkey>   Netkey
        -r --revoke=<uuid>     Revoke token
    """
    CMD = "acl"

    def format(self, application):
        for uuid, token in application.token_ring.acl():
            try:
                name = application.network.get_node(uuid=uuid).name
            except KeyError:
                name = None
            yield uuid, name, token

    async def __call__(self, application, arguments):
        if arguments["--grant"]:
            uuid = UUID(arguments["--grant"])
            dev_key = arguments["--devkey"]
            net_key = arguments["--netkey"]

            if not all([dev_key, net_key]):
                try:
                    dev_key = application.network.get_node(uuid=uuid).device_key
                    net_key = application.network.network_keys[0]
                except KeyError:
                    logging.getLogger("acl_grant").warning(
                        "Some key data is missing "
                        "but node could not be found in network configuration to automagically download it."
                    )
                    return
            else:
                dev_key = DeviceKey(bytes.fromhex(dev_key))
                net_key = NetworkKey(bytes.fromhex(net_key))

            await application.acl_grant(uuid=uuid, dev_key=dev_key, net_key=net_key)

        if arguments["--revoke"]:
            await application.acl_revoke(uuid=UUID(hex=arguments["--revoke"]))

        for uuid, name, token in self.format(application):
            print("\t%s (%s): %s" % (uuid, name, token))
        print()


class LightCommand(ModelCommandMixin, NodeSelectionCommandMixin, Command):
    USAGE = """
            Usage:
                %(cmd)s <uuid>... [--lightness <light>] [--temperature <temp>]
                %(cmd)s -g <groups>... [--lightness <light>] [--temperature <temp>]

            Options:
                -g --groups
                -l --lightness <light>
                -t --temperature <temp>
            """
    ELEMENT = 0
    CMD = "light"
    PARAMETER = "light_status"
    CTL_ELEMENT = 2

    def format(self, data_light, data_ctl):
        return "lightness {present_lightness}, temperature {present_ctl_temperature}".format(
            present_lightness=data_light.get("present_lightness")
            if data_light
            else None,
            present_ctl_temperature=data_ctl.get("present_ctl_temperature")
            if data_ctl
            else None,
        )

    async def __call__(self, application, arguments):
        addresses = self.get_addresses(application, arguments)

        self.MODEL = LightLightnessClient
        model = self.get_model(application)
        if arguments["--lightness"]:
            results_light = await model.set_lightness(
                nodes=addresses, app_index=0, lightness=int(arguments["--lightness"])
            )
        else:
            results_light = await model.get_lightness(nodes=addresses, app_index=0)

        self.MODEL = LightCTLClient
        model = self.get_model(application)
        if arguments["--temperature"]:
            results_ctl = await model.set_ctl(
                nodes=[addr + self.CTL_ELEMENT for addr in addresses],
                app_index=0,
                ctl_temperature=int(arguments["--temperature"]),
            )
        else:
            results_ctl = await model.get_ctl(
                nodes=[addr + self.CTL_ELEMENT for addr in addresses], app_index=0
            )

        for address in addresses:
            node = application.network.get_node(address=address)
            param = self.format(
                results_light[address], results_ctl[address + self.CTL_ELEMENT]
            )
            print("{}: {}".format(node.name, param))


class NetworkTransmissionCommand(ModelCommandMixin, NodeSelectionCommandMixin, Command):
    USAGE = """
        Usage:
            %(cmd)s <uuid>... [--interval <millis>] [--count <count>]
            %(cmd)s -g <groups>... [--interval <millis>] [--count <count>]

        Options:
            -g --groups
            -s --interval <millis>
            -c --count <count>
        """
    ELEMENT = 0
    MODEL = ConfigClient
    CMD = "net_transmission"
    PARAMETER = "net_transmission"

    def format(self, data):
        return "interval={}ms, count={}".format(*data)

    async def __call__(self, application, arguments):
        model = self.get_model(application)
        addresses = self.get_addresses(application, arguments)

        for address in addresses:
            if arguments["--interval"] and arguments["--count"]:
                results = await model.set_network_transmission(
                    address,
                    net_index=0,
                    interval=int(arguments["--interval"]),
                    count=int(arguments["--count"]),
                )
            else:
                results = await model.get_network_transmission(address, net_index=0)

            node = application.network.get_node(address=address)
            param = self.format(results) if results is not None else None
            print("{}: {}".format(node.name, param))


class CompositionDataCommand(ModelCommandMixin, NodeSelectionCommandMixin, Command):
    ELEMENT = 0
    MODEL = ConfigClient
    CMD = "composition"
    PARAMETER = "composition_data"

    async def __call__(self, application, arguments):
        model = self.get_model(application)
        addresses = self.get_addresses(application, arguments)

        for address in addresses:
            data = await model.get_composition_data([address], net_index=0)
            node = application.network.get_node(address=address)

            composition = data[address]["data"]

            yield "{}: CID {}, PID {}, VID {}, CRPL {}, Features {:016b}".format(
                node.name,
                composition["CID"],
                composition["PID"],
                composition["VID"],
                composition["CRPL"],
                composition["features"],
            )

            for i, ele in enumerate(composition["elements"]):
                yield "\tElement {}, location: {}".format(i, ele["location"])
                yield "\t\t   SIG Models: " + ", ".join(
                    "{:04x}".format(mod["model_id"]) for mod in ele["SIG_models"]
                )
                yield "\t\tVendor Models: " + ", ".join(
                    "{:04x}:{:04x}".format(mod["vendor_id"], mod["model_id"])
                    for mod in ele["vendor_models"]
                )


class GenericOnOffCommand(ModelCommandMixin, Command):
    USAGE = """
    Usage:
        %(cmd)s <uuid>...
        %(cmd)s -g <groups>...

    Options:
        -g --groups
    """
    TARGET = None
    MODEL = GenericOnOffClient
    ELEMENT = 0
    PARAMETER = "set_onoff"

    async def __call__(self, application, arguments):
        model = self.get_model(application)

        tasks = []
        if arguments["<uuid>"]:
            command = getattr(model, self.PARAMETER)
            tasks = [
                command(node.address, app_index=0, onoff=self.TARGET)
                for node in application.network.nodes
                if node.uuid.hex[:4] in arguments["<uuid>"]
            ]

        elif arguments["<groups>"]:
            command = getattr(model, "{}_unack".format(self.PARAMETER))
            tasks = [
                command(
                    application.network.get_group_address(self.MODEL, name=name),
                    app_index=0,
                    onoff=self.TARGET,
                )
                for name in arguments["<groups>"]
            ]

        await asyncio.gather(*tasks)


class GenericOnCommand(GenericOnOffCommand):
    CMD = "on"
    TARGET = True


class GenericOffCommand(GenericOnOffCommand):
    CMD = "off"
    TARGET = False


class MorseCommand(ModelCommandMixin, Command):
    USAGE = """
    Usage:
        %(cmd)s -g <group> <text>

    Options:
        -g --group
    """
    CMD = "morse"
    MODEL = GenericLevelClient
    ELEMENT = 0
    PARAMETER = "set_onoff_unack"

    CODE = {
        "A": ".-",
        "B": "-...",
        "C": "-.-.",
        "D": "-..",
        "E": ".",
        "F": "..-.",
        "G": "--.",
        "H": "....",
        "I": "..",
        "J": ".---",
        "K": "-.-",
        "L": ".-..",
        "M": "--",
        "N": "-.",
        "O": "---",
        "P": ".--.",
        "Q": "--.-",
        "R": ".-.",
        "S": "...",
        "T": "-",
        "U": "..-",
        "V": "...-",
        "W": ".--",
        "X": "-..-",
        "Y": "-.--",
        "Z": "--..",
        "1": ".----",
        "2": "..---",
        "3": "...--",
        "4": "....-",
        "5": ".....",
        "6": "-....",
        "7": "--...",
        "8": "---..",
        "9": "----.",
        "0": "-----",
        ".": ".-.-.-",
        ",": "--..--",
        ":": "---...",
        "?": "..--..",
        "'": ".----.",
        "-": "-....-",
        "/": "-..-.",
        "@": ".--.-.",
        "=": "-...-",
    }

    async def __call__(self, application, arguments):
        model = self.get_model(application)

        destination = application.network.get_group_address(
            self.MODEL, name=arguments["<group>"]
        )

        send_interval = 0.01
        retransmissions = 6

        set_unack = partial(
            model.set_level_unack,
            destination=destination,
            app_index=0,
            retransmissions=retransmissions,
            send_interval=send_interval,
        )

        on = partial(set_unack, level=32767)
        off = partial(set_unack, level=-24576)

        try:
            # warm up time
            await off()
            await asyncio.sleep(0.5)

            for letter in arguments["<text>"].upper():
                code = self.CODE[letter]
                logging.getLogger("morse").info("%s = %s", letter, code)

                for blink in code:
                    await on(delay=retransmissions * send_interval)

                    delay = (
                        retransmissions * send_interval + 0.1 if blink == "." else 0.5
                    )
                    await off(delay=delay)
                    await asyncio.sleep(delay + 0.1)

                await asyncio.sleep(0.3)
        finally:
            await set_unack(level=-32768)


class LightExtendedControllerCommand(
    ModelCommandMixin, NodeSelectionCommandMixin, Command
):
    USAGE = """
    Usage:
        %(cmd)s <uuid>...
        %(cmd)s -g <groups>...
    """
    ELEMENT = 0
    MODEL = LightExtendedControllerSetupClient
    CMD = "lec"

    async def __call__(self, application, arguments):
        model = self.get_model(application)
        addresses = self.get_addresses(application, arguments)

        auto_resume = await model.get_auto_resume_mode(nodes=addresses, net_index=0)
        auto_timer = await model.get_auto_resume_timer(nodes=addresses, net_index=0)

        results = {
            k: (auto_resume.get(k), auto_timer.get(k))
            for k in {*auto_resume.keys(), *auto_timer.keys()}
        }

        for address, (resume, timer) in results.items():
            node = application.network.get_node(address=address)
            group = application.network.get_node_group(node)

            yield "{} | {}: resume={}, timer={}".format(group, node.name, resume, timer)


class HelpCommand(Command):
    CMD = "help"

    async def __call__(self, application, arguments):
        for cmd in sorted(application.commands.values()):
            yield "\t{}".format(cmd.CMD)


class PrimaryElement(Element):
    LOCATION = GATTNamespaceDescriptor.FORTY_SECOND

    MODELS = [
        GenericLevelClient,
        LightLightnessClient,
        LightCTLClient,
        GatewayConfigClient,
        ConfigServer,
        ConfigClient,
        HealthClient,
        DebugClient,
        GenericOnOffClient,
        SceneClient,
        NetworkDiagnosticClient,
        NetworkDiagnosticSetupClient,
        LightExtendedControllerSetupClient,
    ]


application_mixins = itertools.chain(*get_plugin_manager().hook.application_mixins())


class MeshCommandLine(*application_mixins, Application):
    PATH = "/com/silvair/meshcli/v7"

    COMMANDS = [
        HelpCommand,
        LsCommand,
        AttentionCommand,
        SceneCommand,
        UptimeCommand,
        FaultCommand,
        VersionCommand,
        IvIndexCommand,
        ArapCommand,
        StatsCommand,
        AppVersionCommand,
        LightCommand,
        GenericOnCommand,
        GenericOffCommand,
        CompositionDataCommand,
        MorseCommand,
        NetworkTransmissionCommand,
        TtlCommand,
        RelayCommand,
        GatewayConfigurationCommand,
        GatewayPacketsCommand,
        AclCommand,
        PublicationCommand,
        LightExtendedControllerCommand,
    ]

    COMPANY_ID = 0xFEE5
    PRODUCT_ID = 0x42
    VERSION_ID = 1
    CRPL = 0xF00

    ELEMENTS = {0: PrimaryElement}

    def __init__(self, loop: asyncio.AbstractEventLoop, arguments):
        self.config_dir = os.path.expanduser("~/.config/meshcli")
        os.makedirs(self.config_dir, exist_ok=True)

        super().__init__(loop)
        self.arguments = arguments

        self.history = FileHistory(f"{self.config_dir}/history")
        self.completer = MeshCompleter(self)
        self.session = PromptSession(
            history=self.history, completer=self.completer, complete_while_typing=False,
        )
        self.commands = {cmd.CMD: cmd() for cmd in self.COMMANDS}
        self._tid = 0

    def get_cache_args(self):
        return (f"{self.config_dir}/cache",), {}

    @property
    @lru_cache(maxsize=1)
    def dev_key(self) -> DeviceKey:
        try:
            with open(f"{self.config_dir}/{self.uuid}.key", "rb") as dev_key:
                return DeviceKey(dev_key.read())
        except FileNotFoundError:
            key = DeviceKey(os.urandom(16))

            with open(f"{self.config_dir}/{self.uuid}.key", "wb") as dev_key:
                dev_key.write(key.bytes)

            return key

    async def get_network(
        self, get_address=True, environment="preprod", partner_id="silvair"
    ):
        return await super().get_network(
            get_address, self.arguments["--env"], self.arguments["--partner"]
        )

    async def add_keys(self):
        for index, key in self.subnet_keys:
            await self.add_net_key(index, key)

        for index, bound, key in self.app_keys:
            await self.add_app_key(
                net_key_index=bound, app_key_index=index, app_key=key
            )

        for node in self.network.nodes:
            # don't overwrite my own key
            if node.address in range(self.addr, self.addr + len(self.ELEMENTS)):
                continue

            await self.management_interface.import_remote_node(
                node.address, len(node.elements), DeviceKey(node.device_key.bytes)
            )

        debug_client = self.get_model_instance(element=0, model=DebugClient)
        health_client = self.get_model_instance(element=0, model=HealthClient)

        for index, *_ in self.app_keys:
            await debug_client.bind(index)
            await health_client.bind(index)

    async def run(self, command):
        addr, self.network = await self.get_network()

        async with self:
            await self._run(addr, command)

    async def _run(self, addr, command):
        await self.connect(addr, socket_path=f"{self.config_dir}/{self.uuid}.socket")
        await self.add_keys()
        self.logger.info(
            "Loaded network %s, %d nodes", self.network, len(self.network.nodes)
        )

        while True:
            if command is not None:
                self.logger.info("Running command: %s", command)
                line = command
            else:
                line = await self.session.prompt("{}> ".format(self.uuid), async_=True)

                if not line.strip():
                    continue

            cmd, *argv = shlex.split(line)

            handler = self.commands.get(cmd, None)

            if not handler:
                print("Command not found: {}".format(cmd))
                continue

            usage = handler.get_usage()
            try:
                arguments = docopt(usage, argv, help=False)

                lines = []
                result = handler(self, arguments)

                if inspect.isasyncgen(result):
                    async for line in result:
                        lines.append(line)
                elif inspect.isawaitable(result):
                    result = await result

                    if result is not None:
                        lines.append(str())

                if lines:
                    print("\n".join(lines))
            except Exception as ex:
                print(traceback.format_exc())
            except futures.TimeoutError:
                print("Command timed out: {}".format(cmd))
            except KeyboardInterrupt:
                pass
            except DocoptExit:
                print(usage.strip("\n").rstrip())

            if command:
                break


def main():
    doc = """
        Mesh CLI

        Usage:
            meshcli [options] [<command>]
            meshcli -h | --help | --version

        Options:
            -l --login <login>             User login to platform service (email)
            -p --password <password>       User password to platform service (!unsecured!)
            -n --project <project>         Project name to be loaded from platform

            --partner <partner>            Partner identifier [default: silvair]
            --env <environment>            Environment: dev,preprod or prod [default: preprod]

            -d --debug
            -h --help                      Show this help message and exit
            --version                      Show version and exit
    """
    use_asyncio_event_loop()
    arguments = docopt(doc, version="stat_checker 0.5")

    logging.basicConfig(
        format="%(asctime)s %(name)-40s %(levelname)-8s %(filename)15s:%(lineno)3s  %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    loop = asyncio.get_event_loop()
    mesh_cli = MeshCommandLine(loop, arguments)

    with suppress(EOFError, KeyboardInterrupt), patch_stdout():
        loop.run_until_complete(mesh_cli.run(arguments.get("<command>")))

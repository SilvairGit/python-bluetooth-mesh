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
import logging
import os
import time

from contextlib import contextmanager, suppress
from itertools import cycle

import bitstring

from docopt import docopt
from gi.repository import GLib, GObject
from prompt_toolkit.history import FileHistory

from bluetooth_mesh.eventloop import use_glib_event_loop
from bluetooth_mesh.repl import REPL
from bluetooth_mesh.gatt import Adapter
from bluetooth_mesh.proxy import ServiceId, GattProxy
from bluetooth_mesh.mesh import BeaconType, SecureNetworkBeacon, AccessMessage
from bluetooth_mesh.schema import NetworkSchema
from bluetooth_mesh.cli.display import Display, Font


class GattClient(GObject.Object):
    def __init__(self, network, adapter):
        self.logger = logging.getLogger('gatt.%s.%s' % (adapter.name,
                                                        network.id.hex()))
        super().__init__()

        self._network = network
        self._adapter = adapter
        self._proxy = None

        self._adapter.device_discovered.connect(self._device_discovered)

    @property
    def network_id(self):
        return self._network.id

    def send(self, access_message, seq, *, device_key=False):
        for seq, pdu in self._network.message_encode(access_message, seq,
                                                     device_key=device_key):
            self._proxy.packet_send(pdu)

        return seq + 1

    def _start_proxy(self, device):
        self.logger.info('Starting proxy')
        self._proxy = GattProxy(device)
        self._proxy.mesh_beacon_received.connect(self._mesh_beacon_received)
        self._proxy.network_pdu_received.connect(self._network_pdu_received)
        self._proxy.start()

    def _device_discovered(self, _, device):
        if not self._is_proxy(device):
            return

        self.logger.info('Found proxy: %s "%s"', device.Address, device.Name)

        if self._proxy is None:
            self.logger.info('Connecting to %s "%s"',
                             device.Address, device.Name)
            if device.ServicesResolved:
                device.Connect()
                self._start_proxy(device)
            else:
                device.services_resolved.connect(self._start_proxy)
                device.Connect()

    def _mesh_beacon_received(self, _, payload):
        try:
            type, beacon = BeaconType(payload[0]), payload[1:]
        except ValueError:
            return

        if type == BeaconType.UNPROVISIONED_DEVICE:
            pass
        elif type == BeaconType.SECURE_NETWORK:
            beacon, auth = SecureNetworkBeacon.unpack(beacon)
            self._network.beacon_receive(beacon, auth)

    def _network_pdu_received(self, _, payload):
        pass

    def _is_proxy(self, device):
        proxy_data = device.ServiceData.get(ServiceId.MESH_PROXY.value)
        return proxy_data and proxy_data[1:] == self.network_id

    def _stop_discovery(self):
        with suppress(GLib.GError):
            self._adapter.stop_discovery()

    def start(self, timeout=5.0):
        GLib.timeout_add(timeout * 1000, self._stop_discovery)
        self._adapter.start_discovery(ServiceId.MESH_PROXY.value)


class CommandLine(REPL, GObject.Object):
    def __init__(self, client, loop=None):
        self._client = client

        self._dir = os.path.expanduser('~/.cache/python-bluetooth-mesh')
        os.makedirs(self._dir, exist_ok=True)

        history = os.path.join(self._dir, 'gatt-client.history')
        super().__init__(loop, prompt=dict(history=FileHistory(history)))

        self._commands = dict(
            attention=self.cmd_attention,
            nodes=self.cmd_nodes,
            off=self.cmd_off,
            on=self.cmd_on,
            publish=self.cmd_publish,
            slow=self.cmd_slow,
            show=self.cmd_show,
            src=self.cmd_src,
            untranslate=self.cmd_untranslate,
            translate=self.cmd_translate,
            unsubscribe=self.cmd_unsubscribe,
            subscribe=self.cmd_subscribe,
        )

        self._tid = cycle(range(255))
        self._seq = None
        self._seq_load()

        self._display = Display(client._network)

    def _seq_load(self):
        try:
            with open(os.path.join(self._dir, 'gatt-client.sequence')) as f:
                src, seq = f.readline().split()
                src = int(src, 16)
                seq = int(seq)
        except (FileNotFoundError, ValueError):
            src = 0
            seq = 0

        with self._seq_update():
            self._src = src
            self._seq = seq

    @contextmanager
    def _seq_update(self):
        try:
            yield
        finally:
            with open(os.path.join(self._dir, 'gatt-client.sequence'), 'w') as f:
                f.write('%04x %d' % (self._src, self._seq))

        return self._src, self._seq

    @property
    def network(self):
        return self._client._network

    def _send(self, payload, *destinations, device_key=False):
        with self._seq_update():
            for dst in destinations:
                access_message = AccessMessage(self._src, dst, ttl=2,
                                               payload=payload)
                print('%04x -> %04x @ %5d %s' % (self._src, dst, self._seq,
                                                 payload.hex()))
                self._seq = self._client.send(access_message, self._seq,
                                              device_key=device_key)

    def cmd_src(self, argv):
        if argv:
            with self._seq_update():
                addr, seq = argv.split()
                self._src = int(addr, 16)
                self._seq = int(seq)
        else:
            print('%04x %d' % (self._src, self._seq))

    def cmd_unsubscribe(self, argv):
        opcode = b'\x80\x1d'  # subcription delete all

        for node in self.network.nodes.values():
            address = node.address

            model = 0x1203  # scene server
            payload = bitstring.pack('bytes, uintle:16, uintle:16',
                                     opcode, address + 0, model)

            self._send(payload.bytes, address, device_key=True)

            model = 0x1000  # generic on off server
            payload = bitstring.pack('bytes, uintle:16, uintle:16',
                                     opcode, address + 2, model)

            self._send(payload.bytes, address, device_key=True)

    def cmd_subscribe(self, argv):
        opcode = b'\x80\x1b'  # subscription add
        model = 0x1000  # generic on off server

        for node in self.network.nodes.values():
            for letter in argv or Font.LETTERS:
                index, _ = self._display.font.glyph(letter)
                group = 0xd000 + index

                print("Subscribe %04x:%04x to %04x" % (node.address, model, group))

                payload = bitstring.pack('bytes, uintle:16, uintle:16, uintle:16',
                                         opcode, node.address + 2, group, model)

                self._send(payload.bytes, node.address, device_key=True)
                time.sleep(0.2)

    def cmd_untranslate(self, argv):
        opcode = b'\xf8\x36\x01\x03'  # scene translator, translation delete all

        for node in self.network.nodes.values():
            self._send(opcode, node.address + 2,
                       device_key=node.address)

    def cmd_translate(self, argv):
        opcode = b'\xf8\x36\x01\x00'  # scene translator, translation store
        trigger = 1

        for node in self.network.nodes.values():
            try:
                row, col = self._display.node2dot[node.address]
            except KeyError:
                continue

            for letter in argv or Font.LETTERS:
                index, glyph = self._display.font.glyph(letter)
                scene = 2 if glyph[row][col] else 1

                group = 0xd000 + index

                payload = bitstring.pack('bytes, uintle:16, uint:8, uintle:16',
                                         opcode, group, trigger, scene)

                print('Translate %04x:%04x to %04x' % (node.address, group, scene))

                # scene translator is on element #2
                self._send(payload.bytes, node.address + 2,
                           device_key=node.address)
                time.sleep(0.1)

    def cmd_publish(self, argv):
        opcode = b'\x03'  # publication set
        model = 0x1205  # scene client

        steps = 0
        resolution = 0
        ttl = 0
        count = 0
        interval = 1

        for node in self.network.nodes.values():
            payload = bitstring.pack('bytes, uintle:16, uintle:16, uint:12, uint:1, pad:3, '
                                     'uint:8, uint:2, uint:6, uint:3, uint:5, '
                                     'uintle:16',
                                     opcode, node.address + 2, node.address, 0, 0,
                                     ttl, resolution, steps, count, interval, model)

            print('Publish %04x:%08x to %04x' % (node.address + 2, model, node.address))

            # config server is on element #0
            self._send(payload.bytes, node.address, device_key=True)

    def cmd_show(self, argv):
        opcode = b'\x82\x03'  # generic onoff set unacknowledged
        value = 1
        steps = 0
        resolution = 0
        delay = 0

        for letter in argv.replace('_', ' '):
            index, _ = self._display.font.glyph(letter)
            group = 0xd000 + index
            tid = next(self._tid)

            payload = bitstring.pack('bytes, uint:8, uint:8, uint:2, uint:6, uint:8',
                                     opcode, value, tid, resolution, steps, delay)

            self._send(payload.bytes, group)
            time.sleep(1.0)

    def _cmd_onoff(self, argv, onoff):
        opcode = b'\x82\x03'  # generic onoff set unacknowledged

        for col, row in (i.split(',') for i in argv.split()):
            try:
                dst = self._display.dot2node[(int(col), int(row))]
            except KeyError:
                continue

            tid = next(self._tid)
            steps = 0
            resolution = 0
            delay = 0

            payload = bitstring.pack('bytes, uint:8, uint:8, uint:2, uint:6, uint:8',
                                     opcode, onoff, tid, resolution, steps, delay)

            self._send(payload.bytes, dst)

    def cmd_on(self, argv):
        self._cmd_onoff(argv, onoff=1)

    def cmd_off(self, argv):
        self._cmd_onoff(argv, onoff=0)

    def cmd_slow(self, argv):
        opcode = b'\x82\x03'  # generic onoff set unacknowledged
        steps = 0
        resolution = 0
        delay = 0

        for node in self.network.nodes.values():
            try:
                row, col = self._display.node2dot[node.address]
            except KeyError:
                continue

            for letter in argv.replace('_', ' '):
                _, glyph = self._display.font.glyph(letter)
                value = 1 if glyph[row][col] else 0
                tid = next(self._tid)

                payload = bitstring.pack('bytes, uint:8, uint:8, uint:2, uint:6, uint:8',
                                         opcode, value, tid, resolution, steps, delay)

                self._send(payload.bytes, node.address)

    def cmd_attention(self, argv):
        opcode = b'\x80\x05\x0a'  # attention

        dst = [int(i, 16) for i in argv.split()]

        self._send(opcode, *dst)

    def cmd_nodes(self, argv):
        for i in self.network.nodes.values():
            print('%s %04x' % (i, i.address))

    @property
    def prompt(self):
        return '%s> ' % self._client.network_id.hex()

    def command(self, command):
        cmd, *argv = command.split(maxsplit=1)
        return self._commands[cmd](argv[0] if argv else '')


def main(argv=None):
    '''Bluetooth Mesh Client

    Usage:
        gatt-client [options] <network>

    Options:
    '''
    logging.basicConfig(level=logging.DEBUG)

    loop = GLib.MainLoop()

    use_glib_event_loop(loop)

    args = docopt(main.__doc__, argv=argv)

    with open(args['<network>']) as f:
        schema = NetworkSchema()
        network = schema.loads(f.read())

    adapter = Adapter('hci0')
    client = GattClient(network, adapter)

    def quit():
        print("Cannot find proxy")
        loop.quit()

    def cli(sender):
        GLib.Source.remove(timeout)
        CommandLine(client, loop=loop)

    timeout = GLib.timeout_add(5000, quit)
    network.connected.connect(cli)

    client.start()

    loop.run()

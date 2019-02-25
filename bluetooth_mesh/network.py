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
from gi.repository import GObject

from bluetooth_mesh.mesh import NetworkMessage


class Network(GObject.Object):
    def __init__(self, name, uuid, network_keys,
                 application_keys=None, device_keys=None):
        super().__init__()

        self.name = name
        self.uuid = uuid

        self.application_keys = application_keys or []
        self.network_keys = network_keys
        self.device_keys = device_keys or {}
        self.nodes = {}
        self.shorts = {}
        self.addrs = {}
        self.spaces = {}
        self.iv_index = None

    @property
    def id(self):
        return self.network_keys[0].network_id

    def beacon_receive(self, beacon, auth):
        for network_key in self.network_keys:
            if not beacon.verify(auth, network_key):
                continue

            self.iv_index = beacon.iv_index
            self.connected.emit()

    def message_encode(self, message, seq, *, device_key=False):
        network_message = NetworkMessage(message)

        network_key = self.network_keys[0]

        if device_key is True:
            device_key = self.device_keys[message.dst]
        elif device_key:
            device_key = self.device_keys[device_key]

        application_key = device_key or self.application_keys[0]

        return network_message.pack(application_key, network_key, seq, self.iv_index)

    @GObject.Signal()
    def connected(self):
        pass

    def __str__(self):
        return '<%s: "%s" %s>' % (type(self).__name__, self.name, self.uuid)


class Node:
    def __init__(self, name, uuid, device_key, address):
        self.name = name
        self.uuid = uuid
        self.device_key = device_key
        self.address = address
        self.tags = {}

    def __str__(self):
        return '<%s: "%s" %s>' % (type(self).__name__, self.name, self.uuid)


class Space:
    def __init__(self, name, id):
        self.name = name
        self.id = id
        self.addresses = []

    def __str__(self):
        return '<%s: "%s" %s>' % (type(self).__name__, self.name, self.id)

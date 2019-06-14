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
from marshmallow import Schema, fields, decorators

import bitstring

from bluetooth_mesh.crypto import DeviceKey, NetworkKey, ApplicationKey
from bluetooth_mesh.network import Network, Node, Space


class SceneSchema(Schema):
    pass


class ApplicationSchema(Schema):
    applicationUuid = fields.UUID()
    unicastAddresses = fields.List(fields.Integer())


class NetKeySchema(Schema):
    index = fields.Integer()
    name = fields.String()
    key = fields.String()

    @decorators.post_load
    def _to_object(self, data):
        return NetworkKey(bytes.fromhex(data['key']))


class AppKeySchema(Schema):
    index = fields.Integer()
    name = fields.String()
    key = fields.String()
    bound = fields.Boolean()

    @decorators.post_load
    def _to_object(self, data):
        return ApplicationKey(bytes.fromhex(data['key']))


class ModelSchema(Schema):
    id = fields.Integer()
    configuration = fields.Dict()
    sensorDescriptors = fields.List(fields.Dict())


class ElementSchema(Schema):
    index = fields.Integer()
    models = fields.Nested(ModelSchema, many=True)
    locationDescriptor = fields.Integer()
    unicastAddress = fields.Integer()


class NodeSchema(Schema):
    name = fields.String()
    uuid = fields.UUID()
    tags = fields.Dict()
    elements = fields.Nested(ElementSchema, many=True)
    deviceKey = fields.String()
    primaryElementUnicastAddress = fields.Integer()
    configuration = fields.Dict()
    tags = fields.Dict()
    status = fields.String()
    description = fields.Dict()

    @decorators.post_load
    def _to_object(self, data):
        node = Node(
            data['name'],
            data['uuid'],
            device_key=DeviceKey(bytes.fromhex(data['deviceKey'])),
            address=data['primaryElementUnicastAddress'])

        node.tags = data['tags']

        return node


class GroupSchema(Schema):
    address = fields.Integer()
    tags = fields.Dict(keys=fields.String())
    name = fields.String()


class NetworkSchema(Schema):
    name = fields.String()
    uuid = fields.UUID()
    groups = fields.Nested(GroupSchema, many=True)
    appKeys = fields.Nested(AppKeySchema, many=True)
    netKeys = fields.Nested(NetKeySchema, many=True)
    nodes = fields.Nested(NodeSchema, many=True)
    applications = fields.List(fields.Dict())

    @decorators.post_load
    def _to_object(self, data):
        network = Network(
            data['name'],
            data['uuid'],
            network_keys=data['netKeys'],
            application_keys=data['appKeys'])

        for node in data['nodes']:
            network.nodes[node.uuid] = node
            short_id = int(node.uuid.hex[:4], 16)
            network.shorts[short_id] = node
            network.addrs[node.address] = node
            network.device_keys[node.address] = node.device_key
            space = Space(node.tags['spaceName'], node.tags['spaceId'])
            network.spaces[space.id] = space

        for group in data['groups']:
            id = group['tags']['spaceId']

            if id in network.spaces:
                network.spaces[id].addresses.append(group['address'])

        return network

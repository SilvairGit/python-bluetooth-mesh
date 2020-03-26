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
import os
import warnings
from typing import Dict
from uuid import UUID
from marshmallow import Schema, fields


class StoredAclSchema(Schema):
    uuid = fields.UUID()
    token = fields.Integer()


class StoredNodeSchema(Schema):
    token = fields.Integer()
    acl = fields.Dict(keys=fields.UUID(), values=fields.Integer())


class NewTokenRing:
    PATH = "~/.cache/bluetooth-mesh-example"

    @property
    def path(self):
        return os.path.expanduser(self.PATH)

    def __init__(self):
        self.__tokens = {}  # type: Dict[UUID, int]
        self.schema = StoredNodeSchema()

        os.makedirs(self.path, exist_ok=True)
        for filename in os.listdir(self.path):
            with open(os.path.join(self.path, filename), "r") as tokenfile:
                r = tokenfile.read()
                try:
                    self.__tokens[UUID(filename)] = self.schema.loads(r)
                except Exception as e:
                    print(e)

    def __getitem__(self, uuid):
        return self.__tokens.get(uuid, {})

    def __setitem__(self, uuid, token):
        if uuid in self.__tokens:
            self.__tokens[uuid]['token'] = token
        else:
            self.__tokens[uuid] = dict(token=token, acl={})
            self._save(uuid)

    def get_acl(self, uuid):
        if uuid not in self.__tokens:
            return {}
        return self.__tokens[uuid].get("acl", {})

    def set_acl(self, uuid, acl_data):
        self.__tokens[uuid]['acl'] = acl_data
        self._save(uuid)

    def _save(self, uuid):
        with open(os.path.join(self.path, str(uuid)), "w") as tokenfile:
            tokenfile.write(self.schema.dumps(self.__tokens[uuid]))

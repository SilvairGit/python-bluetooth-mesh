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
from json.decoder import JSONDecodeError

from marshmallow import Schema, ValidationError, fields


class StoredNodeSchema(Schema):
    token = fields.Integer()
    acl = fields.Dict(keys=fields.UUID(), values=fields.Integer())
    network = fields.Dict(keys=fields.String(), values=fields.String())


class TokenRing:
    PATH = "~/.cache/bluetooth-mesh"
    LEGACY_PATH = "~/.cache/bluetooth-mesh-example"

    @property
    def path(self):
        return os.path.expanduser(self.PATH)

    def __init__(self, uuid):
        self.uuid = str(uuid)
        self.schema = StoredNodeSchema()
        self.data = {}

        os.makedirs(self.path, exist_ok=True)
        for path in [self.path, os.path.expanduser(self.LEGACY_PATH)]:
            try:
                with open(os.path.join(path, self.uuid), "r") as tokenfile:
                    r = tokenfile.read()
                    try:
                        self.data = self.schema.loads(r)
                        return
                    except (JSONDecodeError, ValidationError, EOFError):
                        self.data = dict(token=int(r, 16), acl={}, network={})

            except FileNotFoundError:
                self.data = dict(token=0, acl={}, network={})

    def _save(self):
        with open(os.path.join(self.path, self.uuid), "w") as tokenfile:
            tokenfile.write(self.schema.dumps(self.data))

    @property
    def token(self):
        return self.data["token"]

    @token.setter
    def token(self, value):
        self.data["token"] = value
        self._save()

    def acl(self, uuid=None, token=None):
        if all((uuid, token)):
            self.data["acl"][uuid] = token
            self._save()
            return

        return self.data["acl"].get(uuid) if uuid else self.data["acl"].items()

    def drop_acl(self, uuid):
        del self.data["acl"][uuid]
        self._save()

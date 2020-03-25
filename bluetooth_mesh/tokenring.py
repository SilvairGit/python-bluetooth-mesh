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


class TokenRing:
    PATH = "~/.cache/bluetooth-mesh-example"

    @property
    def path(self):
        return os.path.expanduser(self.PATH)

    def __init__(self):
        self.__tokens = {}  # type: Dict[UUID, int]

        os.makedirs(self.path, exist_ok=True)
        for filename in os.listdir(self.path):
            with open(os.path.join(self.path, filename), "r") as tokenfile:
                self.__tokens[UUID(filename)] = int(tokenfile.readline() or "0", 16)

    def get(self, uuid) -> int:
        warnings.warn("TokenRing.get is deprecated, use dict-like API")
        return self[uuid]

    def set(self, uuid, token):
        warnings.warn("TokenRing.set is deprecated, use dict-like API")
        self[uuid] = token

    def __getitem__(self, uuid) -> int:
        return self.__tokens.get(uuid, 0)

    def __setitem__(self, uuid, token):
        self.__tokens[uuid] = token

        with open(os.path.join(self.path, str(uuid)), "w") as tokenfile:
            tokenfile.write("%x" % token)

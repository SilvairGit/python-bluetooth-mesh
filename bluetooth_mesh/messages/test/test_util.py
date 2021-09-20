#
# python-bluetooth-mesh - Bluetooth Mesh for Python
#
# Copyright (C) 2021  SILVAIR sp. z o.o.
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
from itertools import chain

import pytest

from bluetooth_mesh.messages import AccessMessage
from bluetooth_mesh.messages.util import camelcase, snakecase

valid = [
    # fmt: off
    pytest.param(opcode.lower())
    for opcode in chain(
        *[opcode_class._member_names_ for opcode_class in AccessMessage.OPCODES]
    )
    # fmt: on
]


@pytest.mark.parametrize("opcode", valid)
def test_opcode_name_same_after_case_conversion(opcode):
    assert opcode == snakecase(camelcase(opcode))

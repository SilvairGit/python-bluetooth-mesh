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
import pytest

from bluetooth_mesh.messages import AccessMessage

valid = [
    # fmt: off
    pytest.param(
        bytes.fromhex("04003601030405"),
        {
            "opcode": 0x04,
            "params": {
                "test_id": 0,
                "company_id": 0x0136,
                "fault_array": [0x03, 0x04, 0x05]
            }
        },
        id="1 byte opcode"
    ),
    pytest.param(
        bytes.fromhex("8032013601"),
        {
            "opcode": 0x8032,
            "params": {
                "test_id": 1,
                "company_id": 0x0136
            }
        },
        id="2 byte opcode"
    ),
    pytest.param(
        bytes.fromhex("c0112233"),
        {
            "opcode": 0xc01122,
            "params": bytes([0x33])
        },
        id="3 byte opcode"
    )
    # fmt: on
]


@pytest.mark.parametrize("encoded,decoded", valid)
def test_build(encoded, decoded):
    result = AccessMessage.build(obj=decoded)
    # print(result)
    assert result == encoded


@pytest.mark.parametrize("encoded,decoded", valid)
def test_parse(encoded, decoded):
    result = AccessMessage.parse(data=encoded)
    # print(result)
    assert result == decoded

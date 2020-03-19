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

from bluetooth_mesh.messages.generic.level import (
    GenericLevelMessage,
    GenericLevelOpcode,
)

valid = [
    # fmt: off
    pytest.param(
        b'\x82\x05',
        GenericLevelOpcode.LEVEL_GET,
        dict(),
        id="LEVEL_GET"
    ),
    pytest.param(
        b'\x82\x06\xff\x7f\x22',
        GenericLevelOpcode.LEVEL_SET,
        dict(
            level=32767,
            tid=34
        ),
        id="LEVEL_SET_max"
    ),
    pytest.param(
        b'\x82\x06\x00\x80\x22',
        GenericLevelOpcode.LEVEL_SET,
        dict(
            level=-32768,
            tid=34
        ),
        id="LEVEL_SET_min"
    ),
    pytest.param(
        b'\x82\x06\x01\x00\x22',
        GenericLevelOpcode.LEVEL_SET,
        dict(
            level=1,
            tid=34,
            transition_time=6.3,
            delay=0.3
        ),
        id="LEVEL_SET_invalid"
    ),
    pytest.param(
        b'\x82\x06\x00\x00\x31\x32\x3c',
        GenericLevelOpcode.LEVEL_SET,
        dict(
            level=0,
            tid=49,
            transition_time=5,
            delay=0.3
        ),
        id="LEVEL_SET_with_optional"
    ),
    pytest.param(
        b'\x82\x07\x00\x00\x31\x32\x3c',
        GenericLevelOpcode.LEVEL_SET_UNACKNOWLEDGED,
        dict(
            level=0,
            tid=49,
            transition_time=5,
            delay=0.3
        ),
        id="LEVEL_SET_UNACKNOWLEDGED"
    ),
    pytest.param(
        b'\x82\x08\xff\x7f',
        GenericLevelOpcode.LEVEL_STATUS,
        dict(
            present_level=32767,
            target_level=None,
            remaining_time=None
        ),
        id="LEVEL_STATUS_max"
    ),
    pytest.param(
        b'\x82\x08\x00\x80',
        GenericLevelOpcode.LEVEL_STATUS,
        dict(
            present_level=-32768,
            target_level=None,
            remaining_time=None
        ),
        id="LEVEL_STATUS_min"
    ),
    pytest.param(
        b'\x82\x08\x00\x00\xff\x00\x4a',
        GenericLevelOpcode.LEVEL_STATUS,
        dict(
            present_level=0,
            target_level=255,
            remaining_time=10
        ),
        id="LEVEL_STATUS_with_optional"
    ),
    pytest.param(
        b'\x82\x08\x00\x00\x01\x00\xff',
        GenericLevelOpcode.LEVEL_STATUS,
        dict(
            present_level=0,
            target_level=1,
            remaining_time=37800
        ),
        id="LEVEL_STATUS_max_time"
    ),
    pytest.param(
        b'\x82\x09\xff\xff\xff\x7f\x22',
        GenericLevelOpcode.DELTA_SET,
        dict(
            delta_level=2147483647,
            tid=34
        ),
        id="DELTA_SET_max"
    ),
    pytest.param(
        b'\x82\x09\x00\x00\x00\x80\x22',
        GenericLevelOpcode.DELTA_SET,
        dict(
            delta_level=-2147483648,
            tid=34
        ),
        id="DELTA_SET_min"
    ),
    pytest.param(
        b'\x82\x09\x01\x00\x00\x00\x22',
        GenericLevelOpcode.DELTA_SET,
        dict(
            delta_level=1,
            tid=34,
            transition_time=6.3,
            delay=0.3
        ),
        id="DELTA_SET_invalid"),
    pytest.param(
        b'\x82\x09\x00\x00\x00\x00\x31\x32\x3c',
        GenericLevelOpcode.DELTA_SET,
        dict(
            delta_level=0,
            tid=49,
            transition_time=5,
            delay=0.3
        ),
        id="DELTA_SET_with_optional"),
    pytest.param(
        b'\x82\x0a\x00\x00\x00\x00\x31\x32\x3c',
        GenericLevelOpcode.DELTA_SET_UNACKNOWLEDGED,
        dict(
            delta_level=0,
            tid=49,
            transition_time=5,
            delay=0.3
        ),
        id="DELTA_SET_UNACKNOWLEDGED"),
    pytest.param(
        b'\x82\x0b\xff\x7f\x22',
        GenericLevelOpcode.MOVE_SET,
        dict(
            delta_level=32767,
            tid=34
        ),
        id="MOVE_SET_max"
    ),
    pytest.param(
        b'\x82\x0b\x00\x80\x22',
        GenericLevelOpcode.MOVE_SET,
        dict(
            delta_level=-32768,
            tid=34
        ),
        id="MOVE_SET_min"
    ),
    pytest.param(
        b'\x82\x0b\x01\x00\x22',
        GenericLevelOpcode.MOVE_SET,
        dict(
            delta_level=1,
            tid=34,
            transition_time=6.3,
            delay=0.3
        ),
        id="MOVE_SET_invalid"
    ),
    pytest.param(
        b'\x82\x0b\x00\x00\x31\x32\x3c',
        GenericLevelOpcode.MOVE_SET,
        dict(
            delta_level=0,
            tid=49,
            transition_time=5,
            delay=0.3
        ),
        id="MOVE_SET_with_optional"
    ),
    pytest.param(
        b'\x82\x0c\x00\x00\x31\x32\x3c',
        GenericLevelOpcode.MOVE_SET_UNACKNOWLEDGED,
        dict(
            delta_level=0,
            tid=49,
            transition_time=5,
            delay=0.3
        ),
        id="MOVE_SET_UNACKNOWLEDGED"
    ),
    # fmt: on
]


@pytest.mark.parametrize("encoded,opcode,data", valid)
def test_parse_valid(encoded, opcode, data):
    assert GenericLevelMessage.parse(encoded).params == data


@pytest.mark.parametrize("encoded,opcode,data", valid)
def test_build_valid(encoded, opcode, data):
    assert GenericLevelMessage.build(dict(opcode=opcode, params=data)) == encoded

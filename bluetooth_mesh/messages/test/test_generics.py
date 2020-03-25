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
from construct import ValidationError

from bluetooth_mesh.messages.generic.onoff import *
from bluetooth_mesh.messages.generics import *


@pytest.mark.parametrize(
    # fmt: off
    "steps, resolution, expected_tt",
    [
        (0x00, 0b00, "00"),
        (0x01, 0b00, "01"),
        (0x01, 0b01, "41"),
        (0x3E, 0b00, "3E"),
        (0x3E, 0b11, "FE"),
        (0x3F, 0b11, "FF")
    ]
    # fmt: on
)
def test_build_transition_time(steps, resolution, expected_tt):
    tt = TransitionTime.build(dict(steps=steps, resolution=resolution))
    assert tt == bytes.fromhex(expected_tt)


@pytest.mark.parametrize(
    # fmt: off
    "raw_bytes, expected_steps, expected_resolution",
    [
        ("00", 0x00, 0b00),
        ("01", 0x01, 0b00),
        ("40", 0x00, 0b01),
        ("3E", 0x3E, 0b00),
        ("FE", 0x3E, 0b11),
        ("FF", 0x3F, 0b11)
    ]
    # fmt: on
)
def test_parse_transition_time(raw_bytes, expected_steps, expected_resolution):
    tt = TransitionTime.parse(bytes.fromhex(raw_bytes))
    assert tt.steps == expected_steps
    assert tt.resolution == expected_resolution


valid = [
    # fmt: off
    pytest.param(
        b'\x82\x01',
        GenericOnOffOpcode.ONOFF_GET,
        dict(),
        id="ONOFF_GET"),
    pytest.param(
        b'\x82\x02\x01\x22',
        GenericOnOffOpcode.ONOFF_SET,
        dict(
            onoff=1,
            tid=34
        ),
        id="ONOFF_SET"),
    pytest.param(
        b'\x82\x02\x01\x22',
        GenericOnOffOpcode.ONOFF_SET,
        dict(
            onoff=1,
            tid=34,
            transition_time=6.3,
            delay=0.3
        ),
        id="ONOFF_SET_invalid"),
    pytest.param(
        b'\x82\x02\x00\x31\x32\x3c',
        GenericOnOffOpcode.ONOFF_SET,
        dict(
            onoff=0,
            tid=49,
            transition_time=5,
            delay=0.3
        ),
        id="ONOFF_SET_with_optional"),
    pytest.param(
        b'\x82\x02\x00\x31\xf2\x3c',
        GenericOnOffOpcode.ONOFF_SET,
        dict(
            onoff=0,
            tid=49,
            transition_time=30000,
            delay=0.3
        ),
        id="ONOFF_SET_large_transition_time"),
    pytest.param(
        b'\x82\x04\x00',
        GenericOnOffOpcode.ONOFF_STATUS,
        dict(
            present_onoff=0,
            target_onoff=None,
            remaining_time=None
        ),
        id="ONOFF_STATUS"
    ),
    pytest.param(
        b'\x82\x04\x00\x01\x4a',
        GenericOnOffOpcode.ONOFF_STATUS,
        dict(
            present_onoff=0,
            target_onoff=1,
            remaining_time=10
        ),
        id="ONOFF_STATUS_with_optional"
    ),
    pytest.param(
        b'\x82\x04\x00\x01\xff',
        GenericOnOffOpcode.ONOFF_STATUS,
        dict(
            present_onoff=0,
            target_onoff=1,
            remaining_time=37800
        ),
        id="ONOFF_STATUS_max_time"
    ),
    # fmt: on
]


@pytest.mark.parametrize("encoded,opcode,data", valid)
def test_parse_valid(encoded, opcode, data):
    assert GenericOnOffMessage.parse(encoded).params == data


@pytest.mark.parametrize("encoded,opcode,data", valid)
def test_build_valid(encoded, opcode, data):
    assert GenericOnOffMessage.build(dict(opcode=opcode, params=data)) == encoded

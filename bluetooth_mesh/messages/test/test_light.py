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

from bluetooth_mesh.messages.config import StatusCode
from bluetooth_mesh.messages.generic.light import (
    LightCTLMessage,
    LightCTLOpcode,
    LightCTLSetupMessage,
    LightCTLSetupOpcode,
    LightLightnessMessage,
    LightLightnessOpcode,
    LightLightnessSetupMessage,
    LightLightnessSetupOpcode,
)

valid_lightness = [
    # fmt: off
    pytest.param(
        b'\x82\x4b',
        LightLightnessOpcode.LIGHTNESS_GET,
        dict(),
        id="LIGHTNESS_GET"),
    pytest.param(
        b'\x82\x4c\xbb\xaa\x22',
        LightLightnessOpcode.LIGHTNESS_SET,
        dict(lightness=0xaabb,
             tid=34),
        id="LIGHTNESS_SET"),
    pytest.param(
        b'\x82\x4c\x01\x00\x22',
        LightLightnessOpcode.LIGHTNESS_SET,
        dict(lightness=1,
             tid=34,
             transition_time=6.3,
             delay=0.3),
        id="LIGHTNESS_SET_invalid"),
    pytest.param(
        b'\x82\x4c\x00\x00\x31\x32\x3c',
        LightLightnessOpcode.LIGHTNESS_SET,
        dict(lightness=0,
             tid=49,
             transition_time=5,
             delay=0.3),
        id="LIGHTNESS_SET_with_optional"),
    pytest.param(
        b'\x82\x4d\x00\x00\x31\x32\x3c',
        LightLightnessOpcode.LIGHTNESS_SET_UNACKNOWLEDGED,
        dict(lightness=0,
             tid=49,
             transition_time=5,
             delay=0.3),
        id="LIGHTNESS_SET_UNACKNOWLEDGED"),
    pytest.param(
        b'\x82\x4e\x44\x00',
        LightLightnessOpcode.LIGHTNESS_STATUS,
        dict(present_lightness=0x44),
        id="LIGHTNESS_STATUS"),
    pytest.param(
        b'\x82\x4e\x00\x00\x31\xc8\x0f',
        LightLightnessOpcode.LIGHTNESS_STATUS,
        dict(present_lightness=0,
             target_lightness=0xc831,
             remaining_time=1.5),
        id="LIGHTNESS_STATUS_with_optional"),

    pytest.param(
        b'\x82\x4f',
        LightLightnessOpcode.LIGHTNESS_LINEAR_GET,
        dict(),
        id="LIGHTNESS_LINEAR_GET"),
    pytest.param(
        b'\x82\x50\xbb\xaa\x01',
        LightLightnessOpcode.LIGHTNESS_LINEAR_SET,
        dict(lightness=0xaabb,
             tid=1),
        id="LIGHTNESS_LINEAR_SET"),
    pytest.param(
        b'\x82\x50\x01\x00\x22',
        LightLightnessOpcode.LIGHTNESS_LINEAR_SET,
        dict(lightness=1,
             tid=34,
             transition_time=6.3,
             delay=0.3),
        id="LIGHTNESS_LINEAR_SET_invalid"),
    pytest.param(
        b'\x82\x50\x00\x00\x31\x32\x1a',
        LightLightnessOpcode.LIGHTNESS_LINEAR_SET,
        dict(lightness=0,
             tid=49,
             transition_time=5,
             delay=0.13),
        id="LIGHTNESS_LINEAR_SET_with_optional"),
    pytest.param(
        b'\x82\x51\xff\x00\x31\x32\x3c',
        LightLightnessOpcode.LIGHTNESS_LINEAR_SET_UNACKNOWLEDGED,
        dict(lightness=0xff,
             tid=49,
             transition_time=5,
             delay=0.3),
        id="LIGHTNESS_LINEAR_SET_UNACKNOWLEDGED"),
    pytest.param(
        b'\x82\x52\x00\x00\xdd\xbb\x4c',
        LightLightnessOpcode.LIGHTNESS_LINEAR_STATUS,
        dict(present_lightness=0,
             target_lightness=0xbbdd,
             remaining_time=12),
        id="LIGHTNESS_LINEAR_STATUS"),

    pytest.param(
        b'\x82\x53',
        LightLightnessOpcode.LIGHTNESS_LAST_GET,
        dict(),
        id="LIGHTNESS_LAST_GET"),
    pytest.param(
        b'\x82\x54\x00\x00',
        LightLightnessOpcode.LIGHTNESS_LAST_STATUS,
        dict(lightness=0),
        id="LIGHTNESS_LAST_STATUS"),

    pytest.param(
        b'\x82\x55',
        LightLightnessOpcode.LIGHTNESS_DEFAULT_GET,
        dict(),
        id="LIGHTNESS_DEFAULT_GET"),
    pytest.param(
        b'\x82\x56\x00\x00',
        LightLightnessOpcode.LIGHTNESS_DEFAULT_STATUS,
        dict(lightness=0),
        id="LIGHTNESS_STATUS"),

    pytest.param(
        b'\x82\x57',
        LightLightnessOpcode.LIGHTNESS_RANGE_GET,
        dict(),
        id="LIGHTNESS_RANGE_GET"),
    pytest.param(
        b'\x82\x58\x00\x11\x11\x88\x88',
        LightLightnessOpcode.LIGHTNESS_RANGE_STATUS,
        dict(status=StatusCode.SUCCESS,
             range_min=0x1111,
             range_max=0x8888),
        id="LIGHTNESS_RANGE_STATUS"),
    # fmt: on
]

valid_lightness_setup = [
    # fmt: off
    pytest.param(
        b'\x82\x59\xbb\xaa',
        LightLightnessSetupOpcode.LIGHTNESS_DEFAULT_SET,
        dict(lightness=0xaabb),
        id="LIGHTNESS_DEFAULT_SET"),
    pytest.param(
        b'\x82\x59\x01\x00',
        LightLightnessSetupOpcode.LIGHTNESS_DEFAULT_SET,
        dict(lightness=1,
             tid=34,
             transition_time=6.3,
             delay=0.3),
        id="LIGHTNESS_DEFAULT_SET_invalid"),
    pytest.param(
        b'\x82\x5a\x00\x00',
        LightLightnessSetupOpcode.LIGHTNESS_DEFAULT_SET_UNACKNOWLEDGED,
        dict(lightness=0),
        id="LIGHTNESS_SET_UNACKNOWLEDGED"),

    pytest.param(
        b'\x82\x5b\x11\x00\xff\xee',
        LightLightnessSetupOpcode.LIGHTNESS_RANGE_SET,
        dict(range_min=0x0011,
             range_max=0xeeff),
        id="LIGHTNESS_RANGE_SET"),
    pytest.param(
        b'\x82\x5c\xcd\xab\x34\x12',
        LightLightnessSetupOpcode.LIGHTNESS_RANGE_SET_UNACKNOWLEDGED,
        dict(range_min=0xabcd,
             range_max=0x1234),
        id="LIGHTNESS_RANGE_SET_UNACKNOWLEDGED"),
    # fmt: on
]


valid_ctl = [
    # fmt: off
    pytest.param(
        b'\x82\x5d',
        LightCTLOpcode.CTL_GET,
        dict(),
        id="CTL_GET"),
    pytest.param(
        b'\x82\x5e\xbb\xaa\xdd\xcc\xff\xee\x01',
        LightCTLOpcode.CTL_SET,
        dict(ctl_lightness=0xaabb,
             ctl_temperature=0xccdd,
             ctl_delta_uv=0xeeff,
             tid=1),
        id="CTL_SET"),
    pytest.param(
        b'\x82\x5e\xbb\xaa\xdd\xcc\xff\xee\x22',
        LightCTLOpcode.CTL_SET,
        dict(ctl_lightness=0xaabb,
             ctl_temperature=0xccdd,
             ctl_delta_uv=0xeeff,
             tid=34,
             transition_time=6.3,
             delay=0.3),
        id="CTL_SET_invalid"),
    pytest.param(
        b'\x82\x5e\xbb\xaa\xdd\xcc\xff\xee\x22\x32\x3c',
        LightCTLOpcode.CTL_SET,
        dict(ctl_lightness=0xaabb,
             ctl_temperature=0xccdd,
             ctl_delta_uv=0xeeff,
             tid=34,
             transition_time=5,
             delay=0.3),
        id="CTL_SET_with_optional"),
    pytest.param(
        b'\x82\x5f\x11\x11\x22\x22\x33\x33\x22\x32\x3c',
        LightCTLOpcode.CTL_SET_UNACKNOWLEDGED,
        dict(ctl_lightness=0x1111,
             ctl_temperature=0x2222,
             ctl_delta_uv=0x3333,
             tid=34,
             transition_time=5,
             delay=0.3),
        id="CTL_SET_UNACKNOWLEDGED"),
    pytest.param(
        b'\x82\x60\x11\x11\x22\x22',
        LightCTLOpcode.CTL_STATUS,
        dict(present_ctl_lightness=0x1111,
             present_ctl_temperature=0x2222),
        id="CTL_STATUS"),
    pytest.param(
        b'\x82\x60\x11\x11\x22\x22\x33\x33\x44\x44\x0f',
        LightCTLOpcode.CTL_STATUS,
        dict(present_ctl_lightness=0x1111,
             present_ctl_temperature=0x2222,
             target_ctl_lightness=0x3333,
             target_ctl_temperature=0x4444,
             remaining_time=1.5),
        id="CTL_STATUS_with_optional"),

    pytest.param(
        b'\x82\x61',
        LightCTLOpcode.CTL_TEMPERATURE_GET,
        dict(),
        id="CTL_TEMPERATURE_GET"),
    pytest.param(
        b'\x82\x64\xdd\xcc\xff\xee\x0a',
        LightCTLOpcode.CTL_TEMPERATURE_SET,
        dict(ctl_temperature=0xccdd,
             ctl_delta_uv=0xeeff,
             tid=10),
        id="CTL_TEMPERATURE_SET"),
    pytest.param(
        b'\x82\x64\xdd\xcc\xff\xee\x22\x32\x14',
        LightCTLOpcode.CTL_TEMPERATURE_SET,
        dict(ctl_temperature=0xccdd,
             ctl_delta_uv=0xeeff,
             tid=34,
             transition_time=5,
             delay=0.1),
        id="CTL_TEMPERATURE_SET_with_optional"),
    pytest.param(
        b'\x82\x65\x22\x22\x33\x33\xff\x32\x3c',
        LightCTLOpcode.CTL_TEMPERATURE_SET_UNACKNOWLEDGED,
        dict(ctl_temperature=0x2222,
             ctl_delta_uv=0x3333,
             tid=0xff,
             transition_time=5,
             delay=0.3),
        id="CTL_TEMPERATURE_SET_UNACKNOWLEDGED"),
    pytest.param(
        b'\x82\x66\x22\x22\xff\xff',
        LightCTLOpcode.CTL_TEMPERATURE_STATUS,
        dict(present_ctl_temperature=0x2222,
             present_ctl_delta_uv=0xffff),
        id="CTL_TEMPERATURE_STATUS"),
    pytest.param(
        b'\x82\x66\x11\x11\x22\x22\x33\x33\x44\x44\x0f',
        LightCTLOpcode.CTL_TEMPERATURE_STATUS,
        dict(present_ctl_temperature=0x1111,
             present_ctl_delta_uv=0x2222,
             target_ctl_temperature=0x3333,
             target_ctl_delta_uv=0x4444,
             remaining_time=1.5),
        id="CTL_TEMPERATURE_STATUS_with_optional"),

    pytest.param(
        b'\x82\x62',
        LightCTLOpcode.CTL_TEMPERATURE_RANGE_GET,
        dict(),
        id="CTL_TEMPERATURE_RANGE_GET"),
    pytest.param(
        b'\x82\x63\x00\xdd\xcc\xff\xee',
        LightCTLOpcode.CTL_TEMPERATURE_RANGE_STATUS,
        dict(status=StatusCode.SUCCESS,
             range_min=0xccdd,
             range_max=0xeeff),
        id="CTL_TEMPERATURE_RANGE_STATUS"),

    pytest.param(
        b'\x82\x67',
        LightCTLOpcode.CTL_TEMPERATURE_DEFAULT_GET,
        dict(),
        id="CTL_TEMPERATURE_DEFAULT_GET"),
    pytest.param(
        b'\x82\x68\xdd\xcc\xff\xee\x11\x11',
        LightCTLOpcode.CTL_TEMPERATURE_DEFAULT_STATUS,
        dict(ctl_lightness=0xccdd,
             ctl_temperature=0xeeff,
             ctl_delta_uv=0x1111),
        id="CTL_TEMPERATURE_DEFAULT_STATUS"),
    # fmt: on
]

valid_ctl_setup = [
    # fmt: off
    pytest.param(
        b'\x82\x69\xdd\xcc\xff\xee\x11\x11',
        LightCTLSetupOpcode.CTL_TEMPERATURE_DEFAULT_SET,
        dict(ctl_lightness=0xccdd,
             ctl_temperature=0xeeff,
             ctl_delta_uv=0x1111),
        id="CTL_TEMPERATURE_DEFAULT_SET"),
    pytest.param(
        b'\x82\x6a\xdd\xcc\xff\xee\x11\x11',
        LightCTLSetupOpcode.CTL_TEMPERATURE_DEFAULT_SET_UNACKNOWLEDGED,
        dict(ctl_lightness=0xccdd,
             ctl_temperature=0xeeff,
             ctl_delta_uv=0x1111),
        id="CTL_TEMPERATURE_DEFAULT_SET_UNACKNOWLEDGED"),

    pytest.param(
        b'\x82\x6b\xdd\xcc\xff\xee',
        LightCTLSetupOpcode.CTL_TEMPERATURE_RANGE_SET,
        dict(range_min=0xccdd,
             range_max=0xeeff),
        id="CTL_TEMPERATURE_RANGE_SET"),
    pytest.param(
        b'\x82\x6c\x11\x11\x22\x22',
        LightCTLSetupOpcode.CTL_TEMPERATURE_RANGE_SET_UNACKNOWLEDGED,
        dict(range_min=0x1111,
             range_max=0x2222),
        id="CTL_TEMPERATURE_RANGE_SET_UNACKNOWLEDGED"),
    # fmt: on
]


@pytest.mark.parametrize("encoded,opcode,data", valid_lightness)
def test_parse_valid_lightness(encoded, opcode, data):
    assert LightLightnessMessage.parse(encoded).params == data


@pytest.mark.parametrize("encoded,opcode,data", valid_lightness)
def test_build_valid_lightness(encoded, opcode, data):
    assert LightLightnessMessage.build(dict(opcode=opcode, params=data)) == encoded


@pytest.mark.parametrize("encoded,opcode,data", valid_lightness_setup)
def test_parse_valid_lightness_setup(encoded, opcode, data):
    assert LightLightnessSetupMessage.parse(encoded).params == data


@pytest.mark.parametrize("encoded,opcode,data", valid_lightness_setup)
def test_build_valid_lightness_setup(encoded, opcode, data):
    assert LightLightnessSetupMessage.build(dict(opcode=opcode, params=data)) == encoded


@pytest.mark.parametrize("encoded,opcode,data", valid_ctl)
def test_parse_valid_ctl(encoded, opcode, data):
    assert LightCTLMessage.parse(encoded).params == data


@pytest.mark.parametrize("encoded,opcode,data", valid_ctl)
def test_build_valid_ctl(encoded, opcode, data):
    assert LightCTLMessage.build(dict(opcode=opcode, params=data)) == encoded


@pytest.mark.parametrize("encoded,opcode,data", valid_ctl_setup)
def test_parse_valid_ctl_setup(encoded, opcode, data):
    assert LightCTLSetupMessage.parse(encoded).params == data


@pytest.mark.parametrize("encoded,opcode,data", valid_ctl_setup)
def test_build_valid_ctl_setup(encoded, opcode, data):
    assert LightCTLSetupMessage.build(dict(opcode=opcode, params=data)) == encoded

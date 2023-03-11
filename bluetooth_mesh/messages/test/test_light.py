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
    LightHSLMessage,
    LightHSLOpcode,
    LightHSLSetupMessage,
    LightHSLSetupOpcode,
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
        LightLightnessOpcode.LIGHT_LIGHTNESS_GET,
        dict(),
        id="LIGHTNESS_GET"),
    pytest.param(
        b'\x82\x4c\xbb\xaa\x22',
        LightLightnessOpcode.LIGHT_LIGHTNESS_SET,
        dict(lightness=0xaabb,
             tid=34),
        id="LIGHTNESS_SET"),
    pytest.param(
        b'\x82\x4c\x01\x00\x22',
        LightLightnessOpcode.LIGHT_LIGHTNESS_SET,
        dict(lightness=1,
             tid=34,
             transition_time=6.3,
             delay=0.3),
        id="LIGHTNESS_SET_invalid"),
    pytest.param(
        b'\x82\x4c\x00\x00\x31\x32\x3c',
        LightLightnessOpcode.LIGHT_LIGHTNESS_SET,
        dict(lightness=0,
             tid=49,
             transition_time=5,
             delay=0.3),
        id="LIGHTNESS_SET_with_optional"),
    pytest.param(
        b'\x82\x4d\x00\x00\x31\x32\x3c',
        LightLightnessOpcode.LIGHT_LIGHTNESS_SET_UNACKNOWLEDGED,
        dict(lightness=0,
             tid=49,
             transition_time=5,
             delay=0.3),
        id="LIGHTNESS_SET_UNACKNOWLEDGED"),
    pytest.param(
        b'\x82\x4e\x44\x00',
        LightLightnessOpcode.LIGHT_LIGHTNESS_STATUS,
        dict(present_lightness=0x44),
        id="LIGHTNESS_STATUS"),
    pytest.param(
        b'\x82\x4e\x00\x00\x31\xc8\x0f',
        LightLightnessOpcode.LIGHT_LIGHTNESS_STATUS,
        dict(present_lightness=0,
             target_lightness=0xc831,
             remaining_time=1.5),
        id="LIGHTNESS_STATUS_with_optional"),

    pytest.param(
        b'\x82\x4f',
        LightLightnessOpcode.LIGHT_LIGHTNESS_LINEAR_GET,
        dict(),
        id="LIGHTNESS_LINEAR_GET"),
    pytest.param(
        b'\x82\x50\xbb\xaa\x01',
        LightLightnessOpcode.LIGHT_LIGHTNESS_LINEAR_SET,
        dict(lightness=0xaabb,
             tid=1),
        id="LIGHTNESS_LINEAR_SET"),
    pytest.param(
        b'\x82\x50\x01\x00\x22',
        LightLightnessOpcode.LIGHT_LIGHTNESS_LINEAR_SET,
        dict(lightness=1,
             tid=34,
             transition_time=6.3,
             delay=0.3),
        id="LIGHTNESS_LINEAR_SET_invalid"),
    pytest.param(
        b'\x82\x50\x00\x00\x31\x32\x1a',
        LightLightnessOpcode.LIGHT_LIGHTNESS_LINEAR_SET,
        dict(lightness=0,
             tid=49,
             transition_time=5,
             delay=0.13),
        id="LIGHTNESS_LINEAR_SET_with_optional"),
    pytest.param(
        b'\x82\x51\xff\x00\x31\x32\x3c',
        LightLightnessOpcode.LIGHT_LIGHTNESS_LINEAR_SET_UNACKNOWLEDGED,
        dict(lightness=0xff,
             tid=49,
             transition_time=5,
             delay=0.3),
        id="LIGHTNESS_LINEAR_SET_UNACKNOWLEDGED"),
    pytest.param(
        b'\x82\x52\x00\x00\xdd\xbb\x4c',
        LightLightnessOpcode.LIGHT_LIGHTNESS_LINEAR_STATUS,
        dict(present_lightness=0,
             target_lightness=0xbbdd,
             remaining_time=12),
        id="LIGHTNESS_LINEAR_STATUS"),

    pytest.param(
        b'\x82\x53',
        LightLightnessOpcode.LIGHT_LIGHTNESS_LAST_GET,
        dict(),
        id="LIGHTNESS_LAST_GET"),
    pytest.param(
        b'\x82\x54\x00\x00',
        LightLightnessOpcode.LIGHT_LIGHTNESS_LAST_STATUS,
        dict(lightness=0),
        id="LIGHTNESS_LAST_STATUS"),

    pytest.param(
        b'\x82\x55',
        LightLightnessOpcode.LIGHT_LIGHTNESS_DEFAULT_GET,
        dict(),
        id="LIGHTNESS_DEFAULT_GET"),
    pytest.param(
        b'\x82\x56\x00\x00',
        LightLightnessOpcode.LIGHT_LIGHTNESS_DEFAULT_STATUS,
        dict(lightness=0),
        id="LIGHTNESS_STATUS"),

    pytest.param(
        b'\x82\x57',
        LightLightnessOpcode.LIGHT_LIGHTNESS_RANGE_GET,
        dict(),
        id="LIGHTNESS_RANGE_GET"),
    pytest.param(
        b'\x82\x58\x00\x11\x11\x88\x88',
        LightLightnessOpcode.LIGHT_LIGHTNESS_RANGE_STATUS,
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
        LightLightnessSetupOpcode.LIGHT_LIGHTNESS_SETUP_DEFAULT_SET,
        dict(lightness=0xaabb),
        id="LIGHTNESS_DEFAULT_SET"),
    pytest.param(
        b'\x82\x59\x01\x00',
        LightLightnessSetupOpcode.LIGHT_LIGHTNESS_SETUP_DEFAULT_SET,
        dict(lightness=1,
             tid=34,
             transition_time=6.3,
             delay=0.3),
        id="LIGHTNESS_DEFAULT_SET_invalid"),
    pytest.param(
        b'\x82\x5a\x00\x00',
        LightLightnessSetupOpcode.LIGHT_LIGHTNESS_SETUP_DEFAULT_SET_UNACKNOWLEDGED,
        dict(lightness=0),
        id="LIGHTNESS_SET_UNACKNOWLEDGED"),

    pytest.param(
        b'\x82\x5b\x11\x00\xff\xee',
        LightLightnessSetupOpcode.LIGHT_LIGHTNESS_SETUP_RANGE_SET,
        dict(range_min=0x0011,
             range_max=0xeeff),
        id="LIGHTNESS_RANGE_SET"),
    pytest.param(
        b'\x82\x5c\xcd\xab\x34\x12',
        LightLightnessSetupOpcode.LIGHT_LIGHTNESS_SETUP_RANGE_SET_UNACKNOWLEDGED,
        dict(range_min=0xabcd,
             range_max=0x1234),
        id="LIGHTNESS_RANGE_SET_UNACKNOWLEDGED"),
    # fmt: on
]


valid_ctl = [
    # fmt: off
    pytest.param(
        b'\x82\x5d',
        LightCTLOpcode.LIGHT_CTL_GET,
        dict(),
        id="CTL_GET"),
    pytest.param(
        b'\x82\x5e\xbb\xaa\xdd\xcc\xff\xee\x01',
        LightCTLOpcode.LIGHT_CTL_SET,
        dict(ctl_lightness=0xaabb,
             ctl_temperature=0xccdd,
             ctl_delta_uv=0xeeff,
             tid=1),
        id="CTL_SET"),
    pytest.param(
        b'\x82\x5e\xbb\xaa\xdd\xcc\xff\xee\x22',
        LightCTLOpcode.LIGHT_CTL_SET,
        dict(ctl_lightness=0xaabb,
             ctl_temperature=0xccdd,
             ctl_delta_uv=0xeeff,
             tid=34,
             transition_time=6.3,
             delay=0.3),
        id="CTL_SET_invalid"),
    pytest.param(
        b'\x82\x5e\xbb\xaa\xdd\xcc\xff\xee\x22\x32\x3c',
        LightCTLOpcode.LIGHT_CTL_SET,
        dict(ctl_lightness=0xaabb,
             ctl_temperature=0xccdd,
             ctl_delta_uv=0xeeff,
             tid=34,
             transition_time=5,
             delay=0.3),
        id="CTL_SET_with_optional"),
    pytest.param(
        b'\x82\x5f\x11\x11\x22\x22\x33\x33\x22\x32\x3c',
        LightCTLOpcode.LIGHT_CTL_SET_UNACKNOWLEDGED,
        dict(ctl_lightness=0x1111,
             ctl_temperature=0x2222,
             ctl_delta_uv=0x3333,
             tid=34,
             transition_time=5,
             delay=0.3),
        id="CTL_SET_UNACKNOWLEDGED"),
    pytest.param(
        b'\x82\x60\x11\x11\x22\x22',
        LightCTLOpcode.LIGHT_CTL_STATUS,
        dict(present_ctl_lightness=0x1111,
             present_ctl_temperature=0x2222),
        id="CTL_STATUS"),
    pytest.param(
        b'\x82\x60\x11\x11\x22\x22\x33\x33\x44\x44\x0f',
        LightCTLOpcode.LIGHT_CTL_STATUS,
        dict(present_ctl_lightness=0x1111,
             present_ctl_temperature=0x2222,
             target_ctl_lightness=0x3333,
             target_ctl_temperature=0x4444,
             remaining_time=1.5),
        id="CTL_STATUS_with_optional"),

    pytest.param(
        b'\x82\x61',
        LightCTLOpcode.LIGHT_CTL_TEMPERATURE_GET,
        dict(),
        id="CTL_TEMPERATURE_GET"),
    pytest.param(
        b'\x82\x64\xdd\xcc\xff\xee\x0a',
        LightCTLOpcode.LIGHT_CTL_TEMPERATURE_SET,
        dict(ctl_temperature=0xccdd,
             ctl_delta_uv=0xeeff,
             tid=10),
        id="CTL_TEMPERATURE_SET"),
    pytest.param(
        b'\x82\x64\xdd\xcc\xff\xee\x22\x32\x14',
        LightCTLOpcode.LIGHT_CTL_TEMPERATURE_SET,
        dict(ctl_temperature=0xccdd,
             ctl_delta_uv=0xeeff,
             tid=34,
             transition_time=5,
             delay=0.1),
        id="CTL_TEMPERATURE_SET_with_optional"),
    pytest.param(
        b'\x82\x65\x22\x22\x33\x33\xff\x32\x3c',
        LightCTLOpcode.LIGHT_CTL_TEMPERATURE_SET_UNACKNOWLEDGED,
        dict(ctl_temperature=0x2222,
             ctl_delta_uv=0x3333,
             tid=0xff,
             transition_time=5,
             delay=0.3),
        id="CTL_TEMPERATURE_SET_UNACKNOWLEDGED"),
    pytest.param(
        b'\x82\x66\x22\x22\xff\xff',
        LightCTLOpcode.LIGHT_CTL_TEMPERATURE_STATUS,
        dict(present_ctl_temperature=0x2222,
             present_ctl_delta_uv=0xffff),
        id="CTL_TEMPERATURE_STATUS"),
    pytest.param(
        b'\x82\x66\x11\x11\x22\x22\x33\x33\x44\x44\x0f',
        LightCTLOpcode.LIGHT_CTL_TEMPERATURE_STATUS,
        dict(present_ctl_temperature=0x1111,
             present_ctl_delta_uv=0x2222,
             target_ctl_temperature=0x3333,
             target_ctl_delta_uv=0x4444,
             remaining_time=1.5),
        id="CTL_TEMPERATURE_STATUS_with_optional"),

    pytest.param(
        b'\x82\x62',
        LightCTLOpcode.LIGHT_CTL_TEMPERATURE_RANGE_GET,
        dict(),
        id="CTL_TEMPERATURE_RANGE_GET"),
    pytest.param(
        b'\x82\x63\x00\xdd\xcc\xff\xee',
        LightCTLOpcode.LIGHT_CTL_TEMPERATURE_RANGE_STATUS,
        dict(status=StatusCode.SUCCESS,
             range_min=0xccdd,
             range_max=0xeeff),
        id="CTL_TEMPERATURE_RANGE_STATUS"),

    pytest.param(
        b'\x82\x67',
        LightCTLOpcode.LIGHT_CTL_TEMPERATURE_DEFAULT_GET,
        dict(),
        id="CTL_TEMPERATURE_DEFAULT_GET"),
    pytest.param(
        b'\x82\x68\xdd\xcc\xff\xee\x11\x11',
        LightCTLOpcode.LIGHT_CTL_TEMPERATURE_DEFAULT_STATUS,
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
        LightCTLSetupOpcode.LIGHT_CTL_SETUP_TEMPERATURE_DEFAULT_SET,
        dict(ctl_lightness=0xccdd,
             ctl_temperature=0xeeff,
             ctl_delta_uv=0x1111),
        id="CTL_TEMPERATURE_DEFAULT_SET"),
    pytest.param(
        b'\x82\x6a\xdd\xcc\xff\xee\x11\x11',
        LightCTLSetupOpcode.LIGHT_CTL_SETUP_TEMPERATURE_DEFAULT_SET_UNACKNOWLEDGED,
        dict(ctl_lightness=0xccdd,
             ctl_temperature=0xeeff,
             ctl_delta_uv=0x1111),
        id="CTL_TEMPERATURE_DEFAULT_SET_UNACKNOWLEDGED"),

    pytest.param(
        b'\x82\x6b\xdd\xcc\xff\xee',
        LightCTLSetupOpcode.LIGHT_CTL_SETUP_TEMPERATURE_RANGE_SET,
        dict(range_min=0xccdd,
             range_max=0xeeff),
        id="CTL_TEMPERATURE_RANGE_SET"),
    pytest.param(
        b'\x82\x6c\x11\x11\x22\x22',
        LightCTLSetupOpcode.LIGHT_CTL_SETUP_TEMPERATURE_RANGE_SET_UNACKNOWLEDGED,
        dict(range_min=0x1111,
             range_max=0x2222),
        id="CTL_TEMPERATURE_RANGE_SET_UNACKNOWLEDGED"),
    # fmt: on
]


valid_hsl = [
    # fmt: off
    pytest.param(
        b'\x82\x6d',
        LightHSLOpcode.LIGHT_HSL_GET,
        dict(),
        id="HSL_GET"),
    pytest.param(
        b'\x82\x76\xbb\xaa\xdd\xcc\xff\xee\x10',
        LightHSLOpcode.LIGHT_HSL_SET,
        dict(hsl_lightness=0xaabb,
             hsl_hue=0xccdd,
             hsl_saturation=0xeeff,
             tid=16),
        id="HSL_SET"),
    pytest.param(
        b'\x82\x76\xbb\xaa\xdd\xcc\xff\xee\x10\x32\x64',
        LightHSLOpcode.LIGHT_HSL_SET,
        dict(hsl_lightness=0xaabb,
             hsl_hue=0xccdd,
             hsl_saturation=0xeeff,
             tid=16,
             transition_time=5,
             delay=0.5),
        id="HSL_SET_with_optional"),
    pytest.param(
        b'\x82\x77\x34\x12\x67\x45\xbc\x9a\x11\x37\x6e',
        LightHSLOpcode.LIGHT_HSL_SET_UNACKNOWLEDGED,
        dict(hsl_lightness=0x1234,
             hsl_hue=0x4567,
             hsl_saturation=0x9abc,
             tid=17,
             transition_time=5.5,
             delay=0.55),
        id="HSL_SET_UNACKNOWLEDGED"),
    pytest.param(
        b'\x82\x78\x11\x00\x33\x22\x55\x44',
        LightHSLOpcode.LIGHT_HSL_STATUS,
        dict(hsl_lightness=0x0011,
             hsl_hue=0x2233,
             hsl_saturation=0x4455),
        id="HSL_STATUS"),
    pytest.param(
        b'\x82\x78\x11\x00\x33\x22\x55\x44\x47',
        LightHSLOpcode.LIGHT_HSL_STATUS,
        dict(hsl_lightness=0x0011,
             hsl_hue=0x2233,
             hsl_saturation=0x4455,
             remaining_time=7),
        id="HSL_STATUS_with_optional"),
    pytest.param(
        b'\x82\x79',
        LightHSLOpcode.LIGHT_HSL_TARGET_GET,
        dict(),
        id="HSL_TARGET_GET"),
    pytest.param(
        b'\x82\x7a\x77\x66\x99\x88\xbb\xaa',
        LightHSLOpcode.LIGHT_HSL_TARGET_STATUS,
        dict(hsl_lightness=0x6677,
             hsl_hue=0x8899,
             hsl_saturation=0xaabb),
        id="HSL_TARGET_STATUS"),
    pytest.param(
        b'\x82\x7a\x77\x66\x99\x88\xbb\xaa\x48',
        LightHSLOpcode.LIGHT_HSL_TARGET_STATUS,
        dict(hsl_lightness=0x6677,
             hsl_hue=0x8899,
             hsl_saturation=0xaabb,
             remaining_time=8),
        id="HSL_TARGET_STATUS_with_optional"),

    pytest.param(
        b'\x82\x6e',
        LightHSLOpcode.LIGHT_HSL_HUE_GET,
        dict(),
        id="HSL_HUE_GET"),
    pytest.param(
        b'\x82\x6f\xbb\xaa\x0a',
        LightHSLOpcode.LIGHT_HSL_HUE_SET,
        dict(hue=0xaabb,
             tid=10),
        id="HSL_HUE_SET"),
    pytest.param(
        b'\x82\x6f\xbb\xaa\x0b\x0a\x14',
        LightHSLOpcode.LIGHT_HSL_HUE_SET,
        dict(hue=0xaabb,
             tid=11,
             transition_time=1,
             delay=0.1),
        id="HSL_HUE_SET_with_optional"),
    pytest.param(
        b'\x82\x70\xbb\xaa\x0c\x14\x28',
        LightHSLOpcode.LIGHT_HSL_HUE_SET_UNACKNOWLEDGED,
        dict(hue=0xaabb,
             tid=12,
             transition_time=2,
             delay=0.2),
        id="HSL_HUE_SET_UNACKNOWLEDGED"),
    pytest.param(
        b'\x82\x71\xdd\xcc',
        LightHSLOpcode.LIGHT_HSL_HUE_STATUS,
        dict(present_hue=0xccdd),
        id="HSL_HUE_STATUS"),
    pytest.param(
        b'\x82\x71\xdd\xcc\xff\xee\x1e',
        LightHSLOpcode.LIGHT_HSL_HUE_STATUS,
        dict(present_hue=0xccdd,
             target_hue=0xeeff,
             remaining_time=3),
        id="HSL_HUE_STATUS_with_optional"),

    pytest.param(
        b'\x82\x72',
        LightHSLOpcode.LIGHT_HSL_SATURATION_GET,
        dict(),
        id="HSL_SATURATION_GET"),
    pytest.param(
        b'\x82\x73\xbb\xaa\x0d',
        LightHSLOpcode.LIGHT_HSL_SATURATION_SET,
        dict(saturation=0xaabb,
             tid=13),
        id="HSL_SATURATION_SET"),
    pytest.param(
        b'\x82\x73\x22\x11\x0e\x28\x50',
        LightHSLOpcode.LIGHT_HSL_SATURATION_SET,
        dict(saturation=0x1122,
             tid=14,
             transition_time=4,
             delay=0.4),
        id="HSL_SATURATION_SET_with_optional"),
    pytest.param(
        b'\x82\x74\x44\x33\x0f\x2d\x5a',
        LightHSLOpcode.LIGHT_HSL_SATURATION_SET_UNACKNOWLEDGED,
        dict(saturation=0x3344,
             tid=15,
             transition_time=4.5,
             delay=0.45),
        id="HSL_SATURATION_SET_UNACKNOWLEDGED"),
    pytest.param(
        b'\x82\x75\x66\x55',
        LightHSLOpcode.LIGHT_HSL_SATURATION_STATUS,
        dict(present_saturation=0x5566),
        id="HSL_SATURATION_SATURATION_STATUS"),
    pytest.param(
        b'\x82\x75\x88\x77\x00\x99\x23',
        LightHSLOpcode.LIGHT_HSL_SATURATION_STATUS,
        dict(present_saturation=0x7788,
             target_saturation=0x9900,
             remaining_time=3.5),
        id="HSL_SATURATION_STATUS_with_optional"),
    pytest.param(
        b'\x82\x7b',
        LightHSLOpcode.LIGHT_HSL_DEFAULT_GET,
        dict(),
        id="HSL_DEFAULT_GET"),
    pytest.param(
        b'\x82\x7c\xa9\xcb\x65\x87\x21\x43',
        LightHSLOpcode.LIGHT_HSL_DEFAULT_STATUS,
        dict(hsl_lightness=0xcba9,
             hsl_hue=0x8765,
             hsl_saturation=0x4321),
        id="HSL_DEFAULT_STATUS"),
    pytest.param(
        b'\x82\x7d',
        LightHSLOpcode.LIGHT_HSL_RANGE_GET,
        dict(),
        id="HSL_RANGE_GET"),
    pytest.param(
        b'\x82\x7e\x00\x10\x00\xff\x10\xaa\x00\xff\xaa',
        LightHSLOpcode.LIGHT_HSL_RANGE_STATUS,
        dict(status=StatusCode.SUCCESS,
             hue_range_min=0x0010,
             hue_range_max=0x10ff,
             saturation_range_min=0x00aa,
             saturation_range_max=0xaaff),
        id="HSL_RANGE_STATUS"),
    # fmt: on
]


valid_hsl_setup = [
    # fmt: off
    pytest.param(
        b'\x82\x7f\xaa\xaa\xbb\xbb\xcc\xcc',
        LightHSLSetupOpcode.LIGHT_HSL_SETUP_DEFAULT_SET,
        dict(hsl_lightness=0xaaaa,
             hsl_hue=0xbbbb,
             hsl_saturation=0xcccc),
        id="HSL_SETUP_DEFAULT_SET"),
    pytest.param(
        b'\x82\x80\xdd\xdd\xee\xee\xff\xff',
        LightHSLSetupOpcode.LIGHT_HSL_SETUP_DEFAULT_SET_UNACKNOWLEDGED,
        dict(hsl_lightness=0xdddd,
             hsl_hue=0xeeee,
             hsl_saturation=0xffff),
        id="HSL_SETUP_DEFAULT_SET_UNACKNOWLEDGED"),

    pytest.param(
        b'\x82\x81\x20\x00\xff\x20\xbb\x00\xff\xbb',
        LightHSLSetupOpcode.LIGHT_HSL_SETUP_RANGE_SET,
        dict(hue_range_min=0x0020,
             hue_range_max=0x20ff,
             saturation_range_min=0x00bb,
             saturation_range_max=0xbbff),
        id="HSL_SETUP_RANGE_SET"),
    pytest.param(
        b'\x82\x82\x30\x00\xff\x30\xcc\x00\xff\xcc',
        LightHSLSetupOpcode.LIGHT_HSL_SETUP_RANGE_SET_UNACKNOWLEDGED,
        dict(hue_range_min=0x0030,
             hue_range_max=0x30ff,
             saturation_range_min=0x00cc,
             saturation_range_max=0xccff),
        id="HSL_SETUP_RANGE_SET_UNACKNOWLEDGED"),
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


@pytest.mark.parametrize("encoded,opcode,data", valid_hsl)
def test_parse_valid_hsl(encoded, opcode, data):
    assert LightHSLMessage.parse(encoded).params == data


@pytest.mark.parametrize("encoded,opcode,data", valid_hsl)
def test_build_valid_hsl(encoded, opcode, data):
    assert LightHSLMessage.build(dict(opcode=opcode, params=data)) == encoded


@pytest.mark.parametrize("encoded,opcode,data", valid_hsl_setup)
def test_parse_valid_hsl_setup(encoded, opcode, data):
    assert LightHSLSetupMessage.parse(encoded).params == data


@pytest.mark.parametrize("encoded,opcode,data", valid_hsl_setup)
def test_build_valid_hsl_setup(encoded, opcode, data):
    assert LightHSLSetupMessage.build(dict(opcode=opcode, params=data)) == encoded

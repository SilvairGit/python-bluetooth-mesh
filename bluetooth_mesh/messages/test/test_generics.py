import pytest
from construct import ValidationError

from bluetooth_mesh.messages.generic.onoff import *
from bluetooth_mesh.messages.generics import *


@pytest.mark.parametrize("steps, resolution, expected_tt",
                         [(0x00, 0b00, "00"),
                          (0x01, 0b00, "04"),
                          (0x01, 0b01, "05"),
                          (0x3E, 0b00, "F8"),
                          (0x3E, 0b11, "FB")
                          ]
                         )
def test_build_transition_time(steps, resolution, expected_tt):
    tt = TransitionTime.build(dict(steps=steps, resolution=resolution))
    assert tt == bytes.fromhex(expected_tt)


def test_build_invalid_value():
    with pytest.raises(ValidationError):
        TransitionTime.build(dict(steps=0x3F, resolution=0b00))


@pytest.mark.parametrize("raw_bytes, expected_steps, expected_resolution",
                         [("00", 0x00, 0b00),
                          ("01", 0x00, 0b01),
                          ("04", 0x01, 0b00),
                          ("F8", 0x3E, 0b00),
                          ("FB", 0x3E, 0b11)
                          ]
                         )
def test_parse_transition_time(raw_bytes, expected_steps, expected_resolution):
    tt = TransitionTime.parse(bytes.fromhex(raw_bytes))
    assert tt.steps == expected_steps
    assert tt.resolution == expected_resolution


def test_parse_invalid_value():
    with pytest.raises(ValidationError):
        TransitionTime.parse(bytes.fromhex("FC"))


valid = [
    pytest.param(
        b'\x82\x01',
        GenericOnOffOpcode.ONOFF_GET,
        dict(),
        id="ONOFF_GET"),
    pytest.param(
        b'\x82\x02\x01\x22',
        GenericOnOffOpcode.ONOFF_SET,
        dict(onoff=1,
             tid=34,
             transition_time=None,
             delay=None),
        id="ONOFF_SET"),
    pytest.param(
        b'\x82\x02\x00\x31\x00\x3c',
        GenericOnOffOpcode.ONOFF_SET,
        dict(onoff=0,
             tid=49,
             transition_time=dict(
                 steps=0,
                 resolution=0
             ),
             delay=0.3),
        id="ONOFF_SET_with_optional"),
    pytest.param(
        b'\x82\x04\x00',
        GenericOnOffOpcode.ONOFF_STATUS,
        dict(present_onoff=0,
             target_onoff=None,
             remaining_time=None),
        id="ONOFF_STATUS"),
    pytest.param(
        b'\x82\x04\x00\x01\x05',
        GenericOnOffOpcode.ONOFF_STATUS,
        dict(present_onoff=0,
             target_onoff=1,
             remaining_time=dict(
                 steps=1,
                 resolution=1
             )),
        id="ONOFF_STATUS_with_optional"),
]


@pytest.mark.parametrize("encoded,opcode,data", valid)
def test_parse_valid(encoded, opcode, data):
    assert GenericOnOffMessage.parse(encoded).params == data


@pytest.mark.parametrize("encoded,opcode,data", valid)
def test_build_valid(encoded, opcode, data):
    assert GenericOnOffMessage.build(dict(opcode=opcode, params=data)) == \
        encoded

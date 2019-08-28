import pytest

from bluetooth_mesh.messages.generic.level import GenericLevelMessage, GenericLevelOpcode


valid = [
    pytest.param(
        b'\x82\x05',
        GenericLevelOpcode.LEVEL_GET,
        dict(),
        id="LEVEL_GET"),
    pytest.param(
        b'\x82\x06\xbb\xaa\x22',
        GenericLevelOpcode.LEVEL_SET,
        dict(level=0xaabb,
             tid=34),
        id="LEVEL_SET"),
    pytest.param(
        b'\x82\x06\x01\x00\x22',
        GenericLevelOpcode.LEVEL_SET,
        dict(level=1,
             tid=34,
             transition_time=6.3,
             delay=0.3),
        id="LEVEL_SET_invalid"),
    pytest.param(
        b'\x82\x06\x00\x00\x31\x32\x3c',
        GenericLevelOpcode.LEVEL_SET,
        dict(level=0,
             tid=49,
             transition_time=5,
             delay=0.3),
        id="LEVEL_SET_with_optional"),
    pytest.param(
        b'\x82\x07\x00\x00\x31\x32\x3c',
        GenericLevelOpcode.LEVEL_SET_UNACKNOWLEDGED,
        dict(level=0,
             tid=49,
             transition_time=5,
             delay=0.3),
        id="LEVEL_SET_UNACKNOWLEDGED"),
    pytest.param(
        b'\x82\x08\x00\xff',
        GenericLevelOpcode.LEVEL_STATUS,
        dict(present_level=0xff00,
             target_level=None,
             remaining_time=None),
        id="LEVEL_STATUS"),
    pytest.param(
        b'\x82\x08\x00\x00\xaa\xaa\x4a',
        GenericLevelOpcode.LEVEL_STATUS,
        dict(present_level=0,
             target_level=0xaaaa,
             remaining_time=10),
        id="LEVEL_STATUS_with_optional"),
    pytest.param(
        b'\x82\x08\x00\x00\x01\x00\xff',
        GenericLevelOpcode.LEVEL_STATUS,
        dict(present_level=0,
             target_level=1,
             remaining_time=37800),
        id="LEVEL_STATUS_max_time"),
    pytest.param(
        b'\x82\x09\xdd\xcc\xbb\xaa\x22',
        GenericLevelOpcode.DELTA_SET,
        dict(delta_level=0xaabbccdd,
             tid=34),
        id="DELTA_SET"),
    pytest.param(
        b'\x82\x09\x01\x00\x00\x00\x22',
        GenericLevelOpcode.DELTA_SET,
        dict(delta_level=1,
             tid=34,
             transition_time=6.3,
             delay=0.3),
        id="DELTA_SET_invalid"),
    pytest.param(
        b'\x82\x09\x00\x00\x00\x00\x31\x32\x3c',
        GenericLevelOpcode.DELTA_SET,
        dict(delta_level=0,
             tid=49,
             transition_time=5,
             delay=0.3),
        id="DELTA_SET_with_optional"),
    pytest.param(
        b'\x82\x0a\x00\x00\x00\x00\x31\x32\x3c',
        GenericLevelOpcode.DELTA_SET_UNACKNOWLEDGED,
        dict(delta_level=0,
             tid=49,
             transition_time=5,
             delay=0.3),
        id="DELTA_SET_UNACKNOWLEDGED"),

    pytest.param(
        b'\x82\x0b\xbb\xaa\x22',
        GenericLevelOpcode.MOVE_SET,
        dict(delta_level=0xaabb,
             tid=34),
        id="MOVE_SET"),
    pytest.param(
        b'\x82\x0b\x01\x00\x22',
        GenericLevelOpcode.MOVE_SET,
        dict(delta_level=1,
             tid=34,
             transition_time=6.3,
             delay=0.3),
        id="MOVE_SET_invalid"),
    pytest.param(
        b'\x82\x0b\x00\x00\x31\x32\x3c',
        GenericLevelOpcode.MOVE_SET,
        dict(delta_level=0,
             tid=49,
             transition_time=5,
             delay=0.3),
        id="MOVE_SET_with_optional"),
    pytest.param(
        b'\x82\x0c\x00\x00\x31\x32\x3c',
        GenericLevelOpcode.MOVE_SET_UNACKNOWLEDGED,
        dict(delta_level=0,
             tid=49,
             transition_time=5,
             delay=0.3),
        id="MOVE_SET_UNACKNOWLEDGED"),
]


@pytest.mark.parametrize("encoded,opcode,data", valid)
def test_parse_valid(encoded, opcode, data):
    assert GenericLevelMessage.parse(encoded).params == data


@pytest.mark.parametrize("encoded,opcode,data", valid)
def test_build_valid(encoded, opcode, data):
    assert GenericLevelMessage.build(dict(opcode=opcode, params=data)) == \
        encoded

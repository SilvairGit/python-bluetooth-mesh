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
from datetime import timedelta, datetime, timezone

import pytest

from bluetooth_mesh.messages.time import (
    TimeOpcode,
    TimeMessage,
    TimeRole,
    MESH_UNIX_EPOCH_DIFF,
    mesh_time_zone_offset_to_timedelta,
    mesh_tai_utc_delta_to_timedelta,
    subsecond_to_seconds,
)

valid = [
    # fmt: off
    pytest.param(
        b'\x82\x37',
        TimeOpcode.TIME_GET,
        dict(),
        id="TIME_GET"
    ),
    pytest.param(
        b'\x5C\xbd\xf7\x67\x26\x00\x1a\xb2\x49\x02\x48',
        TimeOpcode.TIME_SET,
        dict(
            date=datetime.fromtimestamp(
                0x2667f7bd + MESH_UNIX_EPOCH_DIFF + subsecond_to_seconds(0x1A) + mesh_time_zone_offset_to_timedelta(
                    0x48).total_seconds(),
                timezone(mesh_time_zone_offset_to_timedelta(0x48))),
            uncertainty=timedelta(milliseconds=(0xB2 * 10)),
            tai_utc_delta=mesh_tai_utc_delta_to_timedelta(0x0248 >> 1),
            time_authority=True,
        ),
        id="TIME_SET"
    ),
    pytest.param(
        b'\x5D\xbd\xf7\x67\x26\x00\x1a\xb2\x49\x02\x48',
        TimeOpcode.TIME_STATUS,
        dict(
            date=datetime.fromtimestamp(
                0x2667f7bd + MESH_UNIX_EPOCH_DIFF + subsecond_to_seconds(0x1A) + mesh_time_zone_offset_to_timedelta(
                    0x48).total_seconds(),
                timezone(mesh_time_zone_offset_to_timedelta(0x48))),
            uncertainty=timedelta(milliseconds=(0xB2 * 10)),
            tai_utc_delta=mesh_tai_utc_delta_to_timedelta(0x0248 >> 1),
            time_authority=True,
        ),
        id="TIME_STATUS"
    ),
    pytest.param(
        bytes.fromhex("823b"),
        TimeOpcode.TIME_ZONE_GET,
        dict(),
        id="TIME_ZONE_GET"
    ),
    pytest.param(
        bytes.fromhex("823cab3400000012"),
        TimeOpcode.TIME_ZONE_SET,
        dict(
            time_zone_offset_new=0xab,
            tai_of_zone_change=0x1200000034
        ),
        id="TIME_ZONE_SET"
    ),
    pytest.param(
        bytes.fromhex("823dcdab3400000012"),
        TimeOpcode.TIME_ZONE_STATUS,
        dict(
            time_zone_offset_current=0xcd,
            time_zone_offset_new=0xab,
            tai_of_zone_change=0x1200000034
        ),
        id="TIME_ZONE_STATUS"
    ),
    pytest.param(
        bytes.fromhex("823e"),
        TimeOpcode.TAI_UTC_DELTA_GET,
        dict(),
        id="TAI_UTC_DELTA_GET"
    ),
    pytest.param(
        bytes.fromhex("823f01005544332211"),
        TimeOpcode.TAI_UTC_DELTA_SET,
        dict(
            tai_utc_delta_new=0b000000000000001,
            tai_of_delta_change=0x1122334455
        ),
        id="TAI_UTC_DELTA_SET"
    ),
    pytest.param(
        bytes.fromhex("8240014001005544332211"),
        TimeOpcode.TAI_UTC_DELTA_STATUS,
        dict(
            tai_utc_delta_current=0b100000000000001,
            tai_utc_delta_new=0b000000000000001,
            tai_of_delta_change=0x1122334455
        ),
        id="TAI_UTC_DELTA_STATUS"
    ),
    pytest.param(
        bytes.fromhex("8238"),
        TimeOpcode.TIME_ROLE_GET,
        dict(),
        id="TIME_ROLE_GET"
    ),
    pytest.param(
        bytes.fromhex("823903"),
        TimeOpcode.TIME_ROLE_SET,
        dict(
            time_role=TimeRole.TIME_CLIENT,
        ),
        id="TIME_ROLE_SET"
    ),
    pytest.param(
        bytes.fromhex("823A03"),
        TimeOpcode.TIME_ROLE_STATUS,
        dict(
            time_role=TimeRole.TIME_CLIENT,
        ),
        id="TIME_ROLE_STATUS"
    ),
    # # fmt: on
]


@pytest.mark.parametrize("encoded,opcode,data", valid)
def test_parse_valid(encoded, opcode, data):
    assert TimeMessage.parse(encoded).params == data


@pytest.mark.parametrize("encoded,opcode,data", valid)
def test_build_valid(encoded, opcode, data):
    assert TimeMessage.build(dict(opcode=opcode, params=data)) == encoded

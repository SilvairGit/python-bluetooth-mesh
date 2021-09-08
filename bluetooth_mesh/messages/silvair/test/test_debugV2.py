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

from bluetooth_mesh.messages.silvair.debugV2 import (
    DebugV2DataTypes,
    DebugV2ParameterTypes,
    DebugV2SubMessage,
    DebugV2SubOpcode,
)

# fmt: off
valid = [
    pytest.param(b'\x02\x09\x00\x02\x00\x10\x20\x30', DebugV2SubOpcode.STATUS, DebugV2ParameterTypes.UPTIME, 0x00,
                 [{"data_type": DebugV2DataTypes.UINT32, "parameter": 807407616}], id="StatusUptime"),
    pytest.param(b'\x02\x08\x00\x04\x20', DebugV2SubOpcode.STATUS, DebugV2ParameterTypes.RSSI_THRESHOLD, 0x00,
                 [{"data_type": DebugV2DataTypes.INT8, "parameter": 0x20}], id="StatusRSSIThreshold"),
    pytest.param(b'\x02\x0B\x02\x0C\x06\x00\x10\x00\x20\x00\x30', DebugV2SubOpcode.STATUS,
                 DebugV2ParameterTypes.TIME_SYNC_MSG_LIST, 0x02,
                 [{"data_type": DebugV2DataTypes.ARRAY, "parameter": [0x00, 0x10, 0x00, 0x20, 0x00, 0x30]}],
                 id="StatusTimeSyncMsgList"),
    pytest.param(b'\x02\x4B\x00\x0B\x09my string', DebugV2SubOpcode.STATUS, 0x4B, 0x00,
                 [{"data_type": DebugV2DataTypes.STRING, "parameter": "my string"}], id="StatusUnknownParameterString"),
    pytest.param(b'\x02\x55\x00\x02\x00\x10\x20\x30\x0A\x00\x08\x00\x32\x00\x28', DebugV2SubOpcode.STATUS, 0x55, 0x00,
                 [{"data_type": DebugV2DataTypes.UINT32, "parameter": 807407616},
                  {"data_type": DebugV2DataTypes.ENUM, "parameter": 0},
                  {"data_type": DebugV2DataTypes.FLOAT, "parameter": 7.116269379325857e-15}],
                 id="StatusUnknownParameterMultipleFields"),
    pytest.param(b'\x03\x13\x00', DebugV2SubOpcode.CLEAR, DebugV2ParameterTypes.OCCUPANCY_HISTORY, 0x00, [],
                 id="ClearMsgWithoutAnyPayload"),
    pytest.param(b'\x00\x0F\x00', DebugV2SubOpcode.GET, DebugV2ParameterTypes.RECALLED_EVENTS_TIME, 0x00, [],
                 id="GetMsgWithoutAnyPayload"),
    pytest.param(b'\x02\xFE\x00\xFF', DebugV2SubOpcode.STATUS, 0xFE, 0x00,
                 [{"data_type": DebugV2DataTypes.INVALID, "parameter": {}}],
                 id="StatusMsgWithInvalidDataType"),
]


# fmt: on


@pytest.mark.parametrize(
    "encoded, subopcode, parameter_type, page_number, payload", valid
)
def test_parse_valid(encoded, subopcode, parameter_type, page_number, payload):
    decoded = DebugV2SubMessage.parse(encoded)
    assert decoded.subopcode == subopcode
    assert decoded.parameter_type == parameter_type
    assert decoded.page_number == page_number
    for idx, element in enumerate(decoded.payload):
        assert element.data_type == payload[idx]["data_type"]
        assert element.parameter == payload[idx]["parameter"]


@pytest.mark.parametrize(
    "encoded, subopcode, parameter_type, page_number, payload", valid
)
def test_build_valid(encoded, subopcode, parameter_type, page_number, payload):
    assert (
        DebugV2SubMessage.build(
            dict(
                subopcode=subopcode,
                parameter_type=parameter_type,
                page_number=page_number,
                payload=payload,
            )
        )
        == encoded
    )

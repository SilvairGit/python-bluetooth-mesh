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

from bluetooth_mesh.messages.silvair.debug import DebugPayload, DebugSubOpcode

# fmt: off
valid = [
    pytest.param(b'\x00', DebugSubOpcode.RSSI_THRESHOLD_GET, None, id="RssiThresholdGet"),
    pytest.param(b'\x04', DebugSubOpcode.TIMESLOT_TX_POWER_GET, None, id="TimeslotTxPowerGet"),
    pytest.param(b'\x07', DebugSubOpcode.SOFTDEVICE_TX_POWER_GET, None, id="SoftDeviceTxPowerGet"),
    pytest.param(b'\x0a', DebugSubOpcode.UPTIME_GET, None, id="UptimeGet"),
    pytest.param(b'\x0c', DebugSubOpcode.LAST_SW_FAULT_GET, None, id="LastSwFaultGet"),
    pytest.param(b'\x0f', DebugSubOpcode.SYSTEM_STATS_GET, None, id="SystemStatsGet"),
    pytest.param(b'\x11', DebugSubOpcode.LAST_MALLOC_FAULT_GET, None, id="LastMallocFaultGet"),
    pytest.param(b'\x14', DebugSubOpcode.LAST_FDS_FAULT_GET, None, id="LastFdsFaultGet"),
    pytest.param(b'\x17', DebugSubOpcode.BYTES_BEFORE_GARBAGE_COLLECTOR_GET, None, id="BytesBeforeGCGet"),
    pytest.param(b'\x19', DebugSubOpcode.PROVISIONED_APP_VERSION_GET, None, id="ProvisionedAppVersionGet"),
    pytest.param(b'\x1b', DebugSubOpcode.FULL_FIRMWARE_VERSION_GET, None, id="FullFirmwareVersionGet"),
    pytest.param(b'\x1d', DebugSubOpcode.IV_INDEX_GET, None, id="IvIndexGet"),
    pytest.param(b'\x1f', DebugSubOpcode.GARBAGE_COLLECTOR_COUNTER_GET, None, id="GCCounterGet"),
    pytest.param(b'\x0d', DebugSubOpcode.LAST_SW_FAULT_CLEAR, None, id="LastSwFaultClear"),
    pytest.param(b'\x12', DebugSubOpcode.LAST_MALLOC_FAULT_CLEAR, None, id="LastMallocFaultClear"),
    pytest.param(b'\x15', DebugSubOpcode.LAST_FDS_FAULT_CLEAR, None, id="FastFdsFaultClear"),
    pytest.param(b'\x21', DebugSubOpcode.ARAP_LIST_SIZE_GET, None, id="ARAPListSizeGet"),
    pytest.param(
        b'\x23\x02',
        DebugSubOpcode.ARAP_LIST_CONTENT_GET,
        {'page': 2},
        id="ARAPListContentGet"
    ),
    pytest.param(
        b'\x01\x80',
        DebugSubOpcode.RSSI_THRESHOLD_SET,
        {'rssi_threshold': 0x80},
        id="RssiThresholdGet"
    ),
    pytest.param(
        b'\x02\x80',
        DebugSubOpcode.RSSI_THRESHOLD_STATUS,
        {'rssi_threshold': 0x80},
        id="RssiThresholdStatus"
    ),
    pytest.param(
        b'\x03\x01',
        DebugSubOpcode.RADIO_TEST,
        {'packet_counter': 0x01},
        id="RadioTest"
    ),
    pytest.param(
        b'\x05\x02',
        DebugSubOpcode.TIMESLOT_TX_POWER_SET,
        {'tx_power': 0x02},
        id="TimeslotTxPowerSet"
    ),
    pytest.param(
        b'\x06\x04',
        DebugSubOpcode.TIMESLOT_TX_POWER_STATUS,
        {'tx_power': 0x04},
        id="TimeslotTxPowerStatus"
    ),
    pytest.param(
        b'\x08\x02',
        DebugSubOpcode.SOFTDEVICE_TX_POWER_SET,
        {'tx_power': 0x02},
        id="SoftDeviceTxPowerSet"
    ),
    pytest.param(
        b'\x09\x04',
        DebugSubOpcode.SOFTDEVICE_TX_POWER_STATUS,
        {'tx_power': 0x04},
        id="SoftDeviceTxPowerStatus"
    ),
    pytest.param(
        b'\x0b\xa2\xd0\x02\x00',
        DebugSubOpcode.UPTIME_STATUS,
        {'uptime': 184482},
        id="UptimeStatus"
    ),
    pytest.param(
        b'\x0e\x0a\x00\x00\x00Power OFF [7]',
        DebugSubOpcode.LAST_SW_FAULT_STATUS,
        {'time': 10, 'fault': 'Power OFF [7]'},
        id="LastSwFaultStatus"
    ),
    pytest.param(
        b'\x13\x00\x00\x00\x00No Error',
        DebugSubOpcode.LAST_MALLOC_FAULT_STATUS,
        {'time': 0, 'fault': 'No Error'},
        id="LastMallocFaultStatus"
    ),
    pytest.param(
        b'\x16\xff\x00\x00\x00Foo error',
        DebugSubOpcode.LAST_FDS_FAULT_STATUS,
        {'time': 255, 'fault': 'Foo error'},
        id="LastFdsFaultStatus"
    ),
    pytest.param(
        b'\x18\xf8.',
        DebugSubOpcode.BYTES_BEFORE_GARBAGE_COLLECTOR_STATUS,
        {'bytes_left': 12024},
        id="BytesBeforeGarbageCollectorStatus"
    ),
    pytest.param(
        b'\x1a\x08\x0c',
        DebugSubOpcode.PROVISIONED_APP_VERSION_STATUS,
        {'version': 3080},
        id="ProvisionedAppVersionStatus"
    ),
    pytest.param(
        b'\x1c2.12.0-rc4-6c74b4d',
        DebugSubOpcode.FULL_FIRMWARE_VERSION_STATUS,
        {'version': '2.12.0-rc4-6c74b4d'},
        id="FullFirmwareVersionStatus"
    ),
    pytest.param(
        b'\x1e\x05\x00\x00\x00',
        DebugSubOpcode.IV_INDEX_STATUS,
        {'ivindex': 5},
        id="IvIndexStatus"
    ),
    pytest.param(
        b' \x01\x00',
        DebugSubOpcode.GARBAGE_COLLECTOR_COUNTER_STATUS,
        {'counter': 1},
        id="GarbageCollectorCounterStatus"
    ),
    pytest.param(
        bytes.fromhex("22 FEFF 0100"),
        DebugSubOpcode.ARAP_LIST_SIZE_STATUS,
        {'capacity': 65534, 'size': 1},
        id="ArapListSizeStatus"
    ),
    pytest.param(
        b'\x10'
        b'KERNEL\x00\x00\x08\x02\x00\x00\x00\x00'
        b'BLE\x00\x00\x00\x00\x00\x08\x05\x00\x00\x00\x00'
        b'SNV\x00\x00\x00\x00\x00\xc8\x00\x00\x00\x00\x00'
        b'APP\x00\x00\x00\x00\x00\xb4\x01\x00\x00\x00\x00'
        b'RX Task\x00\xe4\x01\x00\x00\x00\x00'
        b'MESH\x00\x00\x00\x00\x08\x04\x00\x00\x00\x00'
        b'Tmr Svc\x00\xf0\x01\x00\x00\x00\x00'
        b'IDLE\x00\x00\x00\x00\xe4\x00\x00\x00\x00\x00'
        b'HEAP\x00\x00\x00\x00\xa8I\x00\x00\x00\x00',
        DebugSubOpcode.SYSTEM_STATS_STATUS,
        {
            "stats": {
                'KERNEL': 520,
                'BLE': 1288,
                'SNV': 200,
                'APP': 436,
                'RX Task': 484,
                'MESH': 1032,
                'Tmr Svc': 496,
                'IDLE': 228,
                'HEAP': 18856,
            }
        },
        id='SystemStatsStatus (long)'
    ),
    pytest.param(
        b'\x10'
        b'HEAP\x00\x00\x00\x00\x88J\x00\x00\x00\x00'
        b'Tmr Svc\x00(\x02\x00\x00\x00\x00'
        b'IDLE\x00\x00\x00\x00\xf4\x00\x00\x00\x00\x00',
        DebugSubOpcode.SYSTEM_STATS_STATUS,
        {
            "stats": {
                'HEAP': 19080, 'Tmr Svc': 552, 'IDLE': 244,
            }
        },
        id='SystemStatsStatus (short)'
    ),
    pytest.param(
        b'$\x00\x00\x80\x80X\x00\x00',
        DebugSubOpcode.ARAP_LIST_CONTENT_STATUS,
        {
            'current_page': 0,
            'last_page': 0,
            'nodes': {
                0x0080: {"ivi": True, "sequence": 0x58},
            }
        },
        id='ArapContent (1 node)'
    ),
    pytest.param(
        b'$\x00\x00\x07\x00p\x0c\x02\x80\x00X\x00\x00',
        DebugSubOpcode.ARAP_LIST_CONTENT_STATUS,
        {
            'current_page': 0,
            'last_page': 0,
            'nodes': {
                0x0007: {"ivi": False, "sequence": 0x20c70},
                0x0080: {"ivi": False, "sequence": 0x58},
            }
        },
        id='ArapContent (2 nodes)'
    ),
]

valid_parse = [
    pytest.param(
        bytes.fromhex("22 7E 0E"),
        DebugSubOpcode.ARAP_LIST_SIZE_STATUS,
        {'capacity': 126, 'size': 14},
        id="ArapListSizeStatus")
]

invalid_build = [
    pytest.param(
        bytes.fromhex("22 7E 0E"),
        DebugSubOpcode.ARAP_LIST_SIZE_STATUS,
        {'capacity': 126, 'size': 14},
        id="ArapListSizeStatus",
        marks=pytest.mark.xfail(reason="1 byte ARAP List Size is not supported in latest FW", strict=True))
]
# fmt: on


@pytest.mark.parametrize("encoded,subopcode,data", valid + valid_parse)
def test_parse_valid(encoded, subopcode, data):
    assert DebugPayload.parse(encoded) == dict(subopcode=subopcode, data=data)


@pytest.mark.parametrize("encoded,subopcode,data", valid + invalid_build)
def test_build_valid(encoded, subopcode, data):
    assert DebugPayload.build(dict(subopcode=subopcode, data=data)) == encoded

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
import enum
import json
import logging
import re
import sys
from datetime import datetime
from tempfile import NamedTemporaryFile

import construct
import pytest

from bluetooth_mesh.messages import AccessMessage
from bluetooth_mesh.messages.util import Opcode, to_camelcase_dict, to_snakecase_dict

if sys.version_info >= (3, 7):
    import capnp

    from bluetooth_mesh.messages.capnproto import generate

valid = [
    # debug
    bytes.fromhex("f5360100"),  # RSSI_THRESHOLD_GET
    bytes.fromhex("f5360101f0"),  # RSSI_THRESHOLD_SET
    bytes.fromhex("f5360102f0"),  # RSSI_THRESHOLD_STATUS
    bytes.fromhex("f5360103ff"),  # RADIO_TEST
    bytes.fromhex("f5360104"),  # TIMESLOT_TX_POWER_GET
    bytes.fromhex("f536010500"),  # TIMESLOT_TX_POWER_SET
    bytes.fromhex("f5360105ff"),  # TIMESLOT_TX_POWER_SET
    bytes.fromhex("f536010600"),  # TIMESLOT_TX_POWER_STATUS
    bytes.fromhex("f5360106ff"),  # TIMESLOT_TX_POWER_STATUS
    bytes.fromhex("f5360107"),  # SOFTDEVICE_TX_POWER_GET
    bytes.fromhex("f536010800"),  # SOFTDEVICE_TX_POWER_SET
    bytes.fromhex("f5360108ff"),  # SOFTDEVICE_TX_POWER_SET
    bytes.fromhex("f536010900"),  # SOFTDEVICE_TX_POWER_STATUS
    bytes.fromhex("f5360109ff"),  # SOFTDEVICE_TX_POWER_STATUS
    bytes.fromhex("f536010a"),  # UPTIME_GET
    bytes.fromhex("f536010b00000000"),  # UPTIME_STATUS
    bytes.fromhex("f536010bffffffff"),  # UPTIME_STATUS
    bytes.fromhex("f536010c"),  # LAST_SW_FAULT_GET
    bytes.fromhex("f536010d"),  # LAST_SW_FAULT_CLEAR
    bytes.fromhex("f536010e00000000616263"),  # LAST_SW_FAULT_STATUS
    bytes.fromhex("f536010f"),  # SYSTEM_STATS_GET
    bytes.fromhex("f5360110"),  # SYSTEM_STATS_STATUS
    bytes.fromhex("f53601106162636465666768000000000000"),
    bytes.fromhex("f53601106162636400000000ffff00000000"),
    bytes.fromhex("f5360111"),  # LAST_MALLOC_FAULT_GET
    bytes.fromhex("f5360112"),  # LAST_MALLOC_FAULT_CLEAR
    bytes.fromhex("f536011300000000616263"),  # LAST_MALLOC_FAULT_STATUS
    bytes.fromhex("f5360114"),  # LAST_FDS_FAULT_GET
    bytes.fromhex("f5360115"),  # LAST_FDS_FAULT_CLEAR
    bytes.fromhex("f536011600000000616263"),  # LAST_FDS_FAULT_STATUS
    bytes.fromhex("f5360117"),  # BYTES_BEFORE_GARBAGE_COLLECTOR_GET
    bytes.fromhex("f53601180000"),  # BYTES_BEFORE_GARBAGE_COLLECTOR_STATUS
    bytes.fromhex("f53601181234"),  # BYTES_BEFORE_GARBAGE_COLLECTOR_STATUS
    bytes.fromhex("f5360118ffff"),  # BYTES_BEFORE_GARBAGE_COLLECTOR_STATUS
    bytes.fromhex("f5360119"),  # PROVISIONED_APP_VERSION_GET
    bytes.fromhex("f536011a0000"),  # PROVISIONED_APP_VERSION_STATUS
    bytes.fromhex("f536011a1234"),  # PROVISIONED_APP_VERSION_STATUS
    bytes.fromhex("f536011affff"),  # PROVISIONED_APP_VERSION_STATUS
    bytes.fromhex("f536011b"),  # FULL_FIRMWARE_VERSION_GET
    bytes.fromhex("f536011c61626364"),  # FULL_FIRMWARE_VERSION_STATUS
    bytes.fromhex("f536011d"),  # IV_INDEX_GET
    bytes.fromhex("f536011e00000000"),  # IV_INDEX_STATUS
    bytes.fromhex("f536011e12345678"),  # IV_INDEX_STATUS
    bytes.fromhex("f536011effffffff"),  # IV_INDEX_STATUS
    bytes.fromhex("f536011f"),  # GARBAGE_COLLECTOR_COUNTER_GET
    bytes.fromhex("f53601200000"),  # GARBAGE_COLLECTOR_COUNTER_STATUS
    bytes.fromhex("f53601201234"),  # GARBAGE_COLLECTOR_COUNTER_STATUS
    bytes.fromhex("f5360120ffff"),  # GARBAGE_COLLECTOR_COUNTER_STATUS
    bytes.fromhex("f5360121"),  # ARAP_LIST_SIZE_GET
    bytes.fromhex("f53601220000"),  # ARAP_LIST_SIZE_STATUS
    bytes.fromhex("f53601221234"),  # ARAP_LIST_SIZE_STATUS
    bytes.fromhex("f5360122ffff"),  # ARAP_LIST_SIZE_STATUS
    bytes.fromhex("f536012200000000"),  # ARAP_LIST_SIZE_STATUS
    bytes.fromhex("f536012212345678"),  # ARAP_LIST_SIZE_STATUS
    bytes.fromhex("f5360122ffffffff"),  # ARAP_LIST_SIZE_STATUS
    bytes.fromhex("f536012300"),  # ARAP_LIST_CONTENT_GET
    bytes.fromhex("f536012312"),  # ARAP_LIST_CONTENT_GET
    bytes.fromhex("f5360123ff"),  # ARAP_LIST_CONTENT_GET
    bytes.fromhex("f53601240000"),  # ARAP_LIST_CONTENT_STATUS
    bytes.fromhex("f536012400000000000000"),  # ARAP_LIST_CONTENT_STATUS
    bytes.fromhex("f53601240000ffffffffff"),  # ARAP_LIST_CONTENT_STATUS
    bytes.fromhex(
        "f53601240000ffffffffff00000000001234561234"
    ),  # ARAP_LIST_CONTENT_STATUS
    # config
    bytes.fromhex("02003601CE00FECAEFBE0BB000000000"),
    bytes.fromhex("8002000b00010000012100"),
    bytes.fromhex("8039010203040506070809"),
    bytes.fromhex("803E00A70202000213"),
    # ctl
    bytes.fromhex("826522223333ff323c"),
    # nds
    bytes.fromhex("fd360100"),  # PUBLICATION_GET
    bytes.fromhex("fd3601011234aaaa82031000"),  # PUBLICATION_SET
    bytes.fromhex("fd3601011234aaaa820310000300"),  # PUBLICATION_SET
    bytes.fromhex("fd3601011234aaaa82031000"),  # PUBLICATION_SET
    bytes.fromhex("fd3601021234aaaa820310000300"),  # PUBLICATION_STATUS
    bytes.fromhex("fc360100"),  # SUBSCRIPTION_GET
    bytes.fromhex("fc3601010123aaaa"),  # SUBSCRIPTION_SET
    bytes.fromhex("fc3601020123aaaa"),  # SUBSCRIPTION_SET_UNACKNOWLEDGED
    bytes.fromhex("fc3601031234aaaa20012300110101"),  # SUBSCRIPTION_STATUS
    # sensor
    bytes.fromhex("8230"),
    bytes.fromhex("82300400"),
    bytes.fromhex("8231"),
    bytes.fromhex("82310700"),
    bytes.fromhex("510c00000000040b0c"),
    bytes.fromhex("511900"),
    bytes.fromhex("510c00000000020b0c1f00efcdab071b1c"),
    bytes.fromhex("52e20ac800"),
    bytes.fromhex("52220b2003"),
    bytes.fromhex("52440da244ff"),
    ##vendor sensor
    # bytes.fromhex("52099040a244ff0000"),
    bytes.fromhex("52440da244ff220b2003"),
    bytes.fromhex("583000010004000900"),
    bytes.fromhex("583000"),
    bytes.fromhex("5957005700c800"),
    bytes.fromhex("5b5700570001c800"),
    bytes.fromhex("5b5700020001c80039"),
    bytes.fromhex("5957005700c800"),
    bytes.fromhex("5957000200c80039"),
    bytes.fromhex("5905000500200354"),
    bytes.fromhex("5957000200c80000"),
    bytes.fromhex("59590059000003"),
    bytes.fromhex("5942004d0001"),
    bytes.fromhex("594200420050"),
    bytes.fromhex("590a003600b80b00"),
    bytes.fromhex("596d006d000a0000"),
    ##no value
    # bytes.fromhex("596d006d00ffffff"),
    bytes.fromhex("59550055001a2700"),
    bytes.fromhex("594c004c001b1a"),
    bytes.fromhex("596c006c00ff1b1a"),
    ##no value
    # bytes.fromhex("596c006c00ffffff"),
    bytes.fromhex("59680068000500"),
    bytes.fromhex("5967006700050001007040"),
    bytes.fromhex("590e000e006162636465666768"),
    bytes.fromhex("590e000e006162636465660000"),
    bytes.fromhex(
        "5911001100616263646566676861626364656667686162636465666768616263646566676861626364"
    ),
    bytes.fromhex("596a006a00a244ff"),
    bytes.fromhex("592e002e0044ff"),
    bytes.fromhex("593200320044ff0000"),
    bytes.fromhex("5952005200a08601"),
    bytes.fromhex("5916001600e80300d007000f2700"),
    bytes.fromhex("594f004f001f"),
    bytes.fromhex("594f004f00e1"),
    bytes.fromhex("5954005400e620"),
    bytes.fromhex("59450045003102dc6e71"),
    bytes.fromhex("591400140092096400f8f8204e71"),
    bytes.fromhex("5913001300dc6e"),
    bytes.fromhex("5901000100186da2"),
    bytes.fromhex("5960006000a244ff6da2"),
    bytes.fromhex("592a002a00690140000000f0ff54"),
    bytes.fromhex("594900490000000006f0ff"),
    bytes.fromhex("59470047009709640000007d1571"),
    bytes.fromhex("594600460000007d15"),
    bytes.fromhex("5921002100000001007d15"),
    bytes.fromhex("5970007000020000"),
    bytes.fromhex("59060006000020"),
    bytes.fromhex("5940004000020000"),
    bytes.fromhex("591f001f00d007"),
    bytes.fromhex("5941004100e803d007"),
    bytes.fromhex("593e003e00d407"),
    bytes.fromhex("590f000f00ffeeddccbbaa"),
    bytes.fromhex("590700070064"),
    bytes.fromhex("595e005e009227"),
    bytes.fromhex("5951005100b80b"),
    bytes.fromhex("590a000a0004f0"),
    bytes.fromhex("590b000b002a00"),
    bytes.fromhex("590c000c00de4600"),
    bytes.fromhex("5950005000ee00cdab"),
    bytes.fromhex("590800080064"),
    bytes.fromhex("59080008009c"),
    bytes.fromhex("596100610088aa00bbbb"),
    bytes.fromhex("5962006200881a27001a2700"),
    bytes.fromhex("596400640088ffffe620"),
    bytes.fromhex("5965006500880000cdab"),
    bytes.fromhex("59660066008820032003"),
    # light
    bytes.fromhex("824b"),
    bytes.fromhex("824cbbaa22"),
    bytes.fromhex("824c010022"),
    bytes.fromhex("824c000031323c"),
    bytes.fromhex("824d000031323c"),
    bytes.fromhex("824e4400"),
    bytes.fromhex("824e000031c80f"),
    bytes.fromhex("824f"),
    bytes.fromhex("8250bbaa01"),
    bytes.fromhex("8250010022"),
    bytes.fromhex("8250000031321b"),
    bytes.fromhex("8251ff0031323c"),
    bytes.fromhex("82520000ddbb4c"),
    bytes.fromhex("8253"),
    bytes.fromhex("82540000"),
    bytes.fromhex("8255"),
    bytes.fromhex("82560000"),
    bytes.fromhex("8257"),
    bytes.fromhex("82580011118888"),
    # scene
    bytes.fromhex("8241"),
    bytes.fromhex("824201001e"),
    bytes.fromhex("824301001e"),
    bytes.fromhex("824201001ef23c"),
    bytes.fromhex("824301001ef23c"),
    bytes.fromhex("5e000100"),
    bytes.fromhex("5e0001000200f2"),
    bytes.fromhex("8244"),
    bytes.fromhex("824500010001000200") + 14 * bytes.fromhex("0000"),
    bytes.fromhex("82460100"),
    bytes.fromhex("82470100"),
    bytes.fromhex("829e0100"),
    bytes.fromhex("829f0100"),
    # onoff
    bytes.fromhex("8201"),
    bytes.fromhex("82020122"),
    bytes.fromhex("82020122"),
    bytes.fromhex("82020031323c"),
    bytes.fromhex("82020031f23c"),
    bytes.fromhex("820400"),
    bytes.fromhex("820400014a"),
    bytes.fromhex("82040001ff"),
    # level
    bytes.fromhex("8205"),
    bytes.fromhex("8206ff7f22"),
    bytes.fromhex("8206008022"),
    bytes.fromhex("8206010022"),
    bytes.fromhex("8206000031323c"),
    bytes.fromhex("8207000031323c"),
    bytes.fromhex("8208ff7f"),
    bytes.fromhex("82080080"),
    bytes.fromhex("82080000ff004a"),
    bytes.fromhex("820800000100ff"),
    bytes.fromhex("8209ffffff7f22"),
    bytes.fromhex("82090000008022"),
    bytes.fromhex("82090100000022"),
    bytes.fromhex("82090000000031323c"),
    bytes.fromhex("820a0000000031323c"),
    bytes.fromhex("820bff7f22"),
    bytes.fromhex("820b008022"),
    bytes.fromhex("820b010022"),
    bytes.fromhex("820b000031323c"),
    bytes.fromhex("820c000031323c"),
    bytes.fromhex("5d8ea9282a005905490248"),
]


@pytest.fixture(scope="session")
def capnproto():
    with NamedTemporaryFile("w", suffix=".capnp") as f:
        generate(0xD988DA1AAFBE9E47, f)
        f.flush()
        return capnp.load(f.name)


@pytest.mark.skipif(sys.version_info < (3, 7), reason="requires Python3.7")
@pytest.mark.parametrize("encoded", [pytest.param(i, id=i.hex()) for i in valid])
def test_parse_capnproto(encoded, capnproto):
    logging.info("MESH[%i] %s", len(encoded), encoded.hex())

    decoded = AccessMessage.parse(encoded)
    logging.info("CONSTRUCT %r", decoded)

    params = to_camelcase_dict(decoded)
    logging.info("CAPNP INPUT[%i] %s", len(json.dumps(params)), json.dumps(params))

    message = capnproto.AccessMessage.new_message(**params)
    logging.info("CAPNP %r", message)

    packed = message.to_bytes_packed()
    logging.info("PACKED[%i] %s", len(packed), packed.hex())

    unpacked = capnproto.AccessMessage.from_bytes_packed(packed)
    logging.info("UNPACKED %r", unpacked)

    params = to_snakecase_dict(unpacked.to_dict())
    logging.info("CONSTRUCT INPUT %s", params)

    recoded = AccessMessage.build(params)
    logging.info("RECODED[%i] %s", len(recoded), recoded.hex())

    assert recoded == encoded

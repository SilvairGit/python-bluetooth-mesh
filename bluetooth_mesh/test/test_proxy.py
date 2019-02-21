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
from collections import namedtuple
from pytest import fixture, mark, param

from bluetooth_mesh.proxy import SarProcessor


SAR_PACKETS = dict(
    complete=(
        [
            bytes(range(6)),
        ],
        [
            bytes([0b00000000]) + bytes(range(6)),
        ],
    ),
    two_segments=(
        [
            bytes(range(42)),
        ],
        [
            bytes([0b01000000]) + bytes(range(32)),
            bytes([0b11000000]) + bytes(range(32, 42)),
        ],
    ),
    two_segments_exact=(
        [
            bytes(range(64)),
        ],
        [
            bytes([0b01000000]) + bytes(range(32)),
            bytes([0b11000000]) + bytes(range(32, 64)),
        ],
    ),
    more_segments=(
        [
            bytes(range(72)),
        ],
        [
            bytes([0b01000000]) + bytes(range(32)),
            bytes([0b10000000]) + bytes(range(32, 64)),
            bytes([0b11000000]) + bytes(range(64, 72)),
        ],
    ),
    more_segments_exact=(
        [
            bytes(range(96)),
        ],
        [
            bytes([0b01000000]) + bytes(range(32)),
            bytes([0b10000000]) + bytes(range(32, 64)),
            bytes([0b11000000]) + bytes(range(64, 96)),
        ],
    )
)


@mark.parametrize("packets, segments", [
    param(*v, id=k) for k, v in SAR_PACKETS.items()
])
def test_segmentation(packets, segments):
    received_packets = []
    sent_segments = []

    sar_processor = SarProcessor(None,
                                 sent_segments.append,
                                 segment_size=32)

    for packet in packets:
        sar_processor.packet_send(packet)

    assert sent_segments == segments


@mark.parametrize("packets, segments", [
    param(*v, id=k) for k, v in SAR_PACKETS.items()
])
def test_reassembly(packets, segments):
    received_packets = []
    sent_segments = []

    sar_processor = SarProcessor(lambda packet, type: received_packets.append(packet),
                                 None,
                                 segment_size=32)

    for segment in segments:
        sar_processor.segment_receive(segment)

    assert received_packets == packets


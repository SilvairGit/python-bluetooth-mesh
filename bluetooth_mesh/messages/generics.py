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
# pylint: disable=W0223

from construct import Adapter, BitsInteger, BitStruct, Float32b, Int8ul, Int16ul, Struct


class TransitionTimeAdapter(Adapter):
    _subcon = Float32b
    RESOLUTION = {0b00: 0.1, 0b01: 1, 0b10: 10, 0b11: 10 * 60}

    def __init__(self, subcon, allow_unknown=False):
        self.max_steps = 0x3F if allow_unknown else 0x3E
        super().__init__(subcon)

    def _decode(self, obj, context, path):
        return obj["steps"] * self.RESOLUTION[obj["resolution"]]

    def _encode(self, obj, context, path):
        resolution = None
        steps = None
        for range_index, range_value in self.RESOLUTION.items():
            if obj <= range_value * 0x3F:
                resolution = range_index
                steps = obj / range_value
                assert round(steps, 0) <= self.max_steps, "Unknown not allowed"
                break

        assert resolution is not None

        return dict(steps=int(steps), resolution=resolution)


class Delay(Adapter):
    _subcon = Float32b

    def _decode(self, obj, context, path):
        return obj / 200

    def _encode(self, obj, context, path):
        return int(obj * 200)


# fmt: off
TransitionTime = BitStruct(
    "resolution" / BitsInteger(2),
    "steps" / BitsInteger(6)
)

OptionalSetParameters = Struct(
    "transition_time" / TransitionTimeAdapter(TransitionTime, allow_unknown=False),
    "delay" / Delay(Int8ul)
)
# fmt: on

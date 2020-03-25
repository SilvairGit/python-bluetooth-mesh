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

from bluetooth_mesh.utils import construct_match


@pytest.mark.parametrize(
    "received, expected",
    [
        pytest.param(42, 42,),
        pytest.param([1, 2, 3], [1, 2, 3],),
        pytest.param([1, 2, 3, 4], [1, 2, ..., 4],),
        pytest.param(dict(a=42, b=[1, 2, 3]), dict(a=42, b=[1, 2, 3]),),
        pytest.param(dict(a=42, b=[1, 2, 3]), dict(b=[1, 2, 3]),),
    ],
)
def test_construct_match(received, expected):
    assert construct_match(received, expected)


@pytest.mark.parametrize(
    "received, expected",
    [
        pytest.param(42, 41,),
        pytest.param([1, 2, 3], [1, 2, 3, 4],),
        pytest.param([1, 2, 3, 4], [1, 2, ...],),
        pytest.param(dict(a=42, b=[1, 2, 3]), dict(a=42, b=[1, 3]),),
    ],
)
def test_construct_doesnt_match(received, expected):
    assert not construct_match(received, expected)

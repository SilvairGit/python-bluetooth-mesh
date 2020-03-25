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

from bluetooth_mesh.messages.generic.onoff import GenericOnOffOpcode


@pytest.fixture()
def status_parsed():
    return dict(opcode=GenericOnOffOpcode.ONOFF_STATUS, params=dict(present_onoff=0))


@pytest.fixture()
def status_encoded():
    return b"\x82\x04\x00"


@pytest.fixture()
def get_encoded():
    return b"\x82\x01"


@pytest.fixture()
def source():
    return 0x0001


@pytest.fixture()
def destination():
    return 0x0010


@pytest.fixture()
def app_index():
    return 0


@pytest.fixture()
def net_index():
    return 0


@pytest.fixture
def element_path():
    return "test_element_path_string"

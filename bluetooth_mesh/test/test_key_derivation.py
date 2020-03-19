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
from pytest import fixture, skip

from bluetooth_mesh.crypto import ApplicationKey, DeviceKey, NetworkKey


@fixture
def app_key():
    return ApplicationKey(bytes.fromhex("63964771734fbd76e3b40519d1d94a48"))


@fixture
def net_key():
    return NetworkKey(bytes.fromhex("7dd7364cd842ad18c17c2b820c84c3d6"))


@fixture
def dev_key():
    return DeviceKey(bytes.fromhex("9d6dd0e96eb25dc19a40ed9914f8f03f"))


def test_application_key_id(app_key):
    assert app_key.aid == 0x26


def test_device_key_id(dev_key):
    assert dev_key.aid == 0


def test_encryption_keys_master(net_key):
    nid, encryption_key, privacy_key = net_key.encryption_keys

    assert nid == 0x68
    assert encryption_key == bytes.fromhex("0953fa93e7caac9638f58820220a398e")
    assert privacy_key == bytes.fromhex("8b84eedec100067d670971dd2aa700cf")


def test_network_id(net_key):
    assert net_key.network_id == bytes.fromhex("3ecaff672f673370")


def test_identity_key(net_key):
    assert net_key.identity_key == bytes.fromhex("84396c435ac48560b5965385253e210c")


def test_beacon_key(net_key):
    assert net_key.beacon_key == bytes.fromhex("5423d967da639a99cb02231a83f7d254")

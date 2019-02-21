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
from bluetooth_mesh.mesh import SecureNetworkBeacon, AccessMessage, NetworkMessage, Nonce


@fixture
def app_key():
    return ApplicationKey(bytes.fromhex('63964771734fbd76e3b40519d1d94a48'))


@fixture
def net_key():
    return NetworkKey(bytes.fromhex('7dd7364cd842ad18c17c2b820c84c3d6'))


@fixture
def dev_key():
    return DeviceKey(bytes.fromhex('9d6dd0e96eb25dc19a40ed9914f8f03f'))


@fixture
def health_current_status_message():
    payload = bytes.fromhex('0400000000')
    return AccessMessage(src=0x1201, dst=0xffff, ttl=0x03, payload=payload)


@fixture
def config_appkey_status_message():
    payload = bytes.fromhex('800300563412')
    return AccessMessage(src=0x1201, dst=0x0003, ttl=0x0b, payload=payload)


@fixture
def config_appkey_add_message():
    payload = bytes.fromhex('0056341263964771734fbd76e3b40519d1d94a48')
    return AccessMessage(src=0x0003, dst=0x1201, ttl=0x04, payload=payload)


def test_beacon_received(net_key):
    beacon, auth = SecureNetworkBeacon.unpack(bytes.fromhex('003ecaff672f673370123456788ea261582f364f6f'))

    assert beacon.verify(auth, net_key)

    assert beacon.network_id == net_key.network_id
    assert not beacon.key_refresh
    assert not beacon.iv_update
    assert beacon.iv_index == 0x12345678


def test_beacon_received_iv_update(net_key):
    beacon, auth = SecureNetworkBeacon.unpack(bytes.fromhex('023ecaff672f67337012345679c2af80ad072a135c'))

    assert beacon.verify(auth, net_key)

    assert beacon.network_id == net_key.network_id
    assert not beacon.key_refresh
    assert beacon.iv_update
    assert beacon.iv_index == 0x12345679


def test_beacon_created(net_key):
    beacon = SecureNetworkBeacon(False, False, 0x12345678, network_id=net_key.network_id)

    assert beacon.pack(net_key) == (bytes.fromhex('003ecaff672f67337012345678'),
                                    bytes.fromhex('8ea261582f364f6f'))


def test_network_nonce(config_appkey_status_message):
    assert Nonce(config_appkey_status_message.src,
                 config_appkey_status_message.dst,
                 config_appkey_status_message.ttl,
                 False).network(seq=0x000006, iv_index=0x12345678) == bytes.fromhex('000b0000061201000012345678')


def test_device_nonce(config_appkey_status_message):
    assert Nonce(config_appkey_status_message.src,
                 config_appkey_status_message.dst,
                 config_appkey_status_message.ttl,
                 False).device(seq=0x000006, iv_index=0x12345678) == bytes.fromhex('02000000061201000312345678')


def test_application_nonce(health_current_status_message):
    assert Nonce(health_current_status_message.src,
                 health_current_status_message.dst,
                 health_current_status_message.ttl,
                 False).application(seq=0x000007, iv_index=0x12345678) == bytes.fromhex('01000000071201ffff12345678')


def test_device_transport_pdu(config_appkey_status_message, dev_key):
    (seq, transport_pdu), = \
        config_appkey_status_message.transport_pdu(dev_key, seq=0x000006, iv_index=0x12345678)

    assert transport_pdu == bytes.fromhex('0089511bf1d1a81c11dcef')


def test_application_transport_pdu(health_current_status_message, app_key):
    (seq, transport_pdu), = \
        health_current_status_message.transport_pdu(app_key, seq=0x000007, iv_index=0x12345678)

    assert transport_pdu == bytes.fromhex('665a8bde6d9106ea078a')


def test_application_transport_pdu_segmented(config_appkey_add_message, dev_key):
    (seq0, transport_pdu0), (seq1, transport_pdu1) = \
        config_appkey_add_message.transport_pdu(dev_key, seq=0x3129ab, iv_index=0x12345678)

    assert seq0 == 0x3129ab
    assert transport_pdu0 == bytes.fromhex('8026ac01ee9dddfd2169326d23f3afdf')

    assert seq1 == 0x3129ab + 1
    assert transport_pdu1 == bytes.fromhex('8026ac21cfdc18c52fdef772e0e17308')


def test_application_network_pdu(health_current_status_message, app_key, net_key):
    network_message = NetworkMessage(health_current_status_message)

    (seq, network_pdu), = \
        network_message.pack(app_key, net_key, seq=0x000007, iv_index=0x12345678)

    assert network_pdu.hex() == '6848cba437860e5673728a627fb938535508e21a6baf57'

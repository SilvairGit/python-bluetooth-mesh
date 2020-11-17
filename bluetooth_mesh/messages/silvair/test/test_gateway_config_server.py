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

from bluetooth_mesh.messages.silvair.gateway_config_server import (
    ConnState,
    DhcpFlag,
    GatewayConfigPayload,
    GatewayConfigServerSubOpcode,
    LastError,
    LinkStatus,
    StatusCode,
)
from bluetooth_mesh.messages.util import IPv4Address

valid = [
    pytest.param(
        GatewayConfigPayload,
        bytes.fromhex("00"),
        GatewayConfigServerSubOpcode.GATEWAY_CONFIGURATION_GET,
        None,
        id="ConfigurationGet",
    ),
    pytest.param(
        GatewayConfigPayload,
        bytes.fromhex("01 B004 ABCDEFABCDEF D204 D007 0B 3139322E3136382E302E31"),
        GatewayConfigServerSubOpcode.GATEWAY_CONFIGURATION_SET,
        dict(
            mtu_size=1200,
            mac_address="ab:cd:ef:ab:cd:ef",
            server_port_number=1234,
            reconnect_interval=2000,
            server_address_length=11,
            server_address="192.168.0.1",
        ),
        id="ConfigurationSetWithoutOptionalAutoDhcpEnabled",
    ),
    pytest.param(
        GatewayConfigPayload,
        bytes.fromhex(
            "01 B004 ABCDEFABCDEF D204 D007 19 7777772E72616E646F6D686F73746E616D652E636F6D2E706C"
        ),
        GatewayConfigServerSubOpcode.GATEWAY_CONFIGURATION_SET,
        dict(
            mtu_size=1200,
            mac_address="ab:cd:ef:ab:cd:ef",
            server_port_number=1234,
            reconnect_interval=2000,
            server_address_length=25,
            server_address="www.randomhostname.com.pl",
        ),
        id="ConfigurationSetWithoutOptionalAutoDhcpEnabledHostname",
    ),
    pytest.param(
        GatewayConfigPayload,
        bytes.fromhex(
            "01 B004 ABCDEFABCDEF D204 D007 0B 3139322E3136382E302E31 0A2A0002"
        ),
        GatewayConfigServerSubOpcode.GATEWAY_CONFIGURATION_SET,
        dict(
            mtu_size=1200,
            mac_address="ab:cd:ef:ab:cd:ef",
            server_port_number=1234,
            reconnect_interval=2000,
            server_address_length=11,
            server_address="192.168.0.1",
            dns_ip_address=IPv4Address("10.42.0.2"),
        ),
        id="ConfigurationSetWithOptionalDhcpEnabledWithStaticDns",
    ),
    pytest.param(
        GatewayConfigPayload,
        bytes.fromhex(
            "01 DE03 ABCDEFABCDEF ABCD 04D2"
            "19 7777772E72616E646F6D686F73746E616D652E636F6D2E706C 0A2A0002"
        ),
        GatewayConfigServerSubOpcode.GATEWAY_CONFIGURATION_SET,
        dict(
            mtu_size=990,
            mac_address="ab:cd:ef:ab:cd:ef",
            server_port_number=52651,
            reconnect_interval=53764,
            server_address_length=25,
            server_address="www.randomhostname.com.pl",
            dns_ip_address=IPv4Address("10.42.0.2"),
        ),
        id="ConfigurationSetWithOptionalDhcpEnabledWithStaticDnsHostname",
    ),
    pytest.param(
        GatewayConfigPayload,
        bytes.fromhex(
            "01 B004 ABCDEFABCDEF D204 D007 0B 3139322E3136382E302E31 0A2A0002 C0A80002 C0A80001 08"
        ),
        GatewayConfigServerSubOpcode.GATEWAY_CONFIGURATION_SET,
        dict(
            mtu_size=1200,
            mac_address="ab:cd:ef:ab:cd:ef",
            server_port_number=1234,
            reconnect_interval=2000,
            server_address_length=11,
            server_address="192.168.0.1",
            dns_ip_address=IPv4Address("10.42.0.2"),
            ip_address=IPv4Address("192.168.0.2"),
            gateway_ip_address=IPv4Address("192.168.0.1"),
            netmask=8,
        ),
        id="ConfigurationSetWithOptionalDhcpDisabled",
    ),
    pytest.param(
        GatewayConfigPayload,
        bytes.fromhex(
            "01 B004 ABCDEFABCDEF D204 D007 19 7777772E72616E646F6D686F73746E616D652E636F6D2E706C"
            "0A2A0002 C0A80002 C0A80001 08"
        ),
        GatewayConfigServerSubOpcode.GATEWAY_CONFIGURATION_SET,
        dict(
            mtu_size=1200,
            mac_address="ab:cd:ef:ab:cd:ef",
            server_port_number=1234,
            reconnect_interval=2000,
            server_address_length=25,
            server_address="www.randomhostname.com.pl",
            dns_ip_address=IPv4Address("10.42.0.2"),
            ip_address=IPv4Address("192.168.0.2"),
            gateway_ip_address=IPv4Address("192.168.0.1"),
            netmask=8,
        ),
        id="ConfigurationSetWithOptionalDhcpDisabledHostname",
    ),
    pytest.param(
        GatewayConfigPayload,
        bytes.fromhex("02"),
        GatewayConfigServerSubOpcode.GATEWAY_PACKETS_GET,
        None,
        id="PacketsGet",
    ),
    pytest.param(
        GatewayConfigPayload,
        bytes.fromhex("03"),
        GatewayConfigServerSubOpcode.GATEWAY_PACKETS_CLEAR,
        None,
        id="PacketsClear",
    ),
    pytest.param(
        GatewayConfigPayload,
        bytes.fromhex("04 DC05"),
        GatewayConfigServerSubOpcode.MTU_SIZE_SET,
        dict(mtu_size=1500),
        id="mtu_size",
    ),
    pytest.param(
        GatewayConfigPayload,
        bytes.fromhex("05 112233445566"),
        GatewayConfigServerSubOpcode.ETHERNET_MAC_ADDRESS_SET,
        dict(mac_address="11:22:33:44:55:66"),
        id="EthernetMacAddressSet",
    ),
    pytest.param(
        GatewayConfigPayload,
        bytes.fromhex("06 4522 0B 3139322E3136382E302E31"),
        GatewayConfigServerSubOpcode.SERVER_ADDRESS_AND_PORT_NUMBER_SET,
        dict(
            server_port_number=8773,
            server_address_length=11,
            server_address="192.168.0.1",
        ),
        id="ServerAddressAndPortNumberSet",
    ),
    pytest.param(
        GatewayConfigPayload,
        bytes.fromhex("06 4522 19 7777772E72616E646F6D686F73746E616D652E636F6D2E706C"),
        GatewayConfigServerSubOpcode.SERVER_ADDRESS_AND_PORT_NUMBER_SET,
        dict(
            server_port_number=8773,
            server_address_length=25,
            server_address="www.randomhostname.com.pl",
        ),
        id="ServerAddressAndPortNumberSetHostname",
    ),
    pytest.param(
        GatewayConfigPayload,
        bytes.fromhex("07 E803"),
        GatewayConfigServerSubOpcode.RECONNECT_INTERVAL_SET,
        dict(reconnect_interval=1000),
        id="ReconnectIntervalSet",
    ),
    pytest.param(
        GatewayConfigPayload,
        bytes.fromhex("08 0A2A0002"),
        GatewayConfigServerSubOpcode.DNS_IP_ADDRESS_SET,
        dict(dns_ip_address=IPv4Address("10.42.0.2")),
        id="DnsIpAddressSet",
    ),
    pytest.param(
        GatewayConfigPayload,
        bytes.fromhex("09 C0A80001"),
        GatewayConfigServerSubOpcode.IP_ADDRESS_SET,
        dict(ip_address=IPv4Address("192.168.0.1")),
        id="IpAddressSet",
    ),
    pytest.param(
        GatewayConfigPayload,
        bytes.fromhex("0A C0A80C03"),
        GatewayConfigServerSubOpcode.GATEWAY_IP_ADDRESS_SET,
        dict(gateway_ip_address=IPv4Address("192.168.12.03")),
        id="GatewayIpAddressSet",
    ),
    pytest.param(
        GatewayConfigPayload,
        bytes.fromhex("0B 08"),
        GatewayConfigServerSubOpcode.NETMASK_SET,
        dict(netmask=8),
        id="NetmaskSet",
    ),
    pytest.param(
        GatewayConfigPayload,
        bytes.fromhex(
            "0C 0A B202 DDDDEFABCDEF 1111 2222 0F 7777772E74657374696E672E636F6D 7B2C0515 C0A80A02 C0A80A01 0A 00 00"
        ),
        GatewayConfigServerSubOpcode.GATEWAY_CONFIGURATION_STATUS,
        dict(
            chip_revision_id=10,
            mtu_size=690,
            mac_address="dd:dd:ef:ab:cd:ef",
            server_port_number=4369,
            reconnect_interval=8738,
            server_address_length=15,
            server_address="www.testing.com",
            dns_ip_address=IPv4Address("123.44.5.21"),
            ip_address=IPv4Address("192.168.10.2"),
            gateway_ip_address=IPv4Address("192.168.10.1"),
            netmask=10,
            flags=DhcpFlag.DHCP_DISABLED,
            status_code=StatusCode.STATUS_SUCCESS,
        ),
        id="ConfigurationStatus",
    ),
    pytest.param(
        GatewayConfigPayload,
        bytes.fromhex(
            "0C 0A B202 DDDDEFABCDEF 1111 2222 00 C0A80A02 C0A80A02 C0A80A01 0A 02 00"
        ),
        GatewayConfigServerSubOpcode.GATEWAY_CONFIGURATION_STATUS,
        dict(
            chip_revision_id=10,
            mtu_size=690,
            mac_address="dd:dd:ef:ab:cd:ef",
            server_port_number=4369,
            reconnect_interval=8738,
            server_address_length=0,
            server_address="",
            dns_ip_address=IPv4Address("192.168.10.2"),
            ip_address=IPv4Address("192.168.10.2"),
            gateway_ip_address=IPv4Address("192.168.10.01"),
            netmask=10,
            flags=DhcpFlag.DHCP_ENABLED_AUTO_DNS,
            status_code=StatusCode.STATUS_SUCCESS,
        ),
        id="ConfigurationStatusEmptyHostname",
    ),
    pytest.param(
        GatewayConfigPayload,
        bytes.fromhex("0D 0000 0002 03E8 92"),
        GatewayConfigServerSubOpcode.GATEWAY_PACKETS_STATUS,
        dict(
            total_eth_rx_errors=0,
            total_eth_tx_errors=512,
            bandwidth=59395,
            connection_state=dict(
                conn_state=ConnState.ETHERNET_HANDSHAKE,
                link_status=LinkStatus.LINK_UP,
                last_error=LastError.ERROR_ENODEV,
            ),
        ),
        id="PacketsStatus",
    ),
]


@pytest.mark.parametrize("test, encoded, subopcode, payload", valid)
def test_parse_valid(test, encoded, subopcode, payload):
    print(test.parse(encoded))
    print(dict(subopcode=subopcode, payload=payload))
    assert test.parse(encoded) == dict(subopcode=subopcode, payload=payload)

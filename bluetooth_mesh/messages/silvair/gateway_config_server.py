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
from enum import IntEnum

from construct import (
    BitsInteger,
    BitStruct,
    Bytes,
    Const,
    Default,
    Embedded,
    Int8ul,
    Int16ul,
    PaddedString,
    Select,
    Struct,
    this,
)

from bluetooth_mesh.messages.util import EnumAdapter
from bluetooth_mesh.messages.util import EnumSwitch as Switch
from bluetooth_mesh.messages.util import (
    IpAddressAdapter,
    MacAddressAdapter,
    Opcode,
    SwitchStruct,
)


class GatewayConfigServerOpcode(IntEnum):
    SILVAIR_GATEWAY = 0xF03601


class GatewayConfigServerSubOpcode(IntEnum):
    GATEWAY_CONFIGURATION_GET = 0x00
    GATEWAY_CONFIGURATION_SET = 0x01
    GATEWAY_PACKETS_GET = 0x02
    GATEWAY_PACKETS_CLEAR = 0x03
    MTU_SIZE_SET = 0x04
    ETHERNET_MAC_ADDRESS_SET = 0x05
    SERVER_ADDRESS_AND_PORT_NUMBER_SET = 0x06
    RECONNECT_INTERVAL_SET = 0x07
    DNS_IP_ADDRESS_SET = 0x08
    IP_ADDRESS_SET = 0x09
    GATEWAY_IP_ADDRESS_SET = 0x0A
    NETMASK_SET = 0x0B
    GATEWAY_CONFIGURATION_STATUS = 0x0C
    GATEWAY_PACKETS_STATUS = 0x0D


class ConnState(IntEnum):
    ETHERNET_IDLE = 0x00
    ETHERNET_CONFIGURING = 0x01
    ETHERNET_INITIALIZING = 0x02
    ETHERNET_CONNECTING = 0x03
    ETHERNET_HANDSHAKE = 0x04
    ETHERNET_CONNECTED = 0x05


class LinkStatus(IntEnum):
    LINK_DOWN = 0x00
    LINK_UP = 0x01


class LastError(IntEnum):
    ERROR_NO_ERROR = 0x00
    ERROR_EPERM = 0x01
    ERROR_ENODEV = 0x02
    ERROR_EADDRINUSE = 0x03
    ERROR_EPROTO = 0x04
    ERROR_RFU1 = 0x05
    ERROR_RFU2 = 0x06
    ERROR_RFU3 = 0x07
    ERROR_RFU4 = 0x08
    ERROR_RFU5 = 0x09
    ERROR_RFU6 = 0x0A
    ERROR_RFU7 = 0x0B
    ERROR_RFU8 = 0x0C
    ERROR_RFU9 = 0x0D
    ERROR_RFU10 = 0x0E
    ERROR_UNKNOWN = 0x0F


class DhcpFlag(IntEnum):
    DHCP_DISABLED = 0x00
    DHCP_ENABLED_STATIC_DNS = 0x01
    DHCP_ENABLED_AUTO_DNS = 0x02


class StatusCode(IntEnum):
    STATUS_SUCCESS = 0x00
    STATUS_INVALID_ADDRESS = 0x01
    STATUS_INVALID_MODEL = 0x02
    STATUS_INVALID_APPKEY_IDX = 0x03
    STATUS_INVALID_NETKEY_IDX = 0x04
    STATUS_INSUFF_RESOURCES = 0x05
    STATUS_KEY_INDEX_ALREADY_STORED = 0x06
    STATUS_INVALID_PUBLISH_PARAMS = 0x07
    STATUS_NOT_SUBSCRIBE_MODEL = 0x08
    STATUS_STORAGE_FAILURE = 0x09
    STATUS_FEATURE_NOT_SUPPORTED = 0x0A
    STATUS_CANNOT_UPDATE = 0x0B
    STATUS_CANNOT_REMOVE = 0x0C
    STATUS_CANNOT_BIND = 0x0D
    STATUS_TEMP_UNABLE_TO_CHANGE_STATE = 0x0E
    STATUS_CANNOT_SET = 0x0F
    STATUS_UNSPECIFIED_ERROR = 0x10
    STATUS_INVALID_BINDING = 0x11


# fmt: off
# GATEWAY CONFIGURATION MSG
ConfigurationSetMtu = Struct(
    "mtu_size" / Int16ul,
)

ConfigurationSetMacAddr = Struct(
    "mac_address" / MacAddressAdapter(Bytes(6)),
)

ConfigurationSetServerAddrAndPortNr = Struct(
    "server_port_number" / Int16ul,
    "server_address_length" / Int8ul,
    "server_address" / PaddedString(this.server_address_length, "utf8"),
)

ConfigurationSetReconnectInterval = Struct(
    "reconnect_interval" / Int16ul,
)

ConfigurationSetDnsIpAddr = Struct(
    "dns_ip_address" / IpAddressAdapter(Bytes(4)),
)

ConfigurationSetIpAddr = Struct(
    "ip_address" / IpAddressAdapter(Bytes(4)),
)

ConfigurationSetGatewayIpAddr = Struct(
    "gateway_ip_address" / IpAddressAdapter(Bytes(4)),
)

ConfigurationSetNetmask = Struct(
    "netmask" / Int8ul,
)

ConfigurationSetWithoutOptionalAutoDhcpEnabled = Struct(
    "mtu_size" / Int16ul,
    "mac_address" / MacAddressAdapter(Bytes(6)),
    "server_port_number" / Int16ul,
    "reconnect_interval" / Int16ul,
    "server_address_length" / Int8ul,
    "server_address" / PaddedString(this.server_address_length, "utf8"),
)

ConfigurationSetWithOptionalDhcpEnabledWithStaticDns = Struct(
    Embedded(ConfigurationSetWithoutOptionalAutoDhcpEnabled),
    "dns_ip_address" / IpAddressAdapter(Bytes(4)),
)

ConfigurationSetWithOptionalDhcpDisabled = Struct(
    Embedded(ConfigurationSetWithOptionalDhcpEnabledWithStaticDns),
    "ip_address" / IpAddressAdapter(Bytes(4)),
    "gateway_ip_address" / IpAddressAdapter(Bytes(4)),
    "netmask" / Int8ul,
)

ConfigurationSet = Select(
    static=ConfigurationSetWithOptionalDhcpDisabled,
    dns=ConfigurationSetWithOptionalDhcpEnabledWithStaticDns,
    minimal=ConfigurationSetWithoutOptionalAutoDhcpEnabled,
)

ConfigurationStatus = Struct(
    "chip_revision_id" / Int8ul,
    Embedded(ConfigurationSetWithOptionalDhcpDisabled),
    "flags" / EnumAdapter(Int8ul, DhcpFlag),
    "status_code" / EnumAdapter(Int8ul, StatusCode),
)

ConnectionState = BitStruct(
    "conn_state" / EnumAdapter(BitsInteger(3), ConnState),
    "link_status" / EnumAdapter(BitsInteger(1), LinkStatus),
    "last_error" / EnumAdapter(BitsInteger(4), LastError)
)

# GATEWAY PACKETS MSG
PacketsStatus = Struct(
    "total_eth_rx_errors" / Int16ul,
    "total_eth_tx_errors" / Int16ul,
    "bandwidth" / Int16ul,
    "connection_state" / ConnectionState,
)

GatewayConfigParams = SwitchStruct(
    "subopcode" / EnumAdapter(Int8ul, GatewayConfigServerSubOpcode),
    "payload" / Switch(
        this.subopcode,
        {
            GatewayConfigServerSubOpcode.GATEWAY_CONFIGURATION_SET: ConfigurationSet,
            GatewayConfigServerSubOpcode.MTU_SIZE_SET: ConfigurationSetMtu,
            GatewayConfigServerSubOpcode.ETHERNET_MAC_ADDRESS_SET: ConfigurationSetMacAddr,
            GatewayConfigServerSubOpcode.SERVER_ADDRESS_AND_PORT_NUMBER_SET: ConfigurationSetServerAddrAndPortNr,
            GatewayConfigServerSubOpcode.RECONNECT_INTERVAL_SET: ConfigurationSetReconnectInterval,
            GatewayConfigServerSubOpcode.DNS_IP_ADDRESS_SET: ConfigurationSetDnsIpAddr,
            GatewayConfigServerSubOpcode.IP_ADDRESS_SET: ConfigurationSetIpAddr,
            GatewayConfigServerSubOpcode.GATEWAY_IP_ADDRESS_SET: ConfigurationSetGatewayIpAddr,
            GatewayConfigServerSubOpcode.NETMASK_SET: ConfigurationSetNetmask,
            GatewayConfigServerSubOpcode.GATEWAY_CONFIGURATION_STATUS: ConfigurationStatus,
            GatewayConfigServerSubOpcode.GATEWAY_PACKETS_STATUS: PacketsStatus,
        },
    )
)

GatewayConfigMessage = SwitchStruct(
    "opcode" / Opcode(GatewayConfigServerOpcode),
    "params" / Switch(
        this.opcode,
        {
            GatewayConfigServerOpcode.SILVAIR_GATEWAY: GatewayConfigParams
        }
    )
)
# fmt: on

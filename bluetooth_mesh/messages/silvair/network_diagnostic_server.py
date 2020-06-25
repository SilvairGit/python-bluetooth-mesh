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
    Const,
    Default,
    GreedyRange,
    Int8ul,
    Int16ul,
    Optional,
    Struct,
    Switch,
    this,
)

from bluetooth_mesh.messages.config import (
    TTL,
    ConfigHeartbeatHops,
    ConfigHeartbeatPublicationFeatures,
    Int12ul,
    UnicastUnassignedAddress,
    UnicastUnassignedGroupAddress,
)
from bluetooth_mesh.messages.generic.onoff import TransitionTime
from bluetooth_mesh.messages.util import EnumAdapter, Opcode

MAX_RECORD_COUNT = 32


class NetworkDiagnosticServerOpcode(IntEnum):
    OPCODE = 0xFC3601


class NetworkDiagnosticServerSubOpcode(IntEnum):
    SUBSCRIPTION_GET = 0x00
    SUBSCRIPTION_SET = 0x01
    SUBSCRIPTION_SET_UNACK = 0x02
    SUBSCRIPTION_STATUS = 0x03
    RADIO_STAT_GET = 0x04
    RADIO_STAT_SET = 0x05
    RADIO_STAT_STATUS = 0x06


class NetworkDiagnosticSetupServerOpcode(IntEnum):
    OPCODE = 0xFD3601


class NetworkDiagnosticSetupServerSubOpcode(IntEnum):
    PUBLICATION_GET = 0x00
    PUBLICATION_SET = 0x01
    PUBLICATION_STATUS = 0x02


# fmt: off
RegistryRecord = Struct(
    "source" / UnicastUnassignedAddress,
    "count" / Int16ul,
    "min_hops" / ConfigHeartbeatHops,
    "max_hops" / ConfigHeartbeatHops
)

NetworkDiagnosticSetupServerPublicationSet = Struct(
    "destination" / UnicastUnassignedGroupAddress,
    "count" / Int16ul,
    "period" / TransitionTime,
    "ttl" / TTL,
    "net_key_index" / Int12ul,
    "features" / Optional(ConfigHeartbeatPublicationFeatures)
)

NetworkDiagnosticSetupServerPublicationStatus = NetworkDiagnosticSetupServerPublicationSet

NetworkDiagnosticServerSubscriptionSet = Struct(
    "destination" / UnicastUnassignedGroupAddress,
    "period" / Int16ul
)

NetworkDiagnosticServerSubscriptionStatus = Struct(
    "destination" / UnicastUnassignedGroupAddress,
    "period" / Int16ul,
    "max_record_count" / Const(MAX_RECORD_COUNT, Int8ul),
    "record" / GreedyRange(RegistryRecord)
)

NetworkDiagnosticServerPayload = Struct(
    "subopcode" / EnumAdapter(Int8ul, NetworkDiagnosticServerSubOpcode),
    "payload" / Default(Switch(
        this.subopcode,
        {
            NetworkDiagnosticServerSubOpcode.SUBSCRIPTION_SET: NetworkDiagnosticServerSubscriptionSet,
            NetworkDiagnosticServerSubOpcode.SUBSCRIPTION_SET_UNACK: NetworkDiagnosticServerSubscriptionSet,
            NetworkDiagnosticServerSubOpcode.SUBSCRIPTION_STATUS: NetworkDiagnosticServerSubscriptionStatus
        }
    ), None)
)

NetworkDiagnosticSetupServerPayload = Struct(
    "subopcode" / EnumAdapter(Int8ul, NetworkDiagnosticSetupServerSubOpcode),
    "payload" / Default(Switch(
        this.subopcode,
        {
            NetworkDiagnosticSetupServerSubOpcode.PUBLICATION_SET: NetworkDiagnosticSetupServerPublicationSet,
            NetworkDiagnosticSetupServerSubOpcode.PUBLICATION_STATUS: NetworkDiagnosticSetupServerPublicationStatus,
        }
    ), None)
)

NetworkDiagnosticServerMessage = Struct(
    "opcode" / Const(NetworkDiagnosticServerOpcode.OPCODE, Opcode(NetworkDiagnosticServerOpcode)),
    "params" / NetworkDiagnosticServerPayload
)

NetworkDiagnosticSetupServerMessage = Struct(
    "opcode" / Const(NetworkDiagnosticSetupServerOpcode.OPCODE, Opcode(NetworkDiagnosticSetupServerOpcode)),
    "params" / NetworkDiagnosticSetupServerPayload
)
# fmt: on

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
from construct import ValidationError

from bluetooth_mesh.messages.silvair.network_diagnostic_server import (
    NetworkDiagnosticServerPayload,
    NetworkDiagnosticServerSubOpcode,
    NetworkDiagnosticSetupServerPayload,
    NetworkDiagnosticSetupServerSubOpcode,
)

# fmt: off
valid = [
    pytest.param(
        NetworkDiagnosticSetupServerPayload,
        bytes.fromhex("00"),
        NetworkDiagnosticSetupServerSubOpcode.PUBLICATION_GET,
        None,
        id='PublicationGet'
    ),
    pytest.param(
        NetworkDiagnosticSetupServerPayload,
        bytes.fromhex("01 1234 AAAA 82 03 1000"),
        NetworkDiagnosticSetupServerSubOpcode.PUBLICATION_SET,
        dict(
            destination=0x3412,
            count=0xAAAA,
            period=dict(steps=0x02, resolution=0b10),
            ttl=0x03,
            net_key_index=0x0010,
            features=None
        ),
        id='PublicationSet (no features)'
    ),
    pytest.param(
        NetworkDiagnosticSetupServerPayload,
        bytes.fromhex("01 1234 AAAA 82 03 1000 0300"),
        NetworkDiagnosticSetupServerSubOpcode.PUBLICATION_SET,
        dict(
            destination=0x3412,
            count=0xAAAA,
            period=dict(steps=0x02, resolution=0b10),
            ttl=0x03,
            net_key_index=0x0010,
            features=0x0003
        ),
        id="PublicationSet (with features)"
    ),
    pytest.param(
        NetworkDiagnosticSetupServerPayload,
        bytes.fromhex("02 1234 AAAA 82 03 1000"),
        NetworkDiagnosticSetupServerSubOpcode.PUBLICATION_STATUS,
        dict(
            destination=0x3412,
            count=0xAAAA,
            period=dict(steps=0x02, resolution=0b10),
            ttl=0x03,
            net_key_index=0x0010,
            features=None
        ),
        id="PublicationStatus (no features)"
    ),
    pytest.param(
        NetworkDiagnosticSetupServerPayload,
        bytes.fromhex("02 1234 AAAA 82 03 1000 0300"),
        NetworkDiagnosticSetupServerSubOpcode.PUBLICATION_STATUS,
        dict(
            destination=0x3412,
            count=0xAAAA,
            period=dict(steps=0x02, resolution=0b10),
            ttl=0x03,
            net_key_index=0x0010,
            features=0x0003
        ),
        id="PublicationStatus (with features)"
    ),
    pytest.param(
        NetworkDiagnosticServerPayload,
        bytes.fromhex("00"),
        NetworkDiagnosticServerSubOpcode.SUBSCRIPTION_GET,
        None,
        id="SubscriptionGet"
    ),
    pytest.param(
        NetworkDiagnosticServerPayload,
        bytes.fromhex("01 1234 AAAA"),
        NetworkDiagnosticServerSubOpcode.SUBSCRIPTION_SET,
        dict(
            destination=0x3412,
            period=0xAAAA
        ),
        id="SubscriptionSet"
    ),
    pytest.param(
        NetworkDiagnosticServerPayload,
        bytes.fromhex("03 1234 AAAA 20 5678 BBBB 00 00"),
        NetworkDiagnosticServerSubOpcode.SUBSCRIPTION_STATUS,
        dict(
            destination=0x3412,
            period=0xAAAA,
            max_record_count=32,
            record=[dict(source=0x7856, count=0xBBBB, min_hops=0x00, max_hops=0x00)]
        ),
        id="SubscriptionStatus (one record)"
    ),
    pytest.param(
        NetworkDiagnosticServerPayload,
        bytes.fromhex("03 1234 AAAA 20 5678 BBBB 00 00 9101 CCCC 01 01"),
        NetworkDiagnosticServerSubOpcode.SUBSCRIPTION_STATUS,
        dict(
            destination=0x3412,
            period=0xAAAA,
            max_record_count=32,
            record=[
                dict(source=0x7856, count=0xBBBB, min_hops=0x00, max_hops=0x00),
                dict(source=0x0191, count=0xCCCC, min_hops=0x01, max_hops=0x01),
            ]
        ),
        id="SubscriptionStatus (multiple records)"
    )
]
# fmt: on


@pytest.mark.parametrize("klass,encoded,subopcode,payload", valid)
def test_parse_valid(klass, encoded, subopcode, payload):
    assert klass.parse(encoded) == dict(subopcode=subopcode, payload=payload)


@pytest.mark.parametrize("klass,encoded,subopcode,payload", valid)
def test_build_valid(klass, encoded, subopcode, payload):
    assert klass.build(dict(subopcode=subopcode, payload=payload)) == encoded


def test_prohibited_destination_addr_publication_set():
    with pytest.raises(ValidationError):
        NetworkDiagnosticServerPayload.build(
            dict(
                subopcode=NetworkDiagnosticSetupServerSubOpcode.PUBLICATION_SET,
                payload=dict(
                    destination=0xFF00,
                    count=0xAAAA,
                    period=dict(steps=0x02, resolution=0b10),
                    ttl=0x03,
                    net_key_index=0x0010,
                    features=None,
                ),
            )
        )


def test_prohibited_destination_addr_subscription_set():
    with pytest.raises(ValidationError):
        NetworkDiagnosticServerPayload.build(
            dict(
                subopcode=NetworkDiagnosticServerSubOpcode.SUBSCRIPTION_SET,
                payload=dict(destination=0xFF00, period=0xAAAA),
            )
        )


def test_prohibited_source_addr_subscription_stat():
    with pytest.raises(ValidationError):
        NetworkDiagnosticServerPayload.build(
            dict(
                subopcode=NetworkDiagnosticServerSubOpcode.SUBSCRIPTION_STATUS,
                payload=dict(
                    destination=0x3412,
                    period=0xAAAA,
                    max_record_count=32,
                    record=[
                        dict(source=0xFF00, count=0xBBBB, min_hops=0x00, max_hops=0x00)
                    ],
                ),
            )
        )

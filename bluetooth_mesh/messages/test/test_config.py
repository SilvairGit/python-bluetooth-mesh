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
from copy import deepcopy

import pytest
from construct import ValidationError

from bluetooth_mesh.messages.config import *

valid = [
    # fmt: off
    pytest.param(
        SecureNetworkBeaconAdapter,
        bytes.fromhex('00'),
        SecureNetworkBeacon.OFF,
        id="SecureNetworkBeaconAdapter - Off"
    ),
    pytest.param(
        SecureNetworkBeaconAdapter,
        bytes.fromhex('01'),
        SecureNetworkBeacon.ON,
        id="SecureNetworkBeaconAdapter - On"
    ),
    pytest.param(
        GATTProxyAdapter,
        bytes.fromhex('00'),
        GATTProxy.DISABLED,
        id="GATTProxyAdapter - Disabled"
    ),
    pytest.param(
        GATTProxyAdapter,
        bytes.fromhex('01'),
        GATTProxy.ENABLED,
        id="GATTProxyAdapter - Enabled"
    ),
    pytest.param(
        GATTProxyAdapter,
        bytes.fromhex('02'),
        GATTProxy.NOT_SUPPORTED,
        id="GATTProxyAdapter - NOT_SUPPORTED"
    ),
    pytest.param(
        RelayAdapter,
        bytes.fromhex('00'),
        Relay.DISABLED,
        id="RelayAdapter - Disabled"
    ),
    pytest.param(
        RelayAdapter,
        bytes.fromhex('01'),
        Relay.ENABLED,
        id="RelayAdapter - Enabled"
    ),
    pytest.param(
        RelayAdapter,
        bytes.fromhex('02'),
        Relay.NOT_SUPPORTED,
        id="RelayAdapter - NOT_SUPPORTED"
    ),
    pytest.param(
        GATTNamespaceDescriptorAdapter,
        bytes.fromhex('DC00'),
        GATTNamespaceDescriptor.TWO_HUNDRED_TWENTIETH,
        id="GATTNamespaceDescriptorAdapter - TWO_HUNDRED_TWENTIETH"
    ),
    pytest.param(
        GATTNamespaceDescriptorAdapter,
        bytes.fromhex('0000'),
        GATTNamespaceDescriptor.UNKNOWN,
        id="GATTNamespaceDescriptorAdapter - UNKNOWN"
    ),
    pytest.param(
        TTL,
        bytes.fromhex('7F'),
        0x7F,
        id="TTL-Max"
    ),
    pytest.param(
        TTL,
        bytes.fromhex('6F'),
        0x6F,
        id="TTL"
    ),
    pytest.param(
        TTL,
        bytes.fromhex('00'),
        0x00,
        id="TTL-Min"
    ),
    pytest.param(
        SIGModelId,
        bytes.fromhex('ADDE'),
        {
            "model_id": 0xDEAD,
        },
        id="SIGModelId"
    ),
    pytest.param(
        SIGModelId,
        bytes.fromhex('ADDE'),
        {
            "model_id": 0xDEAD,
            "vendor_id": 0xC0DE
        },
        id="SIGModelId - accepts None vendor id"
    ),
    pytest.param(
        VendorModelId,
        bytes.fromhex('DEC0ADDE'),
        {
            "model_id": 0xDEAD,
            "vendor_id": 0xC0DE
        },
        id="VendorModelId"
    ),
    pytest.param(
        ModelId,
        bytes.fromhex('DEC0ADDE'),
        {
            "model_id": 0xDEAD,
            "vendor_id": 0xC0DE
        },
        id="ModelId - vendor"
    ),
    pytest.param(
        ModelId,
        bytes.fromhex('ADDE'),
        {
            "model_id": 0xDEAD
        },
        id="ModelId - SIG"
    ),
    pytest.param(
        ModelId,
        bytes.fromhex('ADDE'),
        {
            "model_id": 0xDEAD,
            "vendor_id": None
        },
        id="ModelId - accepts None vendor id"
    ),
    pytest.param(
        UnassignedAddress,
        bytes.fromhex('0000'),
        0x0000,
        id="UnassignedAddress"
    ),
    pytest.param(
        UnicastAddress,
        bytes.fromhex('FF7F'),
        0x7FFF,
        id="UnicastAddress - Max"
    ),
    pytest.param(
        UnicastAddress,
        bytes.fromhex('0100'),
        0x0001,
        id="UnicastAddress - Min"
    ),
    pytest.param(
        GroupAddress,
        bytes.fromhex('00C0'),
        0xC000,
        id="GroupAddress - Min"
    ),
    pytest.param(
        VirtualLabel,
        bytes.fromhex('0080'),
        0x8000,
        id="VirtualAddress - Min"
    ),
    pytest.param(
        CompositionDataElement,
        bytes.fromhex('00000101ADDEEFBEADDE'),
        {
            "location": GATTNamespaceDescriptor.UNKNOWN,
            "SIG_number": 0x01,
            "vendor_number": 0x01,
            "SIG_models": [{"model_id": 0xDEAD}],
            "vendor_models": [{"model_id": 0xDEAD, "vendor_id": 0xBEEF}]
        },
        id="CompositionDataElement",),
    pytest.param(
        CompositionDataElement,
        bytes.fromhex('00000001EFBEADDE'),
        {
            "location": GATTNamespaceDescriptor.UNKNOWN,
            "SIG_number": 0x00,
            "vendor_number": 0x01,
            "SIG_models": [],
            "vendor_models": [{"model_id": 0xDEAD, "vendor_id": 0xBEEF}]
        },
        id="CompositionDataElement - No SIG",),
    pytest.param(
        CompositionDataElement,
        bytes.fromhex('00000100ADDE'),
        {
            "location": GATTNamespaceDescriptor.UNKNOWN,
            "SIG_number": 0x01,
            "vendor_number": 0x00,
            "SIG_models": [{"model_id": 0xDEAD}],
            "vendor_models": []
        },
        id="CompositionDataElement - No vendor"
    ),
    pytest.param(
        CompositionData,
        bytes.fromhex('3601CE00FECAEFBE0BB000000000'),
        {
            "CID": 0x0136,
            "PID": 0x00CE,
            "VID": 0xCAFE,
            "CRPL": 0xBEEF,
            "features": 0xB00B,
            "elements": [
                {
                    "location": GATTNamespaceDescriptor.UNKNOWN,
                    "SIG_number": 0x00,
                    "vendor_number": 0x00,
                    "SIG_models": [],
                    "vendor_models": []
                }
            ]
        },
        id="CompositionData - One element",),
    pytest.param(
        CompositionData,
        bytes.fromhex('3601CE00FECAEFBE0BB00000000000000000'),
        {
            "CID": 0x0136,
            "PID": 0x00CE,
            "VID": 0xCAFE,
            "CRPL": 0xBEEF,
            "features": 0xB00B,
            "elements": [
                {
                    "location": GATTNamespaceDescriptor.UNKNOWN,
                    "SIG_number": 0x00,
                    "vendor_number": 0x00,
                    "SIG_models": [],
                    "vendor_models": []
                },
                {
                    "location": GATTNamespaceDescriptor.UNKNOWN,
                    "SIG_number": 0x00,
                    "vendor_number": 0x00,
                    "SIG_models": [],
                    "vendor_models": []
                }
            ]
        },
        id="CompositionData - Two elements"
    ),
    pytest.param(
        Retransmit,
        bytes.fromhex('07'),
        {
            "count": 0x07,
            "interval_steps": 0x00
        },
        id="Retransmit - Max count"
    ),
    pytest.param(
        Retransmit,
        bytes.fromhex('F8'),
        {
            "count": 0x00,
            "interval_steps": 0x1F
        },
        id="Retransmit - Max steps"
    ),
    pytest.param(
        NetworkRetransmit,
        bytes.fromhex('07'),
        {
            "count": 0x07,
            "interval": 10
        },
        id="NetworkRetransmit - Max count"
    ),
    pytest.param(
        NetworkRetransmit,
        bytes.fromhex('F8'),
        {
            "count": 0x00,
            "interval": 320
        },
        id="NetworkRetransmit - Max steps"
    ),
    pytest.param(
        RelayRetransmit,
        bytes.fromhex('07'),
        {
            "count": 0x07,
            "interval": 10
        },
        id="RelayRetransmit - Max count"
    ),
    pytest.param(
        RelayRetransmit,
        bytes.fromhex('F8'),
        {
            "count": 0x00,
            "interval": 320
        },
        id="RelayRetransmit - Max steps"
    ),
    pytest.param(
        PublishRetransmit,
        bytes.fromhex('07'),
        {
            "count": 0x07,
            "interval": 50
        },
        id="PublishRetransmit - Max count"
    ),
    pytest.param(
        PublishRetransmit,
        bytes.fromhex('F8'),
        {
            "count": 0x00,
            "interval": 1600
        },
        id="PublishRetransmit - Max steps"
    ),
    pytest.param(
        Struct(*NetAndAppKeyIndex),
        bytes.fromhex('012345'),
        {
            "net_key_index": 0x301,
            "app_key_index": 0x452,
        },
        id="NetAndAppKeyIndex"
    ),
    pytest.param(
        Struct(*NetAndAppKeyIndex),
        bytes.fromhex('abcdef'),
        {
            "net_key_index": 0xdab,
            "app_key_index": 0xefc
        },
        id="NetAndAppKeyIndex"
    ),
    pytest.param(
        Struct(*NetAndAppKeyIndex),
        bytes.fromhex('efcdab'),
        {
            "net_key_index": 0xdef,
            "app_key_index": 0xabc
        },
        id="NetAndAppKeyIndex"
    ),
    pytest.param(
        PublishPeriod,
        bytes.fromhex('00'),
        {
            "step_resolution": PublishPeriodStepResolution.RESOLUTION_100_MS,
            "number_of_steps": 0x00
        },
        id="PublishPeriod"
    ),
    pytest.param(
        PublishPeriod,
        bytes.fromhex('C0'),
        {
            "step_resolution": PublishPeriodStepResolution.RESOLUTION_10_MIN,
            "number_of_steps": 0x00
        },
        id="PublishPeriod - Max resolution"
    ),
    pytest.param(
        PublishPeriod,
        bytes.fromhex('3F'),
        {
            "step_resolution": PublishPeriodStepResolution.RESOLUTION_100_MS,
            "number_of_steps": 0x3F
        },
        id="PublishPeriod - Max steps"
    ),
    pytest.param(
        ConfigBeaconGet,
        bytes(),
        {},
        id="ConfigBeaconGet"
    ),
    pytest.param(
        ConfigBeaconSet,
        bytes.fromhex('00'),
        {
            "beacon": SecureNetworkBeacon.OFF
        },
        id="ConfigBeaconSet"
    ),
    pytest.param(
        ConfigBeaconStatus,
        bytes.fromhex('01'),
        {
            "beacon": SecureNetworkBeacon.ON
        },
        id="ConfigBeaconStatus-On"
    ),
    pytest.param(
        ConfigCompositionDataGet,
        bytes.fromhex('00'),
        {
            "page": 0x00
        },
        id="ConfigCompositionDataGet - Min page"
    ),
    pytest.param(
        ConfigCompositionDataGet,
        bytes.fromhex('FF'),
        {
            "page": 0xFF
        },
        id="ConfigCompositionDataGet - Max page"
    ),
    pytest.param(
        ConfigCompositionDataStatus,
        bytes.fromhex('003601CE00FECAEFBE0BB000000000'),
        {
            "page": 0x00,
            "data": {
                "CID": 0x0136,
                "PID": 0x00CE,
                "VID": 0xCAFE,
                "CRPL": 0xBEEF,
                "features": 0xB00B,
                "elements": [
                    {
                        "location": GATTNamespaceDescriptor.UNKNOWN,
                        "SIG_number": 0x00,
                        "vendor_number": 0x00,
                        "SIG_models": [],
                        "vendor_models": []
                    }
                ]
            }
        },
        id="ConfigCompositionDataStatus - page 0",),
    pytest.param(
        ConfigCompositionDataStatus,
        bytes.fromhex('01CAFE'),
        {
            "page": 0x01,
            "data": bytes.fromhex('CAFE')
        },
        id="ConfigCompositionDataStatus - not page 0"
    ),
    pytest.param(
        ConfigDefaultTTLGet,
        bytes(),
        {},
        id="ConfigDefaultTTLGet"
    ),
    pytest.param(
        ConfigDefaultTTLSet,
        bytes.fromhex('00'),
        {
            "TTL": 0x00
        },
        id="ConfigDefaultTTLSet - Min"
    ),
    pytest.param(
        ConfigDefaultTTLSet,
        bytes.fromhex('0B'),
        {
            "TTL": 0x0B
        },
        id="ConfigDefaultTTLSet"
    ),
    pytest.param(
        ConfigDefaultTTLSet,
        bytes.fromhex('7F'),
        {
            "TTL": 0x7F
        },
        id="ConfigDefaultTTLSet - Max"
    ),
    pytest.param(
        ConfigDefaultTTLStatus,
        bytes.fromhex('00'),
        {
            "TTL": 0x00
        },
        id="ConfigDefaultTTLStatus - Min"
    ),
    pytest.param(
        ConfigDefaultTTLStatus,
        bytes.fromhex('0B'),
        {
            "TTL": 0x0B
        },
        id="ConfigDefaultTTLStatus"
    ),
    pytest.param(
        ConfigDefaultTTLStatus,
        bytes.fromhex('7F'),
        {
            "TTL": 0x7F
        },
        id="ConfigDefaultTTLStatus - Max"
    ),
    pytest.param(
        ConfigGATTProxyGet,
        bytes(),
        {},
        id="ConfigGATTProxyGet"
    ),
    pytest.param(
        ConfigGATTProxySet,
        bytes.fromhex('00'),
        {
            "GATT_proxy": GATTProxy.DISABLED
        },
        id="ConfigGATTProxySet Disabled"
    ),
    pytest.param(
        ConfigGATTProxyStatus,
        bytes.fromhex('01'),
        {
            "GATT_proxy": GATTProxy.ENABLED
        },
        id="ConfigGATTProxyStatus Enabled"
    ),
    pytest.param(
        ConfigRelayGet,
        bytes(),
        {},
        id="ConfigRelayGet"
    ),
    pytest.param(
        ConfigRelaySet,
        bytes.fromhex('0000'),
        {
            "relay": Relay.DISABLED,
            "retransmit": {
                "count": 0x00,
                "interval": 10
            }
        },
        id="ConfigRelaySet"
    ),
    pytest.param(
        ConfigRelayStatus,
        bytes.fromhex('0200'),
        {
            "relay": Relay.NOT_SUPPORTED,
            "retransmit": {
                "count": 0x00,
                "interval": 10
            }
        },
        id="ConfigRelayStatus"
    ),
    pytest.param(
        ConfigModelPublicationGet,
        bytes.fromhex('0102 0304'),
        {
            "element_address": 0x0201,
            "model": {
                "model_id": 0x0403
            }
        },
        id="ConfigModelPublicationGet - SIG"
    ),
    pytest.param(
        ConfigModelPublicationGet,
        bytes.fromhex('010203040506'),
        {
            "element_address": 0x0201,
            "model": {
                "model_id": 0x0605,
                "vendor_id": 0x0403
            }
        },
        id="ConfigModelPublicationGet - Vendor"
    ),
    pytest.param(
        ConfigModelPublicationSet,
        bytes.fromhex('0102 0100 BC1A 7FC00703040506'),
        {
            "element_address": 0x0201,
            "publish_address": 0x0001,
            "RFU": 0,
            "credential_flag": PublishFriendshipCredentialsFlag.FRIENDSHIP_SECURITY,
            "app_key_index": 0xabc,
            "TTL": 0x7F,
            "publish_period": {
                "step_resolution": PublishPeriodStepResolution.RESOLUTION_10_MIN,
                "number_of_steps": 0x00
            },
            "retransmit": {
                "count": 0x07,
                "interval": 50
            },
            "model": {
                "model_id": 0x0605,
                "vendor_id": 0x0403
            }
        },
        id="ConfigModelPublicationSet"
    ),
    pytest.param(
        ConfigModelPublicationSet,
        bytes.fromhex('0201 0403 0500 0607110403'),
        {
            "element_address": 0x0102,
            "publish_address": 0x0304,
            "RFU": 0,
            "credential_flag": PublishFriendshipCredentialsFlag.MASTER_SECURITY,
            "app_key_index": 5,
            "TTL": 6,
            "publish_period": {
                "step_resolution": PublishPeriodStepResolution.RESOLUTION_100_MS,
                "number_of_steps": 7
            },
            "retransmit": {
                "count": 1,
                "interval": 150
            },
            "model": {
                "model_id": 0x0304
            }
        },
        id="ConfigModelPublicationSet"
    ),
    pytest.param(
        ConfigModelPublicationStatus,
        bytes.fromhex('02 0201 0403 0500 06 07 11 0403 0605'),
        {
            "status": StatusCode.INVALID_MODEL,
            "element_address": 0x0102,
            "publish_address": 0x0304,
            "RFU": 0,
            "credential_flag": PublishFriendshipCredentialsFlag.MASTER_SECURITY,
            "app_key_index": 5,
            "TTL": 6,
            "publish_period": {
                "step_resolution": PublishPeriodStepResolution.RESOLUTION_100_MS,
                "number_of_steps": 7
            },
            "retransmit": {
                "count": 1,
                "interval": 150
            },
            "model": {
                "model_id": 0x0506,
                "vendor_id": 0x0304
            }
        },
        id="ConfigModelPublicationStatus"
    ),
    pytest.param(
        ConfigModelSubscriptionAdd,
        bytes.fromhex('AA11 BBC2 CC33'),
        {
            "element_address": 0x11AA,
            "address": 0xC2BB,
            "model": {
                "model_id": 0x33CC
            }
        },
        id="ConfigModelSubscriptionAddSigId"
    ),
    pytest.param(
        ConfigModelSubscriptionAdd,
        bytes.fromhex('0201 FDFF 3F00 2A00'),
        {
            "element_address": 0x0102,
            "address": 0xFFFD,
            "model": {
                "model_id": 0x002A,
                "vendor_id": 0x003F
            }
        },
        id="ConfigModelSubscriptionAddVendorId"
    ),
    pytest.param(
        ConfigModelSubscriptionStatus,
        bytes.fromhex('00 AA11 0000 CC33'),
        {
            "status": StatusCode.SUCCESS,
            "element_address": 0x11AA,
            "address": 0,
            "model": {
                "model_id": 0x33CC
            }
        },
        id="ConfigModelSubscriptionStatus[UNASSIGNED]"
    ),
    pytest.param(
        ConfigModelSubscriptionStatus,
        bytes.fromhex('00 AA11 0080 CC33'),
        {
            "status": StatusCode.SUCCESS,
            "element_address": 0x11AA,
            "address": 0x8000,
            "model": {
                "model_id": 0x33CC
            }
        },
        id="ConfigModelSubscriptionStatus[VIRTUAL]"
    ),
    pytest.param(
        Struct(*SingleKeyIndex('key_index')),
        bytes.fromhex('bc0a'),
        {
            "key_index": 0xabc,
        },
        id="SingleKeyIndex"
    ),
    pytest.param(
        ConfigAppKeyAdd,
        bytes.fromhex('012345 000102030405060708090A0B0C0D0E0F'),
        {
            "net_key_index": 0x301,
            "app_key_index": 0x452,
            "app_key": bytes.fromhex('000102030405060708090A0B0C0D0E0F'),
        },
        id="ConfigAppKeyAdd"
    ),
    pytest.param(
        ConfigAppKeyAdd,
        bytes.fromhex('236145 63964771734fbd76e3b40519d1d94a48'),
        {
            "net_key_index": 0x123,
            "app_key_index": 0x456,
            "app_key": bytes.fromhex('63964771734fbd76e3b40519d1d94a48'),
        },
        id="ConfigAppKeyAdd"
    ),
    pytest.param(
        ConfigAppKeyGet,
        bytes.fromhex('0200'),
        {
            "net_key_index": 2,
        },
        id="ConfigAppKeyGet"
    ),
    pytest.param(
        ConfigAppKeyStatus,
        bytes.fromhex('00 332322'),
        {
            "status": StatusCode.SUCCESS,
            "net_key_index": 0x333,
            "app_key_index": 0x222
        },
        id="ConfigAppKeyStatus"
    ),
    pytest.param(
        ConfigAppKeyList,
        bytes.fromhex('000b00 010000 012100'),
        {
            "status": StatusCode.SUCCESS,
            "net_key_index": 11,
            "app_key_indices": [0, 1, 2, 257]
        },
        id="ConfigAppKeyList_even"
    ),
    pytest.param(
        ConfigAppKeyList,
        bytes.fromhex('000b00 563412 8907'),
        {
            "status": StatusCode.SUCCESS,
            "net_key_index": 11,
            "app_key_indices": [0x123, 0x456, 0x789]
        },
        id="ConfigAppKeyList_odd"
    ),
    pytest.param(
        ConfigNetKeyList,
        bytes.fromhex('42b000 '),
        {
            "net_key_indices": [11, 66],
        },
        id="ConfigNetKeyList_even"
    ),
    pytest.param(
        ConfigNetKeyAdd,
        bytes.fromhex('4305 000102030405060708090A0B0C0D0E0F'),
        {
            "net_key_index": 0x543,
            "net_key": bytes.fromhex('000102030405060708090A0B0C0D0E0F'),
        },
        id="ConfigNetKeyAdd"
    ),
    pytest.param(
        ConfigNetKeyList,
        bytes.fromhex('43d002 5800'),
        {
            "net_key_indices": [45, 67, 88],

        },
        id="ConfigNetKeyList_odd"
    ),
    pytest.param(
        ConfigNodeIdentitySet,
        bytes.fromhex('FF0F01'),
        {
            "net_key_index": 0xFFF,
            "identity": NodeIdentity.RUNNING
        },
        id="ConfigNodeIdentitySet"
    ),
    pytest.param(
        ConfigNodeIdentityStatus,
        bytes.fromhex('00FF0F01'),
        {
            "status": StatusCode.SUCCESS,
            "net_key_index": 0xFFF,
            "identity": NodeIdentity.RUNNING
        },
        id="ConfigNodeIdentityStatus"
    ),
    pytest.param(
        ConfigHeartbeatPublicationGet,
        bytes(),
        {},
        id="ConfigHeartbeatPublicationGet"
    ),
    pytest.param(
        ConfigHeartbeatPublicationSet,
        bytes.fromhex('010203040506070809'),
        {
            "destination": 0x0201,
            "count": 4,
            "period": 8,
            "TTL": 0x05,
            "features": {5, 6, 13, 14, 15},
            "net_key_index": 0x908,
        },
        id="ConfigHeartbeatPublicationSet"
    ),
    pytest.param(
        ConfigHeartbeatPublicationSet,
        bytes.fromhex('0102ff060506070809'),
        {
            "destination": 0x0201,
            "count": float('inf'),
            "period": 32,
            "TTL": 0x05,
            "features": {5, 6, 13, 14, 15},
            "net_key_index": 0x908,
        },
        id="ConfigHeartbeatPublicationSet - infinite count"
    ),
    pytest.param(
        ConfigHeartbeatPublicationSet,
        bytes.fromhex('0102ff100506070809'),
        {
            "destination": 0x0201,
            "count": float('inf'),
            "period": 0x8000,
            "TTL": 0x05,
            "features": {5, 6, 13, 14, 15},
            "net_key_index": 0x908,
        },
        id="ConfigHeartbeatPublicationSet - long period"
    ),
    pytest.param(
        ConfigNetworkTransmitSet,
        bytes.fromhex('f9'),
        {
            "count": 0x01,
            "interval": 320
        },
        id="ConfigNetworkTransmitSet"
    ),
    # fmt: on
]

build_valid = [
    # fmt: off
    pytest.param(
        CompositionDataElement,
        bytes.fromhex('00000101ADDEEFBEADDE'),
        {
            "location": GATTNamespaceDescriptor.UNKNOWN,
            "SIG_models": [{
                "model_id": 0xDEAD
            }],
            "vendor_models": [{
                "model_id": 0xDEAD,
                "vendor_id": 0xBEEF
            }]
        },
        id="CompositionDataElement (Vendor and SIG number not needed)"
    ),
    pytest.param(
        CompositionDataElement,
        bytes.fromhex('00000001EFBEADDE'),
        {
            "location": GATTNamespaceDescriptor.UNKNOWN,
            "SIG_models": [],
            "vendor_models": [{
                "model_id": 0xDEAD,
                "vendor_id": 0xBEEF
            }]
        },
        id="CompositionDataElement (Vendor and SIG number not needed) - No SIG"
    ),
    pytest.param(
        CompositionDataElement,
        bytes.fromhex('00000100ADDE'),
        {
            "location": GATTNamespaceDescriptor.UNKNOWN,
            "SIG_models": [{
                "model_id": 0xDEAD
            }],
            "vendor_models": []
        },
        id="CompositionDataElement (Vendor and SIG number not needed) - No vendor"
    ),
    # fmt: on
]

parse_invalid = [
    # fmt: off
    pytest.param(
        ConfigHeartbeatPublicationSet,
        bytes.fromhex('010203048006070809'),
        ValidationError,
        id="ConfigHeartbeatPublicationSet - TTL too big",
    ),
    pytest.param(
        ConfigHeartbeatPublicationSet,
        bytes.fromhex('010211040506070809'),
        ValidationError,
        id="ConfigHeartbeatPublicationSet - count too big",
    ),
    pytest.param(
        ConfigHeartbeatPublicationSet,
        bytes.fromhex('010203110506070809'),
        ValidationError,
        id="ConfigHeartbeatPublicationSet - period too long",
    ),
    # fmt: on
]

build_invalid = [
    # fmt: off
    pytest.param(
        ConfigHeartbeatPublicationSet,
        {
            "destination": 0x0201,
            "count": 1,
            "period": 0x8001,
            "TTL": 0x05,
            "features": {5, 6, 13, 14, 15},
            "net_key_index": 0x0908
        },
        ValidationError,
        id="ConfigHeartbeatPublicationSet - period too long",
    ),
    pytest.param(
        ConfigHeartbeatPublicationSet,
        {
            "destination": 0x0201,
            "count": 1,
            "period": float('inf'),
            "TTL": 0x05,
            "features": {5, 6, 13, 14, 15},
            "net_key_index": 0x0908
        },
        ValidationError,
        id="ConfigHeartbeatPublicationSet - infinite period",
    ),
    # fmt: on
]


@pytest.mark.parametrize("message,encoded,decoded", valid + build_valid)
def test_build(message, encoded, decoded):
    _decoded = deepcopy(decoded)
    result = message.build(obj=_decoded)
    assert result.hex() == encoded.hex()


@pytest.mark.parametrize("message,encoded,decoded", valid)
def test_parse(message, encoded, decoded):
    result = message.parse(data=encoded)
    assert result == decoded


@pytest.mark.parametrize("message,encoded,exception", parse_invalid)
def test_parse_invalid(message, encoded, exception):
    with pytest.raises(exception):
        message.parse(data=encoded)


@pytest.mark.parametrize("message,decoded,exception", build_invalid)
def test_build_invalid(message, decoded, exception):
    with pytest.raises(exception):
        message.build(obj=decoded)


def test_build_config_message():
    key = bytes.fromhex("deadbeef" * 4)

    data = ConfigMessage.build(
        dict(
            opcode=ConfigOpcode.APPKEY_ADD,
            params=dict(app_key_index=1, net_key_index=1, app_key=key,),
        )
    )

    assert data == bytes.fromhex("00011000") + key


def test_parse_config_message():
    key = bytes.fromhex("deadbeef" * 4)

    msg = ConfigMessage.parse(bytes.fromhex("00011000") + key)

    assert msg == dict(
        opcode=ConfigOpcode.APPKEY_ADD,
        params=dict(app_key_index=1, net_key_index=1, app_key=key,),
    )


invalid_retr = [
    # fmt: off
    pytest.param(
        NetworkRetransmit,
        bytes.fromhex('F8'),
        {
            "count": 0x00,
            "interval": 0
        },
        id="interval = 0"
    ),
    pytest.param(
        NetworkRetransmit,
        bytes.fromhex('F8'),
        {
            "count": 0x00,
            "interval": 5
        },
        id="interval = 5"
    ),
    pytest.param(
        NetworkRetransmit,
        bytes.fromhex('F8'),
        {
            "count": 0x00,
            "interval": 330
        },
        id="interval too high"
    ),
    pytest.param(
        PublishRetransmit,
        bytes.fromhex('F8'),
        {
            "count": 0x00,
            "interval": 1700
        },
        id="interval too high"
    ),
    pytest.param(
        PublishRetransmit,
        bytes.fromhex('F8'),
        {
            "count": 0x08,
            "interval": 700
        },
        id="count too high"
    ),
]


@pytest.mark.parametrize("message,encoded,decoded", invalid_retr)
def test_build(message, encoded, decoded):
    _decoded = deepcopy(decoded)
    with pytest.raises(AttributeError):
        message.build(obj=_decoded)

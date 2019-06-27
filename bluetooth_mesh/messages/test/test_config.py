import pytest
import construct

from bluetooth_mesh.messages.config import *


valid = [
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
        id="GATTNamespaceDescriptorAdapter - TWO_HUNDRED_TWENTIETH"
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
            "model_id" : 0xDEAD,
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
            "SIG_models": [{ "model_id": 0xDEAD }],
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
        NetAndAppKeyIndex,
        bytes.fromhex('012345'),
        {
            "net_key_index": 0x301,
            "app_key_index": 0x452
        },
        id="NetAndAppKeyIndex"
    ),
    pytest.param(
        NetAndAppKeyIndex,
        bytes.fromhex('abcdef'),
        {
            "net_key_index": 0xdab,
            "app_key_index": 0xefc
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
                "interval_steps": 0x00
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
                "interval_steps": 0x00
            }
        },
        id="ConfigRelayStatus"
    ),
    pytest.param(
        ConfigModelPublicationGet,
        bytes.fromhex('01020304'),
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
        bytes.fromhex('010201001FFF7FC00703040506'),
        {
            "element_address": 0x0201,
            "publish_address": 0x0001,
            "embedded": {
                "RFU": 0,
                "credential_flag": PublishFriendshipCredentialsFlag.FRIENDSHIP_SECURITY,
                "app_key_index": 0xFFF,
            },
            "TTL": 0x7F,
            "publish_period": {
                "step_resolution": PublishPeriodStepResolution.RESOLUTION_10_MIN,
                "number_of_steps": 0x00
            },
            "retransmit": {
                "count": 0x07,
                "interval_steps": 0x00
            },
            "model": {
                "model_id": 0x0605,
                "vendor_id": 0x0403
            }
        },
        id="ConfigModelPublicationSet"
    ),
    pytest.param(
        ConfigModelPublicationStatus,
        bytes.fromhex('010201001FFF7FC00703040506'),
        {
            "element_address": 0x0201,
            "publish_address": 0x0001,
            "embedded": {
                "RFU": 0,
                "credential_flag": PublishFriendshipCredentialsFlag.FRIENDSHIP_SECURITY,
                "app_key_index": 0xFFF,
            },
            "TTL": 0x7F,
            "publish_period": {
                "step_resolution": PublishPeriodStepResolution.RESOLUTION_10_MIN,
                "number_of_steps": 0x00
            },
            "retransmit": {
                "count": 0x07,
                "interval_steps": 0x00
            },
            "model": {
                "model_id": 0x0605,
                "vendor_id": 0x0403
            }
        },
        id="ConfigModelPublicationStatus"
    ),
    pytest.param(
        ConfigAppKeyAdd,
        bytes.fromhex('012345000102030405060708090A0B0C0D0E0F'),
        {
            "indexes":
                {
                    "net_key_index": 0x301,
                    "app_key_index": 0x452
                },
            "app_key": bytes.fromhex('000102030405060708090A0B0C0D0E0F'),
        },
        id="ConfigAppKeyAdd"
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
            "net_key_index": 0x0908
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
            "net_key_index": 0x0908
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
            "net_key_index": 0x0908
        },
        id="ConfigHeartbeatPublicationSet - long period"
    ),
]

build_valid = [
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
]

parse_invalid = [
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
]

build_invalid = [
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
]

@pytest.mark.parametrize("message,encoded,decoded", valid + build_valid)
def test_build(message, encoded, decoded):
    result = message.build(obj=decoded)
    assert result == encoded


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
    key = bytes.fromhex('deadbeef' * 4)

    data = ConfigMessage.build(dict(
        opcode=ConfigOpcode.APPKEY_ADD,
        params=dict(
            indexes=dict(
                app_key_index=1,
                net_key_index=1
            ),
            app_key=key,
        )
    ))

    assert data == bytes.fromhex('00011000') + key


def test_parse_config_message():
    key = bytes.fromhex('deadbeef' * 4)

    msg = ConfigMessage.parse(bytes.fromhex('00011000') + key)

    assert msg == dict(
        opcode=ConfigOpcode.APPKEY_ADD,
        params=dict(
            indexes=dict(
                app_key_index=1,
                net_key_index=1
            ),
            app_key=key,
        )
    )

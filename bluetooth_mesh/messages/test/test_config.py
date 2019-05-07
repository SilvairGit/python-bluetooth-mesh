import pytest
import construct

from bluetooth_mesh.messages.config import *


valid = [
    pytest.param(
        SecureNetworkBeaconAdapter,
        bytearray([0x00]),
        SecureNetworkBeacon.OFF,
        id="SecureNetworkBeaconAdapter - Off"
    ),
    pytest.param(
        SecureNetworkBeaconAdapter,
        bytearray([0x01]),
        SecureNetworkBeacon.ON,
        id="SecureNetworkBeaconAdapter - On"
    ),
    pytest.param(
        GATTProxyAdapter,
        bytearray([0x00]),
        GATTProxy.DISABLED,
        id="GATTProxyAdapter - Disabled"
    ),
    pytest.param(
        GATTProxyAdapter,
        bytearray([0x01]),
        GATTProxy.ENABLED,
        id="GATTProxyAdapter - Enabled"
    ),
    pytest.param(
        GATTProxyAdapter,
        bytearray([0x02]),
        GATTProxy.NOT_SUPPORTED,
        id="GATTProxyAdapter - NOT_SUPPORTED"
    ),
    pytest.param(
        RelayAdapter,
        bytearray([0x00]),
        Relay.DISABLED,
        id="RelayAdapter - Disabled"
    ),
    pytest.param(
        RelayAdapter,
        bytearray([0x01]),
        Relay.ENABLED,
        id="RelayAdapter - Enabled"
    ),
    pytest.param(
        RelayAdapter,
        bytearray([0x02]),
        Relay.NOT_SUPPORTED,
        id="RelayAdapter - NOT_SUPPORTED"
    ),
    pytest.param(
        GATTNamespaceDescriptorAdapter,
        bytearray([0xDC, 0x00]),
        GATTNamespaceDescriptor.TWO_HUNDRED_TWENTIETH,
        id="GATTNamespaceDescriptorAdapter - TWO_HUNDRED_TWENTIETH"
    ),
    pytest.param(
        GATTNamespaceDescriptorAdapter,
        bytearray([0x00, 0x00]),
        GATTNamespaceDescriptor.UNKNOWN,
        id="GATTNamespaceDescriptorAdapter - TWO_HUNDRED_TWENTIETH"
    ),
    pytest.param(
        TTL,
        bytearray([0x7F]),
        0x7F,
        id="TTL-Max"
    ),
    pytest.param(
        TTL,
        bytearray([0x6F]),
        0x6F,
        id="TTL"
    ),
    pytest.param(
        TTL,
        bytearray([0x00]),
        0x00,
        id="TTL-Min"
    ),
    pytest.param(
        SIGModelId,
        bytearray([0xAD, 0xDE]),
        {
            "model_id": 0xDEAD,
        },
        id="SIGModelId"
    ),
    pytest.param(
        SIGModelId,
        bytearray([0xAD, 0xDE]),
        {
            "model_id": 0xDEAD,
            "vendor_id": 0xC0DE
        },
        id="SIGModelId - accepts None vendor id"
    ),
    pytest.param(
        VendorModelId,
        bytearray([0xDE, 0xC0, 0xAD, 0xDE]),
        {
            "model_id" : 0xDEAD,
            "vendor_id": 0xC0DE
        },
        id="VendorModelId"
    ),
    pytest.param(
        ModelId,
        bytearray([0xDE, 0xC0, 0xAD, 0xDE]),
        {
            "model_id": 0xDEAD,
            "vendor_id": 0xC0DE
        },
        id="ModelId - vendor"
    ),
    pytest.param(
        ModelId,
        bytearray([0xAD, 0xDE]),
        {
            "model_id": 0xDEAD
        },
        id="ModelId - SIG"
    ),
    pytest.param(
        ModelId,
        bytearray([0xAD, 0xDE]),
        {
            "model_id": 0xDEAD,
            "vendor_id": None
        },
        id="ModelId - accepts None vendor id"
    ),
    pytest.param(
        UnassignedAddress,
        bytearray([0x00, 0x00]),
        0x0000,
        id="UnassignedAddress"
    ),
    pytest.param(
        UnicastAddress,
        bytearray([0xFF, 0x7F]),
        0x7FFF,
        id="UnicastAddress - Max"
    ),
    pytest.param(
        UnicastAddress,
        bytearray([0x01, 0x00]),
        0x0001,
        id="UnicastAddress - Min"
    ),
    pytest.param(
        GroupAddress,
        bytearray([0x00, 0xC0]),
        0xC000,
        id="GroupAddress - Min"
    ),
    pytest.param(
        VirtualLabel,
        bytearray([0x00, 0x80]),
        0x8000,
        id="VirtualAddress - Min"
    ),
    pytest.param(
        CompositionDataElement,
        bytearray([0x00, 0x00, 0x01, 0x01, 0xAD, 0xDE, 0xEF, 0xBE, 0xAD, 0xDE]),
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
        bytearray([0x00, 0x00, 0x00, 0x01, 0xEF, 0xBE, 0xAD, 0xDE]),
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
        bytearray([0x00, 0x00, 0x01, 0x00, 0xAD, 0xDE]),
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
        bytearray([0x36, 0x01, 0xCE, 0x00, 0xFE, 0xCA, 0xEF, 0xBE, 0x0B, 0xB0, 0x00, 0x00, 0x00, 0x00]),
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
        bytearray([0x36, 0x01, 0xCE, 0x00, 0xFE, 0xCA, 0xEF, 0xBE, 0x0B, 0xB0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
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
        bytearray([0x07]),
        {
            "count": 0x07,
            "interval_steps": 0x00
        },
        id="Retransmit - Max count"
    ),
    pytest.param(
        Retransmit,
        bytearray([0xF8]),
        {
            "count": 0x00,
            "interval_steps": 0x1F
        },
        id="Retransmit - Max steps"
    ),
    pytest.param(
        NetAndAppKeyIndex,
        bytearray([0x01, 0x23, 0x45]),
        {
            "net_key_index": 0x301,
            "app_key_index": 0x452
        },
        id="NetAndAppKeyIndex"
    ),
    pytest.param(
        NetAndAppKeyIndex,
        bytearray([0xab, 0xcd, 0xef]),
        {
            "net_key_index": 0xdab,
            "app_key_index": 0xefc
        },
        id="NetAndAppKeyIndex"
    ),
    pytest.param(
        PublishPeriod,
        bytearray([0x00]),
        {
            "step_resolution": PublishPeriodStepResolution.RESOLUTION_100_MS,
            "number_of_steps": 0x00
        },
        id="PublishPeriod"
    ),
    pytest.param(
        PublishPeriod,
        bytearray([0xC0]),
        {
            "step_resolution": PublishPeriodStepResolution.RESOLUTION_10_MIN,
            "number_of_steps": 0x00
        },
        id="PublishPeriod - Max resolution"
    ),
    pytest.param(
        PublishPeriod,
        bytearray([0x3F]),
        {
            "step_resolution": PublishPeriodStepResolution.RESOLUTION_100_MS,
            "number_of_steps": 0x3F
        },
        id="PublishPeriod - Max steps"
    ),
    pytest.param(
        ConfigBeaconGet,
        bytearray(),
        {},
        id="ConfigBeaconGet"
    ),
    pytest.param(
        ConfigBeaconSet,
        bytearray([0x00]),
        {
            "beacon": SecureNetworkBeacon.OFF
        },
        id="ConfigBeaconSet"
    ),
    pytest.param(
        ConfigBeaconStatus,
        bytearray([0x01]),
        {
            "beacon": SecureNetworkBeacon.ON
        },
        id="ConfigBeaconStatus-On"
    ),
    pytest.param(
        ConfigCompositionDataGet,
        bytearray([0x00]),
        {
            "page": 0x00
        },
        id="ConfigCompositionDataGet - Min page"
    ),
    pytest.param(
        ConfigCompositionDataGet,
        bytearray([0xFF]),
        {
            "page": 0xFF
        },
        id="ConfigCompositionDataGet - Max page"
    ),
    pytest.param(
        ConfigCompositionDataStatus,
        bytearray([0x00, 0x36, 0x01, 0xCE, 0x00, 0xFE, 0xCA, 0xEF, 0xBE, 0x0B, 0xB0, 0x00, 0x00, 0x00, 0x00]),
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
        bytearray([0x01, 0xCA, 0xFE]),
        {
            "page": 0x01,
            "data": bytearray([0xCA, 0xFE])
        },
        id="ConfigCompositionDataStatus - not page 0"
    ),
    pytest.param(
        ConfigDefaultTTLGet,
        bytearray(),
        {},
        id="ConfigDefaultTTLGet"
    ),
    pytest.param(
        ConfigDefaultTTLSet,
        bytearray([0x00]),
        {
            "TTL": 0x00
        },
        id="ConfigDefaultTTLSet - Min"
    ),
    pytest.param(
        ConfigDefaultTTLSet,
        bytearray([0x0B]),
        {
            "TTL": 0x0B
        },
        id="ConfigDefaultTTLSet"
    ),
    pytest.param(
        ConfigDefaultTTLSet,
        bytearray([0x7F]),
        {
            "TTL": 0x7F
        },
        id="ConfigDefaultTTLSet - Max"
    ),
    pytest.param(
        ConfigDefaultTTLStatus,
        bytearray([0x00]),
        {
            "TTL": 0x00
        },
        id="ConfigDefaultTTLStatus - Min"
    ),
    pytest.param(
        ConfigDefaultTTLStatus,
        bytearray([0x0B]),
        {
            "TTL": 0x0B
        },
        id="ConfigDefaultTTLStatus"
    ),
    pytest.param(
        ConfigDefaultTTLStatus,
        bytearray([0x7F]),
        {
            "TTL": 0x7F
        },
        id="ConfigDefaultTTLStatus - Max"
    ),
    pytest.param(
        ConfigGATTProxyGet,
        bytearray(),
        {},
        id="ConfigGATTProxyGet"
    ),
    pytest.param(
        ConfigGATTProxySet,
        bytearray([0x00]),
        {
            "GATT_proxy": GATTProxy.DISABLED
        },
        id="ConfigGATTProxySet Disabled"
    ),
    pytest.param(
        ConfigGATTProxyStatus,
        bytearray([0x01]),
        {
            "GATT_proxy": GATTProxy.ENABLED
        },
        id="ConfigGATTProxyStatus Enabled"
    ),
    pytest.param(
        ConfigRelayGet,
        bytearray(),
        {},
        id="ConfigRelayGet"
    ),
    pytest.param(
        ConfigRelaySet,
        bytearray([0x00, 0x00]),
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
        bytearray([0x02, 0x00]),
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
        bytearray([0x01, 0x02, 0x03, 0x04]),
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
        bytearray([0x01, 0x02, 0x03, 0x04, 0x05, 0x06]),
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
        bytearray([0x01, 0x02, 0x01, 0x00, 0x1F, 0xFF, 0x7F, 0xC0, 0x07, 0x03, 0x04, 0x05, 0x06]),
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
        bytearray([0x01, 0x02, 0x01, 0x00, 0x1F, 0xFF, 0x7F, 0xC0, 0x07, 0x03, 0x04, 0x05, 0x06]),
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
        bytes([0x01, 0x23, 0x45, 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F]),
        {
            "indexes":
                {
                    "net_key_index": 0x301,
                    "app_key_index": 0x452
                },
            "app_key": bytes([0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F]),
        },
        id="ConfigAppKeyAdd"
    ),
    pytest.param(
        ConfigNodeIdentitySet,
        bytearray([0xFF, 0x0F, 0x01]),
        {
            "net_key_index": 0xFFF,
            "identity": NodeIdentity.RUNNING
        },
        id="ConfigNodeIdentitySet"
    ),
    pytest.param(
        ConfigNodeIdentityStatus,
        bytearray([0x00, 0xFF, 0x0F, 0x01]),
        {
            "status": StatusCode.SUCCESS,
            "net_key_index": 0xFFF,
            "identity": NodeIdentity.RUNNING
        },
        id="ConfigNodeIdentityStatus"
    ),
]

build_valid = [
    pytest.param(
        CompositionDataElement,
        bytearray([0x00, 0x00, 0x01, 0x01, 0xAD, 0xDE, 0xEF, 0xBE, 0xAD, 0xDE]),
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
        bytearray([0x00, 0x00, 0x00, 0x01, 0xEF, 0xBE, 0xAD, 0xDE]),
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
        bytearray([0x00, 0x00, 0x01, 0x00, 0xAD, 0xDE]),
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
]

build_invalid = [
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

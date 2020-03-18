import enum

from construct import (
    Adapter, Select, Embedded, Rebuild,
    BitStruct, Struct, Switch,
    GreedyBytes, GreedyRange,
    BitsInteger, Int24ul, Int16ul, Int8ul, Flag, Bytes,
    ExprValidator, ValidationError,
    this, len_, obj_, Padding
)

from .util import (
    EnumAdapter, LogAdapter, BitList, Opcode, Reversed, RangeValidator,
    EmbeddedBitStruct
)


class SecureNetworkBeacon(enum.IntEnum):
    OFF = 0x00
    ON = 0x01


class GATTProxy(enum.IntEnum):
    DISABLED = 0x00
    ENABLED = 0x01
    NOT_SUPPORTED = 0x02


class Relay(enum.IntEnum):
    DISABLED = 0x00
    ENABLED = 0x01
    NOT_SUPPORTED = 0x02


class GATTNamespaceDescriptor(enum.IntEnum):
    AUXILIARY = 0x0108
    BACK = 0x0101
    BACKUP = 0x0107
    BOTTOM = 0x0103
    EIGHTEENTH = 0x0012
    EIGHTH = 0x0008
    EIGHTIETH = 0x0050
    EIGHTY_EIGHTH = 0x0058
    EIGHTY_FIFTH = 0x0055
    EIGHTY_FIRST = 0x0051
    EIGHTY_FOURTH = 0x0054
    EIGHTY_NINTH = 0x0059
    EIGHTY_SECOND = 0x0052
    EIGHTY_SEVENTH = 0x0057
    EIGHTY_SIXTH = 0x0056
    EIGHTY_THIRD = 0x0053
    ELEVENTH = 0x000b
    EXTERNAL = 0x0110
    FIFTEENTH = 0x000f
    FIFTH = 0x0005
    FIFTIETH = 0x0032
    FIFTY_EIGHTH = 0x003a
    FIFTY_FIFTH = 0x0037
    FIFTY_FIRST = 0x0033
    FIFTY_FOURTH = 0x0036
    FIFTY_NINTH = 0x003b
    FIFTY_SECOND = 0x0034
    FIFTY_SEVENTH = 0x0039
    FIFTY_SIXTH = 0x0038
    FIFTY_THIRD = 0x0035
    FIRST = 0x0001
    FLASH = 0x010A
    FORTIETH = 0x0028
    FOURTEENTH = 0x000e
    FOURTH = 0x0004
    FORTY_EIGHTH = 0x0030
    FORTY_FIFTH = 0x002d
    FORTY_FIRST = 0x0029
    FORTY_FOURTH = 0x002c
    FORTY_NINTH = 0x0031
    FORTY_SECOND = 0x002a
    FORTY_SEVENTH = 0x002f
    FORTY_SIXTH = 0x002e
    FORTY_THIRD = 0x002b
    FRONT = 0x0100
    INSIDE = 0x010B
    INTERNAL = 0x010F
    LEFT = 0x010D
    LOWER = 0x0105
    MAIN = 0x0106
    NINETEENTH = 0x0013
    NINTH = 0x0009
    NINETIETH = 0x005a
    NINETY_EIGHTH = 0x0062
    NINETY_FIFTH = 0x005f
    NINETY_FIRST = 0x005b
    NINETY_FOURTH = 0x005e
    NINETY_NINTH = 0x0063
    NINETY_SECOND = 0x005c
    NINETY_SEVENTH = 0x0061
    NINETY_SIXTH = 0x0060
    NINETY_THIRD = 0x005d
    ONE_HUNDRED_AND_EIGHTEENTH = 0x0076
    ONE_HUNDRED_AND_EIGHTH = 0x006c
    ONE_HUNDRED_AND_EIGHTY_EIGHTH = 0x00bc
    ONE_HUNDRED_AND_EIGHTY_FIFTH = 0x00b9
    ONE_HUNDRED_AND_EIGHTY_FIRST = 0x00b5
    ONE_HUNDRED_AND_EIGHTY_FOURTH = 0x00b8
    ONE_HUNDRED_AND_EIGHTY_NINTH = 0x00bd
    ONE_HUNDRED_AND_EIGHTY_SECOND = 0x00b6
    ONE_HUNDRED_AND_EIGHTY_SEVENTH = 0x00bb
    ONE_HUNDRED_AND_EIGHTY_SIXTH = 0x00ba
    ONE_HUNDRED_AND_EIGHTY_THIRD = 0x00b7
    ONE_HUNDRED_AND_ELEVENTH = 0x006f
    ONE_HUNDRED_AND_FIFTEENTH = 0x0073
    ONE_HUNDRED_AND_FIFTH = 0x0069
    ONE_HUNDRED_AND_FIFTY_EIGHTH = 0x009e
    ONE_HUNDRED_AND_FIFTY_FIFTH = 0x009b
    ONE_HUNDRED_AND_FIFTY_FIRST = 0x0097
    ONE_HUNDRED_AND_FIFTY_FOURTH = 0x009a
    ONE_HUNDRED_AND_FIFTY_NINTH = 0x009f
    ONE_HUNDRED_AND_FIFTY_SECOND = 0x0098
    ONE_HUNDRED_AND_FIFTY_SEVENTH = 0x009d
    ONE_HUNDRED_AND_FIFTY_SIXTH = 0x009c
    ONE_HUNDRED_AND_FIFTY_THIRD = 0x0099
    ONE_HUNDRED_AND_FIRST = 0x0065
    ONE_HUNDRED_AND_FOURTEENTH = 0x0072
    ONE_HUNDRED_AND_FOURTH = 0x0068
    ONE_HUNDRED_AND_FORTY_EIGHTH = 0x0094
    ONE_HUNDRED_AND_FORTY_FIFTH = 0x0091
    ONE_HUNDRED_AND_FORTY_FIRST = 0x008d
    ONE_HUNDRED_AND_FORTY_FOURTH = 0x0090
    ONE_HUNDRED_AND_FORTY_NINTH = 0x0095
    ONE_HUNDRED_AND_FORTY_SECOND = 0x008e
    ONE_HUNDRED_AND_FORTY_SEVENTH = 0x0093
    ONE_HUNDRED_AND_FORTY_SIXTH = 0x0092
    ONE_HUNDRED_AND_FORTY_THIRD = 0x008f
    ONE_HUNDRED_AND_NINETEENTH = 0x0077
    ONE_HUNDRED_AND_NINTH = 0x006d
    ONE_HUNDRED_AND_NINETY_EIGHTH = 0x00c6
    ONE_HUNDRED_AND_NINETY_FIFTH = 0x00c3
    ONE_HUNDRED_AND_NINETY_FIRST = 0x00bf
    ONE_HUNDRED_AND_NINETY_FOURTH = 0x00c2
    ONE_HUNDRED_AND_NINETY_NINTH = 0x00c7
    ONE_HUNDRED_AND_NINETY_SECOND = 0x00c0
    ONE_HUNDRED_AND_NINETY_SEVENTH = 0x00c5
    ONE_HUNDRED_AND_NINETY_SIXTH = 0x00c4
    ONE_HUNDRED_AND_NINETY_THIRD = 0x00c1
    ONE_HUNDRED_AND_SECOND = 0x0066
    ONE_HUNDRED_AND_SEVENTEENTH = 0x0075
    ONE_HUNDRED_AND_SEVENTH = 0x006b
    ONE_HUNDRED_AND_SEVENTY_EIGHTH = 0x00b2
    ONE_HUNDRED_AND_SEVENTY_FIFTH = 0x00af
    ONE_HUNDRED_AND_SEVENTY_FIRST = 0x00ab
    ONE_HUNDRED_AND_SEVENTY_FOURTH = 0x00ae
    ONE_HUNDRED_AND_SEVENTY_NINTH = 0x00b3
    ONE_HUNDRED_AND_SEVENTY_SECOND = 0x00ac
    ONE_HUNDRED_AND_SEVENTY_SEVENTH = 0x00b1
    ONE_HUNDRED_AND_SEVENTY_SIXTH = 0x00b0
    ONE_HUNDRED_AND_SEVENTY_THIRD = 0x00ad
    ONE_HUNDRED_AND_SIXTEENTH = 0x0074
    ONE_HUNDRED_AND_SIXTH = 0x006a
    ONE_HUNDRED_AND_SIXTY_EIGHTH = 0x00a8
    ONE_HUNDRED_AND_SIXTY_FIFTH = 0x00a5
    ONE_HUNDRED_AND_SIXTY_FIRST = 0x00a1
    ONE_HUNDRED_AND_SIXTY_FOURTH = 0x00a4
    ONE_HUNDRED_AND_SIXTY_NINTH = 0x00a9
    ONE_HUNDRED_AND_SIXTY_SECOND = 0x00a2
    ONE_HUNDRED_AND_SIXTY_SEVENTH = 0x00a7
    ONE_HUNDRED_AND_SIXTY_SIXTH = 0x00a6
    ONE_HUNDRED_AND_SIXTY_THIRD = 0x00a3
    ONE_HUNDRED_AND_TENTH = 0x006e
    ONE_HUNDRED_AND_THIRD = 0x0067
    ONE_HUNDRED_AND_THIRTEENTH = 0x0071
    ONE_HUNDRED_AND_THIRTY_EIGHTH = 0x008a
    ONE_HUNDRED_AND_THIRTY_FIFTH = 0x0087
    ONE_HUNDRED_AND_THIRTY_FIRST = 0x0083
    ONE_HUNDRED_AND_THIRTY_FOURTH = 0x0086
    ONE_HUNDRED_AND_THIRTY_NINTH = 0x008b
    ONE_HUNDRED_AND_THIRTY_SECOND = 0x0084
    ONE_HUNDRED_AND_THIRTY_SEVENTH = 0x0089
    ONE_HUNDRED_AND_THIRTY_SIXTH = 0x0088
    ONE_HUNDRED_AND_THIRTY_THIRD = 0x0085
    ONE_HUNDRED_AND_TWELVETH = 0x0070
    ONE_HUNDRED_AND_TWENTY_EIGHTH = 0x0080
    ONE_HUNDRED_AND_TWENTY_FIFTH = 0x007d
    ONE_HUNDRED_AND_TWENTY_FIRST = 0x0079
    ONE_HUNDRED_AND_TWENTY_FOURTH = 0x007c
    ONE_HUNDRED_AND_TWENTY_NINTH = 0x0081
    ONE_HUNDRED_AND_TWENTY_SECOND = 0x007a
    ONE_HUNDRED_AND_TWENTY_SEVENTH = 0x007f
    ONE_HUNDRED_AND_TWENTY_SIXTH = 0x007e
    ONE_HUNDRED_AND_TWENTY_THIRD = 0x007b
    ONE_HUNDRED_EIGHTIETH = 0x00b4
    ONE_HUNDRED_FIFTIETH = 0x0096
    ONE_HUNDRED_FORTIETH = 0x008c
    ONE_HUNDRED_NINETIETH = 0x00be
    ONE_HUNDRED_SEVENTIETH = 0x00aa
    ONE_HUNDRED_SIXTIETH = 0x00a0
    ONE_HUNDRED_THIRTIETH = 0x0082
    ONE_HUNDRED_TWENTIETH = 0x0078
    ONE_HUNDREDTH = 0x0064
    OUTSIDE = 0x010C
    RIGHT = 0x010E
    SECOND = 0x0002
    SEVENTEENTH = 0x0011
    SEVENTH = 0x0007
    SEVENTIETH = 0x0046
    SEVENTY_EIGHTH = 0x004e
    SEVENTY_FIFTH = 0x004b
    SEVENTY_FIRST = 0x0047
    SEVENTY_FOURTH = 0x004a
    SEVENTY_NINTH = 0x004f
    SEVENTY_SECOND = 0x0048
    SEVENTY_SEVENTH = 0x004d
    SEVENTY_SIXTH = 0x004c
    SEVENTY_THIRD = 0x0049
    SIXTEENTH = 0x0010
    SIXTH = 0x0006
    SIXTIETH = 0x003c
    SIXTY_EIGHTH = 0x0044
    SIXTY_FIFTH = 0x0041
    SIXTY_FIRST = 0x003d
    SIXTY_FOURTH = 0x0040
    SIXTY_NINTH = 0x0045
    SIXTY_SECOND = 0x003e
    SIXTY_SEVENTH = 0x0043
    SIXTY_SIXTH = 0x0042
    SIXTY_THIRD = 0x003f
    SUPPLEMENTARY = 0x0109
    TENTH = 0x000a
    THIRD = 0x0003
    THIRTEENTH = 0x000d
    THIRTIETH = 0x001e
    THIRTY_EIGHTH = 0x0026
    THIRTY_FIFTH = 0x0023
    THIRTY_FIRST = 0x001f
    THIRTY_FOURTH = 0x0022
    THIRTY_NINTH = 0x0027
    THIRTY_SECOND = 0x0020
    THIRTY_SEVENTH = 0x0025
    THIRTY_SIXTH = 0x0024
    THIRTY_THIRD = 0x0021
    TOP = 0x0102
    TWELVETH = 0x000c
    TWENTIETH = 0x0014
    TWENTY_EIGHTH = 0x001c
    TWENTY_FIFTH = 0x0019
    TWENTY_FIRST = 0x0015
    TWENTY_FOURTH = 0x0018
    TWENTY_NINTH = 0x001d
    TWENTY_SECOND = 0x0016
    TWENTY_SEVENTH = 0x001b
    TWENTY_SIXTH = 0x001a
    TWENTY_THIRD = 0x0017
    TWO_HUNDRED_AND_EIGHTEENTH = 0x00da
    TWO_HUNDRED_AND_EIGHTH = 0x00d0
    TWO_HUNDRED_AND_ELEVENTH = 0x00d3
    TWO_HUNDRED_AND_FIFTEENTH = 0x00d7
    TWO_HUNDRED_AND_FIFTH = 0x00cd
    TWO_HUNDRED_AND_FIFTY_FIFTH = 0x00ff
    TWO_HUNDRED_AND_FIFTY_FIRST = 0x00fb
    TWO_HUNDRED_AND_FIFTY_FOURTH = 0x00fe
    TWO_HUNDRED_AND_FIFTY_SECOND = 0x00fc
    TWO_HUNDRED_AND_FIFTY_THIRD = 0x00fd
    TWO_HUNDRED_AND_FIRST = 0x00c9
    TWO_HUNDRED_AND_FOURTEENTH = 0x00d6
    TWO_HUNDRED_AND_FOURTH = 0x00cc
    TWO_HUNDRED_AND_FORTY_EIGHTH = 0x00f8
    TWO_HUNDRED_AND_FORTY_FIFTH = 0x00f5
    TWO_HUNDRED_AND_FORTY_FIRST = 0x00f1
    TWO_HUNDRED_AND_FORTY_FOURTH = 0x00f4
    TWO_HUNDRED_AND_FORTY_NINTH = 0x00f9
    TWO_HUNDRED_AND_FORTY_SECOND = 0x00f2
    TWO_HUNDRED_AND_FORTY_SEVENTH = 0x00f7
    TWO_HUNDRED_AND_FORTY_SIXTH = 0x00f6
    TWO_HUNDRED_AND_FORTY_THIRD = 0x00f3
    TWO_HUNDRED_AND_NINETEENTH = 0x00db
    TWO_HUNDRED_AND_NINTH = 0x00d1
    TWO_HUNDRED_AND_SECOND = 0x00ca
    TWO_HUNDRED_AND_SEVENTEENTH = 0x00d9
    TWO_HUNDRED_AND_SEVENTH = 0x00cf
    TWO_HUNDRED_AND_SIXTEENTH = 0x00d8
    TWO_HUNDRED_AND_SIXTH = 0x00ce
    TWO_HUNDRED_AND_TENTH = 0x00d2
    TWO_HUNDRED_AND_THIRD = 0x00cb
    TWO_HUNDRED_AND_THIRTEENTH = 0x00d5
    TWO_HUNDRED_AND_THIRTY_EIGHTH = 0x00ee
    TWO_HUNDRED_AND_THIRTY_FIFTH = 0x00eb
    TWO_HUNDRED_AND_THIRTY_FIRST = 0x00e7
    TWO_HUNDRED_AND_THIRTY_FOURTH = 0x00ea
    TWO_HUNDRED_AND_THIRTY_NINTH = 0x00ef
    TWO_HUNDRED_AND_THIRTY_SECOND = 0x00e8
    TWO_HUNDRED_AND_THIRTY_SEVENTH = 0x00ed
    TWO_HUNDRED_AND_THIRTY_SIXTH = 0x00ec
    TWO_HUNDRED_AND_THIRTY_THIRD = 0x00e9
    TWO_HUNDRED_AND_TWELVETH = 0x00d4
    TWO_HUNDRED_AND_TWENTY_EIGHTH = 0x00e4
    TWO_HUNDRED_AND_TWENTY_FIFTH = 0x00e1
    TWO_HUNDRED_AND_TWENTY_FIRST = 0x00dd
    TWO_HUNDRED_AND_TWENTY_FOURTH = 0x00e0
    TWO_HUNDRED_AND_TWENTY_NINTH = 0x00e5
    TWO_HUNDRED_AND_TWENTY_SECOND = 0x00de
    TWO_HUNDRED_AND_TWENTY_SEVENTH = 0x00e3
    TWO_HUNDRED_AND_TWENTY_SIXTH = 0x00e2
    TWO_HUNDRED_AND_TWENTY_THIRD = 0x00df
    TWO_HUNDRED_FIFTIETH = 0x00fa
    TWO_HUNDRED_FORTIETH = 0x00f0
    TWO_HUNDRED_THIRTIETH = 0x00e6
    TWO_HUNDRED_TWENTIETH = 0x00dc
    TWO_HUNDREDTH = 0x00c8
    UNKNOWN = 0x0000
    UPPER = 0x0104


class PublishFriendshipCredentialsFlag(enum.IntEnum):
    MASTER_SECURITY = 0x00
    FRIENDSHIP_SECURITY = 0x01


class StatusCode(enum.IntEnum):
    SUCCESS = 0x00
    INVALID_ADDRESS = 0x01
    INVALID_MODEL = 0x02
    INVALID_APPKEY_INDEX = 0x03
    INVALID_NETKEY_INDEX = 0x04
    INSUFFICIENT_RESOURCES = 0x05
    KEY_INDEX_ALREADY_STORED = 0x06
    INVALID_PUBLISH_PARAMETERS = 0x07
    NOT_A_SUBSCRIBE_MODEL = 0x08
    STORAGE_FAILURE = 0x09
    FEATURE_NOT_SUPPORTED = 0x0A
    CANNOT_UPDATE = 0x0B
    CANNOT_REMOVE = 0x0C
    CANNOT_BIND = 0x0D
    TEMPORARILY_UNABLE_TO_CHANGE_STATE = 0x0E
    CANNOT_SET = 0x0F
    UNSPECIFIED_ERROR = 0x10
    INVALID_BINDING = 0x11


class NodeIdentity(enum.IntEnum):
    STOPPED = 0x00
    RUNNING = 0x01
    NOT_SUPPORTED = 0x02


class Friend(enum.IntEnum):
    DISABLED = 0x00
    ENABLED = 0x01
    NOT_SUPPORTED = 0x02


class KeyRefreshPhase(enum.IntEnum):
    NORMAL = 0x00
    FIRST = 0x01
    SECOND = 0x02


class KeyRefreshTransition(enum.IntEnum):
    SECOND = 0x02
    THIRD = 0x03


SecureNetworkBeaconAdapter = EnumAdapter(Int8ul, SecureNetworkBeacon)

GATTProxyAdapter = EnumAdapter(Int8ul, GATTProxy)

RelayAdapter = EnumAdapter(Int8ul, Relay)

GATTNamespaceDescriptorAdapter = EnumAdapter(Int16ul, GATTNamespaceDescriptor)

PublishFriendshipCredentialsFlagAdapter = EnumAdapter(Flag, PublishFriendshipCredentialsFlag)

StatusCodeAdapter = EnumAdapter(Int8ul, StatusCode)

NodeIdentityAdapter = EnumAdapter(Int8ul, NodeIdentity)

FriendAdapter = EnumAdapter(Int8ul, Friend)

TTL = RangeValidator(Int8ul, max_value=0x7F)

SIGModelId = Struct(
    "model_id" / Int16ul,
)

VendorModelId = Struct(
    "vendor_id" / Int16ul,
    "model_id" / Int16ul,
)

ModelId = Select(
    VendorModelId,
    SIGModelId
)


class AddressType(enum.Enum):
    UNASSIGNED = 0
    UNICAST = 1
    GROUP = 2
    VIRTUAL = 3
    RFU = 4
    ALL_PROXIES = 5
    ALL_FRIENDS = 6
    ALL_RELAYS = 7
    ALL_NODES = 8


def get_address_type(address):
    if address == 0x0000:
        return AddressType.UNASSIGNED

    if 0xFF00 <= address <= 0xFFFB:
        return AddressType.RFU

    if address == 0xFFFC:
        return AddressType.ALL_PROXIES

    if address == 0xFFFD:
        return AddressType.ALL_FRIENDS

    if address == 0xFFFE:
        return AddressType.ALL_RELAYS

    if address == 0xFFFF:
        return AddressType.ALL_NODES

    if (address & 0xC000) == 0xC000:
        return AddressType.GROUP

    if (address & 0x8000) == 0x8000:
        return AddressType.VIRTUAL

    return AddressType.UNICAST


def AddressTypeValidator(subcons, *allowed_types):
    return ExprValidator(
        subcons,
        lambda obj, ctx: get_address_type(obj) in allowed_types
    )


UnassignedAddress = AddressTypeValidator(
    Int16ul,
    AddressType.UNASSIGNED
)

UnicastAddress = AddressTypeValidator(
    Int16ul,
    AddressType.UNICAST
)

# TODO Fixed Groups?
GroupAddress = AddressTypeValidator(
    Int16ul, AddressType.GROUP
)

VirtualLabel = AddressTypeValidator(
    Int16ul,
    AddressType.VIRTUAL
)

NotVirtualLabel = ExprValidator(
    Int16ul,
    lambda obj, ctx: get_address_type(obj) != AddressType.VIRTUAL
)

SubscriptionAddress = ExprValidator(
    Int16ul,
    lambda obj, ctx: get_address_type(obj) not in [AddressType.UNASSIGNED,
                                                   AddressType.UNICAST,
                                                   AddressType.ALL_NODES,
                                                   AddressType.VIRTUAL]
)

StatusSubscriptionAddress = ExprValidator(
    Int16ul,
    lambda obj, ctx: get_address_type(obj) not in [AddressType.UNICAST,
                                                   AddressType.ALL_NODES]
)

UnicastUnassignedAddress = AddressTypeValidator(
    Int16ul,
    AddressType.UNICAST,
    AddressType.UNASSIGNED,
)

UnicastUnassignedGroupAddress = AddressTypeValidator(
    Int16ul,
    AddressType.UNICAST,
    AddressType.UNASSIGNED,
    AddressType.GROUP,
)

Int12ul = ExprValidator(
    Int16ul,
    (obj_ & 0xF000) == 0x00
)

CompositionDataElement = Struct(
    "location" / GATTNamespaceDescriptorAdapter,
    "SIG_number" / Rebuild(Int8ul, len_(this["SIG_models"])),
    "vendor_number" / Rebuild(Int8ul, len_(this["vendor_models"])),
    "SIG_models" / SIGModelId[this["SIG_number"]],
    "vendor_models" / VendorModelId[this["vendor_number"]],
)

CompositionData = Struct(
    "CID" / Int16ul,
    "PID" / Int16ul,
    "VID" / Int16ul,
    "CRPL" / Int16ul,
    "features" / Int16ul,  # TODO should be parsed
    "elements" / GreedyRange(CompositionDataElement),
)

Retransmit = BitStruct(
    # sssssccc
    "interval_steps" / BitsInteger(5),
    "count" / BitsInteger(3),
)


class RetransmitAdapter(Adapter):
    def __init__(self, subcon, interval):
        self.interval = interval
        self.subcon = subcon
        super(RetransmitAdapter, self).__init__(subcon)

    def _decode(self, obj, context, path):
        return dict(count=obj['count'], interval=(obj['interval_steps']+1)*self.interval)

    def _encode(self, obj, context, path):
        return dict(count=obj['count'], interval_steps=int(round((obj['interval']/self.interval)-1)))


NetworkRetransmit = RetransmitAdapter(Retransmit, 10)  # (Network Retransmit Interval Steps + 1) * 10ms

RelayRetransmit = NetworkRetransmit  # (Relay Retransmit Interval Steps + 1) * 10ms

PublishRetransmit = RetransmitAdapter(Retransmit, 50)  # (Publish Retransmit Interval Steps + 1) * 50ms


def DoubleKeyIndex(first, second):
    return EmbeddedBitStruct(
        "_",
        second / BitsInteger(12),
        first / BitsInteger(12),
        reversed=True
    )


def SingleKeyIndex(name):
    return EmbeddedBitStruct(
        "_",
        Padding(4),
        name / BitsInteger(12),
        reversed=True
    )


NetAndAppKeyIndex = DoubleKeyIndex("net_key_index", "app_key_index")

AppKeyIndex = SingleKeyIndex("app_key_index")

NetKeyIndex = SingleKeyIndex("net_key_index")


class KeyIndicesAdapter(Adapter):
    def _decode(self, obj, context, path):
        """
        Flatten a list dictionaries into list of items:
            [{first=1, second=2}, {last=3}] -> [1, 2, 3]
        """
        ret = []
        for item in obj:
            if 'last' in item:
                ret += [item['last']]
            else:
                ret += [item['first'], item['second']]
        return sorted(ret)

    def _encode(self, obj, context, path):
        """
        Expand a list into list of dictionaries:
            [1, 2, 3] -> [{first=1, second=2}, {last=3}]
        """
        ret = []
        obj.sort()
        while len(obj) > 1:
            ret += [dict(first=obj.pop(0), second=obj.pop(0))]

        if obj:
            ret += [dict(last=obj.pop())]

        return ret


KeyIndices = KeyIndicesAdapter(
    GreedyRange(
        Select(
            Reversed(
                BitStruct(
                    "first" / BitsInteger(12),
                    "second" / BitsInteger(12),
                )
            ),
            Reversed(
                BitStruct(
                    Padding(4),
                    "last" / BitsInteger(12),
                )
            )
        )
    )
)
KeyIndices.__construct_doc__ = GreedyRange(BitsInteger(12))


class PublishPeriodStepResolution(enum.IntEnum):
    RESOLUTION_100_MS = 0x0
    RESOLUTION_1_S = 0x1
    RESOLUTION_10_S = 0x2
    RESOLUTION_10_MIN = 0x3


PublishPeriodStepResolutionAdapter = EnumAdapter(
    BitsInteger(2),
    PublishPeriodStepResolution
)

PublishPeriod = BitStruct(
    "step_resolution" / PublishPeriodStepResolutionAdapter,
    "number_of_steps" / BitsInteger(6),
)

ConfigBeaconGet = Struct()

ConfigBeaconSet = Struct(
    "beacon" / SecureNetworkBeaconAdapter,
)

ConfigBeaconStatus = ConfigBeaconSet

ConfigCompositionDataGet = Struct(
    "page" / Int8ul,
)

ConfigCompositionDataStatus = Struct(
    "page" / Int8ul,
    "data" / Switch(
        this.page,
        {
            0: CompositionData,
        },
        default=GreedyBytes
    ),
)

ConfigDefaultTTLGet = Struct()

ConfigDefaultTTLSet = Struct(
    "TTL" / TTL,
)

ConfigDefaultTTLStatus = ConfigDefaultTTLSet

ConfigGATTProxyGet = Struct()

ConfigGATTProxySet = Struct(
    "GATT_proxy" / GATTProxyAdapter,
)

ConfigGATTProxyStatus = ConfigGATTProxySet

ConfigRelayGet = Struct()

ConfigRelaySet = Struct(
    "relay" / RelayAdapter,
    "retransmit" / RelayRetransmit,
)

ConfigRelayStatus = ConfigRelaySet

ConfigModelPublicationGet = Struct(
    "element_address" / UnicastAddress,
    "model" / ModelId,
)

ConfigModelPublicationSet = Struct(
    "element_address" / UnicastAddress,
    "publish_address" / NotVirtualLabel,
    *EmbeddedBitStruct(
        "_",
        "RFU" / BitsInteger(3),
        "credential_flag" / PublishFriendshipCredentialsFlagAdapter,
        "app_key_index" / BitsInteger(12),
        reversed=True
    ),
    "TTL" / TTL,
    "publish_period" / PublishPeriod,
    "retransmit" / PublishRetransmit,
    "model" / ModelId,
)

ConfigModelPublicationStatus = Struct(
    "status" / StatusCodeAdapter,
    Embedded(ConfigModelPublicationSet)
)

ConfigModelPublicationVASet = Struct(
    "element_address" / UnicastAddress,
    "publish_address" / Bytes(16),
    *EmbeddedBitStruct(
        "_",
        "RFU" / BitsInteger(3),
        "credential_flag" / PublishFriendshipCredentialsFlagAdapter,
        "app_key_index" / BitsInteger(12),
        reversed=True
    ),
    "TTL" / TTL,
    "publish_period" / PublishPeriod,
    "retransmit" / PublishRetransmit,
    "model" / ModelId,
)

ConfigModelSubscriptionAdd = Struct(
    "element_address" / UnicastAddress,
    "address" / SubscriptionAddress,
    "model" / ModelId,
)

ConfigModelSubscriptionDelete = ConfigModelSubscriptionAdd
ConfigModelSubscriptionOverwrite = ConfigModelSubscriptionAdd

ConfigModelSubscriptionVAAdd = Struct(
    "element_address" / UnicastAddress,
    "label" / Bytes(16),
    "model" / ModelId,
)

ConfigModelSubscriptionVADelete = ConfigModelSubscriptionVAAdd
ConfigModelSubscriptionVAOverwrite = ConfigModelSubscriptionVAAdd

ConfigModelSubscriptionStatus = Struct(
    "status" / StatusCodeAdapter,
    "element_address" / UnicastAddress,
    "address" / StatusSubscriptionAddress,
    "model" / ModelId,
)

ConfigModelSubscriptionDeleteAll = Struct(
    "element_address" / UnicastAddress,
    "model" / ModelId,
)

ConfigSIGModelSubscriptionGet = Struct(
    "element_address" / UnicastAddress,
    "model" / SIGModelId,
)

ConfigSIGModelSubscriptionList = Struct(
    "status" / StatusCodeAdapter,
    "element_address" / UnicastAddress,
    "model" / SIGModelId,
    "addresses" / GreedyRange(Int16ul),
)

ConfigVendorModelSubscriptionGet = Struct(
    "element_address" / UnicastAddress,
    "model" / VendorModelId,
)

ConfigVendorModelSubscriptionList = Struct(
    "status" / StatusCodeAdapter,
    "element_address" / UnicastAddress,
    "model" / VendorModelId,
    "addresses" / GreedyRange(Int16ul),
)

ConfigNetKeyAdd = Struct(
    *NetKeyIndex,
    "net_key" / Bytes(16),
)

ConfigNetKeyUpdate = ConfigNetKeyAdd

ConfigNetKeyDelete = Struct(
    *NetKeyIndex,
)

ConfigNetKeyStatus = Struct(
    "status" / StatusCodeAdapter,
    *NetKeyIndex,
)

ConfigNetKeyGet = Struct()

ConfigNetKeyList = Struct(
    "net_key_indices" / KeyIndices
)

ConfigAppKeyAdd = Struct(
    *NetAndAppKeyIndex,
    "app_key" / Bytes(16),
)

ConfigAppKeyUpdate = ConfigAppKeyAdd

ConfigAppKeyDelete = Struct(
    *NetAndAppKeyIndex,
)

ConfigAppKeyStatus = Struct(
    "status" / StatusCodeAdapter,
    *NetAndAppKeyIndex,
)

ConfigAppKeyGet = Struct(
    *NetKeyIndex
)

ConfigAppKeyList = Struct(
    "status" / StatusCodeAdapter,
    *NetKeyIndex,
    "app_key_indices" / KeyIndices,
)

ConfigNodeIdentityGet = Struct(
    *NetKeyIndex,
)

ConfigNodeIdentitySet = Struct(
    *NetKeyIndex,
    "identity" / NodeIdentityAdapter,
)

ConfigNodeIdentityStatus = Struct(
    "status" / StatusCodeAdapter,
    Embedded(ConfigNodeIdentitySet),
)

ConfigModelAppBind = Struct(
    "element_address" / UnicastAddress,
    *AppKeyIndex,
    "model" / ModelId,
)

ConfigModelAppUnbind = ConfigModelAppBind

ConfigModelAppStatus = Struct(
    "status" / StatusCodeAdapter,
    Embedded(ConfigModelAppBind),
)

ConfigSIGModelAppGet = Struct(
    "element_address" / UnicastAddress,
    "model" / SIGModelId,
)

ConfigSIGModelAppList = Struct(
    "status" / StatusCodeAdapter,
    Embedded(ConfigSIGModelAppGet),
    "app key indices" / KeyIndices,
)

ConfigVendorModelAppGet = Struct(
    "element_address" / UnicastAddress,
    "model" / VendorModelId,
)

ConfigVendorModelAppList = Struct(
    "status" / StatusCodeAdapter,
    Embedded(ConfigVendorModelAppGet),
    "app key indices" / KeyIndices,
)

ConfigNodeReset = Struct()

ConfigNodeResetStatus = Struct()

ConfigFriendGet = Struct()

ConfigFriendSet = Struct(
    "friend" / FriendAdapter,
)

ConfigFriendStatus = ConfigFriendSet

ConfigKeyRefreshPhaseGet = Struct(
    *NetKeyIndex,
)

ConfigKeyRefreshPhaseSet = Struct(
    Embedded(ConfigKeyRefreshPhaseGet),
    "transition" / EnumAdapter(Int8ul, KeyRefreshTransition),
)

ConfigKeyRefreshPhaseStatus = Struct(
    "status" / StatusCodeAdapter,
    *NetKeyIndex,
    "phase" / EnumAdapter(Int8ul, KeyRefreshPhase),
)

ConfigHeartbeatPublicationFeatures = ExprValidator(Int16ul, lambda obj, ctx: obj <= 0x3)

ConfigHeartbeatHops = ExprValidator(Int8ul, lambda obj, ctx: obj <= 0x7F)

ConfigHeartbeatPublicationGet = Struct()

ConfigHeartbeatPublicationSet = Struct(
    "destination" / UnicastUnassignedGroupAddress,
    "count" / LogAdapter(Int8ul, max_value=0x10, infinity=True),
    "period" / LogAdapter(Int8ul, max_value=0x10),
    "TTL" / TTL,
    "features" / BitList(2),
    *NetKeyIndex,
)

ConfigHeartbeatPublicationStatus = Struct(
    "status" / StatusCodeAdapter,
    Embedded(ConfigHeartbeatPublicationSet),
)

ConfigHeartbeatSubscriptionGet = Struct()

ConfigHeartbeatSubscriptionSet = Struct(
    "source" / UnicastUnassignedAddress,
    "destination" / UnicastUnassignedGroupAddress,
    "period_log" / LogAdapter(Int8ul, max_value=0x11),
)

ConfigHeartbeatSubscriptionStatus = Struct(
    "status" / StatusCodeAdapter,
    Embedded(ConfigHeartbeatSubscriptionSet),
    "count" / LogAdapter(Int8ul, max_value=0x11, infinity=True),
    "min_hops" / RangeValidator(Int8ul, max_value=0x7F),
    "max_hops" / RangeValidator(Int8ul, max_value=0x7F),
)

ConfigLowPowerNodePollTimeoutGet = Struct(
    "lpn_address" / Int16ul,  # TODO
)

ConfigLowPowerNodePollTimeoutStatus = Struct(
    Embedded(ConfigLowPowerNodePollTimeoutGet),
    "poll_timeout" / Int24ul,  # TODO
)

ConfigNetworkTransmitGet = Struct()

ConfigNetworkTransmitSet = NetworkRetransmit

ConfigNetworkTransmitStatus = ConfigNetworkTransmitSet


class ConfigOpcode(enum.IntEnum):
    APPKEY_ADD = 0x00
    APPKEY_DELETE = 0x8000
    APPKEY_GET = 0x8001
    APPKEY_LIST = 0x8002
    APPKEY_STATUS = 0x8003
    APPKEY_UPDATE = 0x01
    BEACON_GET = 0x8009
    BEACON_SET = 0x800A
    BEACON_STATUS = 0x800B
    COMPOSITION_DATA_GET = 0x8008
    COMPOSITION_DATA_STATUS = 0x02
    DEFAULT_TTL_GET = 0x800C
    DEFAULT_TTL_SET = 0x800D
    DEFAULT_TTL_STATUS = 0x800E
    FRIEND_GET = 0x800F
    FRIEND_SET = 0x8010
    FRIEND_STATUS = 0x8011
    GATT_PROXY_GET = 0x8012
    GATT_PROXY_SET = 0x8013
    GATT_PROXY_STATUS = 0x8014
    HEARBEAT_PUBLICATION_GET = 0x8038
    HEARBEAT_PUBLICATION_SET = 0x8039
    HEARBEAT_PUBLICATION_STATUS = 0x06
    HEARBEAT_SUBSCRIPTION_GET = 0x803A
    HEARBEAT_SUBSCRIPTION_SET = 0x803B
    HEARBEAT_SUBSCRIPTION_STATUS = 0x803C
    KEY_REFRESH_PHASE_GET = 0x8015
    KEY_REFRESH_PHASE_SET = 0x8016
    KEY_REFRESH_PHASE_STATUS = 0x8017
    LOW_POWER_NODE_POLLTIMEOUT_GET = 0x802D
    LOW_POWER_NODE_POLLTIMEOUT_STATUS = 0x802E
    MODEL_APP_BIND = 0x803D
    MODEL_APP_STATUS = 0x803E
    MODEL_APP_UNBIND = 0x803F
    MODEL_PUBLICATION_GET = 0x8018
    MODEL_PUBLICATION_SET = 0x03
    MODEL_PUBLICATION_STATUS = 0x8019
    MODEL_PUBLICATION_VIRTUAL_ADDRESS_SET = 0x801A
    MODEL_SUBSCRIPTION_ADD = 0x801B
    MODEL_SUBSCRIPTION_DELETE = 0x801C
    MODEL_SUBSCRIPTION_DELETE_ALL = 0x801D
    MODEL_SUBSCRIPTION_OVERWRITE = 0x801E
    MODEL_SUBSCRIPTION_STATUS = 0x801F
    MODEL_SUBSCRIPTION_VIRTUAL_ADDRESS_ADD = 0x8020
    MODEL_SUBSCRIPTION_VIRTUAL_ADDRESS_DELETE = 0x8021
    MODEL_SUBSCRIPTION_VIRTUAL_ADDRESS_OVERWRITE = 0x8022
    NETKEY_ADD = 0x8040
    NETKEY_DELETE = 0x8041
    NETKEY_GET = 0x8042
    NETKEY_LIST = 0x8043
    NETKEY_STATUS = 0x8044
    NETKEY_UPDATE = 0x8045
    NETWORK_TRANSMIT_GET = 0x8023
    NETWORK_TRANSMIT_SET = 0x8024
    NETWORK_TRANSMIT_STATUS = 0x8025
    NODE_IDENTITY_GET = 0x8046
    NODE_IDENTITY_SET = 0x8047
    NODE_IDENTITY_STATUS = 0x8048
    NODE_RESET = 0x8049
    NODE_RESET_STATUS = 0x804A
    RELAY_GET = 0x8026
    RELAY_SET = 0x8027
    RELAY_STATUS = 0x8028
    SIG_MODEL_APP_GET = 0x804B
    SIG_MODEL_APP_LIST = 0x804C
    SIG_MODEL_SUBSCRIPTION_GET = 0x8029
    SIG_MODEL_SUBSCRIPTION_LIST = 0x802A
    VENDOR_MODEL_APP_GET = 0x804D
    VENDOR_MODEL_APP_LIST = 0x804E
    VENDOR_MODEL_SUBSCRIPTION_GET = 0x802B
    VENDOR_MODEL_SUBSCRIPTION_LIST = 0x802C


ConfigMessage = Struct(
    "opcode" / EnumAdapter(Opcode, ConfigOpcode),
    "params" / Switch(
        this.opcode,
        {
            ConfigOpcode.APPKEY_ADD: ConfigAppKeyAdd,
            ConfigOpcode.APPKEY_DELETE: ConfigAppKeyDelete,
            ConfigOpcode.APPKEY_GET: ConfigAppKeyGet,
            ConfigOpcode.APPKEY_LIST: ConfigAppKeyList,
            ConfigOpcode.APPKEY_STATUS: ConfigAppKeyStatus,
            ConfigOpcode.APPKEY_UPDATE: ConfigAppKeyUpdate,
            ConfigOpcode.BEACON_GET: ConfigBeaconGet,
            ConfigOpcode.BEACON_SET: ConfigBeaconSet,
            ConfigOpcode.BEACON_STATUS: ConfigBeaconStatus,
            ConfigOpcode.COMPOSITION_DATA_GET: ConfigCompositionDataGet,
            ConfigOpcode.COMPOSITION_DATA_STATUS: ConfigCompositionDataStatus,
            ConfigOpcode.DEFAULT_TTL_GET: ConfigDefaultTTLGet,
            ConfigOpcode.DEFAULT_TTL_SET: ConfigDefaultTTLSet,
            ConfigOpcode.DEFAULT_TTL_STATUS: ConfigDefaultTTLStatus,
            ConfigOpcode.FRIEND_GET: ConfigFriendGet,
            ConfigOpcode.FRIEND_SET: ConfigFriendSet,
            ConfigOpcode.FRIEND_STATUS: ConfigFriendStatus,
            ConfigOpcode.GATT_PROXY_GET: ConfigGATTProxyGet,
            ConfigOpcode.GATT_PROXY_SET: ConfigGATTProxySet,
            ConfigOpcode.GATT_PROXY_STATUS: ConfigGATTProxyStatus,
            ConfigOpcode.HEARBEAT_PUBLICATION_GET: ConfigHeartbeatPublicationGet,
            ConfigOpcode.HEARBEAT_PUBLICATION_SET: ConfigHeartbeatPublicationSet,
            ConfigOpcode.HEARBEAT_PUBLICATION_STATUS: ConfigHeartbeatPublicationStatus,
            ConfigOpcode.HEARBEAT_SUBSCRIPTION_GET: ConfigHeartbeatSubscriptionGet,
            ConfigOpcode.HEARBEAT_SUBSCRIPTION_SET: ConfigHeartbeatSubscriptionSet,
            ConfigOpcode.HEARBEAT_SUBSCRIPTION_STATUS: ConfigHeartbeatSubscriptionStatus,
            ConfigOpcode.KEY_REFRESH_PHASE_GET: ConfigKeyRefreshPhaseGet,
            ConfigOpcode.KEY_REFRESH_PHASE_SET: ConfigKeyRefreshPhaseSet,
            ConfigOpcode.KEY_REFRESH_PHASE_STATUS: ConfigKeyRefreshPhaseStatus,
            ConfigOpcode.LOW_POWER_NODE_POLLTIMEOUT_GET: ConfigLowPowerNodePollTimeoutGet,
            ConfigOpcode.LOW_POWER_NODE_POLLTIMEOUT_STATUS: ConfigLowPowerNodePollTimeoutStatus,
            ConfigOpcode.MODEL_APP_BIND: ConfigModelAppBind,
            ConfigOpcode.MODEL_APP_STATUS: ConfigModelAppStatus,
            ConfigOpcode.MODEL_APP_UNBIND: ConfigModelAppUnbind,
            ConfigOpcode.MODEL_PUBLICATION_GET: ConfigModelPublicationGet,
            ConfigOpcode.MODEL_PUBLICATION_SET: ConfigModelPublicationSet,
            ConfigOpcode.MODEL_PUBLICATION_STATUS: ConfigModelPublicationStatus,
            ConfigOpcode.MODEL_PUBLICATION_VIRTUAL_ADDRESS_SET: ConfigModelPublicationVASet,
            ConfigOpcode.MODEL_SUBSCRIPTION_ADD: ConfigModelSubscriptionAdd,
            ConfigOpcode.MODEL_SUBSCRIPTION_DELETE: ConfigModelSubscriptionDelete,
            ConfigOpcode.MODEL_SUBSCRIPTION_DELETE_ALL: ConfigModelSubscriptionDeleteAll,
            ConfigOpcode.MODEL_SUBSCRIPTION_OVERWRITE: ConfigModelSubscriptionOverwrite,
            ConfigOpcode.MODEL_SUBSCRIPTION_STATUS: ConfigModelSubscriptionStatus,
            ConfigOpcode.MODEL_SUBSCRIPTION_VIRTUAL_ADDRESS_ADD: ConfigModelSubscriptionVAAdd,
            ConfigOpcode.MODEL_SUBSCRIPTION_VIRTUAL_ADDRESS_DELETE: ConfigModelSubscriptionVADelete,
            ConfigOpcode.MODEL_SUBSCRIPTION_VIRTUAL_ADDRESS_OVERWRITE: ConfigModelSubscriptionVAOverwrite,
            ConfigOpcode.NETKEY_ADD: ConfigNetKeyAdd,
            ConfigOpcode.NETKEY_DELETE: ConfigNetKeyDelete,
            ConfigOpcode.NETKEY_GET: ConfigNetKeyGet,
            ConfigOpcode.NETKEY_LIST: ConfigNetKeyList,
            ConfigOpcode.NETKEY_STATUS: ConfigNetKeyStatus,
            ConfigOpcode.NETKEY_UPDATE: ConfigNetKeyUpdate,
            ConfigOpcode.NETWORK_TRANSMIT_GET: ConfigNetworkTransmitGet,
            ConfigOpcode.NETWORK_TRANSMIT_SET: ConfigNetworkTransmitSet,
            ConfigOpcode.NETWORK_TRANSMIT_STATUS: ConfigNetworkTransmitStatus,
            ConfigOpcode.NODE_IDENTITY_GET: ConfigNodeIdentityGet,
            ConfigOpcode.NODE_IDENTITY_SET: ConfigNodeIdentitySet,
            ConfigOpcode.NODE_IDENTITY_STATUS: ConfigNodeIdentityStatus,
            ConfigOpcode.NODE_RESET: ConfigNodeReset,
            ConfigOpcode.NODE_RESET_STATUS: ConfigNodeResetStatus,
            ConfigOpcode.RELAY_GET: ConfigRelayGet,
            ConfigOpcode.RELAY_SET: ConfigRelaySet,
            ConfigOpcode.RELAY_STATUS: ConfigRelayStatus,
            ConfigOpcode.SIG_MODEL_APP_GET: ConfigSIGModelAppGet,
            ConfigOpcode.SIG_MODEL_APP_LIST: ConfigSIGModelAppList,
            ConfigOpcode.SIG_MODEL_SUBSCRIPTION_GET: ConfigSIGModelSubscriptionGet,
            ConfigOpcode.SIG_MODEL_SUBSCRIPTION_LIST: ConfigSIGModelSubscriptionList,
            ConfigOpcode.VENDOR_MODEL_APP_GET: ConfigVendorModelAppGet,
            ConfigOpcode.VENDOR_MODEL_APP_LIST: ConfigVendorModelAppList,
            ConfigOpcode.VENDOR_MODEL_SUBSCRIPTION_GET: ConfigVendorModelSubscriptionGet,
            ConfigOpcode.VENDOR_MODEL_SUBSCRIPTION_LIST: ConfigVendorModelSubscriptionList,
        }
    )
)

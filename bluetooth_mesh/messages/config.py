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
# pylint: disable=W0223

import enum
from datetime import timedelta

from construct import (
    Adapter,
    BitsInteger,
    BitStruct,
    Bytes,
    Embedded,
    ExprValidator,
    Flag,
    GreedyBytes,
    GreedyRange,
    Int8ul,
    Int16ul,
    Int24ul,
    Padding,
    Rebuild,
    Select,
    Struct,
    len_,
    obj_,
    this,
)

from bluetooth_mesh.messages.util import BitList, EmbeddedBitStruct, EnumAdapter
from bluetooth_mesh.messages.util import EnumSwitch as Switch
from bluetooth_mesh.messages.util import (
    LogAdapter,
    Opcode,
    RangeValidator,
    Reversed,
    SwitchStruct,
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
    ELEVENTH = 0x000B
    EXTERNAL = 0x0110
    FIFTEENTH = 0x000F
    FIFTH = 0x0005
    FIFTIETH = 0x0032
    FIFTY_EIGHTH = 0x003A
    FIFTY_FIFTH = 0x0037
    FIFTY_FIRST = 0x0033
    FIFTY_FOURTH = 0x0036
    FIFTY_NINTH = 0x003B
    FIFTY_SECOND = 0x0034
    FIFTY_SEVENTH = 0x0039
    FIFTY_SIXTH = 0x0038
    FIFTY_THIRD = 0x0035
    FIRST = 0x0001
    FLASH = 0x010A
    FORTIETH = 0x0028
    FOURTEENTH = 0x000E
    FOURTH = 0x0004
    FORTY_EIGHTH = 0x0030
    FORTY_FIFTH = 0x002D
    FORTY_FIRST = 0x0029
    FORTY_FOURTH = 0x002C
    FORTY_NINTH = 0x0031
    FORTY_SECOND = 0x002A
    FORTY_SEVENTH = 0x002F
    FORTY_SIXTH = 0x002E
    FORTY_THIRD = 0x002B
    FRONT = 0x0100
    INSIDE = 0x010B
    INTERNAL = 0x010F
    LEFT = 0x010D
    LOWER = 0x0105
    MAIN = 0x0106
    NINETEENTH = 0x0013
    NINTH = 0x0009
    NINETIETH = 0x005A
    NINETY_EIGHTH = 0x0062
    NINETY_FIFTH = 0x005F
    NINETY_FIRST = 0x005B
    NINETY_FOURTH = 0x005E
    NINETY_NINTH = 0x0063
    NINETY_SECOND = 0x005C
    NINETY_SEVENTH = 0x0061
    NINETY_SIXTH = 0x0060
    NINETY_THIRD = 0x005D
    ONE_HUNDRED_AND_EIGHTEENTH = 0x0076
    ONE_HUNDRED_AND_EIGHTH = 0x006C
    ONE_HUNDRED_AND_EIGHTY_EIGHTH = 0x00BC
    ONE_HUNDRED_AND_EIGHTY_FIFTH = 0x00B9
    ONE_HUNDRED_AND_EIGHTY_FIRST = 0x00B5
    ONE_HUNDRED_AND_EIGHTY_FOURTH = 0x00B8
    ONE_HUNDRED_AND_EIGHTY_NINTH = 0x00BD
    ONE_HUNDRED_AND_EIGHTY_SECOND = 0x00B6
    ONE_HUNDRED_AND_EIGHTY_SEVENTH = 0x00BB
    ONE_HUNDRED_AND_EIGHTY_SIXTH = 0x00BA
    ONE_HUNDRED_AND_EIGHTY_THIRD = 0x00B7
    ONE_HUNDRED_AND_ELEVENTH = 0x006F
    ONE_HUNDRED_AND_FIFTEENTH = 0x0073
    ONE_HUNDRED_AND_FIFTH = 0x0069
    ONE_HUNDRED_AND_FIFTY_EIGHTH = 0x009E
    ONE_HUNDRED_AND_FIFTY_FIFTH = 0x009B
    ONE_HUNDRED_AND_FIFTY_FIRST = 0x0097
    ONE_HUNDRED_AND_FIFTY_FOURTH = 0x009A
    ONE_HUNDRED_AND_FIFTY_NINTH = 0x009F
    ONE_HUNDRED_AND_FIFTY_SECOND = 0x0098
    ONE_HUNDRED_AND_FIFTY_SEVENTH = 0x009D
    ONE_HUNDRED_AND_FIFTY_SIXTH = 0x009C
    ONE_HUNDRED_AND_FIFTY_THIRD = 0x0099
    ONE_HUNDRED_AND_FIRST = 0x0065
    ONE_HUNDRED_AND_FOURTEENTH = 0x0072
    ONE_HUNDRED_AND_FOURTH = 0x0068
    ONE_HUNDRED_AND_FORTY_EIGHTH = 0x0094
    ONE_HUNDRED_AND_FORTY_FIFTH = 0x0091
    ONE_HUNDRED_AND_FORTY_FIRST = 0x008D
    ONE_HUNDRED_AND_FORTY_FOURTH = 0x0090
    ONE_HUNDRED_AND_FORTY_NINTH = 0x0095
    ONE_HUNDRED_AND_FORTY_SECOND = 0x008E
    ONE_HUNDRED_AND_FORTY_SEVENTH = 0x0093
    ONE_HUNDRED_AND_FORTY_SIXTH = 0x0092
    ONE_HUNDRED_AND_FORTY_THIRD = 0x008F
    ONE_HUNDRED_AND_NINETEENTH = 0x0077
    ONE_HUNDRED_AND_NINTH = 0x006D
    ONE_HUNDRED_AND_NINETY_EIGHTH = 0x00C6
    ONE_HUNDRED_AND_NINETY_FIFTH = 0x00C3
    ONE_HUNDRED_AND_NINETY_FIRST = 0x00BF
    ONE_HUNDRED_AND_NINETY_FOURTH = 0x00C2
    ONE_HUNDRED_AND_NINETY_NINTH = 0x00C7
    ONE_HUNDRED_AND_NINETY_SECOND = 0x00C0
    ONE_HUNDRED_AND_NINETY_SEVENTH = 0x00C5
    ONE_HUNDRED_AND_NINETY_SIXTH = 0x00C4
    ONE_HUNDRED_AND_NINETY_THIRD = 0x00C1
    ONE_HUNDRED_AND_SECOND = 0x0066
    ONE_HUNDRED_AND_SEVENTEENTH = 0x0075
    ONE_HUNDRED_AND_SEVENTH = 0x006B
    ONE_HUNDRED_AND_SEVENTY_EIGHTH = 0x00B2
    ONE_HUNDRED_AND_SEVENTY_FIFTH = 0x00AF
    ONE_HUNDRED_AND_SEVENTY_FIRST = 0x00AB
    ONE_HUNDRED_AND_SEVENTY_FOURTH = 0x00AE
    ONE_HUNDRED_AND_SEVENTY_NINTH = 0x00B3
    ONE_HUNDRED_AND_SEVENTY_SECOND = 0x00AC
    ONE_HUNDRED_AND_SEVENTY_SEVENTH = 0x00B1
    ONE_HUNDRED_AND_SEVENTY_SIXTH = 0x00B0
    ONE_HUNDRED_AND_SEVENTY_THIRD = 0x00AD
    ONE_HUNDRED_AND_SIXTEENTH = 0x0074
    ONE_HUNDRED_AND_SIXTH = 0x006A
    ONE_HUNDRED_AND_SIXTY_EIGHTH = 0x00A8
    ONE_HUNDRED_AND_SIXTY_FIFTH = 0x00A5
    ONE_HUNDRED_AND_SIXTY_FIRST = 0x00A1
    ONE_HUNDRED_AND_SIXTY_FOURTH = 0x00A4
    ONE_HUNDRED_AND_SIXTY_NINTH = 0x00A9
    ONE_HUNDRED_AND_SIXTY_SECOND = 0x00A2
    ONE_HUNDRED_AND_SIXTY_SEVENTH = 0x00A7
    ONE_HUNDRED_AND_SIXTY_SIXTH = 0x00A6
    ONE_HUNDRED_AND_SIXTY_THIRD = 0x00A3
    ONE_HUNDRED_AND_TENTH = 0x006E
    ONE_HUNDRED_AND_THIRD = 0x0067
    ONE_HUNDRED_AND_THIRTEENTH = 0x0071
    ONE_HUNDRED_AND_THIRTY_EIGHTH = 0x008A
    ONE_HUNDRED_AND_THIRTY_FIFTH = 0x0087
    ONE_HUNDRED_AND_THIRTY_FIRST = 0x0083
    ONE_HUNDRED_AND_THIRTY_FOURTH = 0x0086
    ONE_HUNDRED_AND_THIRTY_NINTH = 0x008B
    ONE_HUNDRED_AND_THIRTY_SECOND = 0x0084
    ONE_HUNDRED_AND_THIRTY_SEVENTH = 0x0089
    ONE_HUNDRED_AND_THIRTY_SIXTH = 0x0088
    ONE_HUNDRED_AND_THIRTY_THIRD = 0x0085
    ONE_HUNDRED_AND_TWELVETH = 0x0070
    ONE_HUNDRED_AND_TWENTY_EIGHTH = 0x0080
    ONE_HUNDRED_AND_TWENTY_FIFTH = 0x007D
    ONE_HUNDRED_AND_TWENTY_FIRST = 0x0079
    ONE_HUNDRED_AND_TWENTY_FOURTH = 0x007C
    ONE_HUNDRED_AND_TWENTY_NINTH = 0x0081
    ONE_HUNDRED_AND_TWENTY_SECOND = 0x007A
    ONE_HUNDRED_AND_TWENTY_SEVENTH = 0x007F
    ONE_HUNDRED_AND_TWENTY_SIXTH = 0x007E
    ONE_HUNDRED_AND_TWENTY_THIRD = 0x007B
    ONE_HUNDRED_EIGHTIETH = 0x00B4
    ONE_HUNDRED_FIFTIETH = 0x0096
    ONE_HUNDRED_FORTIETH = 0x008C
    ONE_HUNDRED_NINETIETH = 0x00BE
    ONE_HUNDRED_SEVENTIETH = 0x00AA
    ONE_HUNDRED_SIXTIETH = 0x00A0
    ONE_HUNDRED_THIRTIETH = 0x0082
    ONE_HUNDRED_TWENTIETH = 0x0078
    ONE_HUNDREDTH = 0x0064
    OUTSIDE = 0x010C
    RIGHT = 0x010E
    SECOND = 0x0002
    SEVENTEENTH = 0x0011
    SEVENTH = 0x0007
    SEVENTIETH = 0x0046
    SEVENTY_EIGHTH = 0x004E
    SEVENTY_FIFTH = 0x004B
    SEVENTY_FIRST = 0x0047
    SEVENTY_FOURTH = 0x004A
    SEVENTY_NINTH = 0x004F
    SEVENTY_SECOND = 0x0048
    SEVENTY_SEVENTH = 0x004D
    SEVENTY_SIXTH = 0x004C
    SEVENTY_THIRD = 0x0049
    SIXTEENTH = 0x0010
    SIXTH = 0x0006
    SIXTIETH = 0x003C
    SIXTY_EIGHTH = 0x0044
    SIXTY_FIFTH = 0x0041
    SIXTY_FIRST = 0x003D
    SIXTY_FOURTH = 0x0040
    SIXTY_NINTH = 0x0045
    SIXTY_SECOND = 0x003E
    SIXTY_SEVENTH = 0x0043
    SIXTY_SIXTH = 0x0042
    SIXTY_THIRD = 0x003F
    SUPPLEMENTARY = 0x0109
    TENTH = 0x000A
    THIRD = 0x0003
    THIRTEENTH = 0x000D
    THIRTIETH = 0x001E
    THIRTY_EIGHTH = 0x0026
    THIRTY_FIFTH = 0x0023
    THIRTY_FIRST = 0x001F
    THIRTY_FOURTH = 0x0022
    THIRTY_NINTH = 0x0027
    THIRTY_SECOND = 0x0020
    THIRTY_SEVENTH = 0x0025
    THIRTY_SIXTH = 0x0024
    THIRTY_THIRD = 0x0021
    TOP = 0x0102
    TWELVETH = 0x000C
    TWENTIETH = 0x0014
    TWENTY_EIGHTH = 0x001C
    TWENTY_FIFTH = 0x0019
    TWENTY_FIRST = 0x0015
    TWENTY_FOURTH = 0x0018
    TWENTY_NINTH = 0x001D
    TWENTY_SECOND = 0x0016
    TWENTY_SEVENTH = 0x001B
    TWENTY_SIXTH = 0x001A
    TWENTY_THIRD = 0x0017
    TWO_HUNDRED_AND_EIGHTEENTH = 0x00DA
    TWO_HUNDRED_AND_EIGHTH = 0x00D0
    TWO_HUNDRED_AND_ELEVENTH = 0x00D3
    TWO_HUNDRED_AND_FIFTEENTH = 0x00D7
    TWO_HUNDRED_AND_FIFTH = 0x00CD
    TWO_HUNDRED_AND_FIFTY_FIFTH = 0x00FF
    TWO_HUNDRED_AND_FIFTY_FIRST = 0x00FB
    TWO_HUNDRED_AND_FIFTY_FOURTH = 0x00FE
    TWO_HUNDRED_AND_FIFTY_SECOND = 0x00FC
    TWO_HUNDRED_AND_FIFTY_THIRD = 0x00FD
    TWO_HUNDRED_AND_FIRST = 0x00C9
    TWO_HUNDRED_AND_FOURTEENTH = 0x00D6
    TWO_HUNDRED_AND_FOURTH = 0x00CC
    TWO_HUNDRED_AND_FORTY_EIGHTH = 0x00F8
    TWO_HUNDRED_AND_FORTY_FIFTH = 0x00F5
    TWO_HUNDRED_AND_FORTY_FIRST = 0x00F1
    TWO_HUNDRED_AND_FORTY_FOURTH = 0x00F4
    TWO_HUNDRED_AND_FORTY_NINTH = 0x00F9
    TWO_HUNDRED_AND_FORTY_SECOND = 0x00F2
    TWO_HUNDRED_AND_FORTY_SEVENTH = 0x00F7
    TWO_HUNDRED_AND_FORTY_SIXTH = 0x00F6
    TWO_HUNDRED_AND_FORTY_THIRD = 0x00F3
    TWO_HUNDRED_AND_NINETEENTH = 0x00DB
    TWO_HUNDRED_AND_NINTH = 0x00D1
    TWO_HUNDRED_AND_SECOND = 0x00CA
    TWO_HUNDRED_AND_SEVENTEENTH = 0x00D9
    TWO_HUNDRED_AND_SEVENTH = 0x00CF
    TWO_HUNDRED_AND_SIXTEENTH = 0x00D8
    TWO_HUNDRED_AND_SIXTH = 0x00CE
    TWO_HUNDRED_AND_TENTH = 0x00D2
    TWO_HUNDRED_AND_THIRD = 0x00CB
    TWO_HUNDRED_AND_THIRTEENTH = 0x00D5
    TWO_HUNDRED_AND_THIRTY_EIGHTH = 0x00EE
    TWO_HUNDRED_AND_THIRTY_FIFTH = 0x00EB
    TWO_HUNDRED_AND_THIRTY_FIRST = 0x00E7
    TWO_HUNDRED_AND_THIRTY_FOURTH = 0x00EA
    TWO_HUNDRED_AND_THIRTY_NINTH = 0x00EF
    TWO_HUNDRED_AND_THIRTY_SECOND = 0x00E8
    TWO_HUNDRED_AND_THIRTY_SEVENTH = 0x00ED
    TWO_HUNDRED_AND_THIRTY_SIXTH = 0x00EC
    TWO_HUNDRED_AND_THIRTY_THIRD = 0x00E9
    TWO_HUNDRED_AND_TWELVETH = 0x00D4
    TWO_HUNDRED_AND_TWENTY_EIGHTH = 0x00E4
    TWO_HUNDRED_AND_TWENTY_FIFTH = 0x00E1
    TWO_HUNDRED_AND_TWENTY_FIRST = 0x00DD
    TWO_HUNDRED_AND_TWENTY_FOURTH = 0x00E0
    TWO_HUNDRED_AND_TWENTY_NINTH = 0x00E5
    TWO_HUNDRED_AND_TWENTY_SECOND = 0x00DE
    TWO_HUNDRED_AND_TWENTY_SEVENTH = 0x00E3
    TWO_HUNDRED_AND_TWENTY_SIXTH = 0x00E2
    TWO_HUNDRED_AND_TWENTY_THIRD = 0x00DF
    TWO_HUNDRED_FIFTIETH = 0x00FA
    TWO_HUNDRED_FORTIETH = 0x00F0
    TWO_HUNDRED_THIRTIETH = 0x00E6
    TWO_HUNDRED_TWENTIETH = 0x00DC
    TWO_HUNDREDTH = 0x00C8
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

PublishFriendshipCredentialsFlagAdapter = EnumAdapter(
    Flag, PublishFriendshipCredentialsFlag
)

StatusCodeAdapter = EnumAdapter(Int8ul, StatusCode)

NodeIdentityAdapter = EnumAdapter(Int8ul, NodeIdentity)

FriendAdapter = EnumAdapter(Int8ul, Friend)

TTL = RangeValidator(Int8ul, max_value=0x7F)

# fmt: off
SIGModelId = Struct(
    "model_id" / Int16ul,
)

VendorModelId = Struct(
    "vendor_id" / Int16ul,
    "model_id" / Int16ul,
)

ModelId = Select(
    vendor=VendorModelId,
    sig=SIGModelId
)
# fmt: on


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
    # pylint: disable=R0911

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
        subcons, lambda obj, ctx: get_address_type(obj) in allowed_types
    )


# fmt: off
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
    "sig_number" / Rebuild(Int8ul, len_(this["sig_models"])),
    "vendor_number" / Rebuild(Int8ul, len_(this["vendor_models"])),
    "sig_models" / SIGModelId[this["sig_number"]],
    "vendor_models" / VendorModelId[this["vendor_number"]],
)

CompositionData = Struct(
    "cid" / Int16ul,
    "pid" / Int16ul,
    "vid" / Int16ul,
    "crpl" / Int16ul,
    "features" / Int16ul,  # TODO should be parsed
    "elements" / GreedyRange(CompositionDataElement),
)

Retransmit = BitStruct(
    # sssssccc
    "interval_steps" / BitsInteger(5),
    "count" / BitsInteger(3),
)
# fmt: on


class RetransmitAdapter(Adapter):
    _subcon = Int16ul

    def __init__(self, subcon, interval):
        self.interval = interval
        super(RetransmitAdapter, self).__init__(subcon)

    def _decode(self, obj, context, path):
        return dict(
            count=obj["count"], interval=(obj["interval_steps"] + 1) * self.interval
        )

    def _encode(self, obj, context, path):
        if obj["count"] > 7:
            raise AttributeError("Retransmission count maximum value is 7")
        if (
            not 0 < obj["interval"] <= 0x20 * self.interval
            or obj["interval"] % self.interval
        ):
            raise AttributeError(
                "Interval value must be in range of {min} and {max} with increment of {min}".format(
                    min=self.interval, max=0x20 * self.interval
                )
            )
        return dict(
            count=obj["count"],
            interval_steps=int(round((obj["interval"] / self.interval) - 1)),
        )


NetworkRetransmit = RetransmitAdapter(
    Retransmit, 10
)  # (Network Retransmit Interval Steps + 1) * 10ms

RelayRetransmit = NetworkRetransmit  # (Relay Retransmit Interval Steps + 1) * 10ms

PublishRetransmit = RetransmitAdapter(
    Retransmit, 50
)  # (Publish Retransmit Interval Steps + 1) * 50ms


def DoubleKeyIndex(first, second):
    return EmbeddedBitStruct(
        "_", second / BitsInteger(12), first / BitsInteger(12), reversed=True
    )


def SingleKeyIndex(name):
    return EmbeddedBitStruct("_", Padding(4), name / BitsInteger(12), reversed=True)


NetAndAppKeyIndex = DoubleKeyIndex("net_key_index", "app_key_index")

AppKeyIndex = SingleKeyIndex("app_key_index")

NetKeyIndex = SingleKeyIndex("net_key_index")


class KeyIndicesAdapter(Adapter):
    _subcon = GreedyRange(BitsInteger(12))

    def _decode(self, obj, context, path):
        """
        Flatten a list dictionaries into list of items:
            [{first=1, second=2}, {last=3}] -> [1, 2, 3]
        """
        ret = []
        for item in obj:
            if "last" in item:
                ret += [item["last"]]
            else:
                ret += [item["first"], item["second"]]
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


# fmt: off
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
# fmt: on


class PublishPeriodStepResolution(enum.IntEnum):
    RESOLUTION_100_MS = 0x0
    RESOLUTION_1_S = 0x1
    RESOLUTION_10_S = 0x2
    RESOLUTION_10_MIN = 0x3

    @property
    def multiplier(self):
        if self == PublishPeriodStepResolution.RESOLUTION_100_MS:
            return timedelta(milliseconds=100)

        if self == PublishPeriodStepResolution.RESOLUTION_1_S:
            return timedelta(seconds=1)

        if self == PublishPeriodStepResolution.RESOLUTION_10_S:
            return timedelta(seconds=10)

        if self == PublishPeriodStepResolution.RESOLUTION_10_MIN:
            return timedelta(minutes=10)


# fmt: off
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

class CompositionDataPage(enum.IntEnum):
    ZERO = 0
    FIRST = 1
    TWO_HUNDRED_AND_FIFTY_FIFTH = 255

CompositionDataPageAdapter = EnumAdapter(Int8ul, CompositionDataPage)

ConfigCompositionDataGet = Struct(
    "page" / CompositionDataPageAdapter,
)

ConfigCompositionData = Switch(
    this.page,
    {
        CompositionDataPage.ZERO: CompositionData,
        CompositionDataPage.FIRST: GreedyBytes,
        CompositionDataPage.TWO_HUNDRED_AND_FIFTY_FIFTH: GreedyBytes,
    }
)

ConfigCompositionDataStatus = SwitchStruct(
    "page" / CompositionDataPageAdapter,
    "data" / ConfigCompositionData,
)

ConfigDefaultTTLGet = Struct()

ConfigDefaultTTLSet = Struct(
    "ttl" / TTL,
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
        "rfu" / BitsInteger(3),
        "credential_flag" / PublishFriendshipCredentialsFlagAdapter,
        "app_key_index" / BitsInteger(12),
        reversed=True
    ),
    "ttl" / TTL,
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
    "ttl" / TTL,
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
    "app_key_indices" / KeyIndices,
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
    "ttl" / TTL,
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


# fmt: on
class ConfigOpcode(enum.IntEnum):
    CONFIG_APPKEY_ADD = 0x00
    CONFIG_APPKEY_DELETE = 0x8000
    CONFIG_APPKEY_GET = 0x8001
    CONFIG_APPKEY_LIST = 0x8002
    CONFIG_APPKEY_STATUS = 0x8003
    CONFIG_APPKEY_UPDATE = 0x01
    CONFIG_BEACON_GET = 0x8009
    CONFIG_BEACON_SET = 0x800A
    CONFIG_BEACON_STATUS = 0x800B
    CONFIG_COMPOSITION_DATA_GET = 0x8008
    CONFIG_COMPOSITION_DATA_STATUS = 0x02
    CONFIG_DEFAULT_TTL_GET = 0x800C
    CONFIG_DEFAULT_TTL_SET = 0x800D
    CONFIG_DEFAULT_TTL_STATUS = 0x800E
    CONFIG_FRIEND_GET = 0x800F
    CONFIG_FRIEND_SET = 0x8010
    CONFIG_FRIEND_STATUS = 0x8011
    CONFIG_GATT_PROXY_GET = 0x8012
    CONFIG_GATT_PROXY_SET = 0x8013
    CONFIG_GATT_PROXY_STATUS = 0x8014
    CONFIG_HEARBEAT_PUBLICATION_GET = 0x8038
    CONFIG_HEARBEAT_PUBLICATION_SET = 0x8039
    CONFIG_HEARBEAT_PUBLICATION_STATUS = 0x06
    CONFIG_HEARBEAT_SUBSCRIPTION_GET = 0x803A
    CONFIG_HEARBEAT_SUBSCRIPTION_SET = 0x803B
    CONFIG_HEARBEAT_SUBSCRIPTION_STATUS = 0x803C
    CONFIG_KEY_REFRESH_PHASE_GET = 0x8015
    CONFIG_KEY_REFRESH_PHASE_SET = 0x8016
    CONFIG_KEY_REFRESH_PHASE_STATUS = 0x8017
    CONFIG_LOW_POWER_NODE_POLLTIMEOUT_GET = 0x802D
    CONFIG_LOW_POWER_NODE_POLLTIMEOUT_STATUS = 0x802E
    CONFIG_MODEL_APP_BIND = 0x803D
    CONFIG_MODEL_APP_STATUS = 0x803E
    CONFIG_MODEL_APP_UNBIND = 0x803F
    CONFIG_MODEL_PUBLICATION_GET = 0x8018
    CONFIG_MODEL_PUBLICATION_SET = 0x03
    CONFIG_MODEL_PUBLICATION_STATUS = 0x8019
    CONFIG_MODEL_PUBLICATION_VIRTUAL_ADDRESS_SET = 0x801A
    CONFIG_MODEL_SUBSCRIPTION_ADD = 0x801B
    CONFIG_MODEL_SUBSCRIPTION_DELETE = 0x801C
    CONFIG_MODEL_SUBSCRIPTION_DELETE_ALL = 0x801D
    CONFIG_MODEL_SUBSCRIPTION_OVERWRITE = 0x801E
    CONFIG_MODEL_SUBSCRIPTION_STATUS = 0x801F
    CONFIG_MODEL_SUBSCRIPTION_VIRTUAL_ADDRESS_ADD = 0x8020
    CONFIG_MODEL_SUBSCRIPTION_VIRTUAL_ADDRESS_DELETE = 0x8021
    CONFIG_MODEL_SUBSCRIPTION_VIRTUAL_ADDRESS_OVERWRITE = 0x8022
    CONFIG_NETKEY_ADD = 0x8040
    CONFIG_NETKEY_DELETE = 0x8041
    CONFIG_NETKEY_GET = 0x8042
    CONFIG_NETKEY_LIST = 0x8043
    CONFIG_NETKEY_STATUS = 0x8044
    CONFIG_NETKEY_UPDATE = 0x8045
    CONFIG_NETWORK_TRANSMIT_GET = 0x8023
    CONFIG_NETWORK_TRANSMIT_SET = 0x8024
    CONFIG_NETWORK_TRANSMIT_STATUS = 0x8025
    CONFIG_NODE_IDENTITY_GET = 0x8046
    CONFIG_NODE_IDENTITY_SET = 0x8047
    CONFIG_NODE_IDENTITY_STATUS = 0x8048
    CONFIG_NODE_RESET = 0x8049
    CONFIG_NODE_RESET_STATUS = 0x804A
    CONFIG_RELAY_GET = 0x8026
    CONFIG_RELAY_SET = 0x8027
    CONFIG_RELAY_STATUS = 0x8028
    CONFIG_SIG_MODEL_APP_GET = 0x804B
    CONFIG_SIG_MODEL_APP_LIST = 0x804C
    CONFIG_SIG_MODEL_SUBSCRIPTION_GET = 0x8029
    CONFIG_SIG_MODEL_SUBSCRIPTION_LIST = 0x802A
    CONFIG_VENDOR_MODEL_APP_GET = 0x804D
    CONFIG_VENDOR_MODEL_APP_LIST = 0x804E
    CONFIG_VENDOR_MODEL_SUBSCRIPTION_GET = 0x802B
    CONFIG_VENDOR_MODEL_SUBSCRIPTION_LIST = 0x802C


# fmt: off
ConfigMessage = SwitchStruct(
    "opcode" / Opcode(ConfigOpcode),
    "params" / Switch(
        this.opcode,
        {
            ConfigOpcode.CONFIG_APPKEY_ADD: ConfigAppKeyAdd,
            ConfigOpcode.CONFIG_APPKEY_DELETE: ConfigAppKeyDelete,
            ConfigOpcode.CONFIG_APPKEY_GET: ConfigAppKeyGet,
            ConfigOpcode.CONFIG_APPKEY_LIST: ConfigAppKeyList,
            ConfigOpcode.CONFIG_APPKEY_STATUS: ConfigAppKeyStatus,
            ConfigOpcode.CONFIG_APPKEY_UPDATE: ConfigAppKeyUpdate,
            ConfigOpcode.CONFIG_BEACON_GET: ConfigBeaconGet,
            ConfigOpcode.CONFIG_BEACON_SET: ConfigBeaconSet,
            ConfigOpcode.CONFIG_BEACON_STATUS: ConfigBeaconStatus,
            ConfigOpcode.CONFIG_COMPOSITION_DATA_GET: ConfigCompositionDataGet,
            ConfigOpcode.CONFIG_COMPOSITION_DATA_STATUS: ConfigCompositionDataStatus,
            ConfigOpcode.CONFIG_DEFAULT_TTL_GET: ConfigDefaultTTLGet,
            ConfigOpcode.CONFIG_DEFAULT_TTL_SET: ConfigDefaultTTLSet,
            ConfigOpcode.CONFIG_DEFAULT_TTL_STATUS: ConfigDefaultTTLStatus,
            ConfigOpcode.CONFIG_FRIEND_GET: ConfigFriendGet,
            ConfigOpcode.CONFIG_FRIEND_SET: ConfigFriendSet,
            ConfigOpcode.CONFIG_FRIEND_STATUS: ConfigFriendStatus,
            ConfigOpcode.CONFIG_GATT_PROXY_GET: ConfigGATTProxyGet,
            ConfigOpcode.CONFIG_GATT_PROXY_SET: ConfigGATTProxySet,
            ConfigOpcode.CONFIG_GATT_PROXY_STATUS: ConfigGATTProxyStatus,
            ConfigOpcode.CONFIG_HEARBEAT_PUBLICATION_GET: ConfigHeartbeatPublicationGet,
            ConfigOpcode.CONFIG_HEARBEAT_PUBLICATION_SET: ConfigHeartbeatPublicationSet,
            ConfigOpcode.CONFIG_HEARBEAT_PUBLICATION_STATUS: ConfigHeartbeatPublicationStatus,
            ConfigOpcode.CONFIG_HEARBEAT_SUBSCRIPTION_GET: ConfigHeartbeatSubscriptionGet,
            ConfigOpcode.CONFIG_HEARBEAT_SUBSCRIPTION_SET: ConfigHeartbeatSubscriptionSet,
            ConfigOpcode.CONFIG_HEARBEAT_SUBSCRIPTION_STATUS: ConfigHeartbeatSubscriptionStatus,
            ConfigOpcode.CONFIG_KEY_REFRESH_PHASE_GET: ConfigKeyRefreshPhaseGet,
            ConfigOpcode.CONFIG_KEY_REFRESH_PHASE_SET: ConfigKeyRefreshPhaseSet,
            ConfigOpcode.CONFIG_KEY_REFRESH_PHASE_STATUS: ConfigKeyRefreshPhaseStatus,
            ConfigOpcode.CONFIG_LOW_POWER_NODE_POLLTIMEOUT_GET: ConfigLowPowerNodePollTimeoutGet,
            ConfigOpcode.CONFIG_LOW_POWER_NODE_POLLTIMEOUT_STATUS: ConfigLowPowerNodePollTimeoutStatus,
            ConfigOpcode.CONFIG_MODEL_APP_BIND: ConfigModelAppBind,
            ConfigOpcode.CONFIG_MODEL_APP_STATUS: ConfigModelAppStatus,
            ConfigOpcode.CONFIG_MODEL_APP_UNBIND: ConfigModelAppUnbind,
            ConfigOpcode.CONFIG_MODEL_PUBLICATION_GET: ConfigModelPublicationGet,
            ConfigOpcode.CONFIG_MODEL_PUBLICATION_SET: ConfigModelPublicationSet,
            ConfigOpcode.CONFIG_MODEL_PUBLICATION_STATUS: ConfigModelPublicationStatus,
            ConfigOpcode.CONFIG_MODEL_PUBLICATION_VIRTUAL_ADDRESS_SET: ConfigModelPublicationVASet,
            ConfigOpcode.CONFIG_MODEL_SUBSCRIPTION_ADD: ConfigModelSubscriptionAdd,
            ConfigOpcode.CONFIG_MODEL_SUBSCRIPTION_DELETE: ConfigModelSubscriptionDelete,
            ConfigOpcode.CONFIG_MODEL_SUBSCRIPTION_DELETE_ALL: ConfigModelSubscriptionDeleteAll,
            ConfigOpcode.CONFIG_MODEL_SUBSCRIPTION_OVERWRITE: ConfigModelSubscriptionOverwrite,
            ConfigOpcode.CONFIG_MODEL_SUBSCRIPTION_STATUS: ConfigModelSubscriptionStatus,
            ConfigOpcode.CONFIG_MODEL_SUBSCRIPTION_VIRTUAL_ADDRESS_ADD: ConfigModelSubscriptionVAAdd,
            ConfigOpcode.CONFIG_MODEL_SUBSCRIPTION_VIRTUAL_ADDRESS_DELETE: ConfigModelSubscriptionVADelete,
            ConfigOpcode.CONFIG_MODEL_SUBSCRIPTION_VIRTUAL_ADDRESS_OVERWRITE: ConfigModelSubscriptionVAOverwrite,
            ConfigOpcode.CONFIG_NETKEY_ADD: ConfigNetKeyAdd,
            ConfigOpcode.CONFIG_NETKEY_DELETE: ConfigNetKeyDelete,
            ConfigOpcode.CONFIG_NETKEY_GET: ConfigNetKeyGet,
            ConfigOpcode.CONFIG_NETKEY_LIST: ConfigNetKeyList,
            ConfigOpcode.CONFIG_NETKEY_STATUS: ConfigNetKeyStatus,
            ConfigOpcode.CONFIG_NETKEY_UPDATE: ConfigNetKeyUpdate,
            ConfigOpcode.CONFIG_NETWORK_TRANSMIT_GET: ConfigNetworkTransmitGet,
            ConfigOpcode.CONFIG_NETWORK_TRANSMIT_SET: ConfigNetworkTransmitSet,
            ConfigOpcode.CONFIG_NETWORK_TRANSMIT_STATUS: ConfigNetworkTransmitStatus,
            ConfigOpcode.CONFIG_NODE_IDENTITY_GET: ConfigNodeIdentityGet,
            ConfigOpcode.CONFIG_NODE_IDENTITY_SET: ConfigNodeIdentitySet,
            ConfigOpcode.CONFIG_NODE_IDENTITY_STATUS: ConfigNodeIdentityStatus,
            ConfigOpcode.CONFIG_NODE_RESET: ConfigNodeReset,
            ConfigOpcode.CONFIG_NODE_RESET_STATUS: ConfigNodeResetStatus,
            ConfigOpcode.CONFIG_RELAY_GET: ConfigRelayGet,
            ConfigOpcode.CONFIG_RELAY_SET: ConfigRelaySet,
            ConfigOpcode.CONFIG_RELAY_STATUS: ConfigRelayStatus,
            ConfigOpcode.CONFIG_SIG_MODEL_APP_GET: ConfigSIGModelAppGet,
            ConfigOpcode.CONFIG_SIG_MODEL_APP_LIST: ConfigSIGModelAppList,
            ConfigOpcode.CONFIG_SIG_MODEL_SUBSCRIPTION_GET: ConfigSIGModelSubscriptionGet,
            ConfigOpcode.CONFIG_SIG_MODEL_SUBSCRIPTION_LIST: ConfigSIGModelSubscriptionList,
            ConfigOpcode.CONFIG_VENDOR_MODEL_APP_GET: ConfigVendorModelAppGet,
            ConfigOpcode.CONFIG_VENDOR_MODEL_APP_LIST: ConfigVendorModelAppList,
            ConfigOpcode.CONFIG_VENDOR_MODEL_SUBSCRIPTION_GET: ConfigVendorModelSubscriptionGet,
            ConfigOpcode.CONFIG_VENDOR_MODEL_SUBSCRIPTION_LIST: ConfigVendorModelSubscriptionList,
        }
    )
)
# fmt: on

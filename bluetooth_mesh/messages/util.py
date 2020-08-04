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

import math
from ipaddress import IPv4Address

from construct import (
    Adapter,
    Bit,
    BitStruct,
    Bitwise,
    Computed,
    Construct,
    Container,
    Embedded,
    Enum,
    ExprValidator,
    Int8ub,
    Int16ub,
    Int24ub,
    Rebuild,
    Restreamed,
    Select,
    SizeofError,
    Struct,
    Switch,
    ValidationError,
    obj_,
    stream_read,
    stream_write,
    this,
)


def identity(x):
    return x


def reverse(sequence):
    return sequence[::-1]


def Reversed(subcon):
    return Restreamed(
        subcon, reverse, subcon.sizeof(), reverse, subcon.sizeof(), identity
    )


class BitListAdapter(Adapter):
    def __init__(self, subcon, reversed):
        super().__init__(subcon)
        self.reversed = reversed

    def _decode(self, obj, content, path):
        bits = set()

        for bit, feature in enumerate(reversed(obj) if self.reversed else obj):
            if not feature:
                continue

            bits.add(bit)

        return bits

    def _encode(self, obj, content, path):
        bits = []

        for bit in range(self.sizeof() * 8):
            bits.append(bit in obj)

        return list(reversed(bits)) if self.reversed else bits


def BitList(size, *, reversed=False):
    return BitListAdapter(Bitwise(Bit[size * 8]), reversed)


def EnumAdapter(subcon, enum):
    class _Enum(Enum):
        ENUM = enum

    class _EnumAdapter(Adapter):
        def _decode(self, obj, context, path):
            if obj not in enum._value2member_map_:
                raise ValidationError("object failed validation: %s" % (obj,))
            return enum(obj)

        def _encode(self, obj, context, path):
            if obj == enum:
                return obj.value

            try:
                return enum(obj)
            except ValueError:
                raise ValidationError("object failed validation: %s" % (obj,))

    _EnumAdapter.__construct_doc__ = _Enum(subcon, enum)

    return _EnumAdapter(subcon)


def LogAdapter(subcon, *, max_value=None, infinity=False):
    class _LogAdapter(Adapter):
        MAX_TYPE_VALUE = int(math.pow(2, subcon.length * 8) - 1)

        def _decode(self, obj, context, path):
            if obj == 0:
                return 0

            if obj == self.MAX_TYPE_VALUE:
                if infinity:
                    return float("inf")

            if max_value is not None and obj > max_value:
                raise ValidationError(
                    "max value exceeded, expecting at most %d: %s" % (max_value, obj)
                )

            return int(math.pow(2, obj - 1))

        def _encode(self, obj, context, path):
            if obj == 0:
                return 0

            if obj == float("inf"):
                if infinity:
                    return self.MAX_TYPE_VALUE

                raise ValidationError("infinity is not allowed: %s" % obj)

            value = math.log(obj, 2) + 1

            if max_value is not None and value > max_value:
                raise ValidationError(
                    "max value exceeded, expecting at most %d: %s" % (max_value, obj)
                )

            return int(value)

    return _LogAdapter(subcon)


def RangeValidator(subcon, *, min_value=None, max_value=None):
    def validate_range(obj, ctx):
        if min_value is not None and obj < min_value:
            return False

        if max_value is not None and obj > max_value:
            return False

        return True

    return ExprValidator(subcon, validate_range)


def EmbeddedBitStruct(name, *args, reversed=False):
    """
    Emulates BitStruct embedding:
        - for parsing, adds Computed accessor fields to the parent construct,
        - for building, Rebuild the bit struct using keys passed to the parent

    NOTE: This is a hack. Do not use unless you absolutely have to.
    """
    bit_struct = BitStruct(*args)

    if reversed:
        bit_struct = Reversed(bit_struct)

    bit_struct.__construct_doc__ = Embedded(Struct(*args))

    return (name / Rebuild(bit_struct, dict),) + tuple(
        i.name / Computed(this[name][i.name]) for i in args if i.name is not None
    )


class Opcode(Construct):
    def __init__(self, type=int):
        super().__init__()
        self.type = type

    def _parse(self, stream, context, path):
        try:
            opcode = stream_read(stream, 1)[0]

            if opcode == 0x7F:
                raise ValidationError

            len = opcode >> 7

            # 1 byte opcode
            if not len:
                return self.type(opcode)

            len = opcode >> 6
            opcode = opcode << 8 | stream_read(stream, 1)[0]

            # 2 byte opcode
            if len == 2:
                return self.type(opcode)

            if len == 3:
                opcode = opcode << 8 | stream_read(stream, 1)[0]
                return self.type(opcode)

            raise ValidationError
        except ValueError:
            raise ValidationError

    def _build(self, obj, stream, context, path):
        if obj > 0xFFFF:
            stream_write(stream, obj.to_bytes(3, byteorder="big"))
        elif obj > 0xFF:
            stream_write(stream, obj.to_bytes(2, byteorder="big"))
        else:
            stream_write(stream, obj.to_bytes(1, byteorder="big"))

        return self.type(obj)

    def _sizeof(self, context, path):
        raise SizeofError


class DefaultCountValidator(Adapter):
    def __init__(self, subcon, rounding=None, resolution=1.0):
        super().__init__(subcon)
        self.rounding = rounding
        self.resolution = resolution

    def _decode(self, obj, content, path):
        if obj == (256 ** self.subcon.length) - 1:
            return None
        else:
            return (
                round(obj * self.resolution, self.rounding)
                if self.rounding
                else obj * self.resolution
            )

    def _encode(self, obj, content, path):
        if obj is None:
            return (256 ** self.subcon.length) - 1
        else:
            return round(obj / self.resolution)


# TODO: is there a better way to calculate size of a nested struct?
def SwitchLength(type, switch, mapping, path, default=0):
    def rebuild(type, v):
        return Rebuild(type, lambda x: len(v.build(path(x))))

    return Switch(
        switch,
        {k: rebuild(type, v) for k, v in mapping.items()},
        default=Rebuild(type, lambda x: default),
    )


def RebuildLength(type, subcons, path):
    return Rebuild(type, lambda x: len(subcons.build(path(x))))


class MacAddressAdapter(Adapter):
    def _decode(self, obj, context, path):
        return ":".join(map("{:02x}".format, obj))

    def _encode(self, obj, context, path):
        return bytes(int(i, 16) for i in obj.split(":"))


class IpAddressAdapter(Adapter):
    def _decode(self, obj, context, path):
        return IPv4Address(obj)

    def _encode(self, obj, context, path):
        return bytes(int(i) for i in obj.split("."))


class DictAdapter(Adapter):
    def __init__(self, subcon, key, value):
        super().__init__(subcon)
        self.key = key
        self.value = value

    def _decode(self, obj, context, path):
        if isinstance(self.value, (list, tuple)):
            return {
                self.key(i): {v.__getfield__(): v(i) for v in self.value} for i in obj
            }

        return {self.key(i): self.value(i) for i in obj}

    def _encode(self, obj, context, path):
        key_name = self.key.__getfield__()

        if isinstance(self.value, (list, tuple)):
            for k, v in obj.items():
                yield {key_name: k, **v}
        else:
            value_name = self.value.__getfield__()
            for k, v in obj.items():
                yield {key_name: k, value_name: v}


class OpcodeMessage(Construct):
    OPCODE = Opcode()

    def __init__(self, opcodes):
        super().__init__()
        self.opcodes = {k: v.compile() for k, v in opcodes.items()}

    def _parse(self, stream, context, path):
        opcode = self.OPCODE._parse(stream, context, path)
        params = self.opcodes[opcode]._parse(stream, context, path)

        return Container(opcode=opcode, params=params)

    def _build(self, obj, stream, context, path):
        opcode = obj["opcode"]

        self.OPCODE._build(opcode, stream, context, path)
        self.opcodes[opcode]._build(obj["params"], stream, context, path)

        return obj

    def _sizeof(self, context, path):
        raise SizeofError

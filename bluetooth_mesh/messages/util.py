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
import math
import re
import sys
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
    Float32b,
    Float64b,
    Int8ub,
    Int16ub,
    Int24ub,
    Int32ub,
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
        type = enum
        _enum = enum

        def _decode(self, obj, context, path):
            if obj not in enum._value2member_map_:
                raise ValidationError("object failed validation: %s" % (obj,))
            return enum(obj)

        def _encode(self, obj, context, path):
            if obj == enum:
                return obj.value

            try:
                return enum[obj] if isinstance(obj, str) else enum(obj)
            except ValueError:
                raise ValidationError("object failed validation: %s" % (obj,))

    _EnumAdapter.__construct_doc__ = _Enum(subcon, enum)

    return _EnumAdapter(subcon)


def LogAdapter(subcon, *, max_value=None, infinity=False):
    class _LogAdapter(Adapter):
        MAX_TYPE_VALUE = int(math.pow(2, subcon.length * 8) - 1)
        _subcon = subcon

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


class FieldAdapter(Adapter):
    def __init__(self, subcon, field):
        self._subcon = field
        super().__init__(subcon)

    def _decode(self, obj, content, path):
        return obj

    def _encode(self, obj, content, path):
        return obj


def EmbeddedBitStruct(name, *fields, reversed=False):
    """
    Emulates BitStruct embedding:
        - for parsing, adds Computed accessor fields to the parent construct,
        - for building, Rebuild the bit struct using keys passed to the parent

    NOTE: This is a hack. Do not use unless you absolutely have to.
    """
    bit_struct = BitStruct(*fields)

    if reversed:
        bit_struct = Reversed(bit_struct)

    bit_struct.__construct_doc__ = Embedded(Struct(*fields))

    return (name / Rebuild(bit_struct, dict),) + tuple(
        field.name / FieldAdapter(Computed(this[name][field.name]), field)
        for field in fields
        if field.name is not None
    )


class Opcode(Construct):
    subcon = Int32ub

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
    _subcon = Float64b

    def __init__(self, subcon, rounding=None, resolution=1.0):
        super().__init__(subcon)
        self.rounding = rounding
        self.resolution = resolution

    def _decode(self, obj, content, path):
        if obj == (256 ** self.subcon.length) - 1:
            return float(sys.float_info.max)
        else:
            return (
                round(obj * self.resolution, self.rounding)
                if self.rounding
                else obj * self.resolution
            )

    def _encode(self, obj, content, path):
        if obj == float(sys.float_info.max):
            return (256 ** self.subcon.length) - 1
        else:
            return round(obj / self.resolution)


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


class AliasedContainer(Container):
    ALIAS = None
    ORIGINAL = None

    def __getattr__(self, name):
        if name == self.ORIGINAL:
            name = self.ALIAS

        return super().__getattr__(name)

    def __getitem__(self, name):
        if name == self.ORIGINAL:
            name = self.ALIAS

        return super().__getitem__(name)


class EnumSwitch(Switch):
    def _emitparse(self, code):
        fname = "factory_%s" % code.allocateId()
        code.append(
            "%s = {%s}"
            % (
                fname,
                ", ".join(
                    "%r : lambda io,this: %s" % (int(key), sc._compileparse(code))
                    for key, sc in self.cases.items()
                ),
            )
        )

        defaultfname = "compiled_%s" % code.allocateId()
        code.append(
            "%s = lambda io,this: %s"
            % (
                defaultfname,
                self.default._compileparse(code),
            )
        )
        return "%s.get(%s, %s)(io, this)" % (fname, self.keyfunc, defaultfname)


class SwitchStruct(Adapter):
    def __init__(self, key, switch):
        super().__init__(Struct(key, switch))
        self.key = key
        self.switch = switch
        self._subcon = Struct(key, switch.subcon)

    def _decode(self, obj, context, path):
        key = self.switch.keyfunc(obj)

        try:
            value = obj[self.switch.name]
        except KeyError:
            value = obj[key.name.lower()]

        class _Container(AliasedContainer):
            ORIGINAL = self.switch.name
            ALIAS = key.name.lower()

        return _Container({self.key.name: key, key.name.lower(): value})

    def _encode(self, obj, context, path):
        keytype = self.key.subcon.type
        key = keytype(self.switch.keyfunc(obj))

        try:
            value = obj[key.name.lower()]
        except KeyError:
            value = obj[self.switch.name]

        return Container({self.key.name: key, self.switch.name: value})

    def _emitparse(self, code):
        struct = self.subcon
        keytype = self.key.subcon.type

        fname = f"parse_struct_{code.allocateId()}"
        block = f"""
            def {fname}(io, this):
                from {keytype.__module__} import {keytype.__name__}

                key = {self.key._compileparse(code)}
                key_name = {keytype.__name__}(key).name.lower()

                result = Container()
                this = Container(_ = this, _params = this['_params'], _root = None, _parsing = True, _building = False, _sizing = False, _subcons = None, _io = io, _index = this.get('_index', None))
                this['_root'] = this['_'].get('_root', this)
                try:
                    result[{self.key.name!r}] = this[{self.key.name!r}] = key
                    result[key_name] = this[key_name] = {self.switch._compileparse(code)}
                except StopFieldError:
                    pass
                return result
        """
        code.append(block)
        return f"{fname}(io, this)"


class NameAdapter(Adapter):
    def _decode(self, obj, context, path):
        obj._name = self.subcon.name
        return obj

    def _encode(self, obj, context, path):
        return obj.get(self.subcon.name, obj)


class NamedSelect(Adapter):
    def __init__(self, **subconskw):
        subcons = list(NameAdapter(k / v.compile()) for k, v in subconskw.items())
        super().__init__(Select(*subcons))
        self._subcon = Select(**subconskw)

    def _decode(self, obj, context, path):
        return obj

    def _encode(self, obj, context, path):
        return obj


def camelcase(field_name):
    if field_name is None:
        return None

    head, *tail = str(field_name).lower().replace(" ", "_").split("_")
    return "".join([head, *(i.title() for i in tail)])


def snakecase(camel_input):
    words = re.findall(r"[A-Z]?[a-z]+|[A-Z]{2,}(?=[A-Z][a-z]|\d|\W|$)|\d+", camel_input)
    return "_".join(map(str.lower, words))


def to_case_dict(value, case):
    if isinstance(value, dict):
        new_dict = {
            case(k): to_case_dict(v, case)
            for k, v in value.items()
            if not k.startswith("_")
        }
        return {value["_name"]: new_dict} if "_name" in value else new_dict

    elif isinstance(value, list):
        return [to_case_dict(i, case) for i in value]

    elif isinstance(value, enum.Enum):
        return value.value

    elif isinstance(value, bytes):
        return value.hex()

    return value


def to_camelcase_dict(value):
    return to_case_dict(value, case=camelcase)


def to_snakecase_dict(value):
    return to_case_dict(value, case=snakecase)

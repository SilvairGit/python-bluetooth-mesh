#!python

import importlib
import math
import pkgutil
import sys
from collections import defaultdict
from dataclasses import dataclass
from enum import IntEnum
from functools import partial
from itertools import chain, count
from typing import Dict

from construct import (
    Adapter,
    Array,
    BitsInteger,
    Bytes,
    BytesInteger,
    Const,
    Construct,
    Default,
    FixedSized,
    Flag,
    FormatField,
    GreedyBytes,
    GreedyRange,
    NullStripped,
    Padded,
    Pass,
    Rebuild,
    Renamed,
    Restreamed,
    Select,
    StopIf,
    Struct,
    Switch,
    Transformed,
)

from bluetooth_mesh.messages import AccessMessage


class VariableNames:
    def __init__(self, root_name):
        self.names = {}
        self._load_names(root_name)

    def _load_names(self, root_name):
        root_module = importlib.import_module(root_name)

        for loader, name, is_pkg in pkgutil.walk_packages(root_module.__path__):
            module_name = f"{root_name}.{name}"
            module = importlib.import_module(module_name)
            self.names.update({id(v): k for k, v in module.__dict__.items()})

            if is_pkg:
                self._load_names(module_name)

    def __getitem__(self, item):
        return self.names.get(id(item))


names = VariableNames("bluetooth_mesh.messages")


def convert(
    con,
    visitor,
    field_name=None,
    struct_name=None,
    many=False,
    message_name=None,
):
    struct_name = struct_name or names[con] or f"{message_name}Params"

    if field_name and field_name.startswith("_"):
        return

    if isinstance(con, Struct):
        visitor.enter_struct(field_name, struct_name, many=many)

        for subcon in con.subcons:
            convert(subcon, visitor, message_name=message_name)

        visitor.exit()

    elif isinstance(con, Switch):
        if many:
            visitor.enter_struct(field_name, struct_name, many=many)
            visitor.enter_union(None)
        else:
            visitor.enter_union(field_name)

        for key, subcon in con.cases.items():
            if isinstance(key, IntEnum):
                key = type(key)(key).name

            convert(subcon, visitor, field_name=key, message_name=message_name)

        visitor.exit()

        if many:
            visitor.exit()

    elif isinstance(con, Select):
        if many:
            visitor.enter_struct(field_name, struct_name, many=many)
            visitor.enter_union(None)
        else:
            visitor.enter_union(field_name)

        for subcon in con.subcons:
            convert(
                subcon,
                visitor,
                message_name=message_name,
            )

        visitor.exit()

        if many:
            visitor.exit()

    elif isinstance(con, Renamed):
        convert(
            con.subcon,
            visitor,
            field_name=con.name,
            message_name=message_name,
            many=many,
        )

    elif isinstance(con, (GreedyRange, Array)):
        convert(
            con.subcon,
            visitor,
            field_name=field_name,
            # struct_name=struct_name,
            many=True,
            message_name=message_name,
        )

    elif con is Pass:
        return

    elif isinstance(con, StopIf):
        return

    elif isinstance(con, Construct):
        subcon = getattr(con, "_subcon", getattr(con, "subcon", None))
        if subcon is None:
            visitor.field(con, field_name, struct_name, many=many)
            return

        convert(
            subcon,
            visitor,
            field_name=field_name,
            struct_name=struct_name,
            message_name=message_name,
            many=many,
        )

    else:
        raise TypeError


class Visitor:
    def __init__(self, struct_name):
        self.types = {}
        self.structs = defaultdict(dict)

        struct_fields = self.structs.setdefault(struct_name, {})
        self.stack = [(struct_name, struct_fields)]
        self._has_union = False

    @property
    def current(self):
        field_name, struct_fields = self.stack[-1]
        return struct_fields

    @staticmethod
    def _camelcase(field_name):
        if field_name is None:
            return None

        head, *tail = str(field_name).lower().replace(" ", "_").split("_")
        return "".join([head, *(i.title() for i in tail)])

    @staticmethod
    def make_type(con):
        FORMAT_FIELD_TYPES = dict(
            c="UInt8",
            b="Int8",
            B="UInt8",
            h="Int16",
            H="UInt16",
            i="Int32",
            I="UInt32",
            l="Int32",
            L="UInt32",
            q="Int64",
            Q="UInt64",
            f="Float32",
            d="Float64",
        )

        if isinstance(con, Bytes) or con is GreedyBytes:
            return f"Data"

        elif isinstance(con, FormatField):
            return FORMAT_FIELD_TYPES[con.fmtstr[1:]]

        elif isinstance(con, BitsInteger):
            width = max(2 ** math.ceil(math.log2(con.length)), 8)
            return f"Int{width}" if con.signed else f"UInt{width}"

        elif isinstance(con, BytesInteger):
            width = max(2 ** math.ceil(math.log2(con.length * 8)), 8)
            return f"Int{width}" if con.signed else f"UInt{width}"

        elif con is Flag:
            return "Bool"

    def enter_struct(self, field_name="", struct_name="", many=False):
        field_name = self._camelcase(field_name)

        self.current[field_name] = f"List({struct_name})" if many else struct_name
        struct_fields = self.structs.setdefault(struct_name, {})
        self.stack.append((struct_name, struct_fields))

    def enter_union(self, field_name=""):
        self._has_union = True
        field_name = self._camelcase(field_name)

        union_fields = self.current.setdefault(field_name, {})
        self.stack.append((field_name, union_fields))

    def exit(self):
        if len(self.stack) == 3:
            if not self._has_union:
                struct_name, struct_fields = self.stack[-1]
                self.types[struct_name] = struct_fields
                self.structs.pop(struct_name)

            self._has_union = False

        self.stack.pop(-1)

    def items(self):
        return chain(self.types.items(), self.structs.items())

    def field(self, con, field_name, struct_name, many=False):
        field_name = self._camelcase(field_name)

        type_name = self.make_type(con) or struct_name

        if many:
            type_name = f"List({type_name})"

        self.current[field_name] = type_name


def generate(protocol_id, file=sys.stdout):
    _print = partial(print, file=file, flush=True)
    visitor = Visitor("AccessMessage")

    for opcode, message in AccessMessage.OPCODES.items():
        convert(message, visitor, field_name=names[opcode], message_name=names[message])

    visitor.structs["AccessMessage"] = {"opcode": "UInt32", None: {}}

    for opcode, message in AccessMessage.OPCODES.items():
        message_fields = visitor.structs.pop(
            names[message], visitor.types.get(names[message])
        )
        if (
            message_fields
            and None in message_fields
            and isinstance(message_fields[None], dict)
        ):
            visitor.structs["AccessMessage"][None].update(message_fields[None])

    _print(f"@0x{protocol_id:x};")
    _print("")

    def describe(struct_fields, field_tag=None, level=1):
        field_tag = field_tag or count()

        for field_name, field_type in struct_fields.items():
            if isinstance(field_type, dict):
                if field_name:
                    _print(" " * (level * 4 - 1), f"{field_name} :union {{")
                else:
                    _print(" " * (level * 4 - 1), f"union {{")

                describe(field_type, field_tag, level + 1)

                _print(" " * (level * 4 - 1), f"}}")
            else:
                _print(
                    " " * (level * 4 - 1),
                    f"{field_name} @{next(field_tag)} :{field_type};",
                    file=file,
                )

    for struct_name, struct_fields in visitor.items():
        _print(f"struct {struct_name} {{")
        describe(struct_fields)
        _print("}")
        _print("")


if __name__ == "__main__":
    generate(0xD988DA1AAFBE9E47)

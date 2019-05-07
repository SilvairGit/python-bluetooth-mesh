from construct import (
    Bit, Int8ub, Int16ub, Int24ub,
    Adapter, Bitwise, Restreamed, Rebuild, Select, Switch,
    ExprValidator, ValidationError, obj_
)

__all__ = ('Reversed', 'RebuildLength', 'SwitchLength', 'MacAddressAdapter', 'BitList')


def identity(x):
    return x


def reverse(sequence):
    return sequence[::-1]


def Reversed(subcon):
    return Restreamed(
        subcon,
        reverse, subcon.sizeof(),
        reverse, subcon.sizeof(),
        identity
    )


# TODO: is there a better way to calculate size of a nested struct?
def SwitchLength(type, switch, mapping, path, default=0):
    def rebuild(type, v):
        return Rebuild(type, lambda x: len(v.build(path(x))))

    return Switch(
        switch,
        {k: rebuild(type, v) for k, v in mapping.items()},
        default=Rebuild(type, lambda x: default)
    )


def RebuildLength(type, subcons, path):
    return Rebuild(type, lambda x: len(subcons.build(path(x))))


class MacAddressAdapter(Adapter):
    def _decode(self, obj, context, path):
        return ':'.join(map('{:02x}'.format, obj))

    def _encode(self, obj, context, path):
        return bytes(int(i, 16) for i in obj.split(':'))


class BitListAdapter(Adapter):
    def _decode(self, obj, content, path):
        bits = set()

        for bit, feature in enumerate(obj):
            if not feature:
                continue

            bits.add(bit)

        return bits

    def _encode(self, obj, content, path):
        bits = []

        for bit in range(self.sizeof() * 8):
            bits.append(bit in obj)

        return bits


def BitList(size):
    return BitListAdapter(Bitwise(Bit[size * 8]))


def EnumAdapter(subcon, enum):
    class _EnumAdapter(Adapter):
        def _decode(self, obj, context, path):
            if obj not in enum._value2member_map_:
                raise ValidationError("object failed validation: %s" % (obj,))
            return enum(obj)

        def _encode(self, obj, context, path):
            if obj in enum:
                return obj.value

            try:
                return enum(obj)
            except ValueError:
                raise ValidationError("object failed validation: %s" % (obj,))

    return _EnumAdapter(subcon)


Opcode = Select(
    ExprValidator(
        Int8ub,
        (obj_ != 0x7F) and (obj_ >> 7 == 0)
    ),
    ExprValidator(
        Int16ub,
        (obj_ >> 14 == 2)
    ),
    ExprValidator(
        Int24ub,
        (obj_ >> 22 == 3)
    ),
)

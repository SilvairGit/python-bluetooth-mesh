from construct import (
    Bit, Int8ub, Int16ub, Int24ub,
    Adapter, Bitwise, Restreamed, Rebuild, Select, Switch,
    ExprValidator, ValidationError, obj_
)


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

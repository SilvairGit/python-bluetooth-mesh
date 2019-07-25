from construct import (
    Adapter, BitsInteger, BitStruct, ExprValidator
)

TransitionTime = BitStruct(
    "steps" / ExprValidator(BitsInteger(6), lambda obj, ctx: obj <= 0x3E),
    "resolution" / BitsInteger(2)
)


class Delay(Adapter):
    def _decode(self, obj, context, path):
        return obj/200

    def _encode(self, obj, context, path):
        return int(obj*200)

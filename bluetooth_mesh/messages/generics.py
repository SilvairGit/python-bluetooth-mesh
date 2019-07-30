from construct import (
    Adapter, BitsInteger, BitStruct, ExprValidator
)

TransitionTime = BitStruct(
    "steps" / ExprValidator(BitsInteger(6), lambda obj, ctx: obj <= 0x3E),
    "resolution" / BitsInteger(2)
)


class TransitionTimeAdapter(Adapter):
    RES = [0.1, 1, 10, 10*60]

    def _decode(self, obj, context, path):
        return obj['steps']*self.RES[obj['resolution']]

    def _encode(self, obj, context, path):
        res = None
        for r in self.RES:
            if obj < r*62:
                res = r
                break

        steps = obj/res

        return dict(steps=int(steps), resolution=self.RES.index(res))


class Delay(Adapter):
    def _decode(self, obj, context, path):
        return obj/200

    def _encode(self, obj, context, path):
        return int(obj*200)

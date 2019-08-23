from construct import (
    Adapter, BitsInteger, BitStruct, Struct, Int8ul
)

TransitionTime = BitStruct(
    "resolution" / BitsInteger(2),
    "steps" / BitsInteger(6)
)


class TransitionTimeAdapter(Adapter):
    RESOLUTION = {0b00: 0.1, 0b01: 1, 0b10: 10, 0b11: 10 * 60}

    def __init__(self, subcon, allow_unknown=False):
        self.max_steps = 0x3f if allow_unknown else 0x3e
        super().__init__(subcon)

    def _decode(self, obj, context, path):
        return obj['steps'] * self.RESOLUTION[obj['resolution']]

    def _encode(self, obj, context, path):
        resolution = None
        steps = None
        for range_index, range_value in self.RESOLUTION.items():
            if obj <= range_value * 0x3f:
                resolution = range_index
                steps = obj / range_value
                assert round(steps, 0) <= self.max_steps, "Unknown not allowed"
                break

        assert resolution is not None

        return dict(steps=int(steps), resolution=resolution)


class Delay(Adapter):
    def _decode(self, obj, context, path):
        return obj/200

    def _encode(self, obj, context, path):
        return int(obj*200)


OptionalSetParameters = Struct(
    "transition_time" / TransitionTimeAdapter(TransitionTime, allow_unknown=False),
    "delay" / Delay(Int8ul)
)

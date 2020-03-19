from functools import partial

from bluetooth_mesh.messages.health import HealthOpcode


async def attention_unack(self, destination, app_index, attention):
    # create a argument-less callable that sends an application message
    request = partial(
        self.send_app,
        destination,
        app_index=app_index,
        opcode=HealthOpcode.ATTENTION_SET_UNACKNOWLEDGED,
        params=dict(
            attention=attention,
        )
    )

    # send 3 *repeated* messages with 0.5s interval
    await self.repeat(request, retransmissions=3, send_interval=0.5)

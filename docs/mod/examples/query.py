from functools import partial

from bluetooth_mesh.crypto import ApplicationKey
from bluetooth_mesh.messages.config import ConfigOpcode


async def add_app_key(self,
                      destination: int,
                      net_index: int,
                      app_key_index: int,
                      net_key_index: int,
                      app_key: ApplicationKey):

    # create a Future that gets completed when APPKEY_STATUS is received
    status = self.expect_dev(
        destination,
        net_index=net_index,
        opcode=ConfigOpcode.APPKEY_STATUS,
        params=dict(
            app_key_index=app_key_index,
            net_key_index=net_key_index,
        )
    )

    # each request is the same, just keep retransmitting APPKEY_ADD
    request = partial(
        self.send_dev,
        destination,
        net_index=net_index,
        opcode=ConfigOpcode.APPKEY_ADD,
        params=dict(
            app_key_index=app_key_index,
            net_key_index=net_key_index,
            app_key=app_key.bytes,
        )
    )

    return await self.query(request, status, timeout=1.0)

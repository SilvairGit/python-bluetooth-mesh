from functools import partial

from bluetooth_mesh.messages.debug import DebugOpcode, DebugSubOpcode


async def get_uptime(self, nodes, net_index):
    # dictionary of request callables
    requests = {
        node: partial(
            self.send_dev,
            node,
            net_index=net_index,
            opcode=DebugOpcode.SILVAIR_DEBUG,
            params=dict(subopcode=DebugSubOpcode.UPTIME_GET)
        ) for node in nodes
    }

    # dictionary of Futures
    statuses = {
        node: self.expect_dev(
            node,
            net_index=0,
            opcode=DebugOpcode.SILVAIR_DEBUG,
            params=dict(subopcode=DebugSubOpcode.UPTIME_STATUS)
        ) for node in nodes
    }

    return await self.bulk_query(requests,
                                 statuses,
                                 send_interval=0.1,
                                 timeout=5.0)

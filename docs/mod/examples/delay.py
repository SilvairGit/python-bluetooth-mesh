from bluetooth_mesh.messages.generic.onoff import GenericOnOffOpcode


async def set_onoff_unack(self, destination, app_index, onoff):
    SEND_INTERVAL = 0.075

    # create a mutable state for `request` closure
    state = dict(delay=0.5)

    async def request():
        # for each call, send a message with current delay
        await self.send_app(
            destination,
            app_index=app_index,
            opcode=GenericOnOffOpcode.ONOFF_SET,
            params=dict(
                onoff=onoff,
                tid=42,
                transition_time=0,
                delay=state["delay"]
            )
        )

        # ... then decrease the delay by send_interval
        state["delay"] = max(0, state['delay'] - SEND_INTERVAL)

    # send 3 *different* messages with 0.075s interval:
    #  - 1st with delay 0.5
    #  - 2nd with delay 0.425
    #  - 3rd with delay 0.35
    await self.repeat(request, retransmissions=3, send_interval=SEND_INTERVAL)

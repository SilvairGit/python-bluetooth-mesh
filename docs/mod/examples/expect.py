from bluetooth_mesh.messages.generic.onoff import GenericOnOffOpcode
from bluetooth_mesh.models import Model


class MyModel(Model):
    MODEL_ID = (None, 0x1002)
    OPCODES = [
        GenericOnOffOpcode.ONOFF_SET,
    ]

    async def app_onoff_set_task(self):
        while True:
            level_set = await self.expect_app(
                source=0x0042,
                app_index=0,
                destination=None,
                opcode=GenericOnOffOpcode.ONOFF_SET,
                params={}
            )

    async def dev_onoff_set_task(self):
        while True:
            level_set = await self.expect_dev(
                source=0x0042,
                net_index=0,
                opcode=GenericOnOffOpcode.ONOFF_SET,
                params={}
            )

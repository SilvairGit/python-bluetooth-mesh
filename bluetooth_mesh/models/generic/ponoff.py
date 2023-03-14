#
# python-bluetooth-mesh - Bluetooth Mesh for Python
#
# Copyright (C) 2023  Alexander Ozumenko
#
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
#
"""
This module implements Generic OnPowerUp models, both clients and servers
"""
from functools import partial
from typing import Any, Dict, Iterable, NamedTuple, Optional, Sequence, Tuple, Type

from bluetooth_mesh.models.base import Model
from bluetooth_mesh.messages.generic.ponoff import (
    GenericPowerOnOffOpcode,
    GenericPowerOnOffSetupOpcode,
    GenericOnPowerUp,
)

__all__ = [
    "GenericPowerOnOffServer",
    "GenericPowerOnOffSetupServer",
    "GenericPowerOnOffClient",
]


class GenericPowerOnOffServer(Model):
    MODEL_ID = (None, 0x1006)
    OPCODES = {
        GenericPowerOnOffOpcode.GENERIC_ON_POWERUP_GET,
    }
    PUBLISH = True
    SUBSCRIBE = True


class GenericPowerOnOffSetupServer(Model):
    MODEL_ID = (None, 0x1007)
    OPCODES = {
        GenericPowerOnOffSetupOpcode.GENERIC_ON_POWERUP_SET,
        GenericPowerOnOffSetupOpcode.GENERIC_ON_POWERUP_SET_UNACKNOWLEDGED,
    }
    PUBLISH = True
    SUBSCRIBE = True


class GenericPowerOnOffClient(Model):
    MODEL_ID = (None, 0x1008)
    OPCODES = {
        GenericPowerOnOffOpcode.GENERIC_ON_POWERUP_STATUS,
    }
    PUBLISH = True
    SUBSCRIBE = True


    async def get(
        self,
        nodes: Sequence[int],
        app_index: int,
        *,
        send_interval: Optional[float] = None,
        timeout: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        return await self.client_simple_get(
            nodes=nodes,
            app_index=app_index,
            request_opcode=GenericPowerOnOffOpcode.GENERIC_ON_POWERUP_GET,
            status_opcode= GenericPowerOnOffOpcode.GENERIC_ON_POWERUP_STATUS,
            send_interval=send_interval,
            timeout=timeout)

    async def set(
        self,
        nodes: Sequence[int],
        app_index: int,
        on_power_up: GenericOnPowerUp,
        *,
        send_interval: Optional[float] = None,
        timeout: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        params = dict(
            on_power_up=on_power_up,
        )
        return await self.client_simple_set(
            nodes=nodes,
            app_index=app_index,
            request_opcode=GenericPowerOnOffSetupOpcode.GENERIC_ON_POWERUP_SET,
            status_opcode=GenericPowerOnOffOpcode.GENERIC_ON_POWERUP_STATUS,
            params=params,
            send_interval=send_interval,
            timeout=timeout,
        )

    async def set_unack(
        self,
        destination: int,
        app_index: int,
        on_power_up: GenericOnPowerUp,
        *,
        retransmissions: Optional[int] = None,
        send_interval: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        params = dict(
            on_power_up=on_power_up,
        )
        await self.client_simple_set_unack(
            destination=destination,
            app_index=app_index,
            request_opcode=GenericPowerOnOffSetupOpcode.GENERIC_ON_POWERUP_SET_UNACKNOWLEDGED,
            params=params,
            retransmissions=retransmissions,
            send_interval=send_interval,
        )

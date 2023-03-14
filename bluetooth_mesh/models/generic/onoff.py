#
# python-bluetooth-mesh - Bluetooth Mesh for Python
#
# Copyright (C) 2019  SILVAIR sp. z o.o.
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
This module implements GenericOnOff mesh model, both client and server
"""
from functools import partial
from typing import Any, Dict, Iterable, NamedTuple, Optional, Sequence, Tuple, Type

from bluetooth_mesh.models.base import Model
from bluetooth_mesh.messages.generic.onoff import GenericOnOffOpcode

__all__ = [
    "GenericOnOffServer",
    "GenericOnOffClient",
]



class GenericOnOffServer(Model):
    MODEL_ID = (None, 0x1000)
    OPCODES = {
        GenericOnOffOpcode.GENERIC_ONOFF_GET,
        GenericOnOffOpcode.GENERIC_ONOFF_SET,
        GenericOnOffOpcode.GENERIC_ONOFF_SET_UNACKNOWLEDGED,
    }
    PUBLISH = True
    SUBSCRIBE = True


class GenericOnOffClient(Model):
    MODEL_ID = (None, 0x1001)
    OPCODES = {
        GenericOnOffOpcode.GENERIC_ONOFF_STATUS,
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
            request_opcode=GenericOnOffOpcode.GENERIC_ONOFF_GET,
            status_opcode=GenericOnOffOpcode.GENERIC_ONOFF_STATUS,
            send_interval=send_interval,
            timeout=timeout)

    async def set(
        self,
        nodes: Sequence[int],
        app_index: int,
        onoff: int,
        transition_time: float = 0,
        *,
        send_interval: Optional[float] = None,
        timeout: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        params = dict(
            onoff=onoff,
            tid=self.tid(),
            transition_time=transition_time,
            delay=0,
        )
        return await self.client_simple_set(
            nodes=nodes,
            app_index=app_index,
            request_opcode=GenericOnOffOpcode.GENERIC_ONOFF_SET,
            status_opcode=GenericOnOffOpcode.GENERIC_ONOFF_STATUS,
            params=params,
            send_interval=send_interval,
            timeout=timeout,
        )

    async def set_unack(
        self,
        destination: int,
        app_index: int,
        onoff: int,
        transition_time: float = 0,
        *,
        delay: Optional[float] = None,
        retransmissions: Optional[int] = None,
        send_interval: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        params = dict(
            onoff=onoff,
            tid=self.tid(),
            transition_time=transition_time,
        )
        await self.client_delay_set_unack(
            destination=destination,
            app_index=app_index,
            request_opcode=GenericOnOffOpcode.GENERIC_ONOFF_SET_UNACKNOWLEDGED,
            params=params,
            delay=delay,
            retransmissions=retransmissions,
            send_interval=send_interval,
        )

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
This module implements mesh models, both clients and servers.
"""
from functools import partial
from typing import Any, Dict, Iterable, NamedTuple, Optional, Sequence, Tuple, Type

from bluetooth_mesh.models.base import Model
from bluetooth_mesh.messages.generic.level import GenericLevelOpcode


__all__ = [
    "GenericLevelServer",
    "GenericLevelClient",
]


class GenericLevelServer(Model):
    MODEL_ID = (None, 0x1002)
    OPCODES = {
        GenericLevelOpcode.GENERIC_LEVEL_GET,
        GenericLevelOpcode.GENERIC_LEVEL_SET,
        GenericLevelOpcode.GENERIC_LEVEL_SET_UNACKNOWLEDGED,
        GenericLevelOpcode.GENERIC_LEVEL_STATUS,
        GenericLevelOpcode.GENERIC_DELTA_SET,
        GenericLevelOpcode.GENERIC_DELTA_SET_UNACKNOWLEDGED,
        GenericLevelOpcode.GENERIC_MOVE_SET,
        GenericLevelOpcode.GENERIC_MOVE_SET_UNACKNOWLEDGED,
    }
    PUBLISH = True
    SUBSCRIBE = True


class GenericLevelClient(Model):
    MODEL_ID = (None, 0x1003)
    OPCODES = {
        GenericLevelOpcode.GENERIC_LEVEL_STATUS,
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
            request_opcode=GenericLevelOpcode.GENERIC_LEVEL_GET,
            status_opcode=GenericLevelOpcode.GENERIC_LEVEL_STATUS,
            send_interval=send_interval,
            timeout=timeout)

    async def set(
        self,
        nodes: Sequence[int],
        app_index: int,
        level: int,
        transition_time: float = 0,
        *,
        send_interval: Optional[float] = None,
        timeout: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        params = dict(
            level=level,
            tid=self.tid(),
            transition_time=transition_time,
            delay=0,
        )
        return await self.client_simple_set(
            nodes=nodes,
            app_index=app_index,
            request_opcode=GenericLevelOpcode.GENERIC_LEVEL_SET,
            status_opcode=GenericLevelOpcode.GENERIC_LEVEL_STATUS,
            params=params,
            send_interval=send_interval,
            timeout=timeout,
        )

    async def set_unack(
        self,
        destination: int,
        app_index: int,
        level: int,
        transition_time: float = 0,
        *,
        delay: Optional[float] = None,
        retransmissions: Optional[int] = None,
        send_interval: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        params = dict(
            level=level,
            tid=self.tid(),
            transition_time=transition_time,
        )
        await self.client_delay_set_unack(
            destination=destination,
            app_index=app_index,
            request_opcode=GenericLevelOpcode.GENERIC_LEVEL_SET_UNACKNOWLEDGED,
            params=params,
            delay=delay,
            retransmissions=retransmissions,
            send_interval=send_interval,
        )

    async def delta_set(
        self,
        nodes: Sequence[int],
        app_index: int,
        delta_level: int,
        transition_time: float = 0,
        *,
        send_interval: Optional[float] = None,
        timeout: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        params = dict(
            delta_level=delta_level,
            tid=self.tid(),
            transition_time=transition_time,
            delay=0,
        )
        return await self.client_simple_set(
            nodes=nodes,
            app_index=app_index,
            request_opcode=GenericLevelOpcode.GENERIC_DELTA_SET,
            status_opcode=GenericLevelOpcode.GENERIC_LEVEL_STATUS,
            params=params,
            send_interval=send_interval,
            timeout=timeout,
        )

    async def delta_set_unack(
        self,
        destination: int,
        app_index: int,
        delta_level: int,
        transition_time: float = 0,
        *,
        delay: Optional[float] = None,
        retransmissions: Optional[int] = None,
        send_interval: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        params = dict(
            delta_level=delta_level,
            tid=self.tid(),
            transition_time=transition_time,
        )
        await self.client_delay_set_unack(
            destination=destination,
            app_index=app_index,
            request_opcode=GenericLevelOpcode.GENERIC_DELTA_SET_UNACKNOWLEDGED,
            params=params,
            delay=delay,
            retransmissions=retransmissions,
            send_interval=send_interval,
        )

    async def move_set(
        self,
        nodes: Sequence[int],
        app_index: int,
        delta_level: int,
        transition_time: float = 0,
        *,
        send_interval: Optional[float] = None,
        timeout: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        params = dict(
            delta_level=delta_level,
            tid=self.tid(),
            transition_time=transition_time,
            delay=0,
        )
        return await self.client_simple_set(
            nodes=nodes,
            app_index=app_index,
            request_opcode=GenericLevelOpcode.GENERIC_MOVE_SET,
            status_opcode=GenericLevelOpcode.GENERIC_LEVEL_STATUS,
            params=params,
            send_interval=send_interval,
            timeout=timeout,
        )

    async def move_set_unack(
        self,
        destination: int,
        app_index: int,
        delta_level: int,
        transition_time: float = 0,
        *,
        delay: Optional[float] = None,
        retransmissions: Optional[int] = None,
        send_interval: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        params = dict(
            delta_level=delta_level,
            tid=self.tid(),
            transition_time=transition_time,
        )
        await self.client_delay_set_unack(
            destination=destination,
            app_index=app_index,
            request_opcode=GenericLevelOpcode.GENERIC_MOVE_SET_UNACKNOWLEDGED,
            params=params,
            delay=delay,
            retransmissions=retransmissions,
            send_interval=send_interval,
        )

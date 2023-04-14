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
This module implements Scene mesh models, both clients and servers.
"""
from functools import partial
from typing import Any, Dict, Iterable, NamedTuple, Optional, Sequence, Tuple, Type

from bluetooth_mesh.models.base import Model
from bluetooth_mesh.messages.scene import SceneOpcode


__all__ = [
    "SceneServer",
    "SceneClient",
]


class SceneServer(Model):
    MODEL_ID = (None, 0x1204)
    OPCODES = {
        SceneOpcode.SCENE_GET,
        SceneOpcode.SCENE_RECALL,
        SceneOpcode.SCENE_RECALL_UNACKNOWLEDGED,
        SceneOpcode.SCENE_REGISTER_GET,
        SceneOpcode.SCENE_STORE,
        SceneOpcode.SCENE_STORE_UNACKNOWLEDGED,
        SceneOpcode.SCENE_DELETE,
        SceneOpcode.SCENE_DELETE_UNACKNOWLEDGED,
    }
    PUBLISH = True
    SUBSCRIBE = True



class SceneClient(Model):
    MODEL_ID = (None, 0x1205)
    OPCODES = {
        SceneOpcode.SCENE_STATUS,
        SceneOpcode.SCENE_REGISTER_STATUS,
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
            request_opcode=SceneOpcode.SCENE_GET,
            status_opcode=SceneOpcode.SCENE_STATUS,
            send_interval=send_interval,
            timeout=timeout)

    async def recall(
        self,
        nodes: Sequence[int],
        app_index: int,
        scene_number: int,
        transition_time: float = 0,
        *,
        send_interval: Optional[float] = None,
        timeout: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        params = dict(
            scene_number=scene_number,
            tid=self.tid(),
            transition_time=transition_time,
            delay=0,
        )
        return await self.client_simple_set(
            nodes=nodes,
            app_index=app_index,
            request_opcode=SceneOpcode.SCENE_RECALL,
            status_opcode=SceneOpcode.SCENE_STATUS,
            params=params,
            send_interval=send_interval,
            timeout=timeout,
        )

    async def recall_unack(
        self,
        destination: int,
        app_index: int,
        scene_number: int,
        transition_time: float = 0,
        *,
        delay: Optional[float] = None,
        retransmissions: Optional[int] = None,
        send_interval: Optional[float] = None
    ) -> None:
        params = dict(
            scene_number=scene_number,
            tid=self.tid(),
            transition_time=transition_time,
        )
        await self.client_delay_set_unack(
            destination=destination,
            app_index=app_index,
            request_opcode=SceneOpcode.SCENE_RECALL_UNACKNOWLEDGED,
            params=params,
            delay=delay,
            retransmissions=retransmissions,
            send_interval=send_interval,
        )

    async def register_get(
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
            request_opcode=SceneOpcode.SCENE_REGISTER_GET,
            status_opcode=SceneOpcode.SCENE_REGISTER_STATUS,
            send_interval=send_interval,
            timeout=timeout)

    async def store(
        self,
        nodes: Sequence[int],
        app_index: int,
        scene_number: int,
        transition_time: float = 0,
        *,
        send_interval: Optional[float] = None,
        timeout: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        params = dict(
            scene_number=scene_number
        )
        return await self.client_simple_set(
            nodes=nodes,
            app_index=app_index,
            request_opcode=SceneOpcode.SCENE_STORE,
            status_opcode=SceneOpcode.SCENE_REGISTER_STATUS,
            params=params,
            send_interval=send_interval,
            timeout=timeout,
        )

    async def store_unack(
        self,
        destination: int,
        app_index: int,
        scene_number: int,
        *,
        retransmissions: Optional[int] = None,
        send_interval: Optional[float] = None
    ) -> None:
        params = dict(
            on_power_up=on_power_up,
        )
        await self.client_simple_set_unack(
            destination=destination,
            app_index=app_index,
            request_opcode=SceneOpcode.SCENE_STORE_UNACKNOWLEDGED,
            params=params,
            retransmissions=retransmissions,
            send_interval=send_interval,
        )

    async def delete(
        self,
        nodes: Sequence[int],
        app_index: int,
        scene_number: int,
        transition_time: float = 0,
        *,
        send_interval: Optional[float] = None,
        timeout: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        params = dict(
            scene_number=scene_number
        )
        return await self.client_simple_set(
            nodes=nodes,
            app_index=app_index,
            request_opcode=SceneOpcode.SCENE_DELETE,
            status_opcode=SceneOpcode.SCENE_REGISTER_STATUS,
            params=params,
            send_interval=send_interval,
            timeout=timeout,
        )

    async def delete_unack(
        self,
        destination: int,
        app_index: int,
        scene_number: int,
        *,
        retransmissions: Optional[int] = None,
        send_interval: Optional[float] = None
    ) -> None:
        params = dict(
            on_power_up=on_power_up,
        )
        await self.client_simple_set_unack(
            destination=destination,
            app_index=app_index,
            request_opcode=SceneOpcode.SCENE_STORE_UNACKNOWLEDGED,
            params=params,
            retransmissions=retransmissions,
            send_interval=send_interval,
        )

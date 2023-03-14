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
This module implements Light CTL mesh models, both clients and servers.
"""
from functools import partial
from typing import Any, Dict, Iterable, NamedTuple, Optional, Sequence, Tuple, Type

from bluetooth_mesh.models.base import Model
from bluetooth_mesh.messages.light.ctl import (
    LightCTLOpcode,
    LightCTLSetupOpcode,
)

__all__ = [
    "LightCTLServer",
    "LightCTLSetupServer",
    "LightCTLTemperatureServer",
    "LightCTLClient",
]


class LightCTLServer(Model):
    MODEL_ID = (None, 0x1303)
    OPCODES = {
        LightCTLOpcode.LIGHT_CTL_GET,
        LightCTLOpcode.LIGHT_CTL_SET,
        LightCTLOpcode.LIGHT_CTL_SET_UNACKNOWLEDGED,
        LightCTLOpcode.LIGHT_CTL_STATUS,
    }
    PUBLISH = True
    SUBSCRIBE = True


class LightCTLSetupServer(Model):
    MODEL_ID = (None, 0x1304)
    OPCODES = {
        LightCTLSetupOpcode.LIGHT_CTL_SETUP_TEMPERATURE_DEFAULT_SET,
        LightCTLSetupOpcode.LIGHT_CTL_SETUP_TEMPERATURE_DEFAULT_SET_UNACKNOWLEDGED,
        LightCTLSetupOpcode.LIGHT_CTL_SETUP_TEMPERATURE_RANGE_SET,
        LightCTLSetupOpcode.LIGHT_CTL_SETUP_TEMPERATURE_RANGE_SET_UNACKNOWLEDGED,
    }
    PUBLISH = True
    SUBSCRIBE = True


class LightCTLTemperatureServer(Model):
    MODEL_ID = (None, 0x1306)
    OPCODES = {
        LightCTLOpcode.LIGHT_CTL_TEMPERATURE_GET,
        LightCTLOpcode.LIGHT_CTL_TEMPERATURE_RANGE_GET,
        LightCTLOpcode.LIGHT_CTL_TEMPERATURE_RANGE_STATUS,
        LightCTLOpcode.LIGHT_CTL_TEMPERATURE_SET,
        LightCTLOpcode.LIGHT_CTL_TEMPERATURE_SET_UNACKNOWLEDGED,
        LightCTLOpcode.LIGHT_CTL_TEMPERATURE_STATUS,
        LightCTLOpcode.LIGHT_CTL_TEMPERATURE_DEFAULT_GET,
        LightCTLOpcode.LIGHT_CTL_TEMPERATURE_DEFAULT_STATUS,
    }
    PUBLISH = True
    SUBSCRIBE = True


class LightCTLClient(Model):
    MODEL_ID = (None, 0x1305)
    OPCODES = {
        LightCTLOpcode.LIGHT_CTL_STATUS,
        LightCTLOpcode.LIGHT_CTL_TEMPERATURE_STATUS,
        LightCTLOpcode.LIGHT_CTL_TEMPERATURE_RANGE_STATUS,
        LightCTLOpcode.LIGHT_CTL_TEMPERATURE_DEFAULT_STATUS,
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
            request_opcode=LightCTLOpcode.LIGHT_CTL_GET,
            status_opcode=LightCTLOpcode.LIGHT_CTL_STATUS,
            send_interval=send_interval,
            timeout=timeout)

    async def set(
        self,
        nodes: Sequence[int],
        app_index: int,
        ctl_lightness: int,
        ctl_temperature: int,
        ctl_delta_uv: int,
        transition_time: float = 0,
        *,
        send_interval: Optional[float] = None,
        timeout: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        params = dict(
            ctl_lightness=ctl_lightness,
            ctl_temperature=ctl_temperature,
            ctl_delta_uv=ctl_delta_uv,
            tid=self.tid(),
            delay=0,
            transition_time=transition_time,
        )
        return await self.client_simple_set(
            nodes=nodes,
            app_index=app_index,
            request_opcode=LightCTLOpcode.LIGHT_CTL_SET,
            status_opcode=LightCTLOpcode.LIGHT_CTL_STATUS,
            params=params,
            send_interval=send_interval,
            timeout=timeout,
        )

    async def set_unack(
        self,
        destination: int,
        app_index: int,
        ctl_lightness: int,
        ctl_temperature: int,
        ctl_delta_uv: int,
        transition_time: float = 0,
        *,
        delay: Optional[float] = None,
        retransmissions: Optional[int] = None,
        send_interval: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        params = dict(
            ctl_lightness=ctl_lightness,
            ctl_temperature=ctl_temperature,
            ctl_delta_uv=ctl_delta_uv,
            tid = self.tid(),
            transition_time=transition_time,
        )
        await self.client_delay_set_unack(
            destination=destination,
            app_index=app_index,
            request_opcode=LightCTLOpcode.LIGHT_CTL_SET_UNACKNOWLEDGED,
            params=params,
            delay=delay,
            retransmissions=retransmissions,
            send_interval=send_interval,
        )

    async def temperature_get(
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
            request_opcode=LightCTLOpcode.LIGHT_CTL_TEMPERATURE_GET,
            status_opcode=LightCTLOpcode.LIGHT_CTL_TEMPERATURE_STATUS,
            send_interval=send_interval,
            timeout=timeout)

    async def temperature_set(
        self,
        nodes: Sequence[int],
        app_index: int,
        ctl_temperature: int,
        ctl_delta_uv: int,
        transition_time: float = 0,
        *,
        send_interval: Optional[float] = None,
        timeout: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        params = dict(
            ctl_temperature=ctl_temperature,
            ctl_delta_uv=ctl_delta_uv,
            tid=self.tid(),
            delay=0,
            transition_time=transition_time,
        )
        return await self.client_simple_set(
            nodes=nodes,
            app_index=app_index,
            request_opcode=LightCTLOpcode.LIGHT_CTL_TEMPERATURE_SET,
            status_opcode=LightCTLOpcode.LIGHT_CTL_TEMPERATURE_STATUS,
            params=params,
            send_interval=send_interval,
            timeout=timeout,
        )

    async def temperature_set_unack(
        self,
        destination: int,
        app_index: int,
        ctl_temperature: int,
        ctl_delta_uv: int,
        transition_time: float = 0,
        *,
        delay: Optional[float] = None,
        retransmissions: Optional[int] = None,
        send_interval: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        params = dict(
            ctl_temperature=ctl_temperature,
            ctl_delta_uv=ctl_delta_uv,
            tid=self.tid(),
            delay=0,
            transition_time=transition_time,
        )
        await self.client_delay_set_unack(
            destination=destination,
            app_index=app_index,
            request_opcode=LightCTLOpcode.LIGHT_CTL_TEMPERATURE_SET_UNACKNOWLEDGED,
            params=params,
            delay=delay,
            retransmissions=retransmissions,
            send_interval=send_interval,
        )

    async def temperature_range_get(
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
            request_opcode=LightCTLOpcode.LIGHT_CTL_TEMPERATURE_RANGE_GET,
            status_opcode=LightCTLOpcode.LIGHT_CTL_TEMPERATURE_RANGE_STATUS,
            send_interval=send_interval,
            timeout=timeout)

    async def temperature_range_set(
        self,
        nodes: Sequence[int],
        app_index: int,
        range_min: int,
        range_max: int,
        *,
        send_interval: Optional[float] = None,
        timeout: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        params = dict(
            range_min=range_min,
            range_max=range_max,
        )
        return await self.client_simple_set(
            nodes=nodes,
            app_index=app_index,
            request_opcode=LightCTLSetupOpcode.LIGHT_CTL_SETUP_TEMPERATURE_RANGE_SET,
            status_opcode=LightCTLOpcode.LIGHT_CTL_TEMPERATURE_RANGE_STATUS,
            params=params,
            send_interval=send_interval,
            timeout=timeout,
        )

    async def temperature_range_set_unack(
        self,
        destination: int,
        app_index: int,
        range_min: int,
        range_max: int,
        *,
        retransmissions: Optional[int] = None,
        send_interval: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        params = dict(
            range_min=range_min,
            range_max=range_max,
        )
        await self.client_simple_set_unack(
            destination=destination,
            app_index=app_index,
            request_opcode=LightCTLSetupOpcode.LIGHT_CTL_SETUP_TEMPERATURE_RANGE_SET_UNACKNOWLEDGED,
            params=params,
            retransmissions=retransmissions,
            send_interval=send_interval,
        )

    async def default_get(
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
            request_opcode=LightCTLOpcode.LIGHT_CTL_TEMPERATURE_DEFAULT_GET,
            status_opcode=LightCTLOpcode.LIGHT_CTL_TEMPERATURE_DEFAULT_STATUS,
            send_interval=send_interval,
            timeout=timeout)

    async def default_set(
        self,
        nodes: Sequence[int],
        app_index: int,
        ctl_lightness: int,
        ctl_temperature: int,
        ctl_delta_uv: int,
        *,
        send_interval: Optional[float] = None,
        timeout: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        params = dict(
            ctl_lightness=ctl_lightness,
            ctl_temperature=ctl_temperature,
            ctl_delta_uv=ctl_delta_uv,
        )
        return await self.client_simple_set(
            nodes=nodes,
            app_index=app_index,
            request_opcode=LightCTLSetupOpcode.LIGHT_CTL_SETUP_TEMPERATURE_DEFAULT_SET,
            status_opcode=LightCTLOpcode.LIGHT_CTL_TEMPERATURE_DEFAULT_STATUS,
            params=params,
            send_interval=send_interval,
            timeout=timeout,
        )

    async def default_set_unack(
        self,
        destination: int,
        app_index: int,
        ctl_lightness: int,
        ctl_temperature: int,
        ctl_delta_uv: int,
        *,
        retransmissions: Optional[int] = None,
        send_interval: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        params = dict(
            ctl_lightness=ctl_lightness,
            ctl_temperature=ctl_temperature,
            ctl_delta_uv=ctl_delta_uv,
        )
        await self.client_delay_set_unack(
            destination=destination,
            app_index=app_index,
            request_opcode=LightCTLSetupOpcode.LIGHT_CTL_SETUP_TEMPERATURE_DEFAULT_SET_UNACKNOWLEDGED,
            params=params,
            retransmissions=retransmissions,
            send_interval=send_interval,
        )

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
This module implements Light HSL mesh models, both clients and servers.
"""
from functools import partial
from typing import Any, Dict, Iterable, NamedTuple, Optional, Sequence, Tuple, Type

from bluetooth_mesh.models.base import Model
from bluetooth_mesh.messages.light.hsl import (
    LightHSLOpcode,
    LightHSLSetupOpcode,
)

__all__ = [
    "LightHSLServer",
    "LightHSLSetupServer",
    "LightHSLHueServer",
    "LightHSLSaturationServer",
    "LightHSLClient",
]


class LightHSLServer(Model):
    MODEL_ID = (None, 0x1307)
    OPCODES = {
        LightHSLOpcode.LIGHT_HSL_SET,
        LightHSLOpcode.LIGHT_HSL_SET_UNACKNOWLEDGED,
        LightHSLOpcode.LIGHT_HSL_STATUS,
        LightHSLOpcode.LIGHT_HSL_TARGET_GET,
        LightHSLOpcode.LIGHT_HSL_TARGET_STATUS,
        LightHSLOpcode.LIGHT_HSL_DEFAULT_GET,
        LightHSLOpcode.LIGHT_HSL_DEFAULT_STATUS,
        LightHSLOpcode.LIGHT_HSL_RANGE_GET,
        LightHSLOpcode.LIGHT_HSL_RANGE_STATUS,
    }
    PUBLISH = True
    SUBSCRIBE = True


class LightHSLSetupServer(Model):
    MODEL_ID = (None, 0x1308)
    OPCODES = {
        LightHSLSetupOpcode.LIGHT_HSL_SETUP_DEFAULT_SET,
        LightHSLSetupOpcode.LIGHT_HSL_SETUP_DEFAULT_SET_UNACKNOWLEDGED,
        LightHSLSetupOpcode.LIGHT_HSL_SETUP_RANGE_SET,
        LightHSLSetupOpcode.LIGHT_HSL_SETUP_RANGE_SET_UNACKNOWLEDGED,
    }
    PUBLISH = True
    SUBSCRIBE = True


class LightHSLHueServer(Model):
    MODEL_ID = (None, 0x130A)
    OPCODES = {
        LightHSLOpcode.LIGHT_HSL_HUE_GET,
        LightHSLOpcode.LIGHT_HSL_HUE_SET,
        LightHSLOpcode.LIGHT_HSL_HUE_SET_UNACKNOWLEDGED,
        LightHSLOpcode.LIGHT_HSL_HUE_STATUS,
    }
    PUBLISH = True
    SUBSCRIBE = True


class LightHSLSaturationServer(Model):
    MODEL_ID = (None, 0x130B)
    OPCODES = {
        LightHSLOpcode.LIGHT_HSL_SATURATION_GET,
        LightHSLOpcode.LIGHT_HSL_SATURATION_SET,
        LightHSLOpcode.LIGHT_HSL_SATURATION_SET_UNACKNOWLEDGED,
        LightHSLOpcode.LIGHT_HSL_SATURATION_STATUS,
    }
    PUBLISH = True
    SUBSCRIBE = True


class LightHSLClient(Model):
    MODEL_ID = (None, 0x1309)
    OPCODES = {
        LightHSLOpcode.LIGHT_HSL_STATUS,
        LightHSLOpcode.LIGHT_HSL_TARGET_STATUS,
        LightHSLOpcode.LIGHT_HSL_DEFAULT_STATUS,
        LightHSLOpcode.LIGHT_HSL_RANGE_STATUS,
        LightHSLOpcode.LIGHT_HSL_HUE_STATUS,
        LightHSLOpcode.LIGHT_HSL_SATURATION_STATUS,
    }

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
            request_opcode=LightHSLOpcode.LIGHT_HSL_GET,
            status_opcode=LightHSLOpcode.LIGHT_HSL_STATUS,
            send_interval=send_interval,
            timeout=timeout)

    async def set(
        self,
        nodes: Sequence[int],
        app_index: int,
        hsl_lightness: int,
        hsl_hue: int,
        hsl_saturation: int,
        transition_time: float = 0,
        *,
        send_interval: Optional[float] = None,
        timeout: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        params = dict(
            hsl_lightness=hsl_lightness,
            hsl_hue=hsl_hue,
            hsl_saturation=hsl_saturation,
            tid=self.tid(),
            delay=0,
            transition_time=transition_time,
        )
        return await self.client_simple_set(
            nodes=nodes,
            app_index=app_index,
            request_opcode=LightHSLOpcode.LIGHT_HSL_SET,
            status_opcode=LightHSLOpcode.LIGHT_HSL_STATUS,
            params=params,
            send_interval=send_interval,
            timeout=timeout,
        )

    async def set_unack(
        self,
        destination: int,
        app_index: int,
        hsl_lightness: int,
        hsl_hue: int,
        hsl_saturation: int,
        transition_time: float = 0,
        *,
        delay: Optional[float] = None,
        retransmissions: Optional[int] = None,
        send_interval: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        params = dict(
            hsl_lightness=hsl_lightness,
            hsl_hue=hsl_hue,
            hsl_saturation=hsl_saturation,
            tid=self.tid(),
            transition_time=transition_time,
        )
        await self.client_delay_set_unack(
            destination=destination,
            app_index=app_index,
            request_opcode=LightHSLOpcode.LIGHT_HSL_SET_UNACKNOWLEDGED,
            params=params,
            delay=delay,
            retransmissions=retransmissions,
            send_interval=send_interval,
        )

    async def target_get(
        self,
        nodes: Sequence[int],
        app_index: int,
        *,
        send_interval: float = 0.1,
        timeout: Optional[float] = None,
    ) -> Dict[int, Optional[Any]]:
        return await self.client_simple_get(
            nodes=nodes,
            app_index=app_index,
            request_opcode=LightHSLOpcode.LIGHT_HSL_TARGET_GET,
            status_opcode=LightHSLOpcode.LIGHT_HSL_TARGET_STATUS,
            send_interval=send_interval,
            timeout=timeout)

    async def hue_get(
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
            request_opcode=LightHSLOpcode.LIGHT_HSL_HUE_GET,
            status_opcode=LightHSLOpcode.LIGHT_HSL_HUE_STATUS,
            send_interval=send_interval,
            timeout=timeout)

    async def hue_set(
        self,
        nodes: Sequence[int],
        app_index: int,
        hue: int,
        transition_time: float = 0,
        *,
        send_interval: Optional[float] = None,
        timeout: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        params=dict(
            hue=hue,
            tid=self.tid(),
            transition_time=transition_time,
            delay=0,
        )
        return await self.client_simple_set(
            nodes=nodes,
            app_index=app_index,
            request_opcode=LightHSLOpcode.LIGHT_HSL_HUE_SET,
            status_opcode=LightHSLOpcode.LIGHT_HSL_HUE_STATUS,
            params=params,
            send_interval=send_interval,
            timeout=timeout,
        )

    async def hue_set_unack(
        self,
        destination: int,
        app_index: int,
        hue: int,
        transition_time: float = 0,
        *,
        delay: Optional[float] = None,
        retransmissions: Optional[int] = None,
        send_interval: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        params=dict(
            hue=hue,
            tid=self.tid(),
            transition_time=transition_time,
        )
        await self.client_delay_set_unack(
            destination=destination,
            app_index=app_index,
            request_opcode=LightHSLOpcode.LIGHT_HSL_HUE_SET_UNACKNOWLEDGED,
            params=params,
            delay=delay,
            retransmissions=retransmissions,
            send_interval=send_interval,
        )

    async def saturation_get(
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
            request_opcode=LightHSLOpcode.LIGHT_HSL_SATURATION_GET,
            status_opcode=LightHSLOpcode.LIGHT_HSL_SATURATION_STATUS,
            send_interval=send_interval,
            timeout=timeout)

    async def saturation_set(
        self,
        nodes: Sequence[int],
        app_index: int,
        saturation: int,
        transition_time: float = 0,
        *,
        send_interval: Optional[float] = None,
        timeout: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        params=dict(
            saturation=saturation,
            tid=self.tid(),
            transition_time=transition_time,
            delay=0,
        )
        return await self.client_simple_set(
            nodes=nodes,
            app_index=app_index,
            request_opcode=LightHSLOpcode.LIGHT_HSL_SATURATION_SET,
            status_opcode=LightHSLOpcode.LIGHT_HSL_SATURATION_STATUS,
            params=params,
            send_interval=send_interval,
            timeout=timeout,
        )

    async def saturation_set_unack(
        self,
        destination: int,
        app_index: int,
        saturation: int,
        transition_time: float = 0,
        *,
        delay: Optional[float] = None,
        retransmissions: Optional[int] = None,
        send_interval: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        params=dict(
            saturation=saturation,
            tid=self.tid(),
            transition_time=transition_time,
        )
        await self.client_delay_set_unack(
            destination=destination,
            app_index=app_index,
            request_opcode=LightHSLOpcode.LIGHT_HSL_SATURATION_SET_UNACKNOWLEDGED,
            params=params,
            delay=delay,
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
            request_opcode=LightHSLOpcode.LIGHT_HSL_DEFAULT_GET,
            status_opcode=LightHSLOpcode.LIGHT_HSL_DEFAULT_STATUS,
            send_interval=send_interval,
            timeout=timeout)

    async def default_set(
        self,
        nodes: Sequence[int],
        app_index: int,
        hsl_lightness: int,
        hsl_hue: int,
        hsl_saturation: int,
        *,
        send_interval: Optional[float] = None,
        timeout: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        params=dict(
            hsl_lightness=hsl_lightness,
            hsl_hue=hsl_hue,
            hsl_saturation=hsl_saturation,
        )
        return await self.client_simple_set(
            nodes=nodes,
            app_index=app_index,
            request_opcode=LightHSLSetupOpcode.LIGHT_HSL_SETUP_DEFAULT_SET,
            status_opcode=LightHSLOpcode.LIGHT_HSL_DEFAULT_STATUS,
            params=params,
            send_interval=send_interval,
            timeout=timeout,
        )

    async def default_set_unack(
        self,
        destination: int,
        app_index: int,
        hsl_lightness: int,
        hsl_hue: int,
        hsl_saturation: int,
        *,
        retransmissions: Optional[int] = None,
        send_interval: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        params=dict(
            hsl_lightness=hsl_lightness,
            hsl_hue=hsl_hue,
            hsl_saturation=hsl_saturation,
        )
        await self.client_simple_set_unack(
            destination=destination,
            app_index=app_index,
            request_opcode=LightHSLSetupOpcode.LIGHT_HSL_SETUP_DEFAULT_SET_UNACKNOWLEDGED,
            params=params,
            retransmissions=retransmissions,
            send_interval=send_interval,
        )

    async def range_get(
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
            request_opcode=LightHSLOpcode.LIGHT_HSL_RANGE_GET,
            status_opcode=LightHSLOpcode.LIGHT_HSL_RANGE_STATUS,
            send_interval=send_interval,
            timeout=timeout)

    async def range_set(
        self,
        nodes: Sequence[int],
        app_index: int,
        hue_range_min: int,
        hue_range_max: int,
        saturation_range_min: int,
        saturation_range_max: int,
        *,
        send_interval: Optional[float] = None,
        timeout: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        params=dict(
            hue_range_min=hue_range_min,
            hue_range_max=hue_range_max,
            saturation_range_min=saturation_range_min,
            saturation_range_max=saturation_range_max,
        )
        return await self.client_simple_set(
            nodes=nodes,
            app_index=app_index,
            request_opcode=LightHSLSetupOpcode.LIGHT_HSL_SETUP_RANGE_SET,
            status_opcode=LightHSLOpcode.LIGHT_HSL_RANGE_STATUS,
            params=params,
            send_interval=send_interval,
            timeout=timeout,
        )

    async def range_set_unack(
        self,
        destination: int,
        app_index: int,
        hue_range_min: int,
        hue_range_max: int,
        saturation_range_min: int,
        saturation_range_max: int,
        *,
        retransmissions: Optional[int] = None,
        send_interval: Optional[float] = None
    ) -> Dict[int, Optional[Any]]:
        params=dict(
            hue_range_min=hue_range_min,
            hue_range_max=hue_range_max,
            saturation_range_min=saturation_range_min,
            saturation_range_max=saturation_range_max,
        )
        await self.client_simple_set_unack(
            destination=destination,
            app_index=app_index,
            request_opcode=LightHSLSetupOpcode.LIGHT_HSL_SETUP_RANGE_SET_UNACKNOWLEDGED,
            params=params,
            retransmissions=retransmissions,
            send_interval=send_interval,
        )

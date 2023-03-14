#
# python-bluetooth-mesh - Bluetooth Mesh for Python
#
# Copyright (C) 2019  SILVAIR sp. z o.o.
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
import inspect
import itertools
from datetime import datetime, timedelta
from functools import partial
from typing import Any, Dict, Iterable, NamedTuple, Optional, Sequence, Tuple, Type

from construct import BitStruct

from bluetooth_mesh.crypto import ApplicationKey, NetworkKey
from bluetooth_mesh.messages.config import (
    CompositionData,
    ConfigOpcode,
    PublishFriendshipCredentialsFlag,
    PublishPeriodStepResolution,
    SecureNetworkBeacon,
    StatusCode,
)
from bluetooth_mesh.messages.health import HealthOpcode
from bluetooth_mesh.messages.properties import PropertyID
from bluetooth_mesh.messages.scene import SceneOpcode
from bluetooth_mesh.messages.sensor import SensorOpcode
from bluetooth_mesh.messages.time import TimeOpcode, TimeRole
from bluetooth_mesh.models.base import Model
from bluetooth_mesh.utils import ModelOperationError, ProgressCallback

__all__ = [
    "ConfigServer",
    "ConfigClient",
    "HealthServer",
    "HealthClient",
    "SceneClient",
    "SensorClient",
]

AppKeyStatus = NamedTuple(
    "ApplicationKeyStatus",
    [
        ("net_key_index", int),
        ("app_key_index", int),
    ],
)

NetKeyStatus = NamedTuple(
    "NetworkKeyStatus",
    [
        ("net_key_index", int),
    ],
)

ModelBindStatus = NamedTuple(
    "ModelBindStatus",
    [
        ("element_address", int),
        ("app_key_index", int),
        ("model", Type[Model]),
    ],
)

ModelSubscriptionStatus = NamedTuple(
    "ModelSubscriptionStatus",
    [
        ("element_address", int),
        ("subscription_address", int),
        ("model", Type[Model]),
    ],
)

ModelSubscriptionList = NamedTuple(
    "ModelSubscriptionList",
    [
        ("element_address", int),
        ("model", Type[Model]),
        ("addresses", Sequence[int]),
    ],
)

ModelPublicationStatus = NamedTuple(
    "ModelPublicationStatus",
    [
        ("element_address", int),
        ("publication_address", int),
        ("ttl", int),
        ("app_key_index", int),
        ("period", timedelta),
        ("retransmissions", Any),
        ("model", Type[Model]),
    ],
)


class ConfigServer(Model):
    MODEL_ID = (None, 0x0000)
    OPCODES = {}  # implemented internally by BlueZ


class ConfigClient(Model):
    MODEL_ID = (None, 0x0001)
    OPCODES = {
        ConfigOpcode.CONFIG_APPKEY_LIST,
        ConfigOpcode.CONFIG_APPKEY_STATUS,
        ConfigOpcode.CONFIG_BEACON_STATUS,
        ConfigOpcode.CONFIG_COMPOSITION_DATA_STATUS,
        ConfigOpcode.CONFIG_DEFAULT_TTL_STATUS,
        ConfigOpcode.CONFIG_FRIEND_STATUS,
        ConfigOpcode.CONFIG_GATT_PROXY_STATUS,
        ConfigOpcode.CONFIG_HEARBEAT_PUBLICATION_STATUS,
        ConfigOpcode.CONFIG_HEARBEAT_SUBSCRIPTION_STATUS,
        ConfigOpcode.CONFIG_KEY_REFRESH_PHASE_STATUS,
        ConfigOpcode.CONFIG_LOW_POWER_NODE_POLL_TIMEOUT_STATUS,
        ConfigOpcode.CONFIG_MODEL_APP_STATUS,
        ConfigOpcode.CONFIG_MODEL_PUBLICATION_STATUS,
        ConfigOpcode.CONFIG_MODEL_SUBSCRIPTION_STATUS,
        ConfigOpcode.CONFIG_NETKEY_LIST,
        ConfigOpcode.CONFIG_NETKEY_STATUS,
        ConfigOpcode.CONFIG_NETWORK_TRANSMIT_STATUS,
        ConfigOpcode.CONFIG_NODE_IDENTITY_STATUS,
        ConfigOpcode.CONFIG_NODE_RESET_STATUS,
        ConfigOpcode.CONFIG_RELAY_STATUS,
        ConfigOpcode.CONFIG_SIG_MODEL_APP_LIST,
        ConfigOpcode.CONFIG_SIG_MODEL_SUBSCRIPTION_LIST,
        ConfigOpcode.CONFIG_VENDOR_MODEL_APP_LIST,
        ConfigOpcode.CONFIG_VENDOR_MODEL_SUBSCRIPTION_LIST,
    }

    @staticmethod
    def _get_model_id(model):
        vendor_id, model_id = model.MODEL_ID

        if vendor_id is not None:
            return dict(vendor_id=vendor_id, model_id=model_id)

        return dict(model_id=model_id)

    async def get_param(
        self,
        nodes: Iterable[int],
        net_index: int,
        request: dict,
        status: dict,
        *,
        send_interval: float = 1.0,
        progress_callback: Optional[ProgressCallback] = None,
        timeout: Optional[float] = None,
    ) -> Dict[int, Optional[Any]]:
        requests = {
            node: partial(
                self.send_dev,
                node,
                net_index=net_index,
                opcode=request["opcode"],
                params=request["params"] or dict(),
            )
            for node in nodes
        }

        statuses = {
            node: self.expect_dev(
                node,
                net_index=0,
                opcode=status["opcode"],
                params=status["params"] or dict(),
            )
            for node in nodes
        }

        params_name = status["opcode"].name.lower()

        async def _progress_callback(address, result, done, total):
            if isinstance(result, TimeoutError):
                self.logger.warning("Callback timeout for addr %s", address)
                return

            try:
                aw = progress_callback(
                    address, result[params_name]["data"], done, total
                )
                if inspect.isawaitable(aw):
                    await aw
            except Exception as ex:
                self.logger.warning("Callback failed for addr %s: %s", address, ex)

        results = await self.bulk_query(
            requests,
            statuses,
            send_interval=send_interval,
            timeout=timeout,
            progress_callback=_progress_callback if progress_callback else None,
        )

        return {
            node: None if isinstance(result, Exception) else result[params_name]
            for node, result in results.items()
        }

    async def get_composition_data(
        self,
        nodes: Sequence[int],
        net_index: int,
        send_interval: float = 2.0,
        progress_callback: Optional[ProgressCallback] = None,
        timeout: float = None,
    ) -> CompositionData:
        return await self.get_param(
            nodes,
            net_index,
            request=dict(
                opcode=ConfigOpcode.CONFIG_COMPOSITION_DATA_GET,
                params=dict(
                    page=0,
                ),
            ),
            status=dict(
                opcode=ConfigOpcode.CONFIG_COMPOSITION_DATA_STATUS,
                params=dict(
                    page=0,
                ),
            ),
            send_interval=send_interval,
            progress_callback=progress_callback,
            timeout=timeout or 2 * send_interval * len(nodes),
        )

    async def get_default_ttl(
        self,
        nodes: Sequence[int],
        net_index: int,
        send_interval: float = 0.1,
        progress_callback: Optional[ProgressCallback] = None,
        timeout: float = None,
    ) -> Dict[int, Optional[Any]]:
        return await self.get_param(
            nodes,
            net_index,
            request=dict(opcode=ConfigOpcode.CONFIG_DEFAULT_TTL_GET, params=dict()),
            status=dict(opcode=ConfigOpcode.CONFIG_DEFAULT_TTL_STATUS, params=dict()),
            send_interval=send_interval,
            progress_callback=progress_callback,
            timeout=timeout or 2 * send_interval * len(nodes),
        )

    async def get_relay(
        self,
        nodes: Sequence[int],
        net_index: int,
        send_interval: float = 0.1,
        progress_callback: Optional[ProgressCallback] = None,
        timeout: float = None,
    ) -> Dict[int, Optional[Any]]:
        return await self.get_param(
            nodes,
            net_index,
            request=dict(opcode=ConfigOpcode.CONFIG_RELAY_GET, params=dict()),
            status=dict(opcode=ConfigOpcode.CONFIG_RELAY_STATUS, params=dict()),
            send_interval=send_interval,
            progress_callback=progress_callback,
            timeout=timeout or 2 * send_interval * len(nodes),
        )

    async def get_key_refresh_phase(
        self,
        nodes: Sequence[int],
        net_index: int,
        net_key_index: int,
        send_interval: float = 0.1,
        progress_callback: Optional[ProgressCallback] = None,
        timeout: float = None,
    ) -> Dict[int, Optional[Any]]:
        return await self.get_param(
            nodes,
            net_index,
            request=dict(
                opcode=ConfigOpcode.CONFIG_KEY_REFRESH_PHASE_GET,
                params=dict(
                    net_key_index=0,
                ),
            ),
            status=dict(
                opcode=ConfigOpcode.CONFIG_KEY_REFRESH_PHASE_STATUS,
                params=dict(
                    net_key_index=net_key_index,
                ),
            ),
            send_interval=send_interval,
            progress_callback=progress_callback,
            timeout=timeout or 2 * send_interval * len(nodes),
        )

    async def add_net_key(
        self, destination: int, net_index: int, net_key_index: int, net_key: NetworkKey
    ) -> NetKeyStatus:
        status_opcode = ConfigOpcode.CONFIG_NETKEY_STATUS

        status = self.expect_dev(
            destination,
            net_index=net_index,
            opcode=status_opcode,
            params=dict(
                net_key_index=net_key_index,
                status=StatusCode.SUCCESS,
            ),
        )

        request = partial(
            self.send_dev,
            destination,
            net_index=net_index,
            opcode=ConfigOpcode.CONFIG_NETKEY_ADD,
            params=dict(
                net_key_index=net_key_index,
                net_key=net_key.bytes,
            ),
        )

        status = await self.query(request, status)

        if status[status_opcode.name.lower()]["status"] != StatusCode.SUCCESS:
            raise ModelOperationError("Cannot add net key", status)

        return NetKeyStatus(net_key_index=net_key_index)

    async def delete_net_key(
        self, destination: int, net_index: int, net_key_index: int
    ) -> NetKeyStatus:
        status_opcode = (ConfigOpcode.CONFIG_NETKEY_STATUS,)

        status = self.expect_dev(
            destination,
            net_index=net_index,
            opcode=status_opcode,
            params=dict(
                net_key_index=net_key_index,
                status=StatusCode.SUCCESS,
            ),
        )

        request = partial(
            self.send_dev,
            destination,
            net_index=net_index,
            opcode=ConfigOpcode.CONFIG_NETKEY_DELETE,
            params=dict(
                net_key_index=net_key_index,
            ),
        )

        status = await self.query(request, status)

        if status[status_opcode.name.lower()]["status"] != StatusCode.SUCCESS:
            raise ModelOperationError("Cannot delete net key", status)

        return NetKeyStatus(net_key_index=net_key_index)

    async def add_app_key(
        self,
        destination: int,
        net_index: int,
        app_key_index: int,
        net_key_index: int,
        app_key: ApplicationKey,
    ) -> AppKeyStatus:
        status_opcode = ConfigOpcode.CONFIG_APPKEY_STATUS
        params_name = status_opcode.name.lower()

        status = self.expect_dev(
            destination,
            net_index=net_index,
            opcode=status_opcode,
            params=dict(
                net_key_index=net_key_index,
                app_key_index=app_key_index,
            ),
        )

        request = partial(
            self.send_dev,
            destination,
            net_index=net_index,
            opcode=ConfigOpcode.CONFIG_APPKEY_ADD,
            params=dict(
                net_key_index=net_key_index,
                app_key_index=app_key_index,
                app_key=app_key.bytes,
            ),
        )

        status = await self.query(request, status)

        if status[params_name]["status"] != StatusCode.SUCCESS:
            raise ModelOperationError("Cannot add app key", status)

        return AppKeyStatus(
            status[params_name]["net_key_index"], status[params_name]["app_key_index"]
        )

    async def delete_app_key(
        self,
        destination: int,
        net_index: int,
        app_key_index: int,
        net_key_index: int,
    ) -> AppKeyStatus:
        status_opcode = ConfigOpcode.CONFIG_APPKEY_STATUS
        params_name = status_opcode.name.lower()

        status = self.expect_dev(
            destination,
            net_index=net_index,
            opcode=status_opcode,
            params=dict(
                net_key_index=net_key_index,
                app_key_index=app_key_index,
            ),
        )

        request = partial(
            self.send_dev,
            destination,
            net_index=net_index,
            opcode=ConfigOpcode.CONFIG_APPKEY_DELETE,
            params=dict(
                net_key_index=net_key_index,
                app_key_index=app_key_index,
            ),
        )

        status = await self.query(request, status)

        if status[params_name]["status"] != StatusCode.SUCCESS:
            raise ModelOperationError("Cannot delete app key", status)

        return AppKeyStatus(
            status[params_name]["net_key_index"], status[params_name]["app_key_index"]
        )

    async def update_app_key(
        self,
        destination: int,
        net_index: int,
        net_key_index: int,
        app_key_index: int,
        app_key: ApplicationKey,
    ) -> AppKeyStatus:
        status_opcode = ConfigOpcode.CONFIG_APPKEY_STATUS
        params_name = status_opcode.name.lower()

        status = self.expect_dev(
            destination,
            net_index=net_index,
            opcode=status_opcode,
            params=dict(
                net_key_index=net_key_index,
                app_key_index=app_key_index,
            ),
        )

        request = partial(
            self.send_dev,
            destination,
            net_index=net_index,
            opcode=ConfigOpcode.CONFIG_APPKEY_UPDATE,
            params=dict(
                app_key_index=0,
                net_key_index=0,
                app_key=app_key.bytes,
            ),
        )

        status = await self.query(request, status)

        if status[params_name]["status"] != StatusCode.SUCCESS:
            raise ModelOperationError("Cannot update app key", status)

        return AppKeyStatus(
            status[params_name]["net_key_index"], status[params_name]["app_key_index"]
        )

    async def bind_app_key(
        self,
        destination: int,
        net_index: int,
        element_address: int,
        app_key_index: int,
        model: Type[Model],
    ) -> ModelBindStatus:
        status_opcode = ConfigOpcode.CONFIG_MODEL_APP_STATUS
        params_name = status_opcode.name.lower()

        status = self.expect_dev(
            destination,
            net_index=net_index,
            opcode=status_opcode,
            params=dict(
                element_address=element_address,
                app_key_index=app_key_index,
                model=self._get_model_id(model),
            ),
        )

        request = partial(
            self.send_dev,
            destination,
            net_index=net_index,
            opcode=ConfigOpcode.CONFIG_MODEL_APP_BIND,
            params=dict(
                element_address=element_address,
                app_key_index=app_key_index,
                model=self._get_model_id(model),
            ),
        )

        status = await self.query(request, status)

        if status[params_name]["status"] != StatusCode.SUCCESS:
            raise ModelOperationError("Cannot bind app key", status)

        return ModelBindStatus(
            status[params_name]["element_address"],
            status[params_name]["app_key_index"],
            model,
        )

    async def get_network_transmission(
        self, destination: int, net_index: int
    ) -> Tuple[int, int]:
        status_opcode = ConfigOpcode.CONFIG_NETWORK_TRANSMIT_STATUS
        params_name = status_opcode.name.lower()

        status = self.expect_dev(
            destination,
            net_index=net_index,
            opcode=status_opcode,
            params=dict(),
        )

        request = partial(
            self.send_dev,
            destination,
            net_index=net_index,
            opcode=ConfigOpcode.CONFIG_NETWORK_TRANSMIT_GET,
            params=dict(),
        )

        status = await self.query(request, status)
        return (status[params_name]["interval"], status[params_name]["count"])

    async def set_network_transmission(
        self, destination: int, net_index: int, interval: int, count: int
    ) -> Tuple[int, int]:
        status_opcode = ConfigOpcode.CONFIG_NETWORK_TRANSMIT_STATUS
        params_name = status_opcode.name.lower()

        status = self.expect_dev(
            destination,
            net_index=net_index,
            opcode=status_opcode,
            params=dict(interval=interval, count=count),
        )

        request = partial(
            self.send_dev,
            destination,
            net_index=net_index,
            opcode=ConfigOpcode.CONFIG_NETWORK_TRANSMIT_SET,
            params=dict(interval=interval, count=count),
        )

        status = await self.query(request, status)
        return (status[params_name]["interval"], status[params_name]["count"])

    async def update_net_key(
        self, destination: int, net_index: int, net_key_index: int, net_key: NetworkKey
    ) -> int:
        status_opcode = ConfigOpcode.CONFIG_NETKEY_STATUS
        params_name = status_opcode.name.lower()

        status = self.expect_dev(
            destination,
            net_index=net_index,
            opcode=status_opcode,
            params=dict(
                net_key_index=net_key_index,
            ),
        )

        request = partial(
            self.send_dev,
            destination,
            net_index=net_index,
            opcode=ConfigOpcode.CONFIG_NETKEY_UPDATE,
            params=dict(
                net_key_index=0,
                net_key=net_key.bytes,
            ),
        )

        status = await self.query(request, status)

        if status[params_name]["status"] != StatusCode.SUCCESS:
            raise ModelOperationError("Cannot update net key", status)

        return status[params_name]["net_key_index"]

    async def add_subscription(
        self,
        destination: int,
        net_index: int,
        element_address: int,
        subscription_address: int,
        model: Type[Model],
    ) -> ModelSubscriptionStatus:
        status_opcode = ConfigOpcode.CONFIG_MODEL_SUBSCRIPTION_STATUS
        params_name = status_opcode.name.lower()

        status = self.expect_dev(
            destination,
            net_index=net_index,
            opcode=status_opcode,
            params=dict(
                element_address=element_address,
                address=subscription_address,
                model=self._get_model_id(model),
            ),
        )

        request = partial(
            self.send_dev,
            destination,
            net_index=net_index,
            opcode=ConfigOpcode.CONFIG_MODEL_SUBSCRIPTION_ADD,
            params=dict(
                element_address=element_address,
                address=subscription_address,
                model=self._get_model_id(model),
            ),
        )

        status = await self.query(request, status)

        if status[params_name]["status"] != StatusCode.SUCCESS:
            raise ModelOperationError("Cannot add subscription", status)

        return ModelSubscriptionStatus(
            status[params_name]["element_address"],
            status[params_name]["address"],
            model,
        )

    async def del_subscription(
        self,
        destination: int,
        net_index: int,
        element_address: int,
        subscription_address: int,
        model: Type[Model],
    ) -> ModelSubscriptionStatus:
        status_opcode = ConfigOpcode.CONFIG_MODEL_SUBSCRIPTION_STATUS
        params_name = status_opcode.name.lower()

        status = self.expect_dev(
            destination,
            net_index=net_index,
            opcode=status_opcode,
            params=dict(
                element_address=element_address,
                address=subscription_address,
                model=self._get_model_id(model),
            ),
        )

        request = partial(
            self.send_dev,
            destination,
            net_index=net_index,
            opcode=ConfigOpcode.CONFIG_MODEL_SUBSCRIPTION_DELETE,
            params=dict(
                element_address=element_address,
                address=subscription_address,
                model=self._get_model_id(model),
            ),
        )

        status = await self.query(request, status)

        if status[params_name]["status"] != StatusCode.SUCCESS:
            raise ModelOperationError("Cannot add subscription", status)

        return ModelSubscriptionStatus(
            status[params_name]["element_address"],
            status[params_name]["address"],
            model,
        )

    async def clear_subscriptions(
        self, destination: int, net_index: int, element_address: int, model: Type[Model]
    ) -> ModelSubscriptionStatus:
        status_opcode = ConfigOpcode.CONFIG_MODEL_SUBSCRIPTION_STATUS
        params_name = status_opcode.name.lower()

        status = self.expect_dev(
            destination,
            net_index=net_index,
            opcode=status_opcode,
            params=dict(
                element_address=element_address,
                address=0,
                model=self._get_model_id(model),
            ),
        )

        request = partial(
            self.send_dev,
            destination,
            net_index=net_index,
            opcode=ConfigOpcode.CONFIG_MODEL_SUBSCRIPTION_DELETE_ALL,
            params=dict(
                element_address=element_address,
                model=self._get_model_id(model),
            ),
        )

        status = await self.query(request, status)

        if status[params_name]["status"] != StatusCode.SUCCESS:
            raise ModelOperationError("Cannot add subscription", status)

        return ModelSubscriptionStatus(
            status[params_name]["element_address"],
            status[params_name]["address"],
            model,
        )

    async def get_subscriptions(
        self, destination: int, net_index: int, element_address: int, model: Type[Model]
    ) -> ModelSubscriptionList:
        if model.MODEL_ID[0] is not None:
            status_opcode = ConfigOpcode.CONFIG_VENDOR_MODEL_SUBSCRIPTION_LIST
            request_opcode = ConfigOpcode.CONFIG_VENDOR_MODEL_SUBSCRIPTION_GET
        else:
            status_opcode = ConfigOpcode.CONFIG_SIG_MODEL_SUBSCRIPTION_LIST
            request_opcode = ConfigOpcode.CONFIG_SIG_MODEL_SUBSCRIPTION_GET

        params_name = status_opcode.name.lower()

        status = self.expect_dev(
            destination,
            net_index=net_index,
            opcode=status_opcode,
            params=dict(
                element_address=element_address,
                model=self._get_model_id(model),
            ),
        )

        request = partial(
            self.send_dev,
            destination,
            net_index=net_index,
            opcode=request_opcode,
            params=dict(
                element_address=element_address,
                model=self._get_model_id(model),
            ),
        )

        status = await self.query(request, status)

        if status[params_name]["status"] != StatusCode.SUCCESS:
            raise ModelOperationError("Cannot get subscription list", status)

        return ModelSubscriptionList(
            status[params_name]["element_address"],
            model,
            status[params_name]["addresses"],
        )

    async def get_publication(
        self, destination: int, net_index: int, element_address: int, model: Type[Model]
    ) -> ModelPublicationStatus:
        status_opcode = ConfigOpcode.CONFIG_MODEL_PUBLICATION_STATUS
        params_name = status_opcode.name.lower()

        status = self.expect_dev(
            destination,
            net_index=net_index,
            opcode=status_opcode,
            params=dict(),
        )

        request = partial(
            self.send_dev,
            destination,
            net_index=net_index,
            opcode=ConfigOpcode.CONFIG_MODEL_PUBLICATION_GET,
            params=dict(
                element_address=element_address, model=self._get_model_id(model)
            ),
        )

        status = await self.query(request, status)

        period = (
            status[params_name]["publish_period"]["step_resolution"].multiplier
            * status[params_name]["publish_period"]["number_of_steps"]
        )

        retransmissions = dict(
            count=status[params_name]["retransmit"]["count"],
            interval=timedelta(
                milliseconds=status[params_name]["retransmit"]["interval"]
            ),
        )

        return ModelPublicationStatus(
            status[params_name]["element_address"],
            status[params_name]["publish_address"],
            status[params_name]["ttl"],
            status[params_name]["app_key_index"],
            period,
            retransmissions,
            model,
        )

    async def set_publication(
        self,
        destination: int,
        net_index: int,
        element_address: int,
        publication_address: int,
        app_key_index: int,
        model: Type[Model],
        ttl: int = 8,
        publish_step_resolution: PublishPeriodStepResolution = PublishPeriodStepResolution.RESOLUTION_10_S,
        publish_number_of_steps: int = 6,  # 60seconds
        retransmit_count: int = 0,
        retransmit_interval: int = 50,
    ) -> ModelPublicationStatus:
        status_opcode = ConfigOpcode.CONFIG_MODEL_PUBLICATION_STATUS
        params_name = status_opcode.name.lower()

        status = self.expect_dev(
            destination,
            net_index=net_index,
            opcode=ConfigOpcode.CONFIG_MODEL_PUBLICATION_STATUS,
            params=dict(
                status=StatusCode.SUCCESS,
                element_address=element_address,
                publish_address=publication_address,
                ttl=ttl,
                app_key_index=app_key_index,
                credential_flag=PublishFriendshipCredentialsFlag.MASTER_SECURITY,
                RFU=0,
                publish_period=dict(
                    step_resolution=publish_step_resolution,
                    number_of_steps=publish_number_of_steps,
                ),
                retransmit=dict(count=retransmit_count, interval=retransmit_interval),
                model=self._get_model_id(model),
            ),
        )

        request = partial(
            self.send_dev,
            destination,
            net_index=net_index,
            opcode=ConfigOpcode.CONFIG_MODEL_PUBLICATION_SET,
            params=dict(
                element_address=element_address,
                publish_address=publication_address,
                ttl=ttl,
                app_key_index=app_key_index,
                credential_flag=PublishFriendshipCredentialsFlag.MASTER_SECURITY,
                RFU=0,
                publish_period=dict(
                    step_resolution=publish_step_resolution,
                    number_of_steps=publish_number_of_steps,
                ),
                retransmit=dict(count=retransmit_count, interval=retransmit_interval),
                model=self._get_model_id(model),
            ),
        )

        status = await self.query(request, status, send_interval=0.2, timeout=4)

        if status[params_name]["status"] != StatusCode.SUCCESS:
            raise ModelOperationError("Cannot add subscription", status)

        period = (
            status[params_name]["publish_period"]["step_resolution"].multiplier
            * status[params_name]["publish_period"]["number_of_steps"]
        )

        retransmissions = dict(
            count=status[params_name]["retransmit"]["count"],
            interval=timedelta(
                milliseconds=status[params_name]["retransmit"]["interval"]
            ),
        )

        return ModelPublicationStatus(
            status[params_name]["element_address"],
            status[params_name]["publish_address"],
            status[params_name]["ttl"],
            status[params_name]["app_key_index"],
            period,
            retransmissions,
            model,
        )

    async def set_beacon(
        self,
        destination: int,
        net_index: int,
        enabled: bool,
        send_interval: float = 2.0,
        timeout: float = 5.0,
    ) -> CompositionData:
        status_opcode = ConfigOpcode.CONFIG_BEACON_STATUS

        status = self.expect_dev(
            destination,
            net_index=net_index,
            opcode=status_opcode,
            params=dict(
                beacon=SecureNetworkBeacon.ON if enabled else SecureNetworkBeacon.OFF,
            ),
        )

        request = partial(
            self.send_dev,
            destination,
            net_index=net_index,
            opcode=ConfigOpcode.CONFIG_BEACON_SET,
            params=dict(
                beacon=SecureNetworkBeacon.ON if enabled else SecureNetworkBeacon.OFF,
            ),
        )

        status = await self.query(
            request, status, send_interval=send_interval, timeout=timeout
        )

        return status[status_opcode.name.lower()]["beacon"]


class HealthServer(Model):
    MODEL_ID = (None, 0x0002)
    OPCODES = {
        HealthOpcode.HEALTH_FAULT_GET,
        HealthOpcode.HEALTH_FAULT_CLEAR,
        HealthOpcode.HEALTH_FAULT_CLEAR_UNACKNOWLEDGED,
        HealthOpcode.HEALTH_FAULT_TEST,
        HealthOpcode.HEALTH_FAULT_TEST_UNACKNOWLEDGED,
        HealthOpcode.HEALTH_PERIOD_GET,
        HealthOpcode.HEALTH_PERIOD_SET,
        HealthOpcode.HEALTH_PERIOD_SET_UNACKNOWLEDGED,
        HealthOpcode.HEALTH_ATTENTION_GET,
        HealthOpcode.HEALTH_ATTENTION_SET,
        HealthOpcode.HEALTH_ATTENTION_SET_UNACKNOWLEDGED,
    }
    PUBLISH = True
    SUBSCRIBE = True


class HealthClient(Model):
    MODEL_ID = (None, 0x0003)
    OPCODES = {
        HealthOpcode.HEALTH_CURRENT_STATUS,
        HealthOpcode.HEALTH_FAULT_STATUS,
        HealthOpcode.HEALTH_PERIOD_STATUS,
        HealthOpcode.HEALTH_ATTENTION_STATUS,
    }
    PUBLISH = True
    SUBSCRIBE = True

    async def attention(self, destination: int, app_index: int, attention: int) -> int:
        status_opcode = HealthOpcode.HEALTH_ATTENTION_STATUS

        status = self.expect_app(
            destination,
            app_index=app_index,
            destination=None,
            opcode=status_opcode,
            params=dict(
                attention=attention,
            ),
        )

        request = partial(
            self.send_app,
            destination,
            app_index=app_index,
            opcode=HealthOpcode.HEALTH_ATTENTION_SET,
            params=dict(
                attention=attention,
            ),
        )

        status = await self.query(request, status)
        return status[status_opcode.name.lower()]["attention"]

    async def attention_unack(self, destination: int, app_index: int, attention: int):
        request = partial(
            self.send_app,
            destination,
            app_index=app_index,
            opcode=HealthOpcode.HEALTH_ATTENTION_SET_UNACKNOWLEDGED,
            params=dict(
                attention=attention,
            ),
        )

        await self.repeat(request)


class SceneClient(Model):
    MODEL_ID = (None, 0x1205)
    OPCODES = {
        SceneOpcode.SCENE_GET,
        SceneOpcode.SCENE_RECALL,
        SceneOpcode.SCENE_RECALL_UNACKNOWLEDGED,
        SceneOpcode.SCENE_STATUS,
        SceneOpcode.SCENE_REGISTER_GET,
        SceneOpcode.SCENE_REGISTER_STATUS,
        SceneOpcode.SCENE_STORE,
        SceneOpcode.SCENE_STORE_UNACKNOWLEDGED,
        SceneOpcode.SCENE_DELETE,
        SceneOpcode.SCENE_DELETE_UNACKNOWLEDGED,
    }
    PUBLISH = True
    SUBSCRIBE = True

    async def recall_scene_unack(
        self,
        destination: int,
        app_index: int,
        scene_number: int,
        transition_time: float,
    ):
        tid = self.tid()
        current_delay = 0.5
        send_interval = 0.075

        async def request():
            nonlocal current_delay
            ret = self.send_app(
                destination,
                app_index=app_index,
                opcode=SceneOpcode.SCENE_RECALL_UNACKNOWLEDGED,
                params=dict(
                    scene_number=scene_number,
                    tid=tid,
                    transition_time=transition_time,
                    delay=current_delay,
                ),
            )
            current_delay = max(0.0, current_delay - send_interval)

            return await ret

        await self.repeat(request, retransmissions=6, send_interval=send_interval)

    async def get_scene(
        self,
        nodes: Sequence[int],
        app_index: int,
        *,
        send_interval: float = 0.1,
        timeout: Optional[float] = None,
    ):
        requests = {
            node: partial(
                self.send_app,
                node,
                app_index=app_index,
                opcode=SceneOpcode.SCENE_GET,
                params=dict(),
            )
            for node in nodes
        }

        status_opcode = SceneOpcode.SCENE_STATUS

        statuses = {
            node: self.expect_app(
                node,
                app_index=0,
                destination=None,
                opcode=status_opcode,
                params=dict(),
            )
            for node in nodes
        }

        results = await self.bulk_query(
            requests,
            statuses,
            send_interval=send_interval,
            timeout=timeout or len(nodes) * 0.5,
        )

        return {
            node: None
            if isinstance(result, Exception)
            else result[status_opcode.name.lower()]
            for node, result in results.items()
        }


class SensorClient(Model):
    MODEL_ID = (None, 0x1102)
    OPCODES = {
        SensorOpcode.SENSOR_DESCRIPTOR_GET,
        SensorOpcode.SENSOR_DESCRIPTOR_STATUS,
        SensorOpcode.SENSOR_GET,
        SensorOpcode.SENSOR_STATUS,
    }
    PUBLISH = True
    SUBSCRIBE = True

    async def get_descriptor(
        self,
        nodes: Sequence[int],
        app_index: int,
        *,
        send_interval: float = 0.1,
        timeout: Optional[float] = None,
    ) -> Dict[int, Optional[Any]]:
        requests = {
            node: partial(
                self.send_app,
                node,
                app_index=app_index,
                opcode=SensorOpcode.SENSOR_DESCRIPTOR_GET,
                params=dict(),
            )
            for node in nodes
        }

        status_opcode = SensorOpcode.SENSOR_DESCRIPTOR_STATUS

        statuses = {
            node: self.expect_app(
                node,
                app_index=0,
                destination=None,
                opcode=status_opcode,
                params=dict(),
            )
            for node in nodes
        }

        results = await self.bulk_query(
            requests,
            statuses,
            send_interval=send_interval,
            timeout=timeout or len(nodes) * 0.5,
        )

        return {
            node: None
            if isinstance(result, Exception)
            else result[status_opcode.name.lower()]
            for node, result in results.items()
        }

    async def get_sensor(
        self,
        nodes: Sequence[int],
        app_index: int,
        property_id: PropertyID,
        *,
        send_interval: float = 0.1,
        timeout: Optional[float] = None,
    ) -> Dict[int, Optional[Any]]:
        requests = {
            node: partial(
                self.send_app,
                node,
                app_index=app_index,
                opcode=SensorOpcode.SENSOR_GET,
                params=dict(property_id=property_id),
            )
            for node in nodes
        }

        status_opcode = SensorOpcode.SENSOR_STATUS

        statuses = {
            node: self.expect_app(
                node,
                app_index=0,
                destination=None,
                opcode=status_opcode,
                params=dict(),
            )
            for node in nodes
        }

        results = await self.bulk_query(
            requests,
            statuses,
            send_interval=send_interval,
            timeout=timeout or len(nodes) * 0.5,
        )

        return {
            node: None if isinstance(result, Exception) else result[status.name.lower()]
            for node, result in results.items()
        }


class TimeServer(Model):
    MODEL_ID = (None, 0x1200)
    OPCODES = {
        TimeOpcode.TIME_GET,
        TimeOpcode.TIME_STATUS,
        TimeOpcode.TIME_ZONE_GET,
        TimeOpcode.TIME_ZONE_STATUS,
        TimeOpcode.TAI_UTC_DELTA_GET,
        TimeOpcode.TAI_UTC_DELTA_STATUS,
    }
    PUBLISH = True
    SUBSCRIBE = True


class TimeSetupServer(Model):
    MODEL_ID = (None, 0x1201)
    OPCODES = {
        TimeOpcode.TIME_SET,
        TimeOpcode.TIME_ZONE_SET,
        TimeOpcode.TAI_UTC_DELTA_SET,
        TimeOpcode.TIME_ROLE_SET,
        TimeOpcode.TIME_ROLE_GET,
        TimeOpcode.TIME_ROLE_STATUS,
    }
    PUBLISH = False
    SUBSCRIBE = False


class TimeClient(Model):
    MODEL_ID = (None, 0x1202)
    OPCODES = {
        TimeOpcode.TIME_GET,
        TimeOpcode.TIME_SET,
        TimeOpcode.TIME_STATUS,
        TimeOpcode.TIME_ZONE_GET,
        TimeOpcode.TIME_ZONE_SET,
        TimeOpcode.TIME_ZONE_STATUS,
        TimeOpcode.TAI_UTC_DELTA_GET,
        TimeOpcode.TAI_UTC_DELTA_SET,
        TimeOpcode.TAI_UTC_DELTA_STATUS,
        TimeOpcode.TIME_ROLE_GET,
        TimeOpcode.TIME_ROLE_SET,
        TimeOpcode.TIME_ROLE_STATUS,
    }
    PUBLISH = True
    SUBSCRIBE = True

    async def get_time(
        self,
        nodes: Sequence[int],
        app_index: int,
    ) -> Dict[int, Optional[Any]]:
        requests = {
            node: partial(
                self.send_app,
                node,
                app_index=app_index,
                opcode=TimeOpcode.TIME_GET,
                params=dict(),
            )
            for node in nodes
        }

        status_opcode = TimeOpcode.TIME_STATUS

        statuses = {
            node: self.expect_app(
                node,
                app_index=0,
                destination=None,
                opcode=status_opcode,
                params=dict(),
            )
            for node in nodes
        }

        results = await self.bulk_query(requests, statuses)

        return {
            node: None
            if isinstance(result, Exception)
            else result[status_opcode.name.lower()]
            for node, result in results.items()
        }

    async def get_time_role(
        self,
        nodes: Sequence[int],
        app_index: int,
    ) -> Dict[int, Optional[Any]]:
        requests = {
            node: partial(
                self.send_app,
                node,
                app_index=app_index,
                opcode=TimeOpcode.TIME_ROLE_GET,
                params=dict(),
            )
            for node in nodes
        }

        status_opcode = TimeOpcode.TIME_ROLE_STATUS

        statuses = {
            node: self.expect_app(
                node,
                app_index=0,
                destination=None,
                opcode=status_opcode,
                params=dict(),
            )
            for node in nodes
        }

        results = await self.bulk_query(
            requests,
            statuses,
        )

        return {
            node: None
            if isinstance(result, Exception)
            else result[status_opcode.name.lower()]
            for node, result in results.items()
        }

    async def set_time(
        self,
        nodes: Sequence[int],
        app_index: int,
        date: datetime,
        tai_utc_delta: timedelta,
        uncertainty: timedelta,
        time_authority: bool,
    ):
        requests = {
            node: partial(
                self.send_app,
                node,
                app_index=app_index,
                opcode=TimeOpcode.TIME_SET,
                params=dict(
                    date=date,
                    uncertainty=uncertainty,
                    time_authority=time_authority,
                    tai_utc_delta=tai_utc_delta,
                ),
            )
            for node in nodes
        }

        status_opcode = TimeOpcode.TIME_STATUS

        statuses = {
            node: self.expect_app(
                node,
                app_index=0,
                destination=None,
                opcode=status_opcode,
                params=dict(),
            )
            for node in nodes
        }

        results = await self.bulk_query(
            requests,
            statuses,
        )

        return {
            node: None
            if isinstance(result, Exception)
            else result[status_opcode.name.lower()]
            for node, result in results.items()
        }

    async def set_time_role(
        self, nodes: Sequence[int], app_index: int, time_role: TimeRole
    ):
        requests = {
            node: partial(
                self.send_app,
                node,
                app_index=app_index,
                opcode=TimeOpcode.TIME_ROLE_SET,
                params=dict(time_role=time_role),
            )
            for node in nodes
        }

        status_opcode = TimeOpcode.TIME_ROLE_STATUS

        statuses = {
            node: self.expect_app(
                node,
                app_index=0,
                destination=None,
                opcode=status_opcode,
                params=dict(),
            )
            for node in nodes
        }

        results = await self.bulk_query(
            requests,
            statuses,
        )

        return {
            node: None
            if isinstance(result, Exception)
            else result[status_opcode.name.lower()]
            for node, result in results.items()
        }

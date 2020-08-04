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
from datetime import timedelta
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
from bluetooth_mesh.messages.generic.level import GenericLevelOpcode
from bluetooth_mesh.messages.generic.light.ctl import LightCTLOpcode
from bluetooth_mesh.messages.generic.light.lightness import (
    LightLightnessOpcode,
    LightLightnessSetupOpcode,
)
from bluetooth_mesh.messages.generic.onoff import GenericOnOffOpcode
from bluetooth_mesh.messages.health import HealthOpcode
from bluetooth_mesh.messages.scene import SceneOpcode
from bluetooth_mesh.messages.sensor import SensorOpcode
from bluetooth_mesh.messages.silvair.debug import DebugOpcode, DebugSubOpcode
from bluetooth_mesh.messages.silvair.gateway_config_server import (
    DhcpFlag,
    GatewayConfigServerOpcode,
    GatewayConfigServerSubOpcode,
)
from bluetooth_mesh.messages.silvair.light_extended_controller import (
    LightExtendedControllerMessage,
    LightExtendedControllerOpcode,
    LightExtendedControllerProperty,
    LightExtendedControllerSubOpcode,
)
from bluetooth_mesh.messages.silvair.network_diagnostic_server import (
    NetworkDiagnosticServerOpcode,
    NetworkDiagnosticSetupServerOpcode,
)
from bluetooth_mesh.models.base import Model
from bluetooth_mesh.utils import ModelOperationError, ProgressCallback

__all__ = [
    "ConfigServer",
    "ConfigClient",
    "HealthServer",
    "HealthClient",
    "DebugServer",
    "DebugClient",
    "NetworkDiagnosticClient",
    "NetworkDiagnosticSetupClient",
    "GenericOnOffServer",
    "GenericOnOffClient",
    "SceneClient",
    "GenericLevelClient",
    "SensorClient",
    "LightLightnessClient",
    "LightLightnessServer",
    "LightCTLClient",
    "GatewayConfigServer",
    "GatewayConfigClient",
    "LightExtendedControllerSetupClient",
]

AppKeyStatus = NamedTuple(
    "ApplicationKeyStatus", [("net_key_index", int), ("app_key_index", int),]
)

NetKeyStatus = NamedTuple("NetworkKeyStatus", [("net_key_index", int),])

ModelBindStatus = NamedTuple(
    "ModelBindStatus",
    [("element_address", int), ("app_key_index", int), ("model", Type[Model]),],
)

ModelSubscriptionStatus = NamedTuple(
    "ModelSubscriptionStatus",
    [("element_address", int), ("subscription_address", int), ("model", Type[Model]),],
)

ModelSubscriptionList = NamedTuple(
    "ModelSubscriptionList",
    [("element_address", int), ("model", Type[Model]), ("addresses", Sequence[int]),],
)

ModelPublicationStatus = NamedTuple(
    "ModelSubscriptionStatus",
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
        ConfigOpcode.APPKEY_LIST,
        ConfigOpcode.APPKEY_STATUS,
        ConfigOpcode.BEACON_STATUS,
        ConfigOpcode.COMPOSITION_DATA_STATUS,
        ConfigOpcode.DEFAULT_TTL_STATUS,
        ConfigOpcode.FRIEND_STATUS,
        ConfigOpcode.GATT_PROXY_STATUS,
        ConfigOpcode.HEARBEAT_PUBLICATION_STATUS,
        ConfigOpcode.HEARBEAT_SUBSCRIPTION_STATUS,
        ConfigOpcode.KEY_REFRESH_PHASE_STATUS,
        ConfigOpcode.LOW_POWER_NODE_POLLTIMEOUT_STATUS,
        ConfigOpcode.MODEL_APP_STATUS,
        ConfigOpcode.MODEL_PUBLICATION_STATUS,
        ConfigOpcode.MODEL_SUBSCRIPTION_STATUS,
        ConfigOpcode.NETKEY_LIST,
        ConfigOpcode.NETKEY_STATUS,
        ConfigOpcode.NETWORK_TRANSMIT_STATUS,
        ConfigOpcode.NODE_IDENTITY_STATUS,
        ConfigOpcode.NODE_RESET_STATUS,
        ConfigOpcode.RELAY_STATUS,
        ConfigOpcode.SIG_MODEL_APP_LIST,
        ConfigOpcode.SIG_MODEL_SUBSCRIPTION_LIST,
        ConfigOpcode.VENDOR_MODEL_APP_LIST,
        ConfigOpcode.VENDOR_MODEL_SUBSCRIPTION_LIST,
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

        async def _progress_callback(address, result, done, total):
            if isinstance(result, TimeoutError):
                self.logger.warning("Callback timeout for addr %s", address)
                return

            try:
                aw = progress_callback(address, result["params"]["data"], done, total)
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
            node: None if isinstance(result, Exception) else result["params"]
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
                opcode=ConfigOpcode.COMPOSITION_DATA_GET, params=dict(page=0,)
            ),
            status=dict(
                opcode=ConfigOpcode.COMPOSITION_DATA_STATUS, params=dict(page=0,)
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
            request=dict(opcode=ConfigOpcode.DEFAULT_TTL_GET, params=dict()),
            status=dict(opcode=ConfigOpcode.DEFAULT_TTL_STATUS, params=dict()),
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
            request=dict(opcode=ConfigOpcode.RELAY_GET, params=dict()),
            status=dict(opcode=ConfigOpcode.RELAY_STATUS, params=dict()),
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
                opcode=ConfigOpcode.KEY_REFRESH_PHASE_GET, params=dict(net_key_index=0,)
            ),
            status=dict(
                opcode=ConfigOpcode.KEY_REFRESH_PHASE_STATUS,
                params=dict(net_key_index=net_key_index,),
            ),
            send_interval=send_interval,
            progress_callback=progress_callback,
            timeout=timeout or 2 * send_interval * len(nodes),
        )

    async def add_net_key(
        self, destination: int, net_index: int, net_key_index: int, net_key: NetworkKey
    ) -> NetKeyStatus:
        status = self.expect_dev(
            destination,
            net_index=net_index,
            opcode=ConfigOpcode.NETKEY_STATUS,
            params=dict(net_key_index=net_key_index, status=StatusCode.SUCCESS,),
        )

        request = partial(
            self.send_dev,
            destination,
            net_index=net_index,
            opcode=ConfigOpcode.NETKEY_ADD,
            params=dict(net_key_index=net_key_index, net_key=net_key.bytes,),
        )

        status = await self.query(request, status)

        if status["params"]["status"] != StatusCode.SUCCESS:
            raise ModelOperationError("Cannot add net key", status)

        return NetKeyStatus(net_key_index=net_key_index)

    async def delete_net_key(
        self, destination: int, net_index: int, net_key_index: int
    ) -> NetKeyStatus:
        status = self.expect_dev(
            destination,
            net_index=net_index,
            opcode=ConfigOpcode.NETKEY_STATUS,
            params=dict(net_key_index=net_key_index, status=StatusCode.SUCCESS,),
        )

        request = partial(
            self.send_dev,
            destination,
            net_index=net_index,
            opcode=ConfigOpcode.NETKEY_DELETE,
            params=dict(net_key_index=net_key_index,),
        )

        status = await self.query(request, status)

        if status["params"]["status"] != StatusCode.SUCCESS:
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
        status = self.expect_dev(
            destination,
            net_index=net_index,
            opcode=ConfigOpcode.APPKEY_STATUS,
            params=dict(net_key_index=net_key_index, app_key_index=app_key_index,),
        )

        request = partial(
            self.send_dev,
            destination,
            net_index=net_index,
            opcode=ConfigOpcode.APPKEY_ADD,
            params=dict(
                net_key_index=net_key_index,
                app_key_index=app_key_index,
                app_key=app_key.bytes,
            ),
        )

        status = await self.query(request, status)

        if status["params"]["status"] != StatusCode.SUCCESS:
            raise ModelOperationError("Cannot add app key", status)

        return AppKeyStatus(
            status["params"]["net_key_index"], status["params"]["app_key_index"]
        )

    async def delete_app_key(
        self, destination: int, net_index: int, app_key_index: int, net_key_index: int,
    ) -> AppKeyStatus:
        status = self.expect_dev(
            destination,
            net_index=net_index,
            opcode=ConfigOpcode.APPKEY_STATUS,
            params=dict(net_key_index=net_key_index, app_key_index=app_key_index,),
        )

        request = partial(
            self.send_dev,
            destination,
            net_index=net_index,
            opcode=ConfigOpcode.APPKEY_DELETE,
            params=dict(net_key_index=net_key_index, app_key_index=app_key_index,),
        )

        status = await self.query(request, status)

        if status["params"]["status"] != StatusCode.SUCCESS:
            raise ModelOperationError("Cannot delete app key", status)

        return AppKeyStatus(
            status["params"]["net_key_index"], status["params"]["app_key_index"]
        )

    async def update_app_key(
        self,
        destination: int,
        net_index: int,
        net_key_index: int,
        app_key_index: int,
        app_key: ApplicationKey,
    ) -> AppKeyStatus:
        status = self.expect_dev(
            destination,
            net_index=net_index,
            opcode=ConfigOpcode.APPKEY_STATUS,
            params=dict(net_key_index=net_key_index, app_key_index=app_key_index,),
        )

        request = partial(
            self.send_dev,
            destination,
            net_index=net_index,
            opcode=ConfigOpcode.APPKEY_UPDATE,
            params=dict(app_key_index=0, net_key_index=0, app_key=app_key.bytes,),
        )

        status = await self.query(request, status)

        if status["params"]["status"] != StatusCode.SUCCESS:
            raise ModelOperationError("Cannot update app key", status)

        return AppKeyStatus(
            status["params"]["net_key_index"], status["params"]["app_key_index"]
        )

    async def bind_app_key(
        self,
        destination: int,
        net_index: int,
        element_address: int,
        app_key_index: int,
        model: Type[Model],
    ) -> ModelBindStatus:
        status = self.expect_dev(
            destination,
            net_index=net_index,
            opcode=ConfigOpcode.MODEL_APP_STATUS,
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
            opcode=ConfigOpcode.MODEL_APP_BIND,
            params=dict(
                element_address=element_address,
                app_key_index=app_key_index,
                model=self._get_model_id(model),
            ),
        )

        status = await self.query(request, status)

        if status["params"]["status"] != StatusCode.SUCCESS:
            raise ModelOperationError("Cannot bind app key", status)

        return ModelBindStatus(
            status["params"]["element_address"],
            status["params"]["app_key_index"],
            model,
        )

    async def get_network_transmission(
        self, destination: int, net_index: int
    ) -> Tuple[int, int]:
        status = self.expect_dev(
            destination,
            net_index=net_index,
            opcode=ConfigOpcode.NETWORK_TRANSMIT_STATUS,
            params=dict(),
        )

        request = partial(
            self.send_dev,
            destination,
            net_index=net_index,
            opcode=ConfigOpcode.NETWORK_TRANSMIT_GET,
            params=dict(),
        )

        status = await self.query(request, status)
        return (status["params"]["interval"], status["params"]["count"])

    async def set_network_transmission(
        self, destination: int, net_index: int, interval: int, count: int
    ) -> Tuple[int, int]:
        status = self.expect_dev(
            destination,
            net_index=net_index,
            opcode=ConfigOpcode.NETWORK_TRANSMIT_STATUS,
            params=dict(interval=interval, count=count),
        )

        request = partial(
            self.send_dev,
            destination,
            net_index=net_index,
            opcode=ConfigOpcode.NETWORK_TRANSMIT_SET,
            params=dict(interval=interval, count=count),
        )

        status = await self.query(request, status)
        return (status["params"]["interval"], status["params"]["count"])

    async def update_net_key(
        self, destination: int, net_index: int, net_key_index: int, net_key: NetworkKey
    ) -> int:
        status = self.expect_dev(
            destination,
            net_index=net_index,
            opcode=ConfigOpcode.NETKEY_STATUS,
            params=dict(net_key_index=net_key_index,),
        )

        request = partial(
            self.send_dev,
            destination,
            net_index=net_index,
            opcode=ConfigOpcode.NETKEY_UPDATE,
            params=dict(net_key_index=0, net_key=net_key.bytes,),
        )

        status = await self.query(request, status)

        if status["params"]["status"] != StatusCode.SUCCESS:
            raise ModelOperationError("Cannot update net key", status)

        return status["params"]["net_key_index"]

    async def add_subscription(
        self,
        destination: int,
        net_index: int,
        element_address: int,
        subscription_address: int,
        model: Type[Model],
    ) -> ModelSubscriptionStatus:
        status = self.expect_dev(
            destination,
            net_index=net_index,
            opcode=ConfigOpcode.MODEL_SUBSCRIPTION_STATUS,
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
            opcode=ConfigOpcode.MODEL_SUBSCRIPTION_ADD,
            params=dict(
                element_address=element_address,
                address=subscription_address,
                model=self._get_model_id(model),
            ),
        )

        status = await self.query(request, status)

        if status["params"]["status"] != StatusCode.SUCCESS:
            raise ModelOperationError("Cannot add subscription", status)

        return ModelSubscriptionStatus(
            status["params"]["element_address"], status["params"]["address"], model
        )

    async def del_subscription(
        self,
        destination: int,
        net_index: int,
        element_address: int,
        subscription_address: int,
        model: Type[Model],
    ) -> ModelSubscriptionStatus:
        status = self.expect_dev(
            destination,
            net_index=net_index,
            opcode=ConfigOpcode.MODEL_SUBSCRIPTION_STATUS,
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
            opcode=ConfigOpcode.MODEL_SUBSCRIPTION_DELETE,
            params=dict(
                element_address=element_address,
                address=subscription_address,
                model=self._get_model_id(model),
            ),
        )

        status = await self.query(request, status)

        if status["params"]["status"] != StatusCode.SUCCESS:
            raise ModelOperationError("Cannot add subscription", status)

        return ModelSubscriptionStatus(
            status["params"]["element_address"], status["params"]["address"], model
        )

    async def clear_subscriptions(
        self, destination: int, net_index: int, element_address: int, model: Type[Model]
    ) -> ModelSubscriptionStatus:
        status = self.expect_dev(
            destination,
            net_index=net_index,
            opcode=ConfigOpcode.MODEL_SUBSCRIPTION_STATUS,
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
            opcode=ConfigOpcode.MODEL_SUBSCRIPTION_DELETE_ALL,
            params=dict(
                element_address=element_address, model=self._get_model_id(model),
            ),
        )

        status = await self.query(request, status)

        if status["params"]["status"] != StatusCode.SUCCESS:
            raise ModelOperationError("Cannot add subscription", status)

        return ModelSubscriptionStatus(
            status["params"]["element_address"], status["params"]["address"], model
        )

    async def get_subscriptions(
        self, destination: int, net_index: int, element_address: int, model: Type[Model]
    ) -> ModelSubscriptionList:
        if model.MODEL_ID[0] is not None:
            status_opcode = ConfigOpcode.VENDOR_MODEL_SUBSCRIPTION_LIST
            request_opcode = ConfigOpcode.VENDOR_MODEL_SUBSCRIPTION_GET
        else:
            status_opcode = ConfigOpcode.SIG_MODEL_SUBSCRIPTION_LIST
            request_opcode = ConfigOpcode.SIG_MODEL_SUBSCRIPTION_GET

        status = self.expect_dev(
            destination,
            net_index=net_index,
            opcode=status_opcode,
            params=dict(
                element_address=element_address, model=self._get_model_id(model),
            ),
        )

        request = partial(
            self.send_dev,
            destination,
            net_index=net_index,
            opcode=request_opcode,
            params=dict(
                element_address=element_address, model=self._get_model_id(model),
            ),
        )

        status = await self.query(request, status)

        if status["params"]["status"] != StatusCode.SUCCESS:
            raise ModelOperationError("Cannot get subscription list", status)

        return ModelSubscriptionList(
            status["params"]["element_address"], model, status["params"]["addresses"],
        )

    async def get_publication(
        self, destination: int, net_index: int, element_address: int, model: Type[Model]
    ) -> ModelPublicationStatus:
        status = self.expect_dev(
            destination,
            net_index=net_index,
            opcode=ConfigOpcode.MODEL_PUBLICATION_STATUS,
            params=dict(),
        )

        request = partial(
            self.send_dev,
            destination,
            net_index=net_index,
            opcode=ConfigOpcode.MODEL_PUBLICATION_GET,
            params=dict(
                element_address=element_address, model=self._get_model_id(model)
            ),
        )

        status = await self.query(request, status)

        period = (
            status["params"]["publish_period"]["step_resolution"].multiplier
            * status["params"]["publish_period"]["number_of_steps"]
        )

        retransmissions = dict(
            count=status["params"]["retransmit"]["count"],
            interval=timedelta(milliseconds=status["params"]["retransmit"]["interval"]),
        )

        return ModelPublicationStatus(
            status["params"]["element_address"],
            status["params"]["publish_address"],
            status["params"]["TTL"],
            status["params"]["app_key_index"],
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
        TTL: int = 8,
        publish_step_resolution: PublishPeriodStepResolution = PublishPeriodStepResolution.RESOLUTION_10_S,
        publish_number_of_steps: int = 6,  # 60seconds
        retransmit_count: int = 0,
        retransmit_interval: int = 50,
    ) -> ModelSubscriptionStatus:

        status = self.expect_dev(
            destination,
            net_index=net_index,
            opcode=ConfigOpcode.MODEL_PUBLICATION_STATUS,
            params=dict(
                status=StatusCode.SUCCESS,
                element_address=element_address,
                publish_address=publication_address,
                TTL=TTL,
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
            opcode=ConfigOpcode.MODEL_PUBLICATION_SET,
            params=dict(
                element_address=element_address,
                publish_address=publication_address,
                TTL=TTL,
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

        if status["params"]["status"] != StatusCode.SUCCESS:
            raise ModelOperationError("Cannot add subscription", status)

        period = (
            status["params"]["publish_period"]["step_resolution"].multiplier
            * status["params"]["publish_period"]["number_of_steps"]
        )

        retransmissions = dict(
            count=status["params"]["retransmit"]["count"],
            interval=timedelta(milliseconds=status["params"]["retransmit"]["interval"]),
        )

        return ModelPublicationStatus(
            status["params"]["element_address"],
            status["params"]["publish_address"],
            status["params"]["TTL"],
            status["params"]["app_key_index"],
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
        status = self.expect_dev(
            destination,
            net_index=net_index,
            opcode=ConfigOpcode.BEACON_STATUS,
            params=dict(
                beacon=SecureNetworkBeacon.ON if enabled else SecureNetworkBeacon.OFF,
            ),
        )

        request = partial(
            self.send_dev,
            destination,
            net_index=net_index,
            opcode=ConfigOpcode.BEACON_SET,
            params=dict(
                beacon=SecureNetworkBeacon.ON if enabled else SecureNetworkBeacon.OFF,
            ),
        )

        status = await self.query(
            request, status, send_interval=send_interval, timeout=timeout
        )

        return status["params"]["beacon"]


class HealthServer(Model):
    MODEL_ID = (None, 0x0002)
    OPCODES = {
        HealthOpcode.FAULT_GET,
        HealthOpcode.FAULT_CLEAR,
        HealthOpcode.FAULT_CLEAR_UNACKNOWLEDGED,
        HealthOpcode.FAULT_TEST,
        HealthOpcode.FAULT_TEST_UNACKNOWLEDGED,
        HealthOpcode.PERIOD_GET,
        HealthOpcode.PERIOD_SET,
        HealthOpcode.PERIOD_SET_UNACKNOWLEDGED,
        HealthOpcode.ATTENTION_GET,
        HealthOpcode.ATTENTION_SET,
        HealthOpcode.ATTENTION_SET_UNACKNOWLEDGED,
    }
    PUBLISH = True
    SUBSCRIBE = True


class HealthClient(Model):
    MODEL_ID = (None, 0x0003)
    OPCODES = {
        HealthOpcode.CURRENT_STATUS,
        HealthOpcode.FAULT_STATUS,
        HealthOpcode.PERIOD_STATUS,
        HealthOpcode.ATTENTION_STATUS,
    }
    PUBLISH = True
    SUBSCRIBE = True

    async def attention(self, destination: int, app_index: int, attention: int) -> int:
        status = self.expect_app(
            destination,
            app_index=app_index,
            destination=None,
            opcode=HealthOpcode.ATTENTION_STATUS,
            params=dict(attention=attention,),
        )

        request = partial(
            self.send_app,
            destination,
            app_index=app_index,
            opcode=HealthOpcode.ATTENTION_SET,
            params=dict(attention=attention,),
        )

        status = await self.query(request, status)
        return status["params"]["attention"]

    async def attention_unack(self, destination: int, app_index: int, attention: int):
        request = partial(
            self.send_app,
            destination,
            app_index=app_index,
            opcode=HealthOpcode.ATTENTION_SET_UNACKNOWLEDGED,
            params=dict(attention=attention,),
        )

        await self.repeat(request)


class DebugServer(Model):
    MODEL_ID = (0x0136, 0x0002)
    OPCODES = {
        DebugOpcode.OPCODE,
    }
    PUBLISH = True
    SUBSCRIBE = True


class DebugClient(Model):
    MODEL_ID = (0x0136, 0x0016)
    OPCODES = {
        DebugOpcode.OPCODE,
    }
    PUBLISH = True
    SUBSCRIBE = True

    async def get_param(
        self,
        nodes: Iterable[int],
        net_index: int,
        request: int,
        status: int,
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
                opcode=DebugOpcode.OPCODE,
                params=dict(subopcode=request),
            )
            for node in nodes
        }

        statuses = {
            node: self.expect_dev(
                node,
                net_index=net_index,
                opcode=DebugOpcode.OPCODE,
                params=dict(subopcode=status),
            )
            for node in nodes
        }

        async def _progress_callback(address, result, done, total):
            if isinstance(result, TimeoutError):
                self.logger.warning("Callback timeout for addr %s", address)
                return

            try:
                aw = progress_callback(address, result["params"]["data"], done, total)

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
            node: None if isinstance(result, Exception) else result["params"]["data"]
            for node, result in results.items()
        }

    async def get_uptime(
        self, nodes: Sequence[int], app_index: int
    ) -> Dict[int, Optional[Any]]:
        return await self.get_param(
            nodes,
            app_index,
            DebugSubOpcode.UPTIME_GET,
            DebugSubOpcode.UPTIME_STATUS,
            send_interval=0.1,
            timeout=len(nodes) * 0.5,
        )

    async def get_last_sw_fault(
        self, nodes: Sequence[int], app_index: int
    ) -> Dict[int, Optional[Any]]:
        return await self.get_param(
            nodes,
            app_index,
            DebugSubOpcode.LAST_SW_FAULT_GET,
            DebugSubOpcode.LAST_SW_FAULT_STATUS,
            send_interval=0.1,
            timeout=len(nodes) * 0.5,
        )

    async def get_firmware_version(
        self, nodes: Sequence[int], app_index: int
    ) -> Dict[int, Optional[Any]]:
        return await self.get_param(
            nodes,
            app_index,
            DebugSubOpcode.FULL_FIRMWARE_VERSION_GET,
            DebugSubOpcode.FULL_FIRMWARE_VERSION_STATUS,
            send_interval=0.1,
            timeout=len(nodes) * 0.5,
        )

    async def get_app_version(
        self, nodes: Sequence[int], app_index: int
    ) -> Dict[int, Optional[Any]]:
        return await self.get_param(
            nodes,
            app_index,
            DebugSubOpcode.PROVISIONED_APP_VERSION_GET,
            DebugSubOpcode.PROVISIONED_APP_VERSION_STATUS,
            send_interval=0.1,
            timeout=len(nodes) * 0.5,
        )

    async def get_ivindex(
        self, nodes: Sequence[int], app_index: int
    ) -> Dict[int, Optional[Any]]:
        return await self.get_param(
            nodes,
            app_index,
            DebugSubOpcode.IV_INDEX_GET,
            DebugSubOpcode.IV_INDEX_STATUS,
            send_interval=0.1,
            timeout=len(nodes) * 0.5,
        )

    async def get_system_stats(
        self, nodes: Sequence[int], app_index: int
    ) -> Dict[int, Optional[Any]]:
        return await self.get_param(
            nodes,
            app_index,
            DebugSubOpcode.SYSTEM_STATS_GET,
            DebugSubOpcode.SYSTEM_STATS_STATUS,
            send_interval=2,
            timeout=max(5, len(nodes) * 2),
        )

    async def get_arap_content(
        self,
        nodes: Sequence[int],
        app_index: int,
        *,
        progress_callback: Optional[ProgressCallback] = None,
    ) -> Dict[int, Optional[Any]]:
        requests = {
            node: partial(
                self.send_dev,
                node,
                net_index=app_index,
                opcode=DebugOpcode.OPCODE,
                params=dict(
                    subopcode=DebugSubOpcode.ARAP_LIST_CONTENT_GET, data=dict(page=0),
                ),
            )
            for node in nodes
        }

        statuses = {
            node: self.expect_dev(
                node,
                net_index=0,
                opcode=DebugOpcode.OPCODE,
                params=dict(subopcode=DebugSubOpcode.ARAP_LIST_CONTENT_STATUS),
            )
            for node in nodes
        }

        results = await self.bulk_query(
            requests,
            statuses,
            send_interval=0.5,
            timeout=max(2.5, len(nodes) * 1.0),
            progress_callback=progress_callback,
        )

        return {
            node: None if isinstance(result, Exception) else result["params"]["data"]
            for node, result in results.items()
        }


class NetworkDiagnosticClient(Model):
    MODEL_ID = (0x0136, 0x0014)
    OPCODES = {
        NetworkDiagnosticServerOpcode.OPCODE,
    }
    PUBLISH = True
    SUBSCRIBE = True


class NetworkDiagnosticSetupClient(Model):
    MODEL_ID = (0x0136, 0x0015)
    OPCODES = {
        NetworkDiagnosticSetupServerOpcode.OPCODE,
    }
    PUBLISH = True


class GenericOnOffServer(Model):
    MODEL_ID = (None, 0x1000)
    OPCODES = {
        GenericOnOffOpcode.ONOFF_GET,
        GenericOnOffOpcode.ONOFF_SET,
        GenericOnOffOpcode.ONOFF_SET_UNACKNOWLEDGED,
    }
    PUBLISH = True
    SUBSCRIBE = True


class GenericOnOffClient(Model):
    MODEL_ID = (None, 0x1001)
    OPCODES = {
        GenericOnOffOpcode.ONOFF_STATUS,
    }
    PUBLISH = True
    SUBSCRIBE = True
    _tid = 0

    @property
    def tid(self) -> int:
        self._tid = (self._tid + 1) % 255
        return self._tid

    async def set_onoff(
        self,
        destination: int,
        app_index: int,
        onoff: int,
        delay: float = 0.5,
        send_interval: float = 0.07,
    ) -> int:
        values = dict(delay=delay, send_interval=send_interval, tid=self.tid)

        status = self.expect_app(
            destination,
            app_index=app_index,
            destination=None,
            opcode=GenericOnOffOpcode.ONOFF_STATUS,
            params=dict(present_onoff=onoff),
        )

        async def request():
            ret = self.send_app(
                destination,
                app_index=app_index,
                opcode=GenericOnOffOpcode.ONOFF_SET,
                params=dict(
                    onoff=onoff,
                    tid=values["tid"],
                    transition_time=0,
                    delay=values["delay"],
                ),
            )
            values["delay"] -= values["send_interval"]
            values["delay"] = max(0, values["delay"])

            return await ret

        status = await self.query(
            request, status, send_interval=values["send_interval"], timeout=1
        )

        return status["params"]["present_onoff"]

    async def set_onoff_unack(
        self,
        destination: int,
        app_index: int,
        onoff: int,
        delay: float = 0.5,
        send_interval: float = 0.07,
        transition_time: float = 0,
        retransmissions: int = 6,
    ):
        values = dict(delay=delay, send_interval=send_interval, tid=self.tid)

        async def request():
            ret = self.send_app(
                destination,
                app_index=app_index,
                opcode=GenericOnOffOpcode.ONOFF_SET_UNACKNOWLEDGED,
                params=dict(
                    onoff=onoff,
                    tid=values["tid"],
                    transition_time=transition_time,
                    delay=values["delay"],
                ),
            )
            values["delay"] -= values["send_interval"]
            values["delay"] = max(0, values["delay"])

            return await ret

        await self.repeat(
            request,
            retransmissions=retransmissions,
            send_interval=values["send_interval"],
        )

    async def get_light_status(
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
                opcode=GenericOnOffOpcode.ONOFF_GET,
                params=dict(),
            )
            for node in nodes
        }

        statuses = {
            node: self.expect_app(
                node,
                app_index=0,
                destination=None,
                opcode=GenericOnOffOpcode.ONOFF_STATUS,
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
            node: None if isinstance(result, Exception) else result["params"]
            for node, result in results.items()
        }


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

    def __init__(self, element: "Element"):
        super().__init__(element)
        self.__tid = itertools.cycle(range(255))

    async def recall_scene_unack(
        self,
        destination: int,
        app_index: int,
        scene_number: int,
        transition_time: float,
    ):
        values = dict(delay=0.5, send_interval=0.075, tid=next(self.__tid))

        async def request():
            ret = self.send_app(
                destination,
                app_index=app_index,
                opcode=SceneOpcode.SCENE_RECALL_UNACKNOWLEDGED,
                params=dict(
                    scene_number=scene_number,
                    tid=values["tid"],
                    transition_time=transition_time,
                    delay=values["delay"],
                ),
            )
            values["delay"] -= values["send_interval"]
            values["delay"] = max(0, values["delay"])

            return await ret

        await self.repeat(
            request, retransmissions=6, send_interval=values["send_interval"]
        )

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

        statuses = {
            node: self.expect_app(
                node,
                app_index=0,
                destination=None,
                opcode=SceneOpcode.SCENE_STATUS,
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
            node: None if isinstance(result, Exception) else result["params"]
            for node, result in results.items()
        }


class GenericLevelClient(Model):
    MODEL_ID = (None, 0x1003)
    OPCODES = {
        GenericLevelOpcode.LEVEL_GET,
        GenericLevelOpcode.LEVEL_SET,
        GenericLevelOpcode.LEVEL_SET_UNACKNOWLEDGED,
        GenericLevelOpcode.DELTA_SET,
        GenericLevelOpcode.DELTA_SET_UNACKNOWLEDGED,
        GenericLevelOpcode.MOVE_SET,
        GenericLevelOpcode.MOVE_SET_UNACKNOWLEDGED,
    }
    PUBLISH = True
    SUBSCRIBE = True

    def __init__(self, element: "Element"):
        super().__init__(element)
        self.__tid = itertools.cycle(range(255))

    async def set_level_unack(
        self,
        destination: int,
        app_index: int,
        level: int,
        delay: float = 0.5,
        send_interval: float = 0.07,
        transition_time: float = 0,
        retransmissions: int = 6,
    ):

        values = dict(delay=delay, send_interval=send_interval, tid=next(self.__tid))

        async def request():
            ret = self.send_app(
                destination,
                app_index=app_index,
                opcode=GenericLevelOpcode.LEVEL_SET_UNACKNOWLEDGED,
                params=dict(
                    level=level,
                    tid=values["tid"],
                    transition_time=transition_time,
                    delay=values["delay"],
                ),
            )
            values["delay"] -= values["send_interval"]
            values["delay"] = max(0, values["delay"])

            return await ret

        await self.repeat(
            request,
            retransmissions=retransmissions,
            send_interval=values["send_interval"],
        )


class LightLightnessServer(Model):
    MODEL_ID = (None, 0x1300)
    OPCODES = {
        LightLightnessOpcode.LIGHTNESS_GET,
        LightLightnessOpcode.LIGHTNESS_SET,
        LightLightnessOpcode.LIGHTNESS_SET_UNACKNOWLEDGED,
        LightLightnessOpcode.LIGHTNESS_STATUS,
    }
    PUBLISH = True
    SUBSCRIBE = True


class LightLightnessSetupServer(Model):
    MODEL_ID = (None, 0x1301)
    OPCODES = {
        LightLightnessSetupOpcode.LIGHTNESS_DEFAULT_SET,
        LightLightnessSetupOpcode.LIGHTNESS_DEFAULT_SET_UNACKNOWLEDGED,
        LightLightnessSetupOpcode.LIGHTNESS_RANGE_SET,
        LightLightnessSetupOpcode.LIGHTNESS_RANGE_SET_UNACKNOWLEDGED,
    }
    SUBSCRIBE = True


class LightLightnessClient(Model):
    MODEL_ID = (None, 0x1302)
    OPCODES = {
        LightLightnessOpcode.LIGHTNESS_GET,
        LightLightnessOpcode.LIGHTNESS_SET,
        LightLightnessOpcode.LIGHTNESS_SET_UNACKNOWLEDGED,
        LightLightnessOpcode.LIGHTNESS_STATUS,
        LightLightnessSetupOpcode.LIGHTNESS_RANGE_SET_UNACKNOWLEDGED,
    }
    PUBLISH = True
    SUBSCRIBE = True
    _tid = 0

    @property
    def tid(self) -> int:
        self._tid = (self._tid + 1) % 255
        return self._tid

    async def set_lightness_range_unack(
        self,
        destination: int,
        app_index: int,
        min_lightness: int,
        max_lightness: int,
        *,
        retransmissions: int = 6,
        send_interval: float = 0.075,
    ) -> None:
        async def request():
            ret = self.send_app(
                destination,
                app_index=app_index,
                opcode=LightLightnessSetupOpcode.LIGHTNESS_RANGE_SET_UNACKNOWLEDGED,
                params=dict(range_min=min_lightness, range_max=max_lightness,),
            )

            return await ret

        await self.repeat(
            request, retransmissions=retransmissions, send_interval=send_interval
        )

    async def get_lightness(
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
                opcode=LightLightnessOpcode.LIGHTNESS_GET,
                params=dict(),
            )
            for node in nodes
        }

        statuses = {
            node: self.expect_app(
                node,
                app_index=0,
                destination=None,
                opcode=LightLightnessOpcode.LIGHTNESS_STATUS,
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
            node: None if isinstance(result, Exception) else result["params"]
            for node, result in results.items()
        }

    async def set_lightness(
        self,
        nodes: Sequence[int],
        lightness: int,
        app_index: int,
        *,
        delay: float = 0.5,
        send_interval: float = 0.1,
        timeout: Optional[float] = None,
    ) -> Dict[int, Optional[Any]]:
        values = dict(delay=delay, send_interval=send_interval, tid=self.tid)

        requests = {
            node: partial(
                self.send_app,
                node,
                app_index=app_index,
                opcode=LightLightnessOpcode.LIGHTNESS_SET,
                params=dict(lightness=lightness, tid=values["tid"],),
            )
            for node in nodes
        }

        statuses = {
            node: self.expect_app(
                node,
                app_index=0,
                destination=None,
                opcode=LightLightnessOpcode.LIGHTNESS_STATUS,
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
            node: None if isinstance(result, Exception) else result["params"]
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


class LightCTLClient(Model):
    MODEL_ID = (None, 0x1305)
    OPCODES = {
        LightCTLOpcode.CTL_GET,
        LightCTLOpcode.CTL_SET,
        LightCTLOpcode.CTL_SET_UNACKNOWLEDGED,
        LightCTLOpcode.CTL_STATUS,
        LightCTLOpcode.CTL_TEMPERATURE_GET,
        LightCTLOpcode.CTL_TEMPERATURE_RANGE_GET,
        LightCTLOpcode.CTL_TEMPERATURE_RANGE_STATUS,
        LightCTLOpcode.CTL_TEMPERATURE_SET,
        LightCTLOpcode.CTL_TEMPERATURE_SET_UNACKNOWLEDGED,
        LightCTLOpcode.CTL_TEMPERATURE_STATUS,
        LightCTLOpcode.CTL_TEMPERATURE_DEFAULT_GET,
        LightCTLOpcode.CTL_TEMPERATURE_DEFAULT_STATUS,
    }
    PUBLISH = True
    SUBSCRIBE = True
    _tid = 0

    @property
    def tid(self) -> int:
        self._tid = (self._tid + 1) % 255
        return self._tid

    async def get_ctl(
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
                opcode=LightCTLOpcode.CTL_TEMPERATURE_GET,
                params=dict(),
            )
            for node in nodes
        }

        statuses = {
            node: self.expect_app(
                node,
                app_index=0,
                destination=None,
                opcode=LightCTLOpcode.CTL_TEMPERATURE_STATUS,
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
            node: None if isinstance(result, Exception) else result["params"]
            for node, result in results.items()
        }

    async def set_ctl(
        self,
        nodes: Sequence[int],
        app_index: int,
        *,
        ctl_temperature: int,
        send_interval: float = 0.1,
        timeout: Optional[float] = None,
    ) -> Dict[int, Optional[Any]]:
        requests = {
            node: partial(
                self.send_app,
                node,
                app_index=app_index,
                opcode=LightCTLOpcode.CTL_TEMPERATURE_SET,
                params=dict(
                    ctl_temperature=ctl_temperature, ctl_delta_uv=0, tid=self.tid
                ),
            )
            for node in nodes
        }

        statuses = {
            node: self.expect_app(
                node,
                app_index=0,
                destination=None,
                opcode=LightCTLOpcode.CTL_TEMPERATURE_STATUS,
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
            node: None if isinstance(result, Exception) else result["params"]
            for node, result in results.items()
        }


class GatewayConfigServer(Model):
    MODEL_ID = (0x0136, 0x001D)
    OPCODES = {
        GatewayConfigServerOpcode.OPCODE,
    }
    PUBLISH = True
    SUBSCRIBE = True

    def send_configuration_status(
        self,
        destination: int,
        net_index: int,
        chip_rev_id: int,
        mtu: int,
        mac: str,
        server: Tuple[str, int],
        reconnect: int,
        ip: str,
        dns: str,
        gateway: str,
        netmask: int,
        dhcp: DhcpFlag,
    ):
        params = dict(
            subopcode=GatewayConfigServerSubOpcode.GATEWAY_CONFIGURATION_STATUS,
            payload=dict(
                chip_revision_id=chip_rev_id,
                mtu_size=mtu,
                mac_addr=mac,
                server_port_number=server[1],
                reconnect_interval=reconnect,
                server_address_length=len(server[0]),
                server_address=server[0],
                dns_ip_address=dns,
                ip_addr=ip,
                gateway_ip_addr=gateway,
                netmask=netmask,
                flags=dhcp,
            ),
        )
        self.send_dev(destination, net_index, GatewayConfigServerOpcode.OPCODE, params)

    def send_packets_status(
        self,
        destination: int,
        net_index: int,
        rx_errors: int,
        tx_errors: int,
        bandwidth: int,
        state: BitStruct(),
    ):
        params = dict(
            subopcode=GatewayConfigServerSubOpcode.GATEWAY_PACKETS_STATUS,
            payload=dict(
                total_eth_rx_errors=rx_errors,
                total_eth_tx_errors=tx_errors,
                bandwidth=bandwidth,
                connection_state=state,
            ),
        )
        self.send_dev(destination, net_index, GatewayConfigServerOpcode.OPCODE, params)


class GatewayConfigClient(Model):
    MODEL_ID = (0x0136, 0x001E)
    OPCODES = {
        GatewayConfigServerOpcode.OPCODE,
    }
    PUBLISH = True
    SUBSCRIBE = True

    async def configuration_get(self, destination: int, net_index: int):
        request = partial(
            self.send_dev,
            destination,
            net_index=net_index,
            opcode=GatewayConfigServerOpcode.OPCODE,
            params=dict(
                subopcode=GatewayConfigServerSubOpcode.GATEWAY_CONFIGURATION_GET,
            ),
        )

        status = self.expect_dev(
            destination,
            net_index=net_index,
            opcode=GatewayConfigServerOpcode.OPCODE,
            params=dict(
                subopcode=GatewayConfigServerSubOpcode.GATEWAY_CONFIGURATION_STATUS,
                payload=...,
            ),
        )
        return await self.query(request, status, timeout=1.0)

    async def configuration_set(
        self,
        destination: int,
        net_index: int,
        mtu: int,
        mac: str,
        server: Tuple[str, int],
        reconnect: int,
        dns: str = None,
        ip: str = None,
        gateway: str = None,
        netmask: int = None,
    ):
        payload = dict(
            mtu_size=mtu,
            mac_address=mac,
            server_port_number=server[1],
            reconnect_interval=reconnect,
            server_address_length=len(server[0]),
            server_address=server[0],
        )

        if dns:
            payload.update(dict(dns_ip_address=dns,))

        if ip and gateway and netmask:
            payload.update(
                dict(ip_address=ip, gateway_ip_address=gateway, netmask=netmask,)
            )

        request = partial(
            self.send_dev,
            destination,
            net_index=net_index,
            opcode=GatewayConfigServerOpcode.OPCODE,
            params=dict(
                subopcode=GatewayConfigServerSubOpcode.GATEWAY_CONFIGURATION_SET,
                payload=payload,
            ),
        )

        status = self.expect_dev(
            destination,
            net_index=net_index,
            opcode=GatewayConfigServerOpcode.OPCODE,
            params=dict(
                subopcode=GatewayConfigServerSubOpcode.GATEWAY_CONFIGURATION_STATUS,
                payload=...,
            ),
        )
        return await self.query(request, status, timeout=1.0)

    async def packets_get(self, destination: int, net_index: int):
        request = partial(
            self.send_dev,
            destination,
            net_index=net_index,
            opcode=GatewayConfigServerOpcode.OPCODE,
            params=dict(subopcode=GatewayConfigServerSubOpcode.GATEWAY_PACKETS_GET,),
        )

        status = self.expect_dev(
            destination,
            net_index=net_index,
            opcode=GatewayConfigServerOpcode.OPCODE,
            params=dict(subopcode=GatewayConfigServerSubOpcode.GATEWAY_PACKETS_STATUS,),
        )
        return await self.query(request, status, timeout=1.0)

    async def packets_clear(self, destination: int, net_index: int):
        request = partial(
            self.send_dev,
            destination,
            net_index=net_index,
            opcode=GatewayConfigServerOpcode.OPCODE,
            params=dict(subopcode=GatewayConfigServerSubOpcode.GATEWAY_PACKETS_CLEAR,),
        )

        status = self.expect_dev(
            destination,
            net_index=net_index,
            opcode=GatewayConfigServerOpcode.OPCODE,
            params=dict(
                subopcode=GatewayConfigServerSubOpcode.GATEWAY_PACKETS_STATUS,
                payload=...,
            ),
        )
        return await self.query(request, status, timeout=1.0)

    async def mtu_set(self, destination: int, net_index: int, mtu: int):
        request = partial(
            self.send_dev,
            destination,
            net_index=net_index,
            opcode=GatewayConfigServerOpcode.OPCODE,
            params=dict(
                subopcode=GatewayConfigServerSubOpcode.MTU_SIZE_SET,
                payload=dict(mtu_size=mtu),
            ),
        )

        status = self.expect_dev(
            destination,
            net_index=net_index,
            opcode=GatewayConfigServerOpcode.OPCODE,
            params=dict(
                subopcode=GatewayConfigServerSubOpcode.GATEWAY_CONFIGURATION_STATUS,
                payload=...,
            ),
        )
        return await self.query(request, status, timeout=1.0)

    async def mac_set(self, destination: int, net_index: int, mac: str):
        request = partial(
            self.send_dev,
            destination,
            net_index=net_index,
            opcode=GatewayConfigServerOpcode.OPCODE,
            params=dict(
                subopcode=GatewayConfigServerSubOpcode.ETHERNET_MAC_ADDRESS_SET,
                payload=dict(mac_address=mac),
            ),
        )

        status = self.expect_dev(
            destination,
            net_index=net_index,
            opcode=GatewayConfigServerOpcode.OPCODE,
            params=dict(
                subopcode=GatewayConfigServerSubOpcode.GATEWAY_CONFIGURATION_STATUS,
                payload=...,
            ),
        )
        return await self.query(request, status, timeout=1.0)

    async def server_set(
        self, destination: int, net_index: int, server: Tuple[str, int],
    ):
        request = partial(
            self.send_dev,
            destination,
            net_index=net_index,
            opcode=GatewayConfigServerOpcode.OPCODE,
            params=dict(
                subopcode=GatewayConfigServerSubOpcode.SERVER_ADDRESS_AND_PORT_NUMBER_SET,
                payload=dict(
                    server_port_number=server[1],
                    server_address_length=len(server[0]),
                    server_address=server[0],
                ),
            ),
        )

        status = self.expect_dev(
            destination,
            net_index=net_index,
            opcode=GatewayConfigServerOpcode.OPCODE,
            params=dict(
                subopcode=GatewayConfigServerSubOpcode.GATEWAY_CONFIGURATION_STATUS,
                payload=...,
            ),
        )
        return await self.query(request, status, timeout=1.0)

    async def reconnect_set(self, destination: int, net_index: int, reconnect: int):
        request = partial(
            self.send_dev,
            destination,
            net_index=net_index,
            opcode=GatewayConfigServerOpcode.OPCODE,
            params=dict(
                subopcode=GatewayConfigServerSubOpcode.RECONNECT_INTERVAL_SET,
                payload=dict(reconnect_interval=reconnect),
            ),
        )

        status = self.expect_dev(
            destination,
            net_index=net_index,
            opcode=GatewayConfigServerOpcode.OPCODE,
            params=dict(
                subopcode=GatewayConfigServerSubOpcode.GATEWAY_CONFIGURATION_STATUS,
                payload=...,
            ),
        )
        return await self.query(request, status, timeout=1.0)

    async def dns_set(self, destination: int, net_index: int, dns: str):
        request = partial(
            self.send_dev,
            destination,
            net_index=net_index,
            opcode=GatewayConfigServerOpcode.OPCODE,
            params=dict(
                subopcode=GatewayConfigServerSubOpcode.DNS_IP_ADDRESS_SET,
                payload=dict(dns_ip_address=dns),
            ),
        )

        status = self.expect_dev(
            destination,
            net_index=net_index,
            opcode=GatewayConfigServerOpcode.OPCODE,
            params=dict(
                subopcode=GatewayConfigServerSubOpcode.GATEWAY_CONFIGURATION_STATUS,
                payload=...,
            ),
        )
        return await self.query(request, status, timeout=1.0)

    async def ip_set(self, destination: int, net_index: int, ip: str):
        request = partial(
            self.send_dev,
            destination,
            net_index=net_index,
            opcode=GatewayConfigServerOpcode.OPCODE,
            params=dict(
                subopcode=GatewayConfigServerSubOpcode.IP_ADDRESS_SET,
                payload=dict(ip_address=ip),
            ),
        )

        status = self.expect_dev(
            destination,
            net_index=net_index,
            opcode=GatewayConfigServerOpcode.OPCODE,
            params=dict(
                subopcode=GatewayConfigServerSubOpcode.GATEWAY_CONFIGURATION_STATUS,
                payload=...,
            ),
        )
        return await self.query(request, status, timeout=1.0)

    async def gateway_set(self, destination: int, net_index: int, gateway: str):
        request = partial(
            self.send_dev,
            destination,
            net_index=net_index,
            opcode=GatewayConfigServerOpcode.OPCODE,
            params=dict(
                subopcode=GatewayConfigServerSubOpcode.GATEWAY_IP_ADDRESS_SET,
                payload=dict(gateway_ip_address=gateway),
            ),
        )

        status = self.expect_dev(
            destination,
            net_index=net_index,
            opcode=GatewayConfigServerOpcode.OPCODE,
            params=dict(
                subopcode=GatewayConfigServerSubOpcode.GATEWAY_CONFIGURATION_STATUS,
                payload=...,
            ),
        )
        return await self.query(request, status, timeout=1.0)

    async def netmask_set(self, destination: int, net_index: int, netmask: int):
        request = partial(
            self.send_dev,
            destination,
            net_index=net_index,
            opcode=GatewayConfigServerOpcode.OPCODE,
            params=dict(
                subopcode=GatewayConfigServerSubOpcode.NETMASK_SET,
                payload=dict(netmask=netmask),
            ),
        )

        status = self.expect_dev(
            destination,
            net_index=net_index,
            opcode=GatewayConfigServerOpcode.OPCODE,
            params=dict(
                subopcode=GatewayConfigServerSubOpcode.GATEWAY_CONFIGURATION_STATUS,
                payload=...,
            ),
        )
        return await self.query(request, status, timeout=1.0)


class LightExtendedControllerSetupClient(Model):
    MODEL_ID = (0x0136, 0x0012)
    OPCODES = {
        LightExtendedControllerOpcode.OPCODE,
    }
    PUBLISH = False
    SUBSCRIBE = True

    async def get_property(
        self,
        nodes: Iterable[int],
        net_index: int,
        property_id: int,
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
                opcode=LightExtendedControllerOpcode.OPCODE,
                params=dict(
                    subopcode=LightExtendedControllerSubOpcode.PROPERTY_GET,
                    payload=dict(id=property_id),
                ),
            )
            for node in nodes
        }

        statuses = {
            node: self.expect_dev(
                node,
                net_index=net_index,
                opcode=LightExtendedControllerOpcode.OPCODE,
                params=dict(
                    subopcode=LightExtendedControllerSubOpcode.PROPERTY_STATUS,
                    payload=dict(id=property_id),
                ),
            )
            for node in nodes
        }

        async def _progress_callback(address, result, done, total):
            if isinstance(result, TimeoutError):
                self.logger.warning("Callback timeout for addr %s", address)
                return

            try:
                aw = progress_callback(address, result["params"]["data"], done, total)

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
            node: None
            if isinstance(result, Exception)
            else result["params"]["payload"]["value"]
            for node, result in results.items()
        }

    async def get_auto_resume_mode(
        self, nodes: Sequence[int], net_index: int
    ) -> Dict[int, Optional[Any]]:
        return await self.get_property(
            nodes,
            net_index,
            LightExtendedControllerProperty.AUTO_RESUME_MODE,
            send_interval=0.1,
            timeout=len(nodes) * 0.5,
        )

    async def get_auto_resume_timer(
        self, nodes: Sequence[int], net_index: int
    ) -> Dict[int, Optional[Any]]:
        return await self.get_property(
            nodes,
            net_index,
            LightExtendedControllerProperty.AUTO_RESUME_TIMER,
            send_interval=0.1,
            timeout=len(nodes) * 0.5,
        )

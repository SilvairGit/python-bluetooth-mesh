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
This module provides a high-level API for BlueZ mesh stack.

.. _mesh-api.txt: https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/doc/mesh-api.txt
"""

import asyncio
import logging
from functools import lru_cache
from os import urandom
from typing import Any, Dict, List, Mapping, Optional, Tuple, Type, Union
from uuid import UUID, uuid5

import construct
import dbus_next

from bluetooth_mesh.crypto import ApplicationKey, DeviceKey, NetworkKey
from bluetooth_mesh.interfaces import (
    ApplicationInterface,
    DBusInterface,
    DBusService,
    ElementInterface,
    ManagementInterface,
    MeshService,
    NetworkInterface,
    NodeInterface,
    ProvisionAgentInterface,
)
from bluetooth_mesh.messages import AccessMessage
from bluetooth_mesh.models import ConfigClient
from bluetooth_mesh.tokenring import TokenRing
from bluetooth_mesh.utils import ParsedMeshMessage

__all__ = [
    "Application",
    "Element",
]


class CompositionDataMixin:
    """
    Provides propertied to company id, product id, version id and replay
    protection list size.

    These are used by :py:class:`bluetooth_mesh.interfaces.ApplicationInterface` to
    expose them via D-Bus.
    """

    COMPANY_ID = 0xFEE5
    PRODUCT_ID = 0x42
    VERSION_ID = 1
    CRPL = 0x7FFF

    @property
    def company_id(self) -> int:
        return self.COMPANY_ID

    @property
    def product_id(self) -> int:
        return self.PRODUCT_ID

    @property
    def version_id(self) -> int:
        return self.VERSION_ID

    @property
    def crpl(self) -> int:
        return self.CRPL


class TokenRingMixin:
    """
    Provides `token` property via persistent, UUID-based token storage.

    See :py:class:`bluetooth_mesh.tokenring.TokenRing` for details.
    """

    def __init__(self):
        super().__init__()
        self._token_ring = TokenRing()

    @property
    def token(self) -> int:
        return self._token_ring[self.uuid]

    @token.setter
    def token(self, value):
        self._token_ring[self.uuid] = value


class PathMixin:
    """
    Provides `path` property under which
    py:class:`bluetooth_mesh.interfaces.ApplicationInterface` will be registered on
    D-Bus.
    """

    PATH = "/com/silvair/application"

    @property
    def path(self) -> str:
        return self.PATH


class MachineUUIDMixin(PathMixin):
    """
    Provides `uuid` property based on systemd's machine-id.

    """

    def get_namespace(self):
        with open("/etc/machine-id") as machine_id:
            return UUID(machine_id.read().strip())

    @property
    @lru_cache(maxsize=1)
    def uuid(self) -> UUID:
        namespace = self.get_namespace()
        return uuid5(namespace=namespace, name=self.path)


class NetworkKeyMixin:
    @property
    def primary_net_key(self) -> Tuple[int, NetworkKey]:
        """
        Index and key of the network that the application belongs to. Used when
        creating a new node, see :py:func:`Application.import_node`.
        """
        raise NotImplementedError("Getting primary network key should be overridden!")

    @property
    def subnets_net_keys(self) -> List[Tuple[int, NetworkKey]]:
        """
        Indexes and keyes of the subnets.
        """
        raise NotImplementedError("Getting subnet network keys should be overridden!")


class ApplicationKeyMixin(NetworkKeyMixin):
    @property
    def primary_app_key(self) -> Tuple[int, int, ApplicationKey]:
        """
        Return first found application key that is bound to primary network key.
        """
        net_index, _ = self.primary_net_key

        for index, bound, key in self.app_keys:
            if bound == net_index:
                return index, bound, key

        raise IndexError("Primary application key not found")

    @property
    def app_keys(self) -> List[Tuple[int, int, ApplicationKey]]:
        """
        Indexes, bound network key indexes, and application keys.
        """
        raise NotImplementedError("Getting application keys should be overridden!")


class DeviceKeyMixin:
    @property
    @lru_cache(maxsize=1)
    def dev_key(self) -> DeviceKey:
        """
        Application's device_key. Used when creating a new node, see
        :py:func:`Application.import_node`.
        """
        return DeviceKey(urandom(16))


class DBusMixin:
    DBUS_SERVICE = None

    def _name_owner_changed(self, name, old_owner, new_owner):
        if name != self.DBUS_SERVICE.NAME:
            return

        self.logger.error("Disconnected from %s (%s)", name, old_owner)
        self.dbus_disconnected(old_owner)

    async def dbus_connect(self):
        message_bus = dbus_next.aio.MessageBus(bus_type=dbus_next.BusType.SYSTEM)
        self.logger.debug("Connecting to D-Bus")
        self.bus = await message_bus.connect()

        introspection = await self.bus.introspect(DBusService.NAME, DBusService.PATH)
        dbus_service = self.bus.get_proxy_object(
            DBusService.NAME, DBusService.PATH, introspection
        )
        self.dbus_interface = DBusInterface(dbus_service)

        self.logger.info("Connecting to %s", self.DBUS_SERVICE.NAME)
        owner = await self.dbus_interface.get_service(self.DBUS_SERVICE)

        self.dbus_interface.on_name_owner_changed(self._name_owner_changed)
        await self.dbus_connected(owner)

    async def dbus_disconnect(self):
        self.dbus_interface.off_name_owner_changed(self._name_owner_changed)
        self.bus.disconnect()

    async def dbus_connected(self, owner):
        pass

    def dbus_disconnected(self, owner):
        self.loop.stop()

    async def __aenter__(self):
        return await self.dbus_connect()

    async def __aexit__(self, exc_type, exc, tb):
        return await self.dbus_disconnect()


class Application(
    CompositionDataMixin,
    TokenRingMixin,
    MachineUUIDMixin,
    PathMixin,
    ApplicationKeyMixin,
    DeviceKeyMixin,
    NetworkKeyMixin,
    DBusMixin,
):
    """
    Base class for mesh applications.

    """

    DBUS_SERVICE = MeshService

    ELEMENTS = {}  # type: Dict[int, Type[Element]]

    def __init__(self, loop: asyncio.AbstractEventLoop):
        super().__init__()

        self.loop = loop
        self.logger = logging.getLogger(type(self).__name__)

        self.application_interface = ApplicationInterface(self)
        self.provision_agent_interface = ProvisionAgentInterface(self)

        self.elements = {}  # type: Dict[int, Element]

        self.network_interface = None
        self.node_interface = None
        self.management_interface = None
        self.addr = None

    async def dbus_connected(self, owner):
        introspection = await self.bus.introspect(
            self.DBUS_SERVICE.NAME, self.DBUS_SERVICE.PATH
        )
        service = self.bus.get_proxy_object(
            self.DBUS_SERVICE.NAME, self.DBUS_SERVICE.PATH, introspection
        )

        self.network_interface = NetworkInterface(service)
        self.node_interface = None
        self.management_interface = None

        self._register()

    def dbus_disconnected(self, owner):
        self._unregister()

        self.management_interface = None
        self.node_interface = None
        self.network_interface = None

        super().dbus_disconnected(owner)

    def _register(self):
        # pylint: disable=W0212
        self.logger.info("Registering application")

        self.bus.export(self.path, self.application_interface)
        self.bus.export(self.path, self.provision_agent_interface)

        for index, element_class in self.ELEMENTS.items():
            element = element_class(self, index)
            self.elements[index] = element

            element_interface = ElementInterface(element)
            self.bus.export(element.path, element_interface)

    def _unregister(self):
        # pylint: disable=W0212
        self.logger.info("Unregistering application")

        for element in self.elements.values():
            self.bus.unexport(element.path)

        self.bus.unexport(self.path)

        self.elements = {}

    async def connect(
        self, addr, iv_index=0
    ) -> Mapping[int, Dict[Tuple[int, int], Dict[str, Tuple[Any, int]]]]:
        """
        Connect to BlueZ. If a node doesn't exist yet, it gets created via
        Import() call.

        Returns current node configuration, see documentation for Attach()
        method in mesh-api.txt_.

        """
        try:
            configuration = await self.attach()
        except (ValueError, dbus_next.errors.DBusError) as ex:
            self.logger.error("Attach failed: %s, trying to import node", ex)
            await self.import_node(addr=addr, iv_index=iv_index)
            configuration = await self.attach()

            # after importing, explicitly import own device key to enable
            # communication with local Config Server
            await self.management_interface.import_remote_node(
                self.addr, len(self.ELEMENTS), self.dev_key
            )

        return configuration

    async def configure_node(self):
        for index, key in self.subnets_net_keys:
            await self.add_net_key(index, key)

        for index, bound, key in self.app_keys:
            await self.add_app_key(
                net_key_index=bound, app_key_index=index, app_key=key
            )

    async def add_net_key(self, net_key_index: int, net_key: NetworkKey) -> Any:
        """
        Imports an application key into daemon's keyring.

        :param net_key_index: Index of the network key
        :param net_key: Value of the new network key
        """
        client = self.elements[0][ConfigClient]

        return await client.add_net_key(
            self.addr,
            net_index=self.primary_net_key[0],
            net_key_index=net_key_index,
            net_key=net_key,
        )

    async def add_app_key(
        self, net_key_index: int, app_key_index: int, app_key: ApplicationKey
    ) -> "AppKeyStatus":
        """
        Imports an application key into daemon's keyring.

        :param net_key_index: Index of the network key the new application key is bound to
        :param app_key_index: Index of the new application key
        :param app_key: Value of the new application key
        """
        client = self.elements[0][ConfigClient]

        return await client.add_app_key(
            self.addr,
            net_index=self.primary_net_key[0],
            app_key_index=app_key_index,
            net_key_index=net_key_index,
            app_key=app_key,
        )

    async def bind_app_key(
        self, app_key_index: int, model: "Model"
    ) -> "ModelBindStatus":
        """
        See :py:func:`Model.bind` instead.
        """
        client = self.elements[0][ConfigClient]

        return await client.bind_app_key(
            self.addr,
            net_index=self.primary_net_key[0],
            element_address=self.addr + model.element.index,
            app_key_index=app_key_index,
            model=type(model),
        )

    async def subscribe_model(
        self, subscription_address: int, model: "Model"
    ) -> "ModelSubscriptionStatus":
        """
        See :py:func:`Model.subscribe` instead.
        """
        client = self.elements[0][ConfigClient]

        return await client.add_subscription(
            self.addr,
            net_index=self.primary_net_key[0],
            element_address=self.addr + model.element.index,
            subscription_address=subscription_address,
            model=type(model),
        )

    async def clear_subscriptions(self, model: "Model") -> "ModelSubscriptionStatus":
        """
        See :py:func:`Model.unsubscribe` instead.
        """
        client = self.elements[0][ConfigClient]

        return await client.clear_subscriptions(
            self.addr,
            net_index=self.primary_net_key[0],
            element_address=self.addr + model.element.index,
            model=type(model),
        )

    def get_model_instance(self, element: int, model: Type["Model"]) -> "Model":
        return self.elements[element][model]

    async def join(self):
        """
        Try to join a mesh network by broadcasting Unprovisioned Device Beacons,
        waiting for PB-ADV based provisioner.
        """
        self.logger.info("Join %s", self.uuid)
        await self.network_interface.join("/", self.uuid)

    async def cancel(self):
        """
        Cancel outstanding :py:func:`join` request.
        """
        self.logger.info("Cancel")
        await self.network_interface.cancel()

    async def leave(self):
        """
        Remove the node.
        """
        self.logger.info("Leave")
        await self.network_interface.leave(self.token)

    async def attach(self, token: Optional[int] = None):
        """
        Attach to existing node using a token.

        Returns current node configuration, see documentation for Attach()
        method in mesh-api.txt_.
        """
        token = token if token is not None else self.token

        if token is None:
            raise ValueError("No token")

        self.logger.info("Attach %x", self.token)
        path, configuration = await self.network_interface.attach("/", token)

        self.token = token

        introspection = await self.bus.introspect(MeshService.NAME, path)
        node_service = self.bus.get_proxy_object(MeshService.NAME, path, introspection)

        self.node_interface = NodeInterface(node_service)
        self.management_interface = ManagementInterface(node_service)

        self.addr = await self.node_interface.address()

        configuration = self._convert_config(configuration)

        for element, models_config in configuration.items():
            for model_id, model_config in models_config.items():
                self.elements[element].update_model_configuration(
                    model_id, model_config
                )

        self.logger.info(
            "Attached to node %s, address: %04x, configuration: %s",
            path,
            self.addr,
            configuration,
        )

        return configuration

    def _convert_config(self, configuration):
        ret = {}
        for model_major_list in configuration:
            element = model_major_list[0]
            ret[element] = {}
            for model_minor_list in model_major_list[1:]:
                for model_minor_config_list in model_minor_list:
                    model_config = model_minor_config_list[1]
                    model_id = model_minor_config_list[0]
                    ret[element][model_id] = dict()

                    for param, val in model_config.items():
                        if param == "Subscriptions":
                            ret[element][model_id][param] = [
                                addr.value for addr in val.value
                            ]
                        else:
                            ret[element][model_id][param] = val.value

        return ret

    async def import_node(
        self,
        dev_key: Optional[DeviceKey] = None,
        net_key: Optional[Tuple[int, NetworkKey]] = None,
        iv_index: int = 0,
        addr: int = None,
        flags: Optional[Mapping[str, Any]] = None,
    ) -> int:
        """
        Create a self-provisioned node.
        """
        addr = addr or self.addr

        net_index, net_key = net_key or self.primary_net_key
        dev_key = dev_key or self.dev_key

        self.logger.warning("Import %s", self.uuid)

        if flags:
            flags = {k: dbus_next.Variant("b", v) for k, v in flags.items()}

        self.token = await self.network_interface.import_node(
            "/", self.uuid, dev_key, net_key, net_index, flags or {}, iv_index, addr
        )

        return self.token


class LocationMixin:
    """
    Provides `location` property.
    """

    LOCATION = None  # type: int

    def __init__(self):
        assert self.LOCATION is not None

    @property
    def location(self) -> int:
        return self.LOCATION


class Element(LocationMixin):
    """
    Base class for elements.
    """

    MODELS = []  # type: List[Type["Model"]]

    def __init__(self, application: Application, index: int):
        super().__init__()

        self.logger = application.logger.getChild(
            "Element%d" % index
        )  # type: logging.Logger
        self.application = application
        self.index = index
        self.path = "%s/element%d" % (self.application.path, index)

        self._models = {
            model_class: model_class(self) for model_class in self.MODELS
        }  # type: Dict[Type["Model"], "Model"]

        # TODO: check that models don't have overlapping opcodes

    def _parse_message(self, message: bytes) -> Optional[ParsedMeshMessage]:
        try:
            return AccessMessage.parse(message)
        except construct.ConstructError as ex:
            self.logger.error("Cannot parse access message: %s", ex)

    def message_received(
        self, source: int, app_index: int, destination: Union[int, UUID], data: bytes
    ):
        """
        Called by :py:class:`bluetooth_mesh.interfaces.ElementInterface` when
        receiving a message encrypted with application key.

        The message is parsed using :py:class:`bluetooth_mesh.messages.AccessMessage`
        and (depending on the opcode) passed to relevant models'
        :func:`~bluetooth_mesh.models.Model.message_received`.

        """
        message = self._parse_message(data)

        if message is None:
            self.logger.error(
                "App message parse error: %04x [app_index %d, destination %04x]: %s",
                source,
                app_index,
                destination,
                data.hex(),
            )
            return

        for model in self._models.values():
            if message["opcode"] in model.OPCODES:
                model.message_received(source, app_index, destination, message)
                return

    def dev_key_message_received(
        self, source: int, remote: bool, net_index: int, data: bytes
    ):
        """
        Called by :py:class:`bluetooth_mesh.interfaces.ElementInterface` when
        receiving a message encrypted with device key.

        The message is parsed using :py:class:`bluetooth_mesh.messages.AccessMessage`
        and (depending on the opcode) passed to relevant models'
        :py:func:`bluetooth_mesh.models.Model.dev_key_message_received`.
        """

        message = self._parse_message(data)

        if message is None:
            self.logger.error(
                "Dev message parse error: %04x [net_index %d]: %s",
                source,
                net_index,
                data.hex(),
            )
            return

        for model in self._models.values():
            if message["opcode"] in model.OPCODES:
                model.dev_key_message_received(source, remote, net_index, message)
                return

    def update_model_configuration(
        self, model_id: int, configuration: Mapping[str, Any]
    ):
        """
        Called by :py:class:`bluetooth_mesh.interfaces.ElementInterface` when model
        configuration is updated via daemon's internal Config Server model.

        Passes the configuration to relevant model's
        :py:func:`bluetooth_mesh.models.Model.update_configuration`.
        """
        vendor_id = configuration.get("Vendor", None)

        for model in self._models.values():
            if model.MODEL_ID == (vendor_id, model_id):
                model.update_configuration(configuration)
                return

    def __getitem__(self, model_class: Type["Model"]) -> "Model":
        return self._models[model_class]

    @property
    def models(self) -> List[int]:
        """
        Used by :py:class:`bluetooth_mesh.interfaces.ApplicationInterface` to expose a
        list of supported SIG models via D-Bus.
        """
        return [
            model.MODEL_ID[1]
            for model in self._models.values()
            if model.MODEL_ID[0] is None
        ]

    @property
    def vendor_models(self) -> List[Tuple[int, int]]:
        """
        Used by :py:class:`bluetooth_mesh.interfaces.ApplicationInterface` to expose a
        list of supported vendor models via D-Bus.
        """
        return [
            model.MODEL_ID
            for model in self._models.values()
            if model.MODEL_ID[0] is not None
        ]

    def __repr__(self):
        def model_name(cls):
            if cls.MODEL_ID[0] is None:
                return "<%s %04x>" % (cls.__name__, cls.MODEL_ID[1])

            return "<%s %04x%04x>" % (cls.__name__, cls.MODEL_ID)

        return "<%s: models=%s>" % (
            type(self).__name__,
            ", ".join(model_name(i) for i in self.MODELS),
        )

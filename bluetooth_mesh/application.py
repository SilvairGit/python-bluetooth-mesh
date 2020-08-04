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
import socket
import struct
from enum import Enum
from functools import lru_cache
from os import urandom
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    Mapping,
    Optional,
    Tuple,
    Type,
    Union,
)
from uuid import UUID, uuid5

import construct
import dbus_next

from bluetooth_mesh.crypto import ApplicationKey, DeviceKey, NetworkKey
from bluetooth_mesh.interfaces import (
    AclInterface,
    ApplicationInterface,
    DBusInterface,
    DBusService,
    ElementInterface,
    ManagementInterface,
    MeshService,
    NetworkInterface,
    NodeInterface,
    ProvisionAgentInterface,
    ProvisionerInterface,
)
from bluetooth_mesh.messages import AccessMessage
from bluetooth_mesh.messages.fd import FdMessage, FdMessageType
from bluetooth_mesh.models import ConfigClient, ModelConfig
from bluetooth_mesh.tokenring import TokenRing
from bluetooth_mesh.utils import MeshError, ParsedMeshMessage

__all__ = [
    "Application",
    "Element",
]


class Capabilities(Enum):
    BLINK = "blink"
    BEEP = "beep"
    VIBRATE = "vibrate"
    OUT_NUMERIC = "out-numeric"
    OUT_ALPHA = "out-alpha"
    PUSH = "push"
    TWIST = "twist"
    IN_NUMERIC = "in-numeric"
    IN_ALPHA = "in-alpha"
    STATIC_OOB = "static-oob"
    PUBLIC_OOB = "public-oob"


class OOBInfo(Enum):
    OTHER = "other"
    URI = "uri"
    MACHINE_CODE_2D = "machine-code-2d"
    BAR_CODE = "bar-code"
    NFC = "nfc"
    NUMBER = "number"
    STRING = "string"
    ON_BOX = "on-box"
    IN_BOX = "in-box"
    ON_PAPER = "on-paper"
    IN_MANUAL = "in-manual"
    ON_DEVICE = "on-device"


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

    @staticmethod
    def get_namespace():
        with open("/etc/machine-id") as machine_id:
            return UUID(machine_id.read().strip())

    @property
    @lru_cache(maxsize=1)
    def uuid(self) -> UUID:
        namespace = self.get_namespace()
        return uuid5(namespace=namespace, name=self.path)


class TokenRingMixin(MachineUUIDMixin):
    """
    Provides a token ring handler based on application UUID.

    The handler is responsible for token ring persistence: the framework expects that tokens for nodes of
    a single application are stored & reused with subsequent launches.
    """

    TOKEN_RING = TokenRing

    @property
    @lru_cache(maxsize=1)
    def token_ring(self) -> TokenRing:
        return self.TOKEN_RING(uuid=self.uuid)


class NetworkKeyMixin:
    @property
    def primary_net_key(self) -> Tuple[int, NetworkKey]:
        """
        Index and key of the network that the application belongs to. Used when
        creating a new node, see :py:func:`Application.import_node`.
        """
        raise NotImplementedError("Getting primary network key should be overridden!")

    @property
    def subnet_keys(self) -> List[Tuple[int, NetworkKey]]:
        """
        Indexes and keys of the subnets.
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
    logger: logging.Logger

    def _name_owner_changed(self, name, old_owner, new_owner) -> None:
        if name != self.DBUS_SERVICE.NAME:
            return

        self.logger.error("Disconnected from %s (%s)", name, old_owner)
        self.dbus_disconnected(old_owner)

    async def dbus_connect(self) -> None:
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

    async def dbus_disconnect(self) -> None:
        self.dbus_interface.off_name_owner_changed(self._name_owner_changed)
        self.bus.disconnect()

    async def dbus_connected(self, owner) -> None:
        pass

    def dbus_disconnected(self, owner) -> Any:
        self.loop.stop()

    async def __aenter__(self) -> "DBusMixin":
        await self.dbus_connect()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> Any:
        return await self.dbus_disconnect()


class ProvisioningMixin:
    CAPABILITIES = []
    OOBINFO = []
    URI = ""

    def private_key(self) -> bytes:
        """
        This method is called during provisioning if the Provisioner
        has requested Out-Of-Band ECC key exchange. The Private key is
        returned to the Daemon, and the Public Key is delivered to the
        remote Provisioner using a method that does not involve the
        Bluetooth Mesh system. The Private Key returned must be 32
        octets in size.
        """
        raise NotImplementedError("Getting private key should be overridden!")

    def public_key(self) -> bytes:
        """
        This method is called during provisioning if the local device is
        the Provisioner, and is requestng Out-Of-Band ECC key exchange.
        The Public key is returned to the Daemon that is the matched
        pair of the Private key of the remote device. The Public Key
        returned must be 64 octets in size.
        """
        raise NotImplementedError("Getting public key should be overridden!")

    def display_string(self, value: str):
        """
        This method is called when the Daemon has something important for the Agent to Display,
        but does not require any additional input locally.
        :param value: String
        :return:
        """
        raise NotImplementedError("Display functions should be overridden!")

    def display_numeric(self, type: str, number: int):
        """
        This method is called when the Daemon has something important
        for the Agent to Display, but does not require any additional
        input locally.
        :param type: String
        :param value: Integer
        :return:
        """
        raise NotImplementedError("Display functions should be overridden!")

    def prompt_static(self, type: str) -> bytes:
        """
        This method is called when the Daemon requires a 16 octet byte
        array, as an Out-of-Band authentication.
        :param type:
        :return:
        """
        raise NotImplementedError("Prompt functions should be overridden!")

    def prompt_numeric(self, type: str) -> int:
        """
        This method is called when the Daemon requests the user to
        enter a decimal value between 1-99999999.
        :param type:
        :return:
        """
        raise NotImplementedError("Prompt functions should be overridden!")

    def cancel(self):
        """
        This method gets called by the daemon to cancel any existing
        Agent Requests. When called, any pending user input should be
        canceled, and any display requests removed.
        :return:
        """
        raise NotImplementedError("Cancel functions should be overridden!")

    @property
    def capabilities(self) -> List[Capabilities]:
        """
        Return list of available capabilities.
        """
        return self.CAPABILITIES

    @capabilities.setter
    def capabilities(self, cap: List[Capabilities]):
        self.CAPABILITIES = cap

    @property
    def oob_info(self) -> List[OOBInfo]:
        """
        Indicates availability of OOB data.
        """
        return self.OOBINFO

    @oob_info.setter
    def oob_info(self, info: List[OOBInfo]):
        self.OOBINFO = info

    @property
    def uri(self) -> str:
        return self.URI


class ProvisionerMixin:
    def scan_result(self, rssi: int, data: bytes, options: dict):
        """
        The method is called from the bluetooth-meshd daemon when a
        unique UUID has been seen during UnprovisionedScan() for
        unprovsioned devices.
        :param rssi: signed, normalized measurement of the signal strength of the recieved unprovisioned beacon
        :param data:
        :param options:
        :return:
        """
        raise NotImplementedError("Provisioner functions should be overridden!")

    def request_prov_data(self, count: int) -> Tuple[int, int]:
        """
        This method is implemented by a Provisioner capable application
        and is called when the remote device has been fully
        authenticated and confirmed.

        :param count: consecutive unicast addresses the remote device is requesting
        :return:
            :param unet_index: Subnet index of the net_key
            :param uunicast: Primary Unicast address of the new node
        """
        raise NotImplementedError("Provisioner functions should be overridden!")

    def add_node_complete(self, uuid: bytes, unicast: int, count: int):
        """
        This method is called when the node provisioning initiated
        by an AddNode() method call successfully completed.

        :param uuid: 16 byte remote device UUID
        :param unicast: primary address that has been assigned to the new node, and the address of it's config server
        :param count: number of unicast addresses assigned to the new node
        :return:
        """
        raise NotImplementedError("Provisioner functions should be overridden!")

    def add_node_failed(self, uuid: bytes, reason: str):
        """
        This method is called when the node provisioning initiated by
        AddNode() has failed. Depending on how far Provisioning
        proceeded before failing, some cleanup of cached data may be
        required.

        :param uuid: 16 byte remote device UUID
        :param reason: reason for provisioning failure
        :return:
        """
        raise NotImplementedError("Provisioner functions should be overridden!")


class Application(
    CompositionDataMixin,
    TokenRingMixin,
    MachineUUIDMixin,
    PathMixin,
    ApplicationKeyMixin,
    DeviceKeyMixin,
    NetworkKeyMixin,
    DBusMixin,
    ProvisioningMixin,
    ProvisionerMixin,
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
        self.provisioner_interface = ProvisionerInterface(self)

        self.elements = {}  # type: Dict[int, Element]

        self.network_interface = None
        self.node_interface = None
        self.management_interface = None
        self.addr = None

        self._join_complete = None

    async def _get_acl_interface(self):
        mesh_introspection = await self.bus.introspect(
            MeshService.NAME, MeshService.PATH
        )
        tcp_server = [
            node.name
            for node in mesh_introspection.nodes
            if node.name.startswith("tcpserver_")
        ]
        if not tcp_server:
            self.logger.warning("TCP interface missing")
            raise NotImplementedError

        path = "%s/%s" % (self.DBUS_SERVICE.PATH, tcp_server[0])
        introspection = await self.bus.introspect(MeshService.NAME, path)
        acl_service = self.bus.get_proxy_object(MeshService.NAME, path, introspection)

        return AclInterface(acl_service)

    async def acl_grant(self, uuid, dev_key, net_key):
        server = await self._get_acl_interface()
        token = await server.grant_access(uuid.bytes, dev_key.bytes, net_key.bytes)
        self.token_ring.acl(uuid, token)

    async def acl_revoke(self, uuid):
        server = await self._get_acl_interface()
        await server.revoke_access(self.token_ring.acl(uuid))
        self.token_ring.drop_acl(uuid)

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
        self.bus.export(self.path, self.provisioner_interface)

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
        self,
        addr: Union[int, Callable[[], int], Awaitable[int]],
        iv_index: int = 0,
        **kwargs,
    ) -> Mapping[int, Dict[Tuple[int, int], Dict[str, Tuple[Any, int]]]]:
        """
        Connect to BlueZ. If a node doesn't exist yet, it gets created via
        Import() call.

        Returns current node configuration, see documentation for Attach()
        method in mesh-api.txt_.

        One doesn't have to supply `addr` straight away - you may want to get your address only when
        Attach() call fails. In that case, you can pass a callback for `addr` - a callable or an awaitable
        that yields a mesh address.
        """
        try:
            configuration = await self.attach(**kwargs)
        except (ValueError, dbus_next.errors.DBusError) as ex:
            self.logger.error("Attach failed: %s, trying to import node", ex)
            if isinstance(addr, Awaitable):
                mesh_address = await addr
            elif isinstance(addr, Callable):
                mesh_address = addr()
            elif isinstance(addr, int):
                mesh_address = addr
            else:
                raise TypeError(
                    "Address not given as a value or an acceptable callback."
                )
            await self.import_node(addr=mesh_address, iv_index=iv_index)
            configuration = await self.attach(**kwargs)

        # after attaching, explicitly import own device key to enable
        # communication with local Config Server
        await self.management_interface.import_remote_node(
            self.addr, len(self.ELEMENTS), self.dev_key
        )

        return configuration

    async def add_net_key(self, net_key_index: int, net_key: NetworkKey) -> Any:
        """
        Imports a network key into daemon's keyring.

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

    async def delete_net_key(self, net_key_index: int) -> Any:
        """
        Removes a network key from daemon's keyring.

        :param net_key_index: Index of the network key
        :param net_key: Value of the new network key
        """
        client = self.elements[0][ConfigClient]

        return await client.delete_net_key(
            self.addr, net_index=self.primary_net_key[0], net_key_index=net_key_index,
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

    async def delete_app_key(
        self, net_key_index: int, app_key_index: int
    ) -> "AppKeyStatus":
        """
        Removes an application key from daemon's keyring.

        :param net_key_index: Index of the network key the deleted application key is bound to
        :param app_key_index: Index of the deleted application key
        """
        client = self.elements[0][ConfigClient]

        return await client.delete_app_key(
            self.addr,
            net_index=self.primary_net_key[0],
            app_key_index=app_key_index,
            net_key_index=net_key_index,
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

    async def unsubscribe_model(
        self, subscription_address: int, model: "Model"
    ) -> "ModelSubscriptionStatus":
        """
        See :py:func:`Model.unsubscribe` instead.
        """
        client = self.elements[0][ConfigClient]

        return await client.del_subscription(
            self.addr,
            net_index=self.primary_net_key[0],
            element_address=self.addr + model.element.index,
            subscription_address=subscription_address,
            model=type(model),
        )

    async def clear_subscriptions(self, model: "Model") -> "ModelSubscriptionStatus":
        """
        See :py:func:`Model.unsubscribe_all` instead.
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

        self._join_complete = asyncio.Future()
        await self.network_interface.join("/", self.uuid)
        return await self._join_complete

    async def create_network(self):
        """
        Create a new mesh network.
        """
        self.logger.info("Create %s", self.uuid)

        self._join_complete = asyncio.Future()
        await self.network_interface.create_network("/", self.uuid)
        return await self._join_complete

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
        await self.network_interface.leave(self.token_ring.token)

    async def attach(
        self, token: Optional[int] = None, *, socket_pair=False, socket_path: str = None
    ):
        """
        Attach to existing node using a token.

        Returns current node configuration, see documentation for Attach()
        method in mesh-api.txt_.
        """
        token = token if token is not None else self.token_ring.token

        if token is None:
            raise ValueError("No token")

        self.logger.info(
            "Attach %x (socket_pair=%s, socket_path=%s)",
            token,
            socket_pair,
            socket_path,
        )

        if socket_pair and socket_path:
            raise AssertionError("Use either socket_pair or socket_path")

        if socket_pair:
            path, configuration, sock = await self.network_interface.attach_fd(
                "/", token
            )
            self._add_reader(sock)
        elif socket_path:
            path, configuration, sock = await self.network_interface.attach_unix(
                "/", token, socket_path
            )
            self._add_reader(sock)
        else:
            path, configuration = await self.network_interface.attach("/", token)

        self.token_ring.token = token

        introspection = await self.bus.introspect(MeshService.NAME, path)
        node_service = self.bus.get_proxy_object(MeshService.NAME, path, introspection)

        self.node_interface = NodeInterface(node_service)
        self.management_interface = ManagementInterface(node_service)

        self.addr = await self.node_interface.address()

        for element, models_configs in configuration.items():
            for model_id, model_config in models_configs.items():
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

    def _add_reader(self, sock: Any) -> Any:
        HEADER = struct.Struct("<BHB20s")
        NETKEY_PARAMS = struct.Struct("<H?17x")
        APPKEY_PARAMS = struct.Struct("<HH16s")

        def _read_message() -> Any:
            while True:
                try:
                    line, *_ = sock.recvmsg(1024)
                except BlockingIOError:
                    break

                header, data = line[: HEADER.size], line[HEADER.size :]
                element, source, type, params = HEADER.unpack(header)

                if type == FdMessageType.NETKEY:
                    net_index, remote = NETKEY_PARAMS.unpack(params)

                    self.elements[element].dev_key_message_received(
                        source, remote, net_index, data
                    )
                elif type == FdMessageType.APPKEY:
                    app_index, destination, label = APPKEY_PARAMS.unpack(params)

                    self.elements[element].message_received(
                        source, app_index, destination, data
                    )

        self.loop.add_reader(sock, _read_message)

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

        self._join_complete = asyncio.Future()
        await self.network_interface.import_node(
            "/", self.uuid, dev_key, net_key, net_index, flags or {}, iv_index, addr
        )
        return await self._join_complete

    def join_complete(self, token: int):
        try:
            self.token_ring.token = token
            self._join_complete.set_result(self.token_ring.token)
        except Exception as ex:
            self._join_complete.set_exception(ex)
            raise dbus_next.errors.DBusError(
                "org.bluez.mesh.Application1", str(ex)
            ) from None

    def join_failed(self, reason: str):
        self._join_complete.set_exception(MeshError(reason))


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

        for opcode in sum((list(model.OPCODES) for model in self.MODELS), []):
            models = [model for model in self.MODELS if opcode in model.OPCODES]

            assert len(models) == 1, (
                "Element #%d declares models %r with overlapping opcode %r"
                % (index, models, opcode)
            )

        self._models = {
            model_class: model_class(self) for model_class in self.MODELS
        }  # type: Dict[Type["Model"], "Model"]

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
        self, model_id: Tuple[Optional[int], int], configuration: Mapping[str, Any]
    ):
        """
        Called by :py:class:`bluetooth_mesh.interfaces.ElementInterface` when model
        configuration is updated via daemon's internal Config Server model.

        Passes the configuration to relevant model's
        :py:func:`bluetooth_mesh.models.Model.update_configuration`.
        """
        for model in self._models.values():
            if model.MODEL_ID == model_id:
                model_config = ModelConfig(**configuration)
                model.update_configuration(model_config)
                return model_config

    def __getitem__(self, model_class: Type["Model"]) -> "Model":
        return self._models[model_class]

    @property
    def models(self) -> List[Tuple[int, bool, bool]]:
        """
        Used by :py:class:`bluetooth_mesh.interfaces.ApplicationInterface` to expose a
        list of supported SIG models via D-Bus.
        """
        return [
            (model.MODEL_ID[1], model.PUBLISH, model.SUBSCRIBE)
            for model in self._models.values()
            if model.MODEL_ID[0] is None
        ]

    @property
    def vendor_models(self) -> List[Tuple[Tuple[int, int], bool, bool]]:
        """
        Used by :py:class:`bluetooth_mesh.interfaces.ApplicationInterface` to expose a
        list of supported vendor models via D-Bus.
        """
        return [
            (model.MODEL_ID, model.PUBLISH, model.SUBSCRIBE)
            for model in self._models.values()
            if model.MODEL_ID[0] is not None
        ]

    def __repr__(self):
        def model_name(cls):
            if cls.MODEL_ID[0] is None:
                return "<%s %04x>" % (cls.__name__, cls.MODEL_ID[1])

            return "<%s %04x%04x>" % (cls.__name__, *cls.MODEL_ID)

        return "<%s: models=%s>" % (
            type(self).__name__,
            ", ".join(model_name(i) for i in self.MODELS),
        )

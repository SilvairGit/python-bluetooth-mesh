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
This module implements D-Bus interfaces that need to be exposed by an
application using BlueZ mesh stack, described in detail in mesh-api.txt_.

They are not meant to be used directly. See :py:mod:`bluetooth_mesh.application` instead.

.. _mesh-api.txt: https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/doc/mesh-api.txt
"""
# pylint: disable=R0201,W0613,W0622

import asyncio
import logging
import os
import socket
from collections import defaultdict
from contextlib import suppress
from datetime import timedelta
from enum import Enum
from typing import Any, Dict, Mapping, Optional, Sequence, Tuple
from uuid import UUID

from dbus_next import DBusError, Variant
from dbus_next.message import MessageFlag
from dbus_next.service import PropertyAccess, ServiceInterface, dbus_property, method

from bluetooth_mesh.crypto import ApplicationKey, DeviceKey, NetworkKey
from bluetooth_mesh.utils import Signal


class DBusService:
    NAME = "org.freedesktop.DBus"
    PATH = "/org/freedesktop/DBus"


class DBusInterface:
    def __init__(self, dbus_service):
        self._interface = dbus_service.get_interface("org.freedesktop.DBus")

    async def get_name_owner(self, name):
        return await self._interface.call_get_name_owner(name)

    def on_name_owner_changed(self, callback):
        self._interface.on_name_owner_changed(callback)

    def off_name_owner_changed(self, callback):
        self._interface.off_name_owner_changed(callback)

    def on_name_lost(self, callback):
        self._interface.on_name_lost(callback)

    def off_name_lost(self, callback):
        self._interface.off_name_lost(callback)

    async def get_service(self, service):
        owner = asyncio.Future()

        def name_owner_changed(name, old_owner, new_owner):
            if name != service.NAME:
                return

            if not new_owner:
                return

            owner.set_result(new_owner)

        try:
            self.on_name_owner_changed(name_owner_changed)
            return await self.get_name_owner(service.NAME)
        except DBusError as ex:
            return await owner
        finally:
            self.off_name_owner_changed(name_owner_changed)


class MeshService:
    NAME = "org.bluez.mesh"
    PATH = "/org/bluez/mesh"


def extract_model_config(configuration):
    vendor_id = None
    model_conf_dict = {}

    for key, variant in configuration.items():
        if key == "Vendor":
            vendor_id = variant.value
            continue

        if key == "Bindings":
            model_conf_dict["bindings"] = variant.value
            continue

        if key == "PublicationPeriod":
            model_conf_dict["publication_period"] = timedelta(
                milliseconds=variant.value
            )
            continue

        if key == "Subscriptions":
            subs = []

            for addr in variant.value:
                if addr.signature == "q":
                    subs.append(addr.value)

                elif addr.signature == "ay":
                    subs.append(UUID(bytes=addr.value))

            model_conf_dict["subscriptions"] = set(subs)

    return vendor_id, model_conf_dict


class ElementInterface(ServiceInterface):
    def __init__(self, element):
        self.element = element
        super().__init__(name="org.bluez.mesh.Element1")

    @dbus_property(name="Models", access=PropertyAccess.READ)
    def get_models(self) -> "a(qa{sv})":
        models = []

        for model_id, publish, subscribe in self.element.models:
            models.append(
                [
                    model_id,
                    {
                        "Publish": Variant("b", publish),
                        "Subscribe": Variant("b", subscribe),
                    },
                ]
            )

        return models

    @dbus_property(name="VendorModels", access=PropertyAccess.READ)
    def get_vendor_models(self) -> "a(qqa{sv})":
        models = []

        for model_id, publish, subscribe in self.element.vendor_models:
            models.append(
                [
                    *model_id,
                    {
                        "Publish": Variant("b", publish),
                        "Subscribe": Variant("b", subscribe),
                    },
                ]
            )

        return models

    @method(name="MessageReceived")
    def message_received(
        self, source: "q", key_index: "q", destination: "v", data: "ay"
    ):
        if destination.signature == "q":
            destination = destination.value
        elif destination.signature == "ay":
            destination = UUID(destination.value)

        self.element.message_received(source, key_index, destination, data)

    @method(name="DevKeyMessageReceived")
    def dev_key_message_received(
        self, source: "q", remote: "b", net_index: "q", data: "ay"
    ):
        self.element.dev_key_message_received(source, remote, net_index, data)

    @method(name="UpdateModelConfiguration")
    def update_model_configuration(self, model_id: "q", configuration: "a{sv}"):
        vendor_id, model_config = extract_model_config(configuration)
        self.element.update_model_configuration((vendor_id, model_id), model_config)

    @dbus_property(name="Index", access=PropertyAccess.READ)
    def get_index(self) -> "y":
        return self.element.index

    @dbus_property(name="Location", access=PropertyAccess.READ)
    def get_location(self) -> "q":
        return self.element.location


class ProvisionAgentInterface(ServiceInterface):
    def __init__(self, application):
        self.application = application
        self.logger = logging.getLogger("ProvisionAgentInterface")
        super().__init__(name="org.bluez.mesh.ProvisionAgent1")

    @method(name="PrivateKey")
    def private_key(self) -> "ay":
        return self.application.private_key()

    @method(name="PublicKey")
    def public_key(self) -> "ay":
        return self.application.public_key()

    @method(name="DisplayString")
    def display_string(self, value: "s"):
        self.application.display_string(value)

    @method(name="DisplayNumeric")
    def display_numeric(self, type: "s", number: "u"):
        self.application.display_numeric(type, number)

    @method(name="PromptNumeric")
    def prompt_numeric(self, type: "s") -> "u":
        return self.application.prompt_numeric(type)

    @method(name="PromptStatic")
    def prompt_static(self, type: "s") -> "ay":
        return self.application.prompt_static(type)

    @method(name="Cancel")
    def cancel(self):
        pass

    @dbus_property(name="Capabilities", access=PropertyAccess.READ)
    def get_capabilities(self) -> "as":
        return [cap.value for cap in self.application.capabilities]

    @dbus_property(name="OutOfBandInfo", access=PropertyAccess.READ)
    def out_of_band_info(self) -> "as":
        return [oob.value for oob in self.application.oob_info]

    @dbus_property(name="URI", access=PropertyAccess.READ)
    def uri(self) -> "s":
        return self.application.uri


class ProvisionerInterface(ServiceInterface):
    def __init__(self, application):
        self.application = application
        self.logger = logging.getLogger("ProvisionerInterface")
        super().__init__(name="org.bluez.mesh.Provisioner1")

    @method(name="ScanResult")
    def scan_result(self, rssi: "n", data: "ay", options: "a{sv}"):
        self.application.scan_result(rssi, data, options)

    @method(name="RequestProvData")
    def request_prov_data(self, count: "y") -> "qq":
        return self.application.request_prov_data(count)

    @method(name="AddNodeComplete")
    def add_node_complete(self, uuid: "ay", unicast: "q", count: "y"):
        self.application.add_node_complete(uuid=uuid, unicast=unicast, count=count)

    @method(name="AddNodeFailed")
    def add_node_failed(self, uuid: "ay", reason: "s"):
        self.application.add_node_failed(uuid=uuid, reason=reason)


class _ApplicationInterface(ServiceInterface):
    def __init__(self, application):
        self.application = application
        self.logger = logging.getLogger("ApplicationInterface")
        super().__init__(name="org.bluez.mesh.Application1")

    @method(name="JoinComplete")
    async def join_complete(self, token: "t"):
        self.application.join_complete(token)

    @method(name="JoinFailed")
    async def join_failed(self, reason: "s"):
        self.application.join_failed(reason)

    @dbus_property(name="CompanyID", access=PropertyAccess.READ)
    def get_company_id(self) -> "q":
        return self.application.company_id

    @dbus_property(name="ProductID", access=PropertyAccess.READ)
    def get_product_id(self) -> "q":
        return self.application.product_id

    @dbus_property(name="VersionID", access=PropertyAccess.READ)
    def get_version_id(self) -> "q":
        return self.application.version_id


class _ApplicationInterfaceCRPL(_ApplicationInterface):
    @dbus_property(name="CRPL", access=PropertyAccess.READ)
    def get_crpl(self) -> "q":
        return self.application.crpl


def ApplicationInterface(application):
    if application.crpl is not None:
        return _ApplicationInterfaceCRPL(application)
    else:
        return _ApplicationInterface(application)


class NetworkInterface:
    def __init__(self, mesh_service):
        self._interface = mesh_service.get_interface("org.bluez.mesh.Network1")

    def _extract_model_config(self, configuration):
        configuration_dict = defaultdict(dict)

        for element, element_conf in configuration:
            for model_id, model_conf in element_conf:
                vendor_id, model_conf_dict = extract_model_config(model_conf)

                configuration_dict[element][(vendor_id, model_id)] = model_conf_dict

        return configuration_dict

    async def join(self, app_defined_root: str, uuid: UUID) -> None:
        await self._interface.call_join(app_defined_root, uuid.bytes)

    async def cancel(self) -> None:
        await self._interface.call_cancel()

    async def attach(
        self, app_defined_root: str, token: int
    ) -> Tuple[str, Dict[int, Dict[Tuple[Optional[int], int], Mapping[str, Any]]]]:
        path, configuration = await self._interface.call_attach(app_defined_root, token)

        return path, self._extract_model_config(configuration)

    async def attach_fd(
        self, app_defined_root: str, token: int
    ) -> Tuple[
        str,
        Dict[int, Dict[Tuple[Optional[int], int], Mapping[str, Any]]],
        socket.socket,
    ]:
        path, configuration, fd = await self._interface.call_attach_fd(
            app_defined_root, token
        )

        sock = socket.fromfd(fd, socket.AF_UNIX, socket.SOCK_DGRAM)
        sock.setblocking(False)

        return path, self._extract_model_config(configuration), sock

    async def attach_unix(
        self, app_defined_root: str, token: int, socket_path: str
    ) -> Tuple[
        str,
        Dict[int, Dict[Tuple[Optional[int], int], Mapping[str, Any]]],
        socket.socket,
    ]:
        with suppress(FileNotFoundError):
            os.unlink(socket_path)

        sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM, 0)
        sock.setblocking(False)
        sock.bind(socket_path)

        path, configuration = await self._interface.call_attach_unix(
            app_defined_root, token, socket_path
        )

        return path, self._extract_model_config(configuration), sock

    async def leave(self, token: int) -> None:
        await self._interface.call_leave(token)

    async def create_network(self, app_root: str, uuid: UUID) -> None:
        return await self._interface.call_create_network(app_root, uuid.bytes)

    async def import_node(
        self,
        app_root: str,
        uuid: UUID,
        dev_key: DeviceKey,
        net_key: NetworkKey,
        net_index: int,
        flags: Mapping[str, Any],
        iv_index: int,
        unicast: int,
    ) -> None:

        await self._interface.call_import(
            app_root,
            uuid.bytes,
            dev_key.bytes,
            net_key.bytes,
            net_index,
            flags,
            iv_index,
            unicast,
        )


class AclInterface:
    def __init__(self, mesh_service):
        self._interface = mesh_service.get_interface(
            "org.bluez.mesh.AccessControlList1"
        )

    async def grant_access(
        self, uuid: UUID, dev_key: DeviceKey, net_key: NetworkKey
    ) -> int:
        return await self._interface.call_grant_access(uuid, dev_key, net_key)

    async def revoke_access(self, token: int):
        return await self._interface.call_revoke_access(token)


class IvState(Enum):
    INIT = "init"
    NORMAL = "normal"
    UPDATING = "updating"
    NORMAL_HOLD = "hold"


class NodeInterface:
    def __init__(self, node_service):
        self._interface = node_service.get_interface("org.bluez.mesh.Node1")
        self._properties = node_service.get_interface("org.freedesktop.DBus.Properties")
        self._properties.on_properties_changed(self._on_properties_changed)

    def _on_properties_changed(
        self, interface: str, changed: Mapping[str, Any], invalidated: Sequence[str]
    ):
        if interface != "org.bluez.mesh.Node1":
            return

        for name, variant in changed.items():
            val = variant.value

            if name == "IvIndex":
                sig = self.iv_index.signal
            elif name == "IvUpdate":
                sig = self.iv_update.signal
            elif name == "IvState":
                sig = self.iv_state.signal
                val = IvState(variant.value)
            else:
                sig = None

            if sig:
                asyncio.ensure_future(sig.emit(val))

    async def send(
        self, element_path: str, destination: int, key_index: int, data: bytes
    ) -> None:
        await self._interface.call_send(
            element_path,
            destination,
            key_index,
            data,
            flags=MessageFlag.NO_REPLY_EXPECTED,
        )

    async def dev_key_send(
        self,
        element_path: str,
        destination: int,
        remote: bool,
        net_index: int,
        data: bytes,
    ) -> None:
        await self._interface.call_dev_key_send(
            element_path,
            destination,
            remote,
            net_index,
            data,
            flags=MessageFlag.NO_REPLY_EXPECTED,
        )

    async def add_net_key(
        self,
        element_path: str,
        destination: int,
        subnet_index: int,
        net_index: int,
        update: bool,
    ) -> None:
        await self._interface.call_add_net_key(
            element_path, destination, subnet_index, net_index, update
        )

    async def add_app_key(
        self,
        element_path: str,
        destination: int,
        app_index: int,
        net_index: int,
        update: bool,
    ) -> None:
        await self._interface.call_add_app_key(
            element_path, destination, app_index, net_index, update
        )

    async def publish(self, element_path: str, model: int, data: bytes) -> None:
        await self._interface.call_publish(element_path, model, data)

    async def vendor_publish(
        self, element_path: str, vendor: int, model_id: int, data: bytes
    ):
        await self._interface.call_vendor_publish(element_path, vendor, model_id, data)

    async def update_sequence_number(self, seq_nr: int) -> int:
        updated_seq_nr = await self._interface.call_update_sequence_number(seq_nr)
        if updated_seq_nr != seq_nr:
            raise ValueError("Cannot update sequence number")
        return updated_seq_nr

    async def features(self) -> Mapping[str, bool]:
        return await self._interface.get_features()

    async def beacon(self) -> bool:
        return await self._interface.get_beacon()

    async def iv_update(self) -> bool:
        return await self._interface.get_iv_update()

    iv_update.signal = Signal()

    async def iv_index(self) -> int:
        return await self._interface.get_iv_index()

    iv_index.signal = Signal()

    async def iv_state(self) -> IvState:
        state = await self._interface.get_iv_state()
        return IvState(state)

    iv_state.signal = Signal()

    async def seconds_since_last_heard(self) -> int:
        return await self._interface.get_seconds_since_last_heard()

    async def address(self) -> int:
        return (await self._interface.get_addresses())[0]

    async def sequence_number(self) -> int:
        return await self._interface.get_sequence_number()


class ManagementInterface:
    def __init__(self, node_service):
        self._interface = node_service.get_interface("org.bluez.mesh.Management1")

    async def unprovisioned_scan(self, **kwargs) -> None:
        options = dict(Seconds=Variant("q", kwargs.get("seconds", 0)))
        await self._interface.call_unprovisioned_scan(options)

    async def unprovisioned_scan_cancel(self) -> None:
        await self._interface.call_unprovisioned_scan_cancel()

    async def add_node(self, uuid: UUID, **kwargs) -> None:
        options = dict(
            # TODO: populate with options when defined
        )
        await self._interface.call_add_node(uuid.bytes, options)

    async def create_subnet(self, net_index: int) -> None:
        await self._interface.call_create_subnet(net_index)

    async def import_subnet(self, net_index: int, net_key: NetworkKey) -> None:
        await self._interface.call_import_subnet(net_index, net_key.bytes)

    async def update_subnet(self, net_index: int) -> None:
        await self._interface.call_update_subnet(net_index)

    async def delete_subnet(self, net_index: int) -> None:
        await self._interface.call_delete_subnet(net_index)

    async def set_key_phase(self, net_index: int, phase: int) -> None:
        await self._interface.call_set_key_phase(net_index, phase)

    async def create_app_key(self, net_index: int, app_index: int) -> None:
        await self._interface.call_create_app_key(net_index, app_index)

    async def import_app_key(
        self, net_index: int, app_index: int, app_key: ApplicationKey
    ) -> None:
        await self._interface.call_import_app_key(net_index, app_index, app_key.bytes)

    async def update_app_key(self, app_index: int) -> None:
        await self._interface.call_update_app_key(app_index)

    async def complete_app_key_update(self, app_index: int) -> None:
        await self._interface.call_comlete_app_key_update(app_index)

    async def delete_app_key(self, app_index: int) -> None:
        await self._interface.call_delete_app_key(app_index)

    async def import_remote_node(
        self, primary: int, count: int, device_key: DeviceKey
    ) -> None:
        await self._interface.call_import_remote_node(primary, count, device_key.bytes)

    async def delete_remote_node(self, primary: int, count: int) -> None:
        await self._interface.call_delete_remote_node(primary, count)


class TCPServerService:
    NAME = "org.bluez.mesh"

    def __init__(self, port):
        self.PATH = f"/org/bluez/mesh/tcpserver_{port}"


class AccessControlListInterface:
    def __init__(self, tcpserver_service):
        self._interface = tcpserver_service.get_interface(
            "org.bluez.mesh.AccessControlList1"
        )

    async def grant_access(
        self, uuid: UUID, dev_key: DeviceKey, net_key: NetworkKey
    ) -> int:
        return await self._interface.call_grant_access(
            uuid.bytes, dev_key.bytes, net_key.bytes
        )

    async def revoke_access(self, token: int) -> None:
        await self._interface.call_revoke_access(token)


class TCPConnectionService:
    NAME = "org.bluez.mesh"

    def __init__(self, tcpserver_service: TCPServerService, identity: str):
        self.PATH = f"{tcpserver_service.PATH}/{identity}"


class ConnectionStatInterface:
    def __init__(self, tcpconnection_service):
        self._interface = tcpconnection_service.get_interface(
            "org.bluez.mesh.ConnectionStat1"
        )

    async def connected(self) -> bool:
        return self._interface.connected

    async def last_error(self) -> str:
        return self._interface.last_error

    async def transmitted_msg_count(self) -> int:
        return self._interface.transmitted_msg_count

    async def received_msg_count(self) -> int:
        return self._interface.received_msg_count

    async def last_transmitted_msg_timestamp(self) -> int:
        return self._interface.last_transmitted_msg_timestamp

    async def last_received_msg_timestamp(self) -> int:
        return self._interface.last_received_msg_timestamp

import logging
from functools import lru_cache
from uuid import UUID

import dbus_next.errors
import dbus_next.signature
import pytest

from bluetooth_mesh.application import Application, Element
from bluetooth_mesh.crypto import NetworkKey

pytestmark = [pytest.mark.asyncio]


class Node:
    def __init__(self, path, token, address):
        self.path = path
        self.configuration = []
        self.address = address
        self.token = token


@pytest.fixture
def node():
    return Node("/org/bluez/mesh/node3342c6c574ed4145888ce1d978a1f145", 0x4321, 0x100)


@pytest.fixture
def dbus(monkeypatch, node, application):
    logger = logging.getLogger("dbus")

    class MockInterface:
        def __init__(self, proxy_object, interface_name):
            self.proxy_object = proxy_object
            self.interface_name = interface_name

    class MockDbusInterface(MockInterface):
        def on_name_owner_changed(self, callback):
            pass

        def off_name_owner_changed(self, callback):
            pass

        async def call_get_name_owner(self, service_name):
            pass

    class MockNodeInterface(MockInterface):
        NODE = node

        async def get_addresses(self):
            return [self.NODE.address]

    class MockNetworkInterface(MockInterface):
        NODE = node

        async def call_attach(self, app_root, token):
            if self.NODE is None:
                raise dbus_next.errors.DBusError(
                    "org.bluez.mesh.Failure", "Node doesn't exist"
                )

            if self.NODE.token != token:
                raise dbus_next.errors.DBusError(
                    "org.bluez.mesh.Failure", "Invalid token"
                )

            return self.NODE.path, self.NODE.configuration

        async def call_import(
            self, app_root, uuid, dev_key, net_key, net_index, flags, iv_index, unicast
        ):
            path = f"/org/bluez/mesh/node{uuid.hex()}"

            if MockMessageBus.SERVICE_OBJECTS.get(("org.bluez.mesh", path)):
                raise dbus_next.errors.DBusError(
                    "org.bluez.mesh.Failure", "Node exists"
                )

            MockMessageBus.SERVICE_OBJECTS[
                ("org.bluez.mesh", path)
            ] = MockNodeProxyObject
            MockNodeInterface.NODE = MockNetworkInterface.NODE = Node(
                path, 0x5678, unicast
            )
            application.join_complete(0x5678)

    class MockManagementInterface(MockInterface):
        async def call_import_remote_node(self, primary, count, device_key):
            pass

    class MockPropertiesInterface(MockInterface):
        def on_properties_changed(self, callback):
            pass

    class MockProxyObject:
        INTERFACES = {}

        def __init__(self, service_name, object_path, introspection):
            self.service_name = service_name
            self.object_path = object_path
            self.introspection = introspection

        def get_interface(self, interface_name):
            logger.debug("get interface %s", interface_name)
            return self.INTERFACES[interface_name](self, interface_name)

    class MockDbusProxyObject(MockProxyObject):
        INTERFACES = {"org.freedesktop.DBus": MockDbusInterface}

    class MockNetworkProxyObject(MockProxyObject):
        INTERFACES = {"org.bluez.mesh.Network1": MockNetworkInterface}

    class MockNodeProxyObject(MockProxyObject):
        INTERFACES = {
            "org.freedesktop.DBus.Properties": MockPropertiesInterface,
            "org.bluez.mesh.Node1": MockNodeInterface,
            "org.bluez.mesh.Management1": MockManagementInterface,
        }

    class MockMessageBus:
        SERVICE_OBJECTS = {
            ("org.freedesktop.DBus", "/org/freedesktop/DBus"): MockDbusProxyObject,
            ("org.bluez.mesh", "/org/bluez/mesh"): MockNetworkProxyObject,
        }

        def __init__(self, bus_type):
            pass

        async def connect(self):
            return self

        def disconnect(self):
            pass

        async def introspect(self, service_name, object_path):
            pass

        def export(self, object_path, interface):
            pass

        def unexport(self, object_path):
            pass

        def get_proxy_object(self, service_name, object_path, introspection):
            logger.debug("get proxy object for %s:%s", service_name, object_path)

            return self.SERVICE_OBJECTS[(service_name, object_path)](
                service_name, object_path, introspection
            )

    if node:
        MockMessageBus.SERVICE_OBJECTS[
            ("org.bluez.mesh", node.path)
        ] = MockNodeProxyObject

    monkeypatch.setattr("dbus_next.aio.MessageBus", MockMessageBus)


@pytest.fixture
def application(event_loop):
    class MockElement(Element):
        LOCATION = 0

    class MockApplication(Application):
        ELEMENTS = {0: MockElement}

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.address = 0x200
            self.__uuid = UUID("3a1f9d4659b74b009dfd32cf9e758b7a")

        @property
        def uuid(self) -> UUID:
            return self.__uuid

        @uuid.setter
        def uuid(self, value):
            self.__uuid = value

        @property
        def primary_net_key(self):
            return 0, NetworkKey(bytes.fromhex("b37e0124a48a406bd2b092e82bea6aed"))

    return MockApplication(event_loop)


async def test_attach_bad_token(application, dbus, node):
    async with application:
        with pytest.raises(dbus_next.errors.DBusError, match="Invalid token"):
            await application.attach(node.token + 1)


async def test_attach_good_token(application, dbus, node):
    async with application:
        await application.attach(node.token)
        assert (
            application.node_interface._interface.proxy_object.object_path == node.path
        )


@pytest.mark.parametrize("node", [None])
class TestImportOnConnect:
    async def test_import(self, application, dbus):
        async with application:
            await application.connect()

            assert (
                application.node_interface._interface.proxy_object.object_path
                == f"/org/bluez/mesh/node{application.uuid.hex}"
            )
            assert application.address == 0x200

    async def test_missing_address(self, application, dbus):
        application.address = None

        async with application:
            with pytest.raises(
                AttributeError, match="Application didn't provide an address"
            ):
                await application.connect()


class TestAttachOnConnect:
    async def test_read_address_after_attach(self, application, dbus, node):
        application.address = None
        application.token_ring.token = node.token

        async with application:
            await application.connect()

            assert (
                application.node_interface._interface.proxy_object.object_path
                == node.path
            )
            assert application.address == node.address

            with pytest.raises(AttributeError, match="Can't set address"):
                application.address = 5

    async def test_import_new_on_attach_with_bad_token(self, application, dbus, node):
        application.token_ring.token = node.token + 1

        async with application:
            await application.connect()

            assert (
                application.node_interface._interface.proxy_object.object_path
                == f"/org/bluez/mesh/node{application.uuid.hex}"
            )
            assert application.address == 0x200

    async def test_import_existing_with_bad_token(self, application, dbus, node):
        application.token_ring.token = node.token + 1
        _, uuid = node.path.split("/node")
        application.uuid = UUID(uuid)

        async with application:
            with pytest.raises(dbus_next.errors.DBusError, match="Node exists"):
                await application.connect()

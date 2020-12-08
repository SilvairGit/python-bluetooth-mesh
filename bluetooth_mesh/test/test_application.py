import logging

import dbus_next.errors
import pytest

from bluetooth_mesh.application import Application
from bluetooth_mesh.crypto import NetworkKey

pytestmark = [pytest.mark.asyncio]


class Node:
    def __init__(self, path, configuration):
        self.path = path
        self.configuration = configuration


@pytest.fixture
def node():
    return Node("/org/bluez/mesh/node1234", {})


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

    class MockNetworkInterface(MockInterface):
        async def call_attach(self, app_root, token):
            if node is None:
                raise dbus_next.errors.DBusError(
                    "org.bluez.mesh.Failure", "Node doesn't exist"
                )

            return node.path, node.configuration

        async def call_import(
            self, app_root, uuid, dev_key, net_key, net_index, flags, iv_index, unicast
        ):
            nonlocal node
            node = Node("/org/bluez/mesh/node1234", {})
            application.join_complete(1234)

    class MockNodeInterface(MockInterface):
        async def get_addresses(self):
            return [1]

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
            ("org.bluez.mesh", "/org/bluez/mesh/node1234"): MockNodeProxyObject,
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

    monkeypatch.setattr("dbus_next.aio.MessageBus", MockMessageBus)


@pytest.fixture
def application(event_loop):
    class MockApplication(Application):
        @property
        def primary_net_key(self):
            return 0, NetworkKey(bytes.fromhex("b37e0124a48a406bd2b092e82bea6aed"))

    return MockApplication(event_loop)


async def test_attach(application, dbus):
    async with application:
        await application.attach()


@pytest.mark.parametrize("node", [None])
class TestConnect:
    async def test_addr_value(self, application, dbus):
        async with application:
            await application.connect(addr=1)

    async def test_addr_bad_value(self, application, dbus):
        async with application:
            with pytest.raises(TypeError, match="Address not given"):
                await application.connect(addr="foo")

    async def test_addr_callable(self, application, dbus):
        async with application:
            await application.connect(addr=lambda: 1)

    async def test_addr_bad_callable(self, application, dbus):
        async with application:
            with pytest.raises(TypeError, match="Address not given"):
                await application.connect(addr=lambda: "foo")

    async def test_addr_coroutine(self, application, dbus):
        async def addr():
            return 1

        async with application:
            await application.connect(addr=addr)

    async def test_addr_bad_coroutine(self, application, dbus):
        async def addr():
            return "foo"

        async with application:
            with pytest.raises(TypeError, match="Address not given"):
                await application.connect(addr=addr)

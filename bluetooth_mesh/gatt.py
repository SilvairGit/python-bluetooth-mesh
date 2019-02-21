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
import logging
import re
import uuid

from contextlib import suppress
from pydbus import SystemBus
from gi.repository import GLib, GObject


BLUEZ_SERVICE = 'org.bluez'

DBUS_OBJECT_MANAGER_IF = 'org.freedesktop.DBus.ObjectManager'
BLUEZ_ADAPTER_IF = 'org.bluez.Adapter1'
BLUEZ_DEVICE_IF = 'org.bluez.Device1'
BLUEZ_SERVICE_IF = 'org.bluez.GattService1'
BLUEZ_CHARACTERISTIC_IF = 'org.bluez.GattCharacteristic1'


class BusMixin:
    def __init__(self, path):
        super().__init__()

        self._bus = SystemBus()

        self._object = self._bus.get(BLUEZ_SERVICE, path)
        self._object.PropertiesChanged.connect(self._properties_changed)

        self._object_manager = self._bus.get(BLUEZ_SERVICE, '/')[DBUS_OBJECT_MANAGER_IF]
        self._object_manager.InterfacesAdded.connect(self._interfaces_added)

    @property
    def _path(self):
        return self._object._path

    def _interfaces_added(self, path, interfaces):
        pass

    def _properties_changed(self, path, changed, invalidated):
        pass


class Characteristic(BusMixin, GObject.Object):
    @property
    def UUID(self):
        with suppress(GLib.GError):
            return uuid.UUID(self._object.UUID)

    def _properties_changed(self, path, changed, invalidated):
        value = changed.get('Value')

        if value is not None:
            self.value_updated.emit(bytes(value))

    def read(self, offset=0):
        options = {}
        if offset is not None:
            options['offset'] = GLib.Variant.new_uint16(offset)

        return self._object.ReadValue(options)

    def write(self, value, offset=0):
        value = GLib.Variant.new_array(
            None,
            [GLib.Variant.new_byte(b) for b in value])

        options = {}
        if offset is not None:
            options['offset'] = GLib.Variant.new_uint16(offset)

        self._object.WriteValue(value, options)

    def notify(self, enabled=True):
        if enabled:
            self._object.StartNotify()
        else:
            self._object.StopNotify()

    @GObject.Signal(arg_types=(object, ))
    def value_updated(self, value):
        pass

    def __str__(self):
        return '<%s: %s>' % (type(self).__name__, self.UUID)


class Service(BusMixin, GObject.Object):
    def __init__(self, path):
        super().__init__(path)
        self.logger = logging.getLogger('gatt.service.%s' % self.UUID)

        self.characteristics = {}
        self._characteristics_path = re.compile(self._path + '/char[0-9abcdef]{4}$')

        self._characteristics_update()

    @property
    def UUID(self):
        with suppress(GLib.GError):
            return uuid.UUID(self._object.UUID)

    def _characteristic_add(self, path):
        characteristic = Characteristic(path)
        self.characteristics[characteristic.UUID] = characteristic

    def _characteristics_update(self):
        objects = self._object_manager.GetManagedObjects()

        for path, interfaces in objects.items():
            if BLUEZ_CHARACTERISTIC_IF not in interfaces:
                continue

            if not path.startswith(self._path):
                continue

            self._characteristic_add(path)

    def __str__(self):
        return '<%s: %s>' % (type(self).__name__, self.UUID)


class Device(BusMixin, GObject.Object):
    def __init__(self, path):
        super().__init__(path)
        self.logger = logging.getLogger('gatt.device.%s' % self.Address)

        self.services = {}
        self._services_path = re.compile(self._path + '/service[0-9abcdef]{4}$')

        if self.ServicesResolved:
            self._services_update()

    @property
    def Address(self):
        with suppress(GLib.GError):
            return self._object.Address

    @property
    def Connected(self):
        with suppress(GLib.GError):
            return self._object.Connected

    @property
    def ServiceData(self):
        service_data = {}

        with suppress(GLib.GError):
            for id in self._object.UUIDs:
                data = self._object.ServiceData.get(id, None)
                service_data[uuid.UUID(id)] = bytes(data) if data else None

        return service_data

    @property
    def ServicesResolved(self):
        with suppress(GLib.GError):
            return self._object.ServicesResolved

    @property
    def Name(self):
        with suppress(GLib.GError):
            return self._object.Name

    def Connect(self):
        self._object.Connect()

    def Disconnect(self):
        self.services = {}
        self._object.Disconnect()

    def _properties_changed(self, _, changed, invalidated):
        if 'Connected' in changed:
            self.connection_state.emit(bool(changed['Connected']))

        if 'ServicesResolved' in changed:
            if changed['ServicesResolved']:

                self._services_update()

    def _service_add(self, path):
        service = Service(path)
        self.services[service.UUID] = service

    def _services_update(self):
        objects = self._object_manager.GetManagedObjects()

        for path, interfaces in objects.items():
            if BLUEZ_SERVICE_IF not in interfaces:
                continue

            if not path.startswith(self._path):
                continue

            self._service_add(path)

        self.services_resolved.emit()

    def __str__(self):
        return '<%s: %s "%s">' % (type(self).__name__, self.Address, self.Name)

    @GObject.Signal(arg_types=(bool, ))
    def connection_state(self, connected):
        pass

    @GObject.Signal()
    def services_resolved(self):
        pass


class Adapter(BusMixin, GObject.Object):
    def __init__(self, adapter):
        super().__init__('/org/bluez/%s' % adapter)

        self.name = adapter
        self.logger = logging.getLogger('gatt.adapter.%s' % self.name)
        self.devices = {}

        self._devices_path = re.compile(self._path + '/dev((_[A-Z0-9]{2}){6})$')

    def __str__(self):
        return '<%s: %s>' % (type(self).__name__, self.Address)

    @property
    def Address(self):
        with suppress(GLib.GError):
            return self._object.Address

    def start_discovery(self, *services):
        self._devices_update()

        filter = dict(Transport=GLib.Variant.new_string('le'))

        if services:
            uuids = [str(i) for i in services]
            filter['UUIDs'] = GLib.Variant.new_array(
                None,
                [GLib.Variant.new_string(id) for id in uuids])

        self._object.SetDiscoveryFilter(filter)
        self._object.StartDiscovery()

    def stop_discovery(self):
        self._object.StopDiscovery()

    def remove_all_devices(self):
        for key, device in list(self.devices.items()):
            with suppress(GLib.GError):
                self._object.RemoveDevice(device._path)
            self.devices.pop(key)

    def _interfaces_added(self, path, interfaces):
        if BLUEZ_DEVICE_IF not in interfaces:
            return

        self._device_add(path)

    def _path_from_mac_address(self, mac_address):
        mac_address = mac_address.replace(':', '_')
        return '%s/dev_%s' % (self._path, mac_address)

    def _mac_address_from_path(self, path):
        match = self._devices_path.match(path)
        if match:
            mac_address = match.group(1)[1:]
            return mac_address.replace('_', ':')

    def _device_add(self, path):
        mac_address = self._mac_address_from_path(path)

        if not mac_address:
            return

        device = Device(path)
        self.devices[mac_address] = device

        self.device_discovered.emit(device)

    def _devices_update(self):
        objects = self._object_manager.GetManagedObjects()

        for path, interfaces in objects.items():
            if BLUEZ_DEVICE_IF not in interfaces:
                continue

            if not path.startswith(self._path):
                continue

            self._device_add(path)

    @GObject.Signal(arg_types=(object, ))
    def device_discovered(self, device):
        pass

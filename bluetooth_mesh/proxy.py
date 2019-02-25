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
import enum
import logging
import uuid
import time

import bitstring

from gi.repository import GObject


class ServiceId(enum.Enum):
    GENERIC_ACCESS = uuid.UUID('00001800-0000-1000-8000-00805f9b34fb')
    GENERIC_ATTRIBUTE = uuid.UUID('00001801-0000-1000-8000-00805f9b34fb')
    DEVICE_INFORMATION = uuid.UUID('0000180a-0000-1000-8000-00805f9b34fb')
    MESH_PROXY = uuid.UUID('00001828-0000-1000-8000-00805f9b34fb')
    MESH_PROVISIONING = uuid.UUID('00001827-0000-1000-8000-00805f9b34fb')


class CharacteristicId(enum.Enum):
    MESH_PROXY_WRITE = uuid.UUID('00002add-0000-1000-8000-00805f9b34fb')
    MESH_PROXY_NOTIFY = uuid.UUID('00002ade-0000-1000-8000-00805f9b34fb')


class ProxyPDUType(enum.Enum):
    NETWORK_PDU = 0x00
    MESH_BEACON = 0x01
    PROXY_CONFIGURATION = 0x02
    PROVISIONING_PDU = 0x03


class SarFlag(enum.Enum):
    COMPLETE = 0b00
    FIRST = 0b01
    CONTINUATION = 0b10
    LAST = 0b11


class SarProcessor:
    PDU_FORMAT = 'uint:2, uint:6, bytes'

    def __init__(self, packet_received, segment_send, segment_size=19):
        self._packet_received = packet_received
        self._segment_send = segment_send
        self._segment_size = segment_size

        self._reassembly = self.__reassembly()
        next(self._reassembly)

    def packet_send(self, packet, type=ProxyPDUType.NETWORK_PDU):
        for sar, segment in self.__segmentation(packet, type):
            segment = bitstring.pack(SarProcessor.PDU_FORMAT,
                                     sar.value, type.value, segment).bytes
            self._segment_send(segment)

    def segment_receive(self, segment):
        packet = self._reassembly.send(segment)
        if packet is not None:
            self._packet_received(*packet)

    def __reassembly(self):
        sar = None
        type = None
        packet = b''

        segment = yield

        while True:
            try:
                sar, type, segment = bitstring.BitString(segment).unpack(SarProcessor.PDU_FORMAT)
                sar = SarFlag(sar)
                type = ProxyPDUType(type)
            except ValueError:
                segment = yield
                continue

            if sar == SarFlag.COMPLETE:
                segment = yield segment, type
            elif sar == SarFlag.FIRST:
                packet = segment
                segment = yield
            elif sar == SarFlag.CONTINUATION:
                packet += segment
                segment = yield
            elif sar == SarFlag.LAST:
                packet += segment
                segment = yield packet, type
            else:
                segment = yield

    def __segmentation(self, packet, type):
        if len(packet) <= self._segment_size:
            yield SarFlag.COMPLETE, packet
            return

        yield SarFlag.FIRST, packet[:self._segment_size]
        packet = packet[self._segment_size:]

        while len(packet) > self._segment_size:
            yield SarFlag.CONTINUATION, packet[:self._segment_size]
            packet = packet[self._segment_size:]

        yield SarFlag.LAST, packet


class GattProxy(GObject.Object):
    def __init__(self, device):
        super().__init__()
        self.logger = logging.getLogger('gatt.proxy.%s' % device.Address)

        self._device = device

        proxy = device.services[ServiceId.MESH_PROXY.value]

        self._write = proxy.characteristics[CharacteristicId.MESH_PROXY_WRITE.value]

        self._notify = proxy.characteristics[CharacteristicId.MESH_PROXY_NOTIFY.value]
        self._notify.value_updated.connect(self._notify_value_updated)

        self._sar = SarProcessor(self._packet_received,
                                 self._write_write)

    def start(self):
        self._notify.notify(True)

    def packet_send(self, packet, type=ProxyPDUType.NETWORK_PDU):
        self._sar.packet_send(packet, type)

    def _notify_value_updated(self, _, value):
        self._sar.segment_receive(value)

    def _write_write(self, value):
        self._write.write(value)
        self.logger.info('Write %s', value.hex())
        time.sleep(0.1)

    def _packet_received(self, packet, type):
        if type == ProxyPDUType.MESH_BEACON:
            self.mesh_beacon_received.emit(packet)
        elif type == ProxyPDUType.NETWORK_PDU:
            self.network_pdu_received.emit(packet)
        elif type == ProxyPDUType.PROXY_CONFIGURATION:
            pass
        elif type == ProxyPDUType.PROVISIONING_PDU:
            pass
        else:
            raise KeyError("Unknown ProxyPDUType %d %s", type, packet.hex())

    @GObject.Signal(arg_types=(object, ))
    def network_pdu_received(self, packet):
        pass

    @GObject.Signal(arg_types=(object, ))
    def mesh_beacon_received(self, packet):
        pass

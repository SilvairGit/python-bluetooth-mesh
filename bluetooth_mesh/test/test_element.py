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
# pylint: disable=W0621

from unittest.mock import MagicMock

import pytest

from bluetooth_mesh import Element
from bluetooth_mesh.messages import AccessMessage
from bluetooth_mesh.messages.config import GATTNamespaceDescriptor
from bluetooth_mesh.messages.generic.onoff import GenericOnOffOpcode
from bluetooth_mesh.test.fixtures import *  # pylint: disable=W0614, W0401


class MockModel(MagicMock):
    MODEL_ID = (None, 0x1001)
    OPCODES = {GenericOnOffOpcode.GENERIC_ONOFF_STATUS}
    INSTANCES = []

    def __init__(self, *args, **kwargs):
        super().__init__(
            *[arg for arg in args if not isinstance(arg, Element)], **kwargs
        )
        MockModel.INSTANCES.append(self)


class MockVenforModel(MagicMock):
    MODEL_ID = (0x6666, 0x9999)
    OPCODES = {GenericOnOffOpcode.GENERIC_ONOFF_SET}
    INSTANCES = []

    def __init__(self, *args, **kwargs):
        super().__init__(
            *[arg for arg in args if not isinstance(arg, Element)], **kwargs
        )
        MockVenforModel.INSTANCES.append(self)


@pytest.fixture
def model_mocks():
    MockModel.INSTANCES = []
    MockVenforModel.INSTANCES = []
    return {MockModel, MockVenforModel}


@pytest.fixture
def element(model_mocks):
    class MockElement(Element):
        MODELS = model_mocks
        LOCATION = GATTNamespaceDescriptor.FORTY_SECOND

    mock_element = MockElement(MagicMock(), 0)
    return mock_element


def test_message_received(element, source, app_index, status_encoded):
    status_parsed = AccessMessage.parse(status_encoded)
    element.message_received(source, app_index, False, status_encoded)
    MockModel.INSTANCES[0].message_received.assert_called_once_with(
        source, app_index, False, status_parsed
    )


def test_other_opcode_message_received(element, source, app_index, get_encoded):
    element.message_received(source, app_index, False, get_encoded)
    MockModel.INSTANCES[0].message_received.assert_not_called()


def test_dev_message_received(element, source, net_index, status_encoded):
    status_parsed = AccessMessage.parse(status_encoded)
    element.dev_key_message_received(source, True, net_index, status_encoded)
    MockModel.INSTANCES[0].dev_key_message_received.assert_called_once_with(
        source, True, net_index, status_parsed
    )


def test_other_opcode_dev_message_received(element, source, net_index, get_encoded):
    element.dev_key_message_received(source, True, net_index, get_encoded)
    MockModel.INSTANCES[0].dev_key_message_received.assert_not_called()


def test_update_model_configuration(element):
    config = dict()
    model_config = element.update_model_configuration(
        (MockModel.MODEL_ID[0], MockModel.MODEL_ID[1]), config
    )
    MockModel.INSTANCES[0].update_configuration.assert_called_once_with(model_config)


def test_update_vendor_model_configuration(element):
    config = dict()
    model_config = element.update_model_configuration(
        (MockVenforModel.MODEL_ID[0], MockVenforModel.MODEL_ID[1]), config
    )
    MockVenforModel.INSTANCES[0].update_configuration.assert_called_once_with(
        model_config
    )

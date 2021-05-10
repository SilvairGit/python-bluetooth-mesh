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
# pylint: disable=redefined-outer-name, invalid-name
import asynctest
from asynctest import ANY, call, mock

from bluetooth_mesh import Element, LightLightnessClient
from bluetooth_mesh.messages import LightLightnessMessage, LightLightnessOpcode
from bluetooth_mesh.messages.config import GATTNamespaceDescriptor
from bluetooth_mesh.messages.generic import LightLightnessSetupMessage
from bluetooth_mesh.messages.generic.light import LightLightnessSetupOpcode
from bluetooth_mesh.test.fixtures import *  # pylint: disable=unused-wildcard-import, wildcard-import


class LLElementMock(Element):
    LOCATION = GATTNamespaceDescriptor.BOTTOM
    MODELS = [LightLightnessClient]


@pytest.fixture
def light_lightness_client(element_path) -> LightLightnessClient:
    element = LLElementMock(mock.MagicMock(), mock.MagicMock())
    element.path = element_path
    return LightLightnessClient(element)


@pytest.mark.asyncio
@asynctest.patch("asyncio.sleep", new=asynctest.CoroutineMock())
async def test_sending_set_lightness_range_repeated_6_times_with_intervals_by_default(
    light_lightness_client, destination, app_index
):
    light_lightness_client.repeat = asynctest.CoroutineMock()

    await light_lightness_client.set_lightness_range_unack(
        destination=destination, app_index=app_index, min_lightness=0, max_lightness=100
    )

    light_lightness_client.repeat.assert_awaited_once_with(
        ANY, retransmissions=6, send_interval=0.075
    )


@pytest.mark.asyncio
@asynctest.patch("asyncio.sleep", new=asynctest.CoroutineMock())
async def test_sending_set_lightness_repeated_6_times_with_intervals_by_default(
    light_lightness_client, destination, app_index
):
    light_lightness_client.repeat = asynctest.CoroutineMock()

    await light_lightness_client.set_lightness_unack(
        destination=destination, app_index=app_index, transition_time=0, lightness=100
    )

    light_lightness_client.repeat.assert_awaited_once_with(
        ANY, retransmissions=6, send_interval=0.075
    )


# pylint: disable=protected-access
@pytest.mark.asyncio
@asynctest.patch("asyncio.sleep", new=asynctest.CoroutineMock())
async def test_set_lightness_range_calls_node_interface_with_appropriate_arguments(
    light_lightness_client, destination, app_index, element_path
):
    light_lightness_client._node_interface.send = asynctest.CoroutineMock()

    await light_lightness_client.set_lightness_range_unack(
        destination=destination, app_index=app_index, min_lightness=0, max_lightness=100
    )

    data = LightLightnessSetupMessage.build(
        {
            "opcode": LightLightnessSetupOpcode.LIGHT_LIGHTNESS_SETUP_RANGE_SET_UNACKNOWLEDGED,
            "params": {
                "range_min": 0,
                "range_max": 100,
            },
        }
    )
    light_lightness_client._node_interface.send.assert_awaited_with(
        element_path, destination, app_index, data
    )


# pylint: disable=protected-access
@pytest.mark.asyncio
@asynctest.patch("asyncio.sleep", new=asynctest.CoroutineMock())
async def test_set_lightness_calls_node_interface_with_appropriate_arguments(
    light_lightness_client, destination, app_index, element_path
):
    light_lightness_client._node_interface.send = asynctest.CoroutineMock()

    await light_lightness_client.set_lightness_unack(
        destination=destination,
        app_index=app_index,
        transition_time=0,
        lightness=0,
        send_interval=0.05,
        retransmissions=6,
    )

    frames = [
        LightLightnessMessage.build(
            {
                "opcode": LightLightnessOpcode.LIGHT_LIGHTNESS_SET_UNACKNOWLEDGED,
                "params": dict(lightness=0, tid=0, transition_time=0, delay=d),
            }
        )
        for d in [0.50, 0.45, 0.40, 0.35, 0.30, 0.25]
    ]
    assert light_lightness_client._node_interface.send.await_args_list == [
        call(element_path, destination, app_index, frame) for frame in frames
    ]

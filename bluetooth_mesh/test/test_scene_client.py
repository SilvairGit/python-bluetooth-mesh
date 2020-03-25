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
# pylint: disable=W0621, C0103
from unittest import mock

import asynctest
from asynctest import ANY

from bluetooth_mesh import Element, SceneClient
from bluetooth_mesh.messages.config import GATTNamespaceDescriptor
from bluetooth_mesh.test.fixtures import *  # pylint: disable=W0614, W0401


class SceneElementMock(Element):
    LOCATION = GATTNamespaceDescriptor.BOTTOM
    MODELS = [SceneClient]


@pytest.fixture
def scene_client(element_path) -> SceneClient:
    element = SceneElementMock(mock.MagicMock(), mock.MagicMock())
    element.path = element_path
    return SceneClient(element)


@pytest.mark.asyncio
@asynctest.patch("asyncio.sleep", new=asynctest.CoroutineMock())
async def test_sending_scene_recall_repeated_6_times_with_intervals(
    scene_client, destination, app_index
):
    scene_client.repeat = asynctest.CoroutineMock()

    await scene_client.recall_scene_unack(
        destination=destination, app_index=app_index, scene_number=1, transition_time=0
    )

    scene_client.repeat.assert_awaited_once_with(
        ANY, retransmissions=6, send_interval=0.075
    )


# pylint: disable=W0212
@pytest.mark.asyncio
@asynctest.patch("asyncio.sleep", new=asynctest.CoroutineMock())
async def test_scene_recall_calls_node_interface_with_appropriate_arguments(
    scene_client, destination, app_index, element_path
):
    scene_client._node_interface.send = asynctest.CoroutineMock()

    await scene_client.recall_scene_unack(
        destination, app_index, scene_number=1, transition_time=0
    )

    data = b"\x82C\x01\x00\x00\x00\x18"
    scene_client._node_interface.send.assert_awaited_with(
        element_path, destination, app_index, data
    )


@pytest.mark.asyncio
@asynctest.patch("asyncio.sleep", new=asynctest.CoroutineMock())
@pytest.mark.parametrize(
    "number_of_scene_recalls, next_tid",
    [pytest.param(1, 0), pytest.param(255, 254), pytest.param(256, 0)],
)
async def test_scene_recall_increases_tid(
    scene_client, number_of_scene_recalls, next_tid
):
    scene_client.send_app = asynctest.CoroutineMock()

    for _ in range(number_of_scene_recalls):
        await scene_client.recall_scene_unack(
            ANY, ANY, scene_number=ANY, transition_time=ANY
        )

    scene_client.send_app.assert_awaited_with(
        ANY,
        app_index=ANY,
        opcode=ANY,
        params=dict(scene_number=ANY, tid=next_tid, transition_time=ANY, delay=ANY),
    )

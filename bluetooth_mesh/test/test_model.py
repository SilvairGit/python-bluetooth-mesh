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

import asyncio
from asyncio import Future
from functools import partial
from unittest.mock import MagicMock, call

import asynctest
import pytest

from bluetooth_mesh import Model
from bluetooth_mesh.interfaces import NodeInterface
from bluetooth_mesh.messages.generic.onoff import GenericOnOffOpcode
from bluetooth_mesh.test.fixtures import *  # pylint: disable=W0614, W0401


@pytest.fixture
def node_interface():
    return asynctest.MagicMock(NodeInterface)


@pytest.fixture
def element_mock(element_path, node_interface):
    element_mock = MagicMock()
    element_mock.application.node_interface = node_interface
    element_mock.path = element_path
    return element_mock


@pytest.fixture()
def model(element_mock):
    class MockModel(Model):
        MODEL_ID = (None, 0x1001)
        OPCODES = {GenericOnOffOpcode.GENERIC_ONOFF_STATUS}

    return MockModel(element_mock)


@pytest.mark.asyncio
async def test_single_expect(model, status_parsed, source, app_index):
    status = model.expect_app(source, app_index, False, status_parsed["opcode"], {})
    model.message_received(source, app_index, False, status_parsed)
    assert status_parsed == await status


@pytest.mark.asyncio
async def test_wildcard_expect(model, status_parsed, source, app_index):
    status = model.expect_app(
        source, app_index, False, status_parsed["opcode"], dict(present_onoff=...)
    )
    model.message_received(source, app_index, False, status_parsed)
    assert status_parsed == await status


@pytest.mark.asyncio
async def test_multiple_expect(model, status_parsed, source, app_index):
    status1 = model.expect_app(source, app_index, False, status_parsed["opcode"], {})
    status2 = model.expect_app(source, app_index, False, status_parsed["opcode"], {})
    model.message_received(source, app_index, False, status_parsed)
    assert status_parsed == await status1
    assert status_parsed == await status2


def test_app_single_repeatable_callback(model, status_parsed, source, app_index):
    listener_mock = MagicMock(return_value=False)
    model.app_message_callbacks[status_parsed["opcode"]].add(listener_mock)
    model.message_received(source, app_index, False, status_parsed)
    listener_mock.assert_called_once_with(source, app_index, False, status_parsed)

    listener_mock.reset_mock()
    model.message_received(source, app_index, False, status_parsed)
    listener_mock.assert_called_once_with(source, app_index, False, status_parsed)


def test_single_oneshot_callback(model, status_parsed, source, app_index):
    listener_mock = MagicMock(return_value=True)
    model.app_message_callbacks[status_parsed["opcode"]].add(listener_mock)
    model.message_received(source, app_index, False, status_parsed)
    listener_mock.assert_called_once_with(source, app_index, False, status_parsed)

    listener_mock.reset_mock()
    model.message_received(source, app_index, False, status_parsed)
    listener_mock.assert_not_called()


def test_multiple_callback(model, status_parsed, source, app_index):
    listener_mock_repeatable = MagicMock(return_value=False)
    listener_mock_oneshot = MagicMock(return_value=True)
    model.app_message_callbacks[status_parsed["opcode"]].add(listener_mock_repeatable)
    model.app_message_callbacks[status_parsed["opcode"]].add(listener_mock_oneshot)
    model.message_received(source, app_index, False, status_parsed)
    listener_mock_repeatable.assert_called_once_with(
        source, app_index, False, status_parsed
    )
    listener_mock_oneshot.assert_called_once_with(
        source, app_index, False, status_parsed
    )

    listener_mock_repeatable.reset_mock()
    listener_mock_oneshot.reset_mock()
    model.message_received(source, app_index, False, status_parsed)
    listener_mock_repeatable.assert_called_once_with(
        source, app_index, False, status_parsed
    )
    listener_mock_oneshot.assert_not_called()


@pytest.mark.asyncio
async def test_dev_single_expect(model, status_parsed, source, net_index):
    status = model.expect_dev(source, net_index, status_parsed["opcode"], {})
    model.dev_key_message_received(source, True, net_index, status_parsed)
    assert status_parsed == await status


@pytest.mark.asyncio
async def test_dev_wildcard_expect(model, status_parsed, source, net_index):
    status = model.expect_dev(
        source, net_index, status_parsed["opcode"], dict(present_onoff=...)
    )
    model.dev_key_message_received(source, True, net_index, status_parsed)
    assert status_parsed == await status


@pytest.mark.asyncio
async def test_dev_multiple_expect(model, status_parsed, source, net_index):
    status1 = model.expect_dev(source, net_index, status_parsed["opcode"], {})
    status2 = model.expect_dev(source, net_index, status_parsed["opcode"], {})
    model.dev_key_message_received(source, True, net_index, status_parsed)
    assert status_parsed == await status1
    assert status_parsed == await status2


def test_dev_single_repeatable_callback(model, status_parsed, source, net_index):
    listener_mock = MagicMock(return_value=False)
    model.dev_message_callbacks[status_parsed["opcode"]].add(listener_mock)
    model.dev_key_message_received(source, True, net_index, status_parsed)
    listener_mock.assert_called_once_with(source, net_index, status_parsed)

    listener_mock.reset_mock()
    model.dev_key_message_received(source, True, net_index, status_parsed)
    listener_mock.assert_called_once_with(source, net_index, status_parsed)


def test_dev_single_oneshot_callback(model, status_parsed, source, net_index):
    listener_mock = MagicMock(return_value=True)
    model.dev_message_callbacks[status_parsed["opcode"]].add(listener_mock)
    model.dev_key_message_received(source, True, net_index, status_parsed)
    listener_mock.assert_called_once_with(source, net_index, status_parsed)

    listener_mock.reset_mock()
    model.dev_key_message_received(source, True, net_index, status_parsed)
    listener_mock.assert_not_called()


def test_dev_multiple_callback(model, status_parsed, source, net_index):
    listener_mock_repeatable = MagicMock(return_value=False)
    listener_mock_oneshot = MagicMock(return_value=True)
    model.dev_message_callbacks[status_parsed["opcode"]].add(listener_mock_repeatable)
    model.dev_message_callbacks[status_parsed["opcode"]].add(listener_mock_oneshot)
    model.dev_key_message_received(source, True, net_index, status_parsed)
    listener_mock_repeatable.assert_called_once_with(source, net_index, status_parsed)
    listener_mock_oneshot.assert_called_once_with(source, net_index, status_parsed)

    listener_mock_oneshot.reset_mock()
    listener_mock_repeatable.reset_mock()
    model.dev_key_message_received(source, True, net_index, status_parsed)
    listener_mock_oneshot.assert_not_called()
    listener_mock_repeatable.assert_called_once_with(source, net_index, status_parsed)


@pytest.mark.asyncio
async def test_send_app(
    model, status_parsed, destination, app_index, element_path, node_interface
):
    await model.send_app(
        destination, app_index, status_parsed["opcode"], status_parsed["params"]
    )
    node_interface.send.assert_called_once_with(
        element_path, destination, app_index, b"\x82\x04\x00"
    )


@pytest.mark.asyncio
async def test_send_dev(
    model, status_parsed, destination, net_index, element_path, node_interface
):
    await model.send_dev(
        destination, net_index, status_parsed["opcode"], status_parsed["params"]
    )
    node_interface.dev_key_send.assert_called_once_with(
        element_path, destination, True, net_index, b"\x82\x04\x00"
    )


@pytest.mark.asyncio
async def test_repeat(
    model, status_parsed, destination, app_index, element_path, node_interface
):
    request = partial(
        model.send_app,
        destination,
        app_index,
        status_parsed["opcode"],
        status_parsed["params"],
    )
    await model.repeat(request, send_interval=0.0001)
    node_interface.send.assert_has_calls(
        [
            asynctest.call(element_path, destination, app_index, b"\x82\x04\x00")
            for _ in range(6)
        ]
    )
    assert node_interface.send.call_count == 6


@pytest.mark.asyncio
async def test_query(
    model, status_parsed, source, destination, app_index, element_path, node_interface
):
    request_future = Future()

    async def request():
        await model.send_app(
            destination, app_index, status_parsed["opcode"], status_parsed["params"]
        )
        request_future.set_result(None)

    status = model.expect_app(source, app_index, False, status_parsed["opcode"], {})
    query_status = asyncio.ensure_future(model.query(request, status))
    await request_future
    model.message_received(source, app_index, False, status_parsed)
    await query_status
    node_interface.send.assert_called_once_with(
        element_path, destination, app_index, b"\x82\x04\x00"
    )


@pytest.mark.asyncio
async def test_bulk_query(
    model, status_parsed, destination, app_index, element_path, node_interface
):
    async def request(future, dest):
        await model.send_app(
            dest, app_index, status_parsed["opcode"], status_parsed["params"]
        )
        future.set_result(None)

    destinations = [destination + i for i in range(10)]
    futures = {addr: Future() for addr in destinations}
    requests = {addr: partial(request, futures[addr], addr) for addr in destinations}
    statuses = {
        addr: model.expect_app(addr, app_index, False, status_parsed["opcode"], {})
        for addr in destinations
    }

    query_status = asyncio.ensure_future(
        model.bulk_query(requests, statuses, send_interval=0.01)
    )
    await asyncio.wait(futures.values())

    for addr in destinations:
        model.message_received(addr, app_index, False, status_parsed)

    await query_status
    node_interface.send.assert_has_calls(
        [call(element_path, addr, app_index, b"\x82\x04\x00") for addr in destinations]
    )
    assert node_interface.send.call_count == 10


@pytest.mark.asyncio
async def test_bulk_query_timeout(
    model, status_parsed, destination, app_index, element_path, node_interface
):
    async def request(dest):
        await model.send_app(
            dest, app_index, status_parsed["opcode"], status_parsed["params"]
        )

    async def callback(address, result, done, total):
        if address == 10:
            assert len(done) == 1
            assert result == {
                "opcode": GenericOnOffOpcode.GENERIC_ONOFF_STATUS,
                "params": {"present_onoff": 0},
            }
        elif address == 20:
            assert len(done) == 2
            assert isinstance(result, TimeoutError)

    requests = {
        10: partial(request, 10),
        20: partial(request, 20),
    }
    statuses = {
        10: model.expect_app(10, app_index, False, status_parsed["opcode"], {}),
        20: model.expect_app(20, app_index, False, status_parsed["opcode"], {}),
    }

    query_status = asyncio.ensure_future(
        model.bulk_query(
            requests,
            statuses,
            send_interval=0.001,
            progress_callback=callback,
            timeout=0.1,
        )
    )

    model.message_received(10, app_index, False, status_parsed)

    await query_status

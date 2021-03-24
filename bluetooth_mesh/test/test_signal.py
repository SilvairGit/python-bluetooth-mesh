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
from asyncio import AbstractEventLoop, Task, wait_for
from functools import partial, wraps
from typing import Any, Optional, Callable, Awaitable

import pytest
from asynctest import CoroutineMock, MagicMock, call

from bluetooth_mesh.utils import Signal


@pytest.mark.asyncio
async def test_signal():
    cb1 = CoroutineMock()
    cb2 = CoroutineMock()

    ts = Signal()
    ts.connect(cb1)
    ts.connect(cb2)

    await ts.emit("test msg")
    cb1.assert_called_with("test msg")
    cb2.assert_called_with("test msg")


@pytest.mark.asyncio
async def test_signal_keywords():
    cb1 = CoroutineMock()
    cb2 = CoroutineMock()

    ts = Signal()
    ts.connect(cb1)
    ts.connect(cb2)

    await ts.emit(test_msg="test msg")
    cb1.assert_called_with(test_msg="test msg")
    cb2.assert_called_with(test_msg="test msg")


@pytest.mark.asyncio
async def test_signal_cb_exception():
    cb_ok = CoroutineMock()

    async def cb_exception(*args, **kwargs):
        raise Exception

    ts = Signal()
    ts.connect(cb_ok)
    ts.connect(cb_exception)

    await ts.emit("test msg")
    cb_ok.assert_called_with("test msg")


@pytest.mark.asyncio
async def test_signal_sync_cb():
    ts = Signal()
    cb = MagicMock()
    ts.connect(cb)

    await ts.emit("test msg")
    assert cb.call_args_list == [call("test msg")]


@pytest.mark.asyncio
async def test_signal_connect_parallel_should_call_all_callbacks():
    sig = Signal()
    callbacks = [CoroutineMock(), CoroutineMock()]

    for cb in callbacks:
        sig.connect_parallel(cb)

    await sig.emit("test msg")
    await sig.wait_for_running()

    for cb in callbacks:
        assert cb.await_args_list == [call("test msg")]


def parallel_callback(event_loop: AbstractEventLoop, coro):
    handle: Optional[Task] = None

    @wraps(coro)
    async def exec_as_task(*args: Any, **kwargs: Any) -> Any:
        nonlocal handle
        if handle:
            handle.cancel()
            await handle

        handle = event_loop.create_task(coro(*args, **kwargs))

    return exec_as_task


@pytest.mark.asyncio
async def test_parallel_callback(event_loop: AbstractEventLoop):
    sig = Signal()
    decorator = partial(parallel_callback, event_loop)
    status = event_loop.create_future()

    @decorator
    async def set_code(code):
        status.set_result(code)

    sig.connect(set_code)
    await sig.emit("ok!")

    result = await wait_for(status, timeout=1)
    assert result == "ok!"

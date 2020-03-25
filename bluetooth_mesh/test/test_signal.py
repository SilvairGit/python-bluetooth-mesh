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
import pytest
from asynctest import CoroutineMock

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
async def test_signal_sync_async_cb():
    class Mock:
        def __init__(self):
            self.async_ret = None
            self.sync_ret = None

        async def async_cb(self, *args, **kwargs):
            self.async_ret = args

        def sync_cb(self, *args, **kwargs):
            self.sync_ret = args

    mocker = Mock()

    ts = Signal()
    ts.connect(mocker.async_cb)
    ts.connect(mocker.sync_cb)

    await ts.emit("test msg")
    assert mocker.async_ret == ("test msg",)
    assert mocker.sync_ret == ("test msg",)

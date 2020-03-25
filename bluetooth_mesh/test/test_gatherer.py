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
from asyncio import Future

import pytest

from bluetooth_mesh.utils import Gatherer


@pytest.mark.asyncio
async def test_gatherer():
    aws = [Future(), Future(), Future(), Future(), Future()]
    iaws = iter(aws)

    fut = next(iaws)
    fut.set_result(aws.index(fut))

    async for status in Gatherer(aws):
        assert status == (fut, aws.index(fut))
        fut = next(iaws, None)
        if fut:
            fut.set_result(aws.index(fut))


@pytest.mark.asyncio
async def test_gatherer_timeout():
    aws = [Future(), Future()]

    async for status in Gatherer(aws, timeout=0.1):
        key, val = status
        assert isinstance(val, TimeoutError)


@pytest.mark.asyncio
async def test_gatherer_exception():
    async def raises():
        raise Exception("ex")

    aws = [raises()]

    async for status in Gatherer(aws, timeout=0.1):
        stat, result = status
        assert stat == aws[0]
        assert isinstance(result, Exception)

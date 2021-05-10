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
import asyncio
import itertools
import logging
from asyncio.tasks import Task
from concurrent.futures._base import CancelledError
from contextlib import suppress
from functools import wraps
from inspect import isawaitable
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Hashable,
    Iterable,
    Mapping,
    Optional,
    Tuple,
    TypeVar,
)

from typing_extensions import Protocol

try:
    from asyncio import create_task
except ImportError:
    from asyncio import ensure_future

    create_task = ensure_future

ParsedMeshMessage = Mapping[str, Any]
MessageDescription = Mapping[str, Any]
ProgressCallback = Callable[[Hashable, Any, Mapping, Mapping], None]
T = TypeVar("T")


def chunks(iterable: Iterable[T], n: int, fillvalue: Optional[T] = None):
    """Collect data into fixed-length chunks or blocks"""
    # chunks('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue=fillvalue)


class MeshError(Exception):
    pass


class ModelOperationError(MeshError):
    def __init__(self, message: str, status: Optional[ParsedMeshMessage] = None):
        super().__init__(message)
        self.status = status

    def __repr__(self):
        return "{}({!r})".format(type(self).__name__, self.status)


class Signal:
    def __init__(self):
        self.logger = logging.getLogger(type(self).__name__)
        self.callbacks = set()

    def connect(self, callback):
        self.callbacks.add(callback)

    def disconnect(self, callback):
        try:
            self.callbacks.remove(callback)
        except KeyError:
            pass

    async def emit(self, *args, **kwargs):
        for callback in list(self.callbacks):
            try:
                result = callback(*args, **kwargs)
                if isawaitable(result):
                    await result
            except Exception as ex:
                self.logger.warning("Callback exception: %s", ex)

    @property
    def connections(self):
        return len(self.callbacks)


class Gatherer:
    """
    Gather tasks as they are done and return them in asynchronous iterator form.

    :param aws: iterable collection of tasks
    :param timeout: Timeout in seconds of None for no timeout
    :param loop: asyncio loop or None

    :return: A tuple of:
        - task to collect
        - result of the task
    """

    def __init__(self, aws: Iterable, timeout: int = None, loop=None):
        self.tasks = {asyncio.ensure_future(task): task for task in aws}
        self.buffer = asyncio.Queue()

        for status in self.tasks.keys():
            status.add_done_callback(self._done_callback)

        if timeout:
            loop = loop or asyncio.get_event_loop()
            loop.call_later(timeout, self.timeout)

    def _done_callback(self, item):
        task = self.tasks.pop(item)
        try:
            self.buffer.put_nowait((task, item.exception() or item.result()))
        except asyncio.CancelledError:
            self.buffer.put_nowait((task, TimeoutError()))

    def timeout(self):
        for task in self.tasks.keys():
            if not task.done():
                task.cancel()

    def __aiter__(self):
        return self

    async def __anext__(self):
        if not self.buffer.qsize() and not self.tasks:
            raise StopAsyncIteration

        return await self.buffer.get()


def construct_match(received, expected):
    def match(lhs, rhs):

        if rhs is Any or rhs is ...:
            return True

        if isinstance(rhs, list):
            return len(rhs) == len(lhs) and all(match(*i) for i in zip(lhs, rhs))

        if isinstance(rhs, dict):
            _lhs = {k: v for k, v in lhs.items() if not k.startswith("_")}
            return all(match(v, rhs.get(k, Any)) for k, v in _lhs.items())

        return lhs == rhs

    return match(received, expected)


class AnyCoroutine(Protocol):
    def __call__(self, *args: Any, **kwargs: Any) -> Awaitable[Any]:
        ...


class Respawn(Protocol):
    def __call__(self, *args: Any, **kwargs: Any) -> Awaitable[Task]:
        ...


class TaskGroupKeyFunction(Protocol):
    def __call__(self, *args: Tuple[Any], **kwargs: Mapping[str, Any]) -> Hashable:
        ...


def tasklet(coro: AnyCoroutine) -> Respawn:
    """
    Use case: you need to perform long-running background operations (tasks) that are spawned at random,
    and additionally, you want only one such operation running at a time for any given task group. If a new task is
    scheduled in a group, the previous, running one, is cancelled.

    To group tasks, a user-supplied `group_by` function is used. If set to None, all tasks are deemed to be in the same
    group.

    Example:
        @tasklet
        async def set_level(addr, level):
            result = await send_msg(addr, f"LEVEL={level}")
            while result != 1:
                await asyncio.sleep(60)
                result = await send_msg(addr, f"LEVEL={level}")

        set_level.group_by = lambda addr, level: addr

        levels = Signal()
        levels.connect(set_level)

        ...

        await levels.emit(0xDEAD, 50)   #  Schedules `set_level` coroutine (group = 0xDEAD)
        await levels.emit(0xBEEF, 50)   #  Schedules another `set_level` coroutine (group = 0xBEEF)

        await levels.emit(0xDEAD, 100)  #  Cancels running task in group 0xDEAD and schedules another `set_level`
                                        #  coroutine (group = 0xDEAD). Task scheduled in previous line keeps running.

    """
    handles: Dict[Hashable, Task] = dict()

    @wraps(coro)
    async def respawn(*args: Any, **kwargs: Any) -> Task:
        key = respawn.group_by(*args, **kwargs)
        with suppress(KeyError, CancelledError):
            handle = handles.pop(key)
            handle.cancel()
            await handle

        return handles.setdefault(key, create_task(coro(*args, **kwargs)))

    respawn.group_by = (
        lambda *args, **kwargs: 1
    )  # All tasks belong to one group by default
    return respawn

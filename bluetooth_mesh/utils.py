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
from inspect import isawaitable
from typing import Any, Callable, Hashable, Iterable, Mapping, Optional, TypeVar

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

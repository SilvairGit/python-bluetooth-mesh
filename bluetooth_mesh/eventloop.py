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
from contextlib import suppress
from concurrent.futures import ThreadPoolExecutor
from gi.repository import GLib

from prompt_toolkit.eventloop.defaults import get_event_loop, set_event_loop
from prompt_toolkit.eventloop.base import EventLoop
from prompt_toolkit.eventloop.context import wrap_in_current_context
from prompt_toolkit.eventloop.utils import ThreadWithFuture


class GLibEventLoop(EventLoop):
    """
    Wrapper around the GLib event loop, but compatible with prompt_toolkit.
    """
    def __init__(self, loop=None):
        super(GLibEventLoop, self).__init__()

        self.loop = loop or GLib.MainLoop()
        self.executor = ThreadPoolExecutor()
        self.descriptors = {}
        self.signals = {}
        self.closed = False

    def close(self):
        # Note: we should not close the asyncio loop itself, because that one
        # was not created here.
        self.closed = True

    def run_until_complete(self, future, inputhook=None):
        if inputhook:
            raise ValueError("GLibEventLoop doesn't support input hooks.")

        future.add_done_callback(lambda *args: self.loop.quit())

        with self.executor:
            self.loop.run()

    def run_forever(self, inputhook=None):
        if inputhook:
            raise ValueError("GLibEventLoop doesn't support input hooks.")

        with self.executor:
            self.loop.run()

    def run_in_executor(self, callback, _daemon=False):
        if _daemon:
            # Asyncio doesn't support 'daemon' executors.
            th = ThreadWithFuture(callback, daemon=True)
            self.call_from_executor(th.start)
            return th.future
        else:
            callback = wrap_in_current_context(callback)
            f = self.executor.submit(callback)
            return f

    def call_from_executor(self, callback, _max_postpone_until=None):
        """
        Call this function in the main event loop.
        Similar to Twisted's ``callFromThread``.
        """
        callback = wrap_in_current_context(callback)
        GLib.idle_add(callback)

    def add_reader(self, fd, callback):
        " Start watching the file descriptor for read availability. "
        callback = wrap_in_current_context(callback)

        def io_watch(reader, flags):
            callback()
            return True

        self.descriptors[fd] = GLib.io_add_watch(fd,
                                                 GLib.PRIORITY_DEFAULT,
                                                 GLib.IO_IN,
                                                 io_watch)

    def remove_reader(self, fd):
        " Stop watching the file descriptor for read availability. "
        with suppress(KeyError):
            GLib.Source.remove(self.descriptors.pop(fd))

    def add_signal_handler(self, signum, handler):
        if handler:
            self.signals[signum] = GLib.unix_signal_add(GLib.PRIORITY_DEFAULT,
                                                        signum, handler)
        else:
            with suppress(KeyError):
                GLib.Source.remove(self.signals.pop(signum))


def use_glib_event_loop(loop=None):
    """
    Use the asyncio event loop for prompt_toolkit applications.
    """
    # Don't create a new loop if the current one uses asyncio already.
    current_loop = get_event_loop()
    if current_loop and isinstance(current_loop, GLibEventLoop):
        return

    set_event_loop(GLibEventLoop(loop))

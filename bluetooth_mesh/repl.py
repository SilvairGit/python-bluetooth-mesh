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
import signal
import traceback

from gi.repository import GLib

from prompt_toolkit import PromptSession
from prompt_toolkit.eventloop import Future


class REPL:
    def __init__(self, loop=None, *, prompt=None):
        self.session = PromptSession(**(prompt or {}))
        self.loop = loop or GLib.MainLoop()

        self.__future = None
        GLib.unix_signal_add(GLib.PRIORITY_DEFAULT,
                             signal.SIGINT, self.__interrupt)
        GLib.idle_add(self.__prompt)

    def __interrupt(self):
        if self.__future:
            self.__future.set_exception(KeyboardInterrupt())

        return True

    def __finish(self, future=None):
        if future is self.__future:
            self.__future = None
        self.__prompt()

    def __prompt(self):
        prompt = self.session.prompt(self.prompt, async_=True)

        def done(future):
            try:
                result = future.result()
                self.__future = self.__command(result) if result else None
            except KeyboardInterrupt:
                pass
            except EOFError:
                self.loop.quit()
            except Exception as ex:
                self.__exception(ex)
                self.__finish()
            else:
                if isinstance(self.__future, Future):
                    self.__future.add_done_callback(self.__finish)
                else:
                    self.__finish()

        prompt.add_done_callback(done)

    def __exception(self, ex):
        print(traceback.format_exc())

    def __command(self, cmd):
        return self.command(cmd)

    def command(self, cmd):
        pass

    @property
    def prompt(self):
        return '%s> ' % type(self).__name__

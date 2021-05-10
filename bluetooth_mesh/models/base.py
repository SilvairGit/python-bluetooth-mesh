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
import inspect
from collections import defaultdict
from contextlib import suppress
from datetime import timedelta
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Hashable,
    List,
    Mapping,
    Optional,
    Sequence,
    Set,
    Tuple,
    Union,
)
from uuid import UUID

from bluetooth_mesh.messages import AccessMessage
from bluetooth_mesh.utils import (
    Gatherer,
    MessageDescription,
    ParsedMeshMessage,
    ProgressCallback,
    construct_match,
)

__all__ = [
    "Model",
    "ModelConfig",
]


class Model:
    """
    Base class for mesh models.
    """

    MODEL_ID = (None, None)  # type: Tuple[Optional[int], int]
    OPCODES = []  # type: List[int]
    PUBLISH = False  # type: bool
    SUBSCRIBE = False  # type: bool

    def __init__(self, element: "Element"):
        self.__tid = 0
        self.element = element

        self.logger = self.element.logger.getChild("%s" % type(self).__name__)

        self.app_message_callbacks = defaultdict(set)  # type: Dict[int, Set[Callable]]
        self.dev_message_callbacks = defaultdict(set)  # type: Dict[int, Set[Callable]]
        self.subscription_callbacks = defaultdict(
            set
        )  # type: Dict[Union[int, UUID], Set]

        assert self.MODEL_ID[1] is not None, "A model has to have ID!"
        self.configuration = ModelConfig(bindings=[], subscriptions=[])

    def tid(self) -> int:
        tid = self.__tid
        self.__tid = (tid + 1) % 255
        return tid

    def __str__(self):
        if self.MODEL_ID[0] is None:
            return "<Model %04x>" % self.MODEL_ID[1]

        return "<VendorModel %04x%04x>" % self.MODEL_ID

    @property
    def _node_interface(self):
        return self.element.application.node_interface

    def update_configuration(self, configuration: "ModelConfig"):
        if configuration.bindings is not None:
            self.configuration.bindings = configuration.bindings

        if configuration.publication_period is not None:
            self.configuration.publication_period = configuration.publication_period

        if configuration.subscriptions is not None:
            self.configuration.subscriptions = configuration.subscriptions

        self.logger.info("Update config of %s: %s", self.MODEL_ID, self.configuration)

    def message_received(
        self,
        source: int,
        app_index: int,
        destination: Union[int, UUID],
        message: ParsedMeshMessage,
    ):
        self.logger.debug(
            "App message received: %04x [app_index %d, destination %04x] %r",
            source,
            app_index,
            destination,
            message,
        )

        callbacks = self.app_message_callbacks[message["opcode"]]

        for callback in list(callbacks):
            if callback(source, app_index, destination, message):
                callbacks.remove(callback)

        subscription_callbacks = self.subscription_callbacks.get(destination, ())

        for callback in subscription_callbacks:
            callback(
                source=source,
                destination=destination,
                app_index=app_index,
                message=message,
            )

    def dev_key_message_received(
        self, source: int, remote: bool, net_index: int, message: ParsedMeshMessage
    ):
        self.logger.debug(
            "Dev message received: %04x [remote %s, net_index %d] %r",
            source,
            remote,
            net_index,
            message,
        )

        callbacks = self.dev_message_callbacks[message["opcode"]]

        for callback in list(callbacks):
            if callback(source, net_index, message):
                callbacks.remove(callback)

    def expect_app(
        self,
        source: int,
        app_index: int,
        destination: Optional[Union[int, UUID]],
        opcode: int,
        params: MessageDescription,
    ) -> asyncio.Future:
        """
        Create an `asyncio.Future` that gets fulfilled when a specific
        application message is received.

        `opcode` is the expected message's numeric opcode, as defined in the
        mesh spec. See :py:mod:`bluetooth_mesh.messages` for a list of well-known
        opcodes.

        `params` define the message contents. After a received message is
        parsed using :py:data:`bluetooth_mesh.messages.AccessMessage`, it's compared
        recursively, key-by-key, with `params`. If all keys match, the future's
        result is set to the parsed message. If the keys are not specified,
        they will be ignored.

        One can specify wildcards by specifying key value as
        :py:data:`typing.Any` or :py:data:`...` (Ellipsis) - these match with
        anything, including composite fields.

        :param source: Sender address
        :param app_index: Index of the application key
        :param destination: Destination address
        :param opcode: Expected message opcode.
        :param params: Expected message parameters.
        """

        future = asyncio.Future()

        def app_message_received(
            _source: int,
            _app_index: int,
            _destination: Union[int, UUID],
            message: ParsedMeshMessage,
        ):
            if (_source != source) or (_app_index != app_index):
                return False

            if destination is not None and (_destination != destination):
                return False

            if params and not construct_match(message["params"], params):
                return False

            if not future.done():
                future.set_result(message)

            return True

        self.app_message_callbacks[opcode].add(app_message_received)

        return future

    def expect_dev(
        self, source: int, net_index: int, opcode: int, params: MessageDescription
    ) -> asyncio.Future:
        """
        Create an `asyncio.Future` that gets fulfilled when a specific
        device message is received.

        Unlike application keys, device keys are bound to all subnets, so
        you need to explicitly provide `net_index`.

        See :py:func:`expect_app`

        :param source: Sender address
        :param net_index: Index of the network key
        :param opcode: Expected message opcode.
        :param params: Expected message parameters.
        """

        future = asyncio.Future()

        def dev_message_received(
            _source: int, _net_index: int, message: ParsedMeshMessage
        ):
            if (_source != source) or (_net_index != net_index):
                return False

            if params and not construct_match(message["params"], params):
                return False

            if not future.done():
                future.set_result(message)

            return True

        self.dev_message_callbacks[opcode].add(dev_message_received)

        return future

    async def _send_app(self, destination: int, app_index: int, data: bytes):
        self.logger.debug(
            "Sending: %s -> %04x [app_index %d] %s",
            self.element.path,
            destination,
            app_index,
            data.hex(),
        )
        await self._node_interface.send(self.element.path, destination, app_index, data)

    async def send_app(
        self, destination: int, app_index: int, opcode: int, params: MessageDescription
    ):
        """
        Send a message using an application key.

        :param destination: Destination address
        :param app_index: Index of the application key
        :param opcode: Message opcode.
        :param params: Message parameters.
        """

        data = AccessMessage.build(dict(opcode=opcode, params=params))

        message = AccessMessage.parse(data)
        self.logger.debug(
            "Sending: %s -> %04x [app_index %d] %r",
            self.element.path,
            destination,
            app_index,
            message,
        )

        await self._send_app(destination, app_index, data)

    async def _send_dev(
        self, destination: int, remote: bool, net_index: int, data: bytes
    ):
        self.logger.debug(
            "Sending: %s -> %04x [remote %s, net_index %d] %s",
            self.element.path,
            destination,
            remote,
            net_index,
            data.hex(),
        )

        await self._node_interface.dev_key_send(
            self.element.path, destination, remote, net_index, data
        )

    async def send_dev(
        self, destination: int, net_index: int, opcode: int, params: MessageDescription
    ):
        """
        Send a message using a device key.

        `destination` determines which device key is going to be used. For
        local destinations, the key is always known, but if `destination` is a
        remote node, the caller must first import its device key using
        :func:`~bluetooth_mesh.application.Application.import_remote_node`.

        Unlike application keys, device keys are bound to all subnets, so
        you need to explicitly provide `net_index`.

        See :py:func:`send_app`

        :param destination: Destination address
        :param net_index: Index of the network key
        :param opcode: Message opcode.
        :param params: Message parameters.
        """

        remote = True
        data = AccessMessage.build(dict(opcode=opcode, params=params))

        message = AccessMessage.parse(data)
        self.logger.debug(
            "Sending: %s -> %04x [remote %s, net_index %d] %r",
            self.element.path,
            destination,
            remote,
            net_index,
            message,
        )

        await self._send_dev(destination, remote, net_index, data)

    async def repeat(
        self,
        request: Callable[[], Awaitable],
        *,
        retransmissions: int = 6,
        send_interval: float = 0.05,
    ):
        """
        Application retransmissions

        :param request:
        :param retransmissions:
        :param send_interval:

        """

        for _ in range(retransmissions):
            await request()
            await asyncio.sleep(send_interval)

    async def query(
        self,
        request: Callable[[], Awaitable[None]],
        status: asyncio.Future,
        *,
        send_interval: float = 0.2,
        timeout: float = 2.0,
    ) -> Any:
        """
        Query

        :param request:
        :param status:
        :param send_interval:
        :param timeout:

        """

        async def sender():
            while not status.done():
                await request()
                await asyncio.sleep(send_interval)

        sender = asyncio.ensure_future(sender())

        try:
            await asyncio.wait_for(status, timeout=timeout)
        finally:
            with suppress(asyncio.CancelledError):
                sender.cancel()
                await sender

        return status.result()

    async def bulk_query(
        self,
        requests: Mapping[Hashable, Callable[[], Awaitable[None]]],
        statuses: Mapping[Hashable, asyncio.Future],
        *,
        send_interval: float = 0.5,
        progress_callback: Optional[ProgressCallback] = None,
        timeout: float = 5.0,
    ) -> Mapping[Hashable, Any]:
        """
        Bulk query

        :param requests:
        :param statuses:
        :param send_interval:
        :param progress_callback:
        :param timeout:

        """

        done = {}

        async def sender():
            while requests:
                for request in list(requests.values()):
                    await request()
                    await asyncio.sleep(send_interval)

        key_mapping = {status: key for key, status in statuses.items()}

        sender = asyncio.ensure_future(sender())
        async for status, result in Gatherer(statuses.values(), timeout=timeout):
            key = key_mapping[status]
            requests.pop(key)
            done[key] = result

            if progress_callback:
                cb = progress_callback(key, result, done, statuses)
                if inspect.isawaitable(cb):
                    await cb

        with suppress(asyncio.CancelledError):
            sender.cancel()
            await sender

        results = {}

        for status in statuses.values():
            key = key_mapping[status]
            if status.cancelled():
                results[key] = asyncio.CancelledError()
            else:
                results[key] = status.exception() or status.result()

        return results

    async def subscribe(
        self,
        app_keys: Sequence[Tuple[int, int, "ApplicationKey"]],
        subscription_address: int,
        callback: Callable[[int, Union[int, UUID], int, ParsedMeshMessage], None],
    ) -> "ModelSubscriptionStatus":
        """
        Subscribe to messages sent to `subscription_address` and encrypted with
        either of application keys

        This method ensures that the application key is bound to the model.

        This causes `callback` to be called whenerver such message is received.

        :param app_keys:
        :param subscription_address:
        :param callback:

        :return: A tuple of:
            - unicast address of the element the bound model belongs to
            - subscription address (usually a group address)
            - class object of the bound model
        """
        from bluetooth_mesh.models.models import ModelSubscriptionStatus

        self.subscription_callbacks[subscription_address].add(callback)

        for app_index, *_ in app_keys:
            if app_index in self.configuration.bindings:
                continue

            await self.bind(app_index)

        if subscription_address in self.configuration.subscriptions:
            element_address = self.element.application.address + self.element.index
            return ModelSubscriptionStatus(
                element_address, subscription_address, type(self)
            )

        return await self.element.application.subscribe_model(
            subscription_address, model=self
        )

    async def unsubscribe(
        self,
        subscription_address: Optional[int] = None,
        callback: Optional[
            Callable[[int, Union[int, UUID], int, ParsedMeshMessage], None]
        ] = None,
    ) -> "ModelSubscriptionStatus":
        """
        Unubscribe from messages sent to `subscription_address`, or clear
        subscriptions if `subscription_address` is not provided.

        :return: A tuple of:
            - unicast address of the element the bound model belongs to
            - subscription address (usually a group address)
            - class object of the bound model
        """
        from bluetooth_mesh.models.models import ModelSubscriptionStatus

        if subscription_address is None:
            self.subscription_callbacks.clear()
            return await self.element.application.clear_subscriptions(model=self)

        self.subscription_callbacks[subscription_address].discard(callback)

        # if there are any callbacks left, do not unsubscribe the model
        if self.subscription_callbacks[subscription_address]:
            return

        if subscription_address not in self.configuration.subscriptions:
            element_address = self.element.application.address + self.element.index
            return ModelSubscriptionStatus(
                element_address, subscription_address, type(self)
            )

        return await self.element.application.unsubscribe_model(
            subscription_address, model=self
        )

    async def bind(self, app_key_index: int) -> "ModelBindStatus":
        """
        Bind to application key with index `app_key_index`.

        You probably don't want to call this directly, see
        :py:func:`Model.subscribe` instead.

        :param app_key_index:

        :return: A tuple of:
            - unicast address of the element the bound model belongs to
            - index of the bound application key
            - class object of the bound model
        """

        return await self.element.application.bind_app_key(app_key_index, model=self)


class ModelConfig:
    """
    Model Configuration class for mesh models.
    """

    def __init__(
        self,
        bindings: List[int] = None,
        publication_period: timedelta = None,
        subscriptions: Set[Union[int, UUID]] = None,
    ):
        self.bindings = bindings
        self.publication_period = publication_period
        self.subscriptions = subscriptions

    def __str__(self):
        return f"<ModelConfig bindings={self.bindings}, subs={self.subscriptions}>"

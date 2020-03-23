Models
======

.. automodule:: bluetooth_mesh.models

Each model must declare its id and a list of supported opcodes:

.. literalinclude:: examples/model.py
   :language: python

Sending messages
----------------

There are two basic methods to send messages to remote nodes:
:func:`~Model.send_app` and :func:`~Model.send_dev`. Usage should be
self-explanatory. Keep in mind that they are implemented on top of
:py:data:`bluetooth_mesh.messages.AccessMessage`, so you don't need to deal with raw
encoding - just pass the message contents as a :py:data:`dict` aligned with
message structure. See :py:mod:`bluetooth_mesh.messages` for details.

To handle application retransmissions, use :func:`~Model.repeat`. Basic usage
looks like this:

.. literalinclude:: examples/repeat.py
   :language: python

The :func:`~Model.repeat` method takes a callable, because each application
retransmission might have slightly different content (e.g.  `delay` in
:py:data:`GenericOnOff` message). This means that you can use it like this:

.. literalinclude:: examples/delay.py
   :language: python

.. note::
   It might be more convenient to replace the callable with async generator,
   but I'm not sure about compatibility with older Python versions.

.. note::
   Publication API is not implemented yet.

Receiving messages
------------------

There are two ways to receive messages: first is based on simple callbacks,
while the second is built on top of :py:class:`Future`.

To register a callback for an opcode, simply add it to either
:py:attr:`~Model.app_message_callbacks` or
:py:attr:`~Model.dev_message_callbacks`. Note the different signature for each
of these. Also, callbacks are *not asynchronous*.

.. literalinclude:: examples/callbacks.py
   :language: python

.. note::
   Maybe we should make the callbacks async?

The other method allows the application to *asynchronously* wait for a specific message:

.. literalinclude:: examples/expect.py
   :language: python

.. note::
   At the moment message matching rules are very simple - there is no way to
   specify wildcards, optional fields, variants etc. We might want to expand
   this, see source for :func:`~bluetooth_mesh.models.Model.expect_app`


Combined send/receive
---------------------

A typical request/response sequence retransmits some kind of "get" message
until for a specific "status" message is sent back (or a timeout occurs). To
simplify this, there are two high level methods for "querying" nodes:
:func:`~Model.query` and :func:`~Model.bulk_query`.

Querying a single node
~~~~~~~~~~~~~~~~~~~~~~

To query a single node, use :func:`~Model.query`. The `request` parameter
behaves in the same way as in :func:`~Model.repeat` described above, while
`status` is a :py:class:`Future` obtained from :func:`~Model.expect_app` or
:func:`~Model.expect_dev`. For example:

.. literalinclude:: examples/query.py
   :language: python

Bulk queries
~~~~~~~~~~~~

A similar mechanism is implemented for "bulk queries". Instead of a single
request/status pair, you need to pass two dictionaries with the same
(arbitrary) keys: `requests` and `statuses`.

Callables from `requests` are retransmitted once every `send_interval`, until a
matching `Future` from `statuses` is completed. At this point, the
retransmission stops.

When all `statuses` are completed, or a `timeout` expires, method returns a
`dict` with results. Each result is either a received message, or and
`Exception` object, if a respective query failed or timed out. Note that the
`timeout` parameter is an *overall* timeout for the whole bulk.

Example:

.. literalinclude:: examples/bulk_query.py
   :language: python

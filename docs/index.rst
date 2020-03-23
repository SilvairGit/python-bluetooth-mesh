Welcome to bluetooth-mesh documentation!
========================================

This package provides a micro-framework for mesh applications. 

The framework consists of two main parts:

* :py:mod:`bluetooth_mesh.application` is a high-level wrapper/provider of BlueZ's
  D-Bus API, working on top of dbus-next_.

* :py:mod:`bluetooth_mesh.models` implement a well-known mesh models, both clients and servers.

Internally, it uses the following modules:

* :py:mod:`bluetooth_mesh.messages` contain Construct_-based definitions of messages,
  extending definitions provided by bluetooth-mesh_ package.

.. _mesh-api.txt: https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/doc/mesh-api.txt
.. _Construct: https://construct.readthedocs.io/
.. _bluetooth-mesh: https://pypi.org/project/bluetooth-mesh/
.. _dbus-next: https://github.com/altdesktop/python-dbus-next

.. toctree::
   :caption: Contents:

   installation
   quickstart
   mod
   api


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

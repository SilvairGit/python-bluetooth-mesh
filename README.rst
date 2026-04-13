=====================
python-bluetooth-mesh
=====================

.. image:: https://img.shields.io/pypi/v/bluetooth-mesh.svg
    :target: https://pypi.org/project/bluetooth-mesh
    :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/bluetooth-mesh.svg
    :target: https://pypi.org/project/bluetooth-mesh
    :alt: Python versions

Bluetooth mesh SDK for Python allows developing applications communicating with
Bluetooth mesh network using BlueZ's bluetooth-meshd.

----

What is this thing?
-------------------

https://www.bluetooth.com/specifications/mesh-specifications

https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/doc/mesh-api.txt


Installation
------------

This project requires Python 3.14.

You can install "python-bluetooth-mesh" via `pip`_ from `PyPI`_::

    $ pip install bluetooth-mesh

The package exposes an optional ``bluez`` extra for BlueZ integration::

    $ pip install bluetooth-mesh[bluez]

You can also add it to a Poetry-managed project::

    $ poetry add bluetooth-mesh

To install the optional BlueZ dependencies with Poetry::

    $ poetry add bluetooth-mesh --extras bluez

If you want to work on this repository locally, install the project and development dependencies
with Poetry::

    $ poetry install

Contributing
------------
Contributions are very welcome. This package is a wrapper around the underlying ``bluetooth-mesh-messages``,
``bluetooth-mesh-network``, and ``bluetooth-mesh-bluez`` packages, so code changes should be proposed
in the appropriate dependency repository rather than here:

* ``bluetooth-mesh-bluez``: https://github.com/SilvairGit/python-bluetooth-mesh-bluez
* ``bluetooth-mesh-messages``: https://github.com/SilvairGit/python-bluetooth-mesh-messages
* ``bluetooth-mesh-network``: https://github.com/SilvairGit/python-bluetooth-mesh-network


License
-------

Distributed under the terms of the `GPL-2.0`_ license, "python-bluetooth-mesh" is
free and open source software


Issues
------

If you encounter any problems, please `file an issue`_ along with a detailed description.

.. _`GPL-2.0`: http://opensource.org/licenses/GPL-2.0
.. _`file an issue`: https://github.com/SilvairGit/python-bluetooth-mesh/issues
.. _`pip`: https://pypi.org/project/pip/
.. _`PyPI`: https://pypi.org/project

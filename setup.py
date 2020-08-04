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
from setuptools import find_packages, setup

with open("README.rst", "r") as f:
    long_description = f.read()

# fmt: off
setup(
    name='bluetooth-mesh',
    version='0.2.27',
    author_email='michal.lowas-rzechonek@silvair.com',
    description=(
        'Bluetooth mesh for Python'
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='http://github.com/silvairgit/python-bluetooth-mesh',
    packages=find_packages(exclude=('test*', )),
    python_requires='>=3.6.0,<3.8.0',
    setup_requires=[
        'pytest-runner==4.2',
    ],
    install_requires=[
        'bitstring>=3.1.5',
        'construct>=2.9.45,<2.9.46',
        'cryptography>=2.3.1',
        'crc==0.3.0',
        'dbus-next>=0.1.3',
        'ecdsa==0.15',
        'pluggy>=0.13.1',
        'marshmallow>=3.0.1,<4.0',
    ],
    tests_require=[
        'asynctest==0.12.3',
        'coveralls==2.0.0',
        'pytest==5.0.0',
        'pytest-asyncio==0.10.0',
        'pytest-cov>=2.8.1',
    ],
    extras_require=dict(
        docs=[
            'sphinx>=2.1.2',
            'sphinx-autodoc-typehints>=1.7.0',
        ],
        tools=[
            'prompt-toolkit==2.0.10',
        ],
    ),
    entry_points=dict(
        console_scripts=[
            'meshcli = bluetooth_mesh.apps.meshcli:main [tools]',
        ],
        bluetooth_mesh=[
            'bluetooth_mesh = bluetooth_mesh.apps.mixins',
        ]
    ),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: AsyncIO',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: System :: Networking',
    ],
)
# fmt: on

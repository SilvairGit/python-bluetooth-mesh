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
from setuptools import setup, find_packages


with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name='bluetooth-mesh',
    version='0.1.29',
    author='Michał Lowas-Rzechonek',
    author_email='michal.lowas-rzechonek@silvair.com',
    description=(
        'Bluetooth Mesh for Python'
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='http://github.com/silvairgit/python-bluetooth-mesh',
    packages=find_packages(exclude=('test*', )),
    python_requires='>=3.5.0',
    install_requires=[
        'bitstring>=3.1.5',
        'construct>=2.9.45,<2.10.0',
        'cryptography>=2.3.1',
        'ecdsa==0.15',
        'crc==0.3.0'
    ],
    extras_require={
        'demo': [
            'docopt>=0.6.2',
            'marshmallow>=3.0.0rc3',
            'pillow>=5.4.1',
            'pygobject>=3.30.4',
            'pydbus>=0.6.0',
            'prompt-toolkit>=2.0.8',
        ],
    },
    tests_require=[
        'pytest>4.1.0',
        'pytest-runner>=4.2',
    ],
    entry_points=dict(
        console_scripts=[
            'gatt-client = bluetooth_mesh.cli.gatt_client:main [demo]',
        ]
    ),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.6',
        'Topic :: System :: Networking',
    ],
)

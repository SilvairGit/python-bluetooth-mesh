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

with open("README.md", "r") as f:
    long_description = f.read()

# fmt: off
setup(
    name='bluetooth-mesh',
    version='0.2.0',
    author_email='michal.lowas-rzechonek@silvair.com',
    description=(
        'Bluetooth mesh for Python'
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='http://github.com/silvairgit/python-bluetooth-mesh',
    packages=find_packages(exclude=('test*', )),
    python_requires='>=3.6.0',
    setup_requires=[
        'pytest-runner>=4.2',
    ],
    install_requires=[
        'bitstring>=3.1.5',
        'construct==2.9.45',
        'cryptography>=2.3.1',
        'ecdsa==0.15',
        'crc==0.3.0'
    ],
    tests_require=[
        'pytest>4.1.0',
    ],
    entry_points=dict(
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
# fmt: on

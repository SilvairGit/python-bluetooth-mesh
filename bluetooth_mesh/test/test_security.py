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
from pytest import fixture

from bluetooth_mesh.crypto import k1, k2, k3, k4, s1


@fixture
def app_key():
    return bytes.fromhex("3216d1509884b533248541792b877f98")


@fixture
def net_key():
    return bytes.fromhex("f7a2a44f8e8a8029064f173ddc1e2b00")


@fixture
def dev_key():
    return bytes.fromhex("37c612c4a2d337cb7b98355531b3617f")


def test_s1():
    s = s1(b"test")
    assert s == bytes.fromhex("b73cefbd641ef2ea598c2b6efb62f79c")


def test_k1(app_key):
    N = app_key
    SALT = bytes.fromhex("2ba14ffa0df84a2831938d57d276cab4")
    P = bytes.fromhex("5a09d60797eeb4478aada59db3352a0d")

    k = k1(N, SALT, P)

    assert k == bytes.fromhex("f6ed15a8934afbe7d83e8dcb57fcf5d7")


def test_k2_master(net_key):
    N = net_key
    P = b"\x00"

    n, e, p = k2(N, P)

    assert n == 0x7F
    assert e == bytes.fromhex("9f589181a0f50de73c8070c7a6d27f46")
    assert p == bytes.fromhex("4c715bd4a64b938f99b453351653124f")


def test_k3(net_key):
    N = net_key

    n = k3(N)

    assert n == bytes.fromhex("ff046958233db014")


def test_k4(app_key):
    N = app_key

    a = k4(N)

    assert a == 0x38

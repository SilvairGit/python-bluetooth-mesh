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

# pylint: disable=C0103

from functools import lru_cache

import bitstring
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import cmac
from cryptography.hazmat.primitives.ciphers import Cipher, aead, algorithms, modes


def aes_cmac(k, m):
    c = cmac.CMAC(algorithms.AES(k), backend=default_backend())
    c.update(m)
    return c.finalize()


def aes_ccm_encrypt(k, n, m, a=b"", tag_length=4):
    c = aead.AESCCM(k, tag_length)
    return c.encrypt(n, m, a)


def aes_ccm_decrypt(k, n, m, a=b"", tag_length=4):
    c = aead.AESCCM(k, tag_length)
    return c.decrypt(n, m, a)


def aes_ecb(k, m):
    c = Cipher(algorithms.AES(k), modes.ECB(), backend=default_backend())
    e = c.encryptor()
    return e.update(m) + e.finalize()


def s1(M):
    ZERO = bytes([0] * 16)
    return aes_cmac(ZERO, M)


def k1(N, SALT, P):
    T = aes_cmac(SALT, N)
    return aes_cmac(T, P)


def k2(N, P):
    SALT = s1(b"smk2")
    T = aes_cmac(SALT, N)
    T0 = b""
    T1 = aes_cmac(T, T0 + P + b"\x01")
    T2 = aes_cmac(T, T1 + P + b"\x02")
    T3 = aes_cmac(T, T2 + P + b"\x03")

    k = (T1 + T2 + T3)[-33:]

    n, e, p = bitstring.BitString(k).unpack("pad:1, uint:7, bits:128, bits:128")

    return n, e.bytes, p.bytes


def k3(N):
    SALT = s1(b"smk3")
    T = aes_cmac(SALT, N)
    return aes_cmac(T, b"id64\x01")[-8:]


def k4(N):
    SALT = s1(b"smk4")
    T = aes_cmac(SALT, N)

    k = aes_cmac(T, b"id6\x01")[-1:]

    (aid,) = bitstring.BitString(k).unpack("pad:2, uint:6")

    return aid


class Key:
    def __init__(self, key):
        self.bytes = key

    def __str__(self):
        return "<%s: %s>" % (type(self).__name__, self.bytes.hex())


class ApplicationKey(Key):
    @property
    @lru_cache(maxsize=1)
    def aid(self):
        return k4(self.bytes)


class DeviceKey(Key):
    @property
    def aid(self):
        return 0


class NetworkKey(Key):
    @property
    @lru_cache(maxsize=1)
    def network_id(self):
        return k3(self.bytes)

    @property
    @lru_cache(maxsize=1)
    def encryption_keys(self):
        return k2(self.bytes, b"\x00")

    @property
    @lru_cache(maxsize=1)
    def identity_key(self):
        return k1(self.bytes, s1(b"nkik"), b"id128\x01")

    @property
    @lru_cache(maxsize=1)
    def beacon_key(self):
        return k1(self.bytes, s1(b"nkbk"), b"id128\x01")

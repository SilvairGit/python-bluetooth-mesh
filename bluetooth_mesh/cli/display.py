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
from PIL import Image, ImageFont, ImageDraw
import string


class Font:
    LETTERS = string.ascii_letters + string.digits + ' @'

    def __init__(self, font):
        self.font = ImageFont.load(font)

        size = self.font.getsize(self.LETTERS)
        self.image = Image.new('1', size, 1)

        draw = ImageDraw.Draw(self.image)
        draw.text((0, 0), self.LETTERS, font=self.font)

        self.size = size[1]

    def glyph(self, letter):
        g = [[False] * self.size for _ in range(self.size)]
        index = self.LETTERS.index(letter)

        for row in range(self.size):
            for col in range(self.size):
                if letter == '_':
                    g[row][col] = False
                elif letter == '#':
                    g[row][col] = True
                else:
                    if self.image.getpixel((index * self.size + col, row)):
                        g[row][col] = False
                    else:
                        g[row][col] = True

        return index, g


class Display:
    DOTS = [
        [0x7223, 0xba1e, 0x68db, 0x28d8, 0x7c90, 0x84d4, 0x153b, 0xc6f5],
        [0xf340, 0xf214, 0xa713, 0xc257, 0x5a90, 0xf343, 0xbf3a, 0x772c],
        [0xbf20, 0x8726, 0xc694, 0xea26, 0xdf48, 0x7f8e, 0xbcee, 0xb89c],
        [0x3068, 0x82d8, 0x78fe, 0x38ff, 0xe289, 0x4033, 0x6529, 0x38a2],
        [0xcccf, 0x6dff, 0x4088, 0xb979, 0x826c, 0x4b56, 0x9731, 0xdf26],
        [0x9de6, 0xc5cc, 0x841f, 0xdd48, 0xd5e9, 0xf61a, 0xc281, 0xd14a],
        [0xa23e, 0x35bb, 0x1ffc, 0xa8dc, 0xb672, 0x6c97, 0x2be5, 0x99f7],
        [0x045f, 0xa7c3, 0xca2f, 0x0483, 0xdad2, 0xaefa, 0x5ce5, 0x561d],
    ]

    def __init__(self, network):
        self.font = Font('fonts/unscii-8.pil')
        self.node2dot = {}
        self.dot2node = {}

        for row, line in enumerate(self.DOTS):
            for col, node_id in enumerate(line):
                node = network.shorts[node_id]

                self.node2dot[node.address] = (row, col)
                self.dot2node[(col, row)] = node.address

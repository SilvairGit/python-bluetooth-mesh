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

GLYPHS = '''
A
 ### 
#   #
#####
#   #
#   #
B
#### 
#   #
#### 
#   #
#### 
C
 ####
#    
#    
#    
 ####
D
#### 
#   #
#   #
#   #
#### 
E
#####
#    
#### 
#    
#####
F
#####
#    
#### 
#    
#    
G
 ####
#    
# ###
#   #
 ####
H
#   #
#   #
#####
#   #
#   #
I
  #  
  #  
  #  
  #  
  #  
J
  ###
    #
    #
#   #
 ### 
K
#  # 
# #  
#### 
#   #
#   #
L
#    
#    
#    
#    
#####
M
#   #
## ##
# # #
#   #
#   #
N
##  #
# # #
# # #
# # #
#  ##
O
 ### 
#   #
#   #
#   #
 ### 
P
#### 
#   #
#### 
#    
#    
Q
 ##  
#  # 
#  # 
#  # 
 ####
R
#### 
#   #
#### 
#  # 
#   #
S
 ####
#    
 ### 
    #
#### 
T
#####
  #  
  #  
  #  
  #  
U
#   #
#   #
#   #
#   #
 ### 
V
#   #
#   #
 # # 
 # # 
  #  
W
#   #
#   #
# # #
## ##
#   #
X
#   #
 # # 
  #  
 # # 
#   #
Y
#   #
#   #
 ### 
  #  
  #  
Z
#####
    #
 ### 
#    
#####
_
     
     
     
     
     
'''

DOTS = '''
046f 0490 048a 0478 046c
0499 045d 0457 0463 047e
0472 0493 048d 0496 0454
0487 0484 04a5 047b 04a2
0469 049c 049f 0481 0475
'''


class Display:
    def __init__(self):
        self.glyph = {}

        lines = iter(GLYPHS.split('\n')[1:-1])

        while True:
            try:
                letter = next(lines)
                glyph = [next(lines) for i in range(5)]

                self.glyph[letter] = [
                    [dot == '#' for dot in row] for row in glyph
                ]
            except StopIteration:
                break

        self.node2dot = {}
        self.dot2node = {}

        for row, line in enumerate(DOTS.strip().split('\n')):
            for col, addr in enumerate(line.strip().split()):
                self.node2dot[int(addr, 16)] = (row, col)
                self.dot2node[(col, row)] = int(addr, 16)

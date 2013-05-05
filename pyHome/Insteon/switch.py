"""
Copyright (c) 2012, Tyler Voskuilen
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met: 

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer. 
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution. 

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

from message import Message

import pyHome.core

class Switch(pyHome.core.Switch):
    def __init__(self, house, xml):
        pyHome.core.Switch.__init__(self, house, xml)
        
    def turn_on(self, level=100, fast=False):
        """ Turn the light on to level (0-100) at a normal or fast rate """
        level = min(max(0,level),100)
        cmd1 = 0x12 if fast else 0x11
        cmd2 = int(round(level * 2.55))
        self.send( Message([0x02,0x62]+self.address+[0x0F,cmd1,cmd2]) )

    def turn_off(self, fast=False):
        """ Turn the light off at a normal or fast rate """
        cmd1 = 0x14 if fast else 0x13
        self.send( Message([0x02,0x62]+self.address+[0x0F,cmd1,0xFF]) )
            
            



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

from device import Device

class Switch(Device):
    state_icons = ['On', 'Off']
    
    """
    You must define turn_on and turn_off for this device
    
    .. warning:: This class is abstract. Always implement one of its subclasses
    
    """
    def __init__(self, house, xml):
        Device.__init__(self, house, xml)

    def get_context_menu(self, host):
        return [{'Name':self.name+' - '+self.room, 'Fcn':lambda event: host._show_info(self)},
                {'Name':'Turn On', 'Fcn':self.turn_on},
                {'Name':'Turn Off', 'Fcn':self.turn_off},
                {'Name':'Remove Device', 'Fcn':lambda event: host._remove_device(self)}]
                
    def toggle(self, level=100, fast=False):
        if self.state[0] == 'On':
            self.turn_off(fast)
        else:
            self.turn_on(level,fast)
                    
    def turn_on(self, level=100, fast=False):
        raise NotImplemented
    
    def turn_off(self, fast=False):
        raise NotImplemented
        
        
        

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

from switch import Switch

class Dimmer(Switch):
    state_icons = ['On', 'Off']
    
    """
    You must define turn_on, turn_off, ramp_on, and ramp_off for this device
    
    .. warning:: This class is abstract. Always implement one of its subclasses
    
    """
    def __init__(self, house, xml):
        Switch.__init__(self, house, xml)

    def get_context_menu(self, host):
        return [{'Name':self.name+' - '+self.room, 'Fcn':lambda event: host._show_info(self)},
                {'Name':'Fine Adjust', 'Fcn':lambda event: host._fine_adjust(self)},
                {'Name':'Turn On (100%)', 'Fcn':self.turn_on},
                {'Name':'Turn On (75%)', 'Fcn':lambda event: self.turn_on(75)},
                {'Name':'Turn On (50%)', 'Fcn':lambda event: self.turn_on(50)},
                {'Name':'Turn On (25%)', 'Fcn':lambda event: self.turn_on(25)},
                {'Name':'Turn Off', 'Fcn':self.turn_off},
                {'Name':'Remove Device', 'Fcn':lambda event: host._remove_device(self)}]

    def ramp_on(self, time=10., level=100):
        raise NotImplemented
    
    def ramp_off(self, time=10., level=100):
        raise NotImplemented
        
    def state_str(self):
        return '%s (%d%%)' % self.state
        
        
        

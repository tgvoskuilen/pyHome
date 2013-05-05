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

import xml.etree.ElementTree as ET

from datetime import datetime
from device import Device

class OpenSensor(Device):
    """
    Interface for an open/close state sensor
    
    .. warning:: This class is abstract. Always implement one of its subclasses
    
    """
    
    state_icons = ['Closed','Open','Waiting']
    
    def __init__(self, house, xml):
        Device.__init__(self, house, xml)
        self.last_open_time = None
        self.state = ('Closed',0.)
        
        try:
            self.off_time = float(xml.find("timeout").text)
        except AttributeError:
            timeout = ET.SubElement(self.xml, "timeout")
            timeout.text = "60"
            self.off_time = 60.        

    
    def get_context_menu(self, host):
        return [{'Name':self.name+' - '+self.room, 
                    'Fcn':lambda event: host._show_info(self)},
                {'Name':'Edit timeout', 
                    'Fcn':lambda event: host._edit_timeout(self)},
                {'Name':'Remove Device', 
                    'Fcn':lambda event: host._remove_device(self)}]
                
                
    def set_state(self, new_state):
        if (self.state[0] == 'Closed' or self.state[0] == 'Waiting')    \
             and new_state[0] == 'Open':
             
                
            ns = (new_state[0], self.off_time)
            self.last_open_time = None
            Device.set_state(self, ns)
            
        elif self.state[0] == 'Open' and new_state[0] == 'Closed':
            ns = ('Waiting', self.off_time)
            self.last_open_time = datetime.now()
            Device.set_state(self, ns)

    
    def state_str(self):
        return '%s (%3.0f s)' % self.state
        
    def update(self):
        if self.state[0] == 'Waiting' and self.last_open_time is not None:
            elapsed = datetime.now() - self.last_open_time
            remaining = self.off_time - elapsed.total_seconds()
            if remaining > 0.:
                self.state = ('Waiting', remaining)
            else:
                self.state = ('Off', 0.)
                self.last_open_time = None
    
    
    def activity(self):
        return self.state[1] > 0.
    
    
    def toggle(self):
        """
        Artificially toggle state, mainly for debugging purposes
        """
        if self.state[0] == 'Closed':
            self.state = ('Open', self.off_time)
        else:
            self.state = ('Closed', 0.)

    
    def save(self):
        """ Save device into XML file """
        self.lock.acquire()
        try:
            self.xml.set("name",self.name)
            self.xml.set("room",self.room)
            self.xml.set("type",self.type)
            self.xml.find("address").text = ":".join([str(x) for x in self.address])
            if self.pos is not None:
                self.xml.find("pos").text = " ".join([str(x) for x in self.pos])
            self.xml.find("icon").text = self.icon
            self.xml.find("timeout").text = str(self.off_time)

        finally:
            self.lock.release()
            
        self.house.save_devices()
    

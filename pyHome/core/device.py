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

import threading

class Device(object):
    """
    This can be any home automation device.
    Devices can generate Jobs to send to the PLM.
    Each device is given a unique tag with id().
    Each device also has a thread lock, which must be called by its methods
    before running if the method modifies the device in any way.
    """
    def __init__(self, house, xml):
        """ Initialize a device in a house from its xml entry """
        self.tag = id(self)           # Unique device id number
        self.house = house
        self.xml = xml
        self.state = ('Off',0)        # States are tuples of state and level
        self.lock = threading.Lock()  # Device thread lock
        
        # Load settings from XML file
        self.name = xml.get("name")   # Device name
        self.room = xml.get("room")   # Device room
        self.type = xml.get("type")   # Device type
        self.address = [int(x) for x in xml.find("address").text.split(":")]

        self.pos = xml.find("pos").text
        if self.pos is not None:
            self.pos = [int(x) for x in self.pos.split(" ")]
            
        self.icon = xml.find("icon").text

    def sorting_name(self):
        return self.room+' '+self.name
        
    def col_strings(self):
        """
        Get strings to show in ListCtrl row for this device
        """
        return [self.name, self.room, 
                ":".join(['%02X' % x for x in self.address]), self.state_str()]
                

    def get_context_menu(self, host):
        raise NotImplemented
        
        
    def set_state(self, new_state):
        """ 
        Set the device state. Locked for thread safety, although
        currently only the House class changes device states.
        """
        self.state = new_state

    def update(self):
        """ Update device timers or states """
        pass   
            
    def send(self, msg):
        """ Put a message in the house's PLM's send queue """
        self.house.PLM.send_queue.put( msg )
        
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
            
        finally:
            self.lock.release()
            
        self.house.save_devices()
        

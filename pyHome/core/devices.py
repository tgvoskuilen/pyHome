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

import Queue
import threading

###############################################################################
class BaseDevice(object):
    """
    .. warning:: This class is abstract. Always implement one of its subclasses
    
    This can be any home automation device.
    Devices can generate Jobs to send to the PLM.
    Each device is given a unique tag with id().
    Each device also has a thread lock, which must be called by its methods
    before running if the method modifies the device in any way.
    """
    def __init__(self, name, address):
        """ Initialize a device with its address. """
        self.tag = id(self)           # Unique device id number
        self.name = name              # Device name (used in room dictionary)
        self.address = address        # Address byte list ([0x18,0xFF,0x00])
        self.state = ('Off',0)        # States are tuples of state and level
        self.lock = threading.Lock()  # Device thread lock


    def set_state(self):
        """
        .. warning:: This method is not implemented in the base class.
        
        This sets the device state based on an incoming message state.
        
        """
        raise NotImplemented

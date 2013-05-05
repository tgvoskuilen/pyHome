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

import time

class Message(object):
    """
    This general message class is essentially a list of bytes, with several 
    protocol-specific methods implemented on it when one of its subclasses is
    created.
    """
    def __init__(self, data=None):
        if data is None:
            self._data = []
        else:
            self._data = data


    def __str__(self):
        """ Print the bytes nicely in hex format separated by ':'s """
        return ":".join(['%02X' % x for x in self._data])

    def clear(self):
        """ Clears the data list in the message. """
        self._data = []

    def add_byte(self, newbyte):
        """ Adds a new byte to the end of the byte list. """
        self._data.append(newbyte)
        
    def matches(self, other):
        """
        Checks if two messages match. This is not the same as __eq__ since this
        allows wildcards (a -1 is a byte wildcard). The messages must still be
        the same length.
        """
        return ( all([i==j or i<0 or j<0 for i, j in zip(self._data, other._data)])
                 and len(self._data) == len(other._data) )
        
    def get_byte_string(self):
        """
        Get the message data in raw byte string format, for serial.write()
        """
        return "".join(['%02X' % i for i in self._data]).decode('hex')
        

    def is_complete(self):
        """
        .. warning:: This method is not implemented in the base class.
        
        Bytes are added to messages 1 at a time, and is_complete() is used by 
        the PLM to tell when the message has gotten all of its expected bytes.
        """
        raise NotImplemented

    def process(self, house):
        """
        .. warning:: This method is not implemented in the base class.
        
        Sends an appropriate action to the house
        """
        raise NotImplemented



    





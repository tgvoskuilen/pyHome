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

#############################################################################################
# General message class
class BaseMessage(object):
    """
    This general message class is essentially a list of bytes, with several protocol-specific
    methods implemented on it when one of its subclasses is created.
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

        


#############################################################################################
class Rule(object):
    """
    Rules are kept by the House, and dictate periodic or programmatically determined actions.
    Rules could be pre-defined in the main python script, or sent in by a client.
    
    Inputs:
     * *room* - This is a required string, either the name of a room in the House,
       or the word 'House' to call house-level methods
     * *device* - This call is required unless *room* = 'House'. It is the name
       of the device in *room* to call methods on
     * *commands* - This is a required list of Python string commands to be executed
       if condition() = True.
     * *condition* - This is a Python boolean string to set when to do the rule commands
     * *persist* - This is a Python boolean string to determine how long to keep
       the rule
       
    For convenience, condition() and persist() have the current hour (HH) and 
    minute (MM) available for comparisons.
       
    Example use:
     
    >>> Rule(room='Office', device='Desk Lamp', condition="HH+':'+MM == '08:30'", persist='True')
    
    """
    def __init__(self, room, commands, condition='True', persist='False', device=None):
        self.rule_id = id(self)
        self._room = room
        self._device = device
        self._commands = commands
        self._cond_str = condition
        self._persist_str = persist
        
        #: This is the total number of times this rule has been called. This can
        #: be used in the persist function to remove a rule after a certain
        #: number of executions.
        self.calls = 0
        
        #: Last call time is the epoch time (from time.time()) when this rule's
        #: action was last executed.
        self.last_call_time = 0


    def associate(self, house):
        """
        Associate the rule with the house and locate its implementer device.
        """
        self.house = house
        try:
            if self._room != 'House':
                self.device = house.db[self._room][self._device]
            else:
                self.device = self.house
        except KeyError:
            print "Error: Rule could not find an implementer", str(self._room), str(self._device)
            self.device = None


    def action(self):
        """ Action to perform if self.condition() is True """
        returns = []
        for command in self._commands:
            #try:
                returns.append(eval(command))
            #except: #TODO Shouldn't except without specifying a type or indicating what the error is
            #    print "Error: Could not execute rule action:", command, str(self.device)
                
        self.calls += 1
        self.last_call_time = time.time()
        return returns


    def condition(self):
        """
        Condition when the rule should be executed 
        This commonly involves time, so HH and MM are available.
        """
        HH = str(time.localtime().tm_hour)
        MM = str(time.localtime().tm_min)
        return eval(self._cond_str)


    def persist(self):
        """ Lifetime of the rule """
        HH = str(time.localtime().tm_hour)
        MM = str(time.localtime().tm_min)
        return eval(self._persist_str)


#############################################################################################
class Command(object):
    """
    Commands are sent in by clients (that is their only source). Unlike rules, they are
    executed immediately by directly calling device methods (e.g. 'TurnOn'). The value
    returned by the device method is then returned to the client.

    This means if a device has problems executing the command, this may block for awhile
    until the job times out.
    """
    pass









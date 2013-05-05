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

import copy
import pyHome.core


class Message(pyHome.core.Message):
    """
    This subclass creates an Insteon message to send to an InsteonPLM.

    The relationships used in this class are specific
    to the Insteon PLMs (and only tested on the 2413U so far)
    """
    def __init__(self, data=None):
        pyHome.core.Message.__init__(self, data)

        # Motion sensor command info
        # http://www.fancygaphtrn.com/home-automation/insteon/13627
        
        # What can be in command byte 1, and how to process byte 2, if applicable
        # http://www.madreporite.com/insteon/commands.htm
        self._InsteonCommands = {0x11:{'State':'On', 'Default':100, 
                                       'Fcn':lambda x: int(round(x/2.55))},
                                 0x12:{'State':'On', 'Default':100, 
                                       'Fcn':lambda x: int(round(x/2.55))},
                                 0x13:{'State':'Off','Default':0},
                                 0x14:{'State':'Off','Default':0},
                                 0x2E:{'State':'On', 'Default':100, 
                                       'Fcn':lambda x: int((x >> 4)/15.*100)},
                                 0x2F:{'State':'Off','Default':0}}
                                 

        # Parse the 2nd byte to get the command type, length, and callback
        self._InsteonCommandTypes = \
            {0x50:{'Name':'Insteon Standard Received', 'Length':11,
                   'Callback':self.__process_insteon_std_recv},
             0x51:{'Name':'Insteon Extended Received', 'Length':25,
                   'Callback':self.__ignore},
             0x52:{'Name':'X10 Received',              'Length':4, 
                   'Callback':self.__ignore},
             0x53:{'Name':'All-Link Complete',         'Length':10,
                   'Callback':self.__ignore},
             0x54:{'Name':'Button Event Report',       'Length':3, 
                   'Callback':self.__ignore},
             0x55:{'Name':'User Reset Detected',       'Length':2, 
                   'Callback':self.__ignore},
             0x56:{'Name':'All-Link Cleanup Failure',  'Length':7, 
                   'Callback':self.__ignore},
             0x57:{'Name':'All-Link Record Response',  'Length':10,
                   'Callback':self.__ignore},
             0x58:{'Name':'All-Link Cleanup Report',   'Length':3, 
                   'Callback':self.__ignore},
             0x60:{'Name':'Get IM Info',               'Length':9, 
                   'Callback':self.__ignore},
             0x61:{'Name':'Send All-Link Command',     'Length':6, 
                   'Callback':self.__ignore},
             0x62:{'Name':'Send Insteon Message',      'Length':9, 
                   'Callback':self.__process_insteon_cmd_echo},
             0x63:{'Name':'Send X10 Message',          'Length':5, 
                   'Callback':self.__ignore},
             0x64:{'Name':'Start All-Linking',         'Length':5, 
                   'Callback':self.__ignore},
             0x65:{'Name':'Cancel All-Linking',        'Length':3, 
                   'Callback':self.__ignore},
             0x66:{'Name':'Set Host Device Category',  'Length':6, 
                   'Callback':self.__ignore},
             0x67:{'Name':'Reset IM',                  'Length':3, 
                   'Callback':self.__ignore},
             0x68:{'Name':'Set Insteon ACK Byte',      'Length':4, 
                   'Callback':self.__ignore},
             0x69:{'Name':'Get First All-Link Record', 'Length':3, 
                   'Callback':self.__ignore},
             0x6A:{'Name':'Get Next All-Link Record',  'Length':3, 
                   'Callback':self.__ignore},
             0x6B:{'Name':'Set IM Configuration',      'Length':4, 
                   'Callback':self.__ignore},
             0x6C:{'Name':'Get All-Link Rec for Sndr', 'Length':3, 
                   'Callback':self.__ignore},
             0x6D:{'Name':'LED On',                    'Length':3, 
                   'Callback':self.__ignore},
             0x6E:{'Name':'LED Off',                   'Length':3, 
                   'Callback':self.__ignore},
             0x6F:{'Name':'Manage All-Link Record',    'Length':12,
                   'Callback':self.__ignore},
             0x70:{'Name':'Set Insteon NAK Byte',      'Length':4, 
                   'Callback':self.__ignore},
             0x71:{'Name':'Set Insteon ACK Two Bytes', 'Length':5, 
                   'Callback':self.__ignore},
             0x72:{'Name':'RF Sleep',                  'Length':3, 
                   'Callback':self.__ignore},
             0x73:{'Name':'Get IM Configuration',      'Length':6, 
                   'Callback':self.__ignore}}


    def process(self, house):
        """ Locate the processor for this message and call it """
        try:
            self._InsteonCommandTypes[self._data[1]]['Callback'](house)
        except (IndexError, KeyError):
            print "Unable to process message:", self


    def __ignore(self, house):
        """ Graveyard for unsupported message types """
        print "Ignoring:", self


    def __process_insteon_cmd_echo(self, house):
        """ Do nothing with echo messages """
        print "Got echo:", self
        
    
    def __process_insteon_std_recv(self, house):
        """
        Process 0x50 messages received by the PLM.
        
        This is the most common type of message, and is usually in response
        to a change in a physical device state.
        
        """
        # Parse message flag byte
        msg_flag = self._data[8]
        
        is_broadcast = msg_flag & 1<<7 == 1<<7
        is_ack_direct = msg_flag & 1<<5 == 1<<5
        
        # Get sender address and global type
        self.sender = self._data[2:5]
        self.type = 'Direct' if not is_broadcast else 'Broadcast'
        
        print "Msg:", self
        print "Broadcast:", is_broadcast
        print "Ack direct:", is_ack_direct

        # Parse message command
        cmd = self._data[9:11]
        try:
            newstate = self._InsteonCommands[cmd[0]]['State']
            
            if self._InsteonCommands[cmd[0]].has_key('Fcn') and is_ack_direct:
                newlevel = self._InsteonCommands[cmd[0]]['Fcn'](cmd[1])
            else:
                newlevel = self._InsteonCommands[cmd[0]]['Default']

            self.state = (newstate, newlevel)

            # Add to event_queue
            house.event_queue.put(copy.deepcopy(self))
        
        except KeyError:
            print "Insteon key error with command '%02X' not found" % cmd[0]
            print "  Entire message is:", self
            print "  Type is:", self.type
            print "  Sender is:", self.sender
            print "  Command is:", cmd




    def is_complete(self):
        """ 
        Check if the message is complete. This checks that it is the proper
        length and that it is not corrupted.
        """
        # If the message is corrupted, attempt to repair it then
        # check again to see if it is complete.
        if self._is_corrupted():
            print "Attempting to repair corrupted message", self
            self._repair()
            return self.is_complete()
            
        try:
            target_length = -1
            
            #Check for a NAK - If it's a NAK we can stop here
            if self._data == [0x15]:
                return True

            #The message length is defined by the code in Byte 2
            target_length = self._InsteonCommandTypes[self._data[1]]['Length']

            #The one exception is 0x62, which can be standard or extended length
            if self._data[1] == 0x62:
                if self._data[5] & 1<<4 == 1<<4: # Bit 4 == 1?
                    target_length = 23      # Catch extended messages echoed from 0x62 message types
                    
            return len(self._data) == target_length
        
        except IndexError:
            return False


    def _is_corrupted(self):
        """
        This checks if a message is corrupted based on the following criteria:
         1. If it has more than 25 bytes (largest Insteon message size)
         2. If its first 2 bytes are not a recognized combination
         3. If its first byte is not 0x02 or 0x15
        """
        if len(self._data) > 25: # Largest expected message size is 25 bytes
            return True

        elif len(self._data) > 1: # If it has 2 or more bytes, they should form this pattern
            return not (self._data[0] == 0x02 and self._InsteonCommandTypes.has_key(self._data[1]))

        elif len(self._data) > 0: # If it has only 1 byte, it must be 0x02 or 0x15
            return not (self._data[0] == 0x02 or self._data[0] == 0x15)

        else:
            return False # It can't be corrupted if it has no entries
        
    
    def _repair(self):
        """
        The message repair function starts removing entries from the front of corrupted
        messages which do not start with 0x02. It repeats this until either the message is
        erased, or begins with a valid two-byte combination (0x02 and a valid type byte).
        This method will discard any NAK messages that showed up too, but I don't know how
        else to distinguish a NAK from an 0x15 in the middle of another message.
        """
        while len(self._data) > 0:
            if self._data[0] != 0x02:
                self._data.pop(0)
            else:
                break

        if len(self._data) > 1:
            if not self._InsteonCommandTypes.has_key(self._data[1]):
                self._data.pop(0)
                self._repair()

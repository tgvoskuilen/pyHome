
import copy
import time
import serial
import threading
import Queue

# Import pyHome core classes to derive Insteon specific subclasses from
from pyHome.core.messages import BaseMessage
from pyHome.core.devices import BaseDevice
from pyHome.core.plugins import BasePLM
from pyHome.globals import *

#############################################################################################
class Message(BaseMessage):
    """
    This subclass creates an Insteon message to send to an InsteonPLM.

    The relationships used in this class are specific
    to the Insteon PLMs (and only tested on the 2413U so far)
    """
    def __init__(self, data=None):
        BaseMessage.__init__(self, data)

        # What can be in command byte 1, and how to process byte 2, if applicable
        self._InsteonCommands = {0x11:{'State':'On', 'Default':100, 'Fcn':lambda x: int(round(x/2.55))},
                                 0x12:{'State':'On', 'Default':100, 'Fcn':lambda x: int(round(x/2.55))},
                                 0x13:{'State':'Off','Default':0},
                                 0x14:{'State':'Off','Default':0},
                                 0x2E:{'State':'On', 'Default':100, 'Fcn':lambda x: int((x >> 4) / 15. * 100)},
                                 0x2F:{'State':'Off','Default':0}}

        # How to tranlate Insteon message types to global message types
        self._InsteonMessageTypes = {0:('P2P Direct Message',EVENT_TYPE_DIRECT),
                                     1:('ACK of Direct Message',EVENT_TYPE_DIRECT),
                                     2:('Group Cleanup Direct Message',EVENT_TYPE_DIRECT),
                                     3:('ACK of Group Cleanup Direct Message',EVENT_TYPE_DIRECT),
                                     4:('Broadcast message',EVENT_TYPE_BROADCAST),
                                     5:('NAK of Direct Message',EVENT_TYPE_NAK),
                                     6:('Group Broadcast Message',EVENT_TYPE_BROADCAST),
                                     7:('NAK of Group Cleanup Direct Message',EVENT_TYPE_BROADCAST)}

        # Parse the 2nd byte to get the command type, length, and callback
        self._InsteonCommandTypes = {0x50:{'Name':'Insteon Standard Received', 'Length':11,
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
                                           'Callback':self.__ignore},
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
        try:
            self._InsteonCommandTypes[self._data[1]]['Callback'](house)
        except IndexError, KeyError:
            pass


    def __ignore(self, house):
        pass


    def __process_insteon_std_recv(self, house):
        # Get sender address and global type
        self.sender = self._data[2:5]
        self.type = self._InsteonMessageTypes[self._data[8] >> 5][1]

        # Parse message command
        cmd = self._data[9:11]
        newstate = self._InsteonCommands[cmd[0]]['State']

        if self._InsteonCommands[cmd[0]].has_key('Fcn') and self._data[8] & 1<<5 == 1<<5:
            newlevel = self._InsteonCommands[cmd[0]]['Fcn'](cmd[1])
        else:
            newlevel = self._InsteonCommands[cmd[0]]['Default']

        self.state = (newstate, newlevel)

        # Add to event_queue
        house.event_queue.put(copy.deepcopy(self))


    def is_complete(self):
        """ 
        Check if the message is complete. This checks that it is the proper length,
        and that it is not corrupted.
        """
        # If the message is corrupted, attempt to repair it then
        # check again to see if it is complete.
        if self._is_corrupted():
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



#############################################################################################
#
# This is the class for an Insteon light switch (dimmer)
#
class Dimmer(BaseDevice):
    def __init__(self, name, address):
        BaseDevice.__init__(self, name, address)
        self._InsteonRates = [480., 360., 270., 210., 150., 90., 47., 38.5, 
                              32., 28., 23.5, 19., 6.5, 2., 0.3, 0.1]
        

    def get_context_menu_items(self):
        return [{'Name':'Turn On (100%)', 'Fcn':lambda event: self.turn_on()},
                {'Name':'Turn On (75%)', 'Fcn':lambda event: self.turn_on(75)},
                {'Name':'Turn On (50%)', 'Fcn':lambda event: self.turn_on(50)},
                {'Name':'Turn On (25%)', 'Fcn':lambda event: self.turn_on(25)},
                {'Name':'Turn Off','Fcn':lambda event: self.turn_off()}]


    def set_state(self, new_state):
        self.lock.acquire()
        try:
            self.state = new_state
        finally:
            self.lock.release()


    def get_state(self):
        return self.state


    def toggle(self):
        if self.state[0] == 'On':
            self.turn_off()
        else:
            self.turn_on()


    def turn_on(self, level=100, fast=False):
        cmd1 = 0x12 if fast else 0x11
        cmd2 = int(round(level * 2.55))
        msg = Message([0x02,0x62]+self.address+[0x0F,cmd1,cmd2])
        self.house.PLM.send_queue.put( msg )


    def turn_off(self, fast=False):
        cmd1 = 0x14 if fast else 0x13
        msg = Message([0x02,0x62]+self.address+[0x0F,cmd1,0xFF])
        self.house.PLM.send_queue.put( msg )
            
            
    def ramp_on(self, time=10., level=100):
        # http://www.madreporite.com/insteon/ramprate.htm
        # byte = 1 1 1 1   1 1 0 0
        #       | level | rate code |

        #Coerce inputs
        level = min(max(0,level),100)
        time = min(max(0.1,time),480)

        #Find nearest rate code
        rate_code = min((n,i) for i, n in enumerate([abs(time-x) for x in self._InsteonRates]))[1]

        cmd = (int(round(level / 100. * 15)) << 4) + rate_code
        msg = Message([0x02,0x62]+self.address+[0x0F,0x2E,cmd])
        self.house.PLM.send_queue.put( msg )

      
    def ramp_off(self, time=10.):
        #Coerce inputs
        time = min(max(0.1,time),480)

        #Find nearest rate code
        rate_code = min((n,i) for i, n in enumerate([abs(time-x) for x in self._InsteonRates]))[1]

        msg = Message([0x02,0x62]+self.address+[0x0F,0x2F,rate_code])
        self.house.PLM.send_queue.put( msg )

            


#############################################################################################
# PLM interface class
class PLM(BasePLM):
    def __init__(self, usbport, baud=19200, timeout=0):
        BasePLM.__init__(self)
        self._message = Message()
        self._serialport = serial.Serial(usbport, baud, timeout=timeout)
        
    def run(self):
        while self.running:
            # Send new messages
            while not self.send_queue.empty():
                newmsg = self.send_queue.get(False)
                self._serialport.write( newmsg.get_byte_string() )
                
            # Then check for incoming messages at the serial port
            while self._serialport.inWaiting() > 0: # Read until there are no more bytes at the port
                data = self._serialport.read()      # Read 1 byte from the serial port
                self._message.add_byte(ord(data))   # Add it to the current message

                if self._message.is_complete():     # If the message is complete, process it
                    self._message.process(self.house)                
                    self._message.clear()

            time.sleep(0.005)

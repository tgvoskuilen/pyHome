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
import time
import threading

from pyHome.globals import *

###############################################################################
class House(object):
    """
    The House class is the main controller in pyHome.
    It contains all the devices and the interface to the home automation system.
    It also runs a server to accept commands from pyHome clients.
    
    :param PLM: A PLM derived from :class:`threading.Thread()`
    :param server: A server class
    :param GUI: An observer GUI class derived from :class:`threading.Thread()`
     
    """
    def __init__(self, PLM=None, server=None, GUI=None):
        """
        The house should be initialized with at least a PLM. A house without
        a PLM is somewhat useless.
        """
        
        self.PLM = PLM
        
        if PLM is not None:
            self.PLM.house = self
           
        self.GUI = GUI
        
        if GUI is not None:
            self.GUI.house = self
 
        self.server = server
        
        if server is not None:
            self.server.house = self
            
        self.rule_queue = Queue.Queue()
        self.event_queue = Queue.Queue()

        self.active_rules = []
        self.db = {}
        self.lock = threading.Lock()
       

    def activate(self):
        """
        Once the house is configured, call activate to start all the component
        threads. This will continue running until the program receives a kill
        command from a client or GUI, or a local Ctrl+C.

        **Events**:
         * Events are added to the event_queue using put()
         * A string event 'Kill' stops the program
         * All other events must have the following attributes defined:
         
           * *type* - Gets the event type (defined in globals.py)
           * *sender* - Return the 3-byte address (list) of the sending device
           * *state* - Return the information in the event message


        **Rules**:
         * Rules are added to the rule_queue using put()
         * All rules must have the following methods and attributes defined:
         
           * condition() - Returns a boolean to indicate when to execute the rule
           * last_call_time - Time the rule was last executed, in epoch time
           * action() - Performs an action by calling house or device methods, returns nothing
           * persist() - Returns a boolean of whether to keep the rule after action() is called
           * rule_id - Return the rule's unique integer id

        """
        # Start the PLM and server threads
        if self.PLM is not None:
            self.PLM.start()
            
        if self.server is not None:
            self.server.start()

        if self.GUI is not None:
            self.GUI.start()    

        self.running = True

        # Start main loop
        self.start_time = time.time()
        while self.running:
            # Check for new rules in the queue to add to active_rules
            while not self.rule_queue.empty():
                self.active_rules.append(self.rule_queue.get(False))
                self.active_rules[-1].associate(self)

            # Check for new messages in the event queue and apply them
            while not self.event_queue.empty():
                event = self.event_queue.get(False)

                # Check for kill messages (just the string 'Kill')
                if event == EVENT_TYPE_KILL:
                    self.running = False

                    if self.server is not None:
                        self.server.running = False

                    if self.PLM is not None:
                        self.PLM.running = False

                    break

                # Only try to match direct messages (ignore broadcasts)
                try:
                    if event.type == EVENT_TYPE_DIRECT:
                        for room in self.db:
                            for device in self.db[room]:
                                if event.sender == self.db[room][device].address:
                                    match = self.db[room][device]

                        match.set_state(event.state)
  
                except AttributeError, NameError:
                    print "Error: Event could not be matched:", str(event)

            # Check the Rules in the list
            for rule in self.active_rules:
                if rule.condition() and time.time() - rule.last_call_time > 0.5:
                    print "Performing action for rule", rule.rule_id
                    rule.action()

                    if not rule.persist():
                        print "Deleting rule", rule.rule_id, "from the active rule list"
                        self.active_rules.remove(rule)


            # Insteon devices take about 0.3 seconds to respond and change.
            time.sleep(0.1)
            

    def get_devices(self):
        """
        Get the house device dictionary, with extra formatting.

        This requires devices to have the following methods or attributes
         * tag - Unique integer device tag
         * address - Three-byte list
         * state - Tuple of current state

        """
        devs = []
        self.lock.acquire()
        try:
            for room in self.db:
                for device in self.db[room]:
                    devs.append({'Tag':self.db[room][device].tag,
                                 'Device Name':device,
                                 'Room':room,
                                 'Address':":".join(['%02X' % x for x in self.db[room][device].address]),
                                 'State':'%s (%d%%)' % self.db[room][device].state}) 
                                                        #TODO - Give device a "get_state_str()" function
        finally:
            self.lock.release()

        return devs


    def add_room(self, room):
        """
        Add a new room (an organizational unit) to the house.
        Devices can only be added to rooms. The room is specified
        by a string (its name).
        """
        self.lock.acquire()
        try:
            self.db[room] = {}
        finally:
            self.lock.release()


    def add_device(self, room, device):
        """
        TODO: Check that device is based on BaseDevice class
        
        Add a device to a room. If the specified room does not
        exist, it will be added automatically. The room is specified
        by a string (its name) and the device is an instance of a subclass of
        the BaseDevice class.

        This requires that the device have the attribute 'name' defined
        """
        self.lock.acquire()
        try:
            device.house = self
            try:
                self.db[room][device.name] = device
            except KeyError:
                self.db[room] = {}
                self.db[room][device.name] = device
        finally:
            self.lock.release()


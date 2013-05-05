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
import os
import xml.etree.ElementTree as ET


import pyHome.advancedGUI as GUI
#from pyHome import Insteon

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
    def __init__(self, usbport=None):
        """
        Initialize the house with the USB port it should look for the PLM on.
        """
        
        # Load XML files
        self.dataFolder = 'UserData'
        configTree = ET.parse(os.path.join(self.dataFolder,'config.xml'))
        configRoot = configTree.getroot()
        
        self.floorPlanFile = configRoot.findall("floorplan")[0].get("file")
        print "Floorplan file = ", self.floorPlanFile
        
        deviceTypes = {"Insteon Dimmer": Insteon.Dimmer}


        devTree = ET.parse(os.path.join(self.dataFolder,'devices.xml'))
        devRoot = devTree.getroot()
        
        self.devices = []
        self.rooms = []
        for dev in devRoot.findall("device"):
            name = dev.get("name")
            room = dev.get("room")
            addr = [int(x) for x in dev.find("address").text.split(":")]
            
            pos = dev.find("pos").text
            if pos is not None:
                pos = [int(x) for x in pos.split(" ")]
            
            self.devices.append(   \
                 deviceTypes[dev.get("type")](self, room, name, addr, pos))
            
            if room not in self.rooms:
                self.rooms.append(room)
            
            
        # Set up other objects
        self.PLM = Insteon.PLM(self, usbport)
           
        self.GUI = GUI.Thread(self)
        self.logger = self.GUI.log_event
 
        self.server = None #no server for now
        
        if server is not None:
            self.server.house = self
            
        self.rule_queue = Queue.Queue()
        self.event_queue = Queue.Queue()

        self.active_rules = []
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

        time.sleep(0.5)

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
                if event == 'Kill':
                    self.running = False

                    if self.server is not None:
                        self.server.running = False

                    if self.PLM is not None:
                        self.PLM.running = False

                    break

                # Only try to match direct messages (ignore broadcasts)
                try:
                    if event.type == 'Direct':
                        for device in self.devices:
                            if event.sender == device.address:
                                match = device
                                break

                        disp_str = '%s message from %s (%s) of state change to (%s, %s)' % \
                        (event.type, match.name, ":".join(['%02X' % x for x in event.sender]), \
                         event.state[0], event.state[1])
                        self.logger(disp_str)
                        match.set_state(event.state)
  
                except AttributeError, NameError:
                    self.logger("Error: Event could not be matched: "+str(event))

            # Check the Rules in the list
            for rule in self.active_rules:
                if rule.condition() and time.time() - rule.last_call_time > 0.5:
                    self.logger("Performing action for rule %s"
                                 % str(rule.rule_id))
                    rule.action()

                    if not rule.persist():
                        self.logger("Deleting rule "+str(rule.rule_id)
                                    +" from the active rule list")
                        self.active_rules.remove(rule)


            # Insteon devices take about 0.3 seconds to respond and change.
            time.sleep(0.05)
            
    def get_rooms(self):
        """
        Get the current list of rooms, with 'All Rooms' added in front
        """
        rooms = ['All Rooms']
        self.lock.acquire()
        try:
            for room in self.rooms:
                rooms.append(room)
        finally:
            self.lock.release()

        return rooms
        
    
    def get_devices(self, room=None):
        """
        Get a list of devices either in the whole house or a specific room
        """
        devs = []
        self.lock.acquire()
        try:
            if room is None or room == 'All Rooms':
                devs = self.devices
            else:
                for dev in self.devices:
                    if dev.room == room:
                        devs.append(dev) 
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
            self.rooms.append(room)
        finally:
            self.lock.release()


    def add_device(self, room, device):
        """
        Add a device to the house. If the specified room does not
        exist, it will be added automatically. The room is specified
        by a string (its name) and the device is an instance of a subclass of
        the BaseDevice class.
        """
        self.lock.acquire()
        try:
            device.house = self
            if room not in self.rooms:
                self.rooms.append(room)
            
            device.room = room
            self.devices.append(device)

        finally:
            self.lock.release()


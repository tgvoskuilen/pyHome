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
import sys
import re
import xml.etree.ElementTree as ET


import GUI
import Insteon
from core.macro import Macro


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
        self.lock = threading.Lock()
        
        # Load XML files
        self.dataFolder = 'UserData'
        self.iconFolder = os.path.join('pyHome','icons')
        self.configFile = os.path.join(self.dataFolder,'config.xml')
        self.devFile = os.path.join(self.dataFolder,'devices.xml')
        self.macroFile = os.path.join(self.dataFolder,'macros.xml')
        
        self.configTree = ET.parse(self.configFile)
        self.configRoot = self.configTree.getroot()
        
        self.floorplanFile = os.path.join(self.dataFolder,
            self.configRoot.find("floorplan").get("file"))
        self.programTitle = self.configRoot.find("program").get("title")

        self.windowSize = tuple([int(x) for x in   \
                self.configRoot.find("program").get("size").split("x")])



        self.deviceTypes = {"Insteon Dimmer": Insteon.Dimmer,
                            "Insteon Motion Sensor": Insteon.MotionSensor,
                            "Insteon Open/Close Sensor": Insteon.OpenSensor,
                            "Insteon Switch": Insteon.Switch}


        # Load devices from XML file
        self.devTree = ET.parse(self.devFile)
        self.devRoot = self.devTree.getroot()
                
        self.devices = {}
        
        for d in self.devRoot.findall("device"):
            room = d.get("room")
            if room not in self.devices:
                self.devices[room] = {}
				
            self.devices[room][d.get("name")] = \
                self.deviceTypes[d.get("type")](self, d)


        self.macros = {}
        
        self.macroTree = ET.parse(self.macroFile)
        self.macroRoot = self.macroTree.getroot()
        
        for m in self.macroRoot.findall("macro"):
            name = m.get("name")
            self.macros[name] = Macro(self, m)
        
        
        # Set up other objects
        self.PLM = Insteon.PLM(self, usbport)
           
        self.GUI = GUI.Thread(self)
        self.logger = self.GUI.log_event
 
        self.server = None #no server for now
        
        if self.server is not None:
            self.server.house = self
            
        self.event_queue = Queue.Queue()

        
    def get_icons(self, typeName):
        """
        Get the valid icon sets for typeName
        """
        states = self.deviceTypes[typeName].state_icons
        
        icons = [f for f in os.listdir(self.iconFolder) if f.endswith('.png')
                 and f != 'Unlocked.png']
        
        iconmap = {}
        titles = []
        for s in states:
            iconmap[s] = []
        
        for i in icons:
            name = os.path.splitext(i)[0]
            title,state = name.split('_')
            if state in states:
                iconmap[state].append(title)
                if title not in titles:
                    titles.append(title)
                
        final = []
        
        for t in titles:
            keep = True
            for s in states:
                if t not in iconmap[s]:
                    keep = False
            if keep:
                entry = {'File': os.path.join(self.iconFolder,t+'_'+states[0]+'.png'),'Name':t}
                final.append(entry)
                
        return final
        
       
    def set_new_floorplan(self, floorplanFile):
        newfloorplan = os.path.join(self.dataFolder,floorplanFile)
        if os.path.isfile(newfloorplan):
            self.floorplanFile = newfloorplan
            self.configRoot.findall("floorplan")[0].set("file",floorplanFile)
            self.configTree.write(self.configFile)
        else:
            self.logger("ERROR: Floorplan file does not exist in %s" \
                        % self.dataFolder)
    
    
    def save_devices(self):
        """ Save the device xml file """
        self.lock.acquire()
        try:
            self.devTree.write(self.devFile)
        finally:
            self.lock.release()
            
    def save_macros(self):
        """ Save the macros xml file """
        self.lock.acquire()
        try:
            self.macroTree.write(self.macroFile)
        finally:
            self.lock.release()
            
                  
    def activate(self):
        """
        Once the house is configured, call activate to start all the component
        threads. This will continue running until the program receives a kill
        command from a client or GUI, or a local Ctrl+C.

        """
        # Start the PLM and server threads
        self.PLM.start()
        self.GUI.start()
        
        if self.server is not None:
            self.server.start()

        time.sleep(0.5) #give everything time to get started

        self.running = True

        # Start main loop
        self.start_time = time.time()
        while self.running:
            #Update device states
            for dev in self.get_devices():
                dev.update()
                 
            #Run macros  
            for name, macro in self.macros.iteritems():
                if macro.active:
                    try:
                        exec(macro.code)
                    except Exception as e:
                        self.logger("Macro '%s' raised exception '%s'" % \
                                    (macro.name, repr(e)))
                        self.logger("Macro '%s' is now inactive" % macro.name)
                        macro.register_error(repr(e))
                

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
                        match = [d for d in self.get_devices() if d.address == event.sender][0]
                        disp_str = '%s message from %s (%s) of state change to (%s, %s)' % \
                        (event.type, match.name, ":".join(['%02X' % x for x in event.sender]), \
                         event.state[0], event.state[1])
                        self.logger(disp_str)
                        match.set_state(event.state)

                except (AttributeError, IndexError):
                    self.logger("Error: Event could not be matched: "+str(event))


            # Insteon devices take about 0.3 seconds to respond and change,
            # so this doesn't need to run at max speed.
            time.sleep(0.05)
            
            
    def get_rooms(self):
        """
        Get the current list of rooms, with 'All Rooms' added in front
        """
        self.lock.acquire()
        try:
            rooms = ['All Rooms']
            rooms.extend(self.devices.keys())
        finally:
            self.lock.release()
        return rooms
        
        
    def find_device(self, tag=None, roomAndName=None):
        """
        
        """
        if roomAndName is not None:
            try:
                return self.devices[roomAndName[0]][roomAndName[1]]
            except KeyError:
                print "Device not found"
        
        elif tag is not None:
            devList = [d for r in self.devices.itervalues()
                         for d in r.itervalues() if d.tag == tag]
            
            return devList[0]
    
    
    def find_macro(self, tag):
        """
        
        """
        return [m for m in self.macros.itervalues() if m.tag == tag][0]  
            
                
    def get_devices(self, room=None):
        """
        Get a list of devices either in the whole house or a specific room
        """
        devs = []
        self.lock.acquire()
        try:
            if room not in self.devices:
                devs = [d for r in self.devices.itervalues()
                          for d in r.itervalues()]
            else:
                devs = [d for d in self.devices[room].itervalues()]
        finally:
            self.lock.release()

        return devs
       
       
    def get_macros(self):
        """
        Get a list of the house macros
        """
        macs = []
        self.lock.acquire()
        try:
            macs = [m for m in self.macros.itervalues()]
        finally:
            self.lock.release()

        return macs
        
        
    def remove_device(self, device):
        """
        To remove a device, first remove it from the XML tree, then remove it
        from the device dictionary.
        """
        self.lock.acquire()
        device.lock.acquire() #device gets deleted, what happens to this lock?
        try:
            room = device.room
            self.devRoot.remove(device.xml)
            del self.devices[room][device.name]
            if not self.devices[room]:
                del self.devices[room]
        finally:
            self.lock.release()
        
        self.save_devices()

    def remove_macro(self, mac):
        """
        To remove a macro, first remove it from the XML tree, then remove it
        from the macro dictionary.
        """
        self.lock.acquire()
        try:
            self.macroRoot.remove(mac.xml)
            del self.macros[mac.name]
        finally:
            self.lock.release()
        
        self.save_macros()
        
        
    def edit_device(self, tag, inputDict):
        dev = self.find_device(tag=tag)
        
        if inputDict["Room"] == dev.room and inputDict["Name"] == dev.name:
            dev.address = inputDict["Address"]
            dev.icon = inputDict["Icon"]
            dev.save()
            
        else:
            currentRoom = dev.room
            currentName = dev.name
            if inputDict["Room"] not in self.devices:
                self.devices[inputDict["Room"]] = {}
                
            self.devices[inputDict["Room"]][inputDict["Name"]] = \
                self.devices[currentRoom][currentName]
                
            del self.devices[currentRoom][currentName]
            
            if not self.devices[currentRoom]:
                del self.devices[currentRoom]
                
            newdev = self.devices[inputDict["Room"]][inputDict["Name"]]
            newdev.name = inputDict["Name"]
            newdev.room = inputDict["Room"]
            newdev.address = inputDict["Address"]
            newdev.icon = inputDict["Icon"]
            newdev.save()
            
            
    def edit_macro(self, tag, inputDict):
        mac = self.find_macro(tag=tag)
        
        mac.name = inputDict["Name"]
        mac.description = inputDict["Description"]
        mac.code = inputDict["Code"]
        
        self.logger("Edited macro '%s'" % mac.name)
        if inputDict["Active"]:
            self.logger("Macro '%s' is now active" % mac.name)
        elif not inputDict["Active"] and mac.active:
            self.logger("Macro '%s' is now inactive" % mac.name)
            
        mac.active = inputDict["Active"]
        mac.save()
            
    
    def add_device(self, name, room, address, type, icon, pos=None):
        """
        Add a device to the house. If the specified room does not
        exist, it will be added automatically. The device is first added
        to the XML file, then the Device object is added to self.devices
        """
        print "Adding device ", name
        self.lock.acquire()
        print "got lock"
        try:
            if room not in self.devices:
                self.devices[room] = {}
            
            if name not in self.devices[room]:
                newdev = ET.SubElement(self.devRoot, "device")
                newdev.set("name",name)
                newdev.set("room",room)
                newdev.set("type",type)
                newdevA = ET.SubElement(newdev, "address")
                newdevA.text = ":".join([str(x) for x in address])
                newdevP = ET.SubElement(newdev, "pos")
                if pos is not None:
                    newdevP.text = " ".join([str(x) for x in pos])
                newdevI = ET.SubElement(newdev, "icon")
                newdevI.text = icon
                print "making device object"
                self.devices[room][name] = self.deviceTypes[type](self, newdev)
            else:
                raise ValueError("Duplicate device")

        finally:
            self.lock.release()
        print "saving devices"
        self.save_devices()
        
        
    def add_macro(self, name, desc, code, active):
        """
        Add a new macro
        """
        self.lock.acquire()
        try:
            if name not in self.macros:
                newmac = ET.SubElement(self.macroRoot, "macro")
                newmac.set("name",name)
                newmac.set("active",str(active))
                
                newmacD = ET.SubElement(newmac, "description")
                newmacD.text = desc
                
                newmacC = ET.SubElement(newmac, "code")
                newmacC.text = code
                
                self.macros[name] = Macro(self, newmac)
                
                self.logger("Created new macro '%s'" % name)
                if active:
                    self.logger("Macro '%s' is now active" % name)
                else:
                    self.logger("Macro '%s' is inactive" % name)
                    
            else:
                raise ValueError("Duplicate macro")

        finally:
            self.lock.release()
            
        self.save_macros()

# pyHome demonstration program
#  by Tyler Voskuilen
#
#  TODO:
#    * Write a client class
#    * Think about a client GUI design (wxPython, web, android?)
#    * Think about a server GUI design (wxPython)
#    * Compare with existing Insteon programs, get an edge
#    * Work on SSH or secure server
#
#
#    * Improve Sphinx documentation
#


import pyHome
from pyHome import Insteon
from pyHome import server
from pyHome import GUI

#Create house
house = pyHome.House(PLM=Insteon.PLM(usbport='/dev/ttyUSB0'),
                     server=server.TCPServer(ip='192.168.1.116', port=12345),
                     GUI=GUI.SimpleGUI())

#Add devices to rooms
house.add_device('Office', Insteon.Dimmer('Desk Lamp', [0x18, 0x8F, 0x00]) )

#Add some rules to the house
house.rule_queue.put( pyHome.Rule(room='Office',
                            device='Desk Lamp',
                            commands=['self.device.ramp_on()'],
                            condition="time.time() - self.last_call_time > 5",
                            persist="self.calls < 1"))

#house.AddRule( pyHome.Rule(room='Office',
#                           device='Desk Lamp',
#                           commands=['self.device.TurnOff()'],
#                           condition="self.device.state[0] == 'On'",
#                           persist="self.calls < 6"))

#Start the house
house.activate()


# pyHome demonstration program

import pyHome

#Create house
# You may need to change permissions on the USB port to run this
#   sudo chmod 0777 /dev/ttyUSB0
house = pyHome.House(usbport='/dev/ttyUSB0')

#Start the house
house.activate()


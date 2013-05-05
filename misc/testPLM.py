
# Basic python script to test if the PLM is responding properly


import serial
import time
       
usbport = '/dev/ttyUSB0'
baud = 19200
timeout = 5

sp = serial.Serial(usbport, baud, timeout=timeout)

# Send a status request
testmsg = [0x02, 0x19, 0x00]

sp.write( "".join(['%02X' % i for i in testmsg]).decode('hex') )

time.sleep(0.5)

# Then check for incoming messages at the serial port
while sp.inWaiting() > 0: # Read until there are no more bytes
    data = sp.read()      # Read 1 byte from the serial port
    print "rcv:", ord(data)       # Print the received byte

print "Goodbye"

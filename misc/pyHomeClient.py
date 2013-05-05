# This is a very simple example client that can send commands to pyHome
# Example commands would be methods of the Dimmer class, in this case:
#  turn_on
#  turn_off
#  ramp_on
#  toggle
#  etc...
#
# It doesn't work any more, but is a useful reference for now


import socket
import time
import pickle

host = '192.168.1.116' 
port = 12345

while True:
    s = socket.socket()         # Create a socket object
    command = raw_input('Enter a command to send: ')
    if command == 'x':
        s.close()
        break
    s.connect((host, port))

    mycommand = {'Room':'Office',
                 'Device':'Desk Lamp',
                 'Command':command,
                 'Args': {} }

    mydict_str = pickle.dumps(mycommand)
    s.send(mydict_str)

    data = s.recv(4096)
    print "Response:", data
    s.close                     # Close the socket when done

    

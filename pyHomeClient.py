import socket               # Import socket module
import time
import pickle

host = '192.168.1.116' # Get local machine name
port = 12345                # Reserve a port for your service.

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
    #s.send(command)

    data = s.recv(4096)
    print "Response:", data
    s.close                     # Close the socket when done

    

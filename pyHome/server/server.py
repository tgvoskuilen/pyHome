
import threading
import Queue
import socket
import pickle

from pyHome.core.plugins import BaseServer

#############################################################################################
# server communication interface
class TCPServer(BaseServer):
    """
    This starts and monitors a TCP server which can receive commands to call Device functions. The
    device itself handles generating the appropriate job (which is device specific) so this only needs
    to know the proper command (e.g. 'TurnOn')
    A command can be either house-level or device-level (so far)
    The command consists of the device name, command name, and arguments
    The return value of the appropriate function is returned to the client when the job finishes
    or times out.

    TODO: The server needs to be more robust with respect to wacky commands, and should have a defined
    interface with the House
    """
    def __init__(self, ip='127.0.0.1', port=12345):
        BaseServer.__init__(self, ip, port)


    def run(self):
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self.host, self.port))

        s.listen(5)
        while True:
            conn, addr = s.accept()
            #print "Got connection from", addr
            data_str = conn.recv(1024)
            data = pickle.loads(data_str)
            print "Received Command from ", addr
            #print "command", data_str
            result = self.CallDeviceFunction(data)
            if result is not None:
                conn.send('Done')
            else:
                conn.send('Failed')
            conn.close()


    def CallDeviceFunction(self, data):
        room_name = data['Room']
        device_name = data['Device']
        fcn_name = data['Command']
        fcn_args = data['Args']

        try:
            dev_command = getattr(self.house.db[room_name][device_name], fcn_name)
            return dev_command(**fcn_args)
        except (AttributeError, KeyError):
            return None


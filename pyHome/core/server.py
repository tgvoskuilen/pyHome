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

import threading
import Queue
import socket
import pickle

###############################################################################
# server communication interface
class TCPServer(threading.Thread):
    """
    This starts and monitors a TCP server which can receive commands to call 
    Device functions. The device itself handles generating the appropriate 
    job (which is device specific) so this only needs to know the proper 
    command (e.g. 'turn_on')
    
    A command can be either house-level or device-level (so far)
    The command consists of the device name, command name, and arguments
    The return value of the appropriate function is returned to the client 
    when the job finishes or times out.

    TODO: The server needs to be more robust with respect to wacky 
    commands, and should have a defined interface with the House
    """
    def __init__(self, ip='127.0.0.1', port=12345):
        threading.Thread.__init__(self)
        self._recv_queue = Queue.Queue()
        self._send_queue = Queue.Queue()
        self.host = ip
        self.port = port
        self.running = True
        self.setDaemon(True)
        self.house = None


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


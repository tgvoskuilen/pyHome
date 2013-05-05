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
import serial
import time
import Queue


class PLM(threading.Thread):
    """
    Provide an interface with the Insteon PLM. This is a dedicated PLM thread
    with a send_queue that other devices can add message to. Received messages
    are processed and passed on according to their type.
    """
    def __init__(self, house, usbport, baud=19200, timeout=0):
        threading.Thread.__init__(self)
        self.send_queue = Queue.Queue()
        self.running = True
        self.setDaemon(True)
        self.house = house
        self._serialport = serial.Serial(usbport, baud, timeout=timeout)
        
        
    def run(self):
        while self.running:
            # Send new messages
            while not self.send_queue.empty():
                newmsg = self.send_queue.get(False)
                self._serialport.write( newmsg.get_byte_string() )
                
            # Then check for incoming messages at the serial port
            try:
                while self._serialport.inWaiting() > 0: # Read until there are no more bytes at the port
                    data = self._serialport.read()      # Read 1 byte from the serial port
                    self._message.add_byte(ord(data))   # Add it to the current message

                    if self._message.is_complete():     # If the message is complete, process it
                        self._message.process(self.house)                
                        self._message.clear()
            except SerialException:
                print "Got serial exception"
                pass
                
            # Sleep a little to keep this from using too much of the CPU
            time.sleep(0.005)
            
            

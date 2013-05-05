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

from message import Message

import pyHome.core
from switch import Switch

class Dimmer(Switch, pyHome.core.Dimmer):
    def __init__(self, house, xml):
        pyHome.core.Dimmer.__init__(self, house, xml)
        self._InsteonRates = [480., 360., 270., 210., 150., 90., 47., 38.5, 
                              32., 28., 23.5, 19., 6.5, 2., 0.3, 0.1]
   
    def ramp_on(self, time=10., level=100):
        """ Ramp on in 'time' seconds (0.1-480) to level (0-100) """
        # http://www.madreporite.com/insteon/ramprate.htm
        # byte = 1 1 1 1   1 1 0 0
        #       | level | rate code |

        #Coerce inputs
        level = min(max(0,level),100)
        time = min(max(0.1,time),480)

        #Find nearest rate code
        rate_code = min((n,i) for i, n in    \
                       enumerate([abs(time-x) for x in self._InsteonRates]))[1]

        cmd = (int(round(level / 100. * 15)) << 4) + rate_code
        self.send( Message([0x02,0x62]+self.address+[0x0F,0x2E,cmd]) )

      
    def ramp_off(self, time=10.):
        """ Ramp off in 'time' seconds (0.1-480) """
        #Coerce inputs
        time = min(max(0.1,time),480)

        #Find nearest rate code
        rate_code = min((n,i) for i, n in enumerate([abs(time-x) \
                        for x in self._InsteonRates]))[1]

        self.send( Message([0x02,0x62]+self.address+[0x0F,0x2F,rate_code]) )


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


# Declare pyHome global variables

# Any event added to the house event_queue, with the exception of a 'Kill' message,
# should have a get_type() method which returns one of these event types
EVENT_TYPE_DIRECT = 'Direct Message'
EVENT_TYPE_BROADCAST = 'Broadcast Message'
EVENT_TYPE_UNKNOWN = 'Unknown'
EVENT_TYPE_NAK = 'NAK'
EVENT_TYPE_KILL = 'Kill'


# Device state globals 
# Lights have a tuple state: (STATE, LEVEL)
#  STATE is 'On' or 'Off', level is an integer from 0 to 100
LIGHT_STATE_ON = 'On'
LIGHT_STATE_OFF = 'Off'

# Motion detectors have a tuple state: (CONDITION, [detect time list])
# CONDITION is 'Active' or 'Inactive', detect time list is a list of the time at which the past 25 motions were detected, or something like that

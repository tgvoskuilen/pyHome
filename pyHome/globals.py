
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

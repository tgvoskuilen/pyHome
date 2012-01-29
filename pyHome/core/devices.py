
import Queue
import threading

###############################################################################
class BaseDevice(object):
    """
    .. warning:: This class is abstract. Always inmplement one of its subclasses
    
    This can be any home automation device.
    Devices can generate Jobs to send to the PLM.
    Each device is given a unique software tag with id().
    Each device also has a thread lock, which must be called by its methods
    before running. This ensures that a device cannot be simultaneously turned
    on and off by two different threads, for example.
    
    I'm a bit unclear as to
    whether this is necessary in Python, so better safe than sorry... Since
    many of the device calls block until something comes back into the queue,
    even if two simultaneous executions were possible, there would be no easy 
    way of knowing which queue response goes to which execution.
    """
    def __init__(self, name, address):
        """ Initialize a device with its address. """
        self.tag = id(self)           # Unique device id number
        self.name = name              # Device name (used in room dictionary)
        self.address = address        # Address byte list ([0x18,0xFF,0x00])
        #self.incoming = Queue.Queue() # Device message queue
        self.state = ('Off',0)        # States are tuples of state and level TODO - Not the case for non-lamps
        self.lock = threading.Lock()  # Device thread lock


    def set_state(self):
        """
        .. warning:: This method is not implemented in the base class.
        
        This sets the device state based on the output of get_payload() from
        the Message class.
        """
        raise NotImplemented

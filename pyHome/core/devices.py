
import Queue
import threading

###############################################################################
class BaseDevice(object):
    """
    .. warning:: This class is abstract. Always implement one of its subclasses
    
    This can be any home automation device.
    Devices can generate Jobs to send to the PLM.
    Each device is given a unique tag with id().
    Each device also has a thread lock, which must be called by its methods
    before running if the method modifies the device in any way.
    """
    def __init__(self, name, address):
        """ Initialize a device with its address. """
        self.tag = id(self)           # Unique device id number
        self.name = name              # Device name (used in room dictionary)
        self.address = address        # Address byte list ([0x18,0xFF,0x00])
        self.state = ('Off',0)        # States are tuples of state and level
        self.lock = threading.Lock()  # Device thread lock


    def set_state(self):
        """
        .. warning:: This method is not implemented in the base class.
        
        This sets the device state based on an incoming message state.
        
        """
        raise NotImplemented

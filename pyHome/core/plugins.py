

# Plugin parent classes
import threading
import Queue

#All plugins must be based on Plugin
class Plugin(threading.Thread):
    """
    Plugin is based on threading.Thread and sets up a Daemon thread process
    when Plugin.start() is called by the house.
    """
    def __init__(self):
        threading.Thread.__init__(self)
        self.running = True
        self.setDaemon(True)
        self.house = None
        
    def run(self):
        """
        .. warning:: This method is not implemented in the base class.
        """
        raise NotImplemented
        
        
# Base PLM class
# All PLMs must have:
#  - job_queue (for devices to put jobs into)
#
class BasePLM(Plugin):
    """
    Base class for PLMs (or any communication device between the computer
    and the home). The BasePLM is a Plugin with an active job list and a job
    queue that devices could send Jobs to.
    """
    def __init__(self):
        Plugin.__init__(self)
        self.send_queue = Queue.Queue()

        
        
# Server plugin parent class
# Server plugins must have X        
class BaseServer(Plugin):
    """
    The base server class is a Plugin with a send and recv queue, and ip
    address, and a port.
    
    It is currently incomplete.
    """
    def __init__(self, ip=None, port=None):
        Plugin.__init__(self)
        self._recv_queue = Queue.Queue()
        self._send_queue = Queue.Queue()
        self.host = ip
        self.port = port
    
    
# GUI Base class
# All GUI plugins must have X    
class BaseGUI(Plugin):
    """
    The base GUI is an observer GUI. It runs on a separate thread, so it can be
    stopped, or the pyHome core can be run without it. The GUI provides an
    interface to the House class, with the same functionality as is given to
    the server clients.
    """
    def __init__(self):
        Plugin.__init__(self)
        self.mainframe = None
        self.house = None
        self.update_freq = 100  # Update frequency in ms




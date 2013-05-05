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

import wx
import wx.lib.agw.flatnotebook as fnb

import time
import threading
import Queue
import panels

class MainFrame(wx.Frame):
    """
    The main frame holds the house reference and the top-level notebook
    """
    def __init__(self, parent):
        wx.Frame.__init__(self, None, wx.ID_ANY, parent.house.programTitle, 
                          size=parent.house.windowSize)
        self.parent = parent
        self.house = parent.house
        self.log_queue = self.parent.log_queue
        
        #store devices list, devices dict, or call on demand??
        self.devices = self.house.get_devices()

        #Create Menu bar and menus
        #self.topMenu = wx.MenuBar()
        #self.fileMenu = wx.Menu()

        #File Menu
        #self.fileMenu.AppendSeparator()
        #self.mQuit = self.fileMenu.Append(-1, '&Exit Program', 'Quit pyHome')

        #Add Menus to Menu Bar and create a status bar
        #self.topMenu.Append(self.fileMenu, '&File')
        #self.SetMenuBar(self.topMenu)

        self.Bind(wx.EVT_CLOSE, self._quit_program)
        #self.Bind(wx.EVT_MENU, self._quit_program, self.mQuit)


        self.Notebook = HouseNotebook(self)
        self.Notebook.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.Show()

        #Set up timer to update current panel
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._update_current_panel, self.timer)
        self.timer.Start(self.parent.update_freq)
        
        
    def _quit_program(self, event):
        self.house.event_queue.put('Kill')
        self.Destroy()
        
    def _update_current_panel(self, event):
        self.update()
        self.Notebook.GetCurrentPage().update()

    def update(self):
        self.devices = self.house.get_devices()


class HouseNotebook(fnb.FlatNotebook): #wx.Notebook):
    """
    My custom notebook class. This is where pages are organized and subpanels
    are called in.
    """
    #----------------------------------------------------------------------
    def __init__(self, parent):
        fnb.FlatNotebook.__init__(self, parent, id=wx.ID_ANY,
             agwStyle=fnb.FNB_NO_X_BUTTON|fnb.FNB_NO_NAV_BUTTONS|fnb.FNB_NODRAG|fnb.FNB_FF2)
                                  
        bgcolor = wx.Colour(240,240,240)
        self.SetTabAreaColour(bgcolor) 
        
        #Keep track of who the parent is
        self.parent = parent
        self.house = parent.house
        
        # Create panels
        self.panels = {"Floor Plan": panels.FloorPlan(self),
                       "Devices":    panels.Devices(self),
                       "Macros":     panels.Macros(self),
                       "Event Log":  panels.Log(self)}
        
        # Add panels
        self.AddPage(self.panels["Floor Plan"], "Floor Plan")
        self.AddPage(self.panels["Devices"], "Devices")
        self.AddPage(self.panels["Macros"], "Macros")
        self.AddPage(self.panels["Event Log"], "Event Log")
        


class Thread(threading.Thread):
    """
    This simple GUI shows a ListCtrl with all the devices in the House class.
    It shows and updates their status as they change.
    
    Future: Double clicking on an item toggles its state?
    """
    def __init__(self, house):
        threading.Thread.__init__(self)
        self.running = True
        self.setDaemon(True)
        self.mainframe = None
        self.house = house
        self.update_freq = 100  # Update frequency in ms
        self.log_queue = Queue.Queue()

    def run(self):
        app = wx.App(False)
        self.mainframe = MainFrame(self)
        self.mainframe.Show()
        app.MainLoop()

    def log_event(self, msg):
        timestr = time.strftime("%Y-%m-%d %H:%M:%S")
        text = """[%s] %s""" % (timestr, msg)
        self.log_queue.put(text)
        
        
###############################################################################



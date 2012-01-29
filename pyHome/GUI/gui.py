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
import threading

from panels import DevicePanel

## SimpleGUI ##################################################################

class SimpleFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, None, wx.ID_ANY, "Device Status", size=(500,300))
        self.parent = parent
        self.house = self.parent.house
        self.panel = DevicePanel(self)

        #Create Menu bar and menus
        self.topMenu = wx.MenuBar()
        self.fileMenu = wx.Menu()

        #File Menu
        self.mClose = self.fileMenu.Append(-1, '&Close GUI',
                                          'Close the GUI Window')

        self.fileMenu.AppendSeparator()
        self.mQuit = self.fileMenu.Append(-1, '&Exit Program', 'Quit pyHome')

        #Add Menus to Menu Bar and create a status bar
        self.topMenu.Append(self.fileMenu, '&File')
        self.SetMenuBar(self.topMenu)

        self.Bind(wx.EVT_CLOSE, self._quit_program)
        self.Bind(wx.EVT_MENU, self._close_gui, self.mClose)
        self.Bind(wx.EVT_MENU, self._quit_program, self.mQuit)

        #Set up timer to update current panel
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.panel.update, self.timer)
        self.timer.Start(self.parent.update_freq)
        
        
    def _close_gui(self, event):
        self.Destroy()


    def _quit_program(self, event):
        self.house.event_queue.put('Kill')
        self.Destroy()


class SimpleGUI(threading.Thread):
    """
    This simple GUI shows a ListCtrl with all the devices in the House class.
    It shows and updates their status as they change.
    
    Future: Double clicking on an item toggles its state.
    """
    def __init__(self):
        threading.Thread.__init__(self)
        self.running = True
        self.setDaemon(True)
        self.mainframe = None
        self.house = None
        self.update_freq = 100  # Update frequency in ms

    def run(self):
        app = wx.App(False)
        self.mainframe = SimpleFrame(self)
        self.mainframe.Show()
        app.MainLoop()

###############################################################################



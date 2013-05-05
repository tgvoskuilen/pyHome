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
import time
import os
from gridpanel import GridPanel
from pyHome.GUI import dialogs

class Log(GridPanel):
    """
    This is the event logging panel
    """
    #--------------------------------------------------------------------------
    def __init__(self, parent):
        """ Create the panel. This is called only when the program opens """
        GridPanel.__init__(self, parent)
                
        txtColor = (255,255,255)
        backColor = (0,0,0)
        
        self.log_data = []
        
        self.log_queue = self.parent.parent.log_queue
        
        self.log = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE|wx.TE_READONLY)
        font = wx.Font(9, wx.FONTFAMILY_TELETYPE, wx.FONTWEIGHT_NORMAL, 
                       wx.FONTSTYLE_NORMAL)
        self.log.SetFont(font)
        self.log.SetBackgroundColour(backColor)
        self.log.SetForegroundColour(txtColor)
        
        self.saveLog = wx.Button(self, wx.ID_ANY, 'Save Log')
        
        #Event log Box
        hBox = wx.BoxSizer(wx.HORIZONTAL)
        hBox.Add(self.log,1,wx.EXPAND)
        self.vBox.Add(hBox, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        
        hBox = wx.BoxSizer(wx.HORIZONTAL)
        hBox.Add(self.saveLog,0)
        self.vBox.Add(hBox, 0, wx.ALL|wx.ALIGN_RIGHT, 10)
        
        self.SetSizer(self.vBox)
        
        text = '[%s] Started pyHome' % time.strftime("%Y-%m-%d %H:%M:%S")
        self.add_to_log(text)
       
        self.Bind(wx.EVT_BUTTON, self._save_log, self.saveLog)
        
    #-------------------------------------------------------------------------- 
    def add_to_log(self,text):
        """ Add a line to the display and the stored log data """
        self.log.AppendText(text+'\n')
        self.log_data.append(text+'\n')   
    
    #-------------------------------------------------------------------------- 
    def update(self):
        """
        Empty the GUI log_queue and print it
        """
        while not self.log_queue.empty():
            msg = self.log_queue.get(False)
            self.add_to_log(msg)
        
    #-------------------------------------------------------------------------- 
    def _save_log(self, event):
        """
        Select a file to save the log to
        """
        dlg = dialogs.FileDialog(self, title="Select file to save log to", 
                                 wildcard="All Files|*",
                                 style=wx.SAVE|wx.FD_OVERWRITE_PROMPT)
                                 
        if dlg.ShowModal() == wx.ID_OK:
            newpath = dlg.GetPaths()[0]
            
            text = '[%s] Saved log file' % time.strftime("%Y-%m-%d %H:%M:%S")
            self.add_to_log(text)
        
            with open(newpath,'w') as logfile:
                logfile.writelines(self.log_data)
                
        dlg.Destroy()
    

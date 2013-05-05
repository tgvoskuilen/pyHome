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


class EditTimeout(wx.Dialog):
    """ Edit motion sensor timeout """
    #----------------------------------------------------------------------
    def __init__(self, parent, device, title="Motion Sensor",
                 okButtonText='Close'):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title, size=(350,100))
        self.parent = parent
        self.device = device

        self.timeout = wx.TextCtrl(self, -1, value=str(device.off_time))

        timeLabel = wx.StaticText(self, -1, label='Timeout (s):')
        
        self.okButton = wx.Button(self, wx.ID_OK, 'Edit')
        self.cancelButton = wx.Button(self, wx.ID_CANCEL, 'Cancel')
        
        self.vBox =  wx.BoxSizer(wx.VERTICAL)
        hBox1 = wx.BoxSizer(wx.HORIZONTAL)
        hBox2 = wx.BoxSizer(wx.HORIZONTAL)
        
        hBox1.Add(timeLabel, 0, wx.ALL, 5)
        hBox1.Add(self.timeout, 1, wx.ALL, 5)
        
        hBox2.Add(self.okButton, 1, wx.ALL, 5)
        hBox2.Add(self.cancelButton, 1, wx.ALL, 5)
        
        self.vBox.Add(hBox1, 1, wx.EXPAND|wx.ALL, 5)
        self.vBox.Add(hBox2, 1, wx.EXPAND|wx.ALL, 5)
        
        self.SetSizer(self.vBox)
        
        self.okButton.Bind(wx.EVT_BUTTON, self._check_entries)
        

    #---------------------------------------------------------------------- 
    def _check_entries(self, event):
        """ 
        When 'Ok' is pressed, check that a valid time is entered
        """
        noErrors = True
        
        try:
            time = float(self.timeout.GetValue())
        except ValueError:
            noErrors = False
            wx.MessageBox('Invalid timeout entry','Error',
                          wx.OK|wx.ICON_ERROR)
        
        if noErrors:
            self.device.off_time = time
            self.device.save()
            event.Skip()
            

        

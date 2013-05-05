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


class DimmerSlider(wx.Dialog):
    """ Light dimmer slider dialog """
    #----------------------------------------------------------------------
    def __init__(self, parent, device, title="Dimmer",
                 okButtonText='Close'):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title, size=(450,80))
        self.parent = parent
        self.device = device

        self.slider = wx.Slider(self, wx.ID_ANY, value=device.state[1], 
                        minValue=0, maxValue=100, 
                        pos=wx.DefaultPosition, 
                        size=(250, -1),
                        style=wx.SL_AUTOTICKS | wx.SL_HORIZONTAL | wx.SL_LABELS)

        self.vBox =  wx.BoxSizer(wx.VERTICAL)
        hBox1 = wx.BoxSizer(wx.HORIZONTAL)

        hBox1.Add(self.slider, 1, wx.ALL|wx.EXPAND, 5)

        self.vBox.Add(hBox1, 1, wx.EXPAND|wx.ALL, 5)
        
        self.SetSizer(self.vBox)
        self.Bind(wx.EVT_SCROLL, self.onSlide)
        self.old_state = device.state[1]
        
    def onSlide(self, event):
        new_state = self.slider.GetValue()
        if abs(self.old_state - new_state) > 5:
            self.device.turn_on(new_state)
            self.old_state = new_state

        

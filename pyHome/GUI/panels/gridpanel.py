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

class GridPanel(wx.Panel):
    """
    This is the main project panel
    """
    #----------------------------------------------------------------------
    def __init__(self, parent):
        """ Create the panel. This is called only when the program opens """
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        
        self.parent = parent
        self.house = parent.house
        
        #Organize Layout
        self.vBox = wx.BoxSizer(wx.VERTICAL)
        
    #----------------------------------------------------------------------
    def _addRow(self, entries, scaledID=-1, prePad=False, vProp=0):
        """ Add a new row to the panel sizer """
        hBox = wx.BoxSizer(wx.HORIZONTAL)
        hBox.AddSpacer((15,-1),proportion=(1 if prePad else 0))
        for id, entry in enumerate(entries):
            hBox.Add(entry, proportion=(1 if scaledID == id else 0), 
                     flag=(wx.ALL|wx.ALIGN_CENTER_VERTICAL if vProp == 0
                          else wx.ALL|wx.EXPAND), border=5)
        hBox.AddSpacer((15,-1))
        self.vBox.Add(hBox, proportion=vProp, flag=wx.EXPAND)
        
    #----------------------------------------------------------------------
    def update(self):
        pass

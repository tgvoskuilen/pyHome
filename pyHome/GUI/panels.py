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
from controls import DeviceListCtrl
from controls import DeviceMenu

class DevicePanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.parent = parent
        self.house = self.parent.house
        
        self.status_list = DeviceListCtrl(parent=self, id=-1, style=wx.LC_REPORT | wx.LC_HRULES | wx.SUNKEN_BORDER)
        self.status_list.set_cols([('Device Name',100),
                                   ('Room',100),
                                   ('Address',100),
                                   ('State',100)])

        vBox = wx.BoxSizer(wx.VERTICAL)
        vBox.Add(self.status_list, 1, wx.EXPAND, 0)
        self.SetSizer(vBox)

        self.status_list.Bind(wx.EVT_CONTEXT_MENU, self._call_device_menu)
        self.Show()


    def update(self, event):
        self.status_list.update_devices( self.house.get_devices() )


    def _call_device_menu(self, event):
        item = self.status_list.GetFirstSelected()
        tag = self.status_list.GetItemData(item)
        try:
            room = self.status_list.map[tag]['Room']
            dev_name = self.status_list.map[tag]['Device Name']
            self.PopupMenu(DeviceMenu(self, room, dev_name))
        except KeyError: #Right clicks on no items generate a tag of 0
            pass
            
            

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

class DeviceListCtrl(wx.ListCtrl):
    def __init__(self, *args, **kwargs):
        wx.ListCtrl.__init__(self, *args, **kwargs)
        self.map = {}
        self.col_names = []
        self.Bind(wx.EVT_LIST_DELETE_ITEM, self._delete_item)
        self.Bind(wx.EVT_LIST_DELETE_ALL_ITEMS, self._delete_all_items)
        
    def set_cols(self, cols):
        self.col_names = []
        for i, col in enumerate(cols):
            self.InsertColumn(i, col[0], width=col[1])
            self.col_names.append(col[0])


    def update_devices(self, devices):
        #TODO Deal with deleted devices still in the ListCtrl
        for device in devices:
            if device['Tag'] in self.map:
                self.map[device['Tag']] = device
                row = 0
                while row < self.GetItemCount():
                    key = self.GetItemData(row)
                    if key == device['Tag']:
                        break
                    row += 1
            else:
                self.map[device['Tag']] = device
                row = self.InsertStringItem(self.GetItemCount(), device[self.col_names[0]])
                self.SetItemData(row, device['Tag'])
    
            for i, col in enumerate(self.col_names):
                if i > 0:
                    self.SetStringItem(row, i, str(device[col]))


    def _delete_all_items(self, event):
        self.map.clear()
        event.Skip()
        

    def _delete_item(self, event):
        try:
            del self.map[event.Data]
        except KeyError:
            pass
        event.Skip()
        
class DeviceMenu(wx.Menu):
    """ Right click context menu for devices in the Device List """
    def __init__(self, parent, room, device):
        wx.Menu.__init__(self)
        self.parent = parent
        self.dev = parent.house.db[room][device]

        for item in self.dev.get_context_menu_items():
            mi = wx.MenuItem(self, wx.NewId(), item['Name'])
            self.AppendItem(mi)
            self.Bind(wx.EVT_MENU, item['Fcn'], mi)

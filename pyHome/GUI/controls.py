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

###############################################################################
class ObjectListCtrl(wx.ListCtrl):
    """
    A wx.ListCtrl object that can have Python objects associated with it
    more easily than a standard ListCtrl.
    """
    def __init__(self, id_str='Tag', *args, **kwargs):
        wx.ListCtrl.__init__(self, *args, **kwargs)
        self._map = {}
        self.col_names = []
        self.id_str = id_str
        self.Bind(wx.EVT_LIST_DELETE_ITEM, self._delete_item)
        self.Bind(wx.EVT_LIST_DELETE_ALL_ITEMS, self._delete_all_items)
        
    def set_cols(self, cols):
        """
        Provide a list of strings to be used as the ListCtrl column headers.
        
        This list must correspond with the keys for the dictionary
        passed in update_objects.
        """
        self.col_names = []
        for i, col in enumerate(cols):
            self.InsertColumn(i, col[0], width=col[1])
            self.col_names.append(col[0])


    def update_objects(self, objects):
        """
        In this case, 'objects' is a list of dictionaries. Each dictionary must
        have a unique id in the field 'id_str', and must have a field for each
        string in cols.
        
        If a device state is changed, this looks it up in the ListCtrl and changes
        its properties, without having to erase the entire ListCtrl
        """
        #TODO Deal with deleted objects still in the ListCtrl
        for obj in objects:
            if obj[self.id_str] in self._map:
                self._map[obj[self.id_str]] = obj
                row = 0
                while row < self.GetItemCount(): #There's got to be a more pythonic way of doing this...
                    key = self.GetItemData(row)
                    if key == obj[self.id_str]:
                        break
                    row += 1
            else:
                self._map[obj[self.id_str]] = obj
                row = self.InsertStringItem(self.GetItemCount(), str(obj[self.col_names[0]]))
                self.SetItemData(row, obj[self.id_str])
    
            for i, col in enumerate(self.col_names):
                if i > 0:
                    self.SetStringItem(row, i, str(obj[col]))


    def _delete_all_items(self, event):
        """ Untested """
        self._map.clear()
        event.Skip()
        

    def _delete_item(self, event):
        """ Untested """
        try:
            del self._map[event.Data]
        except KeyError:
            pass
        event.Skip()
        
        
        
###############################################################################
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
            
###############################################################################

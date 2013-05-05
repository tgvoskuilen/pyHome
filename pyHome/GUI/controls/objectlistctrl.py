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

class ObjectListCtrl(wx.ListCtrl):
    """
    A wx.ListCtrl object that can have Python objects associated with it
    more easily than a standard ListCtrl.
    """
    def __init__(self, *args, **kwargs):
        cols = kwargs.get('cols')
        del kwargs['cols']
        wx.ListCtrl.__init__(self, *args, **kwargs)
        self._map = {}

        for i, col in enumerate(cols):
            self.InsertColumn(i, col[0], width=col[1])
            
        self.Bind(wx.EVT_LIST_DELETE_ITEM, self._delete_item)
        self.Bind(wx.EVT_LIST_DELETE_ALL_ITEMS, self._delete_all_items)
        

    def update_objects(self, objects):
        """
        In this case, 'objects' is a list of objects. Each object must
        have a unique attribute 'tag', and must provide strings for all columns
        
        If a device state is changed, this looks it up in the ListCtrl and changes
        its properties, without having to erase the entire ListCtrl
        """
        # Deal with deleted objects still in the ListCtrl
        objkeys = [obj.tag for obj in objects]
                 
        if sorted(objkeys) != sorted(self._map.keys()):
            self.DeleteAllItems()
            self._map.clear()
        
        # Sort objects alphabetically by their sorting_name function
        sortedObjects = sorted(objects, key=lambda k: k.sorting_name())
        
        for obj in sortedObjects:
            # If the object already exists, just update its value
            if obj.tag in self._map:
                self._map[obj.tag] = obj
                row = 0
                
                # Ensure no duplicates?
                while row < self.GetItemCount(): #There's got to be a more pythonic way of doing this...
                    key = self.GetItemData(row)
                    if key == obj.tag:
                        break
                    row += 1
            else:
                self._map[obj.tag] = obj
                row = self.InsertStringItem(self.GetItemCount(), str(obj.name))
                self.SetItemData(row, obj.tag)
    
            for i,s in enumerate(obj.col_strings()):
                self.SetStringItem(row, i, s)
                

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


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
from gridpanel import GridPanel
from pyHome.GUI import controls
from pyHome.GUI import dialogs

class Devices(GridPanel):
    """
    This is the devices panel
    """
    #----------------------------------------------------------------------
    def __init__(self, parent):
        """ Create the panel. This is called only when the program opens """
        GridPanel.__init__(self, parent)
        
        self.house = parent.house
        
        roomLabel = wx.StaticText(self, wx.ID_ANY, 'Select Room')
        self.roomSelect = wx.ComboBox(self, wx.ID_ANY, style=wx.CB_READONLY, 
                                      choices=self.house.get_rooms())
        self.roomSelect.SetSelection(0)
        self._addRow([roomLabel, self.roomSelect], 1)
        
        cols = [('Device Name',200),('Room',200),('Address',150),('State',150)]
        
        self.device_list = controls.ObjectListCtrl(parent=self, id=wx.ID_ANY, 
                         style=wx.LC_REPORT | wx.LC_HRULES | wx.SUNKEN_BORDER,
                         size=(-1,-1), cols=cols)
                                                            
        self._addRow([self.device_list],0,vProp=1)
        
        self.addDevice = wx.Button(self, wx.ID_ANY, 'Add Device')
                
        self._addRow([self.addDevice], prePad=True)
        self.vBox.AddSpacer((-1,15))
        
        #ComboBox bindings
        self.Bind(wx.EVT_COMBOBOX, self._change_room, self.roomSelect)
        
        #Set the panel sizer
        self.SetSizer(self.vBox)
        
        self.device_list.Bind(wx.EVT_CONTEXT_MENU, self._call_device_menu)
        self.device_list.Bind(wx.EVT_LEFT_DCLICK, self._edit_device)
        self.Bind(wx.EVT_BUTTON, self._add_device, self.addDevice)
        
    #----------------------------------------------------------------------  
    def _edit_device(self, event):
        """ Generate a right click context menu on devices in the list """
        item = self.device_list.GetFirstSelected()
        tag = self.device_list.GetItemData(item)
        try:
            dev = self.house.find_device(tag=tag)
            self._show_info(dev)
        except (KeyError, IndexError): #ignore errors when no items selected
            pass
        
    #----------------------------------------------------------------------  
    def _add_device(self, event):
        """ Open a device creation dialog and create a new device """
        dd = dialogs.DeviceDialog(self)
        retval = dd.ShowModal()
        inputs = dd.get_inputs()
        if retval == wx.ID_OK and inputs is not None:
            self.house.add_device( inputs["Name"], inputs["Room"], 
                                   inputs["Address"], inputs["Type"], 
                                   inputs["Icon"] )
            
        dd.Destroy()
        self.update()
        
    #----------------------------------------------------------------------
    def _change_room(self, event):
        self.update()

    #----------------------------------------------------------------------
    def _show_info(self, dev):
        """ Open a device property editing dialog """
        dd = dialogs.DeviceDialog(self, inputDev=dev, okButtonText='Edit')
        retval = dd.ShowModal()
        inputs = dd.get_inputs()
        if retval == wx.ID_OK and inputs is not None:
            self.house.edit_device( dev.tag, inputs )
            
        dd.Destroy()
        self.update()
        
    #----------------------------------------------------------------------
    def _fine_adjust(self, dev):
        """
        Dimmer switch context menus can call the _fine_adjust function to show
        a slider for the dimmer.
        """
        title = dev.room + ' ' + dev.name + ' Dimmer'
        slider = dialogs.DimmerSlider(self, dev, title)        
        slider.ShowModal()
        slider.Destroy()
        
    #----------------------------------------------------------------------
    def _edit_timeout(self, dev):
        """
        Edit motion sensor timeout
        """
        title = dev.room + ' ' + dev.name + ' Motion Sensor'
        slider = dialogs.EditTimeout(self, dev, title)        
        slider.ShowModal()
        slider.Destroy()
        
    #----------------------------------------------------------------------
    def _remove_device(self, dev):
        ans = dialogs.ConfirmRemove(dev.name).ShowModal()
        
        if ans == wx.ID_YES:
            self.house.remove_device(dev)
            self.update()
        
    #----------------------------------------------------------------------
    def _call_device_menu(self, event):
        """ Generate a right click context menu on devices in the list """
        item = self.device_list.GetFirstSelected()
        tag = self.device_list.GetItemData(item)
        try:
            dev = self.house.find_device(tag=tag)
            self.PopupMenu(controls.DeviceMenu(self, dev))
        except (KeyError, IndexError): #ignore errors when no items selected
            pass

    #----------------------------------------------------------------------
    def update(self):
        self.devices = self.parent.parent.devices
        
        room = self.roomSelect.GetValue()
        self.rooms = self.house.get_rooms()
        idx = self.rooms.index(room)
        
        self.roomSelect.Clear()
        self.roomSelect.AppendItems(self.rooms)
        self.roomSelect.SetSelection(idx)
            
        self.device_list.update_objects( self.house.get_devices(room) )


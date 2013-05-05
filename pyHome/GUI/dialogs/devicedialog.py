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
import wx.combo as combo
import os
import pyHome.core

class DeviceDialog(wx.Dialog):
    """ Add/edit device dialog """
    #----------------------------------------------------------------------
    def __init__(self, parent, id=wx.ID_ANY, title="Add Device", inputDev=None,
                 okButtonText='Add'):
                 
        wx.Dialog.__init__(self, parent, id, title, size=(-1,-1))

        self.parent = parent
        
        #Make Items
        if inputDev is None:
            self.typeSelect = wx.ComboBox(self, -1,
                                    choices=parent.house.deviceTypes.keys(),
                                    style=wx.CB_READONLY, size=(250,-1))
            self.typeSelect.SetSelection(0)
            self.Bind(wx.EVT_COMBOBOX, self._update_icons, self.typeSelect)
        else:
            self.typeSelect = wx.TextCtrl(self, wx.ID_ANY, 
                                value=inputDev.type, style=wx.TE_READONLY,
                                size=(250,-1))
            self.typeSelect.SetBackgroundColour((215,215,215))
            
            
        self.name = wx.TextCtrl(self, -1, value='')
        self.room = wx.TextCtrl(self, -1, value='')
        self.address = wx.TextCtrl(self, -1, value='')
        
        self.iconSelect = combo.BitmapComboBox(self, wx.ID_ANY)
        icons = self.parent.house.get_icons(self.typeSelect.GetValue())
        names = [i['Name'] for i in icons]
        for i in icons:
            bmp = wx.Bitmap(i['File'])
            self.iconSelect.Append(i['Name'],bmp,i['Name'])

        self.okButton = wx.Button(self, wx.ID_OK, okButtonText)
        self.cancelButton = wx.Button(self, wx.ID_CANCEL, 'Cancel')

        #set inputs
        if inputDev is not None:
            self.name.SetValue(inputDev.name)
            self.room.SetValue(inputDev.room)
            self.address.SetValue(":".join([str(x) for x in inputDev.address]))
            idx = names.index(inputDev.icon)
            self.iconSelect.SetSelection(idx)


        #Make Labels
        typeLabel = wx.StaticText(self, -1, label='Device Type:')
        nameLabel = wx.StaticText(self, -1, label='Name:')
        roomLabel = wx.StaticText(self, -1, label='Room:')
        addressLabel = wx.StaticText(self, -1, label='Address (i.e. 1:255:1):')
        iconLabel = wx.StaticText(self, -1, label='Icon:')

        #Layout items
        vBox =  wx.BoxSizer(wx.VERTICAL)
        hBox1 = wx.BoxSizer(wx.HORIZONTAL)
        hBox2 = wx.BoxSizer(wx.HORIZONTAL)
        hBox3 = wx.BoxSizer(wx.HORIZONTAL)
        hBox4 = wx.BoxSizer(wx.HORIZONTAL)
        hBox5 = wx.BoxSizer(wx.HORIZONTAL)
        hBox6 = wx.BoxSizer(wx.HORIZONTAL)

        hBox1.Add(typeLabel, 0, wx.ALL, 5)
        hBox1.Add(self.typeSelect, 1, wx.EXPAND|wx.ALL, 5)

        hBox2.Add(nameLabel, 0, wx.ALL, 5)
        hBox2.Add(self.name, 1, wx.EXPAND|wx.ALL, 5)

        hBox3.Add(roomLabel, 0, wx.ALL, 5)
        hBox3.Add(self.room, 1, wx.EXPAND|wx.ALL, 5)

        hBox4.Add(addressLabel, 0, wx.ALL, 5)
        hBox4.Add(self.address, 1, wx.EXPAND|wx.ALL, 5)

        hBox5.Add(iconLabel, 0, wx.ALL, 5)
        hBox5.Add(self.iconSelect, 1, wx.EXPAND|wx.ALL, 5)

        hBox6.Add(self.okButton, 1, wx.EXPAND|wx.ALL, 5)
        hBox6.Add(self.cancelButton, 1, wx.EXPAND|wx.ALL, 5)

        vBox.Add(hBox1, 0, wx.EXPAND|wx.ALL, 5)
        vBox.Add(hBox2, 0, wx.EXPAND|wx.ALL, 5)
        vBox.Add(hBox3, 0, wx.EXPAND|wx.ALL, 5)
        vBox.Add(hBox4, 0, wx.EXPAND|wx.ALL, 5)
        vBox.Add(hBox5, 1, wx.EXPAND|wx.ALL, 5)
        vBox.Add(hBox6, 0, wx.EXPAND|wx.ALL, 5)

        #Bind events to put default AAU value in box when hop is changed
        #self.Bind(wx.EVT_COMBOBOX, self.updateAAU, self.hopSelect)
        self.SetSizer(vBox)
        vBox.Fit(self)
        

        
        self.okButton.Bind(wx.EVT_BUTTON, self._check_entries)
        
    #---------------------------------------------------------------------- 
    def _update_icons(self, event):
        self.iconSelect.Clear()
        icons = self.parent.house.get_icons(self.typeSelect.GetValue())
        names = [i['Name'] for i in icons]
        for i in icons:
            bmp = wx.Bitmap(i['File'])
            self.iconSelect.Append(i['Name'],bmp,i['Name'])
    
    #---------------------------------------------------------------------- 
    def _check_entries(self, event):
        """ 
        When 'Add' or 'Change' is pressed, check that the address is properly
        formatted and that an icon has been selected
        """
        noErrors = True
        
        if not self.name.GetValue():
            noErrors = False
            wx.MessageBox('You must enter a name for this device','Error',
                          wx.OK|wx.ICON_ERROR)
                          
        elif not self.room.GetValue():
            noErrors = False
            wx.MessageBox('You must enter a room for this device','Error',
                          wx.OK|wx.ICON_ERROR)
        
        elif not self.iconSelect.GetValue():
            noErrors = False
            wx.MessageBox('You must select an icon for this device','Error',
                          wx.OK|wx.ICON_ERROR)
        
        else:
            try:
                addr = [int(x) for x in self.address.GetValue().split(":")]
            except ValueError:
                noErrors = False
                wx.MessageBox('Invalid device address type','Error',
                              wx.OK|wx.ICON_ERROR)
        
        if noErrors:
            event.Skip()
            
            
    #----------------------------------------------------------------------
    def get_inputs(self):
        dev = {}
        try:
            dev["Address"] = [int(x) for x in self.address.GetValue().split(":")]
        except ValueError:
            return None
            
        dev["Type"] = self.typeSelect.GetValue()
        dev["Name"] = self.name.GetValue()
        dev["Room"] = self.room.GetValue()
        dev["Icon"] = self.iconSelect.GetValue()
        
        return dev




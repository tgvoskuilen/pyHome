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
import os
import pyHome.core

class MacroDialog(wx.Dialog):
    """ Add/edit macro dialog """
    #----------------------------------------------------------------------
    def __init__(self, parent, id=wx.ID_ANY, title="Add Macro", inputMacro=None,
                 okButtonText='Add'):
                 
        wx.Dialog.__init__(self, parent, id, title, size=(-1,-1))

        self.parent = parent
        
        #Make Items 
        self.name = wx.TextCtrl(self, -1, value='')
        self.description = wx.TextCtrl(self, -1, value='')
        self.errors = wx.TextCtrl(self, -1, value='', style=wx.TE_READONLY)
        self.code = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE,size=(500,250))

        self.errors.SetBackgroundColour((215,215,215))

        self.active = wx.CheckBox(self, wx.ID_ANY, 
                                      label='Active')
        

        self.okButton = wx.Button(self, wx.ID_OK, okButtonText)
        self.cancelButton = wx.Button(self, wx.ID_CANCEL, 'Cancel')

        #set inputs
        if inputMacro is not None:
            self.name.SetValue(inputMacro.name)
            self.description.SetValue(inputMacro.description)
            self.code.SetValue(inputMacro.code)
            self.active.SetValue(inputMacro.active)
            self.errors.SetValue(inputMacro.errors)


        #Make Labels
        nameLabel = wx.StaticText(self, -1, label='Name:')
        descLabel = wx.StaticText(self, -1, label='Description:')
        errLabel = wx.StaticText(self, -1, label='Errors:')
        codeLabel = wx.StaticText(self, -1, label='Macro Code:')

        #Layout items
        vBox =  wx.BoxSizer(wx.VERTICAL)
        hBox1 = wx.BoxSizer(wx.HORIZONTAL)
        hBox2 = wx.BoxSizer(wx.HORIZONTAL)
        hBox3 = wx.BoxSizer(wx.HORIZONTAL)
        hBox4 = wx.BoxSizer(wx.HORIZONTAL)
        hBox5 = wx.BoxSizer(wx.HORIZONTAL)
        hBox6 = wx.BoxSizer(wx.HORIZONTAL)

        hBox1.Add(nameLabel, 0, wx.ALL, 5)
        hBox1.Add(self.name, 1, wx.EXPAND|wx.ALL, 5)

        hBox2.Add(descLabel, 0, wx.ALL, 5)
        hBox2.Add(self.description, 1, wx.EXPAND|wx.ALL, 5)
        
        hBox3.Add(errLabel, 0, wx.ALL, 5)
        hBox3.Add(self.errors, 1, wx.EXPAND|wx.ALL, 5)

        hBox4.Add(codeLabel, 0, wx.LEFT, 5)

        hBox5.Add(self.code, 1, wx.EXPAND|wx.ALL, 5)

        hBox6.Add(self.active, 1, wx.EXPAND|wx.ALL, 5)
        hBox6.Add(self.okButton, 1, wx.EXPAND|wx.ALL, 5)
        hBox6.Add(self.cancelButton, 1, wx.EXPAND|wx.ALL, 5)

        vBox.Add(hBox1, 0, wx.EXPAND|wx.ALL, 5)
        vBox.Add(hBox2, 0, wx.EXPAND|wx.ALL, 5)
        vBox.Add(hBox3, 0, wx.EXPAND|wx.ALL, 5)
        vBox.Add(hBox4, 0, wx.EXPAND|wx.ALL, 5)
        vBox.Add(hBox5, 1, wx.EXPAND|wx.ALL, 5)
        vBox.Add(hBox6, 0, wx.EXPAND|wx.ALL, 5)

        #Bind events to put default AAU value in box when hop is changed
        self.SetSizer(vBox)
        vBox.Fit(self)
                    
            
    #----------------------------------------------------------------------
    def get_inputs(self):
        mac = {}

        mac["Name"] = self.name.GetValue()
        mac["Description"] = self.description.GetValue()
        mac["Active"] = self.active.IsChecked()
        mac["Code"] = self.code.GetValue()
        
        return mac




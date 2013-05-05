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

class Macros(GridPanel):
    """
    This is the macros panel
    """
    #----------------------------------------------------------------------
    def __init__(self, parent):
        """ Create the panel. This is called only when the program opens """
        GridPanel.__init__(self, parent)
                     
        self.house = parent.house
        
        cols =  [('Macro Name',200),('Description',400),('State',150)]
        
        
        self.macro_list = controls.ObjectListCtrl(parent=self, id=wx.ID_ANY, 
                         style=wx.LC_REPORT | wx.LC_HRULES | wx.SUNKEN_BORDER,
                         size=(-1,-1),cols=cols)
           
                                                            
        self._addRow([self.macro_list],0,vProp=1)
        
        self.addMacro = wx.Button(self, wx.ID_ANY, 'Add Macro')
                
        self._addRow([self.addMacro], prePad=True)
        self.vBox.AddSpacer((-1,15))
        
        
        #Set the panel sizer
        self.SetSizer(self.vBox)
        
        self.macro_list.Bind(wx.EVT_CONTEXT_MENU, self._call_macro_menu)
        self.macro_list.Bind(wx.EVT_LEFT_DCLICK, self._edit_macro)
        self.Bind(wx.EVT_BUTTON, self._add_macro, self.addMacro)
                

    #----------------------------------------------------------------------
    def _call_macro_menu(self, event):
        """
        Make macro right-click menu
        """
        item = self.macro_list.GetFirstSelected()
        tag = self.macro_list.GetItemData(item)
        try:
            mac = self.house.find_macro(tag=tag)
            self.PopupMenu(controls.MacroMenu(self, mac))
        except (KeyError, IndexError): #ignore errors when no items selected
            pass
        
    #----------------------------------------------------------------------
    def _show_info(self, mac):
        """ Open a macro property editing dialog """
        dd = dialogs.MacroDialog(self, inputMacro=mac, okButtonText='Edit')
        retval = dd.ShowModal()
        inputs = dd.get_inputs()
        if retval == wx.ID_OK and inputs is not None:
            self.house.edit_macro( mac.tag, inputs )
            if mac.active:
                mac.errors = ''
            
        dd.Destroy()
        self.update()
        
    #----------------------------------------------------------------------
    def _edit_macro(self, event):
        """ Generate a right click context menu on devices in the list """
        item = self.macro_list.GetFirstSelected()
        tag = self.macro_list.GetItemData(item)
        try:
            mac = self.house.find_macro(tag=tag)
            self._show_info(mac)
        except (KeyError, IndexError): #ignore errors when no items selected
            pass
        
    #----------------------------------------------------------------------
    def _add_macro(self, event):
        """ Open a macro creation dialog and create a new device """
        dd = dialogs.MacroDialog(self)
        retval = dd.ShowModal()
        inputs = dd.get_inputs()
        if retval == wx.ID_OK and inputs is not None:
            self.house.add_macro( inputs["Name"], inputs["Description"], 
                                   inputs["Code"], inputs["Active"] )
            
        dd.Destroy()
        self.update()
        
    #----------------------------------------------------------------------
    def _remove_macro(self, mac):
        ans = dialogs.ConfirmRemove(mac.name).ShowModal()
        
        if ans == wx.ID_YES:
            self.house.remove_macro(mac)
            self.update()
            
    #----------------------------------------------------------------------
    def update(self):
        self.macro_list.update_objects( self.house.get_macros() )
        

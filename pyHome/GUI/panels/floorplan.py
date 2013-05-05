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
from gridpanel import GridPanel
from pyHome.GUI import controls
from pyHome.GUI import dialogs

class FloorPlan(GridPanel):
    """
    This is the front tab floor plan panel with device icons
    """
    #----------------------------------------------------------------------
    def __init__(self, parent):
        """ Create the panel. This is called only when the program opens """
        GridPanel.__init__(self, parent)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.devices = self.parent.parent.devices
        
        self._map = {}
        
        #Set the panel sizer
        self.SetSizer(self.vBox)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Bind(wx.EVT_MOTION, self.mouseMove)
        self.Bind(wx.EVT_RIGHT_DOWN, self._process_right_click)
        self.update()
      
    #---------------------------------------------------------------------- 
    def add_device(self):
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
    def _remove_device(self, dev):
        ans = dialogs.ConfirmRemove(dev.name).ShowModal()
        
        if ans == wx.ID_YES:
            #Get rid of the icon
            self._map[dev.tag]['Icon'].Hide()
            del self._map[dev.tag]
            
            #Remove the device from the House list
            self.house.remove_device(dev)
        
        
    #---------------------------------------------------------------------- 
    def change_floorplan(self):
        dlg = dialogs.FileDialog(self, title="Select Floorplan", 
                                 wildcard="PNG Files (*.png)|*.png")
        if dlg.ShowModal() == wx.ID_OK:
            newpath = dlg.GetPaths()[0]
            newfile = os.path.basename(newpath)
            self.house.set_new_floorplan(newfile)
            self.Refresh()
        dlg.Destroy()
    
    
    #---------------------------------------------------------------------- 
    def _process_right_click(self, event):
        self.PopupMenu(controls.FloorplanMenu(self))
     
     
    #---------------------------------------------------------------------- 
    def mouseMove(self, event):
        """
        Make sure that mouse motions keep getting passed to icons if the mouse
        cursor moves off the icon and onto the panel while dragging.
        """
        for dev in self._map.itervalues():
            if 'Icon' in dev:
                dev['Icon']._move(event)
                
        
    #----------------------------------------------------------------------
    def OnEraseBackground(self, event):
        dc = event.GetDC()
        if not dc:
            dc = wx.ClientDC(self)
            rect = self.GetUpdateRegion().GetBox()
            dc.SetClippingRect(rect)
        dc.Clear()
        bmp = wx.Bitmap(self.house.floorplanFile)
        dc.DrawBitmap(bmp, 30, 60)

    #----------------------------------------------------------------------
    def update(self):
        self.devices = self.house.get_devices()
        
        row = 0
        col = 0
        
        tags = [dev.tag for dev in self.devices]
        for tag, devDict in self._map.items():
            if tag not in tags:
                self._map[tag]['Icon'].Hide()
                del self._map[tag]
        
        all_devs_locked = True
        for tag, devDict in self._map.items():
            if devDict['Icon'].is_moving():
                all_devs_locked = False
                break
                
        for dev in self.devices:
            if dev.tag not in self._map: #device not yet added, create device
                self._map[dev.tag] = {}
                self._map[dev.tag]['Device'] = dev #TODO: Remove?
                self._map[dev.tag]['Icon'] = controls.MovableIcon(self, dev)

            #device has no assigned position, place in grid
            if dev.pos is None and all_devs_locked:
                self._map[dev.tag]['Icon'].SetPosition((10+50*col, 10+50*row))
                col += 1
                if col == 15:
                    col = 1
                    row += 1
            
            self._map[dev.tag]['Icon'].update( dev )
            
    #----------------------------------------------------------------------
    def _show_info(self, dev):
        """ 
        Open a device property editing dialog 
        """
        dd = dialogs.DeviceDialog(self, inputDev=dev, okButtonText='Edit')
        retval = dd.ShowModal()
        inputs = dd.get_inputs()
        if retval == wx.ID_OK and inputs is not None:
            self.house.edit_device( dev.tag, inputs )
            self._map[dev.tag]['Icon'].load_icons(dev)
            self._map[dev.tag]['Icon'].update( dev )
            
        dd.Destroy()
        self.update()
        
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
    def _fine_adjust(self, dev):
        """
        Dimmer switches can call the _fine_adjust function to show a slider
        bar.
        """
        title = dev.room + ' ' + dev.name + ' Dimmer'
        slider = dialogs.DimmerSlider(self, dev, title)        
        slider.ShowModal()
        slider.Destroy()  
        
        

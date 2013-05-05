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
from devicemenu import DeviceMenu

class MovableIcon(wx.BitmapButton):
    def __init__(self, parent, dev):
        self.bitmap = {}
        self.parent = parent
        
        self.bitmap['Unlocked'] = wx.Bitmap(
                os.path.join(parent.house.iconFolder,"Unlocked.png"))
                
        self.load_icons(dev)

        self.state = dev.state[0]
        self.device = dev
        
        wx.BitmapButton.__init__(self, parent, wx.ID_ANY,
                                 self.bitmap[self.state], 
                                 style=wx.BU_EXACTFIT,
                                 pos=((-1,-1) if dev.pos is None else dev.pos))

        self.SetMargins(0,0)
        self._moving_button_pos = {}
        
        self.Bind(wx.EVT_LEFT_DOWN, self.__preprocess_left_click)
        self.Bind(wx.EVT_RIGHT_DOWN, self._process_right_click)
        self.Bind(wx.EVT_MOTION, self._move)
        
    def load_icons(self, dev):
        for state in dev.state_icons:
            self.bitmap[state] = wx.Bitmap(
                os.path.join(self.parent.house.iconFolder,
                             dev.icon+"_"+state+".png"))
    
    def _process_right_click(self, event):
        self.PopupMenu(DeviceMenu(self.parent, self.device))
        
    def _process_left_click(self, event): 
        self.device.toggle()  
                                    
    def update(self, dev):
        """
        Change the state based on obj
        """
        self.device = dev
        self.state = dev.state[0]
        if not self._moving_button_pos.keys():
            self.SetBitmapLabel(self.bitmap[self.state])
            
    def is_moving(self):
        return 'act' in self._moving_button_pos
        
    def __preprocess_left_click(self, event):
        if self._moving_button_pos.keys():
            self.SetBitmapLabel(self.bitmap[self.state])
            self._moving_button_pos.clear()
            obj         = event.GetEventObject()
            sx,sy       = obj.GetPositionTuple()
            
            self.device.pos = [sx, sy]
            self.device.save()
            
        else:
            if event.CmdDown():
                self.SetBitmapLabel(self.bitmap['Unlocked'])
                obj    = event.GetEventObject()
                sx,sy  = self.parent.ScreenToClient(obj.GetPositionTuple())
                dx,dy  = self.parent.ScreenToClient(wx.GetMousePosition())
                obj._x,obj._y   = (sx-dx, sy-dy)
                self._moving_button_pos['act'] = obj
            else:
                self._process_left_click(event)
                    
        event.Skip()

    def _move(self, event):
        try:
            if 'act' in self._moving_button_pos:
                obj = self._moving_button_pos['act']
                x, y = wx.GetMousePosition()
                obj.SetPosition(wx.Point(x+obj._x,y+obj._y))
        except:
            pass




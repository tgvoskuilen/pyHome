
import wx
from wx.lib.pubsub import Publisher
import time
import copy

from pyHome.core.plugins import BaseGUI

## SimpleGUI ##################################################################
class DeviceMenu(wx.Menu):
    def __init__(self, parent, room, device):
        wx.Menu.__init__(self)
        self.parent = parent
        self.dev = parent.house.db[room][device]

        for item in self.dev.get_context_menu_items():
            mi = wx.MenuItem(self, wx.NewId(), item['Name'])
            self.AppendItem(mi)
            self.Bind(wx.EVT_MENU, item['Fcn'], mi)


class DeviceList(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.parent = parent
        self.house = self.parent.house
        
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._update_gui, self.timer)
        self.timer.Start(self.parent.parent.update_freq)

        #Set up frame
        #self.panel = wx.Panel(self, id=wx.ID_ANY)
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


    def _update_gui(self, event):
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



# A special ListCtrl that stores its own data
#  The "data" is a dictionary entry of a device, including its unique tag
#
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


class SimpleFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, None, wx.ID_ANY, "Device Status", size=(500,300))
        self.parent = parent
        self.house = self.parent.house
        self.panel = DeviceList(self)

        #Create Menu bar and menus
        self.topMenu = wx.MenuBar()
        self.fileMenu = wx.Menu()

        #File Menu
        self.mClose = self.fileMenu.Append(-1, '&Close GUI',
                                          'Close the GUI Window')

        self.fileMenu.AppendSeparator()
        self.mQuit = self.fileMenu.Append(-1, '&Exit Program', 'Quit pyHome')

        #Add Menus to Menu Bar and create a status bar
        self.topMenu.Append(self.fileMenu, '&File')
        self.SetMenuBar(self.topMenu)

        self.Bind(wx.EVT_CLOSE, self._quit_program)
        self.Bind(wx.EVT_MENU, self._close_gui, self.mClose)
        self.Bind(wx.EVT_MENU, self._quit_program, self.mQuit)


    def _close_gui(self, event):
        self.Destroy()


    def _quit_program(self, event):
        self.house.event_queue.put('Kill')
        self.Destroy()


class SimpleGUI(BaseGUI):
    """
    This simple GUI shows a ListCtrl with all the devices in the House class.
    It shows and updates their status as they change.
    
    Future: Double clicking on an item toggles its state.
    """
    def __init__(self):
        BaseGUI.__init__(self)

    def run(self):
        app = wx.App(False)
        self.mainframe = SimpleFrame(self)
        self.mainframe.Show()
        app.MainLoop()

###############################################################################


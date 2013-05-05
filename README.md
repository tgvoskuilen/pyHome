pyHome
================

pyHome is a Python-based home automation server.

You may need to enable access to the usb port 
with 'sudo chmod 0777 /dev/ttyUSB0' or run it as root.

Customize pyHome with the xml files in UserData or using the GUI. 
You can add your own floor plan and device icons.

Configure runPyHome.py to refer to the address of your PLM and run it.

The docs folder contains information about building messages for Insteon and
X10 devices.

Now that HouseLinc is available for free, this is going on the back burner.
However, the floorplan GUI is still nicer than the table-only layout in
HouseLinc.

GUI Users Guide
=====================

Floor Plan Tab
----------------

This shows the floor plan image you specify in config.xml and icons for all
devices specified in devices.xml.

Right click on the floorplan to change it, or add a new device.

Right click on a device to show its info or remove it.

"Ctrl + Left click" on a device to change it to "movment mode" where it will
follow the mouse cursor so you can reposition it. Left click on it to lock
it back in place and exit "movement mode".

Left clicking on a light will toggle the light. Right click to set a dimmer to
intermediate levels.

Devices Tab
-------------------
This tab shows a list of all devices and their current state. This can be
filtered by which room the device is in using the dropdown at the top.

Right click on a device to access the same menu as in the floor plan.

Double clicking on a device will open the device info.

The "Add Device" button adds a new device. If you add a device here, it will
be staged in the upper left corner of the floor plan view until you position
it where you like.

Macros Tab
--------------------
This panel is where you manage rule macros. A macro consists of some python
code that the house will run.

Event Log Tab
---------------------
A log of house events is output here. You can click "Save Log" to save the log
to a text file.




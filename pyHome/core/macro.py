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


class Macro(object):
    """
    Macro objects contain executable python code. The code is executed in the
    scope of the House, so it can access everything. If the code generates
    any exceptions it is stopped.
    """
    #----------------------------------------------------------------------  
    def __init__(self, house, xml):
        """ Initialize a macro in a house from its xml entry """
        self.tag = id(self)           # Unique device id number
        self.house = house
        self.xml = xml
        
        # Load data from XML file
        self.name = xml.get("name")   # Macro name
        self.description = xml.find("description").text
        self.code = xml.find("code").text
        
        self.active = xml.get("active")=="True"
        self.errors = ''
        
    #----------------------------------------------------------------------  
    def register_error(self, error):
        self.active = False
        self.errors = error
        
    #----------------------------------------------------------------------     
    def sorting_name(self):
        return self.name
        
    #----------------------------------------------------------------------  
    def col_strings(self):
        """
        Get strings to show in ListCtrl row for this device
        """
        state = 'Active' if self.active else 'Inactive'
        
        if self.errors and not self.active:
            state = state + ' (errors)'
            
        return [self.name, self.description, state]
                 
    #----------------------------------------------------------------------  
    def save(self):
        """ Save macro into XML file """

        self.xml.set("name",self.name)
        self.xml.set("active",str(self.active))
        
        self.xml.find("code").text = self.code
        self.xml.find("description").text = self.description
        
        self.house.save_macros()
        
    #----------------------------------------------------------------------   
    def get_context_menu(self, host):
        return [{'Name':'Edit '+self.name, 
                    'Fcn':lambda event: host._show_info(self)},
                {'Name':'Remove Macro', 
                    'Fcn':lambda event: host._remove_macro(self)}]
        

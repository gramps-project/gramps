#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000  Donald N. Allingham
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

"""interface for opening a find person dialog for gramps
"""

__author__ = 'Don Allingham'

import GrampsCfg
import string
import gtk
from gnome.ui import *
import AutoComp
from intl import gettext
_ = gettext

class FindBase:
    """Opens find person dialog for gramps"""
    
    def __init__(self,clist,task,name):
        """Opens a dialog box instance that allows users to
        search for a person.

        clist - GtkCList containing the people information
        task - function to call to change the active person"""
        
        self.clist = clist
        self.nlist = []
        self.task = task
        title = "%s - GRAMPS" % name
        self.top = GnomeDialog(title,STOCK_BUTTON_PREV,
                               STOCK_BUTTON_NEXT,STOCK_BUTTON_CLOSE)
        self.top.set_policy(0,1,0)
        self.top.vbox.set_spacing(5)
        self.top.vbox.pack_start(gtk.GtkLabel(name),0,0,5)
        self.top.vbox.pack_start(gtk.GtkHSeparator(),0,0,0)
        self.entry = gtk.GtkEntry()
        self.top.vbox.pack_start(self.entry,0,0,25)
        self.top.button_connect(0,self.on_prev_clicked)
        self.top.button_connect(1,self.on_next_clicked)
        self.top.button_connect(2,self.on_close_clicked)
        self.top.set_usize(350,175)
        self.top.set_default(1)
        self.top.show_all()
        self.top.editable_enters(self.entry)
        self.entry.grab_focus()

    def enable_autocomp(self):
        if GrampsCfg.autocomp:
            self.comp = AutoComp.AutoEntry(self.entry,self.nlist)
        
    def advance(self,func):
        pass

    def forward(self):
        self.row = self.row + 1
        if self.row == self.clist.rows:
            self.row = 0

    def backward(self):
        self.row = self.row - 1
        if self.row < 0:
            self.row =  self.clist.rows

    def on_close_clicked(self,obj):
        self.top.destroy()

    def on_next_clicked(self,obj):
        """Advances to the next person that matches the dialog text"""
        self.advance(self.forward)

    def on_prev_clicked(self,obj):
        """Advances to the previous person that matches the dialog text"""
        self.advance(self.backward)



class FindPerson(FindBase):
    """Opens a Find Person dialog for GRAMPS"""
    
    def __init__(self,clist,task,plist):
        """Opens a dialog box instance that allows users to
        search for a person.

        clist - GtkCList containing the people information
        task - function to call to change the active person"""
        
        FindBase.__init__(self,clist,task,_("Find Person"))
        for n in plist:
            self.nlist.append(n.getPrimaryName().getName())
        self.enable_autocomp()
        
    def advance(self,func):
        try:
            self.row = self.clist.selection[0]
        except IndexError:
            gtk.gdk_beep()
            return

        text = self.entry.get_text()
        if self.row == None or text == "":
            gtk.gdk_beep()
            return
        orow = self.row
        func()
        person = None
        while self.row != orow:
            value = self.clist.get_row_data(self.row)
            if value == None:
                func()
                continue
            person,alt = value
            if alt == 0:
                name = person.getPrimaryName().getName()
                if string.find(string.upper(name),string.upper(text)) >= 0:
                    self.task(person)
                    return
            func()
        gtk.gdk_beep()

class FindPlace(FindBase):
    """Opens a Find Place dialog for GRAMPS"""
    
    def __init__(self,clist,task,plist):
        """Opens a dialog box instance that allows users to
        search for a place.

        clist - GtkCList containing the people information
        task - function to call to change the active person"""
        
        FindBase.__init__(self,clist,task,_("Find Place"))
        for n in plist:
            self.nlist.append(n.get_title())
        self.enable_autocomp()
        
    def advance(self,func):
        try:
            self.row = self.clist.selection[0]
        except IndexError:
            gtk.gdk_beep()
            return

        text = self.entry.get_text()
        if self.row == None or text == "":
            gtk.gdk_beep()
            return
        orow = self.row
        func()
        while self.row != orow:
            value = self.clist.get_row_data(self.row)
            if value == None:
                func()
                continue
            name = value.get_title()
            if string.find(string.upper(name),string.upper(text)) >= 0:
                self.task(self.row)
                return
            func()
        gtk.gdk_beep()

class FindSource(FindBase):
    """Opens a Find Place dialog for GRAMPS"""
    
    def __init__(self,clist,task,plist):
        """Opens a dialog box instance that allows users to
        search for a place.

        clist - GtkCList containing the people information
        task - function to call to change the active person"""
        
        FindBase.__init__(self,clist,task,_("Find Source"))
        for n in plist:
            self.nlist.append(n.getTitle())
        self.enable_autocomp()
        
    def advance(self,func):
        try:
            self.row = self.clist.selection[0]
        except IndexError:
            gtk.gdk_beep()
            return

        text = self.entry.get_text()
        if self.row == None or text == "":
            gtk.gdk_beep()
            return
        orow = self.row
        func()
        while self.row != orow:
            value = self.clist.get_row_data(self.row)
            if value == None:
                func()
                continue
            name = value.getTitle()
            if string.find(string.upper(name),string.upper(text)) >= 0:
                self.task(self.row)
                return
            func()
        gtk.gdk_beep()

class FindMedia(FindBase):
    """Opens a Find Media Object dialog for GRAMPS"""
    
    def __init__(self,clist,task,plist):
        """Opens a dialog box instance that allows users to
        search for a place.

        clist - GtkCList containing the people information
        task - function to call to change the active person"""
        
        FindBase.__init__(self,clist,task,_("Find Media Object"))
        for n in plist:
            self.nlist.append(n.getDescription())
        self.enable_autocomp()
        
    def advance(self,func):
        try:
            self.row = self.clist.selection[0]
        except IndexError:
            gtk.gdk_beep()
            return

        text = self.entry.get_text()
        if self.row == None or text == "":
            gtk.gdk_beep()
            return
        orow = self.row
        func()
        while self.row != orow:
            value = self.clist.get_row_data(self.row)
            if value == None:
                func()
                continue
            name = value.getDescription()
            if string.find(string.upper(name),string.upper(text)) >= 0:
                self.task(self.row)
                return
            func()
        gtk.gdk_beep()











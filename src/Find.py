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

import libglade
import Config
import const
import utils
import string
import gtk
import AutoComp

class Find:
    """Opens find person dialog for gramps"""
    
    def __init__(self,clist,task,plist):
        """Opens a dialog box instance that allows users to
        search for a person.

        clist - GtkCList containing the people information
        task - function to call to change the active person"""
        
        self.clist = clist
        self.task = task
        self.xml = libglade.GladeXML(const.findFile,"find")
        self.xml.signal_autoconnect({
            "destroy_passed_object" : utils.destroy_passed_object,
            "on_next_clicked"       : self.on_next_clicked,
            "on_prev_clicked"       : self.on_prev_clicked,
            })

        self.top = self.xml.get_widget("find")
        self.entry = self.xml.get_widget("entry")

        self.nlist = []
        for n in plist:
            self.nlist.append(n.getPrimaryName().getName())
            
        if Config.autocomp:
            AutoComp.AutoComp(self.entry,self.nlist)

        self.next = self.xml.get_widget("next")
        self.top.editable_enters(self.entry)

    def find_next(self):
        """Advances to the next person that matches the dialog text"""
        text = self.entry.get_text()

        try:
            row = self.clist.selection[0]
        except IndexError:
            gtk.gdk_beep()
            return

        if row == None or text == "":
            gtk.gdk_beep()
            return

        orow = row
        
        row = row + 1
        last = self.clist.rows
        person = None
        while row != orow:
            person,alt = self.clist.get_row_data(row)
            if alt == 0:
                name = person.getPrimaryName().getName()
                if string.find(string.upper(name),string.upper(text)) >= 0:
                    self.task(person)
                    return
            row = row + 1
            if row == last:
                row = 0
                
        gtk.gdk_beep()

    def find_prev(self):
        """Advances to the previous person that matches the dialog text"""
        text = self.entry.get_text()

        try:
            row = self.clist.selection[0]
        except IndexError:
            gtk.gdk_beep()
            return

        if row == None or text == "":
            gtk.gdk_beep()
            return

        orow = row
        row = row - 1
        last = self.clist.rows
        person = None
        while row != orow:
            value = self.clist.get_row_data(row)
            if value == None:
                row = row - 1
                continue
            person = value[0]
            alt = value[1]
            if alt == 0:
                name = person.getPrimaryName().getName()
                if string.find(string.upper(name),string.upper(text)) >= 0:
                    self.task(person)
                    return
            row = row - 1
            if row < 0:
                row = last
        gtk.gdk_beep()


    def on_next_clicked(self,obj):
        """Callback for dialog box that causes the next person to be found"""
        self.find_next()

    def on_prev_clicked(self,obj):
        """Callback for dialog box that causes the previous person to be found"""
        self.find_prev()


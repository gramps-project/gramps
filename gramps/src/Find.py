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
import const
import utils
import string
import gtk

_OBJECT = "o"

class Find:
    """Opens find person dialog for gramps"""
    
    def __init__(self,clist,task):
        """Opens a dialog box instance that allows users to
        search for a person.

        clist - GtkCList containing the people information
        task - function to call to change the active person"""
        
        self.clist = clist
        self.task = task
        self.xml = libglade.GladeXML(const.gladeFile,"find")
        self.xml.signal_autoconnect({
            "destroy_passed_object" : utils.destroy_passed_object,
            "on_next_clicked" : on_next_clicked,
            "on_prev_clicked" : on_prev_clicked,
            })
        self.top = self.xml.get_widget("find")
        self.top.set_data(_OBJECT,self)
        self.entry = self.xml.get_widget("entry1")

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

        row = row + 1
        last = self.clist.rows
        person = None
        while row < last:
            person,alt = self.clist.get_row_data(row)
            if alt == 0:
                name = person.getPrimaryName().getName()
                if string.find(string.upper(name),string.upper(text)) >= 0:
                    self.task(person)
                    return
            row = row + 1
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

        row = row - 1
        person = None
        while row >= 0:
            person,alt = self.clist.get_row_data(row)
            if alt == 0:
                name = person.getPrimaryName().getName()
                if string.find(string.upper(name),string.upper(text)) >= 0:
                    self.task(person)
                    return
            row = row - 1
        gtk.gdk_beep()



def on_next_clicked(obj):
    """Callback for dialog box that causes the next person to be found"""
    obj.get_data(_OBJECT).find_next()

def on_prev_clicked(obj):
    """Callback for dialog box that causes the previous person to be found"""
    obj.get_data(_OBJECT).find_prev()

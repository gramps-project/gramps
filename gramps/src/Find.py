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

import libglade
import const
import utils
import string

OBJECT = "o"

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class Find:
    def __init__(self,clist,task):
        self.clist = clist
        self.task = task
        self.xml = libglade.GladeXML(const.gladeFile,"find")
        self.xml.signal_autoconnect({
            "destroy_passed_object" : utils.destroy_passed_object,
            "on_next_clicked" : on_next_clicked,
            "on_prev_clicked" : on_prev_clicked,
            })
        self.top = self.xml.get_widget("find")
        self.top.set_data(OBJECT,self)
        self.entry = self.xml.get_widget("entry1")

    def find_next(self):
        text = self.entry.get_text()
        row = self.clist.selection[0]
        if row == None or text == "":
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

    def find_prev(self):
        text = self.entry.get_text()
        row = self.clist.selection[0]
        if row == None or text == "":
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

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_next_clicked(obj):
    f = obj.get_data(OBJECT)
    f.find_next()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_prev_clicked(obj):
    f = obj.get_data(OBJECT)
    f.find_prev()

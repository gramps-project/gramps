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

from gobject import TYPE_STRING
import gtk

class ListModel:
    def __init__(self,tree,dlist):
        self.tree = tree
        l = len(dlist)
        if l == 1:
            self.model = gtk.ListStore(TYPE_STRING)
        elif l == 2:
            self.model = gtk.ListStore(TYPE_STRING, TYPE_STRING)
        elif l == 3:
            self.model = gtk.ListStore(TYPE_STRING, TYPE_STRING, TYPE_STRING)
        elif l == 4:
            self.model = gtk.ListStore(TYPE_STRING, TYPE_STRING, TYPE_STRING,
                                       TYPE_STRING)
        elif l == 5:
            self.model = gtk.ListStore(TYPE_STRING, TYPE_STRING, TYPE_STRING,
                                       TYPE_STRING, TYPE_STRING)
        elif l == 6:
            self.model = gtk.ListStore(TYPE_STRING, TYPE_STRING, TYPE_STRING,
                                       TYPE_STRING, TYPE_STRING, TYPE_STRING)
        elif l == 7:
            self.model = gtk.ListStore(TYPE_STRING, TYPE_STRING, TYPE_STRING,
                                       TYPE_STRING, TYPE_STRING, TYPE_STRING,
                                       TYPE_STRING)
        elif l == 8:
            self.model = gtk.ListStore(TYPE_STRING, TYPE_STRING, TYPE_STRING,
                                       TYPE_STRING, TYPE_STRING, TYPE_STRING,
                                       TYPE_STRING, TYPE_STRING)

        self.selection = self.tree.get_selection()
        self.tree.set_model(self.model)
        
        cnum = 0
        
        for name in dlist:
            renderer = gtk.CellRendererText()
            column = gtk.TreeViewColumn(name[0],renderer,text=cnum)
            column.set_min_width(name[1])
            if name[2]:
                column.set_sort_column_id(name[2])
            if name[0] == '':
                column.set_clickable(gtk.TRUE)
                column.set_visible(gtk.FALSE)
            else:
                column.set_resizable(gtk.TRUE)
            cnum = cnum + 1
            tree.append_column(column)
            if cnum == 1:
                column.clicked()

    def clear(self):
        self.model.clear()
        
    def add(self,data):
        iter = self.model.append()
        col = 0
        for object in data:
            self.model.set_value(iter,col,object)
            col = col + 1
        

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
    def __init__(self,tree,dlist,select_func=None,event_func=None):
        self.tree = tree
        l = len(dlist)
        self.model = gtk.ListStore(*[TYPE_STRING]*l)

        self.selection = self.tree.get_selection()
        self.tree.set_model(self.model)
        
        cnum = 0
        for name in dlist:
            renderer = gtk.CellRendererText()
            column = gtk.TreeViewColumn(name[0],renderer,text=cnum)
            column.set_min_width(name[2])
            if name[0] == '':
                column.set_clickable(gtk.TRUE)
                column.set_visible(gtk.FALSE)
            else:
                column.set_resizable(gtk.TRUE)
            cnum = cnum + 1
            tree.append_column(column)
            if cnum == 1:
                column.clicked()

        cnum = 0
        for name in dlist:
            column = tree.get_column(cnum)
            column.set_sort_column_id(name[1])

        if select_func:
            self.selection.connect('changed',select_func)
        if event_func:
            self.tree.connect('event',event_func)

    def clear(self):
        self.model.clear()
        
    def add(self,data):
        iter = self.model.append()
        col = 0
        for object in data:
            self.model.set_value(iter,col,object)
            col = col + 1
        

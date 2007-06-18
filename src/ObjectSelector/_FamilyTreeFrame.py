#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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

# $Id$

import gtk
import gobject

from DisplayModels import FamilyModel

from _TreeFrameBase import TreeFrameBase

class FamilyTreeFrame(TreeFrameBase):
    
    __gproperties__ = {}

    __gsignals__ = {
        }

    __default_border_width = 5


    def __init__(self,dbstate):
	TreeFrameBase.__init__(self)        

        self._selection = None
        self._model = None
        
        self._dbstate = dbstate
        
        self._list = gtk.TreeView()
        self._list.set_rules_hint(True)
        self._list.set_headers_visible(True)
        self._list.set_headers_clickable(True)

        #self._list.connect('button-press-event',self._button_press)
        #self._list.connect('key-press-event',self._key_press)

        # Add columns
        columns = [['ID',0],
                   ['Father',1],
                   ['Mother',2],
                   ['Type',3],
                   ['Change',4]]
        
        for field in columns:
            column = gtk.TreeViewColumn(field[0], gtk.CellRendererText(), text=field[1])
            column.set_resizable(True)
            column.set_min_width(75)
            column.set_clickable(True)
            self._list.append_column(column)
            
        scrollwindow = gtk.ScrolledWindow()
        scrollwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrollwindow.set_shadow_type(gtk.SHADOW_ETCHED_IN)

        scrollwindow.add(self._list)

        self._selection = self._list.get_selection()

        self.add(scrollwindow)

        self.set_model(self._dbstate.db)

    def set_model(self,db):

        self._model = FamilyModel(db)

        self._list.set_model(self._model)

        self._selection = self._list.get_selection()

    def get_selection(self):
        return self._selection

    def get_tree(self):
        return self._list
    
if gtk.pygtk_version < (2,8,0):
    gobject.type_register(FamilyTreeFrame)

if __name__ == "__main__":

    w = ObjectSelectorWindow()
    w.show_all()
    w.connect("destroy", gtk.main_quit)

    gtk.main()

#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2004  Donald N. Allingham
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

#-------------------------------------------------------------------------
#
# internationalization
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk
import gtk.glade
import pango

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
from DisplayModels import PeopleModel
import ManagedWindow

#-------------------------------------------------------------------------
#
# SelectPerson
#
#-------------------------------------------------------------------------
class SelectPerson(ManagedWindow.ManagedWindow):

    def __init__(self, dbstate, uistate, track=[], title='',
                 filter=None, skip=[]):
        if title:
            self.title = title
        else:
            self.title = _("Select Person")

        ManagedWindow.ManagedWindow.__init__(self, uistate, track, self)

        self.renderer = gtk.CellRendererText()
        self.renderer.set_property('ellipsize',pango.ELLIPSIZE_END)
        self.db = dbstate.db
        self.glade = gtk.glade.XML(const.gladeFile,"select_person","gramps")
        self.plist =  self.glade.get_widget('plist')
        self.notebook =  self.glade.get_widget('notebook')

        window = self.glade.get_widget('select_person')
        title_label = self.glade.get_widget('title')
        self.set_window(window,title_label,self.title)
        self.model = PeopleModel(self.db,
                                 (PeopleModel.FAST, filter),
                                 skip=skip)

        self.add_columns(self.plist)
        self.plist.set_model(self.model)
        self.show()

    def build_menu_names(self,obj):
        return (self.title, None)

    def add_columns(self,tree):
        tree.set_fixed_height_mode(True)
        column = gtk.TreeViewColumn(_('Name'), self.renderer, text=0)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        column.set_fixed_width(225)
        tree.append_column(column)

        column = gtk.TreeViewColumn(_('ID'), self.renderer, text=1)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        column.set_fixed_width(75)
        tree.append_column(column)

        column = gtk.TreeViewColumn(_('Birth date'), self.renderer, text=3)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        column.set_fixed_width(160)
        tree.append_column(column)
        
    def select_function(self,store,path,iter,id_list):
        id_list.append(self.model.get_value(iter,PeopleModel.COLUMN_INT_ID))

    def get_selected_ids(self):
        mlist = []
        self.plist.get_selection().selected_foreach(self.select_function,mlist)
        return mlist

    def run(self):
        val = self.window.run()
        if val == gtk.RESPONSE_OK:
            idlist = self.get_selected_ids()
            self.close()
            if idlist and idlist[0]:
                return_value = self.db.get_person_from_handle(idlist[0])
            else:
                return_value = None
	    return return_value
        elif val != gtk.RESPONSE_DELETE_EVENT:
            self.close()
            return None

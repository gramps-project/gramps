#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2006  Donald N. Allingham
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
# Python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _
try:
    set()
except:
    from sets import Set as set

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk
import pango

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import ManagedWindow

#-------------------------------------------------------------------------
#
# SelectEvent
#
#-------------------------------------------------------------------------
class BaseSelector(ManagedWindow.ManagedWindow):
    NONE   = -1
    TEXT   =  0
    MARKUP =  1
    IMAGE  =  2

    def __init__(self, dbstate, uistate, track=[], filter=None, skip=set()):
        self.title = self.get_window_title()

        ManagedWindow.ManagedWindow.__init__(self, uistate, track, self)

        self.renderer = gtk.CellRendererText()
        self.renderer.set_property('ellipsize',pango.ELLIPSIZE_END)

        self.db = dbstate.db
        self.glade = gtk.glade.XML(const.gladeFile,"select_person","gramps")
        window = self.glade.get_widget('select_person')
        title_label = self.glade.get_widget('title')
        self.tree =  self.glade.get_widget('plist')

        self.set_window(window,title_label,self.title)

        self.model = self.get_model_class()(self.db,skip=skip)
        self.selection = self.tree.get_selection()

        self.tree.set_model(self.model)
        self.add_columns(self.tree)
        self._local_init()
        self.show()

    def add_columns(self,tree):
        tree.set_fixed_height_mode(True)
        titles = self.get_column_titles()
        for ix in range(len(titles)):
            item = titles[ix]
            if item[2] == BaseSelector.NONE:
                continue
            elif item[2] == BaseSelector.TEXT:
                column = gtk.TreeViewColumn(item[0],self.renderer,text=ix)
            elif item[2] == BaseSelector.MARKUP:
                column = gtk.TreeViewColumn(item[0],self.renderer,markup=ix)
            column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
            column.set_fixed_width(item[1])
            column.set_resizable(True)
            tree.append_column(column)           
        
    def build_menu_names(self,obj):
        return (self.title, None)

    def get_selected_ids(self):
        mlist = []
        self.selection.selected_foreach(self.select_function,mlist)
        return mlist

    def select_function(self,store,path,iter,id_list):
        handle_column = self.get_handle_column()
        id_list.append(self.model.get_value(iter,handle_column))

    def run(self):
        val = self.window.run()
        if val == gtk.RESPONSE_OK:
            id_list = self.get_selected_ids()
            self.close()
            if id_list and id_list[0]:
                return_value = self.get_from_handle_func()(id_list[0])
            else:
                return_value = None
	    return return_value
        elif val != gtk.RESPONSE_DELETE_EVENT:
            self.close()
            return None
        else:
            return None

    def _local_init(self):
        # define selector-specific init routine
        pass

    def get_window_title(self):
        # return _("Select something")
        assert False, "Must be defined in the subclass"

    def get_model_class(self):
        # return SourceModel
        assert False, "Must be defined in the subclass"
        
    def get_column_titles(self):
        # return [(_('Title'),350,), (_('ID'),1,50)]
        assert False, "Must be defined in the subclass"

    def get_from_handle_func(self):
        # return self.db.get_source_from_handle
        assert False, "Must be defined in the subclass"
        
    def get_handle_column(self):
        # return 3
        assert False, "Must be defined in the subclass"

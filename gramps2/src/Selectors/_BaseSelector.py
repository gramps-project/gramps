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

# $Id: SelectEvent.py 6155 2006-03-16 20:24:27Z rshura $

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------

import gtk
import gtk.glade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import ListModel
import ManagedWindow

#-------------------------------------------------------------------------
#
# SelectEvent
#
#-------------------------------------------------------------------------
class BaseSelector(ManagedWindow.ManagedWindow):

    def __init__(self, dbstate, uistate, track, title):
        self.title = title
        ManagedWindow.ManagedWindow.__init__(self, uistate, track, self)

        self.db = dbstate.db
        self.glade = gtk.glade.XML(const.gladeFile,"select_person","gramps")
        window = self.glade.get_widget('select_person')
        title_label = self.glade.get_widget('title')
        self.elist =  self.glade.get_widget('plist')

        self.set_window(window,title_label,self.title)

        titles = self.get_column_titles() + [('',0,0)]
        self.ncols = len(titles)

        self.model = ListModel.ListModel(self.elist,titles)

        self.redraw()
        self.show()

    def build_menu_names(self,obj):
        return (self.title, None)

    def redraw(self):
        self.model.clear()
        self.model.new_model()

        cursor_func = self.get_cursor_func()
        class_func = self.get_class_func()

        cursor = cursor_func()
        item = cursor.first()
        while item:
            (handle,data) = item
            obj = class_func()
            obj.unserialize(data)
            model_row_data = self.get_model_row_data(obj)
            self.model.add(model_row_data,handle)
            item = cursor.next()
        cursor.close()
        self.model.connect_model()
   
    def run(self):
        val = self.window.run()

        if val == gtk.RESPONSE_OK:
            store,node = self.model.get_selected()
            if node:
                data = self.model.get_data(node,range(self.ncols))
                handle = data[-1]
                return_value = self.get_from_handle_func()(handle)
            else:
                return_value = None
            self.close()
	    return return_value
        else:
            self.close()
            return None

    def get_column_titles(self):
        # return [(_('Title'),4,350), (_('ID'),1,50)]
        assert False, "Must be defined in the subclass"

    def get_from_handle_func(self):
        # return self.db.get_source_from_handle
        assert False, "Must be defined in the subclass"
        
    def get_cursor_func(self):
        # return self.db.get_source_cursor
        assert False, "Must be defined in the subclass"

    def get_class_func(self):
        # return RelLib.Source
        assert False, "Must be defined in the subclass"

    def get_model_row_data(self,obj):
        # name = obj.get_title()
        # the_id = obj.get_gramps_id()
        # return [name,the_id]
        assert False, "Must be defined in the subclass"

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
class SelectSource(ManagedWindow.ManagedWindow):

    def __init__(self, dbstate, uistate, track, title):
        self.title = title
        ManagedWindow.ManagedWindow.__init__(self, uistate, track, self)

        self.db = dbstate.db
        self.glade = gtk.glade.XML(const.gladeFile,"select_person","gramps")
        window = self.glade.get_widget('select_person')
        title_label = self.glade.get_widget('title')
        self.elist =  self.glade.get_widget('plist')

        self.set_window(window,title_label,self.title)

        titles = [(_('Title'),4,350), (_('ID'),1,50), ('',0,0)]
        self.ncols = len(titles)      

        self.model = ListModel.ListModel(self.elist,titles)

        self.redraw()
        self.show()

    def build_menu_names(self,obj):
        return (self.title, None)

    def redraw(self):
        self.model.clear()
        self.model.new_model()

        for handle in self.db.get_source_handles():
            source = self.db.get_source_from_handle(handle)
            desc = source.get_title()
            the_id = source.get_gramps_id()
            self.model.add([desc,the_id,handle])
        self.model.connect_model()

    def run(self):
        val = self.window.run()

        if val == gtk.RESPONSE_OK:
            store,node = self.model.get_selected()
            if node:
                data = self.model.get_data(node,range(self.ncols))
                handle = data[2]
                return_value = self.db.get_source_from_handle(handle)
            else:
                return_value = None
            self.close()
	    return return_value
        else:
            self.close()
            return None

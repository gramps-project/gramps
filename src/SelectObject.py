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

#
# Written by Alex Roitman, 
# largely based on the MediaView and SelectPerson by Don Allingham
#

#-------------------------------------------------------------------------
#
# general modules
#
#-------------------------------------------------------------------------
import gc

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
import gtk.gdk

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import ListModel
import ImgManip
import Mime
import ManagedWindow

#-------------------------------------------------------------------------
#
# SelectPerson
#
#-------------------------------------------------------------------------
class SelectObject(ManagedWindow.ManagedWindow):

    def __init__(self, dbstate, uistate, track, title):
        self.title = title
        ManagedWindow.ManagedWindow.__init__(self, uistate, track, self)

        self.db = dbstate.db
        self.glade = gtk.glade.XML(const.gladeFile,"select_person","gramps")
        window = self.glade.get_widget('select_person')
        title_label = self.glade.get_widget('object_title')
        self.object_tree = self.glade.get_widget('plist')

        self.set_window(window,title_label,self.title)

        titles = [
            (_('Preview'),0,50,ListModel.IMAGE),
            (_('Title'),1,150),
            (_('ID'),2,50),
            (_('Type'),3,70),
            ('',4,0)
            ]
        
        self.ncols = len(titles)      

        self.object_model = ListModel.ListModel(self.object_tree,titles)
        self.selection = self.object_tree.get_selection()

        self.redraw()
        self.show()

    def build_menu_names(self,obj):
        return (self.title, None)

    def redraw(self):
        self.object_model.clear()
        self.object_model.new_model()

        for key in self.db.get_media_object_handles():
            obj = self.db.get_object_from_handle(key)
            title = obj.get_description()
            the_type = Mime.get_description(obj.get_mime_type())
            pixbuf = ImgManip.get_thumb_from_obj(obj)
            pixbuf = pixbuf.scale_simple(pixbuf.get_width()/2,
                                         pixbuf.get_height()/2,
                                         gtk.gdk.INTERP_BILINEAR)
            self.object_model.add([pixbuf,title,obj.get_gramps_id(),the_type],key)
        self.object_model.connect_model()
        
    def run(self):
        val = self.window.run()

        if val == gtk.RESPONSE_OK:
            store,node = self.object_model.get_selected()
            if node:
                data = self.object_model.get_data(node,range(self.ncols))
                handle = data[4]
                return_value = self.db.get_object_from_handle(handle)
            else:
                return_value = None
            self.close()
            gc.collect()
	    return return_value
        else:
            self.close()
            gc.collect()
            return None

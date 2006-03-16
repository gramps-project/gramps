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
from TransUtils import sgettext as _

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
import Utils
import ListModel
import ImgManip
import Mime

#-------------------------------------------------------------------------
#
# SelectPerson
#
#-------------------------------------------------------------------------
class SelectObject:

    def __init__(self,db,title):

        self.db = db
        self.glade = gtk.glade.XML(const.gladeFile,"select_object","gramps")
        self.top = self.glade.get_widget('select_object')
        title_label = self.glade.get_widget('object_title')
        self.object_tree = self.glade.get_widget('object_tree')
        self.object_handle = self.glade.get_widget('object_id')
        self.object_type = self.glade.get_widget('object_type')
        self.object_desc = self.glade.get_widget('object_desc')
        self.object_path = self.glade.get_widget('object_path')
        self.preview = self.glade.get_widget('preview')
        self.object_details = self.glade.get_widget('object_details')

        Utils.set_titles(self.top,title_label,title)

        titles = [(_('Title'),0,350), (_('ID'),1,50),
                    (_('Type'),2,70), ('Path',3,150), ('',4,0) ] 
        self.ncols = len(titles)      

        self.object_model = ListModel.ListModel(self.object_tree,titles)
        self.selection = self.object_tree.get_selection()
        self.selection.connect('changed',self.on_select_row)

        self.redraw()
        self.top.show()

    def redraw(self):
        self.object_model.clear()
        self.object_model.new_model()

        for key in self.db.get_media_object_handles():
            obj = self.db.get_object_from_handle(key)
            title = obj.get_description()
            the_type = Mime.get_description(obj.get_mime_type())
            path = obj.get_path()
            self.object_model.add([title,obj.get_gramps_id(),the_type,path],key)

        self.object_model.connect_model()
        
    def on_select_row(self,obj):
        store,node = self.object_model.get_selected()
        if not node:
            return
        data = self.object_model.get_data(node,range(self.ncols))
        handle = data[4]
        obj = self.db.get_object_from_handle(handle)
        the_type = obj.get_mime_type()
        path = obj.get_path()

        if the_type and the_type[0:5] == "image":
            image = ImgManip.get_thumbnail_image(path,the_type)
        else:
            image = Mime.find_mime_type_pixbuf(the_type)
        self.preview.set_from_pixbuf(image)
        
        self.object_handle.set_text(obj.get_gramps_id())
        if the_type:
            self.object_type.set_text(the_type)
        else:
            self.object_type.set_text("")
        self.object_desc.set_text(obj.get_description())
        if len(path) == 0:
            self.object_path.set_text(_("The file no longer exists"))
        elif path[0] == "/":
            self.object_path.set_text(path)
        else:
            self.object_path.set_text("<local>")
        self.object_details.set_text(Utils.get_detail_text(obj,0))

    def run(self):
        val = self.top.run()

        if val == gtk.RESPONSE_OK:
            store,node = self.object_model.get_selected()
            if node:
                data = self.object_model.get_data(node,range(self.ncols))
                handle = data[4]
                return_value = self.db.get_object_from_handle(handle)
            else:
                return_value = None
            self.top.destroy()
            gc.collect()
	    return return_value
        else:
            self.top.destroy()
            gc.collect()
            return None

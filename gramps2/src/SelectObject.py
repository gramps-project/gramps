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
import string
import os

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
import RelLib
import const
import Utils
import ListModel

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
        self.object_handle = self.glade.get_widget('object_handle')
        self.object_type = self.glade.get_widget('object_type')
        self.object_desc = self.glade.get_widget('object_desc')
        self.object_path = self.glade.get_widget('object_path')
        self.preview = self.glade.get_widget('preview')
        self.object_details = self.glade.get_widget('object_details')

        Utils.set_titles(self.top,title_label,title)

        titles = [(_('Title'),4,350), (_('ID'),1,50),
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

        for key in self.db.get_object_keys():
            object = self.db.get_object_from_handle(key)
            title = object.get_description()
            the_id = object.get_handle()
            the_type = Utils.get_mime_description(object.get_mime_type())
            path = object.get_path()
            self.object_model.add([title,the_id,the_type,path],key)

        self.object_model.connect_model()
        
    def on_select_row(self,obj):
        fexists = 1

        store,iter = self.object_model.get_selected()
        if not iter:
            return
        data = self.object_model.get_data(iter,range(self.ncols))
        the_id = data[4]
        object = self.db.get_object_from_handle(the_id)
        the_type = Utils.get_mime_description(object.get_mime_type())
        path = object.get_path()

        thumb_path = Utils.thumb_path(self.db.get_save_path(),object)
        pexists = os.path.exists(path)
        if pexists and os.path.exists(thumb_path):
            self.preview.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(thumb_path))
        else:
            icon_image = gtk.gdk.pixbuf_new_from_file(Utils.find_icon(the_type))
            self.preview.set_from_pixbuf(icon_image)
            if not pexists:
                fexists = 0
        
        self.object_handle.set_text(object.get_handle())
        self.object_type.set_text(the_type)
        self.object_desc.set_text(object.get_description())
        if len(path) == 0 or fexists == 0:
            self.object_path.set_text(_("The file no longer exists"))
        elif path[0] == "/":
            self.object_path.set_text(path)
        else:
            self.object_path.set_text("<local>")
        self.object_details.set_text(Utils.get_detail_text(object,0))

    def run(self):
        val = self.top.run()

        if val == gtk.RESPONSE_OK:
            store,iter = self.object_model.get_selected()
            if iter:
                data = self.object_model.get_data(iter,range(self.ncols))
                the_id = data[4]
                return_value = self.db.get_object_from_handle(the_id)
            else:
                return_value = None
            self.top.destroy()
	    return return_value
        else:
            self.top.destroy()
            return None

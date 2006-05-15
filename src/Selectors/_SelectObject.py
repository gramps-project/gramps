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
from gtk.gdk import INTERP_BILINEAR

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from ImgManip import get_thumb_from_obj
from Mime import get_description
from ListModel import IMAGE
from RelLib import MediaObject
from _BaseSelector import BaseSelector

#-------------------------------------------------------------------------
#
# SelectObject
#
#-------------------------------------------------------------------------
class SelectObject(BaseSelector):

    def get_column_titles(self):
        return [(_('Preview'),0,50,IMAGE),
                (_('Title'),1,150),
                (_('ID'),2,50),
                (_('Type'),3,70)]

    def get_from_handle_func(self):
        return self.db.get_object_from_handle
        
    def get_cursor_func(self):
        return self.db.get_media_cursor

    def get_class_func(self):
        return MediaObject

    def get_model_row_data(self,obj):
        title = obj.get_description()
        the_type = get_description(obj.get_mime_type())
        pixbuf = get_thumb_from_obj(obj)
        pixbuf = pixbuf.scale_simple(pixbuf.get_width()/2,
                                     pixbuf.get_height()/2,
                                     INTERP_BILINEAR)
        return [pixbuf,title,obj.get_gramps_id(),the_type]

    def close(self,*obj):
        # needed to collect garbage on closing
        BaseSelector.close(self,*obj)
        gc.collect()

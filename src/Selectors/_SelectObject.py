#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2006  Donald N. Allingham
#               2009       Gary Burton
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

# Written by Alex Roitman, 
# largely based on the MediaView and SelectPerson by Don Allingham

#-------------------------------------------------------------------------
#
# internationalization
#
#-------------------------------------------------------------------------
import gc
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GTK+
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
from Utils import media_path_full
import ThumbNails
from DisplayModels import MediaModel
from _BaseSelector import BaseSelector
import config

#-------------------------------------------------------------------------
#
# SelectObject
#
#-------------------------------------------------------------------------
class SelectObject(BaseSelector):

    def get_window_title(self):
        return _("Select Media Object")
        
    def get_model_class(self):
        return MediaModel

    def get_from_handle_func(self):
        return self.db.get_object_from_handle
        
    def get_handle_column(self):
        return 6

    def get_column_titles(self):
        return [
            (_('Title'), 350, BaseSelector.TEXT, 0),
            (_('ID'),     75, BaseSelector.TEXT, 1),
            (_('Type'),   75, BaseSelector.TEXT, 2),
            ]

    def _local_init(self):
        """
        Perform local initialisation for this class
        """
        self.width_key = 'interface.media-sel-width'
        self.height_key = 'interface.media-sel-height'
        self.preview = gtk.Image()
        self.preview.set_size_request(int(const.THUMBSCALE),
                                    int(const.THUMBSCALE))
        vbox = self.glade.get_object('select_person_vbox')
        vbox.pack_start(self.preview,False)
        vbox.reorder_child(self.preview,1)
        self.preview.show()
        self.selection.connect('changed',self._row_change)

    def _row_change(self, obj):
        id_list = self.get_selected_ids()
        if not (id_list and id_list[0]):
            return
        handle = id_list[0]
        obj = self.get_from_handle_func()(handle)
        pix = ThumbNails.get_thumbnail_image(media_path_full(self.db, 
                                                             obj.get_path()))
        self.preview.set_from_pixbuf(pix)
        gc.collect()

    def column_view_names(self):
        """
        Get correct column view names on which model is based
        """
        import DataViews
        return DataViews.MediaView.COLUMN_NAMES

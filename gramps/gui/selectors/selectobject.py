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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

# Written by Alex Roitman,
# largely based on the MediaView and SelectPerson by Don Allingham

#-------------------------------------------------------------------------
#
# internationalization
#
#-------------------------------------------------------------------------
import gc

#-------------------------------------------------------------------------
#
# GTK+
#
#-------------------------------------------------------------------------
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext
from gramps.gen.const import THUMBSCALE
from gramps.gen.utils.file import media_path_full
from gramps.gen.utils.thumbnails import get_thumbnail_image
from ..views.treemodels import MediaModel
from .baseselector import BaseSelector
from gramps.gen.const import URL_MANUAL_SECT1

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------

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
        return self.db.get_media_from_handle

    def get_column_titles(self):
        return [
            (_('Title'), 350, BaseSelector.TEXT, 0),
            (_('ID'),     75, BaseSelector.TEXT, 1),
            (_('Type'),   75, BaseSelector.TEXT, 2),
            (_('Last Change'), 150, BaseSelector.TEXT, 7),
            ]

    def _local_init(self):
        """
        Perform local initialisation for this class
        """
        self.setup_configs('interface.media-sel', 600, 450)
        self.preview = Gtk.Image()
        self.preview.set_size_request(int(THUMBSCALE),
                                    int(THUMBSCALE))
        vbox = self.glade.get_object('select_person_vbox')
        vbox.pack_start(self.preview, False, True, 0)
        vbox.reorder_child(self.preview,1)
        self.preview.show()
        self.selection.connect('changed',self._row_change)

    def _row_change(self, obj):
        id_list = self.get_selected_ids()
        if not (id_list and id_list[0]):
            return
        handle = id_list[0]
        obj = self.get_from_handle_func()(handle)
        pix = get_thumbnail_image(media_path_full(self.db, obj.get_path()))
        self.preview.set_from_pixbuf(pix)
        gc.collect()

    WIKI_HELP_PAGE = URL_MANUAL_SECT1
    WIKI_HELP_SEC = _('manual|Select_Media_Object_selector')

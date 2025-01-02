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

# -------------------------------------------------------------------------
#
# internationalization
#
# -------------------------------------------------------------------------
import gc

# -------------------------------------------------------------------------
#
# GTK+
#
# -------------------------------------------------------------------------
from gi.repository import GdkPixbuf, Gtk
from gi.repository import GObject
from gi.repository import Pango

# -------------------------------------------------------------------------
#
# gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext
from gramps.gen.const import THUMBSCALE
from gramps.gen.utils.file import media_path_full
from gramps.gen.utils.thumbnails import get_thumbnail_image
from ..views.treemodels import MediaModel
from .baseselector import BaseSelector
from gramps.gen.const import URL_MANUAL_SECT1

# -------------------------------------------------------------------------
#
# Constants
#
# -------------------------------------------------------------------------


# -------------------------------------------------------------------------
#
# SelectObject
#
# -------------------------------------------------------------------------
class SelectObject(BaseSelector):
    def get_window_title(self):
        return _("Select Media Object")

    def get_model_class(self):
        return MediaModel

    def get_from_handle_func(self):
        return self.db.get_media_from_handle

    def get_column_titles(self):
        return [
            (_("Title"), 350, BaseSelector.TEXT, 0),
            (_("ID"), 75, BaseSelector.TEXT, 1),
            (_("Type"), 75, BaseSelector.TEXT, 2),
            (_("Last Change"), 150, BaseSelector.TEXT, 7),
            (_("Path"), 150, BaseSelector.TEXT, 3),
        ]

    def _local_init(self):
        """
        Perform local initialisation for this class
        """
        self.setup_configs("interface.media-sel", 600, 450)

        # insert a ScrolledWindow containing an IconView to display thumbnails
        # of the selected media

        # pixels to pad the image
        padding = 6

        self.iconmodel = Gtk.ListStore(GdkPixbuf.Pixbuf, GObject.TYPE_STRING, object)
        self.iconlist = Gtk.IconView()
        self.track_ref_for_deletion("iconlist")
        self.iconlist.set_pixbuf_column(0)
        self.iconlist.set_item_width(int(THUMBSCALE) + padding * 2)

        text_renderer = Gtk.CellRendererText()
        text_renderer.set_property("wrap-mode", Pango.WrapMode.WORD_CHAR)
        text_renderer.set_property("wrap-width", THUMBSCALE)
        text_renderer.set_property("alignment", Pango.Alignment.CENTER)
        self.iconlist.pack_end(text_renderer, True)
        self.iconlist.add_attribute(text_renderer, "text", 1)

        self.iconlist.set_margin(padding)
        self.iconlist.set_column_spacing(padding)
        self.iconlist.set_model(self.iconmodel)

        # create the scrolled window
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.set_min_content_height(int(THUMBSCALE) + padding * 2)
        scroll.add(self.iconlist)

        vbox = self.glade.get_object("select_person_vbox")
        vbox.pack_start(scroll, False, True, 0)
        vbox.reorder_child(scroll, 1)
        scroll.show()
        self.selection.connect("changed", self._row_change)

    def _row_change(self, obj):
        self.iconmodel.clear()

        id_list = self.get_selected_ids()
        for handle in self.get_selected_ids():
            if handle:
                obj = self.get_from_handle_func()(handle)
                pix = get_thumbnail_image(media_path_full(self.db, obj.get_path()))
                self.iconmodel.append(row=(pix, obj.get_description(), obj))
        gc.collect()

    def get_config_name(self):
        return __name__

    WIKI_HELP_PAGE = URL_MANUAL_SECT1
    WIKI_HELP_SEC = _("Select_Media_Object_selector", "manual")

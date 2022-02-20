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

MEDIA_DATE = None

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
    
    namespace = 'Media'

    def __init__(self, dbstate, uistate, track=[], title=None, filter=None,
                 skip=set(), show_search_bar=False, default=None):

        # SelectMedia may have a title passed to it which should be used
        # instead of the default defined for get_window_title()
        if title is not None:
            self.title = title

        history = uistate.get_history(self.namespace).mru
        active_handle = uistate.get_active(self.namespace)

        # see gui.plug._guioptions

        from gramps.gen.filters import GenericFilterFactory, rules

        # Baseselector? rules.media.IsBookmarked?
        # Create a filter for the media selector.
        sfilter = GenericFilterFactory(self.namespace)()
        sfilter.set_logical_op('or')
        #sfilter.add_rule(rules.media.IsBookmarked([]))

        # Add recent media.
        for handle in history:
            recent = dbstate.db.get_media_from_handle(handle)
            gid = recent.get_gramps_id()
            sfilter.add_rule(rules.media.HasIdOf([gid]))

        # Add bookmarked media.
        for handle in dbstate.db.get_media_bookmarks().get():
            marked = dbstate.db.get_media_from_handle(handle)
            gid = marked.get_gramps_id()
            sfilter.add_rule(rules.media.HasIdOf([gid]))

        if active_handle:
            BaseSelector.__init__(self, dbstate, uistate, track, sfilter,
                                  skip, show_search_bar, active_handle)
        else:
            BaseSelector.__init__(self, dbstate, uistate, track, sfilter,
                                  skip, show_search_bar)

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
            #(_('Last Change'), 150, BaseSelector.TEXT, 7),
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
        SWITCH = self.switch.get_state()

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
    WIKI_HELP_SEC = _('Select_Media_Object_selector', 'manual')

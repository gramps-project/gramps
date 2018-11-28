#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2009-2010  Nick Hall
# Copyright (C) 2009       Benny Malengier
# Copyright (C) 2010       Gary Burton
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

"""
Place Model.
"""
#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
import logging
_LOG = logging.getLogger(".gui.views.treemodels.placemodel")

#-------------------------------------------------------------------------
#
# GNOME/GTK modules
#
#-------------------------------------------------------------------------
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.lib import Place, PlaceType
from gramps.gen.datehandler import format_time
from gramps.gen.utils.place import conv_lat_lon
from gramps.gen.display.place import displayer as place_displayer
from gramps.gen.config import config
from .flatbasemodel import FlatBaseModel
from .treebasemodel import TreeBaseModel

#-------------------------------------------------------------------------
#
# internationalization
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

#-------------------------------------------------------------------------
#
# PlaceBaseModel
#
#-------------------------------------------------------------------------
class PlaceBaseModel:

    def __init__(self, db):
        self.gen_cursor = db.get_place_cursor
        self.map = db.get_raw_place_data
        self.fmap = [
            self.column_name,
            self.column_id,
            self.column_title,
            self.column_type,
            self.column_code,
            self.column_latitude,
            self.column_longitude,
            self.column_private,
            self.column_tags,
            self.column_change,
            self.column_tag_color,
            self.search_name,
            ]
        self.smap = [
            self.column_name,
            self.column_id,
            self.column_title,
            self.column_type,
            self.column_code,
            self.sort_latitude,
            self.sort_longitude,
            self.column_private,
            self.column_tags,
            self.sort_change,
            self.column_tag_color,
            self.search_name,
            ]

    def destroy(self):
        """
        Unset all elements that can prevent garbage collection
        """
        self.db = None
        self.gen_cursor = None
        self.map = None
        self.fmap = None
        self.smap = None

    def color_column(self):
        """
        Return the color column.
        """
        return 10

    def on_get_n_columns(self):
        return len(self.fmap)+1

    def column_title(self, data):
        handle = data[0]
        cached, value = self.get_cached_value(handle, "PLACE")
        if not cached:
            place = Place()
            place.unserialize(data)
            value = place_displayer.display(self.db, place)
            self.set_cached_value(handle, "PLACE", value)
        return value

    def column_name(self, data):
        """ Return the primary name """
        return data[6][0]

    def search_name(self, data):
        """ The search name includes all alt names to enable finding by alt name
        """
        return ','.join([data[6][0]] + [name[0] for name in data[7]])

    def column_longitude(self, data):
        if not data[3]:
            return ''
        value = conv_lat_lon('0', data[3], format='DEG')[1]
        if not value:
            return _("Error in format")
        return value

    def column_latitude(self, data):
        if not data[4]:
            return ''
        value = conv_lat_lon(data[4], '0', format='DEG')[0]
        if not value:
            return _("Error in format")
        return value

    def sort_longitude(self, data):
        if not data[3]:
            return ''
        value = conv_lat_lon('0', data[3], format='ISO-DMS') if data[3] else ''
        if not value:
             return _("Error in format")
        return value

    def sort_latitude(self, data):
        if not data[4]:
            return ''
        value = conv_lat_lon(data[4], '0', format='ISO-DMS') if data[4] else ''
        if not value:
            return _("Error in format")
        return value

    def column_id(self, data):
        return data[1]

    def column_type(self, data):
        return str(PlaceType(data[8]))

    def column_code(self, data):
        return data[9]

    def column_private(self, data):
        if data[17]:
            return 'gramps-lock'
        else:
            # There is a problem returning None here.
            return ''

    def sort_change(self, data):
        return "%012x" % data[15]

    def column_change(self, data):
        return format_time(data[15])

    def get_tag_name(self, tag_handle):
        """
        Return the tag name from the given tag handle.
        """
        cached, value = self.get_cached_value(tag_handle, "TAG_NAME")
        if not cached:
            value = self.db.get_tag_from_handle(tag_handle).get_name()
            self.set_cached_value(tag_handle, "TAG_NAME", value)
        return value

    def column_tag_color(self, data):
        """
        Return the tag color.
        """
        tag_handle = data[0]
        cached, value = self.get_cached_value(tag_handle, "TAG_COLOR")
        if not cached:
            tag_color = ""
            tag_priority = None
            for handle in data[16]:
                tag = self.db.get_tag_from_handle(handle)
                if tag:
                    this_priority = tag.get_priority()
                    if tag_priority is None or this_priority < tag_priority:
                        tag_color = tag.get_color()
                        tag_priority = this_priority
            value = tag_color
            self.set_cached_value(tag_handle, "TAG_COLOR", value)
        return value

    def column_tags(self, data):
        """
        Return the sorted list of tags.
        """
        tag_list = list(map(self.get_tag_name, data[16]))
        # TODO for Arabic, should the next line's comma be translated?
        return ', '.join(sorted(tag_list, key=glocale.sort_key))

    def clear_cache(self, handle=None):
        """
        Clear the LRU cache. Always clear lru_path, because paths may have
        changed.
        Need special version of this because Places include Placerefs, and a
        change in the place the Placeref points to can make the cache stale.
        So just clearing the effected (deleted/changed) handle is not enough.
        Note that this is only a (very) short term issue, during processing of
        signals from a merge event.  The update of the place containing a
        Placeref will occur.
        See bug 10184.

        Note that this method overrides the one from 'BaseModel', through
        FlatBaseModel and TreeBaseModel.  By locating this in PlaceBaseModel,
        the MRU rules mean this method takes precedence.
        """
        self.lru_data.clear()
        # Invalidates all paths
        self.lru_path.clear()

#-------------------------------------------------------------------------
#
# PlaceListModel
#
#-------------------------------------------------------------------------
class PlaceListModel(PlaceBaseModel, FlatBaseModel):
    """
    Flat place model.  (Original code in PlaceBaseModel).
    """
    def __init__(self, db, uistate, scol=0, order=Gtk.SortType.ASCENDING,
                 search=None, skip=set(), sort_map=None):

        PlaceBaseModel.__init__(self, db)
        FlatBaseModel.__init__(self, db, uistate, scol, order, search=search,
                               skip=skip, sort_map=sort_map)

    def destroy(self):
        """
        Unset all elements that can prevent garbage collection
        """
        PlaceBaseModel.destroy(self)
        FlatBaseModel.destroy(self)

#-------------------------------------------------------------------------
#
# PlaceTreeModel
#
#-------------------------------------------------------------------------
class PlaceTreeModel(PlaceBaseModel, TreeBaseModel):
    """
    Hierarchical place model.
    """
    def __init__(self, db, uistate, scol=0, order=Gtk.SortType.ASCENDING,
                 search=None, skip=set(), sort_map=None):

        PlaceBaseModel.__init__(self, db)
        TreeBaseModel.__init__(self, db, uistate, scol=scol, order=order,
                               search=search, skip=skip, sort_map=sort_map,
                               nrgroups=3,
                               group_can_have_handle=True)

    def destroy(self):
        """
        Unset all elements that can prevent garbage collection
        """
        PlaceBaseModel.destroy(self)
        self.number_items = None
        TreeBaseModel.destroy(self)

    def _set_base_data(self):
        """See TreeBaseModel, for place, most have been set in init of
        PlaceBaseModel
        """
        self.number_items = self.db.get_number_of_places
        self.gen_cursor = self.db.get_place_tree_cursor

    def get_tree_levels(self):
        """
        Return the headings of the levels in the hierarchy.
        """
        return [_('Country'), _('State'), _('County'), _('Place')]

    def add_row(self, handle, data):
        """
        Add nodes to the node map for a single place.

        handle      The handle of the gramps object.
        data        The object data.
        """
        sort_key = self.sort_func(data)
        if len(data[5]) > 0:
            parent = data[5][0][0]
        else:
            parent = None

        # Add the node as a root node if the parent is not in the tree.  This
        # will happen when the view is filtered.
        if not self._get_node(parent):
            parent = None

        self.add_node(parent, handle, sort_key, handle, add_parent=False)

    def column_header(self, data):
        # should not get here!
        return '????'

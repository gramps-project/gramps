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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# $Id$

"""
Location Model.
"""
#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
import cgi
import logging
_LOG = logging.getLogger(".gui.views.treemodels.locationmodel")

#-------------------------------------------------------------------------
#
# GNOME/GTK modules
#
#-------------------------------------------------------------------------
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from gramps.gen.datehandler import format_time
from gramps.gen.utils.place import conv_lat_lon
from .flatbasemodel import FlatBaseModel
from .treebasemodel import TreeBaseModel

#-------------------------------------------------------------------------
#
# internationalization
#
#-------------------------------------------------------------------------
from gramps.gen.ggettext import gettext as _

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
LOCATIONTYPES = [_('Country'), _('State'), _('County'), _('City'), 
                 _('Parish'), _('Locality'), _('Street')]

#-------------------------------------------------------------------------
#
# LocationBaseModel
#
#-------------------------------------------------------------------------
class LocationBaseModel(object):

    HANDLE_COL = 5

    def __init__(self, db):
        self.gen_cursor = db.get_location_cursor
        self.map = db.get_raw_location_data
        self.fmap = [
            self.column_name,
            self.column_type,
            self.column_latitude,
            self.column_longitude,
            self.column_change,
            self.column_handle,
            ]
        self.smap = [
            self.column_name,
            self.column_type,
            self.sort_latitude,
            self.sort_longitude,
            self.sort_change,
            self.column_handle,
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

    def on_get_n_columns(self):
        return len(self.fmap)+1

    def column_handle(self, data):
        return unicode(data[0])

    def column_name(self, data):
        return unicode(data[2])

    def column_type(self, data):
        return LOCATIONTYPES[data[3]-1]

    def column_latitude(self, data):
        if not data[4]:
            return u' '
        value = conv_lat_lon(data[4], '0', format='DEG')[0]
        if not value:
            return _("Error in format")
        return value

    def column_longitude(self, data):
        if not data[5]:
            return u' '
        value = conv_lat_lon('0', data[5], format='DEG')[1]
        if not value:
            return _("Error in format")
        return value

    def sort_latitude(self, data):
        if not data[4]:
            return u' '
        value = conv_lat_lon(data[4], '0', format='ISO-DMS') if data[4] else u''
        if not value:
            return _("Error in format")
        return value 

    def sort_longitude(self, data):
        if not data[5]:
            return u' '
        value = conv_lat_lon('0', data[5], format='ISO-DMS') if data[5] else u''
        if not value:
             return _("Error in format")
        return value

    def sort_change(self, data):
        return "%012x" % data[6]
    
    def column_change(self, data):
        return Utils.format_time(data[6])

    def column_place_name(self, data):
        return unicode(data[2])

    def sort_place_change(self, data):
        return "%012x" % data[9]
    
    def column_place_change(self, data):
        return Utils.format_time(data[9])

#-------------------------------------------------------------------------
#
# LocationTreeModel
#
#-------------------------------------------------------------------------
class LocationTreeModel(LocationBaseModel, TreeBaseModel):
    """
    Hierarchical place model.
    """
    def __init__(self, db, scol=0, order=Gtk.SortType.ASCENDING, search=None,
                 skip=set(), sort_map=None):

        LocationBaseModel.__init__(self, db)
        TreeBaseModel.__init__(self, db, scol=scol, order=order,
                                tooltip_column=15,
                                search=search, skip=skip, sort_map=sort_map,
                                nrgroups = 3,
                                group_can_have_handle = True,
                                has_secondary=False)

    def destroy(self):
        """
        Unset all elements that can prevent garbage collection
        """
        LocationBaseModel.destroy(self)
        self.number_items = None
        TreeBaseModel.destroy(self)

    def _set_base_data(self):
        """See TreeBaseModel, for place, most have been set in init of
        PlaceBaseModel
        """
        self.number_items = self.db.get_number_of_locations

        self.gen_cursor2 = self.db.get_place_cursor
        self.map2 = self.db.get_raw_place_data
        self.fmap2 = [
            self.column_place_name,
            lambda handle, data: u'',
            self.column_place_change,
            self.column_handle,
            ]
        self.smap2 = [
            self.column_place_name,
            lambda handle, data: u'',
            self.sort_place_change,
            self.column_handle,
            ]
        self.number_items2 = self.db.get_number_of_places

    def get_tree_levels(self):
        """
        Return the headings of the levels in the hierarchy.
        """
        return [_('Country'), _('State'), _('County'), _('Place')]

    def add_row(self, handle, data):
        """
        Add nodes to the node map for a single location.

        handle      The handle of the gramps object.
        data        The object data.
        """
        sort_key = self.sort_func(data)
        parent = data[1]

        # Add the node as a root node if the parent is not in the tree.  This
        # will happen when the view is filtered.
        if not self.get_node(parent):
            parent = None

        self.add_node(parent, handle, sort_key, handle, add_parent=False)

    def add_row2(self, handle, data):
        """
        Add nodes to the node map for a single place.

        handle      The handle of the gramps object.
        data        The object data.
        """
        sort_key = self.sort_func2(data)
        parent = data[5]
        
        if self.get_node(parent):
            self.add_node(parent, handle, sort_key, handle, add_parent=False,
                          secondary=True)

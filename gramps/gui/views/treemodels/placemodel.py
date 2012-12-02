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
Place Model.
"""
#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
import cgi
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
# GRAMPS modules
#
#-------------------------------------------------------------------------
from gramps.gen.datehandler import format_time
from gramps.gen.utils.place import conv_lat_lon
from gramps.gen.constfunc import cuni
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
COUNTRYLEVELS = {
'default': [_('<Countries>'), _('<States>'), _('<Counties>'), 
            _('<Places>')]
}

#-------------------------------------------------------------------------
#
# PlaceBaseModel
#
#-------------------------------------------------------------------------
class PlaceBaseModel(object):

    HANDLE_COL = 5

    def __init__(self, db):
        self.gen_cursor = db.get_place_cursor
        self.map = db.get_raw_place_data
        self.fmap = [
            self.column_name,
            self.column_id,
            self.column_location,
            self.column_change,
            self.column_place_name,
            self.column_handle,
            self.column_tooltip
            ]
        self.smap = [
            self.column_name,
            self.column_id,
            self.column_location,
            self.sort_change,
            self.column_place_name,
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

    def do_get_n_columns(self):
        return len(self.fmap)+1

    def column_handle(self, data):
        return cuni(data[0])

    def column_place_name(self, data):
        return cuni(data[2])

    def column_id(self, data):
        return cuni(data[1])

    def column_location(self, data):
        try:
            loc = self.db.get_location_from_handle(data[3])
            lines = [loc.name]
            while loc.parent != str(None):
                loc = self.db.get_location_from_handle(loc.parent)
                lines.append(loc.name)
            return ', '.join(lines)
        except:
            return u''

    def sort_change(self, data):
        return "%012x" % data[9]
    
    def column_change(self, data):
        return format_time(data[9])

    def column_tooltip(self, data):
        return u'Place tooltip'

#-------------------------------------------------------------------------
#
# PlaceListModel
#
#-------------------------------------------------------------------------
class PlaceListModel(PlaceBaseModel, FlatBaseModel):
    """
    Flat place model.  (Original code in PlaceBaseModel).
    """
    def __init__(self, db, scol=0, order=Gtk.SortType.ASCENDING, search=None,
                 skip=set(), sort_map=None):

        PlaceBaseModel.__init__(self, db)
        FlatBaseModel.__init__(self, db, scol, order, tooltip_column=15,
                           search=search, skip=skip, sort_map=sort_map)

    def destroy(self):
        """
        Unset all elements that can prevent garbage collection
        """
        PlaceBaseModel.destroy(self)
        FlatBaseModel.destroy(self)

    def column_name(self, data):
        return cuni(data[2])

#-------------------------------------------------------------------------
#
# PlaceTreeModel
#
#-------------------------------------------------------------------------
class PlaceTreeModel(PlaceBaseModel, TreeBaseModel):
    """
    Hierarchical place model.
    """
    def __init__(self, db, scol=0, order=Gtk.SortType.ASCENDING, search=None,
                 skip=set(), sort_map=None):

        PlaceBaseModel.__init__(self, db)
        TreeBaseModel.__init__(self, db, scol=scol, order=order,
                                tooltip_column=15,
                                search=search, skip=skip, sort_map=sort_map,
                                nrgroups = 3,
                                group_can_have_handle = True)

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
        if data[5] is None:
            # No primary location
            level = [''] * 6
        else:
            #country, state, county, city, locality, street
            level = [data[5][0][i] for i in range(5,-1,-1)]

        node1 = (level[0], )
        node2 = (level[1], level[0])
        node3 = (level[2], level[1], level[0])
        sort_key = self.sort_func(data)

        if not (level[3] or level[4] or level[5]):
            if level[2]:
                self.add_node(None, node1, level[0], None, add_parent=False)
                self.add_node(node1, node2, level[1], None, add_parent=False)
                self.add_node(node2, node3, level[2], None, add_parent=False)
                self.add_node(node3, handle, sort_key, handle, add_parent=False)
            elif level[1]:
                self.add_node(None, node1, level[0], None, add_parent=False)
                self.add_node(node1, node2, level[1], None, add_parent=False)
                self.add_node(node2, handle, level[1], handle, add_parent=False)
            elif level[0]:
                self.add_node(None, node1, level[0], None, add_parent=False)
                self.add_node(node1, handle, level[0], handle, add_parent=False)
            else:
                self.add_node(None, node1, level[0], None, add_parent=False)
                self.add_node(node1, node2, level[1], None, add_parent=False)
                self.add_node(node2, node3, level[2], None, add_parent=False)
                self.add_node(node3, handle, sort_key, handle, add_parent=False)
               
        else:        
            self.add_node(None, node1, level[0], None, add_parent=False)
            self.add_node(node1, node2, level[1], None, add_parent=False)
            self.add_node(node2, node3, level[2], None, add_parent=False)
            self.add_node(node3, handle, sort_key, handle, add_parent=False)

    def column_name(self, data):
        name = ''
        if data[5] is not None:
            level = [data[5][0][i] for i in range(5,-1,-1)]
            if not (level[3] or level[4] or level[5]):
                name = cuni(level[2] or level[1] or level[0])
            else:
                name = ', '.join([item for item in level[3:] if item])
        if not name:
            name = cuni(data[2])

        if name:
            return cgi.escape(name)
        else:
            return "<i>%s<i>" % cgi.escape(_("<no name>"))
        
    def column_header(self, node):
        """
        Return a column heading.  This is called for nodes with no associated
        Gramps handle.
        """
        if node.name:
            return '<i>%s</i>' % cgi.escape(node.name)
        else:
            level = len(self.do_get_path(self.get_iter(node)).get_indices())
            heading = '<i>%s</i>' % cgi.escape(COUNTRYLEVELS['default'][level])
            # This causes a problem with Gtk3 unless we cast to str.
            return str(heading)

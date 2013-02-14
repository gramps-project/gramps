# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham
# Copyright (C) 2008       Gary Burton
# Copyright (C) 2011       Tim G L Lyons
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
Provide the location view.
"""

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
from gramps.gen.ggettext import gettext as _
import logging
_LOG = logging.getLogger(".plugins.locationview")

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.lib import Location
from gramps.gen.db import DbTxn
from gramps.gui.views.listview import ListView, TEXT, MARKUP, ICON
from gramps.gui.views.treemodels import LocationTreeModel
from gramps.gen.errors import WindowActiveError
from gramps.gui.views.bookmarks import PlaceBookmarks
from gramps.gui.ddtargets import DdTargets
from gramps.gui.dialog import ErrorDialog
from gramps.gui.editors import EditLocation
from gramps.gen.plug import CATEGORY_QR_PLACE

#-------------------------------------------------------------------------
#
# LocationView
#
#-------------------------------------------------------------------------
class LocationView(ListView):
    """
    LocationView class, derived from the ListView
    """
    # columns in the model used in view
    COL_NAME = 0
    COL_TYPE = 1
    COL_LAT = 2
    COL_LON = 3
    COL_CHAN = 4
    # column definitions
    COLUMNS = [
        (_('Name'), TEXT, None),
        (_('Type'), TEXT, None),
        (_('Latitude'), TEXT, None),
        (_('Longitude'), TEXT, None),
        (_('Last Changed'), TEXT, None),
        ]
    # default setting with visible columns, order of the col, and their size
    CONFIGSETTINGS = (
        ('columns.visible', [COL_NAME, COL_TYPE]),
        ('columns.rank', [COL_NAME, COL_TYPE, COL_LAT, COL_LON, COL_CHAN]),
        ('columns.size', [400, 100, 150, 150, 100])
        )    
    ADD_MSG     = _("Add a new location")
    EDIT_MSG    = _("Edit the selected location")
    DEL_MSG     = _("Delete the selected location")
    MERGE_MSG   = _("Merge the selected locations")
    FILTER_TYPE = "Place"
    QR_CATEGORY = CATEGORY_QR_PLACE

    def __init__(self, pdata, dbstate, uistate, nav_group=0):
        """
        Create the Location View
        """
        signal_map = {
            'location-add'     : self.row_add,
            'location-update'  : self.row_update,
            'location-delete'  : self.row_delete,
            'location-rebuild' : self.object_build,
            }

        ListView.__init__(
            self, _('Locations'), pdata, dbstate, uistate,
            LocationTreeModel,
            signal_map,
            PlaceBookmarks, nav_group,
            multiple=True)
            
        self.func_list.update({
            '<CONTROL>J' : self.jump,
            '<CONTROL>BackSpace' : self.key_delete,
            })

        self.additional_uis.append(self.additional_ui())

    def navigation_type(self):
        return 'Place'

    def get_bookmarks(self):
        """
        Return the bookmark object
        """
        return self.dbstate.db.get_place_bookmarks()

    def drag_info(self):
        """
        Indicate that the drag type is a PLACE_LINK
        """
        return DdTargets.PLACE_LINK

    def get_stock(self):
        """
        Use the gramps-place stock icon
        """
        return 'gramps-place'

    def additional_ui(self):
        """
        Defines the UI string for UIManager
        """
        return '''<ui>
          <menubar name="MenuBar">
            <menu action="BookMenu">
              <placeholder name="AddEditBook">
                <menuitem action="AddBook"/>
                <menuitem action="EditBook"/>
              </placeholder>
            </menu>
            <menu action="GoMenu">
              <placeholder name="CommonGo">
                <menuitem action="Back"/>
                <menuitem action="Forward"/>
                <separator/>
              </placeholder>
            </menu>
            <menu action="FileMenu">
              <placeholder name="LocalExport">
                <menuitem action="ExportTab"/>
              </placeholder>
            </menu>
            <menu action="EditMenu">
              <placeholder name="CommonEdit">
                <menuitem action="Add"/>
                <menuitem action="Edit"/>
                <menuitem action="Remove"/>
                <menuitem action="Merge"/>
              </placeholder>
            </menu>
          </menubar>
          <toolbar name="ToolBar">
            <placeholder name="CommonNavigation">
              <toolitem action="Back"/>  
              <toolitem action="Forward"/>  
            </placeholder>
            <placeholder name="CommonEdit">
              <toolitem action="Add"/>
              <toolitem action="Edit"/>
              <toolitem action="Remove"/>
            </placeholder>
          </toolbar>
          <popup name="Popup">
            <menuitem action="OpenBranch"/>
            <menuitem action="CloseBranch"/>
            <menuitem action="OpenAllNodes"/>
            <menuitem action="CloseAllNodes"/>
            <separator/>
            <menuitem action="Add"/>
            <menuitem action="Edit"/>
            <menuitem action="Remove"/>
            <menuitem action="Merge"/>
            <separator/>
            <menu name="QuickReport" action="QuickReport">
              <menuitem action="Dummy"/>
            </menu>
          </popup>
        </ui>'''

    def define_actions(self):
        ListView.define_actions(self)
        self._add_action('QuickReport', None, 
                         _("Quick View"), None, None, None)
        self._add_action('Dummy', None, 
                         '  ', None, None, self.dummy_report)

        self._add_action('OpenBranch', None, _("Expand this Entire Group"),
                         callback=self.open_branch)
        self._add_action('CloseBranch', None, _("Collapse this Entire Group"),
                         callback=self.close_branch)
        self._add_action('OpenAllNodes', None, _("Expand all Nodes"),
                         callback=self.open_all_nodes)
        self._add_action('CloseAllNodes', None, _("Collapse all Nodes"),
                         callback=self.close_all_nodes)

    def get_handle_from_gramps_id(self, gid):
        obj = self.dbstate.db.get_place_from_gramps_id(gid)
        if obj:
            return obj.get_handle()
        else:
            return None

    def add(self, obj):
        loc = Location()
        selected = self.selected_handles()
        if len(selected) == 1:
            loc.parent = selected[0]
            parent_loc = self.dbstate.db.get_location_from_handle(selected[0])
            parent_type = parent_loc.get_type()
            if parent_type < 7:
                loc.set_type(parent_type + 1)
            else:
                loc.set_type(7)
        try:
            EditLocation(self.dbstate, self.uistate, [], loc, None)
        except WindowActiveError:
            pass

    def remove(self, obj):
        for handle in self.selected_handles():
            place_list = [
                item[1] for item in
                self.dbstate.db.find_backlink_handles(handle, ['Place'])]
            children = [handle for handle in 
                        self.dbstate.db.find_location_child_handles(handle)]
            if place_list or children:
                msg = _("Cannot remove location object.")
                msg2 = _("The location is in use.")
                ErrorDialog(msg, msg2)
            else:
                location = self.dbstate.db.get_location_from_handle(handle)
                with DbTxn(_("Delete Location (%s)") % location.get_name(),
                           self.dbstate.db) as trans:
                    self.dbstate.db.remove_location(handle, trans)

    def edit(self, obj):
        for handle in self.selected_handles():
            loc = self.dbstate.db.get_location_from_handle(handle)
            try:
                EditLocation(self.dbstate, self.uistate, [], loc, None)
            except WindowActiveError:
                pass

    def merge(self, obj):
        """
        Merge the selected locations.
        """
        msg = _("Not yet implemented.")
        ErrorDialog(msg, msg)

    def dummy_report(self, obj):
        """ For the xml UI definition of popup to work, the submenu 
            Quick Report must have an entry in the xml
            As this submenu will be dynamically built, we offer a dummy action
        """
        pass

    def tag_updated(self, handle_list):
        """
        Update tagged rows when a tag color changes.
        """
        pass

    def get_default_gramplets(self):
        """
        Define the default gramplets for the sidebar and bottombar.
        """
        return ((), ())

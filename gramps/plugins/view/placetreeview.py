# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009-2010  Nick Hall
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
Place Tree View
"""

from __future__ import unicode_literals

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gui.views.listview import TEXT, MARKUP, ICON
from gramps.plugins.lib.libplaceview import PlaceBaseView
from gramps.gui.views.treemodels.placemodel import PlaceTreeModel, COUNTRYLEVELS
from gramps.gen.lib import Place
from gramps.gen.errors import WindowActiveError
from gramps.gui.editors import EditPlace

#-------------------------------------------------------------------------
#
# Internationalization
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.get_translation().gettext

#-------------------------------------------------------------------------
#
# PlaceTreeView
#
#-------------------------------------------------------------------------
class PlaceTreeView(PlaceBaseView):
    """
    A hierarchical view of the top three levels of places.
    """
    COL_PLACE = 0
    COL_ID = 1
    COL_STREET = 2
    COL_LOCALITY = 3
    COL_CITY = 4
    COL_COUNTY = 5
    COL_STATE = 6
    COL_COUNTRY = 7
    COL_ZIP = 8
    COL_PARISH = 9
    COL_LAT = 10
    COL_LON = 11
    COL_PRIV = 12
    COL_TAGS = 13
    COL_CHAN = 14
    COL_NAME = 15
    # column definitions
    COLUMNS = [
        (_('Place'), MARKUP, None),
        (_('ID'), TEXT, None),
        (_('Street'), TEXT, None),
        (_('Locality'), TEXT, None),
        (_('City'), TEXT, None),
        (_('County'), TEXT, None),
        (_('State'), TEXT, None),
        (_('Country'), TEXT, None),
        (_('ZIP/Postal Code'), TEXT, None),
        (_('Church Parish'), TEXT, None),
        (_('Latitude'), TEXT, None),
        (_('Longitude'), TEXT, None),
        (_('Private'), ICON, 'gramps-lock'),
        (_('Tags'), TEXT, None),
        (_('Last Changed'), TEXT, None),
        (_('Place Name'), TEXT, None),
        ]
    # default setting with visible columns, order of the col, and their size
    CONFIGSETTINGS = (
        ('columns.visible', [COL_PLACE, COL_ID, COL_STREET, COL_LOCALITY,
                             COL_CITY, COL_COUNTY, COL_STATE]),
        ('columns.rank', [COL_PLACE, COL_ID, COL_STREET, COL_LOCALITY, COL_CITY,
                           COL_COUNTY, COL_STATE, COL_COUNTRY, COL_ZIP,
                           COL_PARISH, COL_LAT, COL_LON, COL_PRIV, COL_TAGS, 
                           COL_CHAN, COL_NAME]),
        ('columns.size', [250, 75, 150, 150, 150, 150, 100, 100, 100, 
                             100, 150, 150, 40, 100, 100, 150])
        )    

    def __init__(self, pdata, dbstate, uistate):
        PlaceBaseView.__init__(self, pdata, dbstate, uistate,
                               _('Place Tree View'), PlaceTreeModel,
                               nav_group=0)

    def get_viewtype_stock(self):
        """
        Override the default icon.  Set for hierarchical view.
        """
        return 'gramps-tree-group'
        
    def define_actions(self):
        """
        Define actions for the popup menu specific to the tree view.
        """
        PlaceBaseView.define_actions(self)
        
        self._add_action('OpenBranch', None, _("Expand this Entire Group"),
                         callback=self.open_branch)
        self._add_action('CloseBranch', None, _("Collapse this Entire Group"),
                         callback=self.close_branch)
        self._add_action('OpenAllNodes', None, _("Expand all Nodes"),
                         callback=self.open_all_nodes)
        self._add_action('CloseAllNodes', None, _("Collapse all Nodes"),
                         callback=self.close_all_nodes)

    def additional_ui(self):
        """
        A user interface definition including tree specific actions.
        """
        return '''<ui>
          <menubar name="MenuBar">
            <menu action="FileMenu">
              <placeholder name="LocalExport">
                <menuitem action="ExportTab"/>
              </placeholder>
            </menu>
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
            <menu action="EditMenu">
              <placeholder name="CommonEdit">
                <menuitem action="Add"/>
                <menuitem action="Edit"/>
                <menuitem action="Remove"/>
                <menuitem action="Merge"/>
              </placeholder>
              <menuitem action="FilterEdit"/>
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
              <toolitem action="Merge"/>
              <separator/>
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
            <menu name="QuickReport" action="QuickReport"/>
            <separator/>
            <menuitem action="GotoMap"/>
          </popup>
        </ui>'''

    def add(self, obj):
        """
        Add a new place.  Attempt to get the top three levels of hierarchy from
        the currently selected row.
        """
        place = Place()
        
        model, pathlist = self.selection.get_selected_rows()
        level = ["", "", ""]
        level1 = level2 = level3 = ""
        if len(pathlist) == 1:
            path = pathlist[0]
            iter_ = model.get_iter(path)
            if iter_:
                if len(path) == 1:
                    level[0] = model.get_node_from_iter(iter_).name
                elif len(path) == 2:
                    level[1] = model.get_node_from_iter(iter_).name
                    parent = model.iter_parent(iter_)
                    level[0] = model.get_node_from_iter(parent).name
                elif len(path) == 3:
                    level[2] = model.get_node_from_iter(iter_).name
                    parent = model.iter_parent(iter_)
                    level[1] = model.get_node_from_iter(parent).name
                    parent = model.iter_parent(parent)
                    level[0] = model.get_node_from_iter(parent).name
                else:
                    parent = model.iter_parent(iter_)
                    level[2] = model.get_node_from_iter(parent).name
                    parent = model.iter_parent(parent)
                    level[1] = model.get_node_from_iter(parent).name
                    parent = model.iter_parent(parent)
                    level[0] = model.get_node_from_iter(parent).name

        for ind in [0, 1, 2]: 
            if level[ind] and level[ind] == COUNTRYLEVELS['default'][ind+1]:
                level[ind] = ""
        place.get_main_location().set_country(level[0])
        place.get_main_location().set_state(level[1])
        place.get_main_location().set_county(level[2])
        try:
            EditPlace(self.dbstate, self.uistate, [], place)
        except WindowActiveError:
            pass

# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009       Nick Hall
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

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gui.views.listview import LISTTREE
from gui.views.placebaseview import PlaceBaseView
from gui.views.treemodels.placetreemodel import PlaceTreeModel, COUNTRYLEVELS
import gen.lib
import Errors
from gui.editors import EditPlace

#-------------------------------------------------------------------------
#
# Internationalization
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# PlaceTreeView
#
#-------------------------------------------------------------------------
class PlaceTreeView(PlaceBaseView):
    """
    A hierarchical view of the top three levels of places.
    """

    def __init__(self, dbstate, uistate):
        PlaceBaseView.__init__(self, dbstate, uistate,
                               _('Tree'), PlaceTreeModel,
                               nav_group=0, markup=True)

    def type_list(self):
        """
        set the listtype, this governs eg keybinding
        """
        return LISTTREE

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

    def ui_definition(self):
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
            <menu action="EditMenu">
              <placeholder name="CommonEdit">
                <menuitem action="Add"/>
                <menuitem action="Edit"/>
                <menuitem action="Remove"/>
              </placeholder>
              <menuitem action="ColumnEdit"/>
              <menuitem action="FilterEdit"/>
              <placeholder name="Merge">
                <menuitem action="FastMerge"/>
              </placeholder>
            </menu>
          </menubar>
          <toolbar name="ToolBar">
            <placeholder name="CommonEdit">
              <toolitem action="Add"/>
              <toolitem action="Edit"/>
              <toolitem action="Remove"/>
              <separator/>
              <toolitem action="MapsList"/>
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
            <separator/>
            <menu name="QuickReport" action="QuickReport">
              <menuitem action="Dummy"/>
            </menu>
            <separator/>
            <menuitem action="GotoMap"/>
          </popup>
        </ui>'''

    def add(self, obj):
        """
        Add a new place.  Attempt to get the top three levels of hierarchy from
        the currently selected row.
        """
        place = gen.lib.Place()
        
        model, pathlist = self.selection.get_selected_rows()
        level = [u"", u"", u""]
        level1 = level2 = level3 = u""
        if len(pathlist) == 1:
            path = pathlist[0]
            node = model.on_get_iter(path)
            value = model.on_get_value(node, 0)
            
            if len(path) == 1:
                level[0] = node.name
            elif len(path) == 2:
                level[1] = node.name
                parent = model.on_iter_parent(node)
                level[0] = parent.name
            elif len(path) == 3:
                level[2] = node.name
                parent = model.on_iter_parent(node)
                level[1] = parent.name
                parent = model.on_iter_parent(parent)
                level[0] = parent.name
            else:
                parent = model.on_iter_parent(node)
                level[2] = parent.name
                parent = model.on_iter_parent(parent)
                level[1] = parent.name
                parent = model.on_iter_parent(parent)
                level[0] = parent.name

        for ind in [0, 1, 2]: 
            if level[ind] and level[ind] == COUNTRYLEVELS['default'][ind+1]:
                level[ind] = u""
        place.get_main_location().set_country(level[0])
        place.get_main_location().set_state(level[1])
        place.get_main_location().set_county(level[2])
        try:
            EditPlace(self.dbstate, self.uistate, [], place)
        except Errors.WindowActiveError:
            pass

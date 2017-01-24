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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Place Tree View
"""

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gui.views.listview import ListView, TEXT, ICON
from gramps.plugins.lib.libplaceview import PlaceBaseView
from gramps.gui.views.treemodels.placemodel import PlaceTreeModel
from gramps.gen.lib import Place, PlaceRef
from gramps.gen.errors import WindowActiveError
from gramps.gui.editors import EditPlace

#-------------------------------------------------------------------------
#
# Internationalization
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

#-------------------------------------------------------------------------
#
# PlaceTreeView
#
#-------------------------------------------------------------------------
class PlaceTreeView(PlaceBaseView):
    """
    A hierarchical view of the top three levels of places.
    """
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
        Add a new place.  Use the currently selected rows as parent places.
        """
        parent_list = []
        for handle in self.selected_handles():
            placeref = PlaceRef()
            placeref.ref = handle
            parent_list.append(placeref)

        place = Place()
        if len(parent_list) > 0:
            place.placeref_list = parent_list

        try:
            EditPlace(self.dbstate, self.uistate, [], place)
        except WindowActiveError:
            pass

    def row_update(self, handle_list):
        """
        Called when a place is updated.
        """
        ListView.row_update(self, handle_list)

        for handle in handle_list:
            # Rebuild the model if the primary parent has changed.
            if self._parent_changed(handle):
                self.build_tree()
                break

    def _parent_changed(self, handle):
        """
        Return True if the primary parent is different from the parent
        displayed in the tree, else return False.
        """
        new_handle = None
        place = self.dbstate.db.get_place_from_handle(handle)
        placeref_list = place.get_placeref_list()
        if len(placeref_list) > 0:
            new_handle = placeref_list[0].ref

        old_handle = None
        iter_ = self.model.get_iter_from_handle(handle)
        if iter_:
            parent_iter = self.model.iter_parent(iter_)
            if parent_iter:
                old_handle = self.model.get_handle_from_iter(parent_iter)

        return True if new_handle != old_handle else False

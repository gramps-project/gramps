# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2008       Gary Burton
# Copyright (C) 2009       Nick Hall
# Copyright (C) 2010       Benny Malengier
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

# $Id: placetreeview.py 14176 2010-02-01 07:01:45Z bmcage $

"""
Person Tree View
"""

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gui.views.listview import LISTTREE
from libpersonview import BasePersonView
from gui.views.treemodels.peoplemodel import PersonTreeModel
import gen.lib
import Errors
from gui.editors import EditPerson

#-------------------------------------------------------------------------
#
# Internationalization
#
#-------------------------------------------------------------------------
from gen.ggettext import gettext as _

#-------------------------------------------------------------------------
#
# PlaceTreeView
#
#-------------------------------------------------------------------------
class PersonTreeView(BasePersonView):
    """
    A hierarchical view of the top three levels of places.
    """
    def __init__(self, dbstate, uistate, nav_group=0):
        BasePersonView.__init__(self, dbstate, uistate,
                               _('People'), PersonTreeModel,
                               nav_group=nav_group)

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
        BasePersonView.define_actions(self)

        self.all_action.add_actions([
                ('OpenAllNodes', None, _("Expand all Nodes"), None, None, 
                 self.open_all_nodes),  
                ('CloseAllNodes', None, _("Collapse all Nodes"), None, None, 
                 self.close_all_nodes), 
                ])

    def ui_definition(self):
        """
        Defines the UI string for UIManager
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
                <menuitem action="HomePerson"/>
                <separator/>
              </placeholder>
            </menu>
            <menu action="EditMenu">
              <placeholder name="CommonEdit">
                <menuitem action="Add"/>
                <menuitem action="Edit"/>
                <menuitem action="Remove"/>
              </placeholder>
              <menuitem action="SetActive"/>
              <menuitem action="FilterEdit"/>
              <placeholder name="Merge">
                <menuitem action="CmpMerge"/>
                <menuitem action="FastMerge"/>
              </placeholder>
            </menu>
          </menubar>
          <toolbar name="ToolBar">
            <placeholder name="CommonNavigation">
              <toolitem action="Back"/>  
              <toolitem action="Forward"/>  
              <toolitem action="HomePerson"/>
            </placeholder>
            <placeholder name="CommonEdit">
              <toolitem action="Add"/>
              <toolitem action="Edit"/>
              <toolitem action="Remove"/>
            </placeholder>
          </toolbar>
          <popup name="Popup">
            <menuitem action="Back"/>
            <menuitem action="Forward"/>
            <menuitem action="HomePerson"/>
            <separator/>
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
          </popup>
        </ui>'''

    def add(self, obj):
        person = gen.lib.Person()
        
        # attempt to get the current surname
        (model, pathlist) = self.selection.get_selected_rows()
        name = u""
        if len(pathlist) == 1:
            path = pathlist[0]
            if len(path) == 1:
                name = model.on_get_iter(path).name
            else:
                node = model.on_get_iter(path)
                name = model.on_iter_parent(node).name

        try:
            person.get_primary_name().set_surname(name)
            EditPerson(self.dbstate, self.uistate, [], person)
        except Errors.WindowActiveError:
            pass

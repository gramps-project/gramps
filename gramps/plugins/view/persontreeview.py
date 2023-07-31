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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Person Tree View
"""

# -------------------------------------------------------------------------
#
# GTK modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gui.views.listview import TEXT, MARKUP, ICON
from gramps.plugins.lib.libpersonview import BasePersonView
from gramps.gui.views.treemodels.peoplemodel import PersonTreeModel
from gramps.gen.lib import Name, Person, Surname
from gramps.gen.errors import WindowActiveError
from gramps.gui.editors import EditPerson
from gramps.gen.utils.db import preset_name

# -------------------------------------------------------------------------
#
# Internationalization
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext


# -------------------------------------------------------------------------
#
# PersonTreeView
#
# -------------------------------------------------------------------------
class PersonTreeView(BasePersonView):
    """
    A hierarchical view of the people based on family name.
    """

    def __init__(self, pdata, dbstate, uistate, nav_group=0):
        BasePersonView.__init__(
            self,
            pdata,
            dbstate,
            uistate,
            _("People Tree View"),
            PersonTreeModel,
            nav_group=nav_group,
        )

    def get_viewtype_stock(self):
        """
        Override the default icon.  Set for hierarchical view.
        """
        return "gramps-tree-group"

    def define_actions(self):
        """
        Define actions for the popup menu specific to the tree view.
        """
        BasePersonView.define_actions(self)

        self.action_list.extend(
            [
                ("OpenAllNodes", self.open_all_nodes),
                ("CloseAllNodes", self.close_all_nodes),
            ]
        )

    additional_ui = BasePersonView.additional_ui[:]
    additional_ui.append(  # Defines the UI string for UIManager
        """
      <section id="PopUpTree">
        <item>
          <attribute name="action">win.OpenAllNodes</attribute>
          <attribute name="label" translatable="yes">"""
        """Expand all Nodes</attribute>
        </item>
        <item>
          <attribute name="action">win.CloseAllNodes</attribute>
          <attribute name="label" translatable="yes">"""
        """Collapse all Nodes</attribute>
        </item>
      </section>
    """
    )

    def add(self, *obj):
        person = Person()

        # attempt to get the current surname
        (model, pathlist) = self.selection.get_selected_rows()
        name = Name()
        # the editor requires a surname
        name.add_surname(Surname())
        name.set_primary_surname(0)
        basepers = None
        if len(pathlist) == 1:
            path = pathlist[0]
            pathids = path.get_indices()
            if len(pathids) == 1:
                path = Gtk.TreePath((pathids[0], 0))
            iter_ = model.get_iter(path)
            handle = model.get_handle_from_iter(iter_)
            basepers = self.dbstate.db.get_person_from_handle(handle)
        if basepers:
            preset_name(basepers, name)
        person.set_primary_name(name)
        try:
            EditPerson(self.dbstate, self.uistate, [], person)
        except WindowActiveError:
            pass

    def get_config_name(self):
        return __name__

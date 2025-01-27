#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2010       Gary Burton
# Copyright (C) 2010       Jakim Friant
# Copyright (C) 2025       Steve Youngs
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

"""Tools/Utilities/Relationship Calculator"""

# -------------------------------------------------------------------------
#
# Standard python modules
#
# -------------------------------------------------------------------------
from __future__ import annotations

# -------------------------------------------------------------------------
#
# GNOME libraries
#
# -------------------------------------------------------------------------
from gi.repository import Gdk
from gi.repository import Gtk

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext
from gramps.gen.dbstate import DbState
from gramps.gen.display.name import displayer as name_displayer
from gramps.gui.managedwindow import ManagedWindow
from gramps.gui.views.treemodels import PeopleBaseModel, PersonTreeModel
from gramps.plugins.lib.libpersonview import BasePersonView
from gramps.gen.relationship import get_relationship_calculator
from gramps.gen.const import URL_MANUAL_PAGE
from gramps.gui.display import display_help

from gramps.gui.dialog import ErrorDialog
from gramps.gui.plug import tool
from gramps.gui.glade import Glade
from gramps.gui.selectors.selectperson import SelectPerson

# -------------------------------------------------------------------------
#
# Constants
#
# -------------------------------------------------------------------------

WIKI_HELP_PAGE = URL_MANUAL_PAGE + "_-_Tools"
WIKI_HELP_SEC = _("Relationship Calculator")


# -------------------------------------------------------------------------
#
#
#
# -------------------------------------------------------------------------
class RelCalc(tool.Tool, SelectPerson):
    def __init__(self, dbstate: DbState, user, options_class, name, callback=None):
        """
        Relationship calculator class.
        """
        uistate = user.uistate
        self.history = uistate.get_history("Person")
        self.history_connection: int = self.history.connect(
            "active-changed", self.active_changed
        )

        self.relationship = get_relationship_calculator(glocale)

        self.WIKI_HELP_PAGE = WIKI_HELP_PAGE
        self.WIKI_HELP_SEC = WIKI_HELP_SEC

        tool.Tool.__init__(self, dbstate, options_class, name)
        SelectPerson.__init__(
            self,
            dbstate,
            uistate,
            show_search_bar=True,
        )

        # add a scrolling text view to the end of "select_person_vbox"
        vbox = self.glade.get_object("select_person_vbox")
        self.relationship_window = Gtk.ScrolledWindow()
        self.relationship_window.set_can_focus(False)
        self.relationship_window.set_min_content_height(75)
        self.relationship_window.set_shadow_type(Gtk.ShadowType.IN)

        self.relationship_view = Gtk.TextView()
        self.relationship_buffer = Gtk.TextBuffer()
        self.relationship_view.set_buffer(self.relationship_buffer)
        self.relationship_view.set_wrap_mode(Gtk.WrapMode.WORD)

        self.relationship_window.add(self.relationship_view)
        vbox.pack_end(self.relationship_window, False, False, 0)

        self.relationship_view.show()
        self.relationship_window.show()

        # relabel the OK button as Close and hide the Cancel button
        okbutton = self.glade.get_object("okbutton1")
        okbutton.set_label(_("Close"))
        self.closebtn = self.glade.get_object("button5")
        okbutton.connect("clicked", self.close)
        self.glade.get_object("cancelbutton1").hide()

        # set the window to modeless
        self.glade.get_object("baseselector").set_modal(False)

        # connect to changes in selection in the tree
        self.selection.connect("changed", self._sel_changed)

        self.person = None  # the active person
        self.other_person = None  # the person selected in the tree

        # refresh the UI based on the currently active person
        self.active_changed(uistate.get_active("Person"))

    def _connect_db_signals(self):
        # any change to a family might alter the relationship to the active person
        self.db_connections.append(self.db.connect("family-add", self.family_callback))
        self.db_connections.append(
            self.db.connect("family-delete", self.family_callback)
        )
        self.db_connections.append(
            self.db.connect("family-update", self.family_callback)
        )

    def _sel_changed(self, obj):
        """
        the person selected in the tree has changed
        update other_person and update the relationship
        """
        self.other_person = None
        model, iter_ = obj.get_selected()
        if iter_:
            handle = model.get_handle_from_iter(iter_)
            if handle:
                self.other_person = self.db.get_person_from_handle(handle)

        self.update_relationship()

    def family_callback(self, handle_list):
        """
        There has been a change to a family.
        recalculate the relationship
        """
        self.update_relationship()

    def update_relationship(self):
        relationship = ""
        if self.person and self.other_person:
            relationship = self._calc_relationship(self.person, self.other_person)

        self.relationship_buffer.set_text(relationship)

    def active_changed(self, handle) -> None:
        """
        Method called when active person changes.
        """
        title: str = _("Active person has not been set")
        self.person = None
        handle = self.uistate.get_active("Person")
        if handle:
            self.person = self.dbstate.db.get_person_from_handle(handle)
            name: str = name_displayer.display(self.person) if self.person else ""

            title = _("Relationship to %(person_name)s") % {"person_name": name}
        self.update_title(title)
        self.update_relationship()

    def _calc_relationship(self, person, other_person):
        rel_strings, common_an = self.relationship.get_all_relationships(
            self.db, person, other_person
        )

        p1 = name_displayer.display(person)
        p2 = name_displayer.display(other_person)

        text = []
        if person.handle == other_person.handle:
            rstr = _("%(person)s and %(active_person)s are the same person.") % {
                "person": p1,
                "active_person": p2,
            }
            text.append((rstr, ""))
        elif len(rel_strings) == 0:
            rstr = _("%(person)s and %(active_person)s are not related.") % {
                "person": p2,
                "active_person": p1,
            }
            text.append((rstr, ""))

        for rel_string, common in zip(rel_strings, common_an):
            rstr = _("%(person)s is the %(relationship)s of %(active_person)s.") % {
                "person": p2,
                "relationship": rel_string,
                "active_person": p1,
            }
            length = len(common)
            if length == 1:
                person = self.db.get_person_from_handle(common[0])
                if common[0] in [other_person.handle, person.handle]:
                    commontext = ""
                else:
                    name = name_displayer.display(person)
                    commontext = " " + _("Their common ancestor is %s.") % name
            elif length == 2:
                p1c = self.db.get_person_from_handle(common[0])
                p2c = self.db.get_person_from_handle(common[1])
                p1str = name_displayer.display(p1c)
                p2str = name_displayer.display(p2c)
                commontext = " " + _(
                    "Their common ancestors are %(ancestor1)s and %(ancestor2)s."
                ) % {"ancestor1": p1str, "ancestor2": p2str}
            elif length > 2:
                index = 0
                commontext = " " + _("Their common ancestors are: ")
                for person_handle in common:
                    person = self.db.get_person_from_handle(person_handle)
                    if index:
                        # TODO for Arabic, should the next comma be translated?
                        commontext += ", "
                    commontext += name_displayer.display(person)
                    index += 1
                commontext += "."
            else:
                commontext = ""
            text.append((rstr, commontext))

        relationship = ""
        for val in text:
            relationship += "%s %s\n" % (val[0], val[1])
        return relationship

    def _on_row_activated(self, treeview, path, view_col):
        pass

    def close(self, *obj):
        """Close relcalc tool. Remove non-gtk connections so garbage
        collection can do its magic.
        """
        self.history.disconnect(self.history_connection)

        SelectPerson.close(self, *obj)

    def build_menu_names(self, obj):
        return (_("Relationship Calculator tool"), None)


# ------------------------------------------------------------------------
#
#
#
# ------------------------------------------------------------------------
class RelCalcOptions(tool.ToolOptions):
    """
    Defines options and provides handling interface.
    """

    def __init__(self, name, person_id=None):
        tool.ToolOptions.__init__(self, name, person_id)

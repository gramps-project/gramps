#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2009       Gary Burton
# Copyright (C) 2010       Nick Hall
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
The EditAddress module provides the EditAddress class. This provides a
mechanism for the user to edit address information.
"""

# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------

# -------------------------------------------------------------------------
#
# GTK/Gnome modules
#
# -------------------------------------------------------------------------
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

# -------------------------------------------------------------------------
#
# gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext
from .editsecondary import EditSecondary
from gramps.gen.lib import NoteType
from ..glade import Glade
from .displaytabs import CitationEmbedList, NoteTab
from ..widgets import MonitoredDate, MonitoredEntry, PrivacyButton
from gramps.gen.const import URL_MANUAL_SECT3

# -------------------------------------------------------------------------
#
# Constants
#
# -------------------------------------------------------------------------

WIKI_HELP_PAGE = URL_MANUAL_SECT3
WIKI_HELP_SEC = _("Address_Editor_dialog", "manual")


# -------------------------------------------------------------------------
#
# EditAddress class
#
# -------------------------------------------------------------------------
class EditAddress(EditSecondary):
    """
    Displays a dialog that allows the user to edit an address.
    """

    def __init__(self, dbstate, uistate, track, addr, callback):
        """
        Displays the dialog box.

        parent - The class that called the Address editor.
        addr - The address that is to be edited
        """
        EditSecondary.__init__(self, dbstate, uistate, track, addr, callback)

    def _local_init(self):
        self.top = Glade()
        self.set_window(
            self.top.toplevel, self.top.get_object("title"), _("Address Editor")
        )
        self.setup_configs("interface.address", 650, 450)

    def _setup_fields(self):
        self.addr_start = MonitoredDate(
            self.top.get_object("date_entry"),
            self.top.get_object("date_stat"),
            self.obj.get_date_object(),
            self.uistate,
            self.track,
            self.db.readonly,
        )

        self.street = MonitoredEntry(
            self.top.get_object("street"),
            self.obj.set_street,
            self.obj.get_street,
            self.db.readonly,
        )

        self.city = MonitoredEntry(
            self.top.get_object("city"),
            self.obj.set_city,
            self.obj.get_city,
            self.db.readonly,
        )

        self.locality = MonitoredEntry(
            self.top.get_object("locality"),
            self.obj.set_locality,
            self.obj.get_locality,
            self.db.readonly,
        )

        self.state = MonitoredEntry(
            self.top.get_object("state"),
            self.obj.set_state,
            self.obj.get_state,
            self.db.readonly,
        )

        self.country = MonitoredEntry(
            self.top.get_object("country"),
            self.obj.set_country,
            self.obj.get_country,
            self.db.readonly,
        )

        self.postal = MonitoredEntry(
            self.top.get_object("postal"),
            self.obj.set_postal_code,
            self.obj.get_postal_code,
            self.db.readonly,
        )

        self.phone = MonitoredEntry(
            self.top.get_object("phone"),
            self.obj.set_phone,
            self.obj.get_phone,
            self.db.readonly,
        )

        self.priv = PrivacyButton(
            self.top.get_object("private"), self.obj, self.db.readonly
        )

    def _connect_signals(self):
        self.define_cancel_button(self.top.get_object("cancel"))
        self.define_ok_button(self.top.get_object("ok"), self.save)
        self.define_help_button(
            self.top.get_object("help"), WIKI_HELP_PAGE, WIKI_HELP_SEC
        )

    def _create_tabbed_pages(self):
        """
        Create the notebook tabs and inserts them into the main
        window.
        """

        notebook = Gtk.Notebook()

        self.srcref_list = CitationEmbedList(
            self.dbstate,
            self.uistate,
            self.track,
            self.obj.get_citation_list(),
            "address_editor_citations",
        )
        self._add_tab(notebook, self.srcref_list)
        self.track_ref_for_deletion("srcref_list")

        self.note_tab = NoteTab(
            self.dbstate,
            self.uistate,
            self.track,
            self.obj.get_note_list(),
            "address_editor_notes",
            notetype=NoteType.ADDRESS,
        )
        self._add_tab(notebook, self.note_tab)
        self.track_ref_for_deletion("note_tab")

        self._setup_notebook_tabs(notebook)
        notebook.show_all()
        self.top.get_object("vbox").pack_start(notebook, True, True, 0)

    def build_menu_names(self, obj):
        return (_("Address"), _("Address Editor"))

    def save(self, *obj):
        """
        Called when the OK button is pressed. Gets data from the
        form and updates the Address data structure.
        """
        if self.callback:
            self.callback(self.obj)
        self.close()

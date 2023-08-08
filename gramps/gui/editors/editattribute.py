#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
#               2009       Gary Burton
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
The EditAttribute module provides the AttributeEditor class. This provides a
mechanism for the user to edit attribute information.
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
from ..widgets import MonitoredEntry, PrivacyButton, MonitoredDataType
from gramps.gen.const import URL_MANUAL_SECT3

# -------------------------------------------------------------------------
#
# Constants
#
# -------------------------------------------------------------------------

WIKI_HELP_PAGE = URL_MANUAL_SECT3
WIKI_HELP_SEC = _("Attribute_Editor_dialog", "manual")


# -------------------------------------------------------------------------
#
# EditAttribute class
#
# -------------------------------------------------------------------------
class EditAttributeRoot(EditSecondary):
    """
    Root baseclass for the root Attribute data editor
    """

    def __init__(self, state, uistate, track, attrib, title, data_list, callback):
        """
        Displays the dialog box.

        state - dbstate
        uistate - the uistate
        track - list of parent windows
        attrib - The attribute that is to be edited
        title - The title of the dialog box
        data_list - list of options for the pop down menu to help selection of a
               attribute type
        """
        self.alist = data_list
        EditSecondary.__init__(self, state, uistate, track, attrib, callback)

    def _local_init(self):
        self.top = Glade("editattribute.glade")

        self.set_window(
            self.top.toplevel, self.top.get_object("title"), _("Attribute Editor")
        )
        self.setup_configs("interface.attribute", 600, 350)

    def _connect_signals(self):
        self.define_cancel_button(self.top.get_object("cancel"))
        self.define_ok_button(self.top.get_object("ok"), self.save)
        self.define_help_button(
            self.top.get_object("help"), WIKI_HELP_PAGE, WIKI_HELP_SEC
        )

    def _setup_fields(self):
        self.value_field = MonitoredEntry(
            self.top.get_object("attr_value"),
            self.obj.set_value,
            self.obj.get_value,
            self.db.readonly,
        )

        self.priv = PrivacyButton(
            self.top.get_object("private"), self.obj, self.db.readonly
        )

        self.type_selector = MonitoredDataType(
            self.top.get_object("attr_menu"),
            self.obj.set_type,
            self.obj.get_type,
            self.db.readonly,
            custom_values=self.alist,
        )

    def _create_tabbed_pages(self):
        notebook = Gtk.Notebook()

        self._setup_notebook_tabs(notebook)
        notebook.show_all()
        self.top.get_object("vbox").pack_start(notebook, True, True, 0)

    def build_menu_names(self, attrib):
        if not attrib:
            label = _("New Attribute")
        else:
            label = str(attrib.get_type())
        if not label.strip():
            label = _("New Attribute")
        label = _("%(str1)s: %(str2)s") % {"str1": _("Attribute"), "str2": label}
        return (label, _("Attribute Editor"))

    def save(self, *obj):
        """
        Called when the OK button is pressed. Gets data from the
        form and updates the Attribute data structure.
        """
        t = self.obj.get_type()

        if t.is_custom() and str(t) == "":
            from ..dialog import ErrorDialog

            ErrorDialog(
                _("Cannot save attribute"),
                _("The attribute type cannot be empty"),
                parent=self.window,
            )
            return
        if self.callback:
            self.callback(self.obj)
        self.close()


# -------------------------------------------------------------------------
#
# EditSrcAttribute class
#
# -------------------------------------------------------------------------
class EditSrcAttribute(EditAttributeRoot):
    """
    Source attribute are minimal attributes. This Displays the editor to
    edit these.
    """

    def __init__(self, state, uistate, track, attrib, title, data_list, callback):
        """
        Displays the dialog box.

        state - dbstate
        uistate - the uistate
        track - list of parent windows
        attrib - The attribute that is to be edited
        title - The title of the dialog box
        data_list - list of options for the pop down menu to help selection of a
               attribute type
        """
        EditAttributeRoot.__init__(
            self, state, uistate, track, attrib, title, data_list, callback
        )


# -------------------------------------------------------------------------
#
# EditAttribute class
#
# -------------------------------------------------------------------------
class EditAttribute(EditAttributeRoot):
    """
    Displays a dialog that allows the user to edit an attribute.
    """

    def __init__(self, state, uistate, track, attrib, title, data_list, callback):
        """
        Displays the dialog box.

        state - dbstate
        uistate - the uistate
        track - list of parent windows
        attrib - The attribute that is to be edited
        title - The title of the dialog box
        data_list - list of options for the pop down menu to help selection of a
               attribute type
        """
        EditAttributeRoot.__init__(
            self, state, uistate, track, attrib, title, data_list, callback
        )

    def _create_tabbed_pages(self):
        notebook = Gtk.Notebook()
        self.srcref_list = CitationEmbedList(
            self.dbstate,
            self.uistate,
            self.track,
            self.obj.get_citation_list(),
            "attribute_editor_citations",
        )
        self._add_tab(notebook, self.srcref_list)
        self.track_ref_for_deletion("srcref_list")

        self.note_tab = NoteTab(
            self.dbstate,
            self.uistate,
            self.track,
            self.obj.get_note_list(),
            "attribute_editor_notes",
            notetype=NoteType.ATTRIBUTE,
        )
        self._add_tab(notebook, self.note_tab)
        self.track_ref_for_deletion("note_tab")

        self._setup_notebook_tabs(notebook)
        notebook.show_all()
        self.top.get_object("vbox").pack_start(notebook, True, True, 0)


# -------------------------------------------------------------------------
#
# EditFamilyAttribute class
#
# -------------------------------------------------------------------------
class EditFamilyAttribute(EditAttribute):
    """
    Displays a dialog that allows the user to edit an attribute.
    """

    def __init__(self, state, uistate, track, attrib, title, data_list, callback):
        """
        Displays the dialog box.

        parent - The class that called the Address editor.
        attrib - The attribute that is to be edited
        title - The title of the dialog box
        list - list of options for the pop down menu
        """
        EditAttribute.__init__(
            self, state, uistate, track, attrib, title, data_list, callback
        )

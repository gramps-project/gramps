#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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
The EditLdsOrd module provides the EditLdsOrd class. This provides a
mechanism for the user to edit personal LDS information.
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
from gramps.gen.lib import LdsOrd, NoteType
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.utils.lds import TEMPLES
from ..glade import Glade
from .editsecondary import EditSecondary
from .objectentries import PlaceEntry
from .displaytabs import CitationEmbedList, NoteTab
from ..widgets import PrivacyButton, MonitoredDate, MonitoredMenu, MonitoredStrMenu
from ..selectors import SelectorFactory
from gramps.gen.const import URL_MANUAL_SECT1

# -------------------------------------------------------------------------
#
# Constants
#
# -------------------------------------------------------------------------

WIKI_HELP_PAGE = URL_MANUAL_SECT1
WIKI_HELP_SEC = _("LDS_Ordinance_Editor", "manual")

_DATA_MAP = {
    LdsOrd.BAPTISM: [
        LdsOrd.STATUS_NONE,
        LdsOrd.STATUS_CHILD,
        LdsOrd.STATUS_CLEARED,
        LdsOrd.STATUS_COMPLETED,
        LdsOrd.STATUS_INFANT,
        LdsOrd.STATUS_PRE_1970,
        LdsOrd.STATUS_QUALIFIED,
        LdsOrd.STATUS_STILLBORN,
        LdsOrd.STATUS_SUBMITTED,
        LdsOrd.STATUS_UNCLEARED,
    ],
    LdsOrd.CONFIRMATION: [
        LdsOrd.STATUS_NONE,
        LdsOrd.STATUS_CHILD,
        LdsOrd.STATUS_CLEARED,
        LdsOrd.STATUS_COMPLETED,
        LdsOrd.STATUS_INFANT,
        LdsOrd.STATUS_PRE_1970,
        LdsOrd.STATUS_QUALIFIED,
        LdsOrd.STATUS_STILLBORN,
        LdsOrd.STATUS_SUBMITTED,
        LdsOrd.STATUS_UNCLEARED,
    ],
    LdsOrd.ENDOWMENT: [
        LdsOrd.STATUS_NONE,
        LdsOrd.STATUS_CHILD,
        LdsOrd.STATUS_CLEARED,
        LdsOrd.STATUS_COMPLETED,
        LdsOrd.STATUS_INFANT,
        LdsOrd.STATUS_PRE_1970,
        LdsOrd.STATUS_QUALIFIED,
        LdsOrd.STATUS_STILLBORN,
        LdsOrd.STATUS_SUBMITTED,
        LdsOrd.STATUS_UNCLEARED,
    ],
    LdsOrd.SEAL_TO_PARENTS: [
        LdsOrd.STATUS_NONE,
        LdsOrd.STATUS_BIC,
        LdsOrd.STATUS_CLEARED,
        LdsOrd.STATUS_COMPLETED,
        LdsOrd.STATUS_DNS,
        LdsOrd.STATUS_PRE_1970,
        LdsOrd.STATUS_QUALIFIED,
        LdsOrd.STATUS_STILLBORN,
        LdsOrd.STATUS_SUBMITTED,
        LdsOrd.STATUS_UNCLEARED,
    ],
    LdsOrd.SEAL_TO_SPOUSE: [
        LdsOrd.STATUS_NONE,
        LdsOrd.STATUS_CANCELED,
        LdsOrd.STATUS_CLEARED,
        LdsOrd.STATUS_COMPLETED,
        LdsOrd.STATUS_DNS,
        LdsOrd.STATUS_PRE_1970,
        LdsOrd.STATUS_QUALIFIED,
        LdsOrd.STATUS_DNS_CAN,
        LdsOrd.STATUS_SUBMITTED,
        LdsOrd.STATUS_UNCLEARED,
    ],
}


# -------------------------------------------------------------------------
#
# EditLdsOrd class
#
# -------------------------------------------------------------------------
class EditLdsOrd(EditSecondary):
    """
    Displays a dialog that allows the user to edit an attribute.
    """

    def __init__(self, state, uistate, track, attrib, callback):
        """
        Displays the dialog box.

        parent - The class that called the Address editor.
        attrib - The attribute that is to be edited
        title - The title of the dialog box
        list - list of options for the pop down menu
        """
        EditSecondary.__init__(self, state, uistate, track, attrib, callback)

    def _local_init(self):
        self.top = Glade()
        self.set_window(
            self.top.toplevel, self.top.get_object("title"), _("LDS Ordinance Editor")
        )
        self.setup_configs("interface.lds", 600, 450)

        self.share_btn = self.top.get_object("share_place")
        self.add_del_btn = self.top.get_object("add_del_place")

    def _connect_signals(self):
        self.parents_select.connect("clicked", self.select_parents_clicked)
        self.define_cancel_button(self.top.get_object("cancel"))
        self.define_ok_button(self.top.get_object("ok"), self.save)
        self.define_help_button(
            self.top.get_object("help"), WIKI_HELP_PAGE, WIKI_HELP_SEC
        )

    def _get_types(self):
        return (
            LdsOrd.BAPTISM,
            LdsOrd.ENDOWMENT,
            LdsOrd.CONFIRMATION,
            LdsOrd.SEAL_TO_PARENTS,
        )

    def _setup_fields(self):
        self.parents_label = self.top.get_object("parents_label")
        self.parents = self.top.get_object("parents")
        self.parents_select = self.top.get_object("parents_select")

        self.priv = PrivacyButton(
            self.top.get_object("private"), self.obj, self.db.readonly
        )

        self.date_field = MonitoredDate(
            self.top.get_object("date_entry"),
            self.top.get_object("date_stat"),
            self.obj.get_date_object(),
            self.uistate,
            self.track,
            self.db.readonly,
        )

        self.place_field = PlaceEntry(
            self.dbstate,
            self.uistate,
            self.track,
            self.top.get_object("place"),
            self.top.get_object("place_event_box"),
            self.obj.set_place_handle,
            self.obj.get_place_handle,
            self.add_del_btn,
            self.share_btn,
        )

        self.type_menu = MonitoredMenu(
            self.top.get_object("type"),
            self.obj.set_type,
            self.obj.get_type,
            [
                (item[1], item[0])
                for item in LdsOrd._TYPE_MAP
                if item[0] in self._get_types()
            ],
            self.db.readonly,
            changed=self.ord_type_changed,
        )
        self.track_ref_for_deletion("type_menu")

        self.temple_menu = MonitoredStrMenu(
            self.top.get_object("temple"),
            self.obj.set_temple,
            self.obj.get_temple,
            TEMPLES.name_code_data(),
            self.db.readonly,
        )
        self.track_ref_for_deletion("temple_menu")

        self.status_menu = MonitoredMenu(
            self.top.get_object("status"),
            self.obj.set_status,
            self.obj.get_status,
            [
                (item[1], item[0])
                for item in LdsOrd._STATUS_MAP
                if item[0] in _DATA_MAP[self.obj.get_type()]
            ],
            self.db.readonly,
        )
        self.track_ref_for_deletion("status_menu")

        self.update_parent_label()

    def _post_init(self):
        self.ord_type_changed()

    def ord_type_changed(self):
        if self.obj.get_type() == LdsOrd.SEAL_TO_PARENTS:
            self.parents.show()
            self.parents_label.show()
            self.parents_select.show()
        else:
            self.parents.hide()
            self.parents_label.hide()
            self.parents_select.hide()

        new_data = [
            (item[1], item[0])
            for item in LdsOrd._STATUS_MAP
            if item[0] in _DATA_MAP[self.obj.get_type()]
        ]
        self.status_menu.change_menu(new_data)

    def _create_tabbed_pages(self):
        notebook = Gtk.Notebook()
        self.citation_list = CitationEmbedList(
            self.dbstate,
            self.uistate,
            self.track,
            self.obj.get_citation_list(),
            "ldsord_editor_citations",
        )
        self._add_tab(notebook, self.citation_list)
        self.track_ref_for_deletion("citation_list")

        self.note_tab = NoteTab(
            self.dbstate,
            self.uistate,
            self.track,
            self.obj.get_note_list(),
            "ldsord_editor_notes",
            notetype=NoteType.LDS,
        )
        self._add_tab(notebook, self.note_tab)
        self.track_ref_for_deletion("note_tab")

        self._setup_notebook_tabs(notebook)
        notebook.show_all()
        self.top.get_object("vbox").pack_start(notebook, True, True, 0)

    def select_parents_clicked(self, obj):
        SelectFamily = SelectorFactory("Family")

        dialog = SelectFamily(self.dbstate, self.uistate, self.track)
        family = dialog.run()
        if family:
            self.obj.set_family_handle(family.handle)
        self.update_parent_label()

    def update_parent_label(self):
        handle = self.obj.get_family_handle()
        if handle:
            family = self.dbstate.db.get_family_from_handle(handle)
            f = self.dbstate.db.get_person_from_handle(family.get_father_handle())
            m = self.dbstate.db.get_person_from_handle(family.get_mother_handle())
            if f and m:
                label = _("%(father)s and %(mother)s [%(gramps_id)s]") % {
                    "father": name_displayer.display(f),
                    "mother": name_displayer.display(m),
                    "gramps_id": family.gramps_id,
                }
            elif f:
                label = _("%(father)s [%(gramps_id)s]") % {
                    "father": name_displayer.display(f),
                    "gramps_id": family.gramps_id,
                }
            elif m:
                label = _("%(mother)s [%(gramps_id)s]") % {
                    "mother": name_displayer.display(m),
                    "gramps_id": family.gramps_id,
                }
            else:
                # No translation for bare gramps_id
                label = "[%(gramps_id)s]" % {
                    "gramps_id": family.gramps_id,
                }
        else:
            label = ""

        self.parents.set_text(label)

    def build_menu_names(self, attrib):
        label = _("LDS Ordinance")
        return (label, _("LDS Ordinance Editor"))

    def save(self, *obj):
        """
        Called when the OK button is pressed. Gets data from the
        form and updates the LdsOrd data structure.
        """
        if self.callback:
            self.callback(self.obj)
        self.callback = None
        self.close()


# -------------------------------------------------------------------------
#
# EditFamilyLdsOrd
#
# -------------------------------------------------------------------------
class EditFamilyLdsOrd(EditSecondary):
    """
    Displays a dialog that allows the user to edit an attribute.
    """

    def __init__(self, state, uistate, track, attrib, callback):
        """
        Displays the dialog box.

        parent - The class that called the Address editor.
        attrib - The attribute that is to be edited
        title - The title of the dialog box
        list - list of options for the pop down menu
        """
        EditSecondary.__init__(self, state, uistate, track, attrib, callback)

    def _local_init(self):
        self.top = Glade()
        self.set_window(
            self.top.toplevel, self.top.get_object("title"), _("LDS Ordinance Editor")
        )
        self.share_btn = self.top.get_object("share_place")
        self.add_del_btn = self.top.get_object("add_del_place")

    def _post_init(self):
        self.parents.hide()
        self.parents_label.hide()
        self.parents_select.hide()

    def _connect_signals(self):
        self.define_cancel_button(self.top.get_object("cancel"))
        self.define_help_button(self.top.get_object("help"))
        self.define_ok_button(self.top.get_object("ok"), self.save)

    def _get_types(self):
        return (LdsOrd.SEAL_TO_SPOUSE,)

    def _setup_fields(self):
        self.parents_label = self.top.get_object("parents_label")
        self.parents = self.top.get_object("parents")
        self.parents_select = self.top.get_object("parents_select")

        self.priv = PrivacyButton(
            self.top.get_object("private"), self.obj, self.db.readonly
        )

        self.date_field = MonitoredDate(
            self.top.get_object("date_entry"),
            self.top.get_object("date_stat"),
            self.obj.get_date_object(),
            self.uistate,
            self.track,
            self.db.readonly,
        )

        self.place_field = PlaceEntry(
            self.dbstate,
            self.uistate,
            self.track,
            self.top.get_object("place"),
            self.top.get_object("place_event_box"),
            self.obj.set_place_handle,
            self.obj.get_place_handle,
            self.add_del_btn,
            self.share_btn,
        )

        self.type_menu = MonitoredMenu(
            self.top.get_object("type"),
            self.obj.set_type,
            self.obj.get_type,
            [
                (item[1], item[0])
                for item in LdsOrd._TYPE_MAP
                if item[0] in self._get_types()
            ],
            self.db.readonly,
        )
        self.track_ref_for_deletion("type_menu")

        self.temple_menu = MonitoredStrMenu(
            self.top.get_object("temple"),
            self.obj.set_temple,
            self.obj.get_temple,
            TEMPLES.name_code_data(),
            self.db.readonly,
        )
        self.track_ref_for_deletion("temple_menu")

        self.status_menu = MonitoredMenu(
            self.top.get_object("status"),
            self.obj.set_status,
            self.obj.get_status,
            [
                (item[1], item[0])
                for item in LdsOrd._STATUS_MAP
                if item[0] in _DATA_MAP[self.obj.get_type()]
            ],
            self.db.readonly,
        )
        self.track_ref_for_deletion("status_menu")

    def _create_tabbed_pages(self):
        notebook = Gtk.Notebook()
        self.srcref_list = CitationEmbedList(
            self.dbstate,
            self.uistate,
            self.track,
            self.obj.get_citation_list(),
            "ldsord_editor_citations",
        )
        self._add_tab(notebook, self.srcref_list)
        self.track_ref_for_deletion("srcref_list")

        self.note_tab = NoteTab(
            self.dbstate,
            self.uistate,
            self.track,
            self.obj.get_note_list(),
            "ldsord_editor_notes",
            notetype=NoteType.LDS,
        )
        self._add_tab(notebook, self.note_tab)
        self.track_ref_for_deletion("note_tab")

        notebook.show_all()
        self.top.get_object("vbox").pack_start(notebook, True, True, 0)

    def build_menu_names(self, attrib):
        label = _("LDS Ordinance")
        return (label, _("LDS Ordinance Editor"))

    def save(self, *obj):
        """
        Called when the OK button is pressed. Gets data from the
        form and updates the LdsOrd data structure.
        """
        if self.callback:
            self.callback(self.obj)
        self.close()

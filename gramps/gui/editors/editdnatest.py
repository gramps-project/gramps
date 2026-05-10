#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Ian Davis
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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

"""
EditDNATest editor dialog.
"""

from gi.repository import Gtk

from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext

from gramps.gen.const import URL_MANUAL_PAGE
from gramps.gen.lib import DNATest, NoteType
from gramps.gen.db import DbTxn
from ..display import display_help
from .editprimary import EditPrimary
from .objectentries import PersonEntry
from ..glade import Glade
from ..dialog import ErrorDialog
from .displaytabs import (
    DNATestAttrEmbedList,
    CitationEmbedList,
    NoteTab,
    GalleryTab,
)
from .displaytabs.dnatestbackreflist import DNATestBackRefList
from ..widgets import (
    MonitoredEntry,
    PrivacyButton,
    MonitoredDataType,
    MonitoredDate,
    MonitoredTagList,
)

WIKI_HELP_PAGE = URL_MANUAL_PAGE
WIKI_HELP_SEC = _("DNA_Test_Editor", "manual")


# -------------------------------------------------------------------------
#
# EditDNATest
#
# -------------------------------------------------------------------------
class EditDNATest(EditPrimary):
    def __init__(self, dbstate, uistate, track, dnatest, callback=None):
        EditPrimary.__init__(
            self,
            dbstate,
            uistate,
            track,
            dnatest,
            dbstate.db.get_dnatest_from_handle,
            dbstate.db.get_dnatest_from_gramps_id,
            callback,
        )

    def empty_object(self):
        return DNATest()

    def get_menu_title(self):
        handle = self.obj.get_handle()
        if handle:
            account = self.obj.get_account_name()
            provider = str(self.obj.get_provider())
            title = account if account else str(self.obj.gramps_id)
            if provider:
                title = "%s (%s)" % (title, provider)
            return _("DNA Test: %s") % title
        return _("New DNA Test")

    def _local_init(self):
        self.top = Glade()
        self.set_window(self.top.toplevel, None, self.get_menu_title())
        self.setup_configs("interface.dnatest", 640, 480)

        self.share_btn = self.top.get_object("select_person")
        self.add_del_btn = self.top.get_object("add_del_person")

    def _connect_signals(self):
        self.top.get_object("cancel").connect("clicked", self.close)
        self.top.get_object("help").connect("clicked", self.help_clicked)
        self.ok_button = self.top.get_object("ok")
        self.ok_button.set_sensitive(not self.db.readonly)
        self.ok_button.connect("clicked", self.save)

    def _connect_db_signals(self):
        self._add_db_signal("dnatest-rebuild", self._do_close)
        self._add_db_signal("dnatest-delete", self.check_for_close)
        self._add_db_signal("person-delete", self._person_delete)
        self._add_db_signal("person-update", self._person_update)

    def _setup_fields(self):
        self.person_field = PersonEntry(
            self.dbstate,
            self.uistate,
            self.track,
            self.top.get_object("person_label"),
            self.top.get_object("person_event_box"),
            self.obj.set_person_handle,
            self.obj.get_person_handle,
            self.add_del_btn,
            self.share_btn,
        )

        self.account_name_field = MonitoredEntry(
            self.top.get_object("account_name"),
            self.obj.set_account_name,
            self.obj.get_account_name,
            self.db.readonly,
        )

        self.provider_field = MonitoredDataType(
            self.top.get_object("provider"),
            self.obj.set_provider,
            self.obj.get_provider,
            self.db.readonly,
        )

        self.kit_id_field = MonitoredEntry(
            self.top.get_object("kit_id"),
            self.obj.set_kit_id,
            self.obj.get_kit_id,
            self.db.readonly,
        )

        self.test_type_field = MonitoredDataType(
            self.top.get_object("test_type"),
            self.obj.set_test_type,
            self.obj.get_test_type,
            self.db.readonly,
        )

        self.genome_build_field = MonitoredDataType(
            self.top.get_object("genome_build"),
            self.obj.set_genome_build,
            self.obj.get_genome_build,
            self.db.readonly,
        )

        self.date_field = MonitoredDate(
            self.top.get_object("date_entry"),
            self.top.get_object("date_stat"),
            self.obj.get_date_object(),
            self.uistate,
            self.track,
            self.db.readonly,
        )

        self.haplogroup_field = MonitoredEntry(
            self.top.get_object("haplogroup"),
            self.obj.set_haplogroup,
            self.obj.get_haplogroup,
            self.db.readonly,
        )

        self.gid = MonitoredEntry(
            self.top.get_object("gid"),
            self.obj.set_gramps_id,
            self.obj.get_gramps_id,
            self.db.readonly,
        )

        self.tags = MonitoredTagList(
            self.top.get_object("tag_label"),
            self.top.get_object("tag_button"),
            self.obj.set_tag_list,
            self.obj.get_tag_list,
            self.db,
            self.uistate,
            self.track,
            self.db.readonly,
        )

        self.priv = PrivacyButton(
            self.top.get_object("private"), self.obj, self.db.readonly
        )

    def _create_tabbed_pages(self):
        notebook = Gtk.Notebook()

        self.attr_list = DNATestAttrEmbedList(
            self.dbstate,
            self.uistate,
            self.track,
            self.obj.get_attribute_list(),
            "dnatest_editor_attributes",
        )
        self._add_tab(notebook, self.attr_list)

        self.note_list = NoteTab(
            self.dbstate,
            self.uistate,
            self.track,
            self.obj.get_note_list(),
            "dnatest_editor_notes",
            notetype=NoteType.GENERAL,
        )
        self._add_tab(notebook, self.note_list)

        self.gallery_list = GalleryTab(
            self.dbstate,
            self.uistate,
            self.track,
            self.obj.get_media_list(),
        )
        self._add_tab(notebook, self.gallery_list)

        self.citation_list = CitationEmbedList(
            self.dbstate,
            self.uistate,
            self.track,
            self.obj.get_citation_list(),
            "dnatest_editor_citations",
            self.get_menu_title(),
        )
        self._add_tab(notebook, self.citation_list)

        handle_list = self.dbstate.db.find_backlink_handles(self.obj.handle)
        self.backref_list = DNATestBackRefList(
            self.dbstate,
            self.uistate,
            self.track,
            handle_list,
            "dnatest_editor_references",
        )
        self._add_tab(notebook, self.backref_list)

        self._setup_notebook_tabs(notebook)
        notebook.show_all()
        self.top.get_object("vbox").pack_start(notebook, True, True, 0)

        self.track_ref_for_deletion("attr_list")
        self.track_ref_for_deletion("note_list")
        self.track_ref_for_deletion("gallery_list")
        self.track_ref_for_deletion("citation_list")
        self.track_ref_for_deletion("backref_list")

    def build_menu_names(self, dnatest):
        return (_("Edit DNA Test"), self.get_menu_title())

    def help_clicked(self, obj):
        display_help(webpage=WIKI_HELP_PAGE, section=WIKI_HELP_SEC)

    def save(self, *obj):
        self.ok_button.set_sensitive(False)

        if self.object_is_empty():
            ErrorDialog(
                _("Cannot save DNA test"),
                _(
                    "No data exists for this DNA test. Please "
                    "enter data or cancel the edit."
                ),
                parent=self.window,
            )
            self.ok_button.set_sensitive(True)
            return

        uses_dupe_id, id = self._uses_duplicate_id()
        if uses_dupe_id:
            prim_object = self.get_from_gramps_id(id)
            name = prim_object.get_account_name()
            msg1 = _("Cannot save DNA test. ID already exists.")
            msg2 = _(
                "You have attempted to use the existing Gramps ID with "
                "value %(id)s. This value is already used by "
                "'%(prim_object)s'. Please enter a different ID or leave "
                "blank to get the next available ID value."
            ) % {"id": id, "prim_object": name}
            ErrorDialog(msg1, msg2, parent=self.window)
            self.ok_button.set_sensitive(True)
            return

        if not self.obj.handle:
            with DbTxn(
                _("Add DNA Test (%s)") % self.obj.get_gramps_id(), self.db
            ) as trans:
                self.db.add_dnatest(self.obj, trans)
        else:
            if self.data_has_changed():
                with DbTxn(
                    _("Edit DNA Test (%s)") % self.obj.get_gramps_id(), self.db
                ) as trans:
                    if not self.obj.get_gramps_id():
                        self.obj.set_gramps_id(self.db.find_next_dnatest_gramps_id())
                    self.db.commit_dnatest(self.obj, trans)

        self._do_close()
        if self.callback:
            self.callback(self.obj)

    def _person_delete(self, handle_list):
        if self.obj.get_person_handle() in handle_list:
            self.close()

    def _person_update(self, handle_list):
        if self.obj.get_person_handle() in handle_list:
            person = self.db.get_person_from_handle(self.obj.get_person_handle())
            if person:
                self.person_field.after_edit(person)

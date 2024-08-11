#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
#               2009       Gary Burton
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

# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------
from copy import deepcopy

# -------------------------------------------------------------------------
#
# gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext
from gramps.gen.lib import NoteType
from gramps.gen.db import DbTxn

from .displaytabs import NoteTab, AddrEmbedList, WebEmbedList, SourceBackRefList
from ..widgets import MonitoredEntry, PrivacyButton, MonitoredDataType
from .editreference import RefTab, EditReference
from ..glade import Glade


# -------------------------------------------------------------------------
#
# EditRepoRef class
#
# -------------------------------------------------------------------------
class EditRepoRef(EditReference):
    def __init__(self, state, uistate, track, source, source_ref, update):
        EditReference.__init__(self, state, uistate, track, source, source_ref, update)
        self.original = deepcopy(source.serialize())

    def _local_init(self):
        self.top = Glade()
        self.set_window(
            self.top.toplevel,
            self.top.get_object("repo_title"),
            _("Repository Reference Editor"),
        )
        self.setup_configs("interface.repo-ref", 600, 450)

        self.define_warn_box(self.top.get_object("warn_box"))
        self.define_expander(self.top.get_object("src_expander"))

        tblref = self.top.get_object("table70")
        notebook = self.top.get_object("notebook_ref")
        # recreate start page as GrampsTab
        notebook.remove_page(0)
        self.reftab = RefTab(
            self.dbstate, self.uistate, self.track, _("General"), tblref
        )
        tblref = self.top.get_object("table69")
        notebook = self.top.get_object("notebook_src")
        # recreate start page as GrampsTab
        notebook.remove_page(0)
        self.primtab = RefTab(
            self.dbstate, self.uistate, self.track, _("_General"), tblref
        )
        self.track_ref_for_deletion("primtab")

    def _connect_signals(self):
        self.define_ok_button(self.top.get_object("ok"), self.ok_clicked)
        self.define_cancel_button(self.top.get_object("cancel"))

    def _connect_db_signals(self):
        """
        Connect any signals that need to be connected.
        Called by the init routine of the base class (_EditPrimary).
        """
        self._add_db_signal("repository-rebuild", self.close)
        self._add_db_signal("repository-delete", self.check_for_close)

    def _setup_fields(self):
        self.callno = MonitoredEntry(
            self.top.get_object("call_number"),
            self.source_ref.set_call_number,
            self.source_ref.get_call_number,
            self.db.readonly,
        )

        self.gid = MonitoredEntry(
            self.top.get_object("gid"),
            self.source.set_gramps_id,
            self.source.get_gramps_id,
            self.db.readonly,
        )

        self.privacy = PrivacyButton(
            self.top.get_object("private"), self.source, self.db.readonly
        )

        self.ref_privacy = PrivacyButton(
            self.top.get_object("private_ref"), self.source_ref, self.db.readonly
        )

        self.title = MonitoredEntry(
            self.top.get_object("repo_name"),
            self.source.set_name,
            self.source.get_name,
            self.db.readonly,
        )

        self.type_selector = MonitoredDataType(
            self.top.get_object("media_type"),
            self.source_ref.set_media_type,
            self.source_ref.get_media_type,
            self.db.readonly,
            self.db.get_source_media_types(),
        )

        self.media_type_selector = MonitoredDataType(
            self.top.get_object("repo_type"),
            self.source.set_type,
            self.source.get_type,
            self.db.readonly,
            self.db.get_repository_types(),
        )

    def _create_tabbed_pages(self):
        """
        Create the notebook tabs and inserts them into the main
        window.
        """

        notebook_src = self.top.get_object("notebook_src")
        notebook_ref = self.top.get_object("notebook_ref")

        self._add_tab(notebook_src, self.primtab)
        self._add_tab(notebook_ref, self.reftab)

        self.note_tab = NoteTab(
            self.dbstate,
            self.uistate,
            self.track,
            self.source.get_note_list(),
            "reporef_editor_shared_notes",
            notetype=NoteType.REPO,
        )
        self._add_tab(notebook_src, self.note_tab)
        self.track_ref_for_deletion("note_tab")

        self.comment_tab = NoteTab(
            self.dbstate,
            self.uistate,
            self.track,
            self.source_ref.get_note_list(),
            "reporef_editor_ref_notes",
            notetype=NoteType.REPOREF,
        )
        self._add_tab(notebook_ref, self.comment_tab)
        self.track_ref_for_deletion("comment_tab")

        self.address_tab = AddrEmbedList(
            self.dbstate,
            self.uistate,
            self.track,
            self.source.get_address_list(),
            "reporef_editor_shared_address",
        )
        self._add_tab(notebook_src, self.address_tab)
        self.track_ref_for_deletion("address_tab")

        self.web_list = WebEmbedList(
            self.dbstate,
            self.uistate,
            self.track,
            self.source.get_url_list(),
            "reporef_editor_shared_internet",
        )
        self._add_tab(notebook_src, self.web_list)
        self.track_ref_for_deletion("web_list")

        self.backref_tab = SourceBackRefList(
            self.dbstate,
            self.uistate,
            self.track,
            self.db.find_backlink_handles(self.source.handle),
            "reporef_editor_shared_references",
            self.enable_warnbox,
        )
        self._add_tab(notebook_src, self.backref_tab)
        self.track_ref_for_deletion("backref_tab")

        self._setup_notebook_tabs(notebook_src)
        self._setup_notebook_tabs(notebook_ref)

    def build_menu_names(self, sourceref):
        if self.source:
            source_name = self.source.get_name()
            submenu_label = _("Repository: %s") % source_name
        else:
            submenu_label = _("New Repository")
        return (_("Repo Reference Editor"), submenu_label)

    def ok_clicked(self, obj):
        if self.source.handle:
            # only commit if it has changed
            if self.source.serialize() != self.original:
                with DbTxn(_("Modify Repository"), self.db) as trans:
                    self.db.commit_repository(self.source, trans)
        else:
            if self.check_for_duplicate_id("Repository"):
                return
            with DbTxn(_("Add Repository"), self.db) as trans:
                self.db.add_repository(self.source, trans)
            self.source_ref.ref = self.source.handle

        if self.update:
            self.update((self.source_ref, self.source))

        self.close()

#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2009       Gary Burton
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

# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------
import logging

log = logging.getLogger(".")
LOG = logging.getLogger(".citation")

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
from gramps.gen.lib import NoteType, Source
from gramps.gen.db import DbTxn
from .editprimary import EditPrimary

from .displaytabs import (
    NoteTab,
    GalleryTab,
    SrcAttrEmbedList,
    CitationBackRefList,
    RepoEmbedList,
)
from ..widgets import MonitoredEntry, PrivacyButton, MonitoredTagList
from ..dialog import ErrorDialog
from ..glade import Glade
from gramps.gen.const import URL_MANUAL_SECT2

# -------------------------------------------------------------------------
#
# Constants
#
# -------------------------------------------------------------------------

WIKI_HELP_PAGE = URL_MANUAL_SECT2
WIKI_HELP_SEC = _("New_Source_dialog", "manual")

# -------------------------------------------------------------------------
#
# EditSource class
#
# -------------------------------------------------------------------------


class EditSource(EditPrimary):
    def __init__(self, dbstate, uistate, track, source, callback=None):
        EditPrimary.__init__(
            self,
            dbstate,
            uistate,
            track,
            source,
            dbstate.db.get_source_from_handle,
            dbstate.db.get_source_from_gramps_id,
            callback,
        )

    def empty_object(self):
        return Source()

    def get_menu_title(self):
        title = self.obj.get_title()
        if title:
            title = _("Source") + ": " + title
        else:
            title = _("New Source")
        return title

    def _local_init(self):
        assert self.obj

        self.glade = Glade()
        self.set_window(self.glade.toplevel, None, self.get_menu_title())
        self.setup_configs("interface.source", 600, 450)

    def _connect_signals(self):
        self.define_ok_button(self.glade.get_object("ok"), self.save)
        self.define_cancel_button(self.glade.get_object("cancel"))
        self.define_help_button(
            self.glade.get_object("help"), WIKI_HELP_PAGE, WIKI_HELP_SEC
        )

    def _connect_db_signals(self):
        """
        Connect any signals that need to be connected.
        Called by the init routine of the base class (_EditPrimary).
        """
        self._add_db_signal("source-rebuild", self._do_close)
        self._add_db_signal("source-delete", self.check_for_close)

    def _setup_fields(self):
        self.author = MonitoredEntry(
            self.glade.get_object("author"),
            self.obj.set_author,
            self.obj.get_author,
            self.db.readonly,
        )

        self.pubinfo = MonitoredEntry(
            self.glade.get_object("pubinfo"),
            self.obj.set_publication_info,
            self.obj.get_publication_info,
            self.db.readonly,
        )

        self.gid = MonitoredEntry(
            self.glade.get_object("gid"),
            self.obj.set_gramps_id,
            self.obj.get_gramps_id,
            self.db.readonly,
        )

        self.tags = MonitoredTagList(
            self.glade.get_object("tag_label"),
            self.glade.get_object("tag_button"),
            self.obj.set_tag_list,
            self.obj.get_tag_list,
            self.db,
            self.uistate,
            self.track,
            self.db.readonly,
        )

        self.priv = PrivacyButton(
            self.glade.get_object("private"), self.obj, self.db.readonly
        )

        self.abbrev = MonitoredEntry(
            self.glade.get_object("abbrev"),
            self.obj.set_abbreviation,
            self.obj.get_abbreviation,
            self.db.readonly,
        )

        self.title = MonitoredEntry(
            self.glade.get_object("source_title"),
            self.obj.set_title,
            self.obj.get_title,
            self.db.readonly,
        )

    def _create_tabbed_pages(self):
        notebook = Gtk.Notebook()

        self.note_tab = NoteTab(
            self.dbstate,
            self.uistate,
            self.track,
            self.obj.get_note_list(),
            "source_editor_notes",
            self.get_menu_title(),
            NoteType.SOURCE,
        )
        self._add_tab(notebook, self.note_tab)
        self.track_ref_for_deletion("note_tab")

        self.gallery_tab = GalleryTab(
            self.dbstate,
            self.uistate,
            self.track,
            self.obj.get_media_list(),
        )
        self._add_tab(notebook, self.gallery_tab)
        self.track_ref_for_deletion("gallery_tab")

        self.attr_tab = SrcAttrEmbedList(
            self.dbstate,
            self.uistate,
            self.track,
            self.obj.get_attribute_list(),
            "source_editor_attributes",
        )
        self._add_tab(notebook, self.attr_tab)
        self.track_ref_for_deletion("attr_tab")

        self.repo_tab = RepoEmbedList(
            self.dbstate,
            self.uistate,
            self.track,
            self.obj.get_reporef_list(),
            "source_editor_repositories",
        )
        self._add_tab(notebook, self.repo_tab)
        self.track_ref_for_deletion("repo_tab")

        self.backref_list = CitationBackRefList(
            self.dbstate,
            self.uistate,
            self.track,
            self.db.find_backlink_handles(self.obj.handle),
            "source_editor_references",
        )
        self.backref_tab = self._add_tab(notebook, self.backref_list)
        self.track_ref_for_deletion("backref_tab")
        self.track_ref_for_deletion("backref_list")

        self._setup_notebook_tabs(notebook)
        notebook.show_all()
        self.glade.get_object("vbox").pack_start(notebook, True, True, 0)

    def build_menu_names(self, source):
        return (_("Edit Source"), self.get_menu_title())

    def save(self, *obj):
        self.ok_button.set_sensitive(False)
        if self.object_is_empty():
            ErrorDialog(
                _("Cannot save source"),
                _(
                    "No data exists for this source. Please "
                    "enter data or cancel the edit."
                ),
                parent=self.window,
            )
            self.ok_button.set_sensitive(True)
            return

        (uses_dupe_id, id) = self._uses_duplicate_id()
        if uses_dupe_id:
            prim_object = self.get_from_gramps_id(id)
            name = prim_object.get_title()
            msg1 = _("Cannot save source. ID already exists.")
            msg2 = _(
                "You have attempted to use the existing Gramps ID with "
                "value %(id)s. This value is already used by '"
                "%(prim_object)s'. Please enter a different ID or leave "
                "blank to get the next available ID value."
            ) % {"id": id, "prim_object": name}
            ErrorDialog(msg1, msg2, parent=self.window)
            self.ok_button.set_sensitive(True)
            return

        if not self.obj.handle:
            with DbTxn(_("Add Source (%s)") % self.obj.get_title(), self.db) as trans:
                self.db.add_source(self.obj, trans)
        else:
            if self.data_has_changed():
                with DbTxn(
                    _("Edit Source (%s)") % self.obj.get_title(), self.db
                ) as trans:
                    if not self.obj.get_gramps_id():
                        self.obj.set_gramps_id(self.db.find_next_source_gramps_id())
                    self.db.commit_source(self.obj, trans)

        self._do_close()
        if self.callback:
            self.callback(self.obj)

#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2009       Gary Burton
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

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext
from gramps.gen.lib import NoteType, Repository
from gramps.gen.db import DbTxn

from ..widgets import (MonitoredEntry, MonitoredDataType, PrivacyButton,
                       MonitoredTagList)
from .displaytabs import AddrEmbedList, WebEmbedList, NoteTab, SourceBackRefList
from .editprimary import EditPrimary
from ..dialog import ErrorDialog
from ..glade import Glade
from gramps.gen.const import URL_MANUAL_SECT2

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------

WIKI_HELP_PAGE = URL_MANUAL_SECT2
WIKI_HELP_SEC = _('New_Repository_dialog', 'manual')

class EditRepository(EditPrimary):

    def __init__(self, dbstate, uistate, track, repository, callback=None):

        EditPrimary.__init__(self, dbstate, uistate, track, repository,
                             dbstate.db.get_repository_from_handle,
                             dbstate.db.get_repository_from_gramps_id, callback)

    def empty_object(self):
        return Repository()

    def get_menu_title(self):
        if self.obj.get_handle():
            title = self.obj.get_name()
            if title:
                title = _('Repository') + ": " + title
            else:
                title = _('Repository')
        else:
            title = _('New Repository')
        return title

    def _local_init(self):
        self.glade = Glade()

        self.set_window(self.glade.toplevel, None,
                        self.get_menu_title())
        self.setup_configs('interface.repo', 650, 450)

    def build_menu_names(self, source):
        return (_('Edit Repository'), self.get_menu_title())

    def _setup_fields(self):

        self.name = MonitoredEntry(self.glade.get_object("repository_name"),
                                   self.obj.set_name, self.obj.get_name,
                                   self.db.readonly)

        self.type = MonitoredDataType(self.glade.get_object("repository_type"),
                                      self.obj.set_type, self.obj.get_type,
                                      self.db.readonly,
                                      self.db.get_repository_types())

        self.call_number = MonitoredEntry(self.glade.get_object('gid'),
                                          self.obj.set_gramps_id,
                                          self.obj.get_gramps_id,
                                          self.db.readonly)

        self.tags = MonitoredTagList(self.glade.get_object("tag_label"),
                                     self.glade.get_object("tag_button"),
                                     self.obj.set_tag_list,
                                     self.obj.get_tag_list,
                                     self.db,
                                     self.uistate, self.track,
                                     self.db.readonly)

        self.privacy = PrivacyButton(self.glade.get_object("private"),
                                     self.obj, self.db.readonly)

    def _create_tabbed_pages(self):

        notebook = Gtk.Notebook()

        self.addr_tab = AddrEmbedList(self.dbstate,
                                      self.uistate,
                                      self.track,
                                      self.obj.get_address_list())
        self._add_tab(notebook, self.addr_tab)
        self.track_ref_for_deletion("addr_tab")

        self.url_tab = WebEmbedList(self.dbstate,
                                    self.uistate,
                                    self.track,
                                    self.obj.get_url_list())
        self._add_tab(notebook, self.url_tab)
        self.track_ref_for_deletion("url_tab")

        self.note_tab = NoteTab(self.dbstate,
                                self.uistate,
                                self.track,
                                self.obj.get_note_list(),
                                self.get_menu_title(),
                                notetype=NoteType.REPO)
        self._add_tab(notebook, self.note_tab)
        self.track_ref_for_deletion("note_tab")

        self.backref_tab = SourceBackRefList(self.dbstate,
                                             self.uistate,
                                             self.track,
                               self.db.find_backlink_handles(self.obj.handle))
        self.backref_list = self._add_tab(notebook, self.backref_tab)
        self.track_ref_for_deletion("backref_tab")
        self.track_ref_for_deletion("backref_list")

        self._setup_notebook_tabs(notebook)
        notebook.show_all()
        self.glade.get_object("vbox").pack_start(notebook, True, True, 0)

    def _connect_signals(self):
        self.define_ok_button(self.glade.get_object('ok'), self.save)
        self.define_cancel_button(self.glade.get_object('cancel'))
        self.define_help_button(self.glade.get_object('help'),
                WIKI_HELP_PAGE, WIKI_HELP_SEC)

    def _connect_db_signals(self):
        """
        Connect any signals that need to be connected.
        Called by the init routine of the base class (_EditPrimary).
        """
        self._add_db_signal('repository-rebuild', self._do_close)
        self._add_db_signal('repository-delete', self.check_for_close)

    def save(self, *obj):
        self.ok_button.set_sensitive(False)
        if self.object_is_empty():
            ErrorDialog(_("Cannot save repository"),
                        _("No data exists for this repository. Please "
                          "enter data or cancel the edit."),
                        parent=self.window)
            self.ok_button.set_sensitive(True)
            return

        (uses_dupe_id, id) = self._uses_duplicate_id()
        if uses_dupe_id:
            prim_object = self.get_from_gramps_id(id)
            name = prim_object.get_name()
            msg1 = _("Cannot save repository. ID already exists.")
            msg2 = _("You have attempted to use the existing Gramps ID with "
                         "value %(id)s. This value is already used by '"
                         "%(prim_object)s'. Please enter a different ID or leave "
                         "blank to get the next available ID value.") % {
                         'id' : id, 'prim_object' : name }
            ErrorDialog(msg1, msg2, parent=self.window)
            self.ok_button.set_sensitive(True)
            return

        if not self.obj.handle:
            with DbTxn(_("Add Repository (%s)") % self.obj.get_name(),
                       self.db) as trans:
                self.db.add_repository(self.obj, trans)
        else:
            if self.data_has_changed():
                with DbTxn(_("Edit Repository (%s)") % self.obj.get_name(),
                           self.db) as trans:
                    if not self.obj.get_gramps_id():
                        self.obj.set_gramps_id(self.db.find_next_repository_gramps_id())
                    self.db.commit_repository(self.obj, trans)

        self._do_close()
        if self.callback:
            self.callback(self.obj)

class DeleteRepositoryQuery:
    def __init__(self, dbstate, uistate, repository, sources):
        self.obj = repository
        self.db = dbstate.db
        self.uistate = uistate
        self.sources = sources

    def query_response(self):
        with DbTxn(_("Delete Repository (%s)") % self.obj.get_name(),
                   self.db) as trans:

            repos_handle_list = [self.obj.get_handle()]

            for handle in self.sources:
                source = self.db.get_source_from_handle(handle)
                source.remove_repo_references(repos_handle_list)
                self.db.commit_source(source, trans)

            self.db.remove_repository(self.obj.get_handle(), trans)

#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2005  Donald N. Allingham
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

# $Id$

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk
import gtk.glade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import Utils
import RelLib

from GrampsWidgets import *
from DisplayTabs import *
from _EditPrimary import EditPrimary

class EditRepository(EditPrimary):

    def __init__(self,dbstate,uistate,track,repository):

        EditPrimary.__init__(self, dbstate, uistate, track,
                             repository, dbstate.db.get_repository_from_handle)

    def empty_object(self):
        return RelLib.Repository()

    def _local_init(self):
        self.glade = gtk.glade.XML(const.gladeFile,"repository_editor","gramps")
        self.define_top_level(self.glade.get_widget("repository_editor"),
                              self.glade.get_widget('repository_title'),
                              _('Repository Editor'))

    def _setup_fields(self):
        
        self.name = MonitoredEntry(
            self.glade.get_widget("repository_name"),
            self.obj.set_name,
            self.obj.get_name,
            self.db.readonly)

        self.type = MonitoredDataType(
            self.glade.get_widget("repository_type"),
            self.obj.set_type,
            self.obj.get_type
            )

        self.call_number = MonitoredEntry(
            self.glade.get_widget('gid'),
            self.obj.set_gramps_id,
            self.obj.get_gramps_id,
            self.db.readonly)

    def _create_tabbed_pages(self):
        
        notebook = gtk.Notebook()

        self.addr_tab = self._add_tab(
            notebook,
            AddrEmbedList(self.dbstate, self.uistate, self.track,
                          self.obj.get_address_list()))

        self.url_tab = self._add_tab(
            notebook,
            WebEmbedList(self.dbstate, self.uistate, self.track,
                         self.obj.get_url_list()))
        
        self.note_tab = self._add_tab(
            notebook,
            NoteTab(self.dbstate, self.uistate, self.track,
                    self.obj.get_note_object()))

        self.backref_tab = self._add_tab(
            notebook,
            SourceBackRefList(self.dbstate, self.uistate, self.track,
                              self.db.find_backlink_handles(self.obj.handle)))

        notebook.show_all()
        self.glade.get_widget("vbox").pack_start(notebook,True,True)

    def _connect_signals(self):
        self.define_help_button(self.glade.get_widget('help'),'adv-src')
        self.define_cancel_button(self.glade.get_widget('cancel'))
        self.define_ok_button(self.glade.get_widget('ok'), self.save)

    def save(self,*obj):
        if self.object_is_empty():
            from QuestionDialog import ErrorDialog
            ErrorDialog(_("Cannot save repository"),
                        _("No data exists for this repository. Please "
                          "enter data or cancel the edit."))
            return

        trans = self.db.transaction_begin()
        if self.obj.get_handle() == None:
            handle = self.db.add_repository(self.obj,trans)
        else:
            self.db.commit_repository(self.obj,trans)
            handle = self.obj.get_handle()
        msg = _("Edit Repository (%s)") % self.obj.get_name()
        self.db.transaction_commit(trans,msg)
        self.close(obj)

class DelRepositoryQuery:
    def __init__(self,repository,db,sources):
        self.obj = repository
        self.db = db
        self.sources = sources

    def query_response(self):
        trans = self.db.transaction_begin()
        

        repos_handle_list = [self.obj.get_handle()]

        for handle in self.sources:
            source = self.db.get_source_from_handle(handle)
            source.remove_repo_references(repos_handle_list)
            self.db.commit_source(source,trans)

        self.db.remove_repository(self.obj.get_handle(),trans)
        self.db.transaction_commit(
            trans,_("Delete Repository (%s)") % self.obj.get_name())

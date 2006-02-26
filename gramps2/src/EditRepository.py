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
import gobject
import gtk.glade
import gtk.gdk

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import Utils
import RelLib
import NameDisplay
import GrampsDisplay

from GrampsWidgets import *
from DisplayTabs import *
import DisplayState

class EditRepository(DisplayState.ManagedWindow):

    def __init__(self,dbstate,uistate,track,repository):

        if repository:
            self.repository = repository
        else:
            self.repository = RelLib.Repository()

        DisplayState.ManagedWindow.__init__(self, uistate, track, repository)

        self.dbstate = dbstate
        self.db = dbstate.db
        self.name_display = NameDisplay.displayer.display

        self.path = self.db.get_save_path()

        self.glade = gtk.glade.XML(const.gladeFile,"repositoryEditor","gramps")
        self.window = self.glade.get_widget("repositoryEditor")

        Utils.set_titles(self.window,self.glade.get_widget('repository_title'),
                         _('Repository Editor'))
        
        self.name = MonitoredEntry(
            self.glade.get_widget("repository_name"),
            self.repository.set_name,
            self.repository.get_name,
            self.db.readonly)

        self.type = MonitoredType(
            self.glade.get_widget("repository_type"),
            self.repository.set_type,
            self.repository.get_type,
            dict(Utils.repository_types),
            RelLib.Repository.CUSTOM)

        self.call_number = MonitoredEntry(
            self.glade.get_widget('gid'),
            self.repository.set_gramps_id,
            self.repository.get_gramps_id,
            self.db.readonly)

        self.notebook = gtk.Notebook()
        self.notebook.show()
        self.glade.get_widget("vbox").pack_start(self.notebook,True,True)

        self.addr_tab = self._add_page(AddrEmbedList(
            self.dbstate, self.uistate, self.track,
            repository.get_address_list()))

        self.url_tab = self._add_page(WebEmbedList(
            self.dbstate, self.uistate, self.track,
            repository.get_url_list()))
        
        self.note_tab = self._add_page(NoteTab(
            self.dbstate, self.uistate, self.track,
            repository.get_note_object()))

        self.backref_tab = self._add_page(SourceBackRefList(
            self.dbstate, self.uistate, self.track,
            self.db.find_backlink_handles(self.repository.handle)))

        self.glade.signal_autoconnect({
            "on_repositoryEditor_help_clicked" : self.on_help_clicked,
            "on_repositoryEditor_ok_clicked" : self.on_repository_apply_clicked,
            "on_repositoryEditor_cancel_clicked" : self.close_window,
            "on_repositoryEditor_delete_event" : self.on_delete_event,
            })

        self.glade.get_widget('ok').set_sensitive(not self.db.readonly)
        self.window.show()

    def _add_page(self,page):
        self.notebook.insert_page(page)
        self.notebook.set_tab_label(page,page.get_tab_widget())
        return page

    def on_delete_event(self,obj,b):
        self.close()

    def on_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        GrampsDisplay.help('adv-src')

    def close_window(self,obj):
        self.close()
        self.window.destroy()
        
    def on_repository_apply_clicked(self,obj):

        trans = self.db.transaction_begin()
        handle = None
        if self.repository.get_handle() == None:
            handle = self.db.add_repository(self.repository,trans)
        else:
            self.db.commit_repository(self.repository,trans)
            handle = self.repository.get_handle()
        self.db.transaction_commit(trans,_("Edit Repository (%s)") % self.repository.get_name())

        self.close(obj)

class DelRepositoryQuery:
    def __init__(self,repository,db,sources):
        self.repository = repository
        self.db = db
        self.sources = sources

    def query_response(self):
        trans = self.db.transaction_begin()
        

        repos_handle_list = [self.repository.get_handle()]

        for handle in self.sources:
            source = self.db.get_source_from_handle(handle)
            source.remove_repo_references(repos_handle_list)
            self.db.commit_source(source,trans)

        self.db.remove_repository(self.repository.get_handle(),trans)
        self.db.transaction_commit(
            trans,_("Delete Repository (%s)") % self.repository.get_name())

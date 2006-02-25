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
import AutoComp
import RepositoryRefEdit
import GrampsDisplay

from GrampsWidgets import *
from DisplayTabs import *
import DisplayState

#-------------------------------------------------------------------------
#
# Classes to manager the list of Sources that have references to the
# Repository
#
#-------------------------------------------------------------------------

class ReposSrcListModel(gtk.ListStore):
    def __init__(self, db, repos=None):
        gtk.ListStore.__init__(self,
                               object,   # source
                               object    # repostory reference
                               )
        
        self.original_item_list = []
        self.set_model(db)
        self.set_repos(repos)

    def rebuild(self):
        """Clear the list and repopulate from the current source record,
           remember the original list in case it is useful later"""
        self.clear()

        # Get the list of sources that reference this repository
        repos_handle = self._repos.get_handle()

        # find_backlink_handles returns a list of (class_name,handle) tuples
        # so src[1] is just the handle of the source.
        source_list = [ src[1] for src in self._db.find_backlink_handles(repos_handle,['Source']) ]
        
        # Add each (source,repos_ref) to list. It is possible for
        # a source to reference to same repository more than once.
        self.original_item_list = []
        for source_hdl in source_list:
            source = self._db.get_source_from_handle(source_hdl)
            repos_ref_list = [ repos_ref for repos_ref in source.get_reporef_list() \
                               if repos_ref.get_reference_handle() == repos_handle ]

            for repos_ref in repos_ref_list:
                self.append([self._db.get_source_from_handle(source_hdl),repos_ref])
                self.original_item_list.append((source_hdl,repos_ref))

            

    def update(self,source,repos_ref,original_source=None):
        """Add the record if it is not already in the list otherwise
        replace the record with the new one."""

        if original_source != None and \
               source.get_handle() != original_source.get_handle():
            # If the source has changed we need to remove the
            # original reference
            found = False
            for val in range(0,len(self)):
                iter = self.get_iter(val)
                if original_source.get_handle() == self.get_value(iter,0).get_handle() \
                       and repos_ref == self.get_value(iter,1):
                    self.remove(iter)
                    found = True
                    break
            
        # If the source has not changed but the ref has then just update the row
        found = False
        for val in range(0,len(self)):
            iter = self.get_iter(val)
            if source.get_handle() == self.get_value(iter,0).get_handle() and \
                   repos_ref == self.get_value(iter,1):
                self.row_changed(self.get_path(iter),iter)
                found = True
                break

        if not found:
            self.append([source,repos_ref])
        
    def set_repos(self, repos):
        self._repos = repos
        self.rebuild()

    def set_model(self, model):
        self._model = model
        self._db = model

    def get_deleted_items(self):
        # These are the ones that are in the original sources list
        # but no longer in the list model

        self.items = []
        for val in range(0,len(self)):
            iter = self.get_iter(val)
            self.items.append((self.get_value(iter,0).get_handle(),self.get_value(iter,1)))
        
        deleted = []
        for item in self.original_item_list:
            found = False
            for cur_item in self.items:
                if item[0] == cur_item[0] and \
                   item[1] == cur_item[1]:
                    found = True
                    break
            if not found:
                deleted.append(item)

        return deleted

    def get_added_items(self):
        # These are the ones that are in the list model but not in the
        # original sources list.

        self.items = []
        for val in range(0,len(self)):
            iter = self.get_iter(val)
            self.items.append((self.get_value(iter,0).get_handle(),self.get_value(iter,1)))
        
        added = []
        for cur_item in self.items:
            found = False
            for item in self.original_item_list:
                if item[0] == cur_item[0] and \
                   item[1] == cur_item[1]:
                    found = True
                    break
            if not found:
                added.append(cur_item)

        return added

    def get_update_items(self):
        # These are in both lists but the repos_ref has changed in the
        # list model.

        self.items = []
        for val in range(0,len(self)):
            iter = self.get_iter(val)
            self.items.append((self.get_value(iter,0).get_handle(),self.get_value(iter,1)))
        
        update = []
        for cur_item in self.items:
            found = False
            for item in self.original_item_list:
                if item[0] == cur_item[0] and \
                   item[1] == cur_item[1]:
                    found = True
                    break
            if found:
                update.append(item)

        return update

        
class ReposSrcListView:

    def __init__(self, db, widget):
        self._db = db
        
        self.database_changed(self._db)
        self._db.connect('database-changed', self.database_changed)

        self._widget = widget

        # Create the tree columns
        self._col1 = gtk.TreeViewColumn(_("Title"))
        self._col2 = gtk.TreeViewColumn(_("Author"))
        self._col3 = gtk.TreeViewColumn(_("Reference Note"))

        # Add columns
        self._widget.append_column(self._col1)
        self._widget.append_column(self._col2)
        self._widget.append_column(self._col3)

        # Create cell renders
        self._col1_cell = gtk.CellRendererText()
        self._col2_cell = gtk.CellRendererText()
        self._col3_cell = gtk.CellRendererText()

        # Add cells to view
        self._col1.pack_start(self._col1_cell, True)
        self._col2.pack_start(self._col2_cell, True)
        self._col3.pack_start(self._col3_cell, True)

        # Setup the cell data callback funcs
        self._col1.set_cell_data_func(self._col1_cell, self.object_title)
        self._col2.set_cell_data_func(self._col2_cell, self.object_author)
        self._col3.set_cell_data_func(self._col3_cell, self.object_ref_note)                        
        self._widget.set_enable_search(False)

        
    def database_changed(self,db):
        self._db = db

    # Methods for rendering the cells.
    
    def object_title(self, column, cell, model, iter, user_data=None):
        source = model.get_value(iter, 0)
        cell.set_property('text', source.get_title())

    def object_author(self, column, cell, model, iter, user_data=None):
        source = model.get_value(iter, 0)
        cell.set_property('text', source.get_author())

    def object_ref_note(self, column, cell, model, iter, user_data=None):
        o = model.get_value(iter, 1)
        cell.set_property('text', o.get_note())

    # proxy methods to provide access to the real widget functions.
    
    def set_model(self,model=None):
        self._widget.set_model(model)

    def get_model(self):
        return self._widget.get_model()

    def get_selection(self):
        return self._widget.get_selection()



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
        
        self.notebook = self.glade.get_widget("notebook")

#         self.phone = self.glade.get_widget("repository_phone")
#         self.email = self.glade.get_widget("repository_email")
#         self.search_url = self.glade.get_widget("repository_search_url")
#         self.home_url = self.glade.get_widget("repository_home_url")
        
#         self.phone.set_editable(mode)
#         self.email.set_editable(mode)
#         self.search_url.set_editable(mode)
#         self.home_url.set_editable(mode)

        self.addr_tab = self._add_page(AddrEmbedList(
            self.dbstate, self.uistate, self.track,
            repository.get_address_list()))
        
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

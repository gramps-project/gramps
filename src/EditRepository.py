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



class EditRepository:

    def __init__(self,repository,dbstate,uistate,parent_window=None,readonly=False):
        if repository:
            self.repository = repository
        else:
            self.repository = RelLib.Repository()
        self.dbstate = dbstate
        self.db = dbstate.db
        #self.parent = parent
        self.name_display = NameDisplay.displayer.display
        if repository:
            #    if parent and self.parent.child_windows.has_key(repository.get_handle()):
            #        self.parent.child_windows[repository.get_handle()].present(None)
            #        return
            #    else:
            self.win_key = repository.get_handle()
        else:
            self.win_key = self
        self.child_windows = {}
        self.path = self.db.get_save_path()
        self.not_loaded = 1
        self.ref_not_loaded = 1
        self.lists_changed = 0
        mode = not self.db.readonly

        self.top_window = gtk.glade.XML(const.gladeFile,"repositoryEditor","gramps")
        self.top = self.top_window.get_widget("repositoryEditor")

        Utils.set_titles(self.top,self.top_window.get_widget('repository_title'),
                         _('Repository Editor'))
        
        self.name = self.top_window.get_widget("repository_name")
        self.name.set_text(repository.get_name())
        self.name.set_editable(mode)

        self.type = self.top_window.get_widget("repository_type")
        self.type_selector = AutoComp.StandardCustomSelector( \
            Utils.repository_types,self.type,
            RelLib.Repository.CUSTOM,RelLib.Repository.LIBRARY)
        self.type_selector.set_values(repository.get_type())
        
        self.street = self.top_window.get_widget("repository_street")
        self.city = self.top_window.get_widget("repository_city")
        self.county = self.top_window.get_widget("repository_county")
        self.state = self.top_window.get_widget("repository_state")
        self.postal = self.top_window.get_widget("repository_postal")
        self.country = self.top_window.get_widget("repository_country")
        self.phone = self.top_window.get_widget("repository_phone")
        self.email = self.top_window.get_widget("repository_email")
        self.search_url = self.top_window.get_widget("repository_search_url")
        self.home_url = self.top_window.get_widget("repository_home_url")
        
        # FIXME: AddressBase has changed to support multiple addresses
        # the UI does not support this yet so for the time being we
        # just grab the first address
        addresses = repository.get_address_list()

        if len(addresses) != 0:
            address = addresses[0]
            self.street.set_text(address.get_street())
            self.city.set_text(address.get_city())        
            #self.county.set_text(address.get_county())
            self.state.set_text(address.get_state())
            self.postal.set_text(address.get_postal_code())
            self.country.set_text(address.get_country())
            self.phone.set_text(address.get_phone())
            #self.email.set_text(repository.get_email())
            #self.search_url.set_text(repository.get_search_url())
            #self.home_url.set_text(repository.get_home_url())

        self.street.set_editable(mode)
        self.city.set_editable(mode)
        self.county.set_editable(mode)
        self.state.set_editable(mode)
        self.postal.set_editable(mode)
        self.country.set_editable(mode)
        self.phone.set_editable(mode)
        self.email.set_editable(mode)
        self.search_url.set_editable(mode)
        self.home_url.set_editable(mode)


        self.note = self.top_window.get_widget("repository_note")
        self.note.set_editable(mode)
        self.notes_buffer = self.note.get_buffer()

        self.refs_label = self.top_window.get_widget("refsRepositoryEditor")
        self.notes_label = self.top_window.get_widget("notesRepositoryEditor")
        
        self.flowed = self.top_window.get_widget("repository_flowed")
        self.flowed.set_sensitive(mode)
        self.preform = self.top_window.get_widget("repository_preformatted")
        self.preform.set_sensitive(mode)
        
        self.refinfo = self.top_window.get_widget("refinfo")
        

        if repository.get_note():
            self.notes_buffer.set_text(repository.get_note())
            # FIXME: this get a 'gtk.Label' object has no attribute 'get_children'
            # from Utils.py", line 650
            #Utils.bold_label(self.notes_label)
            if repository.get_note_format() == 1:
                self.preform.set_active(1)
            else:
                self.flowed.set_active(1)

        # Setup source reference tab
        self.repos_source_view = ReposSrcListView(self.db,
                                                  self.top_window.get_widget("repository_sources"))
        self.repos_source_model = ReposSrcListModel(self.db,repository)
        self.repos_source_view.set_model(self.repos_source_model)

        self.top_window.signal_autoconnect({
            "on_switch_page" : self.on_switch_page,
            "on_repositoryEditor_help_clicked" : self.on_help_clicked,
            "on_repositoryEditor_ok_clicked" : self.on_repository_apply_clicked,
            "on_repositoryEditor_cancel_clicked" : self.close,
            "on_repositoryEditor_delete_event" : self.on_delete_event,
            "on_add_repos_sources_clicked"    : self.on_add_repos_ref_clicked,
            "on_delete_repos_ref_clicked" : self.on_delete_repos_ref_clicked,
            "on_edit_repos_ref_clicked"   : self.on_edit_repos_ref_clicked,
            "on_edit_repos_ref_row_activated" : self.on_edit_repos_ref_clicked,
            })



        if parent_window:
            self.top.set_transient_for(parent_window)

        self.top_window.get_widget('repository_ok').set_sensitive(not self.db.readonly)

        if parent_window:
            self.top.set_transient_for(parent_window)
        self.add_itself_to_menu()
        self.top.show()
        #self.refs_label.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
        #gobject.idle_add(self.display_references)


    def edit_cb(self, cell, path, new_text, data):
        node = self.data_model.get_iter(path)
        self.data_model.set_value(node,data,new_text)

    def on_delete_event(self,obj,b):
        self.close_child_windows()
        self.remove_itself_from_menu()

    def on_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        GrampsDisplay.help('adv-src')

    def close(self,obj):
        self.close_child_windows()
        self.remove_itself_from_menu()
        self.top.destroy()
        
    def close_child_windows(self):
        for child_window in self.child_windows.values():
            child_window.close(None)
        self.child_windows = {}

    def add_itself_to_menu(self):
        #FIXME
        return    
        self.parent.child_windows[self.win_key] = self
        if not self.repository:
            label = _("New Repository")
        else:
            label = self.repository.get_name()
        if not label.strip():
            label = _("New Repository")
        label = "%s: %s" % (_('Repository'),label)
        self.parent_menu_item = gtk.MenuItem(label)
        self.parent_menu_item.set_submenu(gtk.Menu())
        self.parent_menu_item.show()
        self.parent.winsmenu.append(self.parent_menu_item)
        self.winsmenu = self.parent_menu_item.get_submenu()
        self.menu_item = gtk.MenuItem(_('Repository Editor'))
        self.menu_item.connect("activate",self.present)
        self.menu_item.show()
        self.winsmenu.append(self.menu_item)

    def remove_itself_from_menu(self):
        # FIXME
        return
        del self.parent.child_windows[self.win_key]
        self.menu_item.destroy()
        self.winsmenu.destroy()
        self.parent_menu_item.destroy()

    def present(self,obj):
        self.top.present()

    def on_add_repos_ref_clicked(self,widget):
        RepositoryRefEdit.RepositoryRefSourceEdit(RelLib.RepoRef(),
                                                  None,
                                                  self.dbstate,
                                                  self.repos_source_model.update,
                                                  self)

    def on_delete_repos_ref_clicked(self,widget):
        selection = self.repos_source_view.get_selection()
        model, iter = selection.get_selected()
        if iter:
            model.remove(iter)
        return
        


    def on_edit_repos_ref_clicked(self,widget,path=None,colm=None,userp=None):
        selection = self.repos_source_view.get_selection()
        model, iter = selection.get_selected()
        
        if iter:
            source = model.get_value(iter,0)
            repos_ref  = model.get_value(iter,1)

            RepositoryRefEdit.RepositoryRefSourceEdit(repos_ref,
                                                      source,
                                                      self.dbstate,
                                                      self.repos_source_model.update,
                                                      self)



    def on_repository_apply_clicked(self,obj):

        name = unicode(self.name.get_text())
        if name != self.repository.get_name():
            self.repository.set_name(name)

        repos_type = self.type_selector.get_values()
        if repos_type != self.repository.get_type():
            self.repository.set_type(repos_type)


        # FIXME: AddressBase has changed to support multiple addresses
        # the UI does not support this yet so for the time being we
        # just grab the first address
        addresses = self.repository.get_address_list()

        if len(addresses) != 0:
            address = addresses[0]
        else:
            address = RelLib.Address()

        address.set_street(unicode(self.street.get_text()))
        address.set_city(unicode(self.city.get_text()))
        address.set_state(unicode(self.state.get_text()))
        address.set_postal_code(unicode(self.postal.get_text()))
        address.set_country(unicode(self.country.get_text()))
        address.set_phone(unicode(self.phone.get_text()))
        #address.set_search_url(unicode(self.search_url.get_text()))
        #address.set_home_url(unicode(self.home_url.get_text()))
        
        self.repository.set_address_list([address])
        
        note = unicode(self.notes_buffer.get_text(self.notes_buffer.get_start_iter(),
                                                  self.notes_buffer.get_end_iter(),False))
        if note != self.repository.get_note():
            self.repository.set_note(note)

        format = self.preform.get_active()
        if format != self.repository.get_note_format():
            self.repository.set_note_format(format)

        
        trans = self.db.transaction_begin()
        handle = None
        if self.repository.get_handle() == None:
            handle = self.db.add_repository(self.repository,trans)
        else:
            self.db.commit_repository(self.repository,trans)
            handle = self.repository.get_handle()
        self.db.transaction_commit(trans,_("Edit Repository (%s)") % name)



        # Handle the source reference list

        # First look for all the references that need to be deleted
        # These are the ones that are in the original sources list
        # but no longer in the list model
        items_deleted = self.repos_source_model.get_deleted_items()
        
        # Now look for those that need to be added.
        # These are the ones that are in the list model but not in the
        # original sources list.
        items_added =  self.repos_source_model.get_added_items()
        
        for item in items_added:
            item[1].set_reference_handle(handle)
        
        # Finally look for those that need updating
        # These are in both lists but the repos_ref has changed in the
        # list model.
        items_updated =  self.repos_source_model.get_update_items()

        all_sources = {}
        for item in items_deleted + items_added + items_updated:
            all_sources[item[0]] = 1

        commit_list = []
        for source_hdl in all_sources.keys():
            # Fetch existing list of repo_refs
            source = self.db.get_source_from_handle(source_hdl)
            original_list = source.get_reporef_list()

            # strip out those from this repository
            stripped_list = [ repos_ref for repos_ref \
                              in original_list  \
                              if repos_ref.get_reference_handle() != self.repository.get_handle() ]
            
            # Now add back in those to be added and updated
            new_list = stripped_list + \
                       [ item[1] for item in items_added if item[0] == source_hdl ] + \
                       [ item[1] for item in items_updated if item[0] == source_hdl ]

            
            # Set the new list on the source
            source.set_reporef_list(new_list)

            # add it to the list of sources to be commited
            commit_list.append(source)


        trans = self.db.transaction_begin()
        for source in commit_list:
            self.db.commit_source(source,trans)
        self.db.transaction_commit(trans,_("Edit Repository (%s)") % name)
        
        self.close(obj)

    def on_switch_page(self,obj,a,page):
        ##if page == 2 and self.not_loaded:
##            self.not_loaded = 0
##        elif page == 3 and self.ref_not_loaded:
##            self.ref_not_loaded = 0
##            self.refs_label.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
##            gobject.idle_add(self.display_references)
##        text = unicode(self.notes_buffer.get_text(self.notes_buffer.get_start_iter(),
##                                self.notes_buffer.get_end_iter(),False))
##        if text:
##            Utils.bold_label(self.notes_label)
##        else:
##            Utils.unbold_label(self.notes_label)
        pass


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

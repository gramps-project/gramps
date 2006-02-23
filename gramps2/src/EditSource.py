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
import gc
import sys

import logging
log = logging.getLogger(".")

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gobject
import gtk.glade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import Utils
import RelLib
import NameDisplay
import RepositoryRefEdit
import Spell
import GrampsDisplay
import DisplayState

from DisplayTabs import *
from WindowUtils import GladeIf
from GrampsWidgets import *

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------

class ReposRefListModel(gtk.ListStore):
    def __init__(self, source=None):
        gtk.ListStore.__init__(self,
                               object    # repostory reference
                               )
        self.set_source(source)

    def rebuild(self):
        """Clear the list and repopulate from the current source record."""
        self.clear()

        for repos_ref in self._source.get_reporef_list():
            self.append([repos_ref])

    def update(self,repos_ref):
        """Add the record if it is not already in the list otherwise
        replace the record with the new one."""

        found = False
        for val in range(0,len(self)):
            iter = self.get_iter(val)
            if repos_ref == self.get_value(iter,0):
                self.row_changed(self.get_path(iter),iter)
                found = True
                break

        if not found:
            self.append([repos_ref])
        
    def set_source(self, source):
        self._source = source
        self.rebuild()

class ReposRefListView:

    def __init__(self, dbstate, widget):
        self._dbstate = dbstate        
        self.database_changed(self._dbstate.db)
        self._db.connect('database-changed', self.database_changed)

        self._widget = widget

        # Create the tree columns
        self._col1 = gtk.TreeViewColumn(_("Name"))
        self._col2 = gtk.TreeViewColumn(_("Type"))
        self._col3 = gtk.TreeViewColumn(_("Note"))

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
        self._col1.set_cell_data_func(self._col1_cell, self.object_name)
        self._col2.set_cell_data_func(self._col2_cell, self.object_type)
        self._col3.set_cell_data_func(self._col3_cell, self.object_note)                        
        self._widget.set_enable_search(False)

        
    def database_changed(self,db):
        self._db = db

    # Methods for rendering the cells.
    
    def object_name(self, column, cell, model, iter, user_data=None):
        o = model.get_value(iter, 0)
        repos_hdl = o.get_reference_handle()
        repos = self._db.get_repository_from_handle(repos_hdl)
        cell.set_property('text', repos.get_name())

    def object_type(self, column, cell, model, iter, user_data=None):
        o = model.get_value(iter, 0)
        repos_hdl = o.get_reference_handle()
        repos = self._db.get_repository_from_handle(repos_hdl)
        rtype = repos.get_type()
        if rtype[0] == RelLib.Event.CUSTOM or rtype[0] not in Utils.repository_types:
            name = rtype[1]
        else:
            name = Utils.repository_types[rtype[0]]
        cell.set_property('text', name)

    def object_note(self, column, cell, model, iter, user_data=None):
        o = model.get_value(iter, 0)
        cell.set_property('text', o.get_note())

    # proxy methods to provide access to the real widget functions.
    
    def set_model(self,model=None):
        self._widget.set_model(model)

    def get_model(self):
        return self._widget.get_model()

    def get_selection(self):
        return self._widget.get_selection()

        
class EditSource(DisplayState.ManagedWindow):

    def __init__(self,dbstate,uistate,track,source,readonly=False):
        self.dbstate = dbstate
        self.track = track
        self.uistate = uistate

        self.db = dbstate.db
        self.name_display = NameDisplay.displayer.display

        DisplayState.ManagedWindow.__init__(self, uistate, self.track, source)

        if source:
            self.source = source
        else:
            self.source = RelLib.Source()

        self.glade = gtk.glade.XML(const.gladeFile,"sourceEditor","gramps")
        self.window = self.glade.get_widget("sourceEditor")

        Utils.set_titles(self.window,self.glade.get_widget('title'),
                         _('Source Editor'))
                
        self.vbox = self.glade.get_widget('vbox')

        self.notebook = gtk.Notebook()
        self.notebook.show()
        self.vbox.pack_start(self.notebook,True)

        self._create_tabbed_pages()
        self._setup_fields()
        self._connect_signals()
        self.show()

    def _connect_signals(self):
        self.glade.get_widget('cancel').connect('clicked', self.close_window)

        ok = self.glade.get_widget('ok')
        ok.set_sensitive(not self.db.readonly)
        ok.connect('clicked', self.apply_clicked)

    def _setup_fields(self):
        self.author = MonitoredEntry(
            self.glade.get_widget("author"),
            self.source.set_author,
            self.source.get_author,
            self.db.readonly)

        self.pubinfo = MonitoredEntry(
            self.glade.get_widget("pubinfo"),
            self.source.set_publication_info,
            self.source.get_publication_info,
            self.db.readonly)

        self.abbrev = MonitoredEntry(
            self.glade.get_widget("abbrev"),
            self.source.set_abbreviation,
            self.source.get_abbreviation,
            self.db.readonly)

        self.title = MonitoredEntry(
            self.glade.get_widget("source_title"),
            self.source.set_title,
            self.source.get_title,
            self.db.readonly)

    def _add_page(self,page):
        self.notebook.insert_page(page)
        self.notebook.set_tab_label(page,page.get_tab_widget())
        return page

    def _create_tabbed_pages(self):
        self.note_tab = self._add_page(NoteTab(
            self.dbstate, self.uistate, self.track,
            self.source.get_note_object()))
        
        self.gallery_tab = self._add_page(GalleryTab(
            self.dbstate, self.uistate, self.track,
            self.source.get_media_list()))
                                          
        self.data_tab = self._add_page(DataEmbedList(
            self.dbstate, self.uistate, self.track, self.source))
                                       
        self.repo_tab = self._add_page(RepoEmbedList(
            self.dbstate, self.uistate, self.track,
            self.source.get_reporef_list()))
        
        self.backref_tab = self._add_page(SourceBackRefList(
            self.dbstate, self.uistate, self.track,
            self.db.find_backlink_handles(self.source.handle)))
        
        self.notebook.show_all()

    def build_window_key(self,source):
        if source:
            return source.get_handle()
        else:
            return id(self)

    def build_menu_names(self,source):
        if source:
            label = "Edit Source"
        else:
            label = "New Source"
        return (label, _('Source Editor'))        

    def on_delete_event(self,obj,b):
        self.backref_tab.close()

    def on_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        GrampsDisplay.help('adv-src')

    def close_window(self,obj):
        self.backref_tab.close()
        self.close()

    def apply_clicked(self,obj):

        trans = self.db.transaction_begin()
        if self.source.get_handle() == None:
            self.db.add_source(self.source,trans)
        else:
            self.db.commit_source(self.source,trans)
        self.db.transaction_commit(trans,_("Edit Source (%s)") % title)
        self.close(obj)

class DelSrcQuery:
    def __init__(self,source,db,the_lists):
        self.source = source
        self.db = db
        self.the_lists = the_lists

    def query_response(self):
        trans = self.db.transaction_begin()
        self.db.disable_signals()
        
        (person_list,family_list,event_list,
            place_list,source_list,media_list) = self.the_lists

        src_handle_list = [self.source.get_handle()]

        for handle in person_list:
            person = self.db.get_person_from_handle(handle)
            person.remove_source_references(src_handle_list)
            self.db.commit_person(person,trans)

        for handle in family_list:
            family = self.db.get_family_from_handle(handle)
            family.remove_source_references(src_handle_list)
            self.db.commit_family(family,trans)

        for handle in event_list:
            event = self.db.get_event_from_handle(handle)
            event.remove_source_references(src_handle_list)
            self.db.commit_event(event,trans)

        for handle in place_list:
            place = self.db.get_place_from_handle(handle)
            place.remove_source_references(src_handle_list)
            self.db.commit_place(place,trans)

        for handle in source_list:
            source = self.db.get_source_from_handle(handle)
            source.remove_source_references(src_handle_list)
            self.db.commit_source(source,trans)

        for handle in media_list:
            media = self.db.get_object_from_handle(handle)
            media.remove_source_references(src_handle_list)
            self.db.commit_media_object(media,trans)

        self.db.enable_signals()
        self.db.remove_source(self.source.get_handle(),trans)
        self.db.transaction_commit(
            trans,_("Delete Source (%s)") % self.source.get_title())

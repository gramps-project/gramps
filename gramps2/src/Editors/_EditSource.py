#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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

import logging
log = logging.getLogger(".")

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk.glade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import RelLib
from _EditPrimary import EditPrimary

from DisplayTabs import \
     NoteTab,GalleryTab,DataEmbedList,SourceBackRefList,RepoEmbedList
from GrampsWidgets import *

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
class EditSource(EditPrimary):

    def __init__(self,dbstate,uistate,track,source):

        EditPrimary.__init__(self, dbstate, uistate, track,
                             source, dbstate.db.get_source_from_handle)

    def empty_object(self):
        return RelLib.Source()

    def _local_init(self):

        assert(self.obj)
        self.glade = gtk.glade.XML(const.gladeFile,"source_editor","gramps")

        self.set_window(self.glade.get_widget("source_editor"),
                        self.glade.get_widget('title'),
                        _('Source Editor'))

    def _connect_signals(self):
        self.define_ok_button(self.glade.get_widget('ok'),self.save)
        self.define_cancel_button(self.glade.get_widget('cancel'))
        self.define_help_button(self.glade.get_widget('help'),'adv-src')

    def _setup_fields(self):
        self.author = MonitoredEntry(
            self.glade.get_widget("author"),
            self.obj.set_author,
            self.obj.get_author,
            self.db.readonly)

        self.pubinfo = MonitoredEntry(
            self.glade.get_widget("pubinfo"),
            self.obj.set_publication_info,
            self.obj.get_publication_info,
            self.db.readonly)

        self.gid = MonitoredEntry(
            self.glade.get_widget("gid"),
            self.obj.set_gramps_id,
            self.obj.get_gramps_id,
            self.db.readonly)

        self.priv = PrivacyButton(
            self.glade.get_widget("private"),
            self.obj, self.db.readonly)

        self.abbrev = MonitoredEntry(
            self.glade.get_widget("abbrev"),
            self.obj.set_abbreviation,
            self.obj.get_abbreviation,
            self.db.readonly)

        self.title = MonitoredEntry(
            self.glade.get_widget("source_title"),
            self.obj.set_title,
            self.obj.get_title,
            self.db.readonly)

    def _create_tabbed_pages(self):
        notebook = gtk.Notebook()

        self.note_tab = self._add_tab(
            notebook,
            NoteTab(self.dbstate, self.uistate, self.track,
                    self.obj.get_note_object()))
        
        self.gallery_tab = self._add_tab(
            notebook,
            GalleryTab(self.dbstate, self.uistate, self.track,
                       self.obj.get_media_list()))
                                          
        self.data_tab = self._add_tab(
            notebook,
            DataEmbedList(self.dbstate, self.uistate, self.track,
                          self.obj))
                                       
        self.repo_tab = self._add_tab(
            notebook,
            RepoEmbedList(self.dbstate, self.uistate, self.track,
                          self.obj.get_reporef_list()))
        
        self.backref_tab = self._add_tab(
            notebook,
            SourceBackRefList(self.dbstate, self.uistate, self.track,
                              self.db.find_backlink_handles(self.obj.handle)))
        
        notebook.show_all()
        self.glade.get_widget('vbox').pack_start(notebook,True)

    def build_menu_names(self,source):
        if source:
            label = "Edit Source"
        else:
            label = "New Source"
        return (label, _('Source Editor'))        

    def _cleanup_on_exit(self):
        self.backref_tab.close()

    def save(self,*obj):
        if self.object_is_empty():
            from QuestionDialog import ErrorDialog
            
            ErrorDialog(_("Cannot save source"),
                        _("No data exists for this source. Please "
                          "enter data or cancel the edit."))
            return

        trans = self.db.transaction_begin()
        if self.obj.get_handle() == None:
            self.db.add_source(self.obj,trans)
        else:
            self.db.commit_source(self.obj,trans)
        self.db.transaction_commit(trans,
                                   _("Edit Source (%s)") % self.obj.get_title())
        self.close()

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

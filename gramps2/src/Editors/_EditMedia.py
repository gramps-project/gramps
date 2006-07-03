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
# Standard python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _
import os

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import RelLib
import Mime
import ImgManip
from _EditPrimary import EditPrimary

from GrampsWidgets import *
from DisplayTabs import SourceEmbedList,AttrEmbedList,NoteTab,MediaBackRefList

#-------------------------------------------------------------------------
#
# EditMedia
#
#-------------------------------------------------------------------------
class EditMedia(EditPrimary):

    def __init__(self,state,uistate,track,obj):

        EditPrimary.__init__(self, state, uistate, track, obj,
                             state.db.get_object_from_handle)

    def empty_object(self):
        return RelLib.MediaObject()

    def _local_init(self):
        assert(self.obj)
        self.glade = gtk.glade.XML(const.gladeFile,
                                   "change_global","gramps")
        self.set_window(self.glade.get_widget('change_global'),
                        self.glade.get_widget('title'),     
                        _('Media Properties Editor'))

    def _connect_signals(self):
        self.define_cancel_button(self.glade.get_widget('button91'))
        self.define_ok_button(self.glade.get_widget('ok'),self.save)
        self.define_help_button(self.glade.get_widget('button102'),'adv-media')

    def _setup_fields(self):
        self.date_field = MonitoredDate(
            self.glade.get_widget('date'),
            self.glade.get_widget("date_edit"),
            self.obj.get_date_object(),
            self.uistate,
            self.track,
            self.db.readonly)

        self.descr_window = MonitoredEntry(
            self.glade.get_widget("description"),
            self.obj.set_description,
            self.obj.get_description,
            self.db.readonly)
        
        self.gid = MonitoredEntry(
            self.glade.get_widget("gid"),
            self.obj.set_gramps_id,
            self.obj.get_gramps_id,
            self.db.readonly)

        pixmap = self.glade.get_widget("pixmap")
        
        mtype = self.obj.get_mime_type()
        if mtype:
            pb = ImgManip.get_thumbnail_image(self.obj.get_path(),mtype)
            pixmap.set_from_pixbuf(pb)
            descr = Mime.get_description(mtype)
            if descr:
                self.glade.get_widget("type").set_text(descr)
        else:
            pb = Mime.find_mime_type_pixbuf('text/plain')
            pixmap.set_from_pixbuf(pb)
            self.glade.get_widget("type").set_text(_('Note'))

        self.setup_filepath()
        
    def _create_tabbed_pages(self):
        notebook = gtk.Notebook()

        if self.obj.get_mime_type():
            self.src_list = self._add_tab(
                notebook,
                SourceEmbedList(self.dbstate,self.uistate,
                                self.track,self.obj.source_list))
            
            self.attr_list = self._add_tab(
                notebook,
                AttrEmbedList(self.dbstate, self.uistate, self.track,
                              self.obj.get_attribute_list()))
            
            self.note_tab = self._add_tab(
                notebook,
                NoteTab(self.dbstate, self.uistate, self.track,
                        self.obj.get_note_object()))
        else:
            self.note_tab = self._add_tab(
                notebook,
                NoteTab(self.dbstate, self.uistate, self.track,
                        self.obj.get_note_object()))

            self.src_list = self._add_tab(
                notebook,
                SourceEmbedList(self.dbstate,self.uistate,
                                self.track,self.obj.source_list))
            
            self.attr_list = self._add_tab(
                notebook,
                AttrEmbedList(self.dbstate, self.uistate, self.track,
                              self.obj.get_attribute_list()))

        self.backref_list = self._add_tab(
            notebook,
            MediaBackRefList(self.dbstate,self.uistate,self.track,
                             self.db.find_backlink_handles(self.obj.handle)))

        notebook.show_all()
        self.glade.get_widget('vbox').pack_start(notebook,True)

    def build_menu_names(self,person):
        win_menu_label = _("Media Properties")
        return (_('Edit Media Object'),win_menu_label)

    def select_file(self,obj):
        f = gtk.FileChooserDialog(
            _('Select Media Object'),
            action=gtk.FILE_CHOOSER_ACTION_OPEN,
            buttons=(gtk.STOCK_CANCEL,
                     gtk.RESPONSE_CANCEL,
                     gtk.STOCK_OPEN,
                     gtk.RESPONSE_OK))

        text = self.file_path.get_text()
        path = os.path.dirname(text)

        f.set_filename(path)

        status = f.run()
        if status == gtk.RESPONSE_OK:
            self.file_path.set_text(f.get_filename())
        f.destroy()
        
    def setup_filepath(self):
        self.select = self.glade.get_widget('file_select')
        self.file_path = self.glade.get_widget("path")
        
        if self.obj.get_mime_type():
            fname = self.obj.get_path()
            self.file_path.set_text(fname)
            self.select.connect('clicked', self.select_file)
        else:
            self.glade.get_widget('path_label').hide()
            self.file_path.hide()
            self.select.hide()
            
    def save(self, *obj):
        path = self.glade.get_widget('path').get_text()

        if path != self.obj.get_path():
            mime = Mime.get_type(path)
            self.obj.set_mime_type(mime)
        self.obj.set_path(path)

        trans = self.db.transaction_begin()
        self.db.commit_media_object(self.obj,trans)
        self.db.transaction_commit(trans,_("Edit Media Object"))
        self.close()

class DeleteMediaQuery:

    def __init__(self,media_handle,db,the_lists):
        self.db = db
        self.media_handle = media_handle
        self.the_lists = the_lists
        
    def query_response(self):
        trans = self.db.transaction_begin()
        self.db.disable_signals()
        
        (person_list,family_list,event_list,
                place_list,source_list) = self.the_lists

        for handle in person_list:
            person = self.db.get_person_from_handle(handle)
            new_list = [ photo for photo in person.get_media_list() \
                        if photo.get_reference_handle() != self.media_handle ]
            person.set_media_list(new_list)
            self.db.commit_person(person,trans)

        for handle in family_list:
            family = self.db.get_family_from_handle(handle)
            new_list = [ photo for photo in family.get_media_list() \
                        if photo.get_reference_handle() != self.media_handle ]
            family.set_media_list(new_list)
            self.db.commit_family(family,trans)

        for handle in event_list:
            event = self.db.get_event_from_handle(handle)
            new_list = [ photo for photo in event.get_media_list() \
                        if photo.get_reference_handle() != self.media_handle ]
            event.set_media_list(new_list)
            self.db.commit_event(event,trans)

        for handle in place_list:
            place = self.db.get_place_from_handle(handle)
            new_list = [ photo for photo in place.get_media_list() \
                        if photo.get_reference_handle() != self.media_handle ]
            place.set_media_list(new_list)
            self.db.commit_place(place,trans)

        for handle in source_list:
            source = self.db.get_source_from_handle(handle)
            new_list = [ photo for photo in source.get_media_list() \
                        if photo.get_reference_handle() != self.media_handle ]
            source.set_media_list(new_list)
            self.db.commit_source(source,trans)

        self.db.enable_signals()
        self.db.remove_object(self.media_handle,trans)
        self.db.transaction_commit(trans,_("Remove Media Object"))


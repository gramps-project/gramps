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
import gobject
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
import GrampsMime
import DateEdit
import DateHandler
import ImgManip
import DisplayState
import GrampsDisplay

from QuestionDialog import ErrorDialog
from DdTargets import DdTargets
from WindowUtils import GladeIf
from DisplayTabs import *

_drag_targets = [
    ('STRING', 0, 0),
    ('text/plain',0,0),
    ('text/uri-list',0,2),
    ('application/x-rootwin-drop',0,1)]

#-------------------------------------------------------------------------
#
# EditMedia
#
#-------------------------------------------------------------------------
class EditMedia(DisplayState.ManagedWindow):

    def __init__(self,state,uistate,track,obj):
        self.dp = DateHandler.parser
        self.dd = DateHandler.displayer

        DisplayState.ManagedWindow.__init__(self, uistate, track, obj)

        if self.already_exist:
            return

        self.state = state
        self.uistate = uistate

        self.pdmap = {}
        self.obj = obj
        self.lists_changed = 0
        self.db = self.state.db
        self.idle = None
        if obj:
            self.date_object = RelLib.Date(self.obj.get_date_object())
            self.alist = self.obj.get_attribute_list()[:]
            self.refs = 0
        else:
            self.date_object = RelLib.Date()
            self.alist = []
            self.refs = 1

        self.refmodel = None # this becomes the model for the references
        
        self.path = self.db.get_save_path()
        self.change_dialog = gtk.glade.XML(const.gladeFile,
                                           "change_global","gramps")
        self.gladeif = GladeIf(self.change_dialog)

        mode = not self.db.readonly
        
        title = _('Media Properties Editor')

        self.window = self.change_dialog.get_widget('change_global')
        self.select = self.change_dialog.get_widget('file_select')
        self.select.connect('clicked', self.select_file)
                            
        self.date_entry = self.change_dialog.get_widget('date')
        self.date_entry.set_editable(mode)
        
        if self.obj:
            self.date_entry.set_text(self.dd.display(self.date_object))
        
        Utils.set_titles(self.window,
                         self.change_dialog.get_widget('title'),title)
        
        self.descr_window = self.change_dialog.get_widget("description")
        self.descr_window.set_editable(mode)
        self.descr_window.set_text(self.obj.get_description())
        
        self.date_edit = self.change_dialog.get_widget("date_edit")
        self.date_edit.set_sensitive(mode)
        
        self.date_check = DateEdit.DateEdit(
            self.date_object, self.date_entry,
            self.date_edit, self.window)
        
        self.pixmap = self.change_dialog.get_widget("pixmap")
        
        mtype = self.obj.get_mime_type()
        if mtype:
            pb = ImgManip.get_thumbnail_image(self.obj.get_path(),mtype)
            self.pixmap.set_from_pixbuf(pb)
            descr = GrampsMime.get_description(mtype)
            if descr:
                self.change_dialog.get_widget("type").set_text(descr)
        else:
            self.change_dialog.get_widget("type").set_text(_('Note'))
            self.pixmap.hide()

        self.change_dialog.get_widget("gid").set_text(self.obj.get_gramps_id())

        self.update_info()
        
        self.gladeif.connect('change_global','delete_event',
                             self.on_delete_event)
        self.gladeif.connect('button91','clicked',self.close_window)
        self.gladeif.connect('ok','clicked',self.on_ok_clicked)
        self.gladeif.connect('button102','clicked',self.on_help_clicked)

        self.vbox = self.change_dialog.get_widget('vbox')
        self.notebook = gtk.Notebook()
        self.notebook.show()
        self.vbox.pack_start(self.notebook,True)

        self.attr_list = AttrEmbedList(self.state, self.uistate, self.track,
                                       self.obj.get_attribute_list())
        self.note_tab = NoteTab(self.state, self.uistate, self.track,
                                self.obj.get_note_object())
        self.src_list = SourceEmbedList(self.state,self.uistate,
                                        self.track,self.obj.source_list)

        self.notebook.insert_page(self.src_list)
        self.notebook.set_tab_label(self.src_list,self.src_list.get_tab_widget())

        self.notebook.insert_page(self.attr_list)
        self.notebook.set_tab_label(self.attr_list,self.attr_list.get_tab_widget())

        self.notebook.insert_page(self.note_tab)
        self.notebook.set_tab_label(self.note_tab,self.note_tab.get_tab_widget())
        self.show()

    def build_menu_names(self,person):
        win_menu_label = _("Media Properties")
        return (_('Edit Media Object'),win_menu_label)

    def build_window_key(self,person):
        if person:
            return person.get_handle()
        else:
            return id(self)

    def on_delete_event(self,obj,b):
        self.close()

    def select_file(self,obj):
        f = gtk.FileChooserDialog(_('Select Media Object'),
                                  action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                  buttons=(gtk.STOCK_CANCEL,
                                           gtk.RESPONSE_CANCEL,
                                           gtk.STOCK_OPEN,
                                           gtk.RESPONSE_OK))

        text = self.file_path.get_text()
        name = os.path.basename(text)
        path = os.path.dirname(text)

        f.set_filename(path)

        status = f.run()
        if status == gtk.RESPONSE_OK:
            self.file_path.set_text(f.get_filename())
        f.destroy()
        
    def close_window(self,obj):
        if self.idle != None:
            gobject.source_remove(self.idle)
        self.close()

    def update_info(self):
        fname = self.obj.get_path()
        self.file_path = self.change_dialog.get_widget("path")
        self.file_path.set_text(fname)
            
    def on_apply_clicked(self, obj):
        desc = unicode(self.descr_window.get_text())
        note = self.obj.get_note()
        path = self.change_dialog.get_widget('path').get_text()

        if path != self.obj.get_path():
            mime = GrampsMime.get_type(path)
            self.obj.set_mime_type(mime)
        self.obj.set_path(path)

        if not self.date_object.is_equal(self.obj.get_date_object()):
            self.obj.set_date_object(self.date_object)

        trans = self.db.transaction_begin()
        self.db.commit_media_object(self.obj,trans)
        self.db.transaction_commit(trans,_("Edit Media Object"))

    def on_help_clicked(self, obj):
        """Display the relevant portion of GRAMPS manual"""
        GrampsDisplay.help('adv-media')
        
    def on_ok_clicked(self, obj):
        self.on_apply_clicked(obj)
        self.close(obj)

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

def build_dropdown(entry,strings):
    store = gtk.ListStore(str)
    for value in strings:
        node = store.append()
        store.set(node,0,value)
    completion = gtk.EntryCompletion()
    completion.set_text_column(0)
    completion.set_model(store)
    entry.set_completion(completion)

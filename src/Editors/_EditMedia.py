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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk
from gtk import glade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import Config
import gen.lib
import Mime
import ThumbNails
import Utils
from Editors import EditPrimary
from widgets import MonitoredDate, MonitoredEntry, PrivacyButton
from DisplayTabs import (SourceEmbedList, AttrEmbedList, NoteTab, 
                         MediaBackRefList)
from Editors.AddMedia import AddMediaObject
from QuestionDialog import ErrorDialog
#-------------------------------------------------------------------------
#
# EditMedia
#
#-------------------------------------------------------------------------
class EditMedia(EditPrimary):

    def __init__(self, dbstate, uistate, track, obj, callback=None):

        EditPrimary.__init__(self, dbstate, uistate, track, obj,
                             dbstate.db.get_object_from_handle, 
                             dbstate.db.get_object_from_gramps_id, callback)
        if not self.obj.get_handle():
            #show the addmedia dialog immediately, with track of parent.
            AddMediaObject(dbstate, self.uistate, self.track, self.obj, 
                           self._update_addmedia)

    def empty_object(self):
        return gen.lib.MediaObject()

    def get_menu_title(self):
        if self.obj.get_handle():
            name = self.obj.get_description()
            if not name:
                name = self.obj.get_path()
            if not name:
                name = self.obj.get_mime_type()
            if not name:
                name = _('Note')
            dialog_title = _('Media: %s')  % name
        else:
            dialog_title = _('New Media')
        return dialog_title

    def _local_init(self):
        assert(self.obj)
        self.width_key = Config.MEDIA_WIDTH
        self.height_key = Config.MEDIA_HEIGHT
        self.glade = glade.XML(const.GLADE_FILE,
                                   "change_global","gramps")

        self.set_window(self.glade.get_widget('change_global'), 
                        None, self.get_menu_title())

    def _connect_signals(self):
        self.define_cancel_button(self.glade.get_widget('button91'))
        self.define_ok_button(self.glade.get_widget('ok'), self.save)
        self.define_help_button(self.glade.get_widget('button102'))

    def _setup_fields(self):
        self.date_field = MonitoredDate(self.glade.get_widget("date_entry"),
                                        self.glade.get_widget("date_edit"),
                                        self.obj.get_date_object(),
                                        self.uistate, self.track,
                                        self.db.readonly)

        self.descr_window = MonitoredEntry(self.glade.get_widget("description"),
                                           self.obj.set_description,
                                           self.obj.get_description,
                                           self.db.readonly)
        
        self.gid = MonitoredEntry(self.glade.get_widget("gid"),
                                  self.obj.set_gramps_id, 
                                  self.obj.get_gramps_id, self.db.readonly)

        self.privacy = PrivacyButton(self.glade.get_widget("private"),
                                     self.obj, self.db.readonly)

        self.pixmap = self.glade.get_widget("pixmap")
        ebox = self.glade.get_widget('eventbox')
        ebox.connect('button-press-event', self.button_press_event)
        
        self.mimetext = self.glade.get_widget("type")
        self.setup_filepath()
        self.determine_mime()
        self.draw_preview()

    def determine_mime(self):
        descr = Mime.get_description(self.obj.get_mime_type())
        if descr:
            self.mimetext.set_text(descr)

        path = self.file_path.get_text()
        path_full = Utils.media_path_full(self.db, path)
        if path != self.obj.get_path() and path_full != self.obj.get_path():
            #redetermine mime
            mime = Mime.get_type(Utils.find_file(path_full))
            self.obj.set_mime_type(mime)
            descr = Mime.get_description(mime)
            if descr:
                self.mimetext.set_text(descr)
            else:
                self.mimetext.set_text(_('Unknown'))
        #if mime type not set, is note
        if not self.obj.get_mime_type():
            self.mimetext.set_text(_('Note'))

    def draw_preview(self):
        mtype = self.obj.get_mime_type()
        if mtype:
            pb = ThumbNails.get_thumbnail_image(Utils.media_path_full(self.db, self.obj.get_path()), 
                        mtype)
            self.pixmap.set_from_pixbuf(pb)
        else:
            pb = Mime.find_mime_type_pixbuf('text/plain')
            self.pixmap.set_from_pixbuf(pb)

    def setup_filepath(self):
        self.select = self.glade.get_widget('file_select')
        self.file_path = self.glade.get_widget("path")

        fname = self.obj.get_path()
        self.file_path.set_text(fname)
        self.select.connect('clicked', self.select_file)

    def _create_tabbed_pages(self):
        notebook = gtk.Notebook()

        self.src_tab = SourceEmbedList(self.dbstate,
                                       self.uistate,
                                       self.track,
                                       self.obj)
        self._add_tab(notebook, self.src_tab)
        self.track_ref_for_deletion("src_tab")
        
        self.attr_tab = AttrEmbedList(self.dbstate,
                                      self.uistate,
                                      self.track,
                                      self.obj.get_attribute_list())
        self._add_tab(notebook, self.attr_tab)
        self.track_ref_for_deletion("attr_tab")
        
        self.note_tab = NoteTab(self.dbstate,
                                self.uistate,
                                self.track,
                                self.obj.get_note_list(), 
                                notetype=gen.lib.NoteType.MEDIA)
        self._add_tab(notebook, self.note_tab)
        self.track_ref_for_deletion("note_tab")

        self.backref_tab = MediaBackRefList(self.dbstate,
                                            self.uistate,
                                            self.track,
                             self.db.find_backlink_handles(self.obj.handle))
        self.backref_list = self._add_tab(notebook, self.backref_tab)
        self.track_ref_for_deletion("backref_tab")
        self.track_ref_for_deletion("backref_list")

        self._setup_notebook_tabs( notebook)
        notebook.show_all()
        self.glade.get_widget('vbox').pack_start(notebook, True)

    def build_menu_names(self, person):
        return (_('Edit Media Object'), self.get_menu_title())

    def button_press_event(self, obj, event):
        if event.button == 1 and event.type == gtk.gdk._2BUTTON_PRESS:
            self.view_media(obj)

    def view_media(self, obj):
        ref_obj = self.dbstate.db.get_object_from_handle(self.obj.handle)

        if ref_obj:
            media_path = Utils.media_path_full(self.dbstate.db,
                                               ref_obj.get_path())
            Utils.open_file_with_default_application(media_path)

    def select_file(self, val):
        self.determine_mime()
        path = self.file_path.get_text()
        self.obj.set_path(Utils.get_unicode_path(path))
        AddMediaObject(self.dbstate, self.uistate, self.track, self.obj, 
                       self._update_addmedia)

    def _update_addmedia(self, obj):
        """
        Called when the add media dialog has been called.
        This allows us to update the main form in response to
        any changes: Redraw relevant fields: description, mimetype and path
        """
        for obj in (self.descr_window, ):
            obj.update()
        fname = self.obj.get_path()
        self.file_path.set_text(fname)
        self.determine_mime()
        self.draw_preview()

    def save(self, *obj):
        self.ok_button.set_sensitive(False)

        if self.object_is_empty():
            ErrorDialog(_("Cannot save media object"),
                        _("No data exists for this media object. Please "
                          "enter data or cancel the edit."))
            self.ok_button.set_sensitive(True)
            return

        (uses_dupe_id, id) = self._uses_duplicate_id()
        if uses_dupe_id:
            prim_object = self.get_from_gramps_id(id)
            name = prim_object.get_description()
            msg1 = _("Cannot save media object. ID already exists.")
            msg2 = _("You have attempted to use the existing GRAMPS ID with "
                         "value %(id)s. This value is already used by '" 
                         "%(prim_object)s'. Please enter a different ID or leave "
                         "blank to get the next available ID value.") % {
                         'id' : id, 'prim_object' : name }
            ErrorDialog(msg1, msg2)
            self.ok_button.set_sensitive(True)
            return
        
        path = self.file_path.get_text()
        self.determine_mime()

        self.obj.set_path(Utils.get_unicode_path(path))

        trans = self.db.transaction_begin()
        if not self.obj.get_handle():
            self.db.add_object(self.obj, trans)
            msg = _("Add Media Object (%s)") % self.obj.get_description()
        else:
            if not self.obj.get_gramps_id():
                self.obj.set_gramps_id(self.db.find_next_object_gramps_id())
            self.db.commit_media_object(self.obj, trans)
            msg = _("Edit Media Object (%s)") % self.obj.get_description()
            
        self.db.transaction_commit(trans, msg)
        
        if self.callback:
            self.callback(self.obj)
        self.close()

    def _cleanup_on_exit(self):
        self.backref_list.close()

    def data_has_changed(self):
        """
        A date comparison can fail incorrectly because we have made the
        decision to store entered text in the date. However, there is no
        entered date when importing from a XML file, so we can get an
        incorrect fail.
        """
        
        if self.db.readonly:
            return False
        elif self.obj.handle:
            orig = self.get_from_handle(self.obj.handle)
            if orig:
                cmp_obj = orig
            else:
                cmp_obj = self.empty_object()
            return cmp(cmp_obj.serialize(True)[1:],
                       self.obj.serialize(True)[1:]) != 0
        else:
            cmp_obj = self.empty_object()
            return cmp(cmp_obj.serialize(True)[1:],
                       self.obj.serialize()[1:]) != 0

class DeleteMediaQuery:

    def __init__(self, dbstate, uistate, media_handle, the_lists):
        self.db = dbstate.db
        self.uistate = uistate
        self.media_handle = media_handle
        self.the_lists = the_lists
        
    def query_response(self):
        trans = self.db.transaction_begin()
        self.db.disable_signals()
        
        (person_list, family_list, event_list,
                place_list,source_list) = self.the_lists

        for handle in person_list:
            person = self.db.get_person_from_handle(handle)
            new_list = [ photo for photo in person.get_media_list() \
                        if photo.get_reference_handle() != self.media_handle ]
            person.set_media_list(new_list)
            self.db.commit_person(person, trans)

        for handle in family_list:
            family = self.db.get_family_from_handle(handle)
            new_list = [ photo for photo in family.get_media_list() \
                        if photo.get_reference_handle() != self.media_handle ]
            family.set_media_list(new_list)
            self.db.commit_family(family, trans)

        for handle in event_list:
            event = self.db.get_event_from_handle(handle)
            new_list = [ photo for photo in event.get_media_list() \
                        if photo.get_reference_handle() != self.media_handle ]
            event.set_media_list(new_list)
            self.db.commit_event(event, trans)

        for handle in place_list:
            place = self.db.get_place_from_handle(handle)
            new_list = [ photo for photo in place.get_media_list() \
                        if photo.get_reference_handle() != self.media_handle ]
            place.set_media_list(new_list)
            self.db.commit_place(place, trans)

        for handle in source_list:
            source = self.db.get_source_from_handle(handle)
            new_list = [ photo for photo in source.get_media_list() \
                        if photo.get_reference_handle() != self.media_handle ]
            source.set_media_list(new_list)
            self.db.commit_source(source, trans)

        self.db.enable_signals()
        self.db.remove_object(self.media_handle, trans)
        self.db.transaction_commit(trans, _("Remove Media Object"))

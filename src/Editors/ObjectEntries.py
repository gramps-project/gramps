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
import cPickle as pickle

import logging
_LOG = logging.getLogger(".objectentries")

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk
from pango import ELLIPSIZE_END

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gen.lib import (Place, MediaObject, Note)
from Editors._EditPlace import EditPlace
from Editors._EditMedia import EditMedia
from Editors._EditNote import EditNote
from Selectors import selector_factory
from DdTargets import DdTargets
from Errors import WindowActiveError
from Selectors import selector_factory

class ObjEntry(object):
    """
    Handles the selection of a existing or new Object. Supports Drag and Drop
    to select the object.
    This is the base class to create a real entry
    """
    EMPTY_TEXT = ""
    EMPTY_TEXT_RED = ""
    EDIT_STR = ""
    SHARE_STR = ""
    ADD_STR = ""
    DEL_STR = ""

    def __init__(self, dbstate, uistate, track, label, set_val, 
                 get_val, add_edt, share):
        """Pass the dbstate and uistate and present track.
            label is a gtk.Label that shows the persent value
            set_val is function that is called when handle changes, use it
                to update the calling module
            get_val is function that is called to obtain handle from calling
                module
            share is the gtk.Button to call the object selector or del connect
            add_edt is the gtk.Button with add or edit value. Pass None if 
                this button should not be present.
        """
        self.label = label
        self.add_edt = add_edt
        self.share = share
        self.dbstate = dbstate
        self.db = dbstate.db
        self.get_val = get_val
        self.set_val = set_val
        self.uistate = uistate
        self.track = track
        
        #connect drag and drop
        self._init_dnd()
        #set the object specific code
        self._init_object()

        #check if valid object:
        handle = self.get_val()
        if handle:
            obj = self.get_from_handle(handle)
            if not obj:
                #invalid val, set it to None
                self.set_val(None)
        if self.get_val():
            self.set_button(True)
            obj = self.get_from_handle(self.get_val())
            name = self.get_label(obj)
        else:
            name = u""
            self.set_button(False)

        if self.db.readonly:
            if self.add_edt is not None:
                self.add_edt.set_sensitive(False)
            self.share.set_sensitive(False)
        else:
            if self.add_edt is not None:
                self.add_edt.set_sensitive(True)
            self.share.set_sensitive(True)

        if self.add_edt is not None:
            self.add_edt.connect('clicked', self.add_edt_clicked)
        self.share.connect('clicked', self.share_clicked)
        
        if not self.db.readonly and not name:
            if self.add_edt is None:
                self.label.set_text(self.EMPTY_TEXT_RED)
            else:
                self.label.set_text(self.EMPTY_TEXT)
            self.label.set_use_markup(True)
        else:
            self.label.set_text(name)
        self.label.set_ellipsize(ELLIPSIZE_END)

    def _init_dnd(self):
        """inheriting objects must set this
        """
        pass

    def _init_object(self):
        """inheriting objects can use this to set extra variables
        """
        pass

    def get_from_handle(self, handle):
        """ return the object given the hande
            inheriting objects must set this
        """
        pass

    def get_label(self, object):
        """ return the label
            inheriting objects must set this
        """
        pass

    def after_edit(self, obj):
        name = self.get_label(obj)
        self.label.set_text(name)

    def add_edt_clicked(self, obj):
        """ if value, edit, if no value, call editor on new object
        """
        if self.get_val():
            obj = self.get_from_handle(self.get_val())
            self.call_editor(obj)
        else:
            self.call_editor()

    def call_editor(self, obj):
        """inheriting objects must set this
        """
        pass

    def call_selector(self):
        """inheriting objects must set this
        """
        pass

    def drag_data_received(self, widget, context, x, y, selection, info, time):
        (drag_type, idval, obj, val) = pickle.loads(selection.data)
        
        data = self.db.get_place_from_handle(obj)
        self.obj_added(data)
        
    def obj_added(self, data):
        """ callback from adding an object to the entry"""
        self.set_val(data.handle)
        self.label.set_text(self.get_label(data))
        self.set_button(True)

    def share_clicked(self, obj):
        """ if value, delete connect, in no value, select existing object
        """
        if self.get_val():
            self.set_val(None)
            self.label.set_text(self.EMPTY_TEXT)
            self.label.set_use_markup(True)
            self.set_button(False)
        else:
            select = self.call_selector()
            obj = select.run()
            if obj:
                self.obj_added(obj)

    def set_button(self, use_add):
        """ This sets the correct image to the two buttons.
            If False: select icon and add icon
            If True:  remove icon and edit icon
        """
        if self.add_edt is not None:
            for i in self.add_edt.get_children():
                self.add_edt.remove(i)
        for i in self.share.get_children():
            self.share.remove(i)

        if use_add:
            image = gtk.Image()
            image.set_from_stock(gtk.STOCK_REMOVE, gtk.ICON_SIZE_BUTTON)
            image.show()
            self.share.add(image)
            self.share.set_tooltip_text(self.DEL_STR)
            if self.add_edt is not None:
                image = gtk.Image()
                image.set_from_stock(gtk.STOCK_EDIT, gtk.ICON_SIZE_BUTTON)
                image.show()
                self.add_edt.add(image)
                self.add_edt.set_tooltip_text(self.EDIT_STR)
        else:
            image = gtk.Image()
            image.set_from_stock(gtk.STOCK_INDEX, gtk.ICON_SIZE_BUTTON)
            image.show()
            self.share.add(image)
            self.share.set_tooltip_text(self.SHARE_STR)
            if self.add_edt is not None:
                image = gtk.Image()
                image.set_from_stock(gtk.STOCK_ADD, gtk.ICON_SIZE_BUTTON)
                image.show()
                self.add_edt.add(image)
                self.add_edt.set_tooltip_text(self.ADD_STR)

class PlaceEntry(ObjEntry):
    """
    Handles the selection of a existing or new Place. Supports Drag and Drop
    to select a place.
    """
    EMPTY_TEXT = "<i>%s</i>" % _('To select a place, use drag-and-drop '
                                 'or use the buttons')
    EMPTY_TEXT_RED = "<i>%s</i>" % _('No place given, click button to select one')
    EDIT_STR = _('Edit place')
    SHARE_STR = _('Select an existing place')
    ADD_STR = _('Add a new place')
    DEL_STR = _('Remove place')
    
    def __init__(self, dbstate, uistate, track, label, set_val, 
                 get_val, add_edt, share):
        ObjEntry.__init__(self, dbstate, uistate, track, label, set_val, 
                 get_val, add_edt, share)

    def _init_dnd(self):
        """connect drag and drop of places
        """
        self.label.drag_dest_set(gtk.DEST_DEFAULT_ALL, [DdTargets.PLACE_LINK.target()], 
                               gtk.gdk.ACTION_COPY)
        self.label.connect('drag_data_received', self.drag_data_received)

    def get_from_handle(self, handle):
        """ return the object given the hande
        """
        return self.db.get_place_from_handle(handle)

    def get_label(self, place):
        return "%s [%s]" % (place.get_title(), place.gramps_id)

    def call_editor(self, obj=None):
        if obj is None:
            place = Place()
            func = self.obj_added
        else:
            place = obj
            func = self.after_edit
        try:
            EditPlace(self.dbstate, self.uistate, self.track, 
                      place, func)
        except WindowActiveError:
            pass

    def call_selector(self):
        cls = selector_factory('Place')
        return cls(self.dbstate, self.uistate, self.track)

# FIXME isn't used anywhere
class MediaEntry(ObjEntry):
    """
    Handles the selection of a existing or new media. Supports Drag and Drop
    to select a media object.
    """
    EMPTY_TEXT = "<i>%s</i>" % _('To select a media object, use drag-and-drop '
                                 'or use the buttons')
    EMPTY_TEXT_RED = "<i>%s</i>" % _('No image given, click button to select one')
    EDIT_STR = _('Edit media object')
    SHARE_STR = _('Select an existing media object')
    ADD_STR = _('Add a new media object')
    DEL_STR = _('Remove media object')
    
    def __init__(self, dbstate, uistate, track, label, set_val, 
                 get_val, add_edt, share):
        ObjEntry.__init__(self, dbstate, uistate, track, label, set_val, 
                 get_val, add_edt, share)

    def _init_dnd(self):
        """connect drag and drop of places
        """
        self.label.drag_dest_set(gtk.DEST_DEFAULT_ALL, [DdTargets.MEDIAOBJ.target()], 
                               gtk.gdk.ACTION_COPY)
        self.label.connect('drag_data_received', self.drag_data_received)

    def get_from_handle(self, handle):
        """ return the object given the hande
        """
        return self.db.get_object_from_handle(handle)

    def get_label(self, object):
        return "%s [%s]" % (object.get_description(), object.gramps_id)

    def call_editor(self, obj=None):
        if obj is None:
            object = MediaObject()
            func = self.obj_added
        else:
            object = obj
            func = self.after_edit
        try:
            EditMedia(self.dbstate, self.uistate, self.track, 
                      object, func)
        except WindowActiveError:
            pass

    def call_selector(self):
        cls = selector_factory('MediaObject')
        return cls(self.dbstate, self.uistate, self.track)
    
# FIXME isn't used anywhere
class NoteEntry(ObjEntry):
    """
    Handles the selection of a existing or new Note. Supports Drag and Drop
    to select a Note.
        """
    EMPTY_TEXT = "<i>%s</i>" % _('To select a note, use drag-and-drop '
                                 'or use the buttons')
    EMPTY_TEXT_RED = "<i>%s</i>" % _('No note given, click button to select one')
    EDIT_STR = _('Edit Note')
    SHARE_STR = _('Select an existing note')
    ADD_STR = _('Add a new note')
    DEL_STR = _('Remove note')
    
    def __init__(self, dbstate, uistate, track, label, set_val, 
                 get_val, add_edt, share):
        ObjEntry.__init__(self, dbstate, uistate, track, label, set_val, 
                 get_val, add_edt, share)
        self.notetype = None

    def set_notetype(self, type):
        """ set a notetype to use in new notes
        """
        self.notetype = type

    def get_notetype(self):
        """ return the set notetype
        """
        return self.notetype

    def _init_dnd(self):
        """connect drag and drop of places
        """
        self.label.drag_dest_set(gtk.DEST_DEFAULT_ALL, [DdTargets.NOTE_LINK.target()], 
                               gtk.gdk.ACTION_COPY)
        self.label.connect('drag_data_received', self.drag_data_received)

    def get_from_handle(self, handle):
        """ return the object given the hande
        """
        return self.db.get_note_from_handle(handle)

    def get_label(self, note):
        txt = " ".join(note.get().split())
        #String must be unicode for truncation to work for non ascii characters
        txt = unicode(txt)
        if len(txt) > 35:
            txt = txt[:35] + "..."
        return "%s [%s]" % (txt, note.gramps_id)

    def call_editor(self, obj=None):
        if obj is None:
            note = Note()
            note.set_type(self.get_notetype())
            func = self.obj_added
        else:
            note = obj
            func = self.after_edit
        try:
            EditNote(self.dbstate, self.uistate, self.track, 
                         note, func)
        except WindowActiveError:
            pass

    def call_selector(self):
        cls = selector_factory('Note')
        return cls(self.dbstate, self.uistate, self.track)

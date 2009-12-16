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
# python modules
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
import gtk

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import gen.lib
from editprimary import EditPrimary
from displaytabs import (GrampsTab, LocationEmbedList, SourceEmbedList, 
                         GalleryTab, NoteTab, WebEmbedList, PlaceBackRefList)
from gui.widgets import MonitoredEntry, PrivacyButton
from Errors import ValidationError
from PlaceUtils import conv_lat_lon
from QuestionDialog import ErrorDialog
from glade import Glade

#-------------------------------------------------------------------------
#
# Classes
#
#-------------------------------------------------------------------------

class MainLocTab(GrampsTab):
    """
    This class provides the tabpage of the main location tab
    """

    def __init__(self, dbstate, uistate, track, name, widget):
        """
        @param dbstate: The database state. Contains a reference to
        the database, along with other state information. The GrampsTab
        uses this to access the database and to pass to and created
        child windows (such as edit dialogs).
        @type dbstate: DbState
        @param uistate: The UI state. Used primarily to pass to any created
        subwindows.
        @type uistate: DisplayState
        @param track: The window tracking mechanism used to manage windows.
        This is only used to pass to generted child windows.
        @type track: list
        @param name: Notebook label name
        @type name: str/unicode
        @param widget: widget to be shown in the tab
        @type widge: gtk widget
        """
        GrampsTab.__init__(self, dbstate, uistate, track, name)
        eventbox = gtk.EventBox()
        eventbox.add(widget)
        self.pack_start(eventbox)
        self._set_label(show_image=False)
        eventbox.connect('key_press_event', self.key_pressed)
        self.show_all()

    def is_empty(self):
        """
        Override base class
        """
        return False

#-------------------------------------------------------------------------
#
# EditPlace
#
#-------------------------------------------------------------------------
class EditPlace(EditPrimary):

    def __init__(self, dbstate, uistate, track, place, callback=None):
        EditPrimary.__init__(self, dbstate, uistate, track, place,
                             dbstate.db.get_place_from_handle, 
                             dbstate.db.get_place_from_gramps_id, callback)

    def empty_object(self):
        return gen.lib.Place()

    def _local_init(self):
        self.width_key = 'interface.place-width'
        self.height_key = 'interface.place-height'
        
        self.top = Glade()

        self.set_window(self.top.toplevel, None,
                        self.get_menu_title())
        tblmloc =  self.top.get_object('table19')
        notebook = self.top.get_object('notebook3')
        #recreate start page as GrampsTab
        notebook.remove_page(0)
        self.mloc = MainLocTab(self.dbstate, self.uistate, self.track, 
                              _('_Location'), tblmloc)
        self.track_ref_for_deletion("mloc")


    def get_menu_title(self):
        if self.obj and self.obj.get_handle():
            title = self.obj.get_title()
            dialog_title = _('Place: %s')  % title
        else:
            dialog_title = _('New Place')
        return dialog_title

    def _connect_signals(self):
        self.define_ok_button(self.top.get_object('ok'), self.save)
        self.define_cancel_button(self.top.get_object('cancel'))
        self.define_help_button(self.top.get_object('help'))

    def _connect_db_signals(self):
        """
        Connect any signals that need to be connected. 
        Called by the init routine of the base class (_EditPrimary).
        """
        self._add_db_signal('place-rebuild', self._do_close)
        self._add_db_signal('place-delete', self.check_for_close)

    def _setup_fields(self):
        mloc = self.obj.get_main_location()
        
        self.title = MonitoredEntry(self.top.get_object("place_title"),
                                    self.obj.set_title, self.obj.get_title,
                                    self.db.readonly)
        
        self.street = MonitoredEntry(self.top.get_object("street"),
                                     mloc.set_street, mloc.get_street, 
                                     self.db.readonly)

        self.city = MonitoredEntry(self.top.get_object("city"),
                                   mloc.set_city, mloc.get_city, 
                                   self.db.readonly)
        
        self.gid = MonitoredEntry(self.top.get_object("gid"),
                                  self.obj.set_gramps_id, 
                                  self.obj.get_gramps_id, self.db.readonly)
        
        self.privacy = PrivacyButton(self.top.get_object("private"), self.obj, 
                                     self.db.readonly)

        self.parish = MonitoredEntry(self.top.get_object("parish"),
                                     mloc.set_parish, mloc.get_parish, 
                                     self.db.readonly)
        
        self.county = MonitoredEntry(self.top.get_object("county"),
                                     mloc.set_county, mloc.get_county, 
                                     self.db.readonly)
        
        self.state = MonitoredEntry(self.top.get_object("state"),
                                    mloc.set_state, mloc.get_state, 
                                    self.db.readonly)

        self.phone = MonitoredEntry(self.top.get_object("phone"),
                                    mloc.set_phone, mloc.get_phone, 
                                    self.db.readonly)
        
        self.postal = MonitoredEntry(self.top.get_object("postal"),
                                     mloc.set_postal_code, 
                                     mloc.get_postal_code, self.db.readonly)

        self.country = MonitoredEntry(self.top.get_object("country"),
                                      mloc.set_country, mloc.get_country, 
                                      self.db.readonly)

        self.longitude = MonitoredEntry(
            self.top.get_object("lon_entry"),
            self.obj.set_longitude, self.obj.get_longitude,
            self.db.readonly)
        self.longitude.connect("validate", self._validate_coordinate, "lon")
        #force validation now with initial entry
        self.top.get_object("lon_entry").validate(force=True)

        self.latitude = MonitoredEntry(
            self.top.get_object("lat_entry"),
            self.obj.set_latitude, self.obj.get_latitude,
            self.db.readonly)
        self.latitude.connect("validate", self._validate_coordinate, "lat")
        #force validation now with initial entry
        self.top.get_object("lat_entry").validate(force=True)
        
    def _validate_coordinate(self, widget, text, typedeg):
        if (typedeg == 'lat') and not conv_lat_lon(text, "0", "ISO-D"):
            return ValidationError(_(u"Invalid latitude (syntax: 18\u00b09'") +
                                   _('48.21"S, -18.2412 or -18:9:48.21)'))
        elif (typedeg == 'lon') and not conv_lat_lon("0", text, "ISO-D"):
            return ValidationError(_(u"Invalid longitude (syntax: 18\u00b09'") +
                                   _('48.21"E, -18.2412 or -18:9:48.21)'))

    def build_menu_names(self, place):
        return (_('Edit Place'), self.get_menu_title())

    def _create_tabbed_pages(self):
        """
        Create the notebook tabs and inserts them into the main
        window.
        
        """
        notebook = self.top.get_object('notebook3')

        self._add_tab(notebook, self.mloc)

        self.loc_list = LocationEmbedList(self.dbstate,
                                          self.uistate,
                                          self.track,
                                          self.obj.alt_loc)
        self._add_tab(notebook, self.loc_list)
        self.track_ref_for_deletion("loc_list")
        
        self.srcref_list = SourceEmbedList(self.dbstate,
                                           self.uistate,
                                           self.track,
                                           self.obj)
        self._add_tab(notebook, self.srcref_list)
        self.track_ref_for_deletion("srcref_list")
        
        self.note_tab = NoteTab(self.dbstate,
                                self.uistate,
                                self.track,
                                self.obj.get_note_list(),
                                self.get_menu_title(),
                                notetype=gen.lib.NoteType.PLACE)
        self._add_tab(notebook, self.note_tab)
        self.track_ref_for_deletion("note_tab")
        
        self.gallery_tab = GalleryTab(self.dbstate,
                                      self.uistate,
                                      self.track,
                                      self.obj.get_media_list())
        self._add_tab(notebook, self.gallery_tab)
        self.track_ref_for_deletion("gallery_tab")
       
        self.web_list = WebEmbedList(self.dbstate,
                                     self.uistate,
                                     self.track,
                                     self.obj.get_url_list())
        self._add_tab(notebook, self.web_list)
        self.track_ref_for_deletion("web_list")

        self.backref_list = PlaceBackRefList(self.dbstate,
                                             self.uistate,
                                             self.track,
                             self.db.find_backlink_handles(self.obj.handle))
        self.backref_tab = self._add_tab(notebook, self.backref_list)
        self.track_ref_for_deletion("backref_list")
        self.track_ref_for_deletion("backref_tab")

        self._setup_notebook_tabs(notebook)

    def _cleanup_on_exit(self):
        self.backref_tab.close()

    def save(self, *obj):
        self.ok_button.set_sensitive(False)
        if self.object_is_empty():
            ErrorDialog(_("Cannot save place"),
                        _("No data exists for this place. Please "
                          "enter data or cancel the edit."))
            self.ok_button.set_sensitive(True)
            return

        (uses_dupe_id, id) = self._uses_duplicate_id()
        if uses_dupe_id:
            prim_object = self.get_from_gramps_id(id)
            name = prim_object.get_title()
            msg1 = _("Cannot save place. ID already exists.")
            msg2 = _("You have attempted to use the existing Gramps ID with "
                         "value %(id)s. This value is already used by '" 
                         "%(prim_object)s'. Please enter a different ID or leave "
                         "blank to get the next available ID value.") % {
                         'id' : id, 'prim_object' : name }
            ErrorDialog(msg1, msg2)
            self.ok_button.set_sensitive(True)
            return

        trans = self.db.transaction_begin()
        if not self.obj.get_handle():
            self.db.add_place(self.obj, trans)
            msg = _("Add Place (%s)") % self.obj.get_title()
        else:
            if not self.obj.get_gramps_id():
                self.obj.set_gramps_id(self.db.find_next_place_gramps_id())
            self.db.commit_place(self.obj, trans)
            msg = _("Edit Place (%s)") % self.obj.get_title()
        self.db.transaction_commit(trans, msg)
        
        if self.callback:
            self.callback(self.obj)
        self.close()

#-------------------------------------------------------------------------
#
# DeletePlaceQuery
#
#-------------------------------------------------------------------------
class DeletePlaceQuery(object):

    def __init__(self, dbstate, uistate, place, person_list, family_list, 
                 event_list):
        self.db = dbstate.db
        self.uistate = uistate
        self.obj = place
        self.person_list = person_list
        self.family_list = family_list
        self.event_list  = event_list
        
    def query_response(self):
        trans = self.db.transaction_begin()
        self.db.disable_signals()
        
        place_handle = self.obj.get_handle()

        for handle in self.person_list:
            person = self.db.get_person_from_handle(handle)
            person.remove_handle_references('Place', place_handle)
            self.db.commit_person(person, trans)

        for handle in self.family_list:
            family = self.db.get_family_from_handle(handle)
            family.remove_handle_references('Place', place_handle)
            self.db.commit_family(family, trans)

        for handle in self.event_list:
            event = self.db.get_event_from_handle(handle)
            event.remove_handle_references('Place', place_handle)
            self.db.commit_event(event, trans)

        self.db.enable_signals()
        self.db.remove_place(place_handle, trans)
        self.db.transaction_commit(
            trans,_("Delete Place (%s)") % self.obj.get_title())

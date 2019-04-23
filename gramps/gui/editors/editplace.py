#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2009       Gary Burton
# Copyright (C) 2010,2015  Nick Hall
# Copyright (C) 2011       Tim G L lyons
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
import logging
log = logging.getLogger(".")

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext
from gramps.gen.lib import NoteType, Place
from gramps.gen.db import DbTxn
from .editprimary import EditPrimary
from .displaytabs import (PlaceRefEmbedList, PlaceNameEmbedList,
                          LocationEmbedList, CitationEmbedList,
                          GalleryTab, NoteTab, WebEmbedList, PlaceBackRefList)
from ..widgets import (MonitoredEntry, PrivacyButton, MonitoredTagList,
                       MonitoredDataType)
from gramps.gen.errors import ValidationError, WindowActiveError
from gramps.gen.utils.place import conv_lat_lon
from gramps.gen.display.place import displayer as place_displayer
from gramps.gen.config import config
from ..dialog import ErrorDialog
from ..glade import Glade
from gramps.gen.const import URL_MANUAL_SECT2

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------

WIKI_HELP_PAGE = URL_MANUAL_SECT2
WIKI_HELP_SEC = _('manual|Place_Editor_dialog')

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
        return Place()

    def _local_init(self):
        self.top = Glade()
        self.set_window(self.top.toplevel, None, self.get_menu_title())
        self.setup_configs('interface.place', 650, 450)
        self.place_name_label = self.top.get_object('place_name_label')
        self.place_name_label.set_text(_('place|Name:'))

    def get_menu_title(self):
        if self.obj and self.obj.get_handle():
            title = place_displayer.display(self.db, self.obj)
            dialog_title = _('Place: %s')  % title
        else:
            dialog_title = _('New Place')
        return dialog_title

    def _connect_signals(self):
        self.define_ok_button(self.top.get_object('ok'), self.save)
        self.define_cancel_button(self.top.get_object('cancel'))
        self.define_help_button(self.top.get_object('help'),
                WIKI_HELP_PAGE, WIKI_HELP_SEC)

    def _connect_db_signals(self):
        """
        Connect any signals that need to be connected.
        Called by the init routine of the base class (_EditPrimary).
        """
        self._add_db_signal('place-rebuild', self._do_close)
        self._add_db_signal('place-delete', self.check_for_close)

    def _setup_fields(self):

        if not config.get('preferences.place-auto'):
            self.top.get_object("place_title").show()
            self.top.get_object("place_title_label").show()
            self.title = MonitoredEntry(self.top.get_object("place_title"),
                                        self.obj.set_title, self.obj.get_title,
                                        self.db.readonly)

        self.name = MonitoredEntry(self.top.get_object("name_entry"),
                                    self.obj.get_name().set_value,
                                    self.obj.get_name().get_value,
                                    self.db.readonly,
                                    changed=self.name_changed)

        edit_button = self.top.get_object("name_button")
        edit_button.connect('clicked', self.edit_place_name)

        self.gid = MonitoredEntry(self.top.get_object("gid"),
                                  self.obj.set_gramps_id,
                                  self.obj.get_gramps_id, self.db.readonly)

        self.tags = MonitoredTagList(self.top.get_object("tag_label"),
                                     self.top.get_object("tag_button"),
                                     self.obj.set_tag_list,
                                     self.obj.get_tag_list,
                                     self.db,
                                     self.uistate, self.track,
                                     self.db.readonly)

        self.privacy = PrivacyButton(self.top.get_object("private"), self.obj,
                                     self.db.readonly)

        custom_place_types = sorted(self.db.get_place_types(),
                                    key=lambda s: s.lower())
        self.place_type = MonitoredDataType(self.top.get_object("place_type"),
                                            self.obj.set_type,
                                            self.obj.get_type,
                                            self.db.readonly,
                                            custom_place_types)

        self.code = MonitoredEntry(
            self.top.get_object("code_entry"),
            self.obj.set_code, self.obj.get_code,
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

        self.latlon = MonitoredEntry(
            self.top.get_object("latlon_entry"),
            self.set_latlongitude, self.get_latlongitude,
            self.db.readonly)

    def set_latlongitude(self, value):
        try:
            coma = value.index(',')
            self.longitude.set_text(value[coma+1:].strip())
            self.latitude.set_text(value[:coma].strip())
            self.top.get_object("lat_entry").validate(force=True)
            self.top.get_object("lon_entry").validate(force=True)
            self.obj.set_latitude(self.latitude.get_value())
            self.obj.set_longitude(self.longitude.get_value())
        except:
            pass

    def get_latlongitude(self):
        return ""

    def _validate_coordinate(self, widget, text, typedeg):
        if (typedeg == 'lat') and not conv_lat_lon(text, "0", "ISO-D"):
            return ValidationError(
                # translators: translate the "S" too (and the "or" of course)
                _('Invalid latitude\n(syntax: '
                  '18\u00b09\'48.21"S, -18.2412 or -18:9:48.21)'))
        elif (typedeg == 'lon') and not conv_lat_lon("0", text, "ISO-D"):
            return ValidationError(
                # translators: translate the "E" too (and the "or" of course)
                _('Invalid longitude\n(syntax: '
                  '18\u00b09\'48.21"E, -18.2412 or -18:9:48.21)'))

    def update_title(self):
        new_title = place_displayer.display(self.db, self.obj)
        self.top.get_object("preview_title").set_text(new_title)

    def name_changed(self, obj):
        self.update_title()

    def build_menu_names(self, place):
        return (_('Edit Place'), self.get_menu_title())

    def _create_tabbed_pages(self):
        """
        Create the notebook tabs and inserts them into the main
        window.

        """
        notebook = self.top.get_object('notebook3')

        self.placeref_list = PlaceRefEmbedList(self.dbstate,
                                               self.uistate,
                                               self.track,
                                               self.obj.get_placeref_list(),
                                               self.obj.handle,
                                               self.update_title)
        self._add_tab(notebook, self.placeref_list)
        self.track_ref_for_deletion("placeref_list")

        self.alt_name_list = PlaceNameEmbedList(self.dbstate,
                                                self.uistate,
                                                self.track,
                                                self.obj.alt_names)
        self._add_tab(notebook, self.alt_name_list)
        self.track_ref_for_deletion("alt_name_list")

        if len(self.obj.alt_loc) > 0:
            self.loc_list = LocationEmbedList(self.dbstate,
                                              self.uistate,
                                              self.track,
                                              self.obj.alt_loc)
            self._add_tab(notebook, self.loc_list)
            self.track_ref_for_deletion("loc_list")

        self.citation_list = CitationEmbedList(self.dbstate,
                                               self.uistate,
                                               self.track,
                                               self.obj.get_citation_list(),
                                               self.get_menu_title())
        self._add_tab(notebook, self.citation_list)
        self.track_ref_for_deletion("citation_list")

        self.note_tab = NoteTab(self.dbstate,
                                self.uistate,
                                self.track,
                                self.obj.get_note_list(),
                                self.get_menu_title(),
                                notetype=NoteType.PLACE)
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

    def edit_place_name(self, obj):
        try:
            from . import EditPlaceName
            EditPlaceName(self.dbstate, self.uistate, self.track,
                          self.obj.get_name(), self.edit_callback)
        except WindowActiveError:
            return

    def edit_callback(self, obj):
        value = self.obj.get_name().get_value()
        self.top.get_object("name_entry").set_text(value)

    def save(self, *obj):
        self.ok_button.set_sensitive(False)
        if self.obj.get_name().get_value().strip() == '':
            msg1 = _("Cannot save place. Name not entered.")
            msg2 = _("You must enter a name before saving.")
            ErrorDialog(msg1, msg2, parent=self.window)
            self.ok_button.set_sensitive(True)
            return

        (uses_dupe_id, id) = self._uses_duplicate_id()
        if uses_dupe_id:
            prim_object = self.get_from_gramps_id(id)
            name = place_displayer.display(self.db, prim_object)
            msg1 = _("Cannot save place. ID already exists.")
            msg2 = _("You have attempted to use the existing Gramps ID with "
                         "value %(id)s. This value is already used by '"
                         "%(prim_object)s'. Please enter a different ID or leave "
                         "blank to get the next available ID value.") % {
                         'id' : id, 'prim_object' : name }
            ErrorDialog(msg1, msg2, parent=self.window)
            self.ok_button.set_sensitive(True)
            return

        place_title = place_displayer.display(self.db, self.obj)
        if not self.obj.handle:
            with DbTxn(_("Add Place (%s)") % place_title,
                       self.db) as trans:
                self.db.add_place(self.obj, trans)
        else:
            if self.data_has_changed():
                with DbTxn(_("Edit Place (%s)") % place_title,
                           self.db) as trans:
                    if not self.obj.get_gramps_id():
                        self.obj.set_gramps_id(self.db.find_next_place_gramps_id())
                    self.db.commit_place(self.obj, trans)

        self._do_close()
        if self.callback:
            self.callback(self.obj)

#-------------------------------------------------------------------------
#
# DeletePlaceQuery
#
#-------------------------------------------------------------------------
class DeletePlaceQuery:

    def __init__(self, dbstate, uistate, place, person_list, family_list,
                 event_list):
        self.db = dbstate.db
        self.uistate = uistate
        self.obj = place
        self.person_list = person_list
        self.family_list = family_list
        self.event_list  = event_list

    def query_response(self):
        place_title = place_displayer.display(self.db, self.obj)
        with DbTxn(_("Delete Place (%s)") % place_title, self.db) as trans:
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

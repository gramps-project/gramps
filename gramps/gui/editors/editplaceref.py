#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2015       Nick Hall
# Copyright (C) 2019       Paul Culley
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
# Gramps modules
#
#-------------------------------------------------------------------------
from .editreference import RefTab, EditReference
from ..glade import Glade
from ..widgets import (MonitoredDate, MonitoredEntry, MonitoredDataType,
                       PrivacyButton, MonitoredTagList)
from .displaytabs import (PlaceRefEmbedList, PlaceNameEmbedList,
                          PlaceTypeEmbedList, PlaceEventEmbedList,
                          AttrEmbedList,
                          LocationEmbedList, CitationEmbedList,
                          GalleryTab, NoteTab, WebEmbedList, PlaceBackRefList)
from .editlocationtype import EditLocationType

from gramps.gen.lib import NoteType, PlaceType, PlaceHierType
from gramps.gen.db import DbTxn
from gramps.gen.errors import ValidationError, WindowActiveError
from gramps.gen.utils.place import conv_lat_lon
from gramps.gen.display.place import displayer as place_displayer
from gramps.gen.config import config
from ..dialog import ErrorDialog
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext


#-------------------------------------------------------------------------
#
# EditPlaceRef class
#
#-------------------------------------------------------------------------
class EditPlaceRef(EditReference):

    def __init__(self, state, uistate, track, place, place_ref, update):
        EditReference.__init__(self, state, uistate, track, place, place_ref,
                               update)

    def _local_init(self):

        self.top = Glade()
        self.set_window(self.top.toplevel, None, _('Place Reference Editor'))
        self.setup_configs('interface.place-ref', 600, 450)

        self.define_warn_box(self.top.get_object("warning"))
        self.define_expander(self.top.get_object("expander"))
        self.place_name_label = self.top.get_object('place_name_label')
        self.place_name_label.set_text(_('place|Name:'))
        self.name = None
        self.place_type = None

        tblref = self.top.get_object('table64')
        notebook = self.top.get_object('notebook_ref')
        #recreate start page as GrampsTab
        notebook.remove_page(0)
        self.reftab = RefTab(self.dbstate, self.uistate, self.track,
                             _('General'), tblref)
        tblref = self.top.get_object('maintable')

        notebook = self.top.get_object('notebook')
        #recreate start page as GrampsTab
        notebook.remove_page(0)
        self.primtab = RefTab(self.dbstate, self.uistate, self.track,
                              _('_General'), tblref)

    def _connect_signals(self):
        self.define_cancel_button(self.top.get_object('cancel'))
        self.ok_button = self.top.get_object('ok')
        self.define_ok_button(self.ok_button, self.save)
        self.define_help_button(self.top.get_object('help'))

    def _connect_db_signals(self):
        """
        Connect any signals that need to be connected.
        Called by the init routine of the base class (_EditPrimary).
        """
        self._add_db_signal('place-rebuild', self.close)
        self._add_db_signal('place-delete', self.check_for_close)

    def build_menu_names(self, placeref):
        if self.source and self.source.get_handle():
            title = self.source.get_title()
            submenu_label = _('Place: %s')  % title
        else:
            submenu_label = _('New Place')
        return (_('Place Reference Editor'), submenu_label)

    def _setup_fields(self):

        self.date_field = MonitoredDate(self.top.get_object("date_entry"),
                                        self.top.get_object("date_stat"),
                                        self.source_ref.get_date_object(),
                                        self.uistate, self.track,
                                        self.db.readonly)

        # set up a default value for heirarchy type based on enclosing
        # place type.  If place type is unknown (new place), this sets to
        # admin.  If the ref.type is already set, nothing changes
        self.source_ref.set_type_for_place(self.source)

        custom_hier_types = sorted(self.db.get_placehier_types(),
                                   key=lambda s: s.lower())
        self.heir_type = MonitoredDataType(
            self.top.get_object("heirarchy_type"), self.source_ref.set_type,
            self.source_ref.get_type, self.db.readonly, custom_hier_types)

        if not config.get('preferences.place-auto'):
            self.top.get_object("preview_title").hide()
            self.top.get_object("place_title").show()
            self.top.get_object("place_title_label").show()
            self.title = MonitoredEntry(self.top.get_object("place_title"),
                                        self.source.set_title,
                                        self.source.get_title,
                                        self.db.readonly)

        self.name = MonitoredEntry(self.top.get_object("name_entry"),
                                   self.source.get_name().set_value,
                                   self.source.get_name().get_value,
                                   self.db.readonly,
                                   changed=self.name_changed)

        edit_button = self.top.get_object("name_button")
        edit_button.connect('clicked', self.edit_place_name)

        self.gid = MonitoredEntry(self.top.get_object("gid"),
                                  self.source.set_gramps_id,
                                  self.source.get_gramps_id, self.db.readonly)

        self.tags = MonitoredTagList(self.top.get_object("tag_label"),
                                     self.top.get_object("tag_button"),
                                     self.source.set_tag_list,
                                     self.source.get_tag_list,
                                     self.db,
                                     self.uistate, self.track,
                                     self.db.readonly)

        self.privacy = PrivacyButton(self.top.get_object("private"), self.source,
                                     self.db.readonly)

        custom_place_types = sorted(self.db.get_place_types(),
                                    key=lambda s: s.lower())
        self.place_type = MonitoredDataType(self.top.get_object("place_type"),
                                            self.source.set_type,
                                            self.source.get_type,
                                            self.db.readonly,
                                            custom_place_types,
                                            changed=self.type_changed)

        type_button = self.top.get_object("type_button")
        type_button.connect('clicked', self.edit_place_type)

        self.longitude = MonitoredEntry(
            self.top.get_object("lon_entry"),
            self.source.set_longitude, self.source.get_longitude,
            self.db.readonly)
        self.longitude.connect("validate", self._validate_coordinate, "lon")
        #force validation now with initial entry
        self.top.get_object("lon_entry").validate(force=True)

        self.latitude = MonitoredEntry(
            self.top.get_object("lat_entry"),
            self.source.set_latitude, self.source.get_latitude,
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
            self.longitude.set_text(value[coma + 1:])
            self.latitude.set_text(value[:coma])
            self.top.get_object("lat_entry").validate(force=True)
            self.top.get_object("lon_entry").validate(force=True)
            self.source.set_latitude(self.latitude.get_value())
            self.source.set_longitude(self.longitude.get_value())
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
        if config.get('preferences.place-auto'):
            new_title = place_displayer.display(self.db, self.source)
            self.top.get_object("preview_title").set_text(new_title)

    def name_changed(self, obj):
        self.update_title()
        self.name_list.rebuild()

    def update_name(self):
        if self.name:
            self.name.get_val = self.source.get_name().get_value
            self.name.set_val = self.source.get_name().set_value
            self.name.update()

    def type_changed(self, _obj):
        self.type_list.rebuild()

    def update_type(self):
        if self.place_type:
            self.place_type.update()

    def _create_tabbed_pages(self):
        """
        Create the notebook tabs and inserts them into the main
        window.

        """
        notebook = self.top.get_object('notebook')
        notebook_ref = self.top.get_object('notebook_ref')

        self._add_tab(notebook, self.primtab)
        self._add_tab(notebook_ref, self.reftab)
        self.track_ref_for_deletion("primtab")
        self.track_ref_for_deletion("reftab")

        self.srcref_list = CitationEmbedList(
            self.dbstate, self.uistate, self.track,
            self.source_ref.get_citation_list())
        self._add_tab(notebook_ref, self.srcref_list)
        self.track_ref_for_deletion("srcref_list")

        self.placeref_list = PlaceRefEmbedList(self.dbstate,
                                               self.uistate,
                                               self.track,
                                               self.source.get_placeref_list(),
                                               self.source.handle,
                                               self.update_title)
        self._add_tab(notebook, self.placeref_list)
        self.track_ref_for_deletion("placeref_list")

        self.name_list = PlaceNameEmbedList(self.dbstate,
                                            self.uistate,
                                            self.track,
                                            self.source.name_list,
                                            self.update_name)
        self._add_tab(notebook, self.name_list)
        self.track_ref_for_deletion("name_list")

        self.type_list = PlaceTypeEmbedList(self.dbstate,
                                            self.uistate,
                                            self.track,
                                            self.source.type_list,
                                            self.update_type)
        self._add_tab(notebook, self.type_list)
        self.track_ref_for_deletion("type_list")

        if len(self.source.alt_loc) > 0:
            self.loc_list = LocationEmbedList(self.dbstate,
                                              self.uistate,
                                              self.track,
                                              self.source.alt_loc)
            self._add_tab(notebook, self.loc_list)
            self.track_ref_for_deletion("loc_list")

        self.event_list = PlaceEventEmbedList(
            self.dbstate,
            self.uistate,
            self.track,
            self.source)

        self._add_tab(notebook, self.event_list)
        self.track_ref_for_deletion("event_list")

        self.citation_list = CitationEmbedList(self.dbstate,
                                               self.uistate,
                                               self.track,
                                               self.source.get_citation_list())
        self._add_tab(notebook, self.citation_list)
        self.track_ref_for_deletion("citation_list")

        self.attr_list = AttrEmbedList(self.dbstate,
                                       self.uistate,
                                       self.track,
                                       self.source.get_attribute_list())
        self._add_tab(notebook, self.attr_list)
        self.track_ref_for_deletion("attr_list")

        self.note_tab = NoteTab(self.dbstate,
                                self.uistate,
                                self.track,
                                self.source.get_note_list(),
                                notetype=NoteType.PLACE)
        self._add_tab(notebook, self.note_tab)
        self.track_ref_for_deletion("note_tab")

        self.gallery_tab = GalleryTab(self.dbstate,
                                      self.uistate,
                                      self.track,
                                      self.source.get_media_list())
        self._add_tab(notebook, self.gallery_tab)
        self.track_ref_for_deletion("gallery_tab")

        self.web_list = WebEmbedList(self.dbstate,
                                     self.uistate,
                                     self.track,
                                     self.source.get_url_list())
        self._add_tab(notebook, self.web_list)
        self.track_ref_for_deletion("web_list")

        self.backref_list = PlaceBackRefList(self.dbstate,
                                             self.uistate,
                                             self.track,
                             self.db.find_backlink_handles(self.source.handle))
        self.backref_tab = self._add_tab(notebook, self.backref_list)
        self.track_ref_for_deletion("backref_list")
        self.track_ref_for_deletion("backref_tab")

        self._setup_notebook_tabs(notebook)

    def edit_place_name(self, obj):
        try:
            from . import EditPlaceName
            EditPlaceName(self.dbstate, self.uistate, self.track,
                          self.source.get_name(), self.edit_callback)
        except WindowActiveError:
            return

    def edit_callback(self, obj):
        value = self.source.get_name().get_value()
        self.top.get_object("name_entry").set_text(value)

    def edit_place_type(self, obj):
        try:
            EditLocationType(self.dbstate, self.uistate, self.track,
                             self.source.get_type(), self.edit_type_callback)
        except WindowActiveError:
            return

    def edit_type_callback(self, obj):
        value = self.source.get_type().get_value()
        self.top.get_object("type_entry").set_text(value)

    def save(self, *obj):
        self.ok_button.set_sensitive(False)

        if self.source.get_name().get_value().strip() == '':
            msg1 = _("Cannot save place. Name not entered.")
            msg2 = _("You must enter a name before saving.")
            ErrorDialog(msg1, msg2, parent=self.window)
            self.ok_button.set_sensitive(True)
            return

        if self.source.handle:
            with DbTxn(_("Modify Place"), self.db) as trans:
                self.db.commit_place(self.source, trans)
        else:
            if self.check_for_duplicate_id('Place'):
                return
            with DbTxn(_("Add Place"), self.db) as trans:
                self.db.add_place(self.source, trans)
            self.source_ref.ref = self.source.handle

        if self.update:
            self.update(self.source_ref, self.source)

        self.close()

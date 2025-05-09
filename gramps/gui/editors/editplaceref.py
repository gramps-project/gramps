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
from copy import deepcopy

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from .editreference import RefTab, EditReference
from ..glade import Glade
from ..widgets import (
    MonitoredDate,
    MonitoredEntry,
    MonitoredDataType,
    PrivacyButton,
    MonitoredTagList,
)
from ..widgets.placetypeselector import PlaceTypeSelector
from .displaytabs import (
    PlaceRefEmbedList,
    PlaceNameEmbedList,
    PlaceTypeEmbedList,
    PlaceEventEmbedList,
    AttrEmbedList,
    LocationEmbedList,
    CitationEmbedList,
    GalleryTab,
    NoteTab,
    WebEmbedList,
    PlaceBackRefList,
)
from .editplacetype import EditPlaceType

from gramps.gen.lib import NoteType, PlaceType, PlaceName, PlaceGroupType
from gramps.gen.db import DbTxn
from gramps.gen.errors import ValidationError, WindowActiveError
from gramps.gen.utils.place import conv_lat_lon
from gramps.gen.display.place import displayer as place_displayer
from gramps.gen.config import config
from ..dialog import ErrorDialog
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext


# -------------------------------------------------------------------------
#
# EditPlaceRef class
#
# -------------------------------------------------------------------------
class EditPlaceRef(EditReference):
    def __init__(self, state, uistate, track, place, place_ref, update):
        if not place.get_names():
            place.add_name(PlaceName())
        EditReference.__init__(self, state, uistate, track, place, place_ref, update)
        self.original = deepcopy(place.serialize())

    def _local_init(self):
        self.top = Glade()
        self.set_window(self.top.toplevel, None, _("Place Reference Editor"))
        self.setup_configs("interface.place-ref", 600, 450)

        self.define_warn_box(self.top.get_object("warning"))
        self.define_expander(self.top.get_object("expander"))
        # self.place_name_label = self.top.get_object('place_name_label')
        # self.place_name_label.set_text(_('Name:', 'place'))
        self.name = None
        self.place_type = None

        tblref = self.top.get_object("table64")
        notebook = self.top.get_object("notebook_ref")
        # recreate start page as GrampsTab
        notebook.remove_page(0)
        self.reftab = RefTab(
            self.dbstate, self.uistate, self.track, _("General"), tblref
        )

        tblref = self.top.get_object("maintable")

        notebook = self.top.get_object("notebook")
        # recreate start page as GrampsTab
        notebook.remove_page(0)
        self.primtab = RefTab(
            self.dbstate, self.uistate, self.track, _("_General"), tblref
        )

    def _post_init(self):
        self.name.grab_focus()

    def _connect_signals(self):
        self.define_cancel_button(self.top.get_object("cancel"))
        self.ok_button = self.top.get_object("ok")
        self.define_ok_button(self.ok_button, self.save)
        self.define_help_button(self.top.get_object("help"))

    def _connect_db_signals(self):
        """
        Connect any signals that need to be connected.
        Called by the init routine of the base class (_EditPrimary).
        """
        self._add_db_signal("place-rebuild", self.close)
        self._add_db_signal("place-delete", self.check_for_close)

    def build_menu_names(self, placeref):
        if self.source and self.source.get_handle():
            title = self.source.get_title()
            submenu_label = _("Place: %s") % title
        else:
            submenu_label = _("New Place")
        return (_("Place Reference Editor"), submenu_label)

    def _setup_fields(self):
        self.date_field = MonitoredDate(
            self.top.get_object("date_entry"),
            self.top.get_object("date_stat"),
            self.source_ref.get_date_object(),
            self.uistate,
            self.track,
            self.db.readonly,
        )

        # set up a default value for heirarchy type based on enclosing
        # place type.  If place type is unknown (new place), this sets to
        # admin.  If the ref.type is already set, nothing changes
        self.source_ref.set_type_for_place(self.source)

        custom_hier_types = sorted(
            self.db.get_placehier_types(), key=lambda s: s.lower()
        )
        self.heir_type = MonitoredDataType(
            self.top.get_object("heirarchy_type"),
            self.source_ref.set_type,
            self.source_ref.get_type,
            self.db.readonly,
            custom_hier_types,
        )

        if not config.get("preferences.place-auto"):
            self.top.get_object("preview_title").hide()
            self.top.get_object("place_title").show()
            self.top.get_object("place_title_label").show()
            self.title = MonitoredEntry(
                self.top.get_object("place_title"),
                self.source.set_title,
                self.source.get_title,
                self.db.readonly,
            )

        self.name = MonitoredEntry(
            self.top.get_object("name_entry"),
            self.source.get_name().set_value,
            self.source.get_name().get_value,
            self.db.readonly,
            changed=self.name_changed,
        )

        edit_button = self.top.get_object("name_button")
        edit_button.connect("clicked", self.edit_place_name)

        self.gid = MonitoredEntry(
            self.top.get_object("gid"),
            self.source.set_gramps_id,
            self.source.get_gramps_id,
            self.db.readonly,
        )

        self.tags = MonitoredTagList(
            self.top.get_object("tag_label"),
            self.top.get_object("tag_button"),
            self.source.set_tag_list,
            self.source.get_tag_list,
            self.db,
            self.uistate,
            self.track,
            self.db.readonly,
        )

        self.privacy = PrivacyButton(
            self.top.get_object("private"), self.source, self.db.readonly
        )

        custom_placegroup_types = sorted(
            self.db.get_placegroup_types(), key=lambda s: s.lower()
        )
        self.place_group = MonitoredDataType(
            self.top.get_object("place_group"),
            self.source.set_group,
            self.source.get_group,
            custom_placegroup_types,
        )

        self.place_type = PlaceTypeSelector(
            self.dbstate,
            self.top.get_object("place_type"),
            self.source.get_type(),
            changed=self.type_changed,
        )

        type_button = self.top.get_object("type_button")
        type_button.connect("clicked", self.edit_place_type)

        entry = self.top.get_object("lon_entry")
        entry.set_ltr_mode()
        self.longitude = MonitoredEntry(
            entry,
            self.source.set_longitude,
            self.source.get_longitude,
            self.db.readonly,
        )
        self.longitude.connect("validate", self._validate_coordinate, "lon")
        # force validation now with initial entry
        entry.validate(force=True)

        entry = self.top.get_object("lat_entry")
        entry.set_ltr_mode()
        self.latitude = MonitoredEntry(
            entry, self.source.set_latitude, self.source.get_latitude, self.db.readonly
        )
        self.latitude.connect("validate", self._validate_coordinate, "lat")
        # force validation now with initial entry
        entry.validate(force=True)

        entry = self.top.get_object("latlon_entry")
        entry.set_ltr_mode()
        self.latlon = MonitoredEntry(
            entry, self.set_latlongitude, self.get_latlongitude, self.db.readonly
        )

    def set_latlongitude(self, value):
        try:
            # Bug 12349, 12374
            parts = value.split(", ")
            if len(parts) == 2:
                latitude = parts[0].strip().replace(",", ".")
                longitude = parts[1].strip().replace(",", ".")
            else:
                latitude, longitude = value.split(",")

            self.longitude.set_text(longitude)
            self.latitude.set_text(latitude)
            self.top.get_object("lat_entry").validate(force=True)
            self.top.get_object("lon_entry").validate(force=True)
            self.source.set_latitude(self.latitude.get_value())
            self.source.set_longitude(self.longitude.get_value())
        except:
            pass

    def get_latlongitude(self):
        return ""

    def _validate_coordinate(self, widget, text, typedeg):
        if (typedeg == "lat") and not conv_lat_lon(text, "0", "ISO-D"):
            return ValidationError(
                # Translators: translate the "S" too (and the "or" of course)
                _(
                    "Invalid latitude\n(syntax: "
                    "18\u00b09'48.21\"S, -18.2412 or -18:9:48.21)"
                )
            )
        elif (typedeg == "lon") and not conv_lat_lon("0", text, "ISO-D"):
            return ValidationError(
                # Translators: translate the "E" too (and the "or" of course)
                _(
                    "Invalid longitude\n(syntax: "
                    "18\u00b09'48.21\"E, -18.2412 or -18:9:48.21)"
                )
            )

    def update_title(self):
        if config.get("preferences.place-auto"):
            new_title = place_displayer.display(self.db, self.source, fmt=0)
            self.top.get_object("preview_title").set_text(new_title)

    def name_changed(self, _obj):
        """deal with a change to the name list"""
        self.update_title()
        self.name_list.rebuild()

    def update_name(self):
        """Update the name when entry was changed"""
        if self.name:
            self.name.get_val = self.source.get_name().get_value
            self.name.set_val = self.source.get_name().set_value
            self.name.update()

    def type_changed(self):
        """Update the type list when the type is changed"""
        if self.source.group == PlaceGroupType.NONE:
            self.source.group = self.source.get_type().get_probable_group()
            self.place_group.update()
        self.type_list.rebuild()

    def update_type(self):
        """Update the combo when type is changed"""
        if self.place_type:
            self.place_type.update()

    def _create_tabbed_pages(self):
        """
        Create the notebook tabs and inserts them into the main
        window.

        """
        notebook = self.top.get_object("notebook")
        notebook_ref = self.top.get_object("notebook_ref")

        self._add_tab(notebook, self.primtab)
        self._add_tab(notebook_ref, self.reftab)
        self.track_ref_for_deletion("primtab")
        self.track_ref_for_deletion("reftab")

        self.srcref_list = CitationEmbedList(
            self.dbstate,
            self.uistate,
            self.track,
            self.source_ref.get_citation_list(),
            "placeref_editor_src_citations",
        )
        self._add_tab(notebook_ref, self.srcref_list)
        self.track_ref_for_deletion("srcref_list")

        self.placeref_list = PlaceRefEmbedList(
            self.dbstate,
            self.uistate,
            self.track,
            self.source.get_placeref_list(),
            "placeref_editor_placerefs",
            self.source.handle,
            self.update_title,
        )
        self._add_tab(notebook, self.placeref_list)
        self.track_ref_for_deletion("placeref_list")

        self.name_list = PlaceNameEmbedList(
            self.dbstate,
            self.uistate,
            self.track,
            self.source.name_list,
            "placeref_editor_names",
            self.update_name,
        )
        self._add_tab(notebook, self.name_list)
        self.track_ref_for_deletion("name_list")

        self.type_list = PlaceTypeEmbedList(
            self.dbstate,
            self.uistate,
            self.track,
            self.source.type_list,
            "placeref_editor_types",
            self.update_type,
        )
        self._add_tab(notebook, self.type_list)
        self.track_ref_for_deletion("type_list")

        if len(self.source.alt_loc) > 0:
            self.loc_list = LocationEmbedList(
                self.dbstate,
                self.uistate,
                self.track,
                self.source.alt_loc,
                "placeref_editor_locations",
            )
            self._add_tab(notebook, self.loc_list)
            self.track_ref_for_deletion("loc_list")

        self.event_list = PlaceEventEmbedList(
            self.dbstate,
            self.uistate,
            self.track,
            self.source,
            "placeref_editor_events",
        )

        self._add_tab(notebook, self.event_list)
        self.track_ref_for_deletion("event_list")

        self.citation_list = CitationEmbedList(
            self.dbstate,
            self.uistate,
            self.track,
            self.source.get_citation_list(),
            "placeref_editor_citations",
        )
        self._add_tab(notebook, self.citation_list)
        self.track_ref_for_deletion("citation_list")

        self.attr_list = AttrEmbedList(
            self.dbstate,
            self.uistate,
            self.track,
            self.source.get_attribute_list(),
            "placeref_editor_attributes",
        )
        self._add_tab(notebook, self.attr_list)
        self.track_ref_for_deletion("attr_list")

        self.note_tab = NoteTab(
            self.dbstate,
            self.uistate,
            self.track,
            self.source.get_note_list(),
            "placeref_editor_notes",
            notetype=NoteType.PLACE,
        )
        self._add_tab(notebook, self.note_tab)
        self.track_ref_for_deletion("note_tab")

        self.gallery_tab = GalleryTab(
            self.dbstate,
            self.uistate,
            self.track,
            self.source.get_media_list(),
        )
        self._add_tab(notebook, self.gallery_tab)
        self.track_ref_for_deletion("gallery_tab")

        self.web_list = WebEmbedList(
            self.dbstate,
            self.uistate,
            self.track,
            self.source.get_url_list(),
            "placeref_editor_internet",
        )
        self._add_tab(notebook, self.web_list)
        self.track_ref_for_deletion("web_list")

        self.backref_list = PlaceBackRefList(
            self.dbstate,
            self.uistate,
            self.track,
            self.db.find_backlink_handles(self.source.handle),
            "placeref_editor_references",
        )
        self.backref_tab = self._add_tab(notebook, self.backref_list)
        self.track_ref_for_deletion("backref_list")
        self.track_ref_for_deletion("backref_tab")

        self._setup_notebook_tabs(notebook)

    def edit_place_name(self, obj):
        try:
            from . import EditPlaceName

            EditPlaceName(
                self.dbstate,
                self.uistate,
                self.track,
                self.source.get_name(),
                self.edit_callback,
            )
        except WindowActiveError:
            return

    def edit_callback(self, obj):
        value = self.source.get_name().get_value()
        self.top.get_object("name_entry").set_text(value)
        self.name_list.rebuild()

    def edit_place_type(self, _obj):
        """Invoke the place type editor"""
        try:
            EditPlaceType(
                self.dbstate,
                self.uistate,
                self.track,
                self.source.get_type(),
                self.edit_type_callback,
            )
        except WindowActiveError:
            return

    def edit_type_callback(self, _obj):
        """Update the type list after type editor completes"""
        self.type_list.rebuild()
        self.update_type()

    def save(self, *obj):
        self.ok_button.set_sensitive(False)

        if self.source.get_name().get_value().strip() == "":
            msg1 = _("Cannot save place. Name not entered.")
            msg2 = _("You must enter a name before saving.")
            ErrorDialog(msg1, msg2, parent=self.window)
            self.ok_button.set_sensitive(True)
            return

        htype = self.source_ref.get_type()  # hierarchy type
        if htype.is_custom():  # if a new type, add to placetype groups
            self.db.placegroup_types.add(PlaceGroupType(str(htype)))

        place_title = place_displayer.display(self.db, self.source, fmt=0)
        if self.source.handle:
            # only commit if it has changed
            if self.source.serialize() != self.original:
                with DbTxn(_("Edit Place (%s)") % place_title, self.db) as trans:
                    self.db.commit_place(self.source, trans)
        else:
            if self.check_for_duplicate_id("Place"):
                return
            with DbTxn(_("Add Place (%s)") % place_title, self.db) as trans:
                self.db.add_place(self.source, trans)
            self.source_ref.ref = self.source.handle

        if self.update:
            self.update(self.source_ref, self.source)

        self.close()

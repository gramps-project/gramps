# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2011 Nick Hall
# Copyright (C) 2013 Heinz Brinker <heinzbrinker@yahoo.de>
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

# -------------------------------------------------------------------------
#
# Gtk modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk
from gi.repository.GLib import markup_escape_text

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.lib import EventType, EventRoleType
from gramps.gen.plug import Gramplet
from gramps.gui.widgets import Photo
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.display.place import displayer as place_displayer
from gramps.gen.datehandler import get_date
from gramps.gen.utils.file import media_path_full
from gramps.gen.const import COLON, GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext


class PersonDetails(Gramplet):
    """
    Displays details for a person.
    """

    def init(self):
        self.gui.WIDGET = self.build_gui()
        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add(self.gui.WIDGET)
        self.uistate.connect("nameformat-changed", self.update)
        self.uistate.connect("placeformat-changed", self.update)

    def build_gui(self):
        """
        Build the GUI interface.
        """
        self.top = Gtk.Box()
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.photo = Photo(self.uistate.screen_height() < 1000)
        self.photo.show()
        self.name = Gtk.Label(halign=Gtk.Align.START)
        self.name.set_selectable(True)
        vbox.pack_start(self.name, fill=True, expand=False, padding=7)
        self.grid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)
        self.grid.set_column_spacing(10)
        vbox.pack_start(self.grid, fill=True, expand=False, padding=5)
        vbox.show_all()
        self.top.pack_start(self.photo, fill=True, expand=False, padding=5)
        self.top.pack_start(vbox, fill=True, expand=True, padding=10)
        return self.top

    def add_row(self, title, value):
        """
        Add a row to the table.
        """
        label = Gtk.Label(
            label=title + COLON, halign=Gtk.Align.END, valign=Gtk.Align.START
        )
        label.set_selectable(True)
        label.show()
        value = Gtk.Label(label=value, halign=Gtk.Align.START)
        value.set_selectable(True)
        value.show()
        self.grid.add(label)
        self.grid.attach_next_to(value, label, Gtk.PositionType.RIGHT, 1, 1)

    def clear_grid(self):
        """
        Remove all the rows from the grid.
        """
        list(map(self.grid.remove, self.grid.get_children()))

    def db_changed(self):
        self.connect(self.dbstate.db, "person-update", self.update)

    def active_changed(self, handle):
        self.update()

    def update_has_data(self):
        """
        Determine if a person has_data by checking:

            1. has a birth, baptism, death, or burial event; OR
            2. has a father; OR
            3. has a mother
        """
        active_handle = self.get_active("Person")
        has_data = False
        if active_handle:
            active_person = self.dbstate.db.get_person_from_handle(active_handle)
            if active_person:
                for event_type in [
                    EventType(EventType.BIRTH),
                    EventType(EventType.BAPTISM),
                    EventType(EventType.DEATH),
                    EventType(EventType.BURIAL),
                ]:
                    event = self.get_event(active_person, event_type)
                    if event:
                        has_data = True
                        break
                if not has_data:
                    family_handle = active_person.get_main_parents_family_handle()
                    if family_handle:
                        family = self.dbstate.db.get_family_from_handle(family_handle)
                        handle = family.get_father_handle()
                        if handle:
                            if self.dbstate.db.get_person_from_handle(handle):
                                has_data = True
                            else:
                                handle = family.get_mother_handle()
                                if handle:
                                    if self.dbstate.db.get_person_from_handle(handle):
                                        has_data = True
        self.set_has_data(has_data)

    def main(self):  # return false finishes
        self.display_empty()
        active_handle = self.get_active("Person")
        if active_handle:
            active_person = self.dbstate.db.get_person_from_handle(active_handle)
            self.top.hide()
            if active_person:
                self.display_person(active_person)
            self.top.show()
        self.update_has_data()

    def display_person(self, active_person):
        """
        Display details of the active person.
        """
        self.load_person_image(active_person)
        self.name.set_markup(
            "<span size='large' weight='bold'>%s</span>"
            % markup_escape_text(name_displayer.display(active_person), -1)
        )
        self.clear_grid()
        self.display_alternate_names(active_person)
        self.display_parents(active_person)
        self.display_separator()
        self.display_type(active_person, EventType(EventType.BIRTH))
        self.display_type(active_person, EventType(EventType.BAPTISM))
        self.display_type(active_person, EventType(EventType.DEATH))
        self.display_type(active_person, EventType(EventType.BURIAL))
        self.display_separator()
        self.display_attribute(active_person, _("Occupation"))
        self.display_attribute(active_person, _("Title"))
        self.display_attribute(active_person, _("Religion"))

    def display_empty(self):
        """
        Display empty details when no person is selected.
        """
        self.photo.set_image(None)
        self.photo.set_uistate(None, None)
        self.name.set_text(_("No active person"))
        self.clear_grid()

    def display_separator(self):
        """
        Display an empty row to separate groupd of entries.
        """
        label = Gtk.Label()
        label.set_markup("<span font='sans 4'> </span>")
        label.set_selectable(True)
        label.show()
        self.grid.add(label)

    def display_alternate_names(self, active_person):
        """
        Display other names of the person
        """
        try:
            nlist = active_person.get_alternate_names()
            if len(nlist) > 0:
                for altname in nlist:
                    name_type = str(altname.get_type())
                    text = name_displayer.display_name(altname)
                    self.add_row(name_type, text)
                self.display_separator()
        except:
            pass

    def display_parents(self, active_person):
        """
        Display the parents of the active person.
        """
        family_handle = active_person.get_main_parents_family_handle()
        if family_handle:
            family = self.dbstate.db.get_family_from_handle(family_handle)
            handle = family.get_father_handle()
            if handle:
                father = self.dbstate.db.get_person_from_handle(handle)
                father_name = name_displayer.display(father)
            else:
                father_name = _("Unknown")
            handle = family.get_mother_handle()
            if handle:
                mother = self.dbstate.db.get_person_from_handle(handle)
                mother_name = name_displayer.display(mother)
            else:
                mother_name = _("Unknown")
        else:
            father_name = _("Unknown")
            mother_name = _("Unknown")

        self.add_row(_("Father"), father_name)
        self.add_row(_("Mother"), mother_name)

    def display_attribute(self, active_person, attr_key):
        """
        Display an attribute row.
        """
        values = []
        for attr in active_person.get_attribute_list():
            if attr.get_type() == attr_key:
                values.append(attr.get_value())
        if values:
            # Translators: needed for Arabic, ignore otherwise
            self.add_row(attr_key, _(", ").join(values))

    def display_type(self, active_person, event_type):
        """
        Display an event type row.
        """
        event = self.get_event(active_person, event_type)
        if event:
            self.add_row(str(event_type), self.format_event(event))

    def get_event(self, person, event_type):
        """
        Return an event of the given type.
        """
        for event_ref in person.get_event_ref_list():
            if int(event_ref.get_role()) == EventRoleType.PRIMARY:
                event = self.dbstate.db.get_event_from_handle(event_ref.ref)
                if event.get_type() == event_type:
                    return event
        return None

    def format_event(self, event):
        """
        Format the event for display.
        """
        date = get_date(event)
        handle = event.get_place_handle()
        if handle:
            place = place_displayer.display_event(self.dbstate.db, event)
            retval = _("%(date)s - %(place)s.") % {"date": date, "place": place}
        else:
            retval = _("%(date)s.") % dict(date=date)
        return retval

    def load_person_image(self, person):
        """
        Load the primary image if it exists.
        """
        media_list = person.get_media_list()
        if media_list:
            media_ref = media_list[0]
            object_handle = media_ref.get_reference_handle()
            obj = self.dbstate.db.get_media_from_handle(object_handle)
            full_path = media_path_full(self.dbstate.db, obj.get_path())
            mime_type = obj.get_mime_type()
            if mime_type and mime_type.startswith("image"):
                self.photo.set_image(full_path, mime_type, media_ref.get_rectangle())
                self.photo.set_uistate(self.uistate, object_handle)
            else:
                self.photo.set_image(None)
                self.photo.set_uistate(None, None)
        else:
            self.photo.set_image(None)
            self.photo.set_uistate(None, None)

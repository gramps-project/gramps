# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2011 Nick Hall
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
#

from gramps.gen.lib import EventType, EventRoleType
from gramps.gen.plug import Gramplet
from gramps.gui.widgets import Photo
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.ggettext import gettext as _
from gramps.gen.datehandler import get_date
from gramps.gen.utils.file import media_path_full
from gi.repository import Gtk
from gi.repository import Pango

class PersonDetails(Gramplet):
    """
    Displays details for a person.
    """
    def init(self):
        self.gui.WIDGET = self.build_gui()
        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add_with_viewport(self.gui.WIDGET)
        self.uistate.connect('nameformat-changed', self.update)

    def build_gui(self):
        """
        Build the GUI interface.
        """
        self.top = Gtk.HBox()
        vbox = Gtk.VBox()
        self.photo = Photo(self.uistate.screen_height() < 1000)
        self.photo.show()
        self.name = Gtk.Label()
        self.name.set_alignment(0, 0)
        self.name.modify_font(Pango.FontDescription('sans bold 12'))
        vbox.pack_start(self.name, fill=True, expand=False, padding=7)
        self.table = Gtk.Table(1, 2)
        vbox.pack_start(self.table, fill=True, expand=False, padding=5)
        vbox.show_all()
        self.top.pack_start(self.photo, fill=True, expand=False, padding=5)
        self.top.pack_start(vbox, fill=True, expand=True, padding=10)
        return self.top

    def add_row(self, title, value):
        """
        Add a row to the table.
        """
        label = Gtk.Label(label=title + ':')
        label.set_alignment(1, 0)
        label.show()
        value = Gtk.Label(label=value)
        value.set_alignment(0, 0)
        value.show()
        rows = self.table.get_property('n-rows')
        rows += 1
        self.table.resize(rows, 2)
        self.table.attach(label, 0, 1, rows, rows + 1, xoptions=Gtk.AttachOptions.FILL,
                                                       xpadding=10)
        self.table.attach(value, 1, 2, rows, rows + 1)
        
    def clear_table(self):
        """
        Remove all the rows from the table.
        """
        map(self.table.remove, self.table.get_children())
        self.table.resize(1, 2)
        
    def db_changed(self):
        self.dbstate.db.connect('person-update', self.update)

    def active_changed(self, handle):
        self.update()

    def update_has_data(self): 
        active_handle = self.get_active('Person')
        active_person = self.dbstate.db.get_person_from_handle(active_handle)
        self.set_has_data(active_person is not None)

    def main(self): # return false finishes
        active_handle = self.get_active('Person')
        active_person = self.dbstate.db.get_person_from_handle(active_handle)
        self.top.hide()
        if active_person:
            self.display_person(active_person)
            self.set_has_data(True)
        else:
            self.display_empty()
            self.set_has_data(False)
        self.top.show()

    def display_person(self, active_person):
        """
        Display details of the active person.
        """
        self.load_person_image(active_person)
        self.name.set_text(name_displayer.display(active_person))

        self.clear_table()
        self.display_parents(active_person)
        self.display_separator()
        self.display_type(active_person, EventType(EventType.BIRTH))
        self.display_type(active_person, EventType(EventType.BAPTISM))
        self.display_type(active_person, EventType(EventType.DEATH))
        self.display_type(active_person, EventType(EventType.BURIAL))
        self.display_separator()
        self.display_attribute(active_person, _('Occupation'))
        self.display_attribute(active_person, _('Title'))
        self.display_attribute(active_person, _('Religion'))

    def display_empty(self):
        """
        Display empty details when no person is selected.
        """
        self.photo.set_image(None)
        self.name.set_text(_('No active person'))
        self.clear_table()

    def display_separator(self):
        """
        Display an empty row to separate groupd of entries.
        """
        label = Gtk.Label(label='')
        label.modify_font(Pango.FontDescription('sans 4'))
        label.show()
        rows = self.table.get_property('n-rows')
        rows += 1
        self.table.resize(rows, 2)
        self.table.attach(label, 0, 1, rows, rows + 1, xoptions=Gtk.AttachOptions.FILL)

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
                father_name = _('Unknown')
            handle = family.get_mother_handle()
            if handle:
                mother = self.dbstate.db.get_person_from_handle(handle)
                mother_name = name_displayer.display(mother)
            else:
                mother_name = _('Unknown')
        else:
            father_name = _('Unknown')
            mother_name = _('Unknown')

        self.add_row(_('Father'), father_name)
        self.add_row(_('Mother'), mother_name)

    def display_attribute(self, active_person, attr_key):
        """
        Display an attribute row.
        """
        values = []
        for attr in active_person.get_attribute_list():
            if attr.get_type() == attr_key:
                values.append(attr.get_value())
        if values:
            self.add_row(attr_key, _(', ').join(values))

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
            place = self.dbstate.db.get_place_from_handle(handle).get_title()
            retval = _('%(date)s - %(place)s.') % {'date' : date,
                                                   'place' : place}
        else:
            retval = _('%(date)s.') % dict(date = date)
        return retval
        
    def load_person_image(self, person):
        """
        Load the primary image if it exists.
        """
        media_list = person.get_media_list()
        if media_list:
            media_ref = media_list[0]
            object_handle = media_ref.get_reference_handle()
            obj = self.dbstate.db.get_object_from_handle(object_handle)
            full_path = media_path_full(self.dbstate.db, obj.get_path())
            mime_type = obj.get_mime_type()
            if mime_type and mime_type.startswith("image"):
                self.photo.set_image(full_path, mime_type,
                                     media_ref.get_rectangle())
            else:
                self.photo.set_image(None)
        else:
            self.photo.set_image(None)

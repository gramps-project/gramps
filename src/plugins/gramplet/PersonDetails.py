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

from gen.lib import EventType, EventRoleType
from gen.plug import Gramplet
from gui.widgets import Photo
from gen.display.name import displayer as name_displayer
from gen.ggettext import gettext as _
import DateHandler
import Utils
import gtk
import pango

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
        self.load_obj = None
        self.load_rect = None
        self.top = gtk.HBox()
        vbox = gtk.VBox()
        self.photo = Photo(190.0)
        self.photo.show()
        self.name = gtk.Label()
        self.name.set_alignment(0, 0)
        self.name.modify_font(pango.FontDescription('sans bold 12'))
        vbox.pack_start(self.name, fill=True, expand=False, padding=7)
        table = gtk.Table(2, 2)
        self.father = self.make_row(table, 0, _('Father'))
        self.mother = self.make_row(table, 1, _('Mother'))
        vbox.pack_start(table, fill=True, expand=False, padding=5)
        table = gtk.Table(4, 2)
        self.birth = self.make_row(table, 0, _('Birth'))
        self.baptism = self.make_row(table, 1, _('Baptism'))
        self.death = self.make_row(table, 2, _('Death'))
        self.burial = self.make_row(table, 3, _('Burial'))
        vbox.pack_start(table, fill=True, expand=False, padding=5)
        table = gtk.Table(1, 2)
        self.occupation = self.make_row(table, 0, _('Occupation'))
        vbox.pack_start(table, fill=True, expand=False, padding=5)
        vbox.show_all()
        self.top.pack_start(self.photo, fill=True, expand=False, padding=5)
        self.top.pack_start(vbox, fill=True, expand=True, padding=10)
        return self.top

    def make_row(self, table, row, title):
        """
        Make a row in a table.
        """
        label = gtk.Label(title + ':')
        label.set_alignment(1, 0)
        widget = gtk.Label()
        widget.set_alignment(0, 0)
        table.attach(label, 0, 1, row, row + 1, xoptions=gtk.FILL, xpadding=10)
        table.attach(widget, 1, 2, row, row + 1)
        return (label, widget)
        
    def db_changed(self):
        self.dbstate.db.connect('person-update', self.update)
        self.update()

    def active_changed(self, handle):
        self.update()

    def main(self): # return false finishes
        active_handle = self.get_active('Person')
        active_person = self.dbstate.db.get_person_from_handle(active_handle)
        self.top.hide()
        if active_person:
            self.display_person(active_person)
        else:
            self.display_empty()
        self.top.show()

    def display_person(self, active_person):
        """
        Display details of the active person.
        """
        self.load_person_image(active_person)
        self.name.set_text(name_displayer.display(active_person))
        self.display_parents(active_person)
        self.display_type(active_person, self.birth, EventType.BIRTH)
        self.display_type(active_person, self.baptism, EventType.BAPTISM)
        self.display_type(active_person, self.death, EventType.DEATH)
        self.display_type(active_person, self.burial, EventType.BURIAL)
        occupation_text = self.get_attribute(active_person, 'Occupation')
        self.occupation[1].set_text(occupation_text)

    def display_empty(self):
        """
        Display empty details when no person is selected.
        """
        self.photo.set_image(None)
        self.name.set_text(_('No active person'))
        self.father[1].set_text(_('Unknown'))
        self.mother[1].set_text(_('Unknown'))
        self.birth[0].hide()
        self.birth[1].hide()
        self.baptism[0].hide()
        self.baptism[1].hide()
        self.death[0].hide()
        self.death[1].hide()
        self.burial[0].hide()
        self.burial[1].hide()
        self.occupation[1].set_text(_('Unknown'))

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
                self.father[1].set_text(name_displayer.display(father))
            else:
                self.father[1].set_text(_('Unknown'))
            handle = family.get_mother_handle()
            if handle:
                mother = self.dbstate.db.get_person_from_handle(handle)
                self.mother[1].set_text(name_displayer.display(mother))
            else:
                self.mother[1].set_text(_('Unknown'))
        else:
                self.father[1].set_text(_('Unknown'))
                self.mother[1].set_text(_('Unknown'))            

    def get_attribute(self, person, attr_key):
        """
        Return an attribute with the given key.
        """
        for attr in person.get_attribute_list():
            if attr.get_type() == attr_key:
                    return attr.get_value()
        return _('Unknown')

    def display_type(self, active_person, widget, event_type):
        """
        Display an event type row.
        """
        event = self.get_event(active_person, event_type)
        if event:
            widget[1].set_text(self.format_event(event))
            widget[0].show()
            widget[1].show()
        else:
            widget[1].set_text('')
            widget[0].hide()
            widget[1].hide()

    def get_event(self, person, event_type):
        """
        Return an event of the given type.
        """
        for event_ref in person.get_event_ref_list():
            if int(event_ref.get_role()) == EventRoleType.PRIMARY:
                event = self.dbstate.db.get_event_from_handle(event_ref.ref)
                if int(event.get_type()) == event_type:
                    return event
        return None

    def format_event(self, event):
        """
        Format the event for display.
        """
        date = DateHandler.get_date(event)
        handle = event.get_place_handle()
        if handle:
            place = self.dbstate.db.get_place_from_handle(handle).get_title()
            retval = _('%s - %s.') % (date, place)
        else:
            retval = _('%s.') % date
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
            full_path = Utils.media_path_full(self.dbstate.db, obj.get_path())
            mime_type = obj.get_mime_type()
            if mime_type and mime_type.startswith("image"):
                self.photo.set_image(full_path, media_ref.get_rectangle())
            else:
                self.photo.set_image(None)
        else:
            self.photo.set_image(None)

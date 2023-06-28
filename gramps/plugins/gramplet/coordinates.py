# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2011 Nick Hall
# Copyright (C) 2016-     Serge Noiraud
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
# Gtk modules
#
#-------------------------------------------------------------------------
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gui.editors import EditEvent
from gramps.gui.editors import EditPlace
from gramps.gui.listmodel import ListModel, NOSORT
from gramps.gen.plug import Gramplet
from gramps.gen.plug.report.utils import find_spouse
from gramps.gui.dbguielement import DbGUIElement
from gramps.gen.display.place import displayer as place_displayer
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.datehandler import get_date
from gramps.gen.utils.place import conv_lat_lon
from gramps.gen.utils.db import (get_participant_from_event,
                                 get_birth_or_fallback,
                                 get_marriage_or_fallback)
from gramps.gen.errors import WindowActiveError
from gramps.gen.config import config
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

class GeoEvents(Gramplet, DbGUIElement):

    def __init__(self, gui, nav_group=0):
        Gramplet.__init__(self, gui, nav_group)
        DbGUIElement.__init__(self, self.dbstate.db)

    """
    Displays the events for a person or family.
    """
    def init(self):
        self.gui.WIDGET = self.build_gui()
        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add(self.gui.WIDGET)
        self.gui.WIDGET.show()

    def _connect_db_signals(self):
        """
        called on init of DbGUIElement, connect to db as required.
        """
        self.callman.register_callbacks({'event-update': self.changed})
        self.callman.connect_all(keys=['event'])

    def changed(self, handle):
        """
        Called when a registered event is updated.
        """
        self.update()

    def build_gui(self):
        """
        Build the GUI interface.
        """
        tip = _('Right-click on a row to edit the selected event'
                ' or the related place.')
        self.set_tooltip(tip)
        top = Gtk.TreeView()
        top.set_hover_selection(True)
        titles = [('', NOSORT, 50,),
                  (_('Type'), 1, 100),
                  (_('Description'), 2, 250),
                  (_('Date'), 3, 160),
                  ('', NOSORT, 50),
                  (_('Place'), 4, 300),
                  (_('Id'), 5, 80),
                  (_('Latitude'), 6, 130),
                  (_('Longitude'), 7, 130),
                  ]
        self.model = ListModel(top, titles, right_click=self.menu_edit)
        return top

    def add_event_ref(self, event_ref, spouse=None, name=""):
        """
        Add an event to the model.
        """
        self.callman.register_handles({'event': [event_ref.ref]})
        event = self.dbstate.db.get_event_from_handle(event_ref.ref)
        event_date = get_date(event)
        event_sort = '%012d' % event.get_date_object().get_sort_value()
        place_name = place_displayer.display_event(self.dbstate.db, event)
        place_handle = event.get_place_handle()
        place_id = latitude = longitude = ""
        if place_handle:
            plc = self.dbstate.db.get_place_from_handle(place_handle)
            if plc:
                place_id = plc.get_gramps_id()
                latitude = plc.get_latitude()
                longitude = plc.get_longitude()
                latitude, longitude = conv_lat_lon(latitude, longitude, "D.D8")

        description = event.get_description()
        if description == "":
            description = name

        self.model.add((event.get_handle(),
                        str(event.get_type()),
                        description,
                        event_date,
                        event_sort,
                        place_name,
                        place_id,
                        latitude,
                        longitude
                        ))

    def menu_edit(self, treeview, event):
        """
        Show a menu to select either Edit the selected event or
        the Place related to this event.
        """
        self.menu = Gtk.Menu()
        menu = self.menu
        title = _('Edit the event')
        add_item = Gtk.MenuItem(label=title)
        add_item.connect("activate", self.edit_event, treeview)
        add_item.show()
        menu.append(add_item)
        title = _('Edit the place')
        add_item = Gtk.MenuItem(label=title)
        add_item.connect("activate", self.edit_place, treeview)
        add_item.show()
        menu.append(add_item)
        menu.show()
        menu.popup(None, None, None, None, event.button, event.time)

    def edit_place(self, menuitem, treeview):
        """
        Edit the place related to the selected event.
        """
        model, iter_ = treeview.get_selection().get_selected()
        if iter_:
            handle = model.get_value(iter_, 0)
            try:
                event = self.dbstate.db.get_event_from_handle(handle)
                place_handle = event.get_place_handle()
                place_id = latitude = longitude = ""
                if place_handle:
                    plc = self.dbstate.db.get_place_from_handle(place_handle)
                    EditPlace(self.dbstate, self.uistate, [], plc)
            except WindowActiveError:
                pass

    def edit_event(self, menuitem, treeview):
        """
        Edit the selected event.
        """
        model, iter_ = treeview.get_selection().get_selected()
        if iter_:
            handle = model.get_value(iter_, 0)
            try:
                event = self.dbstate.db.get_event_from_handle(handle)
                EditEvent(self.dbstate, self.uistate, [], event)
            except WindowActiveError:
                pass

class GeoPersonEvents(GeoEvents):
    """
    Displays the events for a person.
    """
    def db_changed(self):
        self.connect(self.dbstate.db, 'person-update', self.update)

    def active_changed(self, handle):
        self.update()

    def update_has_data(self):
        active_handle = self.get_active('Person')
        active = None
        if active_handle:
            active = self.dbstate.db.get_person_from_handle(active_handle)
        self.set_has_data(self.get_has_data(active))

    def get_has_data(self, active_person):
        """
        Return True if the gramplet has data, else return False.
        """
        if active_person:
            if active_person.get_event_ref_list():
                return True
            for family_handle in active_person.get_family_handle_list():
                family = self.dbstate.db.get_family_from_handle(family_handle)
                if family:
                    for event_ref in family.get_event_ref_list():
                        return True
        return False

    def main(self): # return false finishes
        active_handle = self.get_active('Person')

        self.model.clear()
        self.callman.unregister_all()
        if active_handle:
            self.display_person(active_handle)
        else:
            self.set_has_data(False)

    def display_person(self, active_handle):
        """
        Display the events for the active person.
        """
        active_person = self.dbstate.db.get_person_from_handle(active_handle)
        if active_person:
            for event_ref in active_person.get_event_ref_list():
                surname = name_displayer.display(active_person)
                self.add_event_ref(event_ref, name=surname)
            for family_handle in active_person.get_family_handle_list():
                family = self.dbstate.db.get_family_from_handle(family_handle)
                self.display_family(family, active_person)
        self.set_has_data(self.model.count > 0)

    def display_family(self, family, active_person):
        """
        Display the events for the given family.
        """
        spouse_handle = find_spouse(active_person, family)
        if spouse_handle:
            spouse = self.dbstate.db.get_person_from_handle(spouse_handle)
        else:
            spouse = None
        if family:
            for event_ref in family.get_event_ref_list():
                self.add_event_ref(event_ref, spouse)

class GeoFamilyEvents(GeoEvents):
    """
    Displays the events for a family.
    """
    def db_changed(self):
        self.connect(self.dbstate.db, 'family-update', self.update)
        self.connect_signal('Family', self.update)

    def update_has_data(self):
        active_handle = self.get_active('Family')
        active = None
        if active_handle:
            active = self.dbstate.db.get_family_from_handle(active_handle)
        self.set_has_data(self.get_has_data(active))

    def get_has_data(self, active_family):
        """
        Return True if the gramplet has data, else return False.
        """
        if active_family:
            for event_ref in active_family.get_event_ref_list():
                return True
        return False

    def main(self): # return false finishes
        active_handle = self.get_active('Family')

        self.model.clear()
        self.callman.unregister_all()
        if active_handle:
            self.display_family(active_handle)
        else:
            self.set_has_data(False)

    def display_family(self, active_handle):
        """
        Display the events for the active family.
        """
        active_family = self.dbstate.db.get_family_from_handle(active_handle)
        for event_ref in active_family.get_event_ref_list():
            self.add_event_ref(event_ref)
        self.set_has_data(self.model.count > 0)
        # for father, add all events
        father_handle = active_family.get_father_handle()
        if father_handle:
            father = self.dbstate.db.get_person_from_handle(father_handle)
            if father:
                for event_ref in father.get_event_ref_list():
                    surname = name_displayer.display(father)
                    self.add_event_ref(event_ref, name=surname)
        # for mother, add all events
        mother_handle = active_family.get_mother_handle()
        if mother_handle:
            mother = self.dbstate.db.get_person_from_handle(mother_handle)
            if mother:
                for event_ref in mother.get_event_ref_list():
                    surname = name_displayer.display(mother)
                    self.add_event_ref(event_ref, name=surname)
        # for each child, add all events
        child_ref_list = active_family.get_child_ref_list()
        if child_ref_list:
            for chld_ref in child_ref_list:
                if chld_ref:
                    child = self.dbstate.db.get_person_from_handle(chld_ref.ref)
                    if child:
                        for event_ref in child.get_event_ref_list():
                            surname = name_displayer.display(child)
                            self.add_event_ref(event_ref, name=surname)

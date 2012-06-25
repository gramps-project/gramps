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

from gui.editors import EditEvent
from gui.listmodel import ListModel, NOSORT
from gen.plug import Gramplet
from gen.ggettext import gettext as _
from gen.display.name import displayer as name_displayer
import gen.datehandler
from gen.utils.db import get_birth_or_fallback, get_marriage_or_fallback
from gen.errors import WindowActiveError
import gtk
from gen.config import config

age_precision = config.get('preferences.age-display-precision')

class Events(Gramplet):
    """
    Displays the events for a person or family.
    """
    def init(self):
        self.gui.WIDGET = self.build_gui()
        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add_with_viewport(self.gui.WIDGET)
        self.gui.WIDGET.show()

    def build_gui(self):
        """
        Build the GUI interface.
        """
        tip = _('Double-click on a row to edit the selected event.')
        self.set_tooltip(tip)
        top = gtk.TreeView()
        titles = [('', NOSORT, 50,),
                  (_('Type'), 1, 100),
                  (_('Details'), 2, 200),
                  (_('Date'), 3, 100),
                  ('', NOSORT, 50),
                  (_('Age'), 4, 100),
                  ('', NOSORT, 50),
                  (_('Place'), 5, 400),
                  (_('Role'), 6, 100)]
        self.model = ListModel(top, titles, event_func=self.edit_event)
        return top
        
    def add_event_ref(self, event_ref, spouse=None):
        """
        Add an event to the model.
        """
        event = self.dbstate.db.get_event_from_handle(event_ref.ref)
        event_date = gen.datehandler.get_date(event)
        event_sort = '%012d' % event.get_date_object().get_sort_value()
        person_age      = self.column_age(event)
        person_age_sort = self.column_sort_age(event)
        place = ''
        handle = event.get_place_handle()
        if handle:
            place = self.dbstate.db.get_place_from_handle(handle).get_title()
        if spouse:
            details = name_displayer.display(spouse)
        else:
            details = event.get_description()
        self.model.add((event.get_handle(),
                        str(event.get_type()),
                        details,
                        event_date,
                        event_sort,
                        person_age,
                        person_age_sort,
                        place,
                        str(event_ref.get_role())))

    def column_age(self, event):
        """
        Returns a string representation of age in years.  Change
        precision=2 for "year, month", or precision=3 for "year,
        month, days"
        """
        date = event.get_date_object()
        start_date = self.get_start_date()
        if date and start_date:
            return (date - start_date).format(precision=age_precision)
        else:
            return ""

    def column_sort_age(self, event):
        """
        Returns a string version of number of days of age.
        """
        date = event.get_date_object()
        start_date = self.get_start_date()
        if date and start_date:
            return "%09d" % int(date - start_date)
        else:
            return ""

    def edit_event(self, treeview):
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

class PersonEvents(Events):
    """
    Displays the events for a person.
    """
    def db_changed(self):
        self.dbstate.db.connect('person-update', self.update)

    def active_changed(self, handle):
        self.update()

    def update_has_data(self):
        active_handle = self.get_active('Person')
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
                for event_ref in family.get_event_ref_list():
                    return True
        return False

    def main(self): # return false finishes
        active_handle = self.get_active('Person')
            
        self.model.clear()
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
                self.add_event_ref(event_ref)
            for family_handle in active_person.get_family_handle_list():
                family = self.dbstate.db.get_family_from_handle(family_handle)
                father_handle = family.get_father_handle()
                mother_handle = family.get_mother_handle()
                if father_handle == active_handle:
                    spouse = self.dbstate.db.get_person_from_handle(mother_handle)
                else:
                    spouse = self.dbstate.db.get_person_from_handle(father_handle)
                for event_ref in family.get_event_ref_list():
                    self.add_event_ref(event_ref, spouse)
        self.set_has_data(self.model.count > 0)

    def get_start_date(self):
        """
        Get the start date for a person, usually a birth date, or
        something close to birth.
        """
        active_handle = self.get_active('Person')
        active = self.dbstate.db.get_person_from_handle(active_handle)
        event = get_birth_or_fallback(self.dbstate.db, active)
        return event.get_date_object() if event else None

class FamilyEvents(Events):
    """
    Displays the events for a family.
    """
    def db_changed(self):
        self.dbstate.db.connect('family-update', self.update)
        self.connect_signal('Family', self.update)

    def update_has_data(self):
        active_handle = self.get_active('Family')
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

    def get_start_date(self):
        """
        Get the start date for a family, usually a marriage date, or
        something close to marriage.
        """
        active_handle = self.get_active('Family')
        active = self.dbstate.db.get_family_from_handle(active_handle)
        event = get_marriage_or_fallback(self.dbstate.db, active)
        return event.get_date_object() if event else None


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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

# -------------------------------------------------------------------------
#
# Gtk modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gui.editors import EditEvent
from gramps.gui.listmodel import ListModel, NOSORT
from gramps.gen.plug import Gramplet
from gramps.gen.lib import EventType, Date
from gramps.gen.plug.report.utils import find_spouse
from gramps.gui.dbguielement import DbGUIElement
from gramps.gen.display.place import displayer as place_displayer
from gramps.gen.datehandler import get_date
from gramps.gen.utils.db import (
    get_participant_from_event,
    get_birth_or_fallback,
    get_marriage_or_fallback,
)
from gramps.gen.errors import WindowActiveError
from gramps.gen.config import config
from gramps.gen.proxy.cache import CacheProxyDb
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gui.widgets.persistenttreeview import PersistentTreeView

_ = glocale.translation.gettext

age_precision = config.get("preferences.age-display-precision")


class Events(Gramplet, DbGUIElement):
    def __init__(self, gui, nav_group=0):
        Gramplet.__init__(self, gui, nav_group)
        DbGUIElement.__init__(self, self.dbstate.db)
        self.db = None

    """
    Displays the events for a person or family.
    """

    def init(self):
        self.gui.WIDGET = self.build_gui()
        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add(self.gui.WIDGET)
        self.gui.WIDGET.show()
        self.gui.WIDGET.restore_column_size()

    def on_save(self):
        self.gui.WIDGET.save_column_info()

    def _connect_db_signals(self):
        """
        called on init of DbGUIElement, connect to db as required.
        """
        self.callman.register_callbacks({"event-update": self.changed})
        self.callman.connect_all(keys=["event"])

    def changed(self, handle):
        """
        Called when a registered event is updated.
        """
        self.update()

    def build_gui(self):
        """
        Build the GUI interface.
        """
        tip = _("Double-click on a row to edit the selected event.")
        self.set_tooltip(tip)
        top = PersistentTreeView(self.uistate, __name__)
        titles = [
            (
                "",
                NOSORT,
                50,
            ),
            (_("Type"), 1, 100),
            (_("Description"), 2, 150),
            (_("Date"), 4, 100),
            ("", NOSORT, 50),
            (_("Age"), 6, 100),
            ("", NOSORT, 50),
            (_("Place"), 7, 400),
            (_("Main Participants"), 8, 200),
            (_("Role"), 9, 100),
        ]
        self.model = ListModel(top, titles, event_func=self.edit_event)
        return top

    def add_event_ref(self, event_ref, spouse=None):
        """
        Add an event to the model.
        """
        self.callman.register_handles({"event": [event_ref.ref]})
        event = self.db.get_event_from_handle(event_ref.ref)
        event_date = get_date(event)
        event_sort = "%012d" % event.get_date_object().get_sort_value()
        person_age = self.column_age(event)
        person_age_sort = self.column_sort_age(event)
        place = place_displayer.display_event(self.db, event)

        participants = get_participant_from_event(self.db, event_ref.ref)

        self.model.add(
            (
                event.get_handle(),
                str(event.get_type()),
                event.get_description(),
                event_date,
                event_sort,
                person_age,
                person_age_sort,
                place,
                participants,
                str(event_ref.get_role()),
            )
        )

    def column_age(self, event):
        """
        Returns a string representation of age in years.  Change
        precision=2 for "year, month", or precision=3 for "year,
        month, days"
        """
        date = event.get_date_object()
        start_date = self.cached_start_date
        if date and start_date:
            if (
                date == start_date
                and date.modifier == Date.MOD_NONE
                and not (
                    event.get_type().is_death_fallback()
                    or event.get_type() == EventType.DEATH
                )
            ):
                return ""
            else:
                return (date - start_date).format(precision=age_precision)
        else:
            return ""

    def column_sort_age(self, event):
        """
        Returns a string version of number of days of age.
        """
        date = event.get_date_object()
        start_date = self.cached_start_date
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
        self.connect(self.dbstate.db, "person-update", self.update)

    def active_changed(self, handle):
        self.update()

    def update_has_data(self):
        active_handle = self.get_active("Person")
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

    def main(self):  # return false finishes
        active_handle = self.get_active("Person")

        self.db = CacheProxyDb(self.dbstate.db)
        self.model.clear()
        self.callman.unregister_all()
        if active_handle:
            self.display_person(active_handle)
        else:
            self.set_has_data(False)
        self.db = None

    def display_person(self, active_handle):
        """
        Display the events for the active person.
        """
        active_person = self.db.get_person_from_handle(active_handle)
        if active_person:
            self.cached_start_date = self.get_start_date()
            for event_ref in active_person.get_event_ref_list():
                self.add_event_ref(event_ref)
            for family_handle in active_person.get_family_handle_list():
                family = self.db.get_family_from_handle(family_handle)
                self.display_family(family, active_person)
        else:
            self.cached_start_date = None
        self.set_has_data(self.model.count > 0)

    def display_family(self, family, active_person):
        """
        Display the events for the given family.
        """
        spouse_handle = find_spouse(active_person, family)
        if spouse_handle:
            spouse = self.db.get_person_from_handle(spouse_handle)
        else:
            spouse = None
        if family:
            for event_ref in family.get_event_ref_list():
                self.add_event_ref(event_ref, spouse)

    def get_start_date(self):
        """
        Get the start date for a person, usually a birth date, or
        something close to birth.
        """
        active_handle = self.get_active("Person")
        active = self.db.get_person_from_handle(active_handle)
        event = get_birth_or_fallback(self.db, active)
        return event.get_date_object() if event else None


class FamilyEvents(Events):
    """
    Displays the events for a family.
    """

    def db_changed(self):
        self.connect(self.dbstate.db, "family-update", self.update)
        self.connect_signal("Family", self.update)

    def update_has_data(self):
        active_handle = self.get_active("Family")
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

    def main(self):  # return false finishes
        active_handle = self.get_active("Family")

        self.db = CacheProxyDb(self.dbstate.db)
        self.model.clear()
        self.callman.unregister_all()
        if active_handle:
            self.display_family(active_handle)
        else:
            self.set_has_data(False)
        self.db = None

    def display_family(self, active_handle):
        """
        Display the events for the active family.
        """
        active_family = self.db.get_family_from_handle(active_handle)
        self.cached_start_date = self.get_start_date()
        for event_ref in active_family.get_event_ref_list():
            self.add_event_ref(event_ref)
        self.set_has_data(self.model.count > 0)

    def get_start_date(self):
        """
        Get the start date for a family, usually a marriage date, or
        something close to marriage.
        """
        active_handle = self.get_active("Family")
        active = self.db.get_family_from_handle(active_handle)
        event = get_marriage_or_fallback(self.db, active)
        return event.get_date_object() if event else None

# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007-2009  Douglas S. Blank <doug.blank@gmail.com>
# Copyright (C) 2025-      Serge Noiraud <serge.noiraud@free.fr>
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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.

# ------------------------------------------------------------------------
#
# Gtk modules
#
# ------------------------------------------------------------------------
from gi.repository import Gtk

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.plug import Gramplet
from gramps.gui.plug.quick import run_quick_report_by_name
from gramps.gen.lib.date import Date, Today
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.utils.db import get_birth_or_fallback, get_death_or_fallback
from gramps.gen.lib import EventType

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# CalendarGramplet class
#
# ------------------------------------------------------------------------
class CalendarGramplet(Gramplet):
    """
    Gramplet showing a calendar of events.
    """

    def __init__(self, gui, nav_group=0):
        super().__init__(gui, nav_group)

    def show_on_calendar(self, date):
        date = date.to_calendar("gregorian")
        year = date.get_year()
        if year < 0:  # Gtk.Calendar only works for positive years
            date = Today()
            year = date.get_year()
        month = date.get_month()
        if month > 0 and month < 13:
            month -= 1
        else:
            month = 0
        self.gui.calendar.select_month(month, date.get_year())
        self.gui.calendar.select_day(date.get_day())

    def init(self):
        self.set_tooltip(_("Double-click a day for details"))
        self.gui.calendar = Gtk.Calendar()
        self.gui.calendar.connect("day-selected-double-click", self.double_click)
        self.gui.calendar.set_display_options(
            Gtk.CalendarDisplayOptions.SHOW_DAY_NAMES
            | Gtk.CalendarDisplayOptions.SHOW_HEADING
        )
        self.gui.get_container_widget().remove(self.gui.textview)
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox.pack_start(self.gui.calendar, False, False, 0)
        self.gui.get_container_widget().add(vbox)
        vbox.show_all()

    def double_click(self, obj):
        """
        Bring up events on this day.
        """
        year, month, day = self.gui.calendar.get_date()
        date = Date()
        date.set_yr_mon_day(year, month + 1, day)
        run_quick_report_by_name(self.gui.dbstate, self.gui.uistate, "onthisday", date)


class StandardCalendar(CalendarGramplet):
    """
    Displays the calendar for other usage.
    """

    def __init__(self, gui, nav_group=0):
        super().__init__(gui, nav_group)


class PersonBirthCalendar(CalendarGramplet):
    """
    Displays the calendar for the person’s birth
    """

    def __init__(self, gui, nav_group=0):
        super().__init__(gui, nav_group)
        self.connect_signal("Person", self.update)

    def db_changed(self):
        self.connect_signal("Person", self.update)
        self.connect(self.dbstate.db, "person-delete", self.update)
        self.connect(self.dbstate.db, "person-add", self.update)
        self.connect(self.dbstate.db, "person-update", self.update)

    def main(self):
        date = Today()
        active_handle = self.get_active("Person")
        if active_handle:
            active = self.dbstate.db.get_person_from_handle(active_handle)
            if active:
                bd_event = get_birth_or_fallback(self.dbstate.db, active)
                if bd_event:
                    date = bd_event.get_date_object()
        self.show_on_calendar(date)


class PersonDeathCalendar(CalendarGramplet):
    """
    Displays the calendar for the person’s death
    """

    def __init__(self, gui, nav_group=0):
        super().__init__(gui, nav_group)
        self.connect_signal("Person", self.update)

    def db_changed(self):
        self.connect_signal("Person", self.update)
        self.connect(self.dbstate.db, "person-delete", self.update)
        self.connect(self.dbstate.db, "person-add", self.update)
        self.connect(self.dbstate.db, "person-update", self.update)

    def main(self):
        date = Today()
        active_handle = self.get_active("Person")
        if active_handle:
            active = self.dbstate.db.get_person_from_handle(active_handle)
            if active:
                bd_event = get_death_or_fallback(self.dbstate.db, active)
                if bd_event:
                    date = bd_event.get_date_object()
        self.show_on_calendar(date)


class FamilyCalendar(CalendarGramplet):
    """
    Displays the calendar for a family.
    """

    def __init__(self, gui, nav_group=0):
        super().__init__(gui, nav_group)
        self.connect_signal("Family", self.update)

    def db_changed(self):
        self.connect_signal("Family", self.update)
        self.connect(self.dbstate.db, "family-delete", self.update)
        self.connect(self.dbstate.db, "family-add", self.update)
        self.connect(self.dbstate.db, "family-update", self.update)

    def main(self):
        date = Today()
        active_handle = self.get_active("Family")
        if active_handle:
            active = self.dbstate.db.get_family_from_handle(active_handle)
            if active:
                fam_evt_ref_list = active.get_event_ref_list()
                if fam_evt_ref_list:
                    for evt_ref in fam_evt_ref_list:
                        evt = self.dbstate.db.get_event_from_handle(evt_ref.ref)
                        if evt:
                            evt_type = evt.get_type()
                            if evt_type == EventType.MARRIAGE:
                                date = evt.get_date_object()
                                break
        self.show_on_calendar(date)


class EventCalendar(CalendarGramplet):
    """
    Displays the calendar for an event.
    """

    def __init__(self, gui, nav_group=0):
        super().__init__(gui, nav_group)
        self.connect_signal("Event", self.update)

    def db_changed(self):
        self.connect_signal("Event", self.update)
        self.connect(self.dbstate.db, "event-delete", self.update)
        self.connect(self.dbstate.db, "event-add", self.update)
        self.connect(self.dbstate.db, "event-update", self.update)

    def main(self):
        date = Today()
        active_handle = self.get_active("Event")
        if active_handle:
            event = self.dbstate.db.get_event_from_handle(active_handle)
            if event:
                date = event.get_date_object()
        self.show_on_calendar(date)

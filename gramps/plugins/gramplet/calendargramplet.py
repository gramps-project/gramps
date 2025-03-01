# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007-2009  Douglas S. Blank <doug.blank@gmail.com>
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
from gramps.gen.utils.db import get_birth_or_fallback
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

    def __init__(self, classname, gui, nav_group=0):
        self.__classname = classname  # must be set before calling super().__init__
        super().__init__(gui, nav_group)

    def db_changed(self):
        self.main()

    def main(self):
        active_handle = self.get_active(self.__classname)
        date = Today()
        if active_handle:
            if self.__classname == "Event":
                active = self.dbstate.db.get_event_from_handle(active_handle)
                if active:
                    date = active.get_date_object()
            elif self.__classname == "Person":
                active = self.dbstate.db.get_person_from_handle(active_handle)
                if active:
                    bd_event = get_birth_or_fallback(self.dbstate.db, active)
                    if bd_event:
                        date = bd_event.get_date_object()
            elif self.__classname == "Family":
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
            year = date.get_year()
            if year < 1:
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

    def active_changed(self, handle):
        self.main()


class StandardCalendar(CalendarGramplet):
    """
    Displays the calendar for other usage.
    """

    def __init__(self, gui, nav_group=0):
        super().__init__("Other", gui, nav_group)


class PersonCalendar(CalendarGramplet):
    """
    Displays the calendar for a person.
    """

    def __init__(self, gui, nav_group=0):
        super().__init__("Person", gui, nav_group)
        self.connect_signal("Person", self.update)


class FamilyCalendar(CalendarGramplet):
    """
    Displays the calendar for a family.
    """

    def __init__(self, gui, nav_group=0):
        super().__init__("Family", gui, nav_group)
        self.connect_signal("Family", self.update)


class EventCalendar(CalendarGramplet):
    """
    Displays the calendar for an event.
    """

    def __init__(self, gui, nav_group=0):
        super().__init__("Event", gui, nav_group)
        self.connect_signal("Event", self.update)

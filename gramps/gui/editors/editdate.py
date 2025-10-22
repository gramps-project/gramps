#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2006  Donald N. Allingham
# Copyright (C) 2009       Douglas S. Blank
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
#

"""
Date editing module for Gramps.

The EditDate provides visual feedback to the user to indicate if
the associated GtkEntry box contains a valid date.
Red means that the date is not valid, and will be viewed as a text string
instead of a date.

The DateEditor provides a dialog in which the date can be
unambiguously built using UI controls such as menus and spin buttons.
"""

# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------


# -------------------------------------------------------------------------
#
# set up logging
#
# -------------------------------------------------------------------------
import logging

# -------------------------------------------------------------------------
#
# GNOME modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk

# -------------------------------------------------------------------------
#
# gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.config import config
from gramps.gen.lib.date import Date, DateError, calendar_has_fixed_newyear, Today
from gramps.gen.datehandler import displayer
from gramps.gen.const import URL_MANUAL_SECT1
from ..display import display_help
from ..managedwindow import ManagedWindow
from ..glade import Glade

LOG = logging.getLogger(".EditDate")
_ = glocale.translation.sgettext
# -------------------------------------------------------------------------
#
# Constants
#
# -------------------------------------------------------------------------
MOD_TEXT = (
    (Date.MOD_NONE, _("Regular")),
    (Date.MOD_BEFORE, _("Before")),
    (Date.MOD_AFTER, _("After")),
    (Date.MOD_ABOUT, _("About")),
    (Date.MOD_RANGE, _("Range")),
    (Date.MOD_FROM, _("From")),
    (Date.MOD_TO, _("To")),
    (Date.MOD_SPAN, _("Span")),
    (Date.MOD_TEXTONLY, _("Text only")),
)

QUAL_TEXT = (
    (Date.QUAL_NONE, _("Regular")),
    (Date.QUAL_ESTIMATED, _("Estimated")),
    (Date.QUAL_CALCULATED, _("Calculated")),
)

CAL_TO_MONTHS_NAMES = {
    Date.CAL_GREGORIAN: displayer.short_months,
    Date.CAL_JULIAN: displayer.short_months,
    Date.CAL_HEBREW: displayer.hebrew,
    Date.CAL_FRENCH: displayer.french,
    Date.CAL_PERSIAN: displayer.persian,
    Date.CAL_ISLAMIC: displayer.islamic,
    Date.CAL_SWEDISH: displayer.swedish,
}

WIKI_HELP_PAGE = URL_MANUAL_SECT1
WIKI_HELP_SEC = _("Editing_dates", "manual")


# -------------------------------------------------------------------------
#
# EditDate
#
# -------------------------------------------------------------------------
class EditDate(ManagedWindow):
    """
    Dialog allowing to build the date precisely, to correct possible
    limitations of parsing and/or underlying structure of :class:`.Date`.
    """

    def __init__(self, date, uistate, track):
        """
        Initiate and display the dialog.
        """
        ManagedWindow.__init__(self, uistate, track, self)

        # Create self.date as a copy of the given Date object.
        self.date = Date(date)

        self.top = Glade()

        self.set_window(
            self.top.toplevel, self.top.get_object("title"), _("Date selection")
        )
        self.setup_configs("interface.editdate", 620, 320)

        self.statusbar = self.top.get_object("statusbar")
        self.ok_button = self.top.get_object("ok_button")
        self.calendar_box = self.top.get_object("calendar_box")
        for name in Date.ui_calendar_names:
            self.calendar_box.get_model().append([name])

        self.new_year = self.top.get_object("newyear")
        self.new_year.set_text(self.date.newyear_to_str())

        cal = self.date.get_calendar()
        self.calendar_box.set_active(cal)
        self.align_newyear_ui_with_calendar(cal)
        self.calendar_box.connect("changed", self.switch_calendar)

        self.quality_box = self.top.get_object("quality_box")
        for item_number, item in enumerate(QUAL_TEXT):
            self.quality_box.append_text(item[1])
            if self.date.get_quality() == item[0]:
                self.quality_box.set_active(item_number)

        self.type_box = self.top.get_object("type_box")
        for item_number, item in enumerate(MOD_TEXT):
            self.type_box.append_text(item[1])
            if self.date.get_modifier() == item[0]:
                self.type_box.set_active(item_number)
        self.type_box.connect("changed", self.switch_type)

        self.start_month_box = self.top.get_object("start_month_box")
        self.stop_month_box = self.top.get_object("stop_month_box")
        month_names = CAL_TO_MONTHS_NAMES[self.date.get_calendar()]
        for name in month_names:
            self.start_month_box.append_text(name)
            self.stop_month_box.append_text(name)
        self.start_month_box.set_active(self.date.get_month())
        self.stop_month_box.set_active(self.date.get_stop_month())

        self.start_day = self.top.get_object("start_day")
        self.start_day.set_value(self.date.get_day())
        self.start_year = self.top.get_object("start_year")
        self.start_year.set_value(self.date.get_year())

        self.stop_day = self.top.get_object("stop_day")
        self.stop_day.set_value(self.date.get_stop_day())
        self.stop_year = self.top.get_object("stop_year")
        self.stop_year.set_value(self.date.get_stop_year())

        self.dual_dated = self.top.get_object("dualdated")

        # The following is not described in the glade file.
        # glade is not for Gtk4.
        table48 = self.top.get_object("table48")
        self.first_date = Gtk.Calendar()
        self.first_date.set_display_options(
            Gtk.CalendarDisplayOptions.SHOW_DAY_NAMES
            | Gtk.CalendarDisplayOptions.SHOW_HEADING
        )
        self.first_date.connect("day-selected", self.date_change_in_calendar, "start")
        self.second_date = Gtk.Calendar()
        self.second_date.set_display_options(
            Gtk.CalendarDisplayOptions.SHOW_DAY_NAMES
            | Gtk.CalendarDisplayOptions.SHOW_HEADING
        )
        self.second_date.connect("day-selected", self.date_change_in_calendar, "stop")
        table48.attach(self.first_date, 0, 6, 3, 6)
        table48.attach(self.second_date, 3, 6, 5, 6)
        self.ofdate = self.first_date.get_date()
        self.osdate = self.second_date.get_date()
        self.showcal = True

        # Disable second date controls if not compound date
        if not self.date.is_compound():
            self.stop_day.set_sensitive(0)
            self.stop_month_box.set_sensitive(0)
            self.stop_year.set_sensitive(0)
            self.second_date.set_sensitive(0)

        # Disable the rest of controls if a text-only date
        if self.date.get_modifier() == Date.MOD_TEXTONLY:
            self.start_day.set_sensitive(0)
            self.start_month_box.set_sensitive(0)
            self.start_year.set_sensitive(0)
            self.calendar_box.set_sensitive(0)
            self.quality_box.set_sensitive(0)
            self.dual_dated.set_sensitive(0)
            self.new_year.set_sensitive(0)
            self.first_date.set_sensitive(0)
            self.second_date.set_sensitive(0)

        self.text_entry = self.top.get_object("date_text_entry")
        self.text_entry.set_text(self.date.get_text())

        if self.date.get_slash():
            self.dual_dated.set_active(1)
            self.calendar_box.set_sensitive(0)
            self.calendar_box.set_active(Date.CAL_JULIAN)
        self.dual_dated.connect("toggled", self.switch_dual_dated)

        # Use the calendar from user preferences for new dates only.
        if self.date.is_empty():
            cal = config.get("preferences.calendar-format-input")
            self.calendar_box.set_active(cal)

        # The dialog is modal -- since dates don't have names, we don't
        # want to have several open dialogs, since then the user will
        # loose track of which is which. Much like opening files.

        self.validated_date = self.return_date = None

        for obj in self.top.get_objects():
            if obj != self.ok_button:
                for signal in ["changed", "value-changed"]:
                    try:
                        obj.connect_after(signal, self.revalidate)
                    except TypeError:
                        # some of them don't support the signal, ignore them...
                        pass
        self.revalidate()
        self.show()

        while True:
            response = self.window.run()
            LOG.debug("response: {0}".format(response))
            if response == Gtk.ResponseType.HELP:
                display_help(webpage=WIKI_HELP_PAGE, section=WIKI_HELP_SEC)
            elif response == Gtk.ResponseType.DELETE_EVENT:
                break
            else:
                if response == Gtk.ResponseType.OK:
                    # if the user pressed OK/enter while inside an edit field,
                    # e.g., the year,
                    # build_date_from_ui won't pick up the new text in the
                    # run of revalidate that allowed the OK!
                    if not self.revalidate():
                        continue
                    self.return_date = Date()
                    self.return_date.copy(self.validated_date)
                self.close()
                break

    def show_on_calendar(self, calendar, date):
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
        if not self.showcal:
            # not set a date for any calendar other than the Gregorian calendar
            # only true after calendar change
            return  # only true after calendar change
        calendar.select_month(month, date.get_year())
        calendar.select_day(date.get_day())

    def date_change_in_calendar(self, calendar, date):
        if self.calendar_box.get_active() != Date.CAL_GREGORIAN:
            return
        current = calendar.get_date()
        if date == "start" and current == self.ofdate:
            return False
        elif current == self.osdate:
            return False
        newdate = Date(current.year, current.month + 1, current.day)
        newdate = newdate.to_calendar(self.calendar_box.get_active())
        if date == "start":
            if self.ofdate.day != current.day:
                self.start_day.set_value(newdate.get_day())
            if self.ofdate.month != current.month:
                self.start_month_box.set_active(newdate.get_month())
            if self.ofdate.year != current.year:
                self.start_year.set_value(newdate.get_year())
            self.ofdate = current
        else:
            if self.osdate.day != current.day:
                self.stop_day.set_value(newdate.get_day())
            if self.osdate.month != current.month:
                self.stop_month_box.set_active(newdate.get_month())
            if self.osdate.year != current.year:
                self.stop_year.set_value(newdate.get_year())
            self.osdate = current

    def revalidate(self, obj=None):
        """
        If anything changed, revalidate the date and
        enable/disable the "OK" button based on the result.
        """
        (
            the_quality,
            the_modifier,
            the_calendar,
            the_value,
            the_text,
            the_newyear,
        ) = self.build_date_from_ui()
        LOG.debug("revalidate: {0} changed, value: {1}".format(obj, the_value))
        dat = Date(self.date)
        if not self.ok_button.get_sensitive():
            self.statusbar.pop(1)
        try:
            dat.set(
                quality=the_quality,
                modifier=the_modifier,
                calendar=the_calendar,
                value=the_value,
                text=the_text,
                newyear=the_newyear,
            )
            # didn't throw yet?
            self.validated_date = dat
            LOG.debug("validated_date set to: {0}".format(dat.__dict__))
            self.ok_button.set_sensitive(1)
            self.calendar_box.set_sensitive(1)
            return True
        except DateError as dummy_err:
            self.ok_button.set_sensitive(0)
            self.calendar_box.set_sensitive(0)
            curmode = MOD_TEXT[self.type_box.get_active()][1]
            txtmode = MOD_TEXT[-1][1]
            self.statusbar.push(
                1,
                _(
                    "Correct the date or switch from `{cur_mode}'" " to `{text_mode}'"
                ).format(cur_mode=curmode, text_mode=txtmode),
            )
            return False

    def build_menu_names(self, obj):
        """
        Define the menu entry for the :class:`.ManagedWindow`
        """
        return (_("Date selection"), None)

    def build_date_from_ui(self):
        """
        Collect information from the UI controls and return
        5-tuple of (quality,modifier,calendar,value,text)
        """
        # It is important to not set date based on these controls.
        # For example, changing the caledar makes the date inconsistent
        # until the callback of the calendar menu is finished.
        # We need to be able to use this function from that callback,
        # so here we just report on the state of all widgets, without
        # actually modifying the date yet.
        modifier = MOD_TEXT[self.type_box.get_active()][0]
        text = self.text_entry.get_text()

        if modifier == Date.MOD_TEXTONLY:
            return (
                Date.QUAL_NONE,
                Date.MOD_TEXTONLY,
                Date.CAL_GREGORIAN,
                Date.EMPTY,
                text,
                Date.NEWYEAR_JAN1,
            )

        quality = QUAL_TEXT[self.quality_box.get_active()][0]

        new_cal = self.calendar_box.get_active()

        if modifier in (Date.MOD_RANGE, Date.MOD_SPAN):
            value = (
                self.start_day.get_value_as_int(),
                self.start_month_box.get_active(),
                self.start_year.get_value_as_int(),
                self.dual_dated.get_active(),
                self.stop_day.get_value_as_int(),
                self.stop_month_box.get_active(),
                self.stop_year.get_value_as_int(),
                self.dual_dated.get_active(),
            )
            dat1 = Date()
            dat1.set_yr_mon_day(
                self.start_year.get_value_as_int(),
                self.start_month_box.get_active(),
                self.start_day.get_value_as_int(),
            )
            dat1.set_calendar(new_cal)
            self.show_on_calendar(self.first_date, dat1)
            dat2 = Date()
            dat2.set_yr_mon_day(
                self.stop_year.get_value_as_int(),
                self.stop_month_box.get_active(),
                self.stop_day.get_value_as_int(),
            )
            dat1.set_calendar(new_cal)
            self.show_on_calendar(self.second_date, dat2)
        else:
            value = (
                self.start_day.get_value_as_int(),
                self.start_month_box.get_active(),
                self.start_year.get_value_as_int(),
                self.dual_dated.get_active(),
            )
            dat1 = Date()
            dat1.set_calendar(self.calendar_box.get_active())
            dat1.set_yr_mon_day(
                self.start_year.get_value_as_int(),
                self.start_month_box.get_active(),
                self.start_day.get_value_as_int(),
            )
            dat1.set_calendar(new_cal)
            self.show_on_calendar(self.first_date, dat1)
            self.show_on_calendar(self.second_date, dat1)

        if new_cal != Date.CAL_GREGORIAN:
            self.first_date.set_sensitive(0)
            self.second_date.set_sensitive(0)

        calendar = self.calendar_box.get_active()
        newyear = Date.newyear_to_code(self.new_year.get_text())
        return (quality, modifier, calendar, value, text, newyear)

    def switch_type(self, obj):
        """
        Disable/enable various date controls depending on the date
        type selected via the menu.
        """

        the_modifier = MOD_TEXT[self.type_box.get_active()][0]

        # Disable/enable second date controls based on whether
        # the type allows compound dates
        if the_modifier in (Date.MOD_RANGE, Date.MOD_SPAN):
            stop_date_sensitivity = 1
        else:
            stop_date_sensitivity = 0
        self.stop_day.set_sensitive(stop_date_sensitivity)
        self.stop_month_box.set_sensitive(stop_date_sensitivity)
        self.stop_year.set_sensitive(stop_date_sensitivity)
        self.second_date.set_sensitive(stop_date_sensitivity)

        # Disable/enable the rest of the controls if the type is text-only.
        date_sensitivity = not the_modifier == Date.MOD_TEXTONLY
        self.start_day.set_sensitive(date_sensitivity)
        self.start_month_box.set_sensitive(date_sensitivity)
        self.start_year.set_sensitive(date_sensitivity)
        self.calendar_box.set_sensitive(date_sensitivity)
        self.quality_box.set_sensitive(date_sensitivity)
        self.dual_dated.set_sensitive(date_sensitivity)
        self.new_year.set_sensitive(date_sensitivity)

    def switch_dual_dated(self, obj):
        """
        Changed whether this is a dual dated year, or not.
        Dual dated years are represented in the Julian calendar
        so that the day/months don't changed in the Text representation.
        """
        if self.dual_dated.get_active():
            self.calendar_box.set_active(Date.CAL_JULIAN)
            self.calendar_box.set_sensitive(0)
        else:
            self.calendar_box.set_sensitive(1)

    def align_newyear_ui_with_calendar(self, cal):
        if calendar_has_fixed_newyear(cal):
            LOG.debug("new year disabled for cal {0}".format(cal))
            self.new_year.set_sensitive(0)
            self.new_year.set_text("")
        else:
            LOG.debug("new year enabled for cal {0}".format(cal))
            self.new_year.set_sensitive(1)

    def switch_calendar(self, obj):
        """
        Change month names and convert the date based on the calendar
        selected via the menu.
        """

        old_cal = self.date.get_calendar()
        new_cal = self.calendar_box.get_active()
        LOG.debug(
            ">>>switch_calendar: {0} changed, {1} -> {2}".format(obj, old_cal, new_cal)
        )

        if new_cal == Date.CAL_GREGORIAN:
            self.first_date.set_sensitive(1)
            self.second_date.set_sensitive(1)
            self.showcal = True
        else:
            self.showcal = False
        self.align_newyear_ui_with_calendar(new_cal)

        (
            the_quality,
            the_modifier,
            dummy_the_calendar,
            the_value,
            the_text,
            the_newyear,
        ) = self.build_date_from_ui()
        try:
            self.date.set(
                quality=the_quality,
                modifier=the_modifier,
                calendar=old_cal,
                value=the_value,
                text=the_text,
                newyear=the_newyear,
            )
        except DateError:
            pass
        else:
            if not self.date.is_empty():
                self.date.convert_calendar(new_cal)

        self.start_month_box.get_model().clear()
        self.stop_month_box.get_model().clear()
        month_names = CAL_TO_MONTHS_NAMES[new_cal]
        for name in month_names:
            self.start_month_box.append_text(name)
            self.stop_month_box.append_text(name)

        self.start_day.set_value(self.date.get_day())
        self.start_month_box.set_active(self.date.get_month())
        self.start_year.set_value(self.date.get_year())
        self.stop_day.set_value(self.date.get_stop_day())
        self.stop_month_box.set_active(self.date.get_stop_month())
        self.stop_year.set_value(self.date.get_stop_year())
        LOG.debug(
            "<<<switch_calendar: {0} changed, {1} -> {2}".format(obj, old_cal, new_cal)
        )

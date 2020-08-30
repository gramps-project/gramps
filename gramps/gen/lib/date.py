#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2009-2013  Douglas S. Blank
# Copyright (C) 2013       Paul Franklin
# Copyright (C) 2013-2014  Vassilii Khachaturov
# Copyright (C) 2017       Nick Hall
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

"""Support for dates."""

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging

#-------------------------------------------------------------------------
#
# Gnome/GTK modules
#
#-------------------------------------------------------------------------


#------------------------------------------------------------------------
#
# Gramps modules
#
#------------------------------------------------------------------------
from .gcalendar import (gregorian_sdn, julian_sdn, hebrew_sdn,
                        french_sdn, persian_sdn, islamic_sdn, swedish_sdn,
                        gregorian_ymd, julian_ymd, hebrew_ymd,
                        french_ymd, persian_ymd, islamic_ymd,
                        swedish_ymd)
from ..config import config
from ..errors import DateError
from ..const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext

LOG = logging.getLogger(".Date")

class Span:
    """
    Span is used to represent the difference between two dates for three
    main purposes: sorting, ranking, and describing.

    sort = (base day count, offset)
    minmax = (min days, max days)

    """
    BEFORE = config.get('behavior.date-before-range')
    AFTER = config.get('behavior.date-after-range')
    ABOUT = config.get('behavior.date-about-range')
    ALIVE = config.get('behavior.max-age-prob-alive')
    def __init__(self, date1, date2):
        self.valid = (date1.sortval != 0 and date2.sortval != 0)
        self.date1 = date1
        self.date2 = date2
        self.sort = (-9999, -9999)
        self.minmax = (9999, -9999)
        self.precision = 2
        self.negative = False
        if self.valid:
            if self.date1.calendar != Date.CAL_GREGORIAN:
                self.date1 = self.date1.to_calendar("gregorian")
            if self.date2.calendar != Date.CAL_GREGORIAN:
                self.date2 = self.date2.to_calendar("gregorian")
            if self.date1.sortval < self.date2.sortval:
                self.date1 = date2
                self.date2 = date1
                self.negative = True
            if self.date1.get_modifier() == Date.MOD_NONE:
                if   self.date2.get_modifier() == Date.MOD_NONE:
                    val = self.date1.sortval - self.date2.sortval
                    self.sort = (val, 0)
                    self.minmax = (val, val)
                elif self.date2.get_modifier() == Date.MOD_BEFORE:
                    val = self.date1.sortval - self.date2.sortval
                    self.sort = (val, -Span.BEFORE)
                    self.minmax = (val - Span.BEFORE, val)
                elif self.date2.get_modifier() == Date.MOD_AFTER:
                    val = self.date1.sortval - self.date2.sortval
                    self.sort = (val, Span.AFTER)
                    self.minmax = (val, val + Span.AFTER)
                elif self.date2.get_modifier() == Date.MOD_ABOUT:
                    val = self.date1.sortval - self.date2.sortval
                    self.sort = (val, -Span.ABOUT)
                    self.minmax = (val - Span.ABOUT, val + Span.ABOUT)
                elif self.date2.is_compound():
                    start, stop = self.date2.get_start_stop_range()
                    start = Date(*start)
                    stop = Date(*stop)
                    val1 = self.date1.sortval - stop.sortval  # min
                    val2 = self.date1.sortval - start.sortval # max
                    self.sort = (val1, val2 - val1)
                    self.minmax = (val1, val2)
            elif self.date1.get_modifier() == Date.MOD_BEFORE:
                if   self.date2.get_modifier() == Date.MOD_NONE:
                    val = self.date1.sortval - self.date2.sortval
                    self.sort = (val, 0)
                    self.minmax = (0, val)
                elif self.date2.get_modifier() == Date.MOD_BEFORE:
                    val = self.date1.sortval - self.date2.sortval
                    self.sort = (val, -Span.BEFORE)
                    self.minmax = (val, val + Span.BEFORE)
                elif self.date2.get_modifier() == Date.MOD_AFTER:
                    val = self.date1.sortval - self.date2.sortval
                    self.sort = (val, -Span.AFTER)
                    self.minmax = (0, val)
                elif self.date2.get_modifier() == Date.MOD_ABOUT:
                    val = self.date1.sortval - self.date2.sortval
                    self.sort = (val, -Span.ABOUT)
                    self.minmax = (val - Span.ABOUT, val + Span.ABOUT)
                elif self.date2.is_compound():
                    val = self.date1.sortval - self.date2.sortval
                    self.sort = (val, -Span.ABOUT)
                    self.minmax = (val - Span.ABOUT, val + Span.ABOUT)
            elif self.date1.get_modifier() == Date.MOD_AFTER:
                if self.date2.get_modifier() == Date.MOD_NONE:
                    val = self.date1.sortval - self.date2.sortval
                    self.sort = (val, Span.AFTER)
                    self.minmax = (val, val + Span.AFTER)
                elif self.date2.get_modifier() == Date.MOD_BEFORE:
                    val = self.date1.sortval - self.date2.sortval
                    self.sort = (val, Span.AFTER)
                    self.minmax = (val - Span.BEFORE, val + Span.AFTER)
                elif self.date2.get_modifier() == Date.MOD_AFTER:
                    val = self.date1.sortval - self.date2.sortval
                    self.sort = (val, Span.AFTER)
                    self.minmax = (val, val + Span.AFTER)
                elif self.date2.get_modifier() == Date.MOD_ABOUT:
                    val = self.date1.sortval - self.date2.sortval
                    self.sort = (val, -Span.ABOUT)
                    self.minmax = (val - Span.ABOUT, val + Span.AFTER)
                elif self.date2.is_compound():
                    val = self.date1.sortval - self.date2.sortval
                    self.sort = (val, -Span.ABOUT)
                    self.minmax = (val - Span.ABOUT, val + Span.ABOUT)
            elif self.date1.get_modifier() == Date.MOD_ABOUT:
                if self.date2.get_modifier() == Date.MOD_NONE:
                    val = self.date1.sortval - self.date2.sortval
                    self.sort = (val, -Span.ABOUT)
                    self.minmax = (val - Span.ABOUT, val + Span.ABOUT)
                elif self.date2.get_modifier() == Date.MOD_BEFORE:
                    val = self.date1.sortval - self.date2.sortval
                    self.sort = (val, -Span.BEFORE)
                    self.minmax = (val - Span.BEFORE, val + Span.ABOUT)
                elif self.date2.get_modifier() == Date.MOD_AFTER:
                    val = self.date1.sortval - self.date2.sortval
                    self.sort = (val, Span.AFTER)
                    self.minmax = (val - Span.ABOUT, val + Span.ABOUT)
                elif self.date2.get_modifier() == Date.MOD_ABOUT:
                    val = self.date1.sortval - self.date2.sortval
                    self.sort = (val, -Span.ABOUT)
                    self.minmax = (val - Span.ABOUT, val + Span.ABOUT)
                elif self.date2.is_compound():
                    val = self.date1.sortval - self.date2.sortval
                    self.sort = (val, -Span.ABOUT)
                    self.minmax = (val - Span.ABOUT, val + Span.ABOUT)
            elif self.date1.is_compound():
                if self.date2.get_modifier() == Date.MOD_NONE:
                    start, stop = self.date1.get_start_stop_range()
                    start = Date(*start)
                    stop = Date(*stop)
                    val1 = start.sortval - self.date2.sortval # min
                    val2 = stop.sortval - self.date2.sortval # max
                    self.sort = (val1, val2 - val1)
                    self.minmax = (val1, val2)
                elif self.date2.get_modifier() == Date.MOD_BEFORE:
                    val = self.date1.sortval - self.date2.sortval
                    self.sort = (val, Span.BEFORE)
                    self.minmax = (val - Span.BEFORE, val + Span.BEFORE)
                elif self.date2.get_modifier() == Date.MOD_AFTER:
                    val = self.date1.sortval - self.date2.sortval
                    self.sort = (val, -Span.AFTER)
                    self.minmax = (val - Span.AFTER, val + Span.AFTER)
                elif self.date2.get_modifier() == Date.MOD_ABOUT:
                    val = self.date1.sortval - self.date2.sortval
                    self.sort = (val, -Span.ABOUT)
                    self.minmax = (val - Span.ABOUT, val + Span.ABOUT)
                elif self.date2.is_compound():
                    start1, stop1 = self.date1.get_start_stop_range()
                    start2, stop2 = self.date2.get_start_stop_range()
                    start1 = Date(*start1)
                    start2 = Date(*start2)
                    stop1 = Date(*stop1)
                    stop2 = Date(*stop2)
                    val1 = start1.sortval - stop2.sortval  # min
                    val2 = stop1.sortval - start2.sortval # max
                    self.sort = (val1, val2 - val1)
                    self.minmax = (val1, val2)

    def is_valid(self):
        return self.valid

    def tuple(self):
        return self._diff(self.date1, self.date2)

    def __getitem__(self, pos):
        # Depricated!
        return self._diff(self.date1, self.date2)[pos]

    def __int__(self):
        """
        Returns the number of days of span.
        """
        if self.negative:
            return -(self.sort[0] + self.sort[1])
        else:
            return self.sort[0] + self.sort[1]

##    def __cmp__(self, other):
##        """
##        DEPRECATED - not available in python 3
##
##        Comparing two Spans for SORTING purposes.
##        Use cmp(abs(int(span1)), abs(int(span2))) for comparing
##        actual spans of times, as spans have directionality
##        as indicated by negative values.
##        """
##        raise NotImplementedError
##        if other is None:
##            return cmp(int(self), -9999)
##        else:
##            return cmp(int(self), int(other))

    def as_age(self):
        """
        Get Span as an age (will not return more than Span.ALIVE).
        """
        return self.get_repr(as_age=True)

    def as_time(self):
        """
        Get Span as a time (can be greater than Span.ALIVE).
        """
        return self.get_repr(as_age=False)

    def __repr__(self):
        """
        Get the Span as an age. Use Span.as_time() to get as a textual
        description of time greater than Span.ALIVE.
        """
        return self.get_repr(as_age=True)

    def get_repr(self, as_age=False, dlocale=glocale):
        """
        Get the representation as a time or age.

        If dlocale is passed in (a :class:`.GrampsLocale`) then
        the translated value will be returned instead.

        :param dlocale: allow deferred translation of strings
        :type dlocale: a :class:`.GrampsLocale` instance
        """
        # trans_text is a defined keyword (see po/update_po.py, po/genpot.sh)
        trans_text = dlocale.translation.sgettext
        _repr = trans_text("unknown")
        # FIXME all this concatenation will fail for RTL languages -- really??
        if self.valid:
            fdate12 = self._format(self._diff(self.date1, self.date2), dlocale)
            fdate12p1 = self._format(self._diff(self.date1, self.date2),
                                     dlocale).format(precision=1)
            if as_age and self._diff(self.date1, self.date2)[0] > Span.ALIVE:
                _repr = trans_text("greater than %s years") % Span.ALIVE
            elif self.date1.get_modifier() == Date.MOD_NONE:
                if self.date2.get_modifier() == Date.MOD_NONE:
                    _repr = fdate12
                elif self.date2.get_modifier() == Date.MOD_BEFORE:
                    _repr = trans_text("more than") + " " + fdate12
                elif self.date2.get_modifier() == Date.MOD_AFTER:
                    _repr = trans_text("less than") + " " + fdate12
                elif self.date2.get_modifier() == Date.MOD_ABOUT:
                    _repr = trans_text("about", "age") + " " + fdate12p1
                elif self.date2.is_compound():
                    start, stop = self.date2.get_start_stop_range()
                    start = Date(*start)
                    stop = Date(*stop)
                    _repr = (trans_text("between") + " " +
                             self._format(self._diff(self.date1, stop),
                                          dlocale) + " " +
                             trans_text("and") + " " +
                             self._format(self._diff(self.date1, start),
                                          dlocale))
            elif self.date1.get_modifier() == Date.MOD_BEFORE:
                if   self.date2.get_modifier() == Date.MOD_NONE:
                    _repr = trans_text("less than") + " " + fdate12
                elif self.date2.get_modifier() == Date.MOD_BEFORE:
                    _repr = self._format((-1, -1, -1))
                elif self.date2.get_modifier() == Date.MOD_AFTER:
                    _repr = trans_text("less than") + " " + fdate12
                elif self.date2.get_modifier() == Date.MOD_ABOUT:
                    _repr = trans_text("less than about") + " " + fdate12
                elif self.date2.is_compound():
                    _repr = trans_text("less than") + " " + fdate12
            elif self.date1.get_modifier() == Date.MOD_AFTER:
                if   self.date2.get_modifier() == Date.MOD_NONE:
                    _repr = trans_text("more than") + " " + fdate12
                elif self.date2.get_modifier() == Date.MOD_BEFORE:
                    _repr = trans_text("more than") + " " + fdate12
                elif self.date2.get_modifier() == Date.MOD_AFTER:
                    _repr = self._format((-1, -1, -1))
                elif self.date2.get_modifier() == Date.MOD_ABOUT:
                    _repr = trans_text("more than about") + " " + fdate12p1
                elif self.date2.is_compound():
                    _repr = trans_text("more than") + " " + fdate12
            elif self.date1.get_modifier() == Date.MOD_ABOUT:
                if   self.date2.get_modifier() == Date.MOD_NONE:
                    _repr = trans_text("about", "age") + " " + fdate12p1
                elif self.date2.get_modifier() == Date.MOD_BEFORE:
                    _repr = trans_text("more than about") + " " + fdate12p1
                elif self.date2.get_modifier() == Date.MOD_AFTER:
                    _repr = trans_text("less than about") + " " + fdate12p1
                elif self.date2.get_modifier() == Date.MOD_ABOUT:
                    _repr = trans_text("about", "age") + " " + fdate12p1
                elif self.date2.is_compound():
                    _repr = trans_text("about", "age") + " " + fdate12p1
            elif self.date1.is_compound():
                if   self.date2.get_modifier() == Date.MOD_NONE:
                    start, stop = self.date1.get_start_stop_range()
                    start = Date(*start)
                    stop = Date(*stop)
                    _repr = (trans_text("between") + " " +
                             self._format(self._diff(start, self.date2),
                                          dlocale) + " " +
                             trans_text("and") + " " +
                             self._format(self._diff(stop, self.date2),
                                          dlocale))
                elif self.date2.get_modifier() == Date.MOD_BEFORE:
                    _repr = trans_text("more than") + " " + fdate12
                elif self.date2.get_modifier() == Date.MOD_AFTER:
                    _repr = trans_text("less than") + " " + fdate12
                elif self.date2.get_modifier() == Date.MOD_ABOUT:
                    _repr = trans_text("about", "age") + " " + fdate12p1
                elif self.date2.is_compound():
                    start1, stop1 = self.date1.get_start_stop_range()
                    start2, stop2 = self.date2.get_start_stop_range()
                    start1 = Date(*start1)
                    start2 = Date(*start2)
                    stop1 = Date(*stop1)
                    stop2 = Date(*stop2)
                    _repr = (trans_text("between") + " " +
                             self._format(self._diff(start1, stop2), dlocale) +
                             " " + trans_text("and") + " " +
                             self._format(self._diff(stop1, start2), dlocale))
        if _repr.find('-') == -1: # we don't have a negative value to return.
            return _repr
        else:
            return '(' + _repr.replace('-', '') + ')'

    def __eq__(self, other):
        """
        For comparing of Spans. Uses the integer representation.
        """
        if other is None:
            return False
        return int(self) == int(other)

    def __lt__(self, other):
        """
        For less-than comparing of Spans. Uses the integer representation.
        """
        if other is None:
            return False
        return int(self) < int(other)

    def __gt__(self, other):
        """
        For greater-than comparing of Spans. Uses the integer representation.
        """
        if other is None:
            return True
        return int(self) > int(other)

    def format(self, precision=2, as_age=True, dlocale=glocale):
        """
        Force a string representation at a level of precision.

        ==  ====================================================
        1   only most significant level (year, month, day)
        2   only most two significant levels (year, month, day)
        3   at most three items of signifance (year, month, day)
        ==  ====================================================

        If dlocale is passed in (a :class:`.GrampsLocale`) then
        the translated value will be returned instead.

        :param dlocale: allow deferred translation of strings
        :type dlocale: a :class:`.GrampsLocale` instance
        """
        self.precision = precision
        return self.get_repr(as_age, dlocale=dlocale)

    def _format(self, diff_tuple, dlocale=glocale):
        """
        If dlocale is passed in (a :class:`.GrampsLocale`) then
        the translated value will be returned instead.

        :param dlocale: allow deferred translation of strings
        :type dlocale: a :class:`.GrampsLocale` instance
        """
        ngettext = dlocale.translation.ngettext # to see "nearby" comments
        # trans_text is a defined keyword (see po/update_po.py, po/genpot.sh)
        trans_text = dlocale.translation.sgettext
        if diff_tuple == (-1, -1, -1):
            return trans_text("unknown")
        retval = ""
        detail = 0
        if diff_tuple[0] != 0:
            # translators: leave all/any {...} untranslated
            retval += ngettext("{number_of} year", "{number_of} years",
                               diff_tuple[0]
                              ).format(number_of=diff_tuple[0])
            detail += 1
        if self.precision == detail:
            if diff_tuple[1] >= 6: # round up years
                # translators: leave all/any {...} untranslated
                retval = ngettext("{number_of} year", "{number_of} years",
                                  diff_tuple[0] + 1
                                 ).format(number_of=diff_tuple[0] + 1)
            return retval
        if diff_tuple[1] != 0:
            if retval != "":
                # translators: needed for Arabic, ignore otherwise
                retval += trans_text(", ")
            # translators: leave all/any {...} untranslated
            retval += ngettext("{number_of} month", "{number_of} months",
                               diff_tuple[1]
                              ).format(number_of=diff_tuple[1])
            detail += 1
        if self.precision == detail:
            return retval
        if diff_tuple[2] != 0:
            if retval != "":
                # translators: needed for Arabic, ignore otherwise
                retval += trans_text(", ")
            # translators: leave all/any {...} untranslated
            retval += ngettext("{number_of} day", "{number_of} days",
                               diff_tuple[2]
                              ).format(number_of=diff_tuple[2])
            detail += 1
        if self.precision == detail:
            return retval
        if retval == "":
            retval = trans_text("0 days")
        return retval

    def _diff(self, date1, date2):
        # We should make sure that Date2 + tuple -> Date1 and
        #                          Date1 - tuple -> Date2
        if date1.get_new_year() or date2.get_new_year():
            days = date1.sortval - date2.sortval
            years = days // 365
            months = (days - years * 365) // 30
            days = (days - years * 365) - months * 30
            if self.negative:
                return (-years, -months, -days)
            else:
                return (years, months, days)
        ymd1 = [i or 1 for i in date1.get_ymd()]
        ymd2 = [i or 1 for i in date2.get_ymd()]
        # ymd1 - ymd2 (1998, 12, 32) - (1982, 12, 15)
        # days:
        if ymd2[2] > ymd1[2]:
            # months:
            if ymd2[1] > ymd1[1]:
                ymd1[0] -= 1
                ymd1[1] += 12
            ymd1[1] -= 1
            ymd1[2] += 31
        # months:
        if ymd2[1] > ymd1[1]:
            ymd1[0] -= 1  # from years
            ymd1[1] += 12 # to months
        days = ymd1[2] - ymd2[2]
        months = ymd1[1] - ymd2[1]
        years = ymd1[0] - ymd2[0]
        if days > 31:
            months += days // 31
            days = days % 31
        if months > 12:
            years += months // 12
            months = months % 12
        # estimate: (years, months, days)
        # Check transitivity:
        if date1.is_full() and date2.is_full():
            edate = date1 - (years, months, days)
            if edate < date2: # too small, strictly less than
                diff = 0
                while edate << date2 and diff < 60:
                    diff += 1
                    edate = edate + (0, 0, diff)
                if diff == 60:
                    return (-1, -1, -1)
                if self.negative:
                    return (-years, -months, -(days - diff))
                else:
                    return (years, months, days - diff)
            elif edate > date2:
                diff = 0
                while edate >> date2 and diff > -60:
                    diff -= 1
                    edate -= (0, 0, abs(diff))
                if diff == -60:
                    return (-1, -1, -1)
                if self.negative:
                    return (-years, -months, -(days + diff))
                else:
                    return (years, months, days + diff)
        if self.negative:
            return (-years, -months, -days)
        else:
            return (years, months, days)

#-------------------------------------------------------------------------
#
# Date class
#
#-------------------------------------------------------------------------
class Date:
    """
    The core date handling class for Gramps.

    Supports partial dates, compound dates and alternate calendars.
    """
    MOD_NONE = 0  # CODE
    MOD_BEFORE = 1
    MOD_AFTER = 2
    MOD_ABOUT = 3
    MOD_RANGE = 4
    MOD_SPAN = 5
    MOD_TEXTONLY = 6

    QUAL_NONE = 0 # BITWISE
    QUAL_ESTIMATED = 1
    QUAL_CALCULATED = 2
    #QUAL_INTERPRETED = 4 unused in source!!

    CAL_GREGORIAN = 0 # CODE
    CAL_JULIAN = 1
    CAL_HEBREW = 2
    CAL_FRENCH = 3
    CAL_PERSIAN = 4
    CAL_ISLAMIC = 5
    CAL_SWEDISH = 6
    CALENDARS = range(7)

    NEWYEAR_JAN1 = 0 # CODE
    NEWYEAR_MAR1 = 1
    NEWYEAR_MAR25 = 2
    NEWYEAR_SEP1 = 3

    EMPTY = (0, 0, 0, False)

    _POS_DAY = 0
    _POS_MON = 1
    _POS_YR = 2
    _POS_SL = 3
    _POS_RDAY = 4
    _POS_RMON = 5
    _POS_RYR = 6
    _POS_RSL = 7

    _calendar_convert = [
        gregorian_sdn,
        julian_sdn,
        hebrew_sdn,
        french_sdn,
        persian_sdn,
        islamic_sdn,
        swedish_sdn,
        ]

    _calendar_change = [
        gregorian_ymd,
        julian_ymd,
        hebrew_ymd,
        french_ymd,
        persian_ymd,
        islamic_ymd,
        swedish_ymd,
        ]

    calendar_names = ["Gregorian",
                      "Julian",
                      "Hebrew",
                      "French Republican",
                      "Persian",
                      "Islamic",
                      "Swedish"]


    ui_calendar_names = [_("Gregorian", "calendar"),
                         _("Julian", "calendar"),
                         _("Hebrew", "calendar"),
                         _("French Republican", "calendar"),
                         _("Persian", "calendar"),
                         _("Islamic", "calendar"),
                         _("Swedish", "calendar")]

    def __init__(self, *source):
        """
        Create a new Date instance.
        """
        #### setup None, Date, or numbers
        if len(source) == 0:
            source = None
        elif len(source) == 1:
            if isinstance(source[0], int):
                source = (source[0], 0, 0)
            else:
                source = source[0]
        elif len(source) == 2:
            source = (source[0], source[1], 0)
        elif len(source) == 3:
            pass # source is ok
        else:
            raise AttributeError("invalid args to Date: %s" % source)
        self.format = None
        #### ok, process either date or tuple
        if isinstance(source, tuple):
            self.calendar = Date.CAL_GREGORIAN
            self.modifier = Date.MOD_NONE
            self.quality = Date.QUAL_NONE
            self.dateval = Date.EMPTY
            self.text = ""
            self.sortval = 0
            self.newyear = 0
            self.set_yr_mon_day(*source)
        elif source:
            self.calendar = source.calendar
            self.modifier = source.modifier
            self.quality = source.quality
            self.dateval = source.dateval
            self.text = source.text
            self.sortval = source.sortval
            self.newyear = source.newyear
        else:
            self.calendar = Date.CAL_GREGORIAN
            self.modifier = Date.MOD_NONE
            self.quality = Date.QUAL_NONE
            self.dateval = Date.EMPTY
            self.text = ""
            self.sortval = 0
            self.newyear = Date.NEWYEAR_JAN1

    def serialize(self, no_text_date=False):
        """
        Convert to a series of tuples for data storage.
        """
        if no_text_date:
            text = ''
        else:
            text = self.text

        return (self.calendar, self.modifier, self.quality,
                self.dateval, text, self.sortval, self.newyear)

    def unserialize(self, data):
        """
        Load from the format created by serialize.
        """
        #FIXME: work around 3.1.0 error:
        #2792: Dates in sourcereferences in person_ref_list not upgraded
        #Added 2009/03/09
        if len(data) == 7:
            # This is correct:
            (self.calendar, self.modifier, self.quality,
             self.dateval, self.text, self.sortval, self.newyear) = data
        elif len(data) == 6:
            # This is necessary to fix 3.1.0 bug:
            (self.calendar, self.modifier, self.quality,
             self.dateval, self.text, self.sortval) = data
            self.newyear = 0
            # Remove all except if-part after 3.1.1
        else:
            raise DateError("Invalid date to unserialize")
        return self

    @classmethod
    def get_schema(cls):
        """
        Returns the JSON Schema for this class.

        :returns: Returns a dict containing the schema.
        :rtype: dict
        """
        return {
            "type": "object",
            "title": _("Date"),
            "properties": {
                "_class": {"enum": [cls.__name__]},
                "calendar": {"type": "integer",
                             "title": _("Calendar")},
                "modifier": {"type": "integer",
                             "title": _("Modifier")},
                "quality": {"type": "integer",
                            "title": _("Quality")},
                "dateval": {"type": "array",
                            "title": _("Values"),
                            "items": {"type": ["integer", "boolean"]}},
                "text": {"type": "string",
                         "title": _("Text")},
                "sortval": {"type": "integer",
                            "title": _("Sort value")},
                "newyear": {"type": "integer",
                            "title": _("New year begins")}
            }
        }

    def copy(self, source):
        """
        Copy all the attributes of the given Date instance to the present
        instance, without creating a new object.
        """
        self.calendar = source.calendar
        self.modifier = source.modifier
        self.quality = source.quality
        self.dateval = source.dateval
        self.text = source.text
        self.sortval = source.sortval
        self.newyear = source.newyear

##   PYTHON 3 no __cmp__
##    def __cmp__(self, other):
##        """
##        Compare two dates.
##
##        Comparison function. Allows the usage of equality tests.
##        This allows you do run statements like 'date1 <= date2'
##        """
##        if isinstance(other, Date):
##            return cmp(self.sortval, other.sortval)
##        else:
##            return -1

    # Can't use this (as is) as this breaks comparing dates to None
    #def __eq__(self, other):
    #    return self.sortval == other.sortval

    def __eq__(self, other):
        """
        Equality based on sort value, use is_equal/match instead if needed
        """
        if isinstance(other, Date):
            return self.sortval == other.sortval
        else:
            #indicate this is not supported
            return False

    def __ne__(self, other):
        """
        Equality based on sort value, use is_equal/match instead if needed
        """
        if isinstance(other, Date):
            return self.sortval != other.sortval
        else:
            #indicate this is not supported
            return True

    def __le__(self, other):
        """
        <= based on sort value, use match instead if needed
        So this is different from using < which uses match!
        """
        if isinstance(other, Date):
            return self.sortval <= other.sortval
        else:
            #indicate this is not supported
            return NotImplemented

    def __ge__(self, other):
        """
        >= based on sort value, use match instead if needed
        So this is different from using > which uses match!
        """
        if isinstance(other, Date):
            return self.sortval >= other.sortval
        else:
            #indicate this is not supported
            return NotImplemented

    def __add__(self, other):
        """
        Date arithmetic: Date() + years, or Date() + (years, [months, [days]]).
        """
        if isinstance(other, int):
            return self.copy_offset_ymd(other)
        elif isinstance(other, (tuple, list)):
            return self.copy_offset_ymd(*other)
        else:
            raise AttributeError("unknown date add type: %s " % type(other))

    def __radd__(self, other):
        """
        Add a number + Date() or (years, months, days) + Date().
        """
        return self + other

    def __sub__(self, other):
        """
        Date arithmetic: Date() - years, Date - (y,m,d), or Date() - Date().
        """
        if isinstance(other, int):                # Date - value -> Date
            return self.copy_offset_ymd(-other)
        elif isinstance(other, (tuple, list)):    # Date - (y, m, d) -> Date
            return self.copy_offset_ymd(*[-i for i in other])
        elif isinstance(other, type(self)):       # Date1 - Date2 -> tuple
            return Span(self, other)
        else:
            raise AttributeError("unknown date sub type: %s " % type(other))

    def __contains__(self, string):
        """
        For use with "x in Date" syntax.
        """
        return str(string) in self.text

    def __lshift__(self, other):
        """
        Comparison for strictly less than.
        """
        return self.match(other, comparison="<<")

    def __lt__(self, other):
        """
        Comparison for less than using match, use sortval instead if needed.
        """
        return self.match(other, comparison="<")

    def __rshift__(self, other):
        """
        Comparison for strictly greater than.
        """
        return self.match(other, comparison=">>")

    def __gt__(self, other):
        """
        Comparison for greater than using match, use sortval instead if needed.
        """
        return self.match(other, comparison=">")

    def is_equal(self, other):
        """
        Return 1 if the given Date instance is the same as the present
        instance IN ALL REGARDS.

        Needed, because the __cmp__ only looks at the sorting value, and
        ignores the modifiers/comments.
        """
        if self.modifier == other.modifier \
               and self.modifier == Date.MOD_TEXTONLY:
            value = self.text == other.text
        else:
            value = (self.calendar == other.calendar and
                     self.modifier == other.modifier and
                     self.quality == other.quality and
                     self.dateval == other.dateval)
        return value

    def get_start_stop_range(self):
        """
        Return the minimal start_date, and a maximal stop_date corresponding
        to this date, given in Gregorian calendar.

        Useful in doing range overlap comparisons between different dates.

        Note that we stay in (YR,MON,DAY)
        """

        def yr_mon_day(dateval):
            """
            Local function to swap order for easy comparisons, and correct
            year of slash date.

            Slash date is given as year1/year2, where year1 is Julian year,
            and year2=year1+1 the Gregorian year.

            Slash date is already taken care of.
            """
            return (dateval[Date._POS_YR], dateval[Date._POS_MON],
                    dateval[Date._POS_DAY])
        def date_offset(dateval, offset):
            """
            Local function to do date arithmetic: add the offset, return
            (year,month,day) in the Gregorian calendar.
            """
            new_date = Date()
            new_date.set_yr_mon_day(*dateval[:3])
            return new_date.offset(offset)

        datecopy = Date(self)
        #we do all calculation in Gregorian calendar
        datecopy.convert_calendar(Date.CAL_GREGORIAN)

        start = yr_mon_day(datecopy.get_start_date())
        stop = yr_mon_day(datecopy.get_stop_date())

        if stop == (0, 0, 0):
            stop = start

        stopmax = list(stop)
        if stopmax[0] == 0: # then use start_year, if one
            stopmax[0] = start[Date._POS_YR]
        if stopmax[1] == 0:
            stopmax[1] = 12
        if stopmax[2] == 0:
            stopmax[2] = 31
        startmin = list(start)
        if startmin[1] == 0:
            startmin[1] = 1
        if startmin[2] == 0:
            startmin[2] = 1
        # if BEFORE, AFTER, or ABOUT/EST, adjust:
        if self.modifier == Date.MOD_BEFORE:
            stopmax = date_offset(startmin, -1)
            fdiff = config.get('behavior.date-before-range')
            startmin = (stopmax[0] - fdiff, stopmax[1], stopmax[2])
        elif self.modifier == Date.MOD_AFTER:
            startmin = date_offset(stopmax, 1)
            fdiff = config.get('behavior.date-after-range')
            stopmax = (startmin[0] + fdiff, startmin[1], startmin[2])
        elif (self.modifier == Date.MOD_ABOUT or
              self.quality == Date.QUAL_ESTIMATED):
            fdiff = config.get('behavior.date-about-range')
            startmin = (startmin[0] - fdiff, startmin[1], startmin[2])
            stopmax = (stopmax[0] + fdiff, stopmax[1], stopmax[2])
        # return tuples not lists, for comparisons
        return (tuple(startmin), tuple(stopmax))

    def match_exact(self, other_date):
        """
        Perform an extact match between two dates. The dates are not treated
        as being person-centric. This is used to match date ranges in places.
        """
        if other_date.modifier == Date.MOD_NONE:
            return other_date.sortval == self.sortval
        elif other_date.modifier == Date.MOD_BEFORE:
            return other_date.sortval > self.sortval
        elif other_date.modifier == Date.MOD_AFTER:
            return other_date.sortval < self.sortval
        elif other_date.is_compound():
            start, stop = other_date.get_start_stop_range()
            start = Date(*start)
            stop = Date(*stop)
            return start.sortval <= self.sortval <= stop.sortval
        else:
            return False

    def match(self, other_date, comparison="="):
        """
        Compare two dates using sophisticated techniques looking for any match
        between two possible dates, date spans and qualities.

        The other comparisons for Date (is_equal() and __cmp() don't actually
        look for anything other than a straight match, or a simple comparison
        of the sortval.

        ==========  =======================================================
        Comparison  Returns
        ==========  =======================================================
        =,==        True if any part of other_date matches any part of self
        <           True if any part of other_date < any part of self
        <<          True if all parts of other_date < all parts of self
        >           True if any part of other_date > any part of self
        >>          True if all parts of other_date > all parts of self
        ==========  =======================================================
        """
        if (other_date.modifier == Date.MOD_TEXTONLY or
                self.modifier == Date.MOD_TEXTONLY):
            if comparison == "=":
                return self.text.upper().find(other_date.text.upper()) != -1
            elif comparison == "==":
                return self.text == other_date.text
            else:
                return False
        if self.sortval == 0 or other_date.sortval == 0:
            return False

        # Obtain minimal start and maximal stop in Gregorian calendar
        other_start, other_stop = other_date.get_start_stop_range()
        self_start, self_stop = self.get_start_stop_range()

        if comparison == "=":
            # If some overlap then match is True, otherwise False.
            return ((self_start <= other_start <= self_stop) or
                    (self_start <= other_stop <= self_stop) or
                    (other_start <= self_start <= other_stop) or
                    (other_start <= self_stop <= other_stop))
        elif comparison == "==":
            # If they match exactly on start and stop
            return ((self_start == other_start) and
                    (other_stop == other_stop))
        elif comparison == "<":
            # If any < any
            return self_start < other_stop
        elif comparison == "<=":
            # If any < any
            return self_start <= other_stop
        elif comparison == "<<":
            # If all < all
            return self_stop < other_start
        elif comparison == ">":
            # If any > any
            return self_stop > other_start
        elif comparison == ">=":
            # If any > any
            return self_stop >= other_start
        elif comparison == ">>":
            # If all > all
            return self_start > other_stop
        else:
            raise AttributeError("invalid match comparison operator: '%s'" %
                                 comparison)

    def __str__(self):
        """
        Produce a string representation of the Date object.

        If the date is not valid, the text representation is displayed. If
        the date is a range or a span, a string in the form of
        'YYYY-MM-DD - YYYY-MM-DD' is returned. Otherwise, a string in
        the form of 'YYYY-MM-DD' is returned.
        """
        if self.quality == Date.QUAL_ESTIMATED:
            qual = "est "
        elif self.quality == Date.QUAL_CALCULATED:
            qual = "calc "
        else:
            qual = ""

        if self.modifier == Date.MOD_BEFORE:
            pref = "bef "
        elif self.modifier == Date.MOD_AFTER:
            pref = "aft "
        elif self.modifier == Date.MOD_ABOUT:
            pref = "abt "
        else:
            pref = ""

        nyear = self.newyear_to_str()

        if self.calendar != Date.CAL_GREGORIAN:
            if nyear:
                cal = " (%s,%s)" % (Date.calendar_names[self.calendar], nyear)
            else:
                cal = " (%s)" % Date.calendar_names[self.calendar]
        else:
            if nyear:
                cal = " (%s)" % nyear
            else:
                cal = ""

        if self.modifier == Date.MOD_TEXTONLY:
            val = self.text
        elif self.get_slash():
            val = "%04d/%d-%02d-%02d" % (
                self.dateval[Date._POS_YR] - 1,
                (self.dateval[Date._POS_YR]) % 10,
                self.dateval[Date._POS_MON],
                self.dateval[Date._POS_DAY])
        elif self.is_compound():
            val = "%04d-%02d-%02d - %04d-%02d-%02d" % (
                self.dateval[Date._POS_YR], self.dateval[Date._POS_MON],
                self.dateval[Date._POS_DAY], self.dateval[Date._POS_RYR],
                self.dateval[Date._POS_RMON], self.dateval[Date._POS_RDAY])
        else:
            val = "%04d-%02d-%02d" % (
                self.dateval[Date._POS_YR], self.dateval[Date._POS_MON],
                self.dateval[Date._POS_DAY])
        return "%s%s%s%s" % (qual, pref, val, cal)

    def newyear_to_str(self):
        """
        Return the string representation of the newyear.
        """
        if self.newyear == Date.NEWYEAR_JAN1:
            nyear = ""
        elif self.newyear == Date.NEWYEAR_MAR1:
            nyear = "Mar1"
        elif self.newyear == Date.NEWYEAR_MAR25:
            nyear = "Mar25"
        elif self.newyear == Date.NEWYEAR_SEP1:
            nyear = "Sep1"
        elif isinstance(self.newyear, (list, tuple)):
            nyear = "%s-%s" % (self.newyear[0], self.newyear[1])
        else:
            nyear = "Err"
        return nyear

    @staticmethod
    def newyear_to_code(string):
        """
        Return newyear code of string, where string is:
           '', 'Jan1', 'Mar1', '3-25', '9-1', etc.
        """
        string = string.strip().lower()
        if string == "" or string == "jan1":
            code = Date.NEWYEAR_JAN1
        elif string == "mar1":
            code = Date.NEWYEAR_MAR1
        elif string == "mar25":
            code = Date.NEWYEAR_MAR25
        elif string == "sep1":
            code = Date.NEWYEAR_SEP1
        elif "-" in string:
            try:
                code = tuple(map(int, string.split("-")))
            except:
                code = 0
        else:
            code = 0
        return code

    def get_sort_value(self):
        """
        Return the sort value of Date object.

        If the value is a text string, 0 is returned. Otherwise, the
        calculated sort date is returned. The sort date is rebuilt on every
        assignment.

        The sort value is an integer representing the value. The sortval is
        the integer number of days that have elapsed since Monday, January 1,
        4713 BC in the proleptic Julian calendar.

        .. seealso:: http://en.wikipedia.org/wiki/Julian_day
        """
        return self.sortval

    def get_modifier(self):
        """
        Return an integer indicating the calendar selected.

        The valid values are:

        ============  =====================
        MOD_NONE      no modifier (default)
        MOD_BEFORE    before
        MOD_AFTER     after
        MOD_ABOUT     about
        MOD_RANGE     date range
        MOD_SPAN      date span
        MOD_TEXTONLY  text only
        ============  =====================
        """
        return self.modifier

    def set_modifier(self, val):
        """
        Set the modifier for the date.
        """
        if val not in (Date.MOD_NONE, Date.MOD_BEFORE, Date.MOD_AFTER,
                       Date.MOD_ABOUT, Date.MOD_RANGE, Date.MOD_SPAN,
                       Date.MOD_TEXTONLY):
            raise DateError("Invalid modifier")
        self.modifier = val

    def get_quality(self):
        """
        Return an integer indicating the calendar selected.

        The valid values are:

        ===============  ================
        QUAL_NONE        normal (default)
        QUAL_ESTIMATED   estimated
        QUAL_CALCULATED  calculated
        ===============  ================
        """
        return self.quality

    def set_quality(self, val):
        """
        Set the quality selected for the date.
        """
        if val not in (Date.QUAL_NONE, Date.QUAL_ESTIMATED,
                       Date.QUAL_CALCULATED):
            raise DateError("Invalid quality")
        self.quality = val

    def get_calendar(self):
        """
        Return an integer indicating the calendar selected.

        The valid values are:

        =============  ==========================================
        CAL_GREGORIAN  Gregorian calendar
        CAL_JULIAN     Julian calendar
        CAL_HEBREW     Hebrew (Jewish) calendar
        CAL_FRENCH     French Republican calendar
        CAL_PERSIAN    Persian calendar
        CAL_ISLAMIC    Islamic calendar
        CAL_SWEDISH    Swedish calendar 1700-03-01 -> 1712-02-30!
        =============  ==========================================
        """
        return self.calendar

    def set_calendar(self, val):
        """
        Set the calendar selected for the date.
        """
        if val not in Date.CALENDARS:
            raise DateError("Invalid calendar")
        self.calendar = val

    def get_start_date(self):
        """
        Return a tuple representing the start date.

        If the date is a compound date (range or a span), it is the first part
        of the compound date. If the date is a text string, a tuple of
        (0, 0, 0, False) is returned. Otherwise, a date of (DD, MM, YY, slash)
        is returned. If slash is True, then the date is in the form of 1530/1.
        """
        if self.modifier == Date.MOD_TEXTONLY:
            val = Date.EMPTY
        else:
            val = self.dateval[0:4]
        return val

    def get_stop_date(self):
        """
        Return a tuple representing the second half of a compound date.

        If the date is not a compound date, (including text strings) a tuple
        of (0, 0, 0, False) is returned. Otherwise, a date of (DD, MM, YY, slash)
        is returned. If slash is True, then the date is in the form of 1530/1.
        """
        if self.is_compound():
            val = self.dateval[4:8]
        else:
            val = Date.EMPTY
        return val

    def _get_low_item(self, index):
        """
        Return the item specified.
        """
        if self.modifier == Date.MOD_TEXTONLY:
            val = 0
        else:
            val = self.dateval[index]
        return val

    def _get_low_item_valid(self, index):
        """
        Determine if the item specified is valid.
        """
        if self.modifier == Date.MOD_TEXTONLY:
            val = False
        else:
            val = self.dateval[index] != 0
        return val

    def _get_high_item(self, index):
        """
        Return the item specified.
        """
        if self.is_compound():
            val = self.dateval[index]
        else:
            val = 0
        return val

    def get_year(self):
        """
        Return the year associated with the date.

        If the year is not defined, a zero is returned. If the date is a
        compound date, the lower date year is returned.
        """
        return self._get_low_item(Date._POS_YR)

    def get_year_calendar(self, calendar_name=None):
        """
        Return the year of this date in the calendar name given.

        Defaults to self's calendar if one is not given.

        >>> Date(2009, 12, 8).to_calendar("hebrew").get_year_calendar()
        5770
        """
        if calendar_name:
            cal = lookup_calendar(calendar_name)
        else:
            cal = self.calendar
        if cal == self.calendar:
            return self.get_year()
        else:
            retval = Date(self)
            retval.convert_calendar(cal)
            return retval.get_year()

    def get_new_year(self):
        """
        Return the new year code associated with the date.
        """
        return self.newyear

    def set_new_year(self, value):
        """
        Set the new year code associated with the date.
        """
        self.newyear = value

    def __set_yr_mon_day(self, year, month, day, pos_yr, pos_mon, pos_day):
        dlist = list(self.dateval)
        dlist[pos_yr] = year
        dlist[pos_mon] = month
        dlist[pos_day] = day
        self.dateval = tuple(dlist)

    def set_yr_mon_day(self, year, month, day, remove_stop_date=None):
        """
        Set the year, month, and day values.

        :param remove_stop_date:
            Required parameter for a compound date.
            When True, the stop date is changed to the same date as well.
            When False, the stop date is not changed.
        """
        if self.is_compound() and remove_stop_date is None:
            raise DateError("Required parameter remove_stop_date not set!")

        self.__set_yr_mon_day(year, month, day,
                              Date._POS_YR, Date._POS_MON, Date._POS_DAY)
        self._calc_sort_value()
        if remove_stop_date and self.is_compound():
            self.set2_yr_mon_day(year, month, day)

    def _assert_compound(self):
        if not self.is_compound():
            raise DateError("Operation allowed for compound dates only!")

    def set2_yr_mon_day(self, year, month, day):
        """
        Set the year, month, and day values in the 2nd part of
        a compound date (range or span).
        """
        self._assert_compound()
        self.__set_yr_mon_day(year, month, day,
                              Date._POS_RYR, Date._POS_RMON, Date._POS_RDAY)

    def __set_yr_mon_day_offset(self, year, month, day,
                                pos_yr, pos_mon, pos_day):
        dlist = list(self.dateval)
        if dlist[pos_yr]:
            dlist[pos_yr] += year
        elif year:
            dlist[pos_yr] = year
        if dlist[pos_mon]:
            dlist[pos_mon] += month
        elif month:
            if month < 0:
                dlist[pos_mon] = 1 + month
            else:
                dlist[pos_mon] = month
        # Fix if month out of bounds:
        if month != 0: # only check if changed
            if dlist[pos_mon] == 0: # subtraction
                dlist[pos_mon] = 12
                dlist[pos_yr] -= 1
            elif dlist[pos_mon] < 0: # subtraction
                dlist[pos_yr] -= int((-dlist[pos_mon]) // 12) + 1
                dlist[pos_mon] = (dlist[pos_mon] % 12)
            elif dlist[pos_mon] > 12 or dlist[pos_mon] < 1:
                dlist[pos_yr] += int(dlist[pos_mon] // 12)
                dlist[pos_mon] = dlist[pos_mon] % 12
        self.dateval = tuple(dlist)
        self._calc_sort_value()
        return day != 0 or dlist[pos_day] > 28

    def set_yr_mon_day_offset(self, year=0, month=0, day=0):
        """
        Offset the date by the given year, month, and day values.
        """
        if self.__set_yr_mon_day_offset(year, month, day, Date._POS_YR,
                                        Date._POS_MON, Date._POS_DAY):
            self.set_yr_mon_day(*self.offset(day), remove_stop_date=False)
        if self.is_compound():
            self.set2_yr_mon_day_offset(year, month, day)

    def set2_yr_mon_day_offset(self, year=0, month=0, day=0):
        """
        Set the year, month, and day values by offset in the 2nd part
        of a compound date (range or span).
        """
        self._assert_compound()
        if self.__set_yr_mon_day_offset(year, month, day, Date._POS_RYR,
                                        Date._POS_RMON, Date._POS_RDAY):
            stop = Date(self.get_stop_ymd())
            self.set2_yr_mon_day(*stop.offset(day))

    def copy_offset_ymd(self, year=0, month=0, day=0):
        """
        Return a Date copy based on year, month, and day offset.
        """
        orig_cal = self.calendar
        if self.calendar != 0:
            new_date = self.to_calendar("gregorian")
        else:
            new_date = self
        retval = Date(new_date)
        retval.set_yr_mon_day_offset(year, month, day)
        if orig_cal == 0:
            return retval
        else:
            retval.convert_calendar(orig_cal)
            return retval

    def copy_ymd(self, year=0, month=0, day=0, remove_stop_date=None):
        """
        Return a Date copy with year, month, and day set.

        :param remove_stop_date: Same as in set_yr_mon_day.
        """
        retval = Date(self)
        retval.set_yr_mon_day(year, month, day, remove_stop_date)
        return retval

    def set_year(self, year):
        """
        Set the year value.
        """
        self.dateval = self.dateval[0:2] + (year, ) + self.dateval[3:]
        self._calc_sort_value()

    def get_year_valid(self):
        """
        Return true if the year is valid.
        """
        return self._get_low_item_valid(Date._POS_YR)

    def get_month(self):
        """
        Return the month associated with the date.

        If the month is not defined, a zero is returned. If the date is a
        compound date, the lower date month is returned.
        """
        return self._get_low_item(Date._POS_MON)

    def get_month_valid(self):
        """
        Return true if the month is valid
        """
        return self._get_low_item_valid(Date._POS_MON)

    def get_day(self):
        """
        Return the day of the month associated with the date.

        If the day is not defined, a zero is returned. If the date is a
        compound date, the lower date day is returned.
        """
        return self._get_low_item(Date._POS_DAY)

    def get_day_valid(self):
        """
        Return true if the day is valid.
        """
        return self._get_low_item_valid(Date._POS_DAY)

    def get_valid(self):
        """
        Return true if any part of the date is valid.
        """
        return self.modifier != Date.MOD_TEXTONLY

    def is_valid(self):
        """
        Return true if any part of the date is valid.
        """
        return self.modifier != Date.MOD_TEXTONLY and self.sortval != 0

    def get_stop_year(self):
        """
        Return the day of the year associated with the second part of a
        compound date.

        If the year is not defined, a zero is returned.
        """
        return self._get_high_item(Date._POS_RYR)

    def get_stop_month(self):
        """
        Return the month of the month associated with the second part of a
        compound date.

        If the month is not defined, a zero is returned.
        """
        return self._get_high_item(Date._POS_RMON)

    def get_stop_day(self):
        """
        Return the day of the month associated with the second part of a
        compound date.

        If the day is not defined, a zero is returned.
        """
        return self._get_high_item(Date._POS_RDAY)

    def get_high_year(self):
        """
        Return the high year estimate.

        For compound dates with non-zero stop year, the stop year is returned.
        Otherwise, the start year is returned.
        """
        if self.is_compound():
            ret = self.get_stop_year()
            if ret:
                return ret
        else:
            return self.get_year()

    def get_text(self):
        """
        Return the text value associated with an invalid date.
        """
        return self.text

    def get_dow(self):
        """
        Return an integer representing the day of the week associated with the
        date (Monday=0).

        If the day is not defined, a None is returned. If the date is a
        compound date, the lower date day is returned.
        """
        return self.sortval % 7 if self.is_regular() else None

    def _zero_adjust_ymd(self, year, month, day):
        year = year if year != 0 else 1
        month = max(month, 1)
        day = max(day, 1)
        return (year, month, day)

    def _adjust_newyear(self):
        """
        Returns year adjustment performed (0 or -1).
        """
        nyear = self.get_new_year()
        year_delta = 0
        if nyear: # new year offset?
            if nyear == Date.NEWYEAR_MAR1:
                split = (3, 1)
            elif nyear == Date.NEWYEAR_MAR25:
                split = (3, 25)
            elif nyear == Date.NEWYEAR_SEP1:
                split = (9, 1)
            elif isinstance(nyear, (list, tuple)):
                split = nyear
            else:
                split = (0, 0)
            if (self.get_month(), self.get_day()) >= split and split != (0, 0):
                year_delta = -1
                new_date = Date(self.get_year() + year_delta, self.get_month(),
                                self.get_day())
                new_date.set_calendar(self.calendar)
                new_date.recalc_sort_value()
                self.sortval = new_date.sortval
        return year_delta

    def set(self, quality=None, modifier=None, calendar=None,
            value=None, text=None, newyear=0):
        """
        Set the date to the specified value.

        :param quality: The date quality for the date (see :meth:`get_quality`
                        for more information).
                        Defaults to the previous value for the date.
        :param modified: The date modifier for the date (see
                         :meth:`get_modifier` for more information)
                         Defaults to the previous value for the date.
        :param calendar: The calendar associated with the date (see
                         :meth:`get_calendar` for more information).
                         Defaults to the previous value for the date.
        :param value: A tuple representing the date information. For a
                      non-compound date, the format is (DD, MM, YY, slash)
                      and for a compound date the tuple stores data as
                      (DD, MM, YY, slash1, DD, MM, YY, slash2)
                      Defaults to the previous value for the date.
        :param text: A text string holding either the verbatim user input
                     or a comment relating to the date.
                     Defaults to the previous value for the date.
        :param newyear: The newyear code, or tuple representing (month, day)
                        of newyear day.
                        Defaults to 0.

        The sort value is recalculated.
        """

        if quality is None:
            quality = self.quality
        if modifier is None:
            modifier = self.modifier
        if calendar is None:
            calendar = self.calendar
        if value is None:
            value = self.dateval

        if modifier in (Date.MOD_NONE, Date.MOD_BEFORE,
                        Date.MOD_AFTER, Date.MOD_ABOUT) and len(value) < 4:
            raise DateError("Invalid value. Should be: (DD, MM, YY, slash)")
        if modifier in (Date.MOD_RANGE, Date.MOD_SPAN) and len(value) < 8:
            raise DateError("Invalid value. Should be: (DD, MM, "
                            "YY, slash1, DD, MM, YY, slash2)")
        if modifier not in (Date.MOD_NONE, Date.MOD_BEFORE, Date.MOD_AFTER,
                            Date.MOD_ABOUT, Date.MOD_RANGE, Date.MOD_SPAN,
                            Date.MOD_TEXTONLY):
            raise DateError("Invalid modifier")
        if quality not in (Date.QUAL_NONE, Date.QUAL_ESTIMATED,
                           Date.QUAL_CALCULATED):
            raise DateError("Invalid quality")
        if calendar not in Date.CALENDARS:
            raise DateError("Invalid calendar")
        if newyear != 0 and calendar_has_fixed_newyear(calendar):
            raise DateError(
                "May not adjust newyear to {ny} for calendar {cal}".format(
                    ny=newyear, cal=calendar))

        self.quality = quality
        self.modifier = modifier
        self.calendar = calendar
        self.dateval = value
        self.set_new_year(newyear)
        year, month, day = self._zero_adjust_ymd(
            value[Date._POS_YR],
            value[Date._POS_MON],
            value[Date._POS_DAY])

        if year == month == day == 0:
            self.sortval = 0
        else:
            func = Date._calendar_convert[calendar]
            self.sortval = func(year, month, day)

        if self.get_slash() and self.get_calendar() != Date.CAL_JULIAN:
            self.set_calendar(Date.CAL_JULIAN)
            self.recalc_sort_value()

        year_delta = self._adjust_newyear()

        if text:
            self.text = text

        if modifier != Date.MOD_TEXTONLY:
            sanity = Date(self)
            sanity.convert_calendar(self.calendar, known_valid=False)
            # convert_calendar resets slash and new year, restore these as needed
            if sanity.get_slash() != self.get_slash():
                sanity.set_slash(self.get_slash())
            if self.is_compound() and sanity.get_slash2() != self.get_slash2():
                sanity.set_slash2(self.get_slash2())
            if sanity.get_new_year() != self.get_new_year():
                sanity.set_new_year(self.get_new_year())
                sanity._adjust_newyear()

            # We don't do the roundtrip conversion on self, becaue
            # it would remove uncertainty on day/month expressed with zeros

            # Did the roundtrip change the date value?!
            if sanity.dateval != value:
                try:
                    self.__compare(sanity.dateval, value, year_delta)
                except DateError as err:
                    LOG.debug("Sanity check failed - self: {}, sanity: {}".
                              format(self.__dict__, sanity.__dict__))
                    err.date = self
                    raise

    def __compare(self, sanity, value, year_delta):
        ziplist = zip(sanity, value)
        # Loop over all values present, whether compound or not
        for day, month, year, slash in zip(*[iter(ziplist)]*4):
            # each of d,m,y,sl is a pair from dateval and value, to compare
            adjusted, original = slash
            if adjusted != original:
                raise DateError("Invalid date value {}".
                                format(value))

            for adjusted, original in day, month:
                if adjusted != original and not(original == 0 and
                                                adjusted == 1):
                    raise DateError("Invalid day/month {} passed in value {}".
                                    format(original, value))

            adjusted, original = year
            adjusted -= year_delta
            if adjusted != original and not(original == 0 and adjusted == 1):
                raise DateError("Invalid year {} passed in value {}".
                                format(original, value))

    def recalc_sort_value(self):
        """
        Recalculates the numerical sort value associated with the date
        and returns it. Public method.
        """
        self._calc_sort_value()
        return self.sortval

    def _calc_sort_value(self):
        """
        Calculate the numerical sort value associated with the date.
        """
        year, month, day = self._zero_adjust_ymd(
            self.dateval[Date._POS_YR],
            self.dateval[Date._POS_MON],
            self.dateval[Date._POS_DAY])
        if year == month == 0 and day == 0:
            self.sortval = 0
        else:
            func = Date._calendar_convert[self.calendar]
            self.sortval = func(year, month, day)

    def convert_calendar(self, calendar, known_valid=True):
        """
        Convert the date from the current calendar to the specified calendar.
        """
        if (known_valid  # if not known valid, round-trip convert anyway
                and calendar == self.calendar
                and self.newyear == Date.NEWYEAR_JAN1):
            return
        (year, month, day) = Date._calendar_change[calendar](self.sortval)
        if self.is_compound():
            ryear, rmonth, rday = self._zero_adjust_ymd(
                self.dateval[Date._POS_RYR],
                self.dateval[Date._POS_RMON],
                self.dateval[Date._POS_RDAY])
            sdn = Date._calendar_convert[self.calendar](ryear, rmonth, rday)
            (nyear, nmonth, nday) = Date._calendar_change[calendar](sdn)
            self.dateval = (day, month, year, False,
                            nday, nmonth, nyear, False)
        else:
            self.dateval = (day, month, year, False)
        self.calendar = calendar
        self.newyear = Date.NEWYEAR_JAN1

    def set_as_text(self, text):
        """
        Set the day to a text string, and assign the sort value to zero.
        """
        self.modifier = Date.MOD_TEXTONLY
        self.text = text
        self.sortval = 0

    def set_text_value(self, text):
        """
        Set the text string to a given text.
        """
        self.text = text

    def is_empty(self):
        """
        Return True if the date contains no information (empty text).
        """
        return not((self.modifier == Date.MOD_TEXTONLY and self.text)
               or self.get_start_date() != Date.EMPTY
                or self.get_stop_date() != Date.EMPTY)

    def is_compound(self):
        """
        Return True if the date is a date range or a date span.
        """
        return self.modifier == Date.MOD_RANGE \
               or self.modifier == Date.MOD_SPAN

    def is_regular(self):
        """
        Return True if the date is a regular date.

        The regular date is a single exact date, i.e. not text-only, not
        a range or a span, not estimated/calculated, not about/before/after
        date, and having year, month, and day all non-zero.
        """
        return self.modifier == Date.MOD_NONE \
               and self.quality == Date.QUAL_NONE \
               and self.get_year_valid() and self.get_month_valid() \
               and self.get_day_valid()

    def is_full(self):
        """
        Return True if the date is fully specified.
        """
        return (self.get_year_valid() and
                self.get_month_valid() and
                self.get_day_valid())

    def get_ymd(self):
        """
        Return (year, month, day).
        """
        return (self.get_year(), self.get_month(), self.get_day())

    def get_dmy(self, get_slash=False):
        """
        Return (day, month, year, [slash]).
        """
        if get_slash:
            return (self.get_day(), self.get_month(), self.get_year(),
                    self.get_slash())
        else:
            return (self.get_day(), self.get_month(), self.get_year())

    def get_stop_ymd(self):
        """
        Return (year, month, day) of the stop date, or all-zeros if it's not
        defined.
        """
        return (self.get_stop_year(), self.get_stop_month(),
                self.get_stop_day())

    def offset(self, value):
        """
        Return (year, month, day) of this date +- value.
        """
        return Date._calendar_change[Date.CAL_GREGORIAN](self.sortval + value)

    def offset_date(self, value):
        """
        Return (year, month, day) of this date +- value.
        """
        return Date(Date._calendar_change[Date.CAL_GREGORIAN](self.sortval +
                                                              value))

    def lookup_calendar(self, calendar):
        """
        Lookup calendar name in the list of known calendars, even if translated.
        """
        return lookup_calendar(calendar)

    def lookup_quality(self, quality):
        """
        Lookup date quality keyword, even if translated.
        """
        qualities = ["none", "estimated", "calculated"]
        ui_qualities = [_("none", "date-quality"),
                        _("estimated"), _("calculated")]
        if quality.lower() in qualities:
            return qualities.index(quality.lower())
        elif quality.lower() in ui_qualities:
            return ui_qualities.index(quality.lower())
        else:
            raise AttributeError("invalid quality: '%s'" % quality)

    def lookup_modifier(self, modifier):
        """
        Lookup date modifier keyword, even if translated.
        """
        mods = ["none", "before", "after", "about",
                "range", "span", "textonly"]
        ui_mods = [_("none", "date-modifier"),
                   _("before"), _("after"), _("about"),
                   _("range"), _("span"), _("textonly")]
        if modifier.lower() in mods:
            return mods.index(modifier.lower())
        elif modifier.lower() in ui_mods:
            return ui_mods.index(modifier.lower())
        else:
            raise AttributeError("invalid modifier: '%s'" % modifier)

    def to_calendar(self, calendar_name):
        """
        Return a new Date object in the calendar calendar_name.

        >>> Date(1591, 1, 1).to_calendar("julian")
        1590-12-22 (Julian)
        """
        cal = lookup_calendar(calendar_name)
        retval = Date(self)
        retval.convert_calendar(cal)
        return retval

    def get_slash(self):
        """
        Return true if the date is a slash-date (dual dated).
        """
        return self._get_low_item_valid(Date._POS_SL)

    def set_slash(self, value):
        """
        Set to 1 if the date is a slash-date (dual dated).
        """
        temp = list(self.dateval)
        temp[Date._POS_SL] = value
        self.dateval = tuple(temp)

    def get_slash2(self):
        """
        Return true if the ending date is a slash-date (dual dated).
        """
        return self._get_low_item_valid(Date._POS_RSL)

    def set_slash2(self, value):
        """
        Set to 1 if the ending date is a slash-date (dual dated).
        """
        temp = list(self.dateval)
        temp[Date._POS_RSL] = value
        self.dateval = tuple(temp)

    def make_vague(self):
        """
        Remove month and day details to make the date approximate.
        """
        dlist = list(self.dateval)
        dlist[Date._POS_MON] = 0
        dlist[Date._POS_DAY] = 0
        if Date._POS_RDAY < len(dlist):
            dlist[Date._POS_RDAY] = 0
            dlist[Date._POS_RMON] = 0
        self.dateval = tuple(dlist)
        self._calc_sort_value()

    year = property(get_year, set_year)

def Today():
    """
    Returns a Date object set to the current date.
    """
    import time
    current_date = Date()
    current_date.set_yr_mon_day(*time.localtime(time.time())[0:3])
    return current_date

def NextYear():
    """
    Returns a Date object set to next year
    """
    return Today() + 1

#-------------------------------------------------------------------------
#
# Date Functions
#
#-------------------------------------------------------------------------


def lookup_calendar(calendar):
    """
    Find the ID associated with the calendar name.

    >>> lookup_calendar("hebrew")
    2
    """
    if calendar is None: return Date.CAL_GREGORIAN
    if isinstance(calendar, int): return calendar
    for pos, calendar_name in enumerate(Date.calendar_names):
        if calendar.lower() == calendar_name.lower():
            return pos
    for pos, calendar_name in enumerate(Date.ui_calendar_names):
        if calendar.lower() == calendar_name.lower():
            return pos
    raise AttributeError("invalid calendar: '%s'" % calendar)

def gregorian(date):
    """Convert given date to gregorian. Doesn't modify the original object."""
    if date.get_calendar() != Date.CAL_GREGORIAN:
        date = Date(date)
        date.convert_calendar(Date.CAL_GREGORIAN)
    return date

def calendar_has_fixed_newyear(cal):
    """Does the given calendar have a fixed new year, or may it be reset?"""
    return cal not in (Date.CAL_GREGORIAN, Date.CAL_JULIAN, Date.CAL_SWEDISH)

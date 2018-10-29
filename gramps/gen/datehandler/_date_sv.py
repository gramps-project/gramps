# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2006  Donald N. Allingham
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

"""
Swedish-specific classes for parsing and displaying dates.
"""

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import re

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from ..lib.date import Date
from ._dateparser import DateParser
from ._datedisplay import DateDisplay
from ._datehandler import register_datehandler

#-------------------------------------------------------------------------
#
# Swedish parser class
#
#-------------------------------------------------------------------------
class DateParserSv(DateParser):
    """
    Convert a text string into a Date object, expecting a date
    notation in the swedish language. If the date cannot be converted,
    the text string is assigned.
    """

    # modifiers before the date
    modifier_to_int = {
        'före'    : Date.MOD_BEFORE,
        'innan'   : Date.MOD_BEFORE,
        'efter'   : Date.MOD_AFTER,
        'omkring' : Date.MOD_ABOUT,
        'ca'      : Date.MOD_ABOUT,
        'c:a'     : Date.MOD_ABOUT
        }

    bce = ["f Kr"]

    calendar_to_int = {
        'gregoriansk   '      : Date.CAL_GREGORIAN,
        'g'                   : Date.CAL_GREGORIAN,
        'juliansk'            : Date.CAL_JULIAN,
        'j'                   : Date.CAL_JULIAN,
        'hebreisk'            : Date.CAL_HEBREW,
        'h'                   : Date.CAL_HEBREW,
        'islamisk'            : Date.CAL_ISLAMIC,
        'muslimsk'            : Date.CAL_ISLAMIC,
        'i'                   : Date.CAL_ISLAMIC,
        'fransk'              : Date.CAL_FRENCH,
        'fransk republikansk' : Date.CAL_FRENCH,
        'f'                   : Date.CAL_FRENCH,
        'persisk'             : Date.CAL_PERSIAN,
        'p'                   : Date.CAL_PERSIAN,
        'svensk'              : Date.CAL_SWEDISH,
        's'                   : Date.CAL_SWEDISH,
        }

    quality_to_int = {
        'uppskattat' : Date.QUAL_ESTIMATED,
        'uppskattad' : Date.QUAL_ESTIMATED,
        'bedömt'     : Date.QUAL_ESTIMATED,
        'bedömd'     : Date.QUAL_ESTIMATED,
        'beräknat'   : Date.QUAL_CALCULATED,
        'beräknad'   : Date.QUAL_CALCULATED,
        }

    def init_strings(self):
        """ Define, in Swedish, span and range regular expressions"""
        DateParser.init_strings(self)
        self._numeric = re.compile(r"((\d+)/)?\s*((\d+)/)?\s*(\d+)[/ ]?$")
        # this next RE has the (possibly-slashed) year at the string's start
        self._text2 = re.compile(r'((\d+)(/\d+)?)?\s+?%s\s*(\d+)?\s*$'
                                 % self._mon_str, re.IGNORECASE)
        self._span = re.compile(
            r"(från)?\s*(?P<start>.+)\s*(till|--|–)\s*(?P<stop>.+)",
            re.IGNORECASE)
        self._range = re.compile(
            r"(mellan)\s+(?P<start>.+)\s+och\s+(?P<stop>.+)",
            re.IGNORECASE)

#-------------------------------------------------------------------------
#
# Swedish display class
#
#-------------------------------------------------------------------------
class DateDisplaySv(DateDisplay):
    """
    Swedish language date display class.
    """

    _bce_str = "%s f Kr"

    formats = (
        "ÅÅÅÅ-MM-DD (ISO)",
        "År/mån/dag",
        "År månad dag",
        "År mån dag",
        )
        # this definition must agree with its "_display_calendar" method

    def _display_calendar(self, date_val, long_months, short_months = None,
                          inflect=""):
        # this must agree with its locale-specific "formats" definition

        if short_months is None:
            # Let the short formats work the same as long formats
            short_months = long_months

        if self.format == 0:
            return self.display_iso(date_val)
        elif self.format == 1:
            # numerical: year/month/day (with slashes)
            value = self.dd_dformat01(date_val)
        elif self.format == 2:
            # year month_name day
            value = self.dd_dformat02_sv(date_val, long_months)
        # elif self.format == 3:
        else:
            # year month_abbreviation day
            value = self.dd_dformat03_sv(date_val, short_months)
        if date_val[2] < 0:
            # TODO fix BUG 7064: non-Gregorian calendars wrongly use BCE notation for negative dates
            return self._bce_str % value
        else:
            return value

    def dd_dformat02_sv(self, date_val, long_months):
        # year month_name day
        year = self._slash_year(date_val[2], date_val[3])
        if date_val[0] == 0:
            if date_val[1] == 0:
                return year
            else:
                return "%s %s" % (year, long_months[date_val[1]])
        elif date_val[1] == 0: # month is zero but day is not (see 8477)
            return self.display_iso(date_val)
        else:
            return "%s %s %s" % (year, long_months[date_val[1]], date_val[0])

    def dd_dformat03_sv(self, date_val, short_months):
        # year month_abbreviation day
        year = self._slash_year(date_val[2], date_val[3])
        if date_val[0] == 0:
            if date_val[1] == 0:
                return year
            else:
                return "%s %s" % (year, short_months[date_val[1]])
        elif date_val[1] == 0: # month is zero but day is not (see 8477)
            return self.display_iso(date_val)
        else:
            return "%s %s %s" % (year, short_months[date_val[1]], date_val[0])

    display = DateDisplay.display_formatted

#-------------------------------------------------------------------------
#
# Register classes
#
#-------------------------------------------------------------------------
register_datehandler(
    ('sv_SE', 'sv_SE.UTF-8', 'sv', 'Swedish', ('%Y-%m-%d',)),
    DateParserSv, DateDisplaySv)

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
Danish-specific classes for parsing and displaying dates.
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
# Danish parser class
#
#-------------------------------------------------------------------------
class DateParserDa(DateParser):
    """
    Convert a text string into a Date object, expecting a date
    notation in the Danish language. If the date cannot be converted,
    the text string is assigned.
    """

    # modifiers before the date
    modifier_to_int = {
        'før'    : Date.MOD_BEFORE,
        'inden'  : Date.MOD_BEFORE,
        'efter'   : Date.MOD_AFTER,
        'omkring' : Date.MOD_ABOUT,
        'ca.'     : Date.MOD_ABOUT
        }

    bce = ["f Kr"]

    calendar_to_int = {
        'gregoriansk   '      : Date.CAL_GREGORIAN,
        'g'                   : Date.CAL_GREGORIAN,
        'juliansk'            : Date.CAL_JULIAN,
        'j'                   : Date.CAL_JULIAN,
        'hebraisk'            : Date.CAL_HEBREW,
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
        'estimeret' : Date.QUAL_ESTIMATED,
        'beregnet'   : Date.QUAL_CALCULATED,
        }

    def init_strings(self):
        DateParser.init_strings(self)
        self._span = re.compile(
            r"(fra)?\s*(?P<start>.+)\s*(til|--|–)\s*(?P<stop>.+)",
            re.IGNORECASE)
        self._range = re.compile(
            r"(mellem)\s+(?P<start>.+)\s+og\s+(?P<stop>.+)", re.IGNORECASE)

#-------------------------------------------------------------------------
#
# Danish display class
#
#-------------------------------------------------------------------------
class DateDisplayDa(DateDisplay):
    """
    Danish language date display class.
    """

    long_months = ( "", "januar", "februar", "marts", "april", "maj",
                    "juni", "juli", "august", "september", "oktober",
                    "november", "december" )

    short_months = ( "", "jan", "feb", "mar", "apr", "maj", "jun",
                     "jul", "aug", "sep", "okt", "nov", "dec" )

    formats = (
        "ÅÅÅÅ-MM-DD (ISO)",
        "Numerisk",
        "Måned dag, år",
        "Md Dag År",
        "Dag måned år",
        "Dag md År",
        )
        # this must agree with DateDisplayEn's "formats" definition
        # (since no locale-specific _display_gregorian exists, here)

    calendar = (
        "",
        "juliansk",
        "hebraisk",
        "fransk republikansk",
        "persisk",
        "islamisk",
        "svensk"
        )

    _mod_str = ("", "før ", "efter ", "ca. ", "", "", "")

    _qual_str = ("", "beregnet ", "beregnet ")

    _bce_str = "%s f. Kr."

    def display(self, date):
        """
        Return a text string representing the date.
        """
        mod = date.get_modifier()
        cal = date.get_calendar()
        qual = date.get_quality()
        start = date.get_start_date()
        newyear = date.get_new_year()

        qual_str = self._qual_str[qual]

        if mod == Date.MOD_TEXTONLY:
            return date.get_text()
        elif start == Date.EMPTY:
            return ""
        elif mod == Date.MOD_SPAN:
            d1 = self.display_cal[cal](start)
            d2 = self.display_cal[cal](date.get_stop_date())
            scal = self.format_extras(cal, newyear)
            return "%sfra %s til %s%s" % (qual_str, d1, d2, scal)
        elif mod == Date.MOD_RANGE:
            d1 = self.display_cal[cal](start)
            d2 = self.display_cal[cal](date.get_stop_date())
            scal = self.format_extras(cal, newyear)
            return "%smellem %s og %s%s" % (qual_str, d1, d2,
                                              scal)
        else:
            text = self.display_cal[date.get_calendar()](start)
            scal = self.format_extras(cal, newyear)
            return "%s%s%s%s" % (qual_str, self._mod_str[mod],
                                 text, scal)

#-------------------------------------------------------------------------
#
# Register classes
#
#-------------------------------------------------------------------------
register_datehandler(
    ('da_DK', 'da', 'dansk', 'Danish', ('%d-%m-%Y',)),
    DateParserDa, DateDisplayDa)

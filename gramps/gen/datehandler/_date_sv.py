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
        self._span     = re.compile("(från)?\s*(?P<start>.+)\s*(till|--|–)\s*(?P<stop>.+)",
                                    re.IGNORECASE)
        self._range    = re.compile("(mellan)\s+(?P<start>.+)\s+och\s+(?P<stop>.+)",
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
    long_months = ( "", "januari", "februari", "mars", "april", "maj",
                    "juni", "juli", "augusti", "september", "oktober",
                    "november", "december" )

    short_months = ( "", "jan", "feb", "mar", "apr", "maj", "jun",
                      "jul", "aug", "sep", "okt", "nov", "dec" )

    formats = (
        "ÅÅÅÅ-MM-DD (ISO)",
        "År/mån/dag",
        "Månad dag, år",
        "MÅN DAG ÅR",
        "Dag månad år",
        "DAG MÅN ÅR",
        )
        # this must agree with DateDisplayEn's "formats" definition
        # (since no locale-specific _display_gregorian exists, here)

    calendar = (
        "",
        "juliansk",
        "hebreisk",
        "fransk republikansk",
        "persisk",
        "islamisk",
        "svensk"
        )

    _mod_str = ("", "före ", "efter ", "c:a ", "", "", "")

    _qual_str = ("", "uppskattat ", "beräknat ")

    _bce_str = "%s f Kr"

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
            return "%sfrån %s till %s%s" % (qual_str, d1, d2, scal)
        elif mod == Date.MOD_RANGE:
            d1 = self.display_cal[cal](start)
            d2 = self.display_cal[cal](date.get_stop_date())
            scal = self.format_extras(cal, newyear)
            return "%smellan %s och %s%s" % (qual_str, d1, d2,
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
register_datehandler(('sv_SE', 'sv_SE.UTF-8', 'sv', 'Swedish'), DateParserSv, DateDisplaySv)

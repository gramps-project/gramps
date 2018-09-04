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
Slovak-specific classes for parsing and displaying dates.
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
# Slovak parser
#
#-------------------------------------------------------------------------
class DateParserSK(DateParser):

    modifier_to_int = {
        'pred'   : Date.MOD_BEFORE,
        'do'     : Date.MOD_BEFORE,
        'po'     : Date.MOD_AFTER,
        'asi'    : Date.MOD_ABOUT,
        'okolo'  : Date.MOD_ABOUT,
        'pribl.' : Date.MOD_ABOUT,
        }

    calendar_to_int = {
        'gregoriánsky'  : Date.CAL_GREGORIAN,
        'g'             : Date.CAL_GREGORIAN,
        'juliánsky'     : Date.CAL_JULIAN,
        'j'             : Date.CAL_JULIAN,
        'hebrejský'     : Date.CAL_HEBREW,
        'h'             : Date.CAL_HEBREW,
        'islamský'      : Date.CAL_ISLAMIC,
        'i'             : Date.CAL_ISLAMIC,
        'republikánsky' : Date.CAL_FRENCH,
        'r'             : Date.CAL_FRENCH,
        'perzský'       : Date.CAL_PERSIAN,
        'p'             : Date.CAL_PERSIAN,
        'švédsky'      : Date.CAL_SWEDISH,
        's'            : Date.CAL_SWEDISH,
        }

    quality_to_int = {
        'odhadovaný' : Date.QUAL_ESTIMATED,
        'odh.'       : Date.QUAL_ESTIMATED,
        'vypočítaný' : Date.QUAL_CALCULATED,
        'vyp.'       : Date.QUAL_CALCULATED,
        }

    def init_strings(self):
        DateParser.init_strings(self)
        _span_1 = ['od']
        _span_2 = ['do']
        _range_1 = ['medzi']
        _range_2 = ['a']
        self._span = re.compile(r"(%s)\s+(?P<start>.+)\s+(%s)\s+(?P<stop>.+)"
                                % ('|'.join(_span_1), '|'.join(_span_2)),
                                re.IGNORECASE)
        self._range = re.compile(r"(%s)\s+(?P<start>.+)\s+(%s)\s+(?P<stop>.+)"
                                 % ('|'.join(_range_1), '|'.join(_range_2)),
                                 re.IGNORECASE)

#-------------------------------------------------------------------------
#
# Slovak display
#
#-------------------------------------------------------------------------
class DateDisplaySK(DateDisplay):
    """
    Slovak language date display class.
    """
    long_months = ( "", "január", "február", "marec", "apríl", "máj",
                    "jún", "júl", "august", "september", "október",
                    "november", "december" )

    short_months = ( "", "jan", "feb", "mar", "apr", "máj", "jún",
                     "júl", "aug", "sep", "okt", "nov", "dec" )

    calendar = (
        "", "juliánsky", "hebrejský",
        "republikánsky", "perzský", "islamský",
        "švédsky"
        )

    _mod_str = ("", "pred ", "po ", "okolo ", "", "", "")

    _qual_str = ("", "odh. ", "vyp. ")

    formats = (
        "RRRR-MM-DD (ISO)", "numerický", "Mesiac Deň, Rok",
        "MES Deň, Rok", "Deň, Mesiac, Rok", "Deň MES Rok"
        )
        # this must agree with DateDisplayEn's "formats" definition
        # (since no locale-specific _display_gregorian exists, here)

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
            return "%s%s %s %s %s%s" % (qual_str, 'od', d1,
                                        'do', d2, scal)
        elif mod == Date.MOD_RANGE:
            d1 = self.display_cal[cal](start)
            d2 = self.display_cal[cal](date.get_stop_date())
            scal = self.format_extras(cal, newyear)
            return "%s%s %s %s %s%s" % (qual_str, 'medzi',
                                        d1, 'a', d2, scal)
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
    ('sk_SK', 'sk', 'SK', 'Slovak', ('%d.%m.%Y',)),
    DateParserSK, DateDisplaySK)

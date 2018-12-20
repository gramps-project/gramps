# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2007  Donald N. Allingham
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
# $Id: _date_hr.py 22672 2013-07-13 18:01:08Z paul-franklin $
#

# Croatian version 2008 by Josip
# Croatian version 2018 by Milo

"""
Croatian-specific classes for parsing and displaying dates.
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
# Croatian parser
#
#-------------------------------------------------------------------------
class DateParserHR(DateParser):
    modifier_to_int = {
        'prije'   : Date.MOD_BEFORE,
        'pr. '    : Date.MOD_BEFORE,
        'poslije' : Date.MOD_AFTER,
        'po. '    : Date.MOD_AFTER,
        'nakon'   : Date.MOD_AFTER,
        'na. '    : Date.MOD_AFTER,
        'oko'     : Date.MOD_ABOUT,
        'okolo'   : Date.MOD_ABOUT,
        'ok. '    : Date.MOD_ABOUT,
        }

    quality_to_int = {
        'približno' : Date.QUAL_ESTIMATED,
        'prb.'      : Date.QUAL_ESTIMATED,
        'izračunato'  : Date.QUAL_CALCULATED,
        'izr.'       : Date.QUAL_CALCULATED,
        }

    bce = ["prije nove ere", "prije Krista",
           "p.n.e."] + DateParser.bce

    def init_strings(self):
        """
        compiles regular expression strings for matching dates
        """
        DateParser.init_strings(self)

        # match 'Day. MONTH year.' format with or without dots
        self._text2 = re.compile(r'(\d+)?\.?\s*?%s\.?\s*((\d+)(/\d+)?)?\s*\.?$'
                                 % self._mon_str, re.IGNORECASE)

        # match Day.Month.Year.
        self._numeric = re.compile(
                            r"((\d+)[/\. ])?\s*((\d+)[/\.])?\s*(\d+)\.?$")

        self._jtext2 = re.compile(r'(\d+)?.?\s+?%s\s*((\d+)(/\d+)?)?'
                                  % self._jmon_str, re.IGNORECASE)

        _span_1 = ['od']
        _span_2 = ['do']
        _range_1 = ['između']
        _range_2 = ['i']
        self._span = re.compile(r"(%s)\s+(?P<start>.+)\s+(%s)\s+(?P<stop>.+)"
                                % ('|'.join(_span_1), '|'.join(_span_2)),
                                re.IGNORECASE)
        self._range = re.compile(r"(%s)\s+(?P<start>.+)\s+(%s)\s+(?P<stop>.+)"
                                 % ('|'.join(_range_1), '|'.join(_range_2)),
                                 re.IGNORECASE)

#-------------------------------------------------------------------------
#
# Croatian display
#
#-------------------------------------------------------------------------
class DateDisplayHR(DateDisplay):
    """
    Croatian language date display class.
    """
     # TODO fix BUG 7064: non-Gregorian calendars wrongly use BCE notation for negative dates
    # not refactoring _bce_str into base class because it'll be gone under #7064
    _bce_str = "%s p.n.e."

    display = DateDisplay.display_formatted

    def format_short_month_year(self, month, year, inflect, short_months):
        """ Allow a subclass to modify the year, e.g. add a period """
        if not hasattr(short_months[1], 'f'): # not a Lexeme: no inflection
            return "{short_month} {year}.".format(
                     short_month = short_months[month], year = year)
        return self.FORMATS_short_month_year[inflect].format(
                     short_month = short_months[month], year = year)

    def _get_localized_year(self, year):
        """ Allow a subclass to modify the year, e.g. add a period """
        return year + '.'

    # FIXME probably there should be a Croatian-specific "formats" (and this
    # ("American comma") format (and dd_dformat03 too) should be eliminated)
    def dd_dformat02(self, date_val, inflect, long_months):
        """ month_name day, year """
        return DateDisplay.dd_dformat02(
            self, date_val, inflect, long_months).replace(' .', '')

    def dd_dformat04(self, date_val, inflect, long_months):
        """ day month_name year """
        return DateDisplay.dd_dformat04(
            self, date_val, inflect, long_months).replace(' .', '')

#-------------------------------------------------------------------------
#
# Register classes
#
#-------------------------------------------------------------------------
register_datehandler(
    ('hr_HR', 'hr', 'HR', 'croatian', 'Croatian', 'hrvatski', ('%d. %m. %Y.',)),
    DateParserHR, DateDisplayHR)

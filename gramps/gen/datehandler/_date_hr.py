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
# GRAMPS modules
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
        'prije'    : Date.MOD_BEFORE, 
        'pr. '    : Date.MOD_BEFORE,
        'poslije'   : Date.MOD_AFTER,
        'po. '   : Date.MOD_AFTER,
        'okolo'  : Date.MOD_ABOUT,
        'ok. '     : Date.MOD_ABOUT,
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
        self._text2 = re.compile('(\d+)?\.?\s*?%s\.?\s*((\d+)(/\d+)?)?\s*\.?$'
                                    % self._mon_str, re.IGNORECASE)


        # match Day.Month.Year.
        self._numeric = re.compile(
                            "((\d+)[/\. ])?\s*((\d+)[/\.])?\s*(\d+)\.?$")
                                #"((\d+)[/\.]\s*)?((\d+)[/\.]\s*)?(\d+)\s*$")
        self._span = re.compile(
                            "(od)\s+(?P<start>.+)\s+(do)\s+(?P<stop>.+)",
                                re.IGNORECASE)
        self._jtext2 = re.compile('(\d+)?.?\s+?%s\s*((\d+)(/\d+)?)?'\
                                % self._jmon_str, re.IGNORECASE) 

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

    def dd_dformat01(self, date_val):
        """
        numerical
        """
        if date_val[3]:
            return self.display_iso(date_val)
        else:
            if date_val[0] == date_val[1] == 0:
                return str(date_val[2]) + '.'
            else:
                value = self._tformat.replace('%m', str(date_val[1]))
                value = value.replace('%d', str(date_val[0]))
                value = value.replace('%Y', str(abs(date_val[2])))
                return value

    def dd_dformat04(self, date_val, inflect, long_months):
        """
        day month_name year

        this must agree with DateDisplayEn's "formats" definition
        (it may be overridden if a locale-specific date displayer exists)
        """

        _ = self._locale.translation.sgettext
        year = self._slash_year(date_val[2], date_val[3])
        if date_val[0] == 0:
            if date_val[1] == 0:
                return year + '.'
            else:
                return self.format_long_month_year(date_val[1], year,
                                                   inflect, long_months)
        elif date_val[1] == 0: # month is zero but day is not (see 8477)
            return self.display_iso(date_val)
        else:
            # TRANSLATORS: this month is ALREADY inflected: ignore it
            return _("{day:d} {long_month} {year}").format(
                       day = date_val[0],
                       long_month = self.format_long_month(date_val[1],
                                        inflect, long_months).replace(' .', ''),
                       year = year)

#-------------------------------------------------------------------------
#
# Register classes
#
#-------------------------------------------------------------------------
register_datehandler(('hr', 'HR', 'croatian', 'Croatian', 'hrvatski', 'hr_HR'),
                                    DateParserHR, DateDisplayHR)

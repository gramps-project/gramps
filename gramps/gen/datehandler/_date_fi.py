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
Finnish-specific classes for parsing and displaying dates.
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
# Finnish parser
#
# This handles only dates where days and months are given as numeric, as:
# - That's how they are normally used in Finland
# - Parsing Finnish is much more complicated than English
#-------------------------------------------------------------------------
class DateParserFI(DateParser):

    # NOTE: these need to be in lower case because the "key" comparison
    # is done as lower case.  In the display method correct capitalization
    # can be used.

    modifier_to_int = {
        # examples:
        # - ennen 1.1.2005
        # - noin 1.1.2005
        'ennen'   : Date.MOD_BEFORE,
        'e.'      : Date.MOD_BEFORE,
        'noin'    : Date.MOD_ABOUT,
        'n.'      : Date.MOD_ABOUT,
        }
    modifier_after_to_int = {
        # examples:
        # - 1.1.2005 jälkeen
        'jälkeen' : Date.MOD_AFTER,
        'j.'      : Date.MOD_AFTER,
        }

    bce = ["ekr.", "ekr"]

    calendar_to_int = {
        'gregoriaaninen'  : Date.CAL_GREGORIAN,
        'greg.'           : Date.CAL_GREGORIAN,
        'juliaaninen'     : Date.CAL_JULIAN,
        'jul.'            : Date.CAL_JULIAN,
        'heprealainen'    : Date.CAL_HEBREW,
        'hepr.'           : Date.CAL_HEBREW,
        'islamilainen'    : Date.CAL_ISLAMIC,
        'isl.'            : Date.CAL_ISLAMIC,
        'ranskan vallankumouksen aikainen': Date.CAL_FRENCH,
        'ranskan v.'      : Date.CAL_FRENCH,
        'persialainen'    : Date.CAL_PERSIAN,
        'pers.'           : Date.CAL_PERSIAN,
        'svensk'          : Date.CAL_SWEDISH,
        's'               : Date.CAL_SWEDISH,
        }

    quality_to_int = {
        'arviolta'   : Date.QUAL_ESTIMATED,
        'arv.'       : Date.QUAL_ESTIMATED,
        'laskettuna' : Date.QUAL_CALCULATED,
        'lask.'      : Date.QUAL_CALCULATED,
        }

    def init_strings(self):
        DateParser.init_strings(self)
        self._text2 = re.compile(r'(\d+)?\.?\s+?%s\.?\s*((\d+)(/\d+)?)?\s*$'
                                 % self._mon_str, re.IGNORECASE)
        self._span = re.compile(r"(?P<start>.+)\s+(-)\s+(?P<stop>.+)",
                                re.IGNORECASE)
        self._range = re.compile(
            r"(vuosien\s*)?(?P<start>.+)\s+ja\s+(?P<stop>.+)\s+välillä",
            re.IGNORECASE)

#-------------------------------------------------------------------------
#
# Finnish display
#
#-------------------------------------------------------------------------
class DateDisplayFI(DateDisplay):
    """
    Finnish language date display class.
    """
    _bce_str = "%s ekr."

    formats = (
        "VVVV-KK-PP (ISO)",
        "PP.KK.VVVV",
        "Päivä Kuukausi Vuosi" # Day, full month name, year
        )
        # this definition must agree with its "_display_calendar" method

    display = DateDisplay.display_formatted

    def _display_calendar(self, date_val, long_months, short_months = None,
                          inflect=""):
        # this must agree with its locale-specific "formats" definition

        if short_months is None:
            # Let the short formats work the same as long formats
            short_months = long_months

        if self.format == 0:
            return self.display_iso(date_val)
        elif self.format == 1:
            # numerical
            value = self.dd_dformat01(date_val)
        # elif self.format == 4:
        else:
            # day month_name year
            value = self.dd_dformat04(date_val, inflect, long_months)
        if date_val[2] < 0:
            # TODO fix BUG 7064: non-Gregorian calendars wrongly use BCE notation for negative dates
            return self._bce_str % value
        else:
            return value

    def dd_dformat04(self, date_val, inflect, long_months):
        """
        day month_name year -- for Finnish locale
        """
        year = self._slash_year(date_val[2], date_val[3])
        if date_val[0] == 0:
            if date_val[1] == 0:
                return year
            else:
                if inflect:
                    return self.format_long_month_year(date_val[1], year,
                                                       inflect, long_months)
                else:
                    return "{long_month.f[IN]} {year}".format(
                             long_month = long_months[date_val[1]],
                             year = year)
        else:
            if not hasattr(long_months[date_val[1]], 'f'): # not a Lexeme
                return self.dd_dformat01(date_val) # maybe the month is zero
            return "{day:d}. {long_month.f[P]} {year}".format(
                     day = date_val[0],
                     long_month = long_months[date_val[1]],
                     year = year)

#-------------------------------------------------------------------------
#
# Register classes
#
#-------------------------------------------------------------------------
register_datehandler(
    ('fi_FI', 'fi', 'finnish', 'Finnish', ('%d.%m.%Y',)),
    DateParserFI, DateDisplayFI)

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

# Italian version, 2009 (derived from the catalan version)

"""
Italian-specific classes for parsing and displaying dates.
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
# Italian parser
#
#-------------------------------------------------------------------------
class DateParserIT(DateParser):

    modifier_to_int = {
        'prima del'            : Date.MOD_BEFORE,
        'prima'                : Date.MOD_BEFORE,
        'dopo del'             : Date.MOD_AFTER,
        'dopo'                 : Date.MOD_AFTER,
        'approssimativamente'  : Date.MOD_ABOUT,
        'apross.'              : Date.MOD_ABOUT,
        'apross'               : Date.MOD_ABOUT,
        'circa il'             : Date.MOD_ABOUT,
        'circa'                : Date.MOD_ABOUT,
        'ca.'                  : Date.MOD_ABOUT,
        'ca'                   : Date.MOD_ABOUT,
        'c.'                   : Date.MOD_ABOUT,
        }

    calendar_to_int = {
        'gregoriano'    : Date.CAL_GREGORIAN,
        'g'             : Date.CAL_GREGORIAN,
        'giuliano'      : Date.CAL_JULIAN,
        'j'             : Date.CAL_JULIAN,
        'ebraico'       : Date.CAL_HEBREW,
        'e'             : Date.CAL_HEBREW,
        'islamico'      : Date.CAL_ISLAMIC,
        'i'             : Date.CAL_ISLAMIC,
        'rivoluzionario': Date.CAL_FRENCH,
        'r'             : Date.CAL_FRENCH,
        'persiano'      : Date.CAL_PERSIAN,
        'p'             : Date.CAL_PERSIAN,
        'svedese'      : Date.CAL_SWEDISH,
        's'            : Date.CAL_SWEDISH,
        }

    quality_to_int = {
        'stimata'   : Date.QUAL_ESTIMATED,
        'st.'       : Date.QUAL_ESTIMATED,
        'st'        : Date.QUAL_ESTIMATED,
        'calcolata' : Date.QUAL_CALCULATED,
        'calc.'     : Date.QUAL_CALCULATED,
        'calc'      : Date.QUAL_CALCULATED,
        }

    def init_strings(self):
        DateParser.init_strings(self)
        _span_1 = ['dal', 'da']
        _span_2 = ['al', 'a']
        _range_1 = ['tra', 'fra']
        _range_2 = ['e']
        self._span = re.compile(r"(%s)\s+(?P<start>.+)\s+(%s)\s+(?P<stop>.+)" %
                                ('|'.join(_span_1), '|'.join(_span_2)),
                                 re.IGNORECASE)
        self._range = re.compile(
            r"(%s)\s+(?P<start>.+)\s+(%s)\s+(?P<stop>.+)" %
            ('|'.join(_range_1), '|'.join(_range_2)), re.IGNORECASE)

#-------------------------------------------------------------------------
#
# Italian display
#
#-------------------------------------------------------------------------
class DateDisplayIT(DateDisplay):
    """
    Italian language date display class.
    """
    long_months = ( "", "gennaio", "febbraio", "marzo", "aprile",
                    "maggio", "giugno", "luglio", "agosto", "settembre",
                    "ottobre", "novembre", "dicembre" )

    short_months = ( "", "gen", "feb", "mar", "apr", "mag", "giu",
                     "lug", "ago", "set", "ott", "nov", "dic" )

    calendar = (
        "", "Giuliano", "Ebraico",
        "Rivoluzionario", "Persiano", "Islamico",
        "Svedese"
        )

    _mod_str = ("", "prima del ", "dopo del ", "circa il ", "", "", "")

    _qual_str = ("", "stimata ", "calcolata ")

    french = (
        '',
        'vendemmiaio',
        'brumaio',
        'frimaio',
        'nevoso',
        'piovoso',
        'ventoso',
        'germile',
        'fiorile',
        'pratile',
        'messidoro',
        'termidoro',
        'fruttidoro',
        'extra',
        )

    formats = (
        "AAAA-MM-DD (ISO)", "Numerico", "Mese Giorno Anno",
        "MES Giorno, Anno", "Giorno Mese Anno", "Giorno MES Anno"
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
            return "%s%s %s %s %s%s" % (qual_str, 'dal', d1, 'al', d2, scal)
        elif mod == Date.MOD_RANGE:
            d1 = self.display_cal[cal](start)
            d2 = self.display_cal[cal](date.get_stop_date())
            scal = self.format_extras(cal, newyear)
            return "%s%s %s %s %s%s" % (qual_str, 'tra', d1, 'e', d2, scal)
        else:
            text = self.display_cal[date.get_calendar()](start)
            scal = self.format_extras(cal, newyear)
            return "%s%s%s%s" % (qual_str, self._mod_str[mod], text, scal)

#-------------------------------------------------------------------------
#
# Register classes
#
#-------------------------------------------------------------------------
register_datehandler(
    ('it_IT', 'it', 'italian', 'Italian', 'it_CH', ('%d/%m/%Y',)),
    DateParserIT, DateDisplayIT)

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
Lithuanian-specific classes for parsing and displaying dates.
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
# Lithuanian parser
#
#-------------------------------------------------------------------------
class DateParserLT(DateParser):
    """
    Convert a text string into a Date object. If the date cannot be
    converted, the text string is assigned.
    """

    month_to_int = DateParser.month_to_int

    # Custom months not the same as long months

    month_to_int["sausis"] = 1
    month_to_int["vasaris"] = 2
    month_to_int["kovas"] = 3
    month_to_int["balandis"] = 4
    month_to_int["gegužė"] = 5
    month_to_int["gegužis"] = 5
    month_to_int["birželis"] = 6
    month_to_int["liepa"] = 7
    month_to_int["rugpjūtis"] = 8
    month_to_int["rugsėjis"] = 9
    month_to_int["spalis"] = 10
    month_to_int["lapkritis"] = 11
    month_to_int["gruodis"] = 12

    # For not full months

    month_to_int["saus"] = 1
    month_to_int["vasa"] = 2
    month_to_int["vasar"] = 2
    month_to_int["bala"] = 4
    month_to_int["balan"] = 4
    month_to_int["baland"] = 4
    month_to_int["gegu"] = 5
    month_to_int["geguž"] = 5
    month_to_int["birž"] = 6
    month_to_int["birže"] = 6
    month_to_int["biržel"] = 6
    month_to_int["liep"] = 7
    month_to_int["rugp"] = 8
    month_to_int["rugpj"] = 8
    month_to_int["rugpjū"] = 8
    month_to_int["rugpjūt"] = 8
    month_to_int["rugs"] = 9
    month_to_int["rugsė"] = 9
    month_to_int["rugsėj"] = 9
    month_to_int["rugsėjis"] = 9
    month_to_int["spal"] = 10
    month_to_int["lapk"] = 11
    month_to_int["lapkr"] = 11
    month_to_int["lapkri"] = 11
    month_to_int["lapkrit"] = 11
    month_to_int["gru"] = 12
    month_to_int["gruo"] = 12
    month_to_int["gruod"] = 12

    modifier_to_int = {
        'prieš'    : Date.MOD_BEFORE,
        'po' : Date.MOD_AFTER,
        'apie' : Date.MOD_ABOUT,
        }

    calendar_to_int = {
        'grigaliaus'   : Date.CAL_GREGORIAN,
        'g'                 : Date.CAL_GREGORIAN,
        'julijaus'            : Date.CAL_JULIAN,
        'j'                 : Date.CAL_JULIAN,
        'hebrajų'         : Date.CAL_HEBREW,
        'h'         : Date.CAL_HEBREW,
        'islamo'         : Date.CAL_ISLAMIC,
        'i'                 : Date.CAL_ISLAMIC,
        'prancūzų respublikos': Date.CAL_FRENCH,
        'r'                 : Date.CAL_FRENCH,
        'persų'             : Date.CAL_PERSIAN,
        'p'             : Date.CAL_PERSIAN,
        'švedų'      : Date.CAL_SWEDISH,
        's'            : Date.CAL_SWEDISH,
        }

    quality_to_int = {
        'apytikriai'  : Date.QUAL_ESTIMATED,
        'apskaičiuota'      : Date.QUAL_CALCULATED,
        }

    def init_strings(self):
        DateParser.init_strings(self)
        # this next RE has the (possibly-slashed) year at the string's start
        self._text2 = re.compile(
            r'((\d+)(/\d+)?)?\s+?m\.\s+%s\s*(\d+)?\s*d?\.?$'
            % self._mon_str, re.IGNORECASE)
        _span_1 = ['nuo']
        _span_2 = ['iki']
        _range_1 = ['tarp']
        _range_2 = ['ir']
        self._span = re.compile(r"(%s)\s+(?P<start>.+)\s+(%s)\s+(?P<stop>.+)" %
                                ('|'.join(_span_1), '|'.join(_span_2)),
                                re.IGNORECASE)
        self._range = re.compile(
            r"(%s)\s+(?P<start>.+)\s+(%s)\s+(?P<stop>.+)" %
            ('|'.join(_range_1), '|'.join(_range_2)), re.IGNORECASE)

#-------------------------------------------------------------------------
#
# Lithuanian displayer
#
#-------------------------------------------------------------------------
class DateDisplayLT(DateDisplay):
    """
    Lithuanian language date display class.
    """

    long_months = ( "", "sausio", "vasario", "kovo", "balandžio", "gegužės",
                    "birželio", "liepos", "rugpjūčio", "rugsėjo", "spalio",
                    "lapkričio", "gruodžio" )

    long_months_vardininkas = ( "", "sausis", "vasaris", "kovas", "balandis", "gegužė",
                    "birželis", "liepa", "rugpjūtis", "rugsėjis", "spalis",
                    "lapkritis", "gruodis" )

    short_months = ( "", "Sau", "Vas", "Kov", "Bal", "Geg", "Bir",
                     "Lie", "Rgp", "Rgs", "Spa", "Lap", "Grd" )

    calendar = (
        "", "julijaus",
        "hebrajų",
        "prancūzų respublikos",
        "persų",
        "islamo",
        "švedų"
        )

    _mod_str = ("",
        "prieš ",
        "po ",
        "apie ",
        "", "", "")

    _qual_str = ("", "apytikriai ", "apskaičiuota ")

    formats = (
        "mmmm-MM-DD (ISO)", "mmmm.MM.DD",
        "mmmm m. mėnesio diena d.", "Mėn diena, metai")
        # this definition must agree with its "_display_gregorian" method

    def _display_gregorian(self, date_val, **kwargs):
        """
        display gregorian calendar date in different format
        """
        # this must agree with its locale-specific "formats" definition
        value = self.display_iso(date_val)
        year = self._slash_year(date_val[2], date_val[3])
        if self.format == 0:
            return self.display_iso(date_val)
        elif self.format == 1:
            # numerical
            return self.dd_dformat01(date_val)
        elif self.format == 2:
            # mmmm m. mėnesio diena d. (year m. month_name day d.)
            if date_val[0] == 0:
                if date_val[1] == 0:
                    value = year
                else:
                    value = "%s m. %s" % (year, self.long_months_vardininkas[date_val[1]])
            else:
                value = "%s m. %s %d d." % (year,
                                            self.long_months[date_val[1]],
                                            date_val[0])
        elif self.format == 3:
            # month_abbreviation day, year
            if date_val[0] == 0:
                if date_val[1] == 0:
                    value = year
                else:
                    value = "%s %s" % (self.short_months[date_val[1]], year)
            else:
                value = "%s %d, %s" % (self.short_months[date_val[1]],
                                       date_val[0], year)
        if date_val[2] < 0:
            return self._bce_str % value
        else:
            return value

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
            return "%s%s %s %s %s%s" % (qual_str, 'nuo', d1, 'iki',
                                        d2, scal)
        elif mod == Date.MOD_RANGE:
            d1 = self.display_cal[cal](start)
            d2 = self.display_cal[cal](date.get_stop_date())
            scal = self.format_extras(cal, newyear)
            return "%s%s %s %s %s%s" % (qual_str, 'tarp', d1, 'ir',
                                        d2, scal)
        else:
            text = self.display_cal[date.get_calendar()](start)
            scal = self.format_extras(cal, newyear)
            return "%s%s%s%s" % (qual_str, self._mod_str[mod], text,
                                 scal)

#-------------------------------------------------------------------------
#
# Register classes
#
#-------------------------------------------------------------------------
register_datehandler(
    ('lt_LT', 'lt', 'lithuanian', 'Lithuanian', ('%Y.%m.%d',)),
    DateParserLT, DateDisplayLT)

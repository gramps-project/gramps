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
Spanish-specific classes for parsing and displaying dates.
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
# Spanish parser
#
#-------------------------------------------------------------------------
class DateParserES(DateParser):

    modifier_to_int = {
        'antes de'   : Date.MOD_BEFORE,
        'antes'      : Date.MOD_BEFORE,
        'ant.'       : Date.MOD_BEFORE,
        'ant'        : Date.MOD_BEFORE,
        'después de' : Date.MOD_AFTER,
        'después'    : Date.MOD_AFTER,
        'desp.'      : Date.MOD_AFTER,
        'desp'       : Date.MOD_AFTER,
        'aprox.'     : Date.MOD_ABOUT,
        'aprox'      : Date.MOD_ABOUT,
        'apr.'       : Date.MOD_ABOUT,
        'apr'        : Date.MOD_ABOUT,
        'circa'      : Date.MOD_ABOUT,
        'ca.'        : Date.MOD_ABOUT,
        'ca'         : Date.MOD_ABOUT,
        'c.'         : Date.MOD_ABOUT,
        'hacia'      : Date.MOD_ABOUT,
        }

    calendar_to_int = {
        'gregoriano'     : Date.CAL_GREGORIAN,
        'g'              : Date.CAL_GREGORIAN,
        'juliano'        : Date.CAL_JULIAN,
        'j'              : Date.CAL_JULIAN,
        'hebreo'         : Date.CAL_HEBREW,
        'h'              : Date.CAL_HEBREW,
        'islámico'       : Date.CAL_ISLAMIC,
        'i'              : Date.CAL_ISLAMIC,
        'revolucionario' : Date.CAL_FRENCH,
        'r'              : Date.CAL_FRENCH,
        'persa'          : Date.CAL_PERSIAN,
        'p'              : Date.CAL_PERSIAN,
        'swedish'        : Date.CAL_SWEDISH,
        's'              : Date.CAL_SWEDISH,
        }

    quality_to_int = {
        'estimado'   : Date.QUAL_ESTIMATED,
        'est.'       : Date.QUAL_ESTIMATED,
        'est'        : Date.QUAL_ESTIMATED,
        'calc.'      : Date.QUAL_CALCULATED,
        'calc'       : Date.QUAL_CALCULATED,
        'calculado'  : Date.QUAL_CALCULATED,
        }

    def init_strings(self):
        DateParser.init_strings(self)
        _span_1 = ['de']
        _span_2 = ['a']
        _range_1 = ['entre', r'ent\.', 'ent']
        _range_2 = ['y']
        self._span = re.compile(
            r"(%s)\s+(?P<start>.+)\s+(%s)\s+(?P<stop>.+)" %
            ('|'.join(_span_1), '|'.join(_span_2)), re.IGNORECASE)
        self._range = re.compile(
            r"(%s)\s+(?P<start>.+)\s+(%s)\s+(?P<stop>.+)" %
            ('|'.join(_range_1), '|'.join(_range_2)), re.IGNORECASE)

#-------------------------------------------------------------------------
#
# Spanish display
#
#-------------------------------------------------------------------------
class DateDisplayES(DateDisplay):
    """
    Spanish language date display class.
    """
    # TODO: Translate these month strings:
    long_months = ( "", "enero", "febrero", "marzo", "abril", "mayo",
                    "junio", "julio", "agosto", "septiembre", "octubre",
                    "noviembre", "diciembre" )

    short_months = ( "", "enero", "feb.", "marzo", "abr.", "mayo",
                     "jun.", "jul.", "agosto", "set.", "oct.", "nov.",
                     "dic" )

    calendar = (
        "", "Juliano", "Hebreo",
        "Revolucionario", "Persa", "Islámico",
        "Swedish"
        )

    _mod_str = ("", "antes de ", "después de ", "hacia ", "", "", "")

    _qual_str = ("", "estimado ", "calculado ")

    formats = (
        "AAAA-MM-DD (ISO)", "Numérica", "Mes Día, Año",
        "MES Día, Año", "Día Mes, Año", "Día MES, Año"
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
            return "%s%s %s %s %s%s" % (qual_str, 'de', d1, 'a', d2, scal)
        elif mod == Date.MOD_RANGE:
            d1 = self.display_cal[cal](start)
            d2 = self.display_cal[cal](date.get_stop_date())
            scal = self.format_extras(cal, newyear)
            return "%s%s %s %s %s%s" % (qual_str, 'entre', d1, 'y', d2, scal)
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
    ('es_ES', 'es', 'spanish', 'Spanish', ('%d/%m/%Y',)),
    DateParserES, DateDisplayES)

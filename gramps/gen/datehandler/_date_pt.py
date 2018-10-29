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
# Portuguese version translated by Duarte Loreto <happyguy_pt@hotmail.com>, 2007.
# Based on the Spanish file.

"""
Portuguese-specific classes for parsing and displaying dates.
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
# Portuguese parser
#
#-------------------------------------------------------------------------
class DateParserPT(DateParser):

    modifier_to_int = {
        'antes de'     : Date.MOD_BEFORE,
        'antes'        : Date.MOD_BEFORE,
        'ant.'         : Date.MOD_BEFORE,
        'ant'          : Date.MOD_BEFORE,
        'até'          : Date.MOD_BEFORE,
        'depois de'    : Date.MOD_AFTER,
        'depois'       : Date.MOD_AFTER,
        'dep.'         : Date.MOD_AFTER,
        'dep'          : Date.MOD_AFTER,
        'aprox.'       : Date.MOD_ABOUT,
        'aprox'        : Date.MOD_ABOUT,
        'apr.'         : Date.MOD_ABOUT,
        'apr'          : Date.MOD_ABOUT,
        'cerca de'     : Date.MOD_ABOUT,
        'ca.'          : Date.MOD_ABOUT,
        'ca'           : Date.MOD_ABOUT,
        'c.'           : Date.MOD_ABOUT,
        'por volta de' : Date.MOD_ABOUT,
        'por volta'    : Date.MOD_ABOUT,
        'pvd.'         : Date.MOD_ABOUT,
        }

    calendar_to_int = {
        'gregoriano'            : Date.CAL_GREGORIAN,
        'g'                     : Date.CAL_GREGORIAN,
        'juliano'               : Date.CAL_JULIAN,
        'j'                     : Date.CAL_JULIAN,
        'hebreu'                : Date.CAL_HEBREW,
        'h'                     : Date.CAL_HEBREW,
        'islâmico'              : Date.CAL_ISLAMIC,
        'i'                     : Date.CAL_ISLAMIC,
        'revolucionário'        : Date.CAL_FRENCH,
        'r'                     : Date.CAL_FRENCH,
        'persa'                 : Date.CAL_PERSIAN,
        'p'                     : Date.CAL_PERSIAN,
        'swedish'               : Date.CAL_SWEDISH,
        's'                     : Date.CAL_SWEDISH,
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
        _range_2 = ['e']
        self._span = re.compile(r"(%s)\s+(?P<start>.+)\s+(%s)\s+(?P<stop>.+)"
                                % ('|'.join(_span_1), '|'.join(_span_2)),
                                re.IGNORECASE)
        self._range = re.compile(r"(%s)\s+(?P<start>.+)\s+(%s)\s+(?P<stop>.+)"
                                 % ('|'.join(_range_1), '|'.join(_range_2)),
                                 re.IGNORECASE)

#-------------------------------------------------------------------------
#
# Portuguese display
#
#-------------------------------------------------------------------------
class DateDisplayPT(DateDisplay):
    """
    Portuguese language date display class.
    """
    long_months = ( "", "Janeiro", "Fevereiro", "Março", "Abril", "Maio",
                    "Junho", "Julho", "Agosto", "Setembro", "Outubro",
                    "Novembro", "Dezembro" )

    short_months = ( "", "Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
                     "Jul", "Ago", "Set", "Out", "Nov", "Dez" )

    calendar = (
        "", "Juliano", "Hebreu",
        "Revolucionário", "Persa", "Islâmico",
        "Sueco"
        )

    _mod_str = ("","antes de ","depois de ","por volta de ","","","")

    _qual_str = ("","estimado ","calculado ")

    formats = (
        "AAAA-MM-DD (ISO)", "Numérica", "Mês Dia, Ano",
        "MÊS Dia, Ano", "Dia Mês, Ano", "Dia MÊS, Ano"
        )
        # this must agree with DateDisplayEn's "formats" definition
        # (since no locale-specific _display_gregorian exists, here)

    def display(self,date):
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
            return "%s%s %s %s %s%s" % (qual_str, 'entre', d1, 'e', d2, scal)
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
    ('pt_PT', 'pt_PT.UTF-8', 'pt_BR', 'pt_BR.UTF-8',
     'pt' 'portuguese', 'Portuguese', ('%d-%m-%Y',)),
    DateParserPT, DateDisplayPT)

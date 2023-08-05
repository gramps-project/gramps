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

# Catalan Version, 2008

"""
Catalan-specific classes for parsing and displaying dates.
"""

# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------
import re

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ..lib.date import Date
from ._dateparser import DateParser
from ._datedisplay import DateDisplay
from ._datehandler import register_datehandler


# -------------------------------------------------------------------------
#
# Catalan parser
#
# -------------------------------------------------------------------------
class DateParserCA(DateParser):
    modifier_to_int = {
        "abans de": Date.MOD_BEFORE,
        "abans": Date.MOD_BEFORE,
        "ab.": Date.MOD_BEFORE,
        "després de": Date.MOD_AFTER,
        "després": Date.MOD_AFTER,
        "desp.": Date.MOD_AFTER,
        "desp": Date.MOD_AFTER,
        "aprox.": Date.MOD_ABOUT,
        "aprox": Date.MOD_ABOUT,
        "circa": Date.MOD_ABOUT,
        "ca.": Date.MOD_ABOUT,
        "ca": Date.MOD_ABOUT,
        "c.": Date.MOD_ABOUT,
        "cap a": Date.MOD_ABOUT,
        "al voltant": Date.MOD_ABOUT,
        "al voltant de": Date.MOD_ABOUT,
        "des de": Date.MOD_FROM,
        "fins": Date.MOD_TO,
    }

    calendar_to_int = {
        "gregorià": Date.CAL_GREGORIAN,
        "g": Date.CAL_GREGORIAN,
        "julià": Date.CAL_JULIAN,
        "j": Date.CAL_JULIAN,
        "hebreu": Date.CAL_HEBREW,
        "h": Date.CAL_HEBREW,
        "islàmic": Date.CAL_ISLAMIC,
        "i": Date.CAL_ISLAMIC,
        "revolucionari": Date.CAL_FRENCH,
        "r": Date.CAL_FRENCH,
        "persa": Date.CAL_PERSIAN,
        "p": Date.CAL_PERSIAN,
        "swedish": Date.CAL_SWEDISH,
        "s": Date.CAL_SWEDISH,
    }

    quality_to_int = {
        "estimat": Date.QUAL_ESTIMATED,
        "est.": Date.QUAL_ESTIMATED,
        "est": Date.QUAL_ESTIMATED,
        "calc.": Date.QUAL_CALCULATED,
        "calc": Date.QUAL_CALCULATED,
        "calculat": Date.QUAL_CALCULATED,
    }

    def init_strings(self):
        DateParser.init_strings(self)
        _span_1 = ["des de"]
        _span_2 = ["fins a"]
        _range_1 = ["entre", r"ent\.", "ent"]
        _range_2 = ["i"]
        self._span = re.compile(
            r"(%s)\s+(?P<start>.+)\s+(%s)\s+(?P<stop>.+)"
            % ("|".join(_span_1), "|".join(_span_2)),
            re.IGNORECASE,
        )
        self._range = re.compile(
            r"(%s)\s+(?P<start>.+)\s+(%s)\s+(?P<stop>.+)"
            % ("|".join(_range_1), "|".join(_range_2)),
            re.IGNORECASE,
        )


# -------------------------------------------------------------------------
#
# Catalan display
#
# -------------------------------------------------------------------------
class DateDisplayCA(DateDisplay):
    """
    Catalan language date display class.
    """

    long_months = (
        "",
        "Gener",
        "Febrer",
        "Març",
        "Abril",
        "Maig",
        "Juny",
        "Juliol",
        "Agost",
        "Setembre",
        "Octubre",
        "Novembre",
        "Desembre",
    )

    short_months = (
        "",
        "Gen",
        "Feb",
        "Mar",
        "Abr",
        "Mai",
        "Jun",
        "Jul",
        "Ago",
        "Set",
        "Oct",
        "Nov",
        "Des",
    )

    calendar = ("", "Julià", "Hebreu", "Revolucionari", "Persa", "Islàmic", "Suec")

    _mod_str = ("", "abans de ", "després de ", "cap a ", "", "", "")

    _qual_str = ("", "estimat ", "calculat ")

    french = (
        "",
        "Vendemiari",
        "Brumari",
        "Frimari",
        "Nivós",
        "Pluviós",
        "Ventós",
        "Germinal",
        "Floreal",
        "Pradial",
        "Messidor",
        "Termidor",
        "Fructidor",
        "Extra",
    )

    formats = (
        "AAAA-MM-DD (ISO)",
        "Numèrica",
        "Mes Dia, Any",
        "MES Dia, Any",
        "Dia Mes, Any",
        "Dia MES, Any",
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
            return "%s%s %s %s %s%s" % (qual_str, "des de", d1, "fins a", d2, scal)
        elif mod == Date.MOD_RANGE:
            d1 = self.display_cal[cal](start)
            d2 = self.display_cal[cal](date.get_stop_date())
            scal = self.format_extras(cal, newyear)
            return "%s%s %s %s %s%s" % (qual_str, "entre", d1, "i", d2, scal)
        else:
            text = self.display_cal[date.get_calendar()](start)
            scal = self.format_extras(cal, newyear)
            return "%s%s%s%s" % (qual_str, self._mod_str[mod], text, scal)


# -------------------------------------------------------------------------
#
# Register classes
#
# -------------------------------------------------------------------------
register_datehandler(
    ("ca_ES", "ca", "català", "Catalan", "ca_FR", "ca_AD", "ca_IT", ("%d/%m/%Y",)),
    DateParserCA,
    DateDisplayCA,
)

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

# Polish version 2007 by Piotr Czubaszek
# Updated in 2010 by Łukasz Rymarczyk

"""
Polish-specific classes for parsing and displaying dates.
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
# Polish parser
#
# -------------------------------------------------------------------------
class DateParserPL(DateParser):
    month_to_int = DateParser.month_to_int
    month_to_int["styczeń"] = 1
    month_to_int["sty"] = 1
    month_to_int["I"] = 1
    month_to_int["luty"] = 2
    month_to_int["lut"] = 2
    month_to_int["II"] = 2
    month_to_int["marzec"] = 3
    month_to_int["mar"] = 3
    month_to_int["III"] = 3
    month_to_int["kwiecień"] = 4
    month_to_int["kwi"] = 4
    month_to_int["IV"] = 4
    month_to_int["maj"] = 5
    month_to_int["V"] = 5
    month_to_int["czerwiec"] = 6
    month_to_int["cze"] = 6
    month_to_int["VI"] = 6
    month_to_int["lipiec"] = 7
    month_to_int["lip"] = 7
    month_to_int["VII"] = 7
    month_to_int["sierpień"] = 8
    month_to_int["sie"] = 8
    month_to_int["VIII"] = 8
    month_to_int["wrzesień"] = 9
    month_to_int["wrz"] = 9
    month_to_int["IX"] = 9
    month_to_int["październik"] = 10
    month_to_int["paź"] = 10
    month_to_int["X"] = 10
    month_to_int["listopad"] = 11
    month_to_int["lis"] = 11
    month_to_int["XI"] = 11
    month_to_int["grudzień"] = 12
    month_to_int["gru"] = 12
    month_to_int["XII"] = 12
    # Alternative forms: declined nouns
    month_to_int["stycznia"] = 1
    month_to_int["lutego"] = 2
    month_to_int["marca"] = 3
    month_to_int["kwietnia"] = 4
    month_to_int["maja"] = 5
    month_to_int["czerwca"] = 6
    month_to_int["lipca"] = 7
    month_to_int["sierpnia"] = 8
    month_to_int["września"] = 9
    month_to_int["października"] = 10
    month_to_int["listopada"] = 11
    month_to_int["grudnia"] = 12
    # Alternative forms: nouns without polish accent letters
    # (misspellings sometimes used in emails)
    month_to_int["styczen"] = 1
    month_to_int["kwiecien"] = 4
    month_to_int["sierpien"] = 8
    month_to_int["wrzesien"] = 9
    month_to_int["pazdziernik"] = 10
    month_to_int["grudzien"] = 12
    month_to_int["wrzesnia"] = 9
    month_to_int["pazdziernika"] = 10
    month_to_int["paz"] = 10

    modifier_to_int = {
        "przed": Date.MOD_BEFORE,
        "po": Date.MOD_AFTER,
        "około": Date.MOD_ABOUT,
        "ok.": Date.MOD_ABOUT,
        "circa": Date.MOD_ABOUT,
        "ca.": Date.MOD_ABOUT,
        # Alternative forms: misspellings sometimes used in emails
        "okolo": Date.MOD_ABOUT,
        "ok": Date.MOD_ABOUT,
        "od": Date.MOD_FROM,
        "do": Date.MOD_TO,
    }

    calendar_to_int = {
        "gregoriański": Date.CAL_GREGORIAN,
        "greg.": Date.CAL_GREGORIAN,
        "juliański": Date.CAL_JULIAN,
        "jul.": Date.CAL_JULIAN,
        "hebrajski": Date.CAL_HEBREW,
        "hebr.": Date.CAL_HEBREW,
        "islamski": Date.CAL_ISLAMIC,
        "isl.": Date.CAL_ISLAMIC,
        "francuski republikański": Date.CAL_FRENCH,
        "franc.": Date.CAL_FRENCH,
        "perski": Date.CAL_PERSIAN,
        "szwedzki": Date.CAL_SWEDISH,
        "s": Date.CAL_SWEDISH,
        # Alternative forms: nouns without polish accent letters
        # (misspellings sometimes used in emails)
        "gregorianski": Date.CAL_GREGORIAN,
        "julianski": Date.CAL_JULIAN,
        "francuski republikanski": Date.CAL_FRENCH,
    }

    quality_to_int = {
        "szacowany": Date.QUAL_ESTIMATED,
        "szac.": Date.QUAL_ESTIMATED,
        "obliczony": Date.QUAL_CALCULATED,
        "obl.": Date.QUAL_CALCULATED,
    }

    bce = ["przed naszą erą", "przed Chrystusem", "p.n.e."] + DateParser.bce

    def init_strings(self):
        DateParser.init_strings(self)
        self._span = re.compile(
            r"(od)\s+(?P<start>.+)\s+(do)\s+(?P<stop>.+)", re.IGNORECASE
        )
        # Also handle a common mistakes
        self._range = re.compile(
            r"((?:po)?mi(?:ę|e)dzy)\s+(?P<start>.+)\s+(a)\s+(?P<stop>.+)", re.IGNORECASE
        )
        self._text2 = re.compile(
            r"(\d+)?.?\s+?%s\s*((\d+)(/\d+)?)?" % self._mon_str, re.IGNORECASE
        )
        self._jtext2 = re.compile(
            r"(\d+)?.?\s+?%s\s*((\d+)(/\d+)?)?" % self._jmon_str, re.IGNORECASE
        )


# -------------------------------------------------------------------------
#
# Polish display
#
# -------------------------------------------------------------------------
class DateDisplayPL(DateDisplay):
    """
    Polish language date display class.
    """

    long_months = (
        "",
        "Styczeń",
        "Luty",
        "Marzec",
        "Kwiecień",
        "Maj",
        "Czerwiec",
        "Lipiec",
        "Sierpień",
        "Wrzesień",
        "Październik",
        "Listopad",
        "Grudzień",
    )

    short_months = (
        "",
        "Sty",
        "Lut",
        "Mar",
        "Kwi",
        "Maj",
        "Cze",
        "Lip",
        "Sie",
        "Wrz",
        "Paź",
        "Lis",
        "Gru",
    )

    calendar = (
        "",
        "juliański",
        "hebrajski",
        "francuski republikański",
        "perski",
        "islamski",
        "swedish",
    )

    _mod_str = ("", "przed ", "po ", "ok. ", "", "", "")

    _qual_str = ("", "szacowany ", "obliczony ")

    _bce_str = "%s p.n.e."

    formats = (
        "RRRR-MM-DD (ISO)",
        "Numeryczny",
        "Miesiąc Dzień, Rok",
        "Miesiąc.Dzień.Rok",
        "Dzień Miesiąc Rok",
        "Dzień MieRzym Rok",
    )
    # this definition must agree with its "_display_gregorian" method

    roman_months = (
        "",
        "I",
        "II",
        "III",
        "IV",
        "V",
        "VI",
        "VII",
        "VIII",
        "IX",
        "X",
        "XI",
        "XII",
    )

    def _display_gregorian(self, date_val, **kwargs):
        """
        display gregorian calendar date in different format
        """
        # this must agree with its locale-specific "formats" definition
        year = self._slash_year(date_val[2], date_val[3])
        if self.format == 0:
            return self.display_iso(date_val)
        elif self.format == 1:
            # day.month_number.year
            if date_val[3]:
                return self.display_iso(date_val)
            else:
                if date_val[0] == date_val[1] == 0:
                    value = str(date_val[2])
                else:
                    value = self.dhformat.replace("%d", str(date_val[0]))
                    value = value.replace("%m", str(date_val[1]))
                    value = value.replace("%Y", str(date_val[2]))
        elif self.format == 2:
            # month_name day, year
            if date_val[0] == 0:
                if date_val[1] == 0:
                    value = year
                else:
                    value = "%s %s" % (self.long_months[date_val[1]], year)
            else:
                value = "%s %d, %s" % (self.long_months[date_val[1]], date_val[0], year)
        elif self.format == 3:
            # month_number. day. year
            if date_val[0] == 0:
                if date_val[1] == 0:
                    value = year
                else:
                    value = "%d.%s" % (date_val[1], year)
            else:
                value = "%d.%d.%s" % (date_val[1], date_val[0], year)
        elif self.format == 4:
            # day month_name year
            if date_val[0] == 0:
                if date_val[1] == 0:
                    value = year
                else:
                    value = "%s %s" % (self.long_months[date_val[1]], year)
            else:
                value = "%d %s %s" % (date_val[0], self.long_months[date_val[1]], year)
        else:
            # day Roman_number_month year
            if date_val[0] == 0:
                if date_val[1] == 0:
                    value = year
                else:
                    value = "%s %s" % (self.roman_months[date_val[1]], year)
            else:
                value = "%d %s %s" % (date_val[0], self.roman_months[date_val[1]], year)
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
            return "%s%s %s %s %s%s" % (qual_str, "od", d1, "do", d2, scal)
        elif mod == Date.MOD_RANGE:
            d1 = self.display_cal[cal](start)
            d2 = self.display_cal[cal](date.get_stop_date())
            scal = self.format_extras(cal, newyear)
            return "%s%s %s %s %s%s" % (qual_str, "między", d1, "a", d2, scal)
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
    ("pl_PL", "polish", "Polish_Poland", "pl", ("%d.%m.%Y",)),
    DateParserPL,
    DateDisplayPL,
)

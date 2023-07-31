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

# Serbian version by Vlada Perić <vlada.peric@gmail.com>, 2009.
# Based on the Croatian DateHandler by Josip

"""
Serbian-specific classes for parsing and displaying dates.
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
# Serbian parser
#
# -------------------------------------------------------------------------
class DateParserSR(DateParser):
    """
    Converts a text string into a Date object
    """

    month_to_int = DateParser.month_to_int

    month_to_int["januar"] = 1
    month_to_int["januara"] = 1
    month_to_int["jan"] = 1
    month_to_int["јан"] = 1
    month_to_int["јануара"] = 1
    month_to_int["јануар"] = 1
    month_to_int["i"] = 1

    month_to_int["februar"] = 2
    month_to_int["februara"] = 2
    month_to_int["feb"] = 2
    month_to_int["феб"] = 2
    month_to_int["фебруар"] = 2
    month_to_int["фебруара"] = 2
    month_to_int["ii"] = 2

    month_to_int["mart"] = 3
    month_to_int["marta"] = 3
    month_to_int["mar"] = 3
    month_to_int["мар"] = 3
    month_to_int["март"] = 3
    month_to_int["марта"] = 3
    month_to_int["iii"] = 3

    month_to_int["april"] = 4
    month_to_int["aprila"] = 4
    month_to_int["apr"] = 4
    month_to_int["апр"] = 4
    month_to_int["април"] = 4
    month_to_int["априла"] = 4
    month_to_int["iv"] = 4

    month_to_int["maj"] = 5
    month_to_int["maja"] = 5
    month_to_int["мај"] = 5
    month_to_int["маја"] = 5
    month_to_int["v"] = 5

    month_to_int["jun"] = 6
    month_to_int["juna"] = 6
    month_to_int["јун"] = 6
    month_to_int["јуна"] = 6
    month_to_int["vi"] = 6

    month_to_int["jul"] = 7
    month_to_int["jula"] = 7
    month_to_int["јул"] = 7
    month_to_int["јула"] = 7
    month_to_int["vii"] = 7

    month_to_int["avgust"] = 8
    month_to_int["avgusta"] = 8
    month_to_int["avg"] = 8
    month_to_int["авг"] = 8
    month_to_int["август"] = 8
    month_to_int["августа"] = 8
    month_to_int["viii"] = 8

    month_to_int["septembar"] = 9
    month_to_int["septembra"] = 9
    month_to_int["sep"] = 9
    month_to_int["сеп"] = 9
    month_to_int["септембар"] = 9
    month_to_int["септембра"] = 9
    month_to_int["ix"] = 9

    month_to_int["oktobar"] = 10
    month_to_int["oktobra"] = 10
    month_to_int["okt"] = 10
    month_to_int["окт"] = 10
    month_to_int["октобар"] = 10
    month_to_int["октобра"] = 10
    month_to_int["x"] = 10

    month_to_int["novembar"] = 11
    month_to_int["novembra"] = 11
    month_to_int["nov"] = 11
    month_to_int["нов"] = 11
    month_to_int["новембар"] = 11
    month_to_int["новембра"] = 11
    month_to_int["xi"] = 11

    month_to_int["decembar"] = 12
    month_to_int["decembra"] = 12
    month_to_int["dec"] = 12
    month_to_int["дец"] = 12
    month_to_int["децембар"] = 12
    month_to_int["децембра"] = 12
    month_to_int["xii"] = 12

    modifier_to_int = {
        "pre": Date.MOD_BEFORE,
        "posle": Date.MOD_AFTER,
        "oko": Date.MOD_ABOUT,
        "cca": Date.MOD_ABOUT,
        "пре": Date.MOD_BEFORE,
        "после": Date.MOD_AFTER,
        "око": Date.MOD_ABOUT,
        "from": Date.MOD_FROM,
        "to": Date.MOD_TO,
    }

    calendar_to_int = {
        "gregorijanski": Date.CAL_GREGORIAN,
        "greg.": Date.CAL_GREGORIAN,
        "julijanski": Date.CAL_JULIAN,
        "jul.": Date.CAL_JULIAN,
        "hebrejski": Date.CAL_HEBREW,
        "hebr.": Date.CAL_HEBREW,
        "islamski": Date.CAL_ISLAMIC,
        "isl.": Date.CAL_ISLAMIC,
        "francuski republikanski": Date.CAL_FRENCH,
        "franc.": Date.CAL_FRENCH,
        "persijski": Date.CAL_PERSIAN,
        "pers. ": Date.CAL_PERSIAN,
        "švedski": Date.CAL_SWEDISH,
        "šv.": Date.CAL_SWEDISH,
        "грегоријански": Date.CAL_GREGORIAN,
        "грег.": Date.CAL_GREGORIAN,
        "јулијански": Date.CAL_JULIAN,
        "јул.": Date.CAL_JULIAN,
        "хебрејски": Date.CAL_HEBREW,
        "хебр.": Date.CAL_HEBREW,
        "исламски": Date.CAL_ISLAMIC,
        "исл.": Date.CAL_ISLAMIC,
        "француски републикански": Date.CAL_FRENCH,
        "франц.": Date.CAL_FRENCH,
        "персијски": Date.CAL_PERSIAN,
        "перс. ": Date.CAL_PERSIAN,
        "шведски": Date.CAL_SWEDISH,
        "шв": Date.CAL_SWEDISH,
    }

    quality_to_int = {
        "procenjeno": Date.QUAL_ESTIMATED,
        "pro.": Date.QUAL_ESTIMATED,
        "izračunato": Date.QUAL_CALCULATED,
        "izr.": Date.QUAL_CALCULATED,
        "процењено": Date.QUAL_ESTIMATED,
        "про.": Date.QUAL_ESTIMATED,
        "приближно": Date.QUAL_ESTIMATED,
        "израчунато": Date.QUAL_CALCULATED,
        "изр.": Date.QUAL_CALCULATED,
        "прорачунато": Date.QUAL_CALCULATED,
    }

    bce = [
        "пре нове ере",
        "пре Христа",
        "п.н.е." "pre nove ere",
        "pre Hrista",
        "p.n.e.",
    ] + DateParser.bce

    def init_strings(self):
        """
        compiles regular expression strings for matching dates
        """
        DateParser.init_strings(self)
        # match 'Day. MONTH year.' format with or without dots
        self._text2 = re.compile(
            r"(\d+)?\.?\s*?%s\s*((\d+)(/\d+)?)?\.?\s*$" % self._mon_str, re.IGNORECASE
        )

        # match Day.Month.Year.
        self._numeric = re.compile(r"((\d+)[/\. ])?\s*((\d+)[/\.])?\s*(\d+)\.?$")

        _span_1 = ["od", "од", "из"]
        _span_2 = ["do", "до"]
        _range_1 = ["između", "између"]
        _range_2 = ["i", "и"]
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
# Serbian display
#
# -------------------------------------------------------------------------
class DateDisplaySR_Base(DateDisplay):
    """
    Serbian (base) date display class
    """

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
            # day.month_number.year.
            if date_val[3]:
                return self.display_iso(date_val)
            else:
                if date_val[0] == 0 and date_val[1] == 0:
                    value = str(date_val[2])
                else:
                    value = self.dhformat.replace("%m", str(date_val[1]))
                    value = value.replace("%d", str(date_val[0]))
                    value = value.replace("%Y", str(abs(date_val[2])))
                    # some locale magic already provides the right separator
                    # value = value.replace('/', '.')
        elif self.format == 2:
            # day. month_abbreviation year.
            if date_val[0] == 0:
                if date_val[1] == 0:
                    value = "%s." % year
                else:
                    value = "%s %s." % (self.short_months[date_val[1]], year)
            else:
                value = "%d. %s %s." % (
                    date_val[0],
                    self.short_months[date_val[1]],
                    year,
                )
        elif self.format == 3:
            # day. month_name year.
            if date_val[0] == 0:
                if date_val[1] == 0:
                    value = "%s." % year
                else:
                    value = "%s %s." % (self.long_months[date_val[1]], year)
            else:
                value = "%d. %s %s." % (
                    date_val[0],
                    self.long_months[date_val[1]],
                    year,
                )
        else:
            # day. Roman_number_month year.
            if date_val[0] == 0:
                if date_val[1] == 0:
                    value = "%s." % year
                else:
                    value = "%s %s." % (self.roman_months[date_val[1]], year)
            else:
                value = "%d. %s %s." % (
                    date_val[0],
                    self.roman_months[date_val[1]],
                    year,
                )
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
        span1 = self._span1
        span2 = self._span2
        range1 = self._range1
        range2 = self._range2

        if mod == Date.MOD_TEXTONLY:
            return date.get_text()
        elif start == Date.EMPTY:
            return ""
        elif mod == Date.MOD_SPAN:
            d_1 = self.display_cal[cal](start)
            d_2 = self.display_cal[cal](date.get_stop_date())
            scal = self.format_extras(cal, newyear)
            return "%s%s %s %s %s%s" % (qual_str, span1, d_1, span2, d_2, scal)
        elif mod == Date.MOD_RANGE:
            d_1 = self.display_cal[cal](start)
            d_2 = self.display_cal[cal](date.get_stop_date())
            scal = self.format_extras(cal, newyear)
            return "%s%s %s %s %s%s" % (qual_str, range1, d_1, range2, d_2, scal)
        else:
            text = self.display_cal[date.get_calendar()](start)
            scal = self.format_extras(cal, newyear)
            return "%s%s%s%s" % (qual_str, self._mod_str[mod], text, scal)


class DateDisplaySR_Latin(DateDisplaySR_Base):
    """
    Serbian (Latin) date display class
    """

    long_months = (
        "",
        "januara",
        "februara",
        "marta",
        "aprila",
        "maja",
        "juna",
        "jula",
        "avgusta",
        "septembra",
        "oktobra",
        "novembra",
        "decembra",
    )

    short_months = (
        "",
        "jan",
        "feb",
        "mar",
        "apr",
        "maj",
        "jun",
        "jul",
        "avg",
        "sep",
        "okt",
        "nov",
        "dec",
    )

    calendar = (
        "",
        "julijanski",
        "hebrejski",
        "francuski republikanski",
        "persijski",
        "islamski",
        "švedski",
    )

    _mod_str = ("", "pre ", "posle ", "oko ", "", "", "")

    _qual_str = ("", "procenjeno ", "izračunato ")

    _bce_str = "%s p.n.e."

    formats = (
        "GGGG-MM-DD (ISO-8601)",
        "Numerički (DD.MM.GGGG.)",
        "D. MMM GGGG.",
        "D. Mesec GGGG.",
        "D. Rb GGGG.",
    )
    # this definition must agree with its "_display_gregorian" method

    _span1 = "od"
    _span2 = "do"
    _range1 = "između"
    _range2 = "i"


class DateDisplaySR_Cyrillic(DateDisplaySR_Base):
    """
    Serbian (Cyrillic) date display class
    """

    long_months = (
        "",
        "Јануар",
        "Фебруар",
        "Март",
        "Април",
        "Мај",
        "Јуне",
        "Јули",
        "Аугуст",
        "Септембар",
        "Оцтобер",
        "Новембер",
        "Децембар",
    )

    short_months = (
        "",
        "Јан",
        "Феб",
        "Мар",
        "Апр",
        "Мај",
        "Јун",
        "Јул",
        "Авг",
        "Сеп",
        "Окт",
        "Нов",
        "Дец",
    )

    calendar = (
        "",
        "Јулиан",
        "хебрејски",
        "француски републиканац",
        "Персиан",
        "исламски",
        "шведски",
    )

    _mod_str = ("", "пре ", "после ", "око ", "", "", "")

    _qual_str = ("", "процењено ", "израчунато ")

    _bce_str = "%s п.н.е."

    formats = (
        "ГГГГ-ММ-ДД (ISO-8601)",
        "Нумеричка (ДД.ММ.ГГГГ.)",
        "Д. МММ ГГГГ.",
        "Д. Месец ГГГГ.",
        "Д. Rb ГГГГ.",
    )
    # this definition must agree with its "_display_gregorian" method

    _span1 = "из"
    _span2 = "до"
    _range1 = "између"
    _range2 = "и"


# -------------------------------------------------------------------------
#
# Register classes
#
# -------------------------------------------------------------------------
register_datehandler(
    (
        "sr_RS.utf8@latin",
        "srpski",
        "Srpski",
        "sr_Latn",
        "sr_Latn_RS",
        "sr_RS@latin",
        ("%d.%m.%Y.",),
    ),
    DateParserSR,
    DateDisplaySR_Latin,
)
register_datehandler(
    (
        "sr_RS",
        "sr",
        "sr_Cyrl",
        "sr_Cyrl_RS",
        "српски",
        "Српски",
        "serbian",
        ("%d.%m.%Y.",),
    ),
    DateParserSR,
    DateDisplaySR_Cyrillic,
)

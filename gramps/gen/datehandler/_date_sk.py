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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

"""
Slovak-specific classes for parsing and displaying dates.
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
# Slovak parser
#
# -------------------------------------------------------------------------
class DateParserSK(DateParser):
    modifier_to_int = {
        "pred": Date.MOD_BEFORE,
        "po": Date.MOD_AFTER,
        "okolo": Date.MOD_ABOUT,
        "asi": Date.MOD_ABOUT,
        "približne": Date.MOD_ABOUT,
        "priblizne": Date.MOD_ABOUT,
        "pribl.": Date.MOD_ABOUT,
        "pribl": Date.MOD_ABOUT,
        "circa": Date.MOD_ABOUT,
        "cca": Date.MOD_ABOUT,
        "cca.": Date.MOD_ABOUT,
        "c.": Date.MOD_ABOUT,
        "od": Date.MOD_FROM,
        "do": Date.MOD_TO,
    }

    quality_to_int = {
        "odhadovaný": Date.QUAL_ESTIMATED,
        "odhadovaná": Date.QUAL_ESTIMATED,
        "odhadované": Date.QUAL_ESTIMATED,
        "odhadovany": Date.QUAL_ESTIMATED,
        "odhadovana": Date.QUAL_ESTIMATED,
        "odhadovane": Date.QUAL_ESTIMATED,
        "odh.": Date.QUAL_ESTIMATED,
        "odh": Date.QUAL_ESTIMATED,
        "vypočítaný": Date.QUAL_CALCULATED,
        "vypočítaná": Date.QUAL_CALCULATED,
        "vypočítané": Date.QUAL_CALCULATED,
        "vypocitany": Date.QUAL_CALCULATED,
        "vypocitana": Date.QUAL_CALCULATED,
        "vypocitane": Date.QUAL_CALCULATED,
        "vyp.": Date.QUAL_CALCULATED,
        "vyp": Date.QUAL_CALCULATED,
    }

    bce = [
        "pred naším letopočtom",
        "pred nasim letopoctom",
        "pred Kristom",
        "pred Kr.",
        "pred n. l.",
        "pred n.l.",
        "pr. n. l.",
        "pr.n.l.",
        "p. n. l.",
        "p.n.l.",
    ] + DateParser.bce

    def dhformat_changed(self):
        """Allow overriding so a subclass can modify it"""
        self.dhformat = self.dhformat.replace("/", "")

    def init_strings(self):
        """
        This method compiles regular expression strings for matching dates.

        Most of the re's in most languages can stay as is. span and range
        most likely will need to change. Whatever change is done, this method
        may be called first as DateParser.init_strings(self) so that the
        invariant expresions don't need to be repeatedly coded. All differences
        can be coded after DateParser.init_strings(self) call is made.
        """
        DateParser.init_strings(self)
        self._text2 = re.compile(
            r"(\d+)?\.?\s*?%s\.?\s*((\d+)(/\d+)?)?\s*\.?$" % self._mon_str,
            re.IGNORECASE,
        )
        self._jtext2 = re.compile(
            r"(\d+)?\.?\s*?%s\.?\s*((\d+)(/\d+)?)?\s*\.?$" % self._jmon_str,
            re.IGNORECASE,
        )
        self._numeric = re.compile(r"((\d+)[/\. ])\s*((\d+)[/\. ])\s*(\d+)\.?$")
        _span_1 = ["od"]
        _span_2 = ["do"]
        _range_1 = ["medzi"]
        _range_2 = ["a"]
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
# Slovak display
#
# -------------------------------------------------------------------------
class DateDisplaySK(DateDisplay):
    """
    Slovak language date display class.
    """

    _bce_str = "%s pred n. l."

    display = DateDisplay.display_formatted

    def formats_changed(self):
        """Allow overriding so a subclass can modify"""
        self.dhformat = self.dhformat.replace("/", "")

    def dd_dformat04(self, date_val, inflect, long_months):
        """
        day month_name year

        this must agree with DateDisplayEn's "formats" definition
        (it may be overridden if a locale-specific date displayer exists)

        Month case follows .po lexemes N/G/L/I via ``inflect`` (from, to,
        between, and, before, after, about, estimated, calculated).
        A bare day+month+year uses genitive (G).
        """
        year = self._slash_year(date_val[2], date_val[3])
        if date_val[0] == 0:
            if date_val[1] == 0:
                return self._get_localized_year(year)
            else:
                return self.format_long_month_year(
                    date_val[1], year, inflect, long_months
                )
        elif date_val[1] == 0:  # month is zero but day is not (see 8477)
            return self.display_iso(date_val)
        elif not hasattr(long_months[date_val[1]], "forms"):  # not a Lexeme
            return "{day:d}. {long_month} {year}".format(
                day=date_val[0], long_month=long_months[date_val[1]], year=year
            )
        else:
            # All non-empty inflect keys use FORMATS_* from DateDisplay / .po
            if inflect:
                long_month = self.format_long_month(date_val[1], inflect, long_months)
            else:
                long_month = "{long_month.forms[G]}".format(
                    long_month=long_months[date_val[1]]
                )
            return "{day:d}. {long_month} {year}".format(
                day=date_val[0], long_month=long_month, year=year
            )

    def dd_dformat05(self, date_val, inflect, short_months):
        """
        day month_abbreviation year

        this must agree with DateDisplayEn's "formats" definition
        (it may be overridden if a locale-specific date displayer exists)

        Month case follows .po lexemes N/G/L/I via ``inflect``; bare date
        uses genitive (G).
        """
        year = self._slash_year(date_val[2], date_val[3])
        if date_val[0] == 0:
            if date_val[1] == 0:
                return self._get_localized_year(year)
            else:
                return self.format_short_month_year(
                    date_val[1], year, inflect, short_months
                )
        elif date_val[1] == 0:  # month is zero but day is not (see 8477)
            return self.display_iso(date_val)
        elif not hasattr(short_months[date_val[1]], "forms"):  # not a Lexeme
            return "{day:d}. {short_month} {year}".format(
                day=date_val[0], short_month=short_months[date_val[1]], year=year
            )
        else:
            if inflect:
                short_month = self.format_short_month(
                    date_val[1], inflect, short_months
                )
            else:
                short_month = "{short_month.forms[G]}".format(
                    short_month=short_months[date_val[1]]
                )
            return "{day:d}. {short_month} {year}".format(
                day=date_val[0], short_month=short_month, year=year
            )


# -------------------------------------------------------------------------
#
# Register classes
#
# -------------------------------------------------------------------------
register_datehandler(
    ("sk_SK", "sk", "SK", "Slovak", ("%d.%m.%Y",)),
    DateParserSK,
    DateDisplaySK,
)


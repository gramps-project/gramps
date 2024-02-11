# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2006  Donald N. Allingham
# Copyright (C) 2015       Lajos Nemeséri <nemeseril@gmail.com>
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
Hungarian-specific classes for parsing and displaying dates.
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
# Hungarian parser
#
#
# -------------------------------------------------------------------------
class DateParserHU(DateParser):
    month_to_int = DateParser.month_to_int

    month_to_int["-"] = 0  # to make the Zero month to work

    month_to_int["január"] = 1
    month_to_int["jan"] = 1
    month_to_int["jan."] = 1
    month_to_int["I"] = 1
    #    month_to_int["i"] = 1

    month_to_int["február"] = 2
    month_to_int["feb"] = 2
    month_to_int["feb."] = 2
    month_to_int["II"] = 2
    #    month_to_int["ii"] = 2

    month_to_int["március"] = 3
    month_to_int["márc"] = 3
    month_to_int["márc."] = 3
    month_to_int["III"] = 3
    #    month_to_int["iii"] = 3

    month_to_int["április"] = 4
    month_to_int["ápr"] = 4
    month_to_int["ápr."] = 4
    month_to_int["IV"] = 4
    #    month_to_int["iv"] = 4

    month_to_int["május"] = 5
    month_to_int["máj"] = 5
    month_to_int["máj."] = 5
    month_to_int["V"] = 5
    #    month_to_int["v"] = 5

    month_to_int["június"] = 6
    month_to_int["jún"] = 6
    month_to_int["jún."] = 6
    month_to_int["VI"] = 6
    #    month_to_int["vi"] = 6

    month_to_int["július"] = 7
    month_to_int["júl"] = 7
    month_to_int["júl."] = 7
    month_to_int["VII"] = 7
    #    month_to_int["vii"] = 7

    month_to_int["augusztus"] = 8
    month_to_int["aug"] = 8
    month_to_int["aug."] = 8
    month_to_int["VIII"] = 8
    #    month_to_int["viii"] = 8

    month_to_int["szeptember"] = 9
    month_to_int["szept"] = 9
    month_to_int["szept."] = 9
    month_to_int["IX"] = 9
    #    month_to_int["ix"] = 9

    month_to_int["október"] = 10
    month_to_int["okt"] = 10
    month_to_int["okt."] = 10
    month_to_int["X"] = 10
    #    month_to_int["x"] = 10

    month_to_int["november"] = 11
    month_to_int["nov"] = 11
    month_to_int["nov."] = 11
    month_to_int["XI"] = 11
    #    month_to_int["xi"] = 11

    month_to_int["december"] = 12
    month_to_int["dec"] = 12
    month_to_int["dec."] = 12
    month_to_int["XII"] = 12
    #    month_to_int["xii"] = 12

    # -----------------------------------------------------------------------
    #
    #  Alternative and latin names - not verified
    #
    # -----------------------------------------------------------------------
    # Other common latin names

    #    month_to_int["januaris"] = 01
    #    month_to_int["januarii"] = 01
    #    month_to_int["januarius"] = 01
    #    month_to_int["februaris"] = 02
    #    month_to_int["februarii"] = 02
    #    month_to_int["februarius"] = 02
    #    month_to_int["martii"] = 03
    #    month_to_int["martius"] = 03
    #    month_to_int["aprilis"] = 04
    #    month_to_int["maius"] = 05
    #    month_to_int["maii"] = 05
    #    month_to_int["junius"] = 06
    #    month_to_int["junii"] = 06
    #    month_to_int["julius"] = 07
    #    month_to_int["julii"] = 07
    #    month_to_int["augustus"] = 08
    #    month_to_int["augusti"] = 08
    #    month_to_int["septembris"] = 09
    #    month_to_int["7bris"] = 09
    #    month_to_int["september"] = 09
    #    month_to_int["october"] = 10
    #    month_to_int["octobris"] = 10
    #    month_to_int["8bris"] = 10
    #    month_to_int["novembris"] = 11
    #    month_to_int["9bris"] = 11
    #    month_to_int["november"] = 11
    #    month_to_int["decembris"] = 12
    #    month_to_int["10bris"] = 12
    #    month_to_int["xbris"] = 12
    #    month_to_int["december"] = 12

    # old Hungarian names

    #    month_to_int["Boldogasszony hava"] = 01
    #    month_to_int["Fergeteg hava"] = 01
    #    month_to_int["Böjtelő hava"] = 02
    #    month_to_int["Jégbontó hava"] = 02
    #    month_to_int["Böjtmás hava"] = 03
    #    month_to_int["Kikelet hava"] = 03
    #    month_to_int["Szent György hava"] = 04
    #    month_to_int["Szelek hava"] = 04
    #    month_to_int["Pünkösd hava"] = 05
    #    month_to_int["Ígéret hava"] = 05
    #    month_to_int["Szent Iván hava"] = 06
    #    month_to_int["Napisten hava"] = 06
    #    month_to_int["Szent Jakab hava"] = 07
    #    month_to_int["Áldás hava"] = 07
    #    month_to_int["Kisasszony hava"] = 08
    #    month_to_int["Újkenyér hava"] = 08
    #    month_to_int["Szent Mihály hava"] = 09
    #    month_to_int["Földanya hava"] = 09
    #    month_to_int["Mindszent hava"] = 10
    #    month_to_int["Magvető hava"] = 10
    #    month_to_int["Szent András hava"] = 11
    #    month_to_int["Enyészet hava"] = 11
    #    month_to_int["Karácsony hava"] = 12
    #    month_to_int["Álom hava"] = 12

    modifier_to_int = {
        "előtt": Date.MOD_BEFORE,
        "körül": Date.MOD_ABOUT,
        "után": Date.MOD_AFTER,
        "-tól": Date.MOD_FROM,
        "-ig": Date.MOD_TO,
    }

    quality_to_int = {
        "becsült": Date.QUAL_ESTIMATED,
        "hozzávetőleg": Date.QUAL_ESTIMATED,
        "becs.": Date.QUAL_ESTIMATED,
        "számított": Date.QUAL_CALCULATED,
        "körülbelül": Date.QUAL_ESTIMATED,
        "számolt": Date.QUAL_CALCULATED,
        "szám.": Date.QUAL_CALCULATED,
    }

    bce = [
        "időszámításunk előtt",
        "időszámítás előtt",
        "i. e.",
        "Krisztus előtt",
        "Krisztus előtti",
        "Kr. e.",
    ] + DateParser.bce

    calendar_to_int = {
        "Gergely": Date.CAL_GREGORIAN,
        "Julián": Date.CAL_JULIAN,
        "julián": Date.CAL_JULIAN,
        "héber": Date.CAL_HEBREW,
        "iszlám": Date.CAL_ISLAMIC,
        "francia köztársasági": Date.CAL_FRENCH,
        "perzsa": Date.CAL_PERSIAN,
        "svéd": Date.CAL_SWEDISH,
    }

    def init_strings(self):
        # Compiles regular expression strings for matching dates
        DateParser.init_strings(self)

        self._numeric = re.compile(r"((\d+)[/\.])?\s*((\d+)[/\.])?\s*(\d+)[/\. ]?$")
        # this next RE has the (possibly-slashed) year at the string's start
        self._text2 = re.compile(
            r"((\d+)(/\d+)?\.)?\s+?%s\.?\s*(\d+\.)?\s*$" % self._mon_str, re.IGNORECASE
        )
        _span_1 = [r"-tó\(ő\)l", "-tól", "-től"]
        _span_2 = ["-ig"]
        _range_1 = ["és"]
        _range_2 = ["között"]
        self._span = re.compile(
            r"(?P<start>.+)(%s)\s+(?P<stop>.+)(%s)"
            % ("|".join(_span_1), "|".join(_span_2)),
            re.IGNORECASE,
        )
        self._range = re.compile(
            r"(?P<start>.+)\s+(%s)\s+(?P<stop>.+)\s+(%s)"
            % ("|".join(_range_1), "|".join(_range_2)),
            re.IGNORECASE,
        )

    def _get_int(self, val):
        """
        Convert the string to an integer if the value is not None. If the
        value is None, a zero is returned
        """
        if val is None:
            return 0
        else:
            return int(val.replace(".", ""))


# -------------------------------------------------------------------------
#
# Hungarian display
#
# -------------------------------------------------------------------------
class DateDisplayHU(DateDisplay):
    """
    Hungarian language date display class.
    """

    _bce_str = "i. e. %s"

    roman_months = (
        "-.",
        "I.",
        "II.",
        "III.",
        "IV.",
        "V.",
        "VI.",
        "VII.",
        "VIII.",
        "IX.",
        "X.",
        "XI.",
        "XII.",
    )

    formats = (
        "ÉÉÉÉ-HH-NN (ISO)",  # 0
        "Alapértelmezett éééé. hh. nn.",  # 1
        "Év hónap nap",  # year, full month name, day     # 2
        "Év hó nap",  # year, short month name, day     # 3
        "Év római h.sz. nap",  # year, Roman number, day  # 4
    )
    # this definition must agree with its "_display_calendar" method

    display = DateDisplay.display_formatted

    def _display_calendar(self, date_val, long_months, short_months=None, inflect=""):
        # this must agree with its locale-specific "formats" definition

        year = self._slash_year(date_val[2], date_val[3])

        if short_months is None:
            # Let the short formats work the same as long formats
            short_months = long_months

        if self.format == 0:
            return self.display_iso(date_val)

        elif self.format == 1:
            # Base defined Hungarian form
            if date_val[3]:
                return self.display_iso(date_val)
            else:
                if date_val[0] == 0:  # No day
                    if date_val[1] == 0:  # No month -> year
                        value = "%s" % year
                    else:
                        value = "%s. %02d." % (
                            year,
                            date_val[1],
                        )  # If no day -> year, month
                else:
                    value = "%s. %02d. %02d." % (year, date_val[1], date_val[0])

        elif self.format == 2:
            # year, full month name, day

            if date_val[0] == 0:
                if date_val[1] == 0:
                    value = "%s" % year
                else:
                    value = "%s. %s" % (
                        year,
                        self.long_months[date_val[1]],
                    )  # If no day -> year, month
            else:
                if date_val[1] == 0:
                    value = "%s. %s %02d." % (
                        year,
                        "-",
                        date_val[0],
                    )  # To indicate somehow if the month is missing
                else:
                    value = "%s. %s %02d." % (
                        year,
                        self.long_months[date_val[1]],
                        date_val[0],
                    )

        elif self.format == 3:
            # year, short month name, day

            if date_val[0] == 0:
                if date_val[1] == 0:
                    value = "%s" % year
                else:
                    value = "%s. %s" % (
                        year,
                        self.short_months[date_val[1]],
                    )  # If no day -> year, month
            else:
                if date_val[1] == 0:
                    value = "%s. %s %02d." % (
                        year,
                        "-.",
                        date_val[0],
                    )  # To indicate somehow if the month is missing
                else:
                    value = "%s. %s %02d." % (
                        year,
                        self.short_months[date_val[1]],
                        date_val[0],
                    )

        elif self.format == 4:
            # year, Roman number, day

            if date_val[0] == 0:
                if date_val[1] == 0:
                    value = "%s" % year
                else:
                    value = "%s. %s" % (
                        year,
                        self.roman_months[date_val[1]],
                    )  # If no day -> year, month
            else:
                value = "%s. %s %02d." % (
                    year,
                    self.roman_months[date_val[1]],
                    date_val[0],
                )

        else:
            # day month_name year
            value = self.dd_dformat04(date_val, inflect, long_months)

        if date_val[2] < 0:
            # TODO fix BUG 7064: non-Gregorian calendars wrongly use BCE notation for negative dates
            return self._bce_str % value
        else:
            return value


# -------------------------------------------------------------------------
#
# Register classes
#
# -------------------------------------------------------------------------
register_datehandler(
    ("hu_HU", "hu", "hungarian", "Hungarian", "magyar", ("%Y-%m-%d",)),
    DateParserHU,
    DateDisplayHU,
)

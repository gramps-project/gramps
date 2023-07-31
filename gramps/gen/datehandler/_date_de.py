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
German-specific classes for parsing and displaying dates.
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
# German parser
#
# -------------------------------------------------------------------------
class DateParserDE(DateParser):
    month_to_int = DateParser.month_to_int
    # Always add german and austrian name variants no matter what the current
    # locale is
    month_to_int["januar"] = 1
    month_to_int["jan"] = 1
    month_to_int["jänner"] = 1
    month_to_int["jän"] = 1

    # Add other common latin,

    month_to_int["januaris"] = 1
    month_to_int["ianarius"] = 1
    month_to_int["januarii"] = 1
    month_to_int["januarius"] = 1
    month_to_int["january"] = 1
    month_to_int["ianuary"] = 1
    month_to_int["mensis"] = 1
    month_to_int["februaris"] = 2
    month_to_int["februarii"] = 2
    month_to_int["februarius"] = 2
    month_to_int["february"] = 2
    month_to_int["martii"] = 3
    month_to_int["martius"] = 3
    month_to_int["martij"] = 3
    month_to_int["marty"] = 3
    month_to_int["aprilis"] = 4
    month_to_int["maius"] = 5
    month_to_int["majus"] = 5
    month_to_int["maii"] = 5
    month_to_int["maij"] = 5
    month_to_int["may"] = 5
    month_to_int["junius"] = 6
    month_to_int["iunius"] = 6
    month_to_int["junii"] = 6
    month_to_int["iunius"] = 6
    month_to_int["junij"] = 6
    month_to_int["iunij"] = 6
    month_to_int["juny"] = 6
    month_to_int["iuny"] = 6
    month_to_int["julius"] = 7
    month_to_int["iulius"] = 7
    month_to_int["julii"] = 7
    month_to_int["iulii"] = 7
    month_to_int["july"] = 7
    month_to_int["iuly"] = 7
    month_to_int["quintilis"] = 7
    month_to_int["augustus"] = 8
    month_to_int["augusti"] = 8
    month_to_int["sextilis"] = 8
    month_to_int["septembris"] = 9
    month_to_int["7ber"] = 9
    month_to_int["7bris"] = 9
    month_to_int["viiber"] = 9
    month_to_int["viibris"] = 9
    month_to_int["september"] = 9
    month_to_int["october"] = 10
    month_to_int["octobris"] = 10
    month_to_int["8bris"] = 10
    month_to_int["viiiber"] = 10
    month_to_int["viiibris"] = 10
    month_to_int["novembris"] = 11
    month_to_int["9ber"] = 11
    month_to_int["9bris"] = 11
    month_to_int["ixber"] = 11
    month_to_int["ixbris"] = 11
    month_to_int["november"] = 11
    month_to_int["decembris"] = 12
    month_to_int["10bris"] = 12
    month_to_int["xbris"] = 12
    month_to_int["december"] = 12

    # local and historical variants

    month_to_int["jenner"] = 1
    month_to_int["feber"] = 2
    month_to_int["merz"] = 3
    month_to_int["augst"] = 8
    month_to_int["7ber"] = 9
    month_to_int["8ber"] = 10
    month_to_int["9ber"] = 11
    month_to_int["10ber"] = 12
    month_to_int["xber"] = 12

    # old german names

    month_to_int["hartung"] = 1
    month_to_int["hartmonat"] = 1
    month_to_int["hartmond"] = 1
    month_to_int["eismond"] = 1
    month_to_int["eismonat"] = 1
    month_to_int["lassmonat"] = 1
    month_to_int["wolfsmonat"] = 1
    month_to_int["wintermonat"] = 1
    month_to_int["hornung"] = 2
    month_to_int["hintester"] = 2
    month_to_int["sporkel"] = 2
    month_to_int["spörkel"] = 2
    month_to_int["rebmonat"] = 2
    month_to_int["schmelzmond"] = 2
    month_to_int["taumond"] = 2
    month_to_int["narrenmond"] = 2
    month_to_int["rebmond"] = 2
    month_to_int["letzter Wintermonat"] = 2
    month_to_int["lenzing"] = 3
    month_to_int["lenzmond"] = 3
    month_to_int["lenzmonat"] = 3
    month_to_int["frühlingsmonat"] = 3
    month_to_int["launing"] = 4
    month_to_int["grasmond"] = 4
    month_to_int["ostermond"] = 4
    month_to_int["ostermonat"] = 4
    month_to_int["beuet"] = 5
    month_to_int["blühmond"] = 5
    month_to_int["winnemond"] = 5
    month_to_int["wonnemond"] = 5
    month_to_int["wonnemonat"] = 5
    month_to_int["weidenmonat"] = 5
    month_to_int["blumenmond"] = 5
    month_to_int["brachet"] = 6
    month_to_int["brachmond"] = 6
    month_to_int["brachmonat"] = 6
    month_to_int["johannismond"] = 6
    month_to_int["weidemaent"] = 6
    month_to_int["heuet"] = 7
    month_to_int["heuert"] = 7
    month_to_int["heumond"] = 7
    month_to_int["heumonat"] = 7
    month_to_int["bärenmonat"] = 7
    month_to_int["honigmond"] = 7
    month_to_int["honigmonat"] = 7
    month_to_int["ernting"] = 8
    month_to_int["erntemond"] = 8
    month_to_int["bisemond"] = 8
    month_to_int["holzing"] = 9
    month_to_int["holzmond"] = 9
    month_to_int["scheiding"] = 9
    month_to_int["scheidung"] = 9
    month_to_int["erster herbstmond"] = 9
    month_to_int["herbstmonat"] = 9
    month_to_int["engelmonat"] = 9
    month_to_int["gilbhard"] = 10
    month_to_int["gilbhart"] = 10
    month_to_int["weinmond"] = 10
    month_to_int["weinmonat"] = 10
    month_to_int["zweiter herbstmond"] = 10
    month_to_int["windmond"] = 11
    month_to_int["windmonat"] = 11
    month_to_int["nebelung"] = 11
    month_to_int["nebelmond"] = 11
    month_to_int["schlachtmond"] = 11
    month_to_int["wintermond"] = 11
    month_to_int["dritter herbstmond"] = 11
    month_to_int["julmond"] = 12
    month_to_int["heilmond"] = 12
    month_to_int["christmond"] = 12
    month_to_int["christmonat"] = 12
    month_to_int["dustermond"] = 12
    month_to_int["heiligenmonat"] = 12
    month_to_int["wendeling"] = 11

    modifier_to_int = {
        "vor": Date.MOD_BEFORE,
        "nach": Date.MOD_AFTER,
        "gegen": Date.MOD_ABOUT,
        "um": Date.MOD_ABOUT,
        "etwa": Date.MOD_ABOUT,
        "circa": Date.MOD_ABOUT,
        "ca.": Date.MOD_ABOUT,
        "von": Date.MOD_FROM,
        "bis": Date.MOD_TO,
    }

    calendar_to_int = {
        "gregorianisch": Date.CAL_GREGORIAN,
        "greg.": Date.CAL_GREGORIAN,
        "julianisch": Date.CAL_JULIAN,
        "jul.": Date.CAL_JULIAN,
        "hebräisch": Date.CAL_HEBREW,
        "hebr.": Date.CAL_HEBREW,
        "islamisch": Date.CAL_ISLAMIC,
        "isl.": Date.CAL_ISLAMIC,
        "französisch republikanisch": Date.CAL_FRENCH,
        "franz.": Date.CAL_FRENCH,
        "persisch": Date.CAL_PERSIAN,
        "schwedisch": Date.CAL_SWEDISH,
        "s": Date.CAL_SWEDISH,
    }

    quality_to_int = {
        "geschätzt": Date.QUAL_ESTIMATED,
        "gesch.": Date.QUAL_ESTIMATED,
        "errechnet": Date.QUAL_CALCULATED,
        "berechnet": Date.QUAL_CALCULATED,
        "ber.": Date.QUAL_CALCULATED,
    }

    bce = [
        "vor unserer Zeitrechnung",
        "vor unserer Zeit",
        "vor der Zeitrechnung",
        "vor der Zeit",
        "v. u. Z.",
        "v. d. Z.",
        "v.u.Z.",
        "v.d.Z.",
        "vor Christi Geburt",
        "vor Christus",
        "v. Chr.",
    ] + DateParser.bce

    def init_strings(self):
        DateParser.init_strings(self)
        self._span = re.compile(
            r"(von|vom)\s+(?P<start>.+)\s+(bis)\s+(?P<stop>.+)", re.IGNORECASE
        )
        self._range = re.compile(
            r"zwischen\s+(?P<start>.+)\s+und\s+(?P<stop>.+)", re.IGNORECASE
        )
        self._text2 = re.compile(
            r"(\d+)?.?\s+?%s\s*((\d+)(/\d+)?)?" % self._mon_str, re.IGNORECASE
        )
        self._jtext2 = re.compile(
            r"(\d+)?.?\s+?%s\s*((\d+)(/\d+)?)?" % self._jmon_str, re.IGNORECASE
        )


# -------------------------------------------------------------------------
#
# German display
#
# -------------------------------------------------------------------------
class DateDisplayDE(DateDisplay):
    """
    German language date display class.
    """

    calendar = (
        "",
        "julianisch",
        "hebräisch",
        "französisch republikanisch",
        "persisch",
        "islamisch",
        "schwedisch",
    )

    _mod_str = ("", "vor ", "nach ", "etwa ", "", "", "")

    _qual_str = ("", "geschätzt ", "errechnet ")

    _bce_str = "%s v. u. Z."

    formats = (
        "JJJJ-MM-DD (ISO)",
        "Numerisch",
        "Monat Tag Jahr",
        "MONAT Tag Jahr",
        "Tag. Monat Jahr",
        "Tag. MONAT Jahr",
        "Numerisch mit führenden Nullen",
    )
    # this definition must agree with its "_display_gregorian" method

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
                    value = self.dhformat.replace("%m", str(date_val[1]))
                    value = value.replace("%d", str(date_val[0]))
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
            # month_abbreviation day, year
            if date_val[0] == 0:
                if date_val[1] == 0:
                    value = year
                else:
                    value = "%s %s" % (self.short_months[date_val[1]], year)
            else:
                value = "%s %d, %s" % (
                    self.short_months[date_val[1]],
                    date_val[0],
                    year,
                )
        elif self.format == 4:
            # day. month_name year
            if date_val[0] == 0:
                if date_val[1] == 0:
                    value = year
                else:
                    value = "%s %s" % (self.long_months[date_val[1]], year)
            else:
                value = "%d. %s %s" % (date_val[0], self.long_months[date_val[1]], year)
        elif self.format == 6:
            # day.month_number.year with leading zeros
            if date_val[3]:
                return self.display_iso(date_val)
            else:
                if date_val[0] == date_val[1] == 0:
                    value = str(date_val[2])
                else:
                    value = self.dhformat.replace("%m", str(date_val[1]).zfill(2))
                    value = value.replace("%d", str(date_val[0]).zfill(2))
                    value = value.replace("%Y", str(date_val[2]))
        else:
            # day. month_abbreviation year
            if date_val[0] == 0:
                if date_val[1] == 0:
                    value = year
                else:
                    value = "%s %s" % (self.short_months[date_val[1]], year)
            else:
                value = "%d. %s %s" % (
                    date_val[0],
                    self.short_months[date_val[1]],
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

        if mod == Date.MOD_TEXTONLY:
            return date.get_text()
        elif start == Date.EMPTY:
            return ""
        elif mod == Date.MOD_SPAN:
            d1 = self.display_cal[cal](start)
            d2 = self.display_cal[cal](date.get_stop_date())
            scal = self.format_extras(cal, newyear)
            return "%s%s %s %s %s%s" % (qual_str, "von", d1, "bis", d2, scal)
        elif mod == Date.MOD_RANGE:
            d1 = self.display_cal[cal](start)
            d2 = self.display_cal[cal](date.get_stop_date())
            scal = self.format_extras(cal, newyear)
            return "%szwischen %s und %s%s" % (qual_str, d1, d2, scal)
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
    (
        "de_DE",
        "german",
        "German",
        "de_CH",
        "de_LI",
        "de_LU",
        "de_BE",
        "de",
        ("%d.%m.%Y",),
    ),
    DateParserDE,
    DateDisplayDE,
)
register_datehandler(("de_AT", ("%d.%m.%Y",)), DateParserDE, DateDisplayDE)

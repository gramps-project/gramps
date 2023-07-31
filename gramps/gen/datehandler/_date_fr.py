#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2006  Donald N. Allingham
# Copyright (C) 2012       Mathieu MD
# Copyright (C) 2023       Christophe aka khrys63
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
French-specific classes for parsing and displaying dates.
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
# French parser
#
# -------------------------------------------------------------------------
class DateParserFR(DateParser):
    """
    Convert a text string into a Date object. If the date cannot be
    converted, the text string is assigned.
    """

    month_to_int = DateParser.month_to_int

    modifier_to_int = {
        "avant": Date.MOD_BEFORE,
        "av.": Date.MOD_BEFORE,
        # u'av'     : Date.MOD_BEFORE, # Broke Hebrew "Av" month name
        # u'<'      : Date.MOD_BEFORE, # Worrying about XML/HTML parsing
        "après": Date.MOD_AFTER,
        "ap.": Date.MOD_AFTER,
        "ap": Date.MOD_AFTER,
        # u'>'      : Date.MOD_AFTER, # Worrying about XML/HTML parsing
        "environ": Date.MOD_ABOUT,
        "env.": Date.MOD_ABOUT,
        "env": Date.MOD_ABOUT,
        "circa": Date.MOD_ABOUT,
        "ca.": Date.MOD_ABOUT,
        "ca": Date.MOD_ABOUT,
        "c.": Date.MOD_ABOUT,
        "vers": Date.MOD_ABOUT,
        "~": Date.MOD_ABOUT,
        "de": Date.MOD_FROM,
        "à": Date.MOD_TO,
    }

    quality_to_int = {
        "estimée": Date.QUAL_ESTIMATED,
        "est.": Date.QUAL_ESTIMATED,
        "est": Date.QUAL_ESTIMATED,
        "calculée": Date.QUAL_CALCULATED,
        "calc.": Date.QUAL_CALCULATED,
        "calc": Date.QUAL_CALCULATED,
        "comptée": Date.QUAL_CALCULATED,
        "compt.": Date.QUAL_CALCULATED,
        "compt": Date.QUAL_CALCULATED,
    }

    bce = [
        "avant le calendrier",
        "avant notre ère",
        "avant JC",
        "avant J.C",
    ] + DateParser.bce

    def init_strings(self):
        """
        This method compiles regular expression strings for matching dates.

        Most of the re's in most languages can stay as is. span and range
        most likely will need to change. Whatever change is done, this method
        may be called first as DateParser.init_strings(self) so that the
        invariant expresions don't need to be repeteadly coded. All differences
        can be coded after DateParser.init_strings(self) call, that way they
        override stuff from this method. See DateParserRU() as an example.
        """
        DateParser.init_strings(self)

        DateParser.calendar_to_int.update(
            {
                "révolutionnaire": Date.CAL_FRENCH,
                "r": Date.CAL_FRENCH,
                "perse": Date.CAL_PERSIAN,
            }
        )

        DateParser.month_to_int.update(
            {
                "januaris": 1,
                "januarii": 1,
                "januarius": 1,
                "janer": 1,
                "jänner": 1,
                "jenner": 1,
                "hartmonat": 1,
                "hartung": 1,
                "horn": 1,
                "eismond": 1,
                "februaris": 2,
                "februarii": 2,
                "februarius": 2,
                "hornig": 2,
                "hornung": 2,
                "wintermonat": 2,
                "taumond": 2,
                "narrenmond": 2,
                "martii": 3,
                "martius": 3,
                "lenzing": 3,
                "aprilis": 4,
                "ostermond": 4,
                "maius": 5,
                "maii": 5,
                "maien": 5,
                "bluviose": 5,
                "wonnemond": 5,
                "wiesenmonat": 5,
                "junius": 6,
                "junii": 6,
                "vendose": 6,
                "brachet": 6,
                "julius": 7,
                "julii": 7,
                "heuet": 7,
                "heuert": 7,
                "augustus": 8,
                "augusti": 8,
                "ernting": 8,
                "septembris": 9,
                "7bre": 9,
                "7bris": 9,
                "september": 9,
                "scheidling": 9,
                "october": 10,
                "octobris": 10,
                "8bre": 10,
                "8bris": 10,
                "gilbhard": 10,
                "november": 11,
                "novembris": 11,
                "9bre": 11,
                "9bris": 11,
                "nebelmonat": 11,
                "nebelung": 11,
                "december": 12,
                "decembris": 12,
                "10bre": 12,
                "10bris": 12,
                "xbre": 12,
                "xbris": 12,
                "julmond": 12,
                "christmond": 12,
            }
        )

        # This self._numeric is different from the base
        # avoid bug gregorian / french calendar conversion (+/-10 days)

        self._numeric = re.compile(r"((\d+)[/\. ])?\s*((\d+)[/\.])?\s*(\d+)\s*$")
        self._span = re.compile(
            r"(de)\s+(?P<start>.+)\s+(à)\s+(?P<stop>.+)", re.IGNORECASE
        )
        self._range = re.compile(
            r"(entre|ent\.|ent)\s+(?P<start>.+)\s+(et)\s+(?P<stop>.+)", re.IGNORECASE
        )

        # This self._text are different from the base
        # by adding ".?" after the first date and removing "\s*$" at the end

        # gregorian and julian

        self._text2 = re.compile(
            r"(\d+)?.?\s+?%s\s*((\d+)(/\d+)?)?" % self._mon_str, re.IGNORECASE
        )

        # hebrew

        self._jtext2 = re.compile(
            r"(\d+)?.?\s+?%s\s*((\d+)(/\d+)?)?" % self._jmon_str, re.IGNORECASE
        )

        # french

        self._ftext2 = re.compile(
            r"(\d+)?.?\s+?%s\s*((\d+)(/\d+)?)?" % self._fmon_str, re.IGNORECASE
        )

        # persian

        self._ptext2 = re.compile(
            r"(\d+)?.?\s+?%s\s*((\d+)(/\d+)?)?" % self._pmon_str, re.IGNORECASE
        )

        # islamic

        self._itext2 = re.compile(
            r"(\d+)?.?\s+?%s\s*((\d+)(/\d+)?)?" % self._imon_str, re.IGNORECASE
        )

        # swedish

        self._stext2 = re.compile(
            r"(\d+)?.?\s+?%s\s*((\d+)(/\d+)?)?" % self._smon_str, re.IGNORECASE
        )


# -------------------------------------------------------------------------
#
# French display
#
# -------------------------------------------------------------------------
class DateDisplayFR(DateDisplay):
    """
    French language date display class.
    """

    _bce_str = "%s avant le calendrier"

    def formats_changed(self):
        """Allow overriding so a subclass can modify"""

        # Replace the previous "Numérique" by a string which
        # do have an explicit meaning: "System default (format)"
        example = self.dhformat
        example = example.replace("%d", "J")
        example = example.replace("%m", "M")
        example = example.replace("%Y", "A")

        self.formats = (
            "AAAA-MM-JJ (ISO)",  # 0
            "Défaut système (" + example + ")",  # 1
            "Jour Mois Année",  # 2
            "Jour MOI Année",  # 3
            "Jour. Mois Année",  # 4
            "Jour. MOI Année",  # 5
            "Mois Jour, Année",  # 6
            "MOI Jour, Année",  # 7
            "JJ/MM/AAAA",  # 8
        )
        # this definition must agree with its "_display_gregorian" method

    def _display_gregorian(self, date_val, **kwargs):
        """
        display gregorian calendar date in different format
        """
        # this must agree with its locale-specific "formats" definition
        year = self._slash_year(date_val[2], date_val[3])
        if self.format == 0:
            # ISO

            return self.display_iso(date_val)
        elif self.format == 1:
            # numerical

            if date_val[2] < 0 or date_val[3]:
                return self.display_iso(date_val)
            else:
                if date_val[0] == date_val[1] == 0:
                    value = str(date_val[2])
                else:
                    value = self.dhformat.replace("%m", str(date_val[1]))
                    value = value.replace("%d", str(date_val[0]))

                    # base_display :
                    # value = value.replace('%Y', str(abs(date_val[2])))
                    # value = value.replace('-', '/')

                    value = value.replace("%Y", str(date_val[2]))
        elif self.format == 2:
            # day month_name year

            if date_val[0] == 0:
                if date_val[1] == 0:
                    value = year
                else:
                    value = "%s %s" % (self.long_months[date_val[1]], year)
            else:
                value = "%d %s %s" % (date_val[0], self.long_months[date_val[1]], year)
        elif self.format == 3:
            # day month_abbreviation year

            if date_val[0] == 0:
                if date_val[1] == 0:
                    value = year
                else:
                    value = "%s %s" % (self.short_months[date_val[1]], year)
            else:
                value = "%d %s %s" % (date_val[0], self.short_months[date_val[1]], year)
        elif self.format == 4:
            # day. month_name year

            if date_val[0] == 0:
                if date_val[1] == 0:
                    value = year
                else:
                    value = "%s %s" % (self.long_months[date_val[1]], year)
            else:
                # base_display :
                # value = "%d %s %s" % (date_val[0],
                #                       self.long_months[date_val[1]], year)

                value = "%d. %s %s" % (date_val[0], self.long_months[date_val[1]], year)
        elif self.format == 5:
            # day. month_abbreviation year

            if date_val[0] == 0:
                if date_val[1] == 0:
                    value = year
                else:
                    value = "%s %s" % (self.short_months[date_val[1]], year)
            else:
                # base_display :
                # value = "%d %s %s" % (date_val[0],
                #                       self.short_months[date_val[1]], year)

                value = "%d. %s %s" % (
                    date_val[0],
                    self.short_months[date_val[1]],
                    year,
                )
        elif self.format == 6:
            # month_name day, year

            if date_val[0] == 0:
                if date_val[1] == 0:
                    value = year
                else:
                    value = "%s %s" % (self.long_months[date_val[1]], year)
            else:
                value = "%s %d, %s" % (self.long_months[date_val[1]], date_val[0], year)
        elif self.format == 7:
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
        elif self.format == 8:
            # French numerical with 0

            if date_val[2] < 0 or date_val[3]:
                return self.display_iso(date_val)
            else:
                if date_val[0] == date_val[1] == 0:
                    value = str(date_val[2])
                else:
                    value = self.dhformat.replace("%m", str(date_val[1]).zfill(2))
                    value = value.replace("%d", str(date_val[0]).zfill(2))
                    value = value.replace("%Y", str(date_val[2]))
        else:
            return self.display_iso(date_val)

        if date_val[2] < 0:
            return self._bce_str % value
        else:
            return value

    display = DateDisplay.display_formatted


# -------------------------------------------------------------------------
#
# Register classes
#
# -------------------------------------------------------------------------

register_datehandler(
    ("fr_FR", "fr", "french", "French", "fr_CA", "fr_BE", "fr_CH", ("%d/%m/%Y",)),
    DateParserFR,
    DateDisplayFR,
)

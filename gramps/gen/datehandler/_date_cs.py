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
Czech-specific classes for parsing and displaying dates.
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
# Czech parser
#
#-------------------------------------------------------------------------
class DateParserCZ(DateParser):
    """
    Converts a text string into a Date object
    """
    month_to_int = DateParser.month_to_int

    month_to_int["leden"] = 1
    month_to_int["ledna"] = 1
    month_to_int["lednu"] = 1
    month_to_int["led"] = 1
    month_to_int["I"] = 1
    month_to_int["i"] = 1

    month_to_int["únor"] = 2
    month_to_int["února"] = 2
    month_to_int["únoru"] = 2
    month_to_int["ún"] = 2
    month_to_int["II"] = 2
    month_to_int["ii"]  = 2

    month_to_int["březen"] = 3
    month_to_int["března"] = 3
    month_to_int["březnu"] = 3
    month_to_int["bře"] = 3
    month_to_int["III"] = 3
    month_to_int["iii"]  = 3

    month_to_int["duben"] = 4
    month_to_int["dubna"] = 4
    month_to_int["dubnu"] = 4
    month_to_int["dub"] = 4
    month_to_int["IV"]  = 4
    month_to_int["iv"]  = 4

    month_to_int["květen"] = 5
    month_to_int["května"] = 5
    month_to_int["květnu"] = 5
    month_to_int["V"]  = 5
    month_to_int["v"]  = 5

    month_to_int["červen"] = 6
    month_to_int["června"] = 6
    month_to_int["červnu"] = 6
    month_to_int["čer"] = 6
    month_to_int["vi"]  = 6

    month_to_int["červenec"]  = 7
    month_to_int["července"]  = 7
    month_to_int["červenci"]  = 7
    month_to_int["čvc"]  = 7
    month_to_int["VII"]  = 7
    month_to_int["vii"]  = 7

    month_to_int["srpen"]  = 8
    month_to_int["srpna"]  = 8
    month_to_int["srpnu"]  = 8
    month_to_int["srp"]  = 8
    month_to_int["VIII"]  = 8
    month_to_int["viii"]  = 8

    month_to_int["září"]  = 9
    month_to_int["zář"]  = 9
    month_to_int["IX"]  = 9
    month_to_int["ix"]  = 9

    month_to_int["říjen"]  = 10
    month_to_int["října"]  = 10
    month_to_int["říjnu"]  = 10
    month_to_int["říj"]  = 10
    month_to_int["X"]  = 10
    month_to_int["x"]  = 10

    month_to_int["listopad"]  = 11
    month_to_int["listopadu"]  = 11
    month_to_int["lis"]  = 11
    month_to_int["XI"]  = 11
    month_to_int["xi"]  = 11

    month_to_int["prosinec"]  = 12
    month_to_int["prosince"]  = 12
    month_to_int["prosinci"]  = 12
    month_to_int["pro"]  = 12
    month_to_int["XII"]  = 12
    month_to_int["xii"]  = 12

    modifier_to_int = {
        'před'   : Date.MOD_BEFORE,
        'do'     : Date.MOD_BEFORE,
        'po'     : Date.MOD_AFTER,
        'asi'    : Date.MOD_ABOUT,
        'kolem'  : Date.MOD_ABOUT,
        'přibl.' : Date.MOD_ABOUT,
        }

    calendar_to_int = {
        'gregoriánský'  : Date.CAL_GREGORIAN,
        'greg.'         : Date.CAL_GREGORIAN,
        'g'             : Date.CAL_GREGORIAN,
        'juliánský'     : Date.CAL_JULIAN,
        'jul.'          : Date.CAL_JULIAN,
        'j'             : Date.CAL_JULIAN,
        'hebrejský'     : Date.CAL_HEBREW,
        'hebr.'         : Date.CAL_HEBREW,
        'h'             : Date.CAL_HEBREW,
        'islámský'      : Date.CAL_ISLAMIC,
        'isl.'          : Date.CAL_ISLAMIC,
        'i'             : Date.CAL_ISLAMIC,
        'francouzský republikánský'    : Date.CAL_FRENCH,
        'fr.'           : Date.CAL_FRENCH,
        'perský'        : Date.CAL_PERSIAN,
        'per.'          : Date.CAL_PERSIAN,
        'p'             : Date.CAL_PERSIAN,
        'švédský'       : Date.CAL_SWEDISH,
        'sve.'          : Date.CAL_SWEDISH,
        's'             : Date.CAL_SWEDISH,
        }

    quality_to_int = {
        'přibližně'  : Date.QUAL_ESTIMATED,
        'odhadem'    : Date.QUAL_ESTIMATED,
        'odh.'       : Date.QUAL_ESTIMATED,
        'vypočteno'  : Date.QUAL_CALCULATED,
        'vypočtené'  : Date.QUAL_CALCULATED,
        'vyp.'       : Date.QUAL_CALCULATED,
        }

    def init_strings(self):
        DateParser.init_strings(self)
        self._text2 = re.compile('(\d+)?\.?\s+?%s\.?\s*((\d+)(/\d+)?)?\s*$'
                                         % self._mon_str, re.IGNORECASE)
        self._span  = re.compile(
            "(od)\s+(?P<start>.+)\s+(do)\s+(?P<stop>.+)",
            re.IGNORECASE)
        self._range = re.compile(
            "(mezi)\s+(?P<start>.+)\s+(a)\s+(?P<stop>.+)",
            re.IGNORECASE)


#-------------------------------------------------------------------------
#
# Czech display
#
#-------------------------------------------------------------------------
class DateDisplayCZ(DateDisplay):
    """
    Czech language date display class.
    """
    long_months = ( "", "leden", "únor", "březen", "duben", "květen",
                    "červen", "červenec", "srpen", "září", "říjen",
                    "listopad", "prosinec" )

    short_months = ( "", "led", "úno", "bře", "dub", "kvě", "čer",
                     "čvc", "srp", "zář", "říj", "lis", "pro" )

    calendar = (
        "", "juliánský", "hebrejský",
        "francouzský republikánský", "perský", "islámský",
        "švédský"
        )

    _mod_str = ("", "před ", "po ", "kolem ", "", "", "")

    _qual_str = ("", "přibližně ", "vypočteno ")

    bce = ["před naším letopočtem", "před Kristem",
           "př. n. l.", "př. Kr."] + DateParser.bce

    formats = (
        "ISO (rrrr-mm-dd)",
        "numerický",
        "měsíc den, Rok",
        "měs den, Rok",
        "den. měsíc rok",
        "den. měs rok"
        )
        # this must agree with DateDisplayEn's "formats" definition
        # (since no locale-specific _display_gregorian exists, here)

    display = DateDisplay.display_formatted

    def orig_display(self, date):
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
#        elif mod == Date.MOD_NONE:
#            date_decl_string = self.display_cal[cal](start)
#            date_decl_string = date_decl_string.replace("den ", "dna ")
#            date_decl_string = date_decl_string.replace("or ", "ora ")
#            date_decl_string = date_decl_string.replace("en ", "na ")
#            date_decl_string = date_decl_string.replace("ad ", "adu ")
#            date_decl_string = date_decl_string.replace("ec ", "ce ")
#            return date_decl_string
        elif mod == Date.MOD_SPAN:
            dat1 = self.display_cal[cal](start)
            dat2 = self.display_cal[cal](date.get_stop_date())
            scal = self.format_extras(cal, newyear)
            return "%s%s %s %s %s%s" % (qual_str, 'od', dat1,
                                        'do', dat2, scal)
        elif mod == Date.MOD_RANGE:
            dat1 = self.display_cal[cal](start)
            dat2 = self.display_cal[cal](date.get_stop_date())
            scal = self.format_extras(cal, newyear)
            return "%s%s %s %s %s%s" % (qual_str, 'mezi',
                                        dat1, 'a', dat2, scal)
        else:
            text = self.display_cal[date.get_calendar()](start)
            scal = self.format_extras(cal, newyear)
            return "%s%s%s%s" % (qual_str, self._mod_str[mod],
                                 text, scal)

#-------------------------------------------------------------------------
#
# Register classes
#
#-------------------------------------------------------------------------
register_datehandler(("cs", "CS", "cs_CZ", "Czech"), DateParserCZ, DateDisplayCZ)

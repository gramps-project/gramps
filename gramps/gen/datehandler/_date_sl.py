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

# Slovenian version 2010 by Bernard Banko, based on croatian one by Josip

"""
Slovenian-specific classes for parsing and displaying dates - new framework.
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
# Slovenian parser
#
#-------------------------------------------------------------------------
class DateParserSL(DateParser):
    """
    Converts a text string into a Date object
    """

    modifier_to_int = {
        'pred'   : Date.MOD_BEFORE,
        'pr.'    : Date.MOD_BEFORE,
        'po'     : Date.MOD_AFTER,
        'okoli'  : Date.MOD_ABOUT,
        'okrog'  : Date.MOD_ABOUT,
        'okr.'   : Date.MOD_ABOUT,
        'ok.'    : Date.MOD_ABOUT,
        'cca.'   : Date.MOD_ABOUT,
        'cca'    : Date.MOD_ABOUT,
        'circa'  : Date.MOD_ABOUT,
        'ca.'    : Date.MOD_ABOUT,
        'približno' : Date.MOD_ABOUT,
        'pribl.' : Date.MOD_ABOUT,
        '~'      : Date.MOD_ABOUT,
        }

    quality_to_int = {
        'ocenjeno'   : Date.QUAL_ESTIMATED,
        'oc.'        : Date.QUAL_ESTIMATED,
        'po oceni'   : Date.QUAL_ESTIMATED,
        'izračunano' : Date.QUAL_CALCULATED,
        'izrač.'     : Date.QUAL_CALCULATED,
        'po izračunu': Date.QUAL_CALCULATED,
        }

    bce = ["pred našim štetjem", "pred Kristusom",
           "p.n.š.", "p. n. š.", "pr.Kr.", "pr. Kr."] + DateParser.bce

    def init_strings(self):
        """
        compiles regular expression strings for matching dates
        """

        DateParser.init_strings(self)
        # match 'Day. MONTH year.' format with or without dots
        self._text2 = re.compile(r'(\d+)?\.?\s*?%s\.?\s*((\d+)(/\d+)?)?\s*\.?$'
                                 % self._mon_str, re.IGNORECASE)
        # match Day.Month.Year.
        self._numeric = re.compile(
            r"((\d+)[/\.-])?\s*((\d+)[/\.-])?\s*(\d+)\.?$")

        self._span = re.compile(r"od\s+(?P<start>.+)\s+do\s+(?P<stop>.+)",
                                re.IGNORECASE)
        self._range = re.compile(
            r"med\s+(?P<start>.+)\s+in\s+(?P<stop>.+)", re.IGNORECASE)
        self._jtext2 = re.compile(r'(\d+)?.?\s+?%s\s*((\d+)(/\d+)?)?'
                                  % self._jmon_str, re.IGNORECASE)

#-------------------------------------------------------------------------
#
# Slovenian display
#
#-------------------------------------------------------------------------
class DateDisplaySL(DateDisplay):
    """
    Slovenian language date display class.
    """
    # TODO fix BUG 7064: non-Gregorian calendars wrongly use BCE notation for negative dates
    # not refactoring _bce_str into base class because it'll be gone under #7064
    _bce_str = "%s pr.Kr."

    display = DateDisplay.display_formatted

#-------------------------------------------------------------------------
#
# Register classes
#
#-------------------------------------------------------------------------
register_datehandler(
    ("sl_SI", "sl", "SL",
     "slovenščina", "slovenian", "Slovenian", ('%d. %m. %Y',)),
    DateParserSL, DateDisplaySL)

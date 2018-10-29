# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2006  Donald N. Allingham
# Copyright (C) 2013-2014  Fedir Zinchuk <fedikw[at]gmail.com>
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
Ukrainian-specific classes for parsing and displaying dates.
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
# Ukrainian parser
#
#-------------------------------------------------------------------------
class DateParserUK(DateParser):
    """
    Convert a text string into a :class:`.Date` object. If the date cannot be
    converted, the text string is assigned.
    """

    # modifiers before the date
    modifier_to_int = {
        'перед'    : Date.MOD_BEFORE,
        'до'       : Date.MOD_BEFORE,
        'раніше'   : Date.MOD_BEFORE,

        'після'    : Date.MOD_AFTER,
        'п.'       : Date.MOD_AFTER,
        'за'       : Date.MOD_AFTER,

        'приблизно': Date.MOD_ABOUT,
        'прибл.'   : Date.MOD_ABOUT,
        'приб.'    : Date.MOD_ABOUT,
        'близько'  : Date.MOD_ABOUT,
        'бл.'      : Date.MOD_ABOUT,
        'біля'     : Date.MOD_ABOUT,
        }

    quality_to_int = {
        'за оцінкою'  : Date.QUAL_ESTIMATED,
        'за оц.'      : Date.QUAL_ESTIMATED,
        'оцінено'     : Date.QUAL_ESTIMATED,
        'орієнтовно'  : Date.QUAL_ESTIMATED,
        'приблизно'   : Date.QUAL_ESTIMATED,
        'прибл.'      : Date.QUAL_ESTIMATED,

        'підраховано' : Date.QUAL_CALCULATED,
        'підрах.'     : Date.QUAL_CALCULATED,
        'розраховано' : Date.QUAL_CALCULATED,
        'розрахунково' : Date.QUAL_CALCULATED,
        'розрах.'     : Date.QUAL_CALCULATED,
        }

    bce = [
        'до нашої ери', 'до н. е.', 'до н.е.',
        'до народження Христа'
        ] + DateParser.bce

    def init_strings(self):
        """
        This method compiles regular expression strings for matching dates.

        See DateParser.init_strings()
        """
        DateParser.init_strings(self)

        DateParser.hebrew_to_int.update({
            'мархешван': 2,
            'ве адар'  : 7,
            'адар бет' : 7,
            'авів'     : 8,
        })

        _span_1 = ['з', 'від']
        # b.c.e. pattern also have "до" so skip "до н."
        _span_2 = ['по', r'до(?!\s+н)']
        _range_1 = ['між']
        _range_2 = ['і', 'та']
        self._span = re.compile(r"(%s)\s+(?P<start>.+)\s+(%s)\s+(?P<stop>.+)" %
                                ('|'.join(_span_1), '|'.join(_span_2)),
                                re.IGNORECASE)
        self._range = re.compile(r"(%s)\s+(?P<start>.+)\s+(%s)\s+(?P<stop>.+)"
                                 % ('|'.join(_range_1), '|'.join(_range_2)),
                                 re.IGNORECASE)

#-------------------------------------------------------------------------
#
# Ukrainian displayer
#
#-------------------------------------------------------------------------
class DateDisplayUK(DateDisplay):
    """
    Ukrainian language date display class.
    """

    _bce_str = "%s до н.е."

    display = DateDisplay.display_formatted


#-------------------------------------------------------------------------
#
# Register classes
#
#-------------------------------------------------------------------------
register_datehandler(
    ('uk_UA', 'uk', 'ukrainian', 'Ukrainian', ('%d.%m.%Y',)),
    DateParserUK, DateDisplayUK)

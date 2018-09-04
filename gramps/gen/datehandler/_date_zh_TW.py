# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2006  Donald N. Allingham
# Copyright (C) 2014-2015  Paul Franklin
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
Traditional-Chinese-specific classes for parsing and displaying dates.
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
# Traditional-Chinese parser
#
#-------------------------------------------------------------------------
class DateParserZH_TW(DateParser):
    """
    Convert a text string into a Date object. If the date cannot be
    converted, the text string is assigned.
    """

    # modifiers before the date
    modifier_to_int = {
        '以前'   : Date.MOD_BEFORE,
        '以後'   : Date.MOD_AFTER,
        '大約'   : Date.MOD_ABOUT,
        }

    month_to_int = DateParser.month_to_int

    month_to_int["正"] = 1
    month_to_int["一"] = 1
    month_to_int["zhēngyuè"] = 1
    month_to_int["二"] = 2
    month_to_int["èryuè"] = 2
    month_to_int["三"] = 3
    month_to_int["sānyuè"] = 3
    month_to_int["四"] = 4
    month_to_int["sìyuè"] = 4
    month_to_int["五"] = 5
    month_to_int["wǔyuè"] = 5
    month_to_int["六"] = 6
    month_to_int["liùyuè"] = 6
    month_to_int["七"] = 7
    month_to_int["qīyuè"] = 7
    month_to_int["八"] = 8
    month_to_int["bāyuè"] = 8
    month_to_int["九"] = 9
    month_to_int["jiǔyuè"] = 9
    month_to_int["十"] = 10
    month_to_int["shíyuè"] = 10
    month_to_int["十一"] = 11
    month_to_int["shíyīyuè"] = 11
    month_to_int["十二"] = 12
    month_to_int["shí'èryuè"] = 12
    month_to_int["假閏"] = 13
    month_to_int["jiǎ rùn yùe"] = 13

    calendar_to_int = {
        '陽曆'             : Date.CAL_GREGORIAN,
        'g'                : Date.CAL_GREGORIAN,
        '儒略曆'           : Date.CAL_JULIAN,
        'j'                : Date.CAL_JULIAN,
        '希伯來歷'         : Date.CAL_HEBREW,
        'h'                : Date.CAL_HEBREW,
        '伊斯蘭曆'         : Date.CAL_ISLAMIC,
        'i'                : Date.CAL_ISLAMIC,
        '法國共和歷'       : Date.CAL_FRENCH,
        'f'                : Date.CAL_FRENCH,
        '伊郎歷'           : Date.CAL_PERSIAN,
        'p'                : Date.CAL_PERSIAN,
        '瑞典歷'           : Date.CAL_SWEDISH,
        's'                : Date.CAL_SWEDISH,
        }

    quality_to_int = {
        '據估計'     : Date.QUAL_ESTIMATED,
        '據計算'     : Date.QUAL_CALCULATED,
        }

    # FIXME translate these English strings into traditional-Chinese ones
    bce = ["before calendar", "negative year"] + DateParser.bce

    def init_strings(self):
        """
        This method compiles regular expression strings for matching dates.
        """
        DateParser.init_strings(self)
        _span_1 = ['自']
        _span_2 = ['至']
        _range_1 = ['介於']
        _range_2 = ['與']
        self._span = re.compile(r"(%s)(?P<start>.+)(%s)(?P<stop>\d+)" %
                                ('|'.join(_span_1), '|'.join(_span_2)),
                                re.IGNORECASE)
        self._range = re.compile(r"(%s)(?P<start>.+)(%s)(?P<stop>\d+)" %
                                 ('|'.join(_range_1), '|'.join(_range_2)),
                                 re.IGNORECASE)
        self._numeric = re.compile(r"((\d+)年\s*)?((\d+)月\s*)?(\d+)?日?\s*$")

#-------------------------------------------------------------------------
#
# Traditional-Chinese display
#
#-------------------------------------------------------------------------
class DateDisplayZH_TW(DateDisplay):
    """
    Traditional-Chinese language date display class.
    """

    formats = (
        "年年年年-月月-日日 (ISO)",  "數字格式",
        )
        # this definition must agree with its "_display_calendar" method

    # FIXME translate these English strings into traditional-Chinese ones
    _bce_str = "%s B.C.E."

    display = DateDisplay.display_formatted

    def _display_calendar(self, date_val, long_months, short_months = None,
                          inflect=""):
        # this must agree with its locale-specific "formats" definition

        if short_months is None:
            # Let the short formats work the same as long formats
            short_months = long_months

        if self.format == 0:
            return self.display_iso(date_val)
        # elif self.format == 1:
        else:
            # numerical
            value = self.dd_dformat01(date_val)
        if date_val[2] < 0:
            # TODO fix BUG 7064: non-Gregorian calendars wrongly use BCE notation for negative dates
            return self._bce_str % value
        else:
            return value

#-------------------------------------------------------------------------
#
# Register classes
#
#-------------------------------------------------------------------------

register_datehandler(
    ('zh_TW', 'zh_HK', ('西元%Y年%m月%d日',)),
    DateParserZH_TW, DateDisplayZH_TW)

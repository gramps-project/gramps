# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2006  Donald N. Allingham
# Copyright (C) 2014       Mathieu MD <mathieu.md@gmail.com>
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
#

"""
Japanese-specific classes for parsing and displaying dates.
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
# Japanese parser
#
#-------------------------------------------------------------------------
class DateParserJA(DateParser):
    """
    Convert a text string into a Date object. If the date cannot be
    converted, the text string is assigned.
    """

    # modifiers before the date
    modifier_to_int = {
        '以前' : Date.MOD_BEFORE,
        '以降' : Date.MOD_AFTER,
        '頃'   : Date.MOD_ABOUT,
        'ごろ' : Date.MOD_ABOUT,
        }

    month_to_int = DateParser.month_to_int

    quality_to_int = {
        'およそ'    : Date.QUAL_ESTIMATED,
        'ごろ'      : Date.QUAL_ESTIMATED,
        '位'      : Date.QUAL_ESTIMATED,
        '計算上'  : Date.QUAL_CALCULATED,
        }

    bce = ["紀元前", "BC"] + DateParser.bce

    def init_strings(self):
        """
        This method compiles regular expression strings for matching dates.
        """
        DateParser.init_strings(self)

        DateParser.calendar_to_int.update({
            'グレゴリオ暦' : Date.CAL_GREGORIAN,
            'g'            : Date.CAL_GREGORIAN,
            'ユリウス暦' : Date.CAL_JULIAN,
            'j'          : Date.CAL_JULIAN,
            'ユダヤ暦' : Date.CAL_HEBREW,
            'h'        : Date.CAL_HEBREW,
            'ヒジュラ暦' : Date.CAL_ISLAMIC,
            'i'          : Date.CAL_ISLAMIC,
            'フランス革命暦' : Date.CAL_FRENCH,
            '共和暦'         : Date.CAL_FRENCH,
            'f'              : Date.CAL_FRENCH,
            'イラン暦' : Date.CAL_PERSIAN,
            'p'        : Date.CAL_PERSIAN,
            'スウェーデン暦' : Date.CAL_SWEDISH,
            's'              : Date.CAL_SWEDISH,
        })

        DateParser.month_to_int.update({
            "一月"      : 1,
            "ichigatsu" : 1,
            "睦月"      : 1,
            "mutsuki"   : 1,
            "二月"       : 2,
            "nigatsu"    : 2,
            "如月"       : 2,
            "kisaragi"   : 2,
            "衣更着"     : 2,
            "kinusaragi" : 2,
            "三月"     : 3,
            "sangatsu" : 3,
            "弥生"     : 3,
            "yayoi"    : 3,
            "四月"     : 4,
            "shigatsu" : 4,
            "卯月"     : 4,
            "uzuki"    : 4,
            "五月"       : 5,
            "gogatsu"    : 5,
            "皐月"       : 5,
            "satsuki"    : 5,
            "早苗月"     : 5,
            "sanaetsuki" : 5,
            "六月"      : 6,
            "rokugatsu" : 6,
            "水無月"    : 6,
            "minazuki"  : 6,
            "七月"        : 7,
            "shichigatsu" : 7,
            "文月"        : 7,
            "fumizuki"    : 7,
            "八月"       : 8,
            "hachigatsu" : 8,
            "葉月"       : 8,
            "hazuki"     : 8,
            "九月"      : 9,
            "kugatsu"   : 9,
            "長月"      : 9,
            "nagatsuki" : 9,
            "十月"        : 10,
            "jugatsu"     : 10,
            "jūgatsu"     : 10,
            "juugatsu"    : 10,
            "神無月"      : 10,
            "kannazuki"   : 10,
            "kaminazuki"  : 10,
            "神有月"      : 10,
            "神在月"      : 10,
            "kamiarizuki" : 10,
            "十一月"       : 11,
            "juichigatsu"  : 11,
            "jūichigatsu"  : 11,
            "juuichigatsu" : 11,
            "霜月"         : 11,
            "shimotsuki"   : 11,
            "十二月"     : 12,
            "junigatsu"  : 12,
            "jūnigatsu"  : 12,
            "juunigatsu" : 12,
            "師走"       : 12,
            "shiwasu"    : 12,
        })

        _span_1 = ['から', '~', '〜']
        _span_2 = ['まで', '']
        _range_1 = ['から', 'と', '~', '〜']
        _range_2 = ['までの間', 'の間']
        self._span = re.compile(r"(?P<start>.+)(%s)(?P<stop>\d+)(%s)" %
                                ('|'.join(_span_1), '|'.join(_span_2)),
                                re.IGNORECASE)
        self._range = re.compile(r"(?P<start>.+)(%s)(?P<stop>.+)(%s)" %
                                 ('|'.join(_range_1), '|'.join(_range_2)),
                                 re.IGNORECASE)
        self._numeric = re.compile(r"((\d+)年\s*)?((\d+)月\s*)?(\d+)?日?\s*$")

#-------------------------------------------------------------------------
#
# Japanese display
#
#-------------------------------------------------------------------------
class DateDisplayJA(DateDisplay):
    """
    Japanese language date display class.
    """

    def formats_changed(self):
        """ Allow overriding so a subclass can modify """

        # Specify what is actually the "System Default".
        example = self.dhformat
        example = example.replace('%d', "31")
        example = example.replace('%m', "12")
        example = example.replace('%Y', "1999")

        # This definition must agree with its "_display_gregorian" method
        self. formats = ("YYYY-MM-DD (ISO)", # 0
                "システムデフォールト (" + example + ")", # 1
                "1999年12月31日",   # 2
                "1999年十二月31日", # 3
                )

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
            # System Default
            if date_val[2] < 0 or date_val[3]:
                return self.display_iso(date_val)
            else:
                if date_val[0] == date_val[1] == 0:
                    value = str(date_val[2])
                else:
                    value = self.dhformat.replace('%m', str(date_val[1]))
                    if date_val[0] == 0: # ignore the zero day and its delimiter
                        i_day = value.find('%d')
                        value = value.replace(value[i_day:i_day+3], '')
                    value = value.replace('%d', str(date_val[0]))
                    value = value.replace('%Y', str(date_val[2]))

        elif self.format == 2:
            # 1999年12月31日
            if date_val[0] == 0:
                if date_val[1] == 0:
                    value = "%s年" % year
                else:
                    value = "%s年%s" % (year,
                                        self.short_months[date_val[1]])
            else:
                value = "%s年%s%s日" % (year,
                                        self.short_months[date_val[1]],
                                        date_val[0])

        elif self.format == 3:
            # 1999年十二月31日
            if date_val[0] == 0:
                if date_val[1] == 0:
                    value = "%s年" % year
                else:
                    value = "%s年%s" % (year,
                                        self.long_months[date_val[1]])
            else:
                value = "%s年%s%s日" % (year,
                                        self.long_months[date_val[1]],
                                        date_val[0])

        else:
            return self.display_iso(date_val)

        if date_val[2] < 0:
            return self._bce_str % value
        else:
            return value

    display = DateDisplay.display_formatted

#-------------------------------------------------------------------------
#
# Register classes
#
#-------------------------------------------------------------------------

register_datehandler(
    ('ja_JP', 'ja', 'japanese', 'Japanese', ('%Y年%m月%d日',)),
    DateParserJA, DateDisplayJA)

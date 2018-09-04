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
Arabic-specific classes for parsing and displaying dates.
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
from ..const import ARABIC_COMMA

#-------------------------------------------------------------------------
#
# Arabic parser class
#
#-------------------------------------------------------------------------
class DateParserAR(DateParser):
    """
    Convert a text string into a Date object. If the date cannot be
    converted, the text string is assigned.
    """

    # modifiers before the date
    modifier_to_int = {
        'قبل' : Date.MOD_BEFORE,
        'قبل'    : Date.MOD_BEFORE,
        'قبل.'   : Date.MOD_BEFORE,
        'بعد'  : Date.MOD_AFTER,
        'بعد'    : Date.MOD_AFTER,
        'بعد.'   : Date.MOD_AFTER,
        'حوالي'  : Date.MOD_ABOUT,
        'حوالي.'   : Date.MOD_ABOUT,
        'حوالي'    : Date.MOD_ABOUT,
        'حوالي'  : Date.MOD_ABOUT,
        'حوالي.'     : Date.MOD_ABOUT,
        'حوالي' : Date.MOD_ABOUT,
        }

    islamic_to_int = {
        "محرّم"           : 1,  "محرّم الحرام"  : 1,
        "صفر"              : 2,  "ربيع الأول"      : 3,
        "ربيع 1"             : 3,  "ربيع الأخير"      : 4,
        "ربيع الثاني"     : 4,  "ربيع الثاني"    : 4,
        "ربيع الثاني"     : 4,  "ربيع الثاني"    : 4,
        "ربيع 2"           : 4,  "جمادى الأولى"       : 5,
        "جمادى الأول"   : 5,  "جمادى 1"          : 5,
        "جمادى الثانية"     : 6,  "جمادى الأخير"   : 6,
        "جمادى الثاني"  : 6,  "جمادى 2"         : 5,
        "رجب"              : 7,  "شعبان"            : 8,
        "شعبان"           : 8,  "رمضان"            : 9,
        "رمضان"           : 9,  "شوال"            : 10,
        "ذو القعدة"        : 11, "ذو القعدة"          : 11,
        "ذو القعدة"      : 11, "ذو الحجة"        : 12,
        "ذو الحجة"          : 12, "ذو الحجة"      : 12,
        }

    bce = ["قبل الميلاد", "قبل الميلاد", "قبل الميلاد", "قبل الميلاد", "قبل الميلاد", "قبل الميلاد" ]

    calendar_to_int = {
        'غريغوري'        : Date.CAL_GREGORIAN,
        'غريغوري'                : Date.CAL_GREGORIAN,
        'يوليوسي'           : Date.CAL_JULIAN,
        'يوليوسي'                : Date.CAL_JULIAN,
        'عبري'           : Date.CAL_HEBREW,
        'عبري'                : Date.CAL_HEBREW,
        'إسلامي'          : Date.CAL_ISLAMIC,
        'إسلامي'                : Date.CAL_ISLAMIC,
        'فرنسي'           : Date.CAL_FRENCH,
        'فرنسي جمهوري': Date.CAL_FRENCH,
        'فرنسي'                : Date.CAL_FRENCH,
        'فارسي'          : Date.CAL_PERSIAN,
        'فارسي'                : Date.CAL_PERSIAN,
        'سويدي'          : Date.CAL_SWEDISH,
        'سويدي'                : Date.CAL_SWEDISH,
        }

    quality_to_int = {
        'متوقع'  : Date.QUAL_ESTIMATED,
        'متوقع.'       : Date.QUAL_ESTIMATED,
        'متوقع'        : Date.QUAL_ESTIMATED,
        'محسوب.'      : Date.QUAL_CALCULATED,
        'محسوب'       : Date.QUAL_CALCULATED,
        'محسوب' : Date.QUAL_CALCULATED,
        }

    def init_strings(self):
        """
        This method compiles regular expression strings for matching dates.
        """
        DateParser.init_strings(self)
        _span_1 = ['من']
        _span_2 = ['إلى']
        _range_1 = ['بين']
        _range_2 = ['و']
        self._span = re.compile(
            r"(%s)\s+(?P<start>.+)\s+(%s)\s+(?P<stop>.+)" %
            ('|'.join(_span_1), '|'.join(_span_2)), re.IGNORECASE)
        self._range = re.compile(
            r"(%s)\s+(?P<start>.+)\s+(%s)\s+(?P<stop>.+)" %
            ('|'.join(_range_1), '|'.join(_range_2)), re.IGNORECASE)

#-------------------------------------------------------------------------
#
# Arabic display
#
#-------------------------------------------------------------------------
class DateDisplayAR(DateDisplay):
    """
    Arabic language date display class.
    """
    # this is used to display the 12 gregorian months
    long_months = ( "", "كانون الثاني", "شباط", "آذار", "نيسان", "أيار",
                    "حزيران", "تموز", "آب", "أيلول", "تشرين الأول",
                    "تشرين الثاني", "كانون الأول" )

    short_months = ( "", "كانون2", "شباط", "آذار", "نيسان", "أيار", "حزيران",
                     "تموز", "آب", "أيلول", "تشرين1", "تشرين2", "كانون1" )

    islamic = (
        "", "محرّم", "صفر", "ربيع الأول", "ربيع الثاني",
        "جمادى الأولى", "جمادى الثانية", "رجب", "شعبان",
        "رمضان", "شوال", "ذو القعدة", "ذو الحجة"
        )

    formats = (
        "YYYY-MM-DD (قياسي)", "عددي", "شهر يوم, سنة",
        "شهر يوم, سنة", "يوم شهر سنة", "يوم شهر سنة"
        )
        # this must agree with DateDisplayEn's "formats" definition
        # (since no locale-specific _display_gregorian exists, here)

    calendar = (
        "", "يوليوسي", "عبري", "فرنسي",
        "فارسي", "إسلامي", "سويدي"
        )

    _mod_str = ("", "قبل ", "بعد ", "حوالي ", "", "", "")

    _qual_str = ("", "متوقع ", "محسوب ")

    _bce_str = "%s قبل الميلاد."

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
            return "%s%s %s %s %s%s" % (qual_str, 'من', d1, 'إلى', d2, scal)
        elif mod == Date.MOD_RANGE:
            d1 = self.display_cal[cal](start)
            d2 = self.display_cal[cal](date.get_stop_date())
            scal = self.format_extras(cal, newyear)
            return "%s%s %s %s %s%s" % (qual_str, 'بين', d1, 'و', d2, scal)
        else:
            text = self.display_cal[date.get_calendar()](start)
            scal = self.format_extras(cal, newyear)
            return "%s%s%s%s" % (qual_str, self._mod_str[mod], text, scal)

    def dd_dformat01(self, date_val):
        """
        numerical -- for Arabic dates
        """
        value = DateDisplay.dd_dformat01(self, date_val)
        return value.replace(',', ARABIC_COMMA)

    def dd_dformat02(self, date_val, inflect, long_months):
        """
        month_name day, year -- for Arabic dates
        """
        value = DateDisplay.dd_dformat02(self, date_val, inflect, long_months)
        return value.replace(',', ARABIC_COMMA)

    def dd_dformat03(self, date_val, inflect, short_months):
        """
        month_abbreviation day, year -- for Arabic dates
        """
        value = DateDisplay.dd_dformat03(self, date_val, inflect, short_months)
        return value.replace(',', ARABIC_COMMA)

#-------------------------------------------------------------------------
#
# Register classes
#
#-------------------------------------------------------------------------
register_datehandler(
    ('ar_EG', 'ar_AR', 'ar', 'Arabic', 'arabic', ('%d %b, %Y',)),
    DateParserAR, DateDisplayAR)

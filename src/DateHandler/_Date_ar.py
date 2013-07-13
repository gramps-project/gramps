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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

"""
Arabic-specific classes for parsing and displaying dates.
"""

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from __future__ import unicode_literals
import re

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from gen.lib import Date
from _DateParser import DateParser
from _DateDisplay import DateDisplay
from _DateHandler import register_datehandler

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
    # in some languages some of above listed modifiers are after the date,
    # in that case the subclass should put them into this dictionary instead
    modifier_after_to_int = {}

    hebrew_to_int = {
        "tishri"  : 1,   "heshvan" : 2,   "kislev"  : 3,
        "tevet"   : 4,   "shevat"  : 5,   "adari"   : 6,
        "adarii"  : 7,   "nisan"   : 8,   "iyyar"   : 9,
        "sivan"   : 10,  "tammuz"  : 11,  "av"      : 12,
        "elul"    : 13,
        #alternative spelling
        "cheshvan": 2,   "adar sheni":  7, "iyar"    : 9,
        }

    french_to_int = {
        'vendémiaire'  : 1,    'brumaire'   : 2,
        'frimaire'     : 3,    'nivôse': 4,
        'pluviôse'     : 5,    'ventôse' : 6,
        'germinal'     : 7,    'floréal' : 8,
        'prairial'     : 9,    'messidor'   : 10,
        'thermidor'    : 11,   'fructidor'  : 12,
        'extra'        : 13,
        #GEDCOM months
        'vend'    : 1,    'brum' : 2,
        'frim'    : 3,    'nivo' : 4,
        'pluv'    : 5,    'vent' : 6,
        'germ'    : 7,    'flor' : 8,
        'prai'    : 9,    'mess' : 10,
        'ther'    : 11,   'fruc' : 12,
        'comp'    : 13,
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

    persian_to_int = {
        "farvardin"   : 1,  "ordibehesht" : 2,
        "khordad"     : 3,  "tir"         : 4,
        "mordad"      : 5,  "shahrivar"   : 6,
        "mehr"        : 7,  "aban"        : 8,
        "azar"        : 9,  "dey"         : 10,
        "bahman"      : 11, "esfand"      : 12,
        }

    swedish_to_int = {
        "januari"    :  1, "februari"   :  2,
        "mars"       :  3, "april"      :  4,
        "maj"        :  5, "juni"       :  6,
        "juli"       :  7, "augusti"    :  8,
        "september"  :  9, "oktober"    : 10,
        "november"   : 11, "december"   : 12,
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
        _span_1 = [u'من']
        _span_2 = [u'إلى']
        _range_1 = [u'بين']
        _range_2 = [u'و']
        self._span =  re.compile("(%s)\s+(?P<start>.+)\s+(%s)\s+(?P<stop>.+)" %
                                 ('|'.join(_span_1), '|'.join(_span_2)),
                                 re.IGNORECASE)
        self._range = re.compile("(%s)\s+(?P<start>.+)\s+(%s)\s+(?P<stop>.+)" %
                                 ('|'.join(_range_1), '|'.join(_range_2)),
                                 re.IGNORECASE)

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

    #Hebrew months - don't translate if not needed
    hebrew = (
        "", "Tishri", "Heshvan", "Kislev", "Tevet", "Shevat", 
        "AdarI", "AdarII", "Nisan", "Iyyar", "Sivan", "Tammuz", 
        "Av", "Elul"
        )
    #french republican months - don't translate if not needed
    french = (
        '', 
        "Vendémiaire", 
        'Brumaire', 
        'Frimaire', 
        "Nivôse", 
        "Pluviôse", 
        "Ventôse", 
        'Germinal', 
        "Floréal", 
        'Prairial', 
        'Messidor', 
        'Thermidor', 
        'Fructidor', 
        'Extra', 
        )
    
    persian = (
        "", "Farvardin", "Ordibehesht", "Khordad", "Tir", 
        "Mordad", "Shahrivar", "Mehr", "Aban", "Azar", 
        "Dey", "Bahman", "Esfand"
        )
    
    islamic = (
        "", "محرّم", "صفر", "ربيع الأول", "ربيع الثاني", 
        "جمادى الأولى", "جمادى الثانية", "رجب", "شعبان", 
        "رمضان", "شوال", "ذو القعدة", "ذو الحجة"
        )

    swedish = (
        "", "Januari", "Februari", "Mars",
        "April", "Maj", "Juni",
        "Juli", "Augusti", "September",
        "Oktober", "November", "December"
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

#-------------------------------------------------------------------------
#
# Register classes
#
#-------------------------------------------------------------------------
register_datehandler(('ar_AR', 'ar', 'Arabic', 'arabic'), 
    DateParserAR, DateDisplayAR)

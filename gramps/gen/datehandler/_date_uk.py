# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2006  Donald N. Allingham
# Copyright (C) 2013       Fedir Zinchuk <fedikw[at]gmail.com>
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
Ukrainian-specific classes for parsing and displaying dates.
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

from ..lib.date import Date
from ._dateparser import DateParser
from ._datedisplay import DateDisplay
from ._datehandler import register_datehandler
from . import _grampslocale

#-------------------------------------------------------------------------
#
# Ukrainian parser
#
#-------------------------------------------------------------------------
class DateParserUK(DateParser):
    """
    Convert a text string into a Date object. If the date cannot be
    converted, the text string is assigned.
    """

    month_to_int = DateParser.month_to_int

    # the genitive
    month_to_int["січня"] = 1
    month_to_int["лютого"] = 2
    month_to_int["березня"] = 3
    month_to_int["квітня"] = 4
    month_to_int["травня"] = 5
    month_to_int["червня"] = 6
    month_to_int["липня"] = 7
    month_to_int["серпня"] = 8
    month_to_int["вересня"] = 9
    month_to_int["жовтня"] = 10
    month_to_int["листопада"] = 11
    month_to_int["грудня"] = 12

    # some short variants of the months
    month_to_int["січ."] = 1
    month_to_int["січ"] = 1
    month_to_int["лют."] = 2
    month_to_int["лют"] = 2
    month_to_int["бер."] = 3
    month_to_int["бер"] = 3
    month_to_int["квіт."] = 4
    month_to_int["квіт"] = 4
    month_to_int["трав."] = 5
    month_to_int["трав"] = 5
    month_to_int["черв."] = 6
    month_to_int["черв"] = 6
    month_to_int["лип."] = 7
    month_to_int["лип"] = 7
    month_to_int["серп."] = 8
    month_to_int["серп"] = 8
    month_to_int["вер."] = 9
    month_to_int["вер"] = 9
    month_to_int["жовт."] = 10
    month_to_int["жовт"] = 10
    month_to_int["лист."] = 11
    month_to_int["лист"] = 11
    month_to_int["груд."] = 12
    month_to_int["груд"] = 12


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

    hebrew_to_int = {
        "тішрі"    : 1,    "хешвен"   : 2,    "кіслев"   : 3,
        "тевет"    : 4,    "шват"     : 5,    "адар"     : 6,
        "адара"    : 7,    "нісан"    : 8,    "іяр"      : 9,
        "сиван"    : 10,   "таммуз"   : 11,   "ав"       : 12,
        "елул"     : 13,
        #alternative spelling
        "мархешван": 2, "ве адар"  : 7,
        #GEDCOM months
        "tsh" : 1, "csh": 5, "ksl": 3, "tvt": 4, "shv": 5, "adr": 6,
        "ads" : 7, "nsn": 8, "iyr": 9, "svn":10, "tmz":11, "aav":12,
        "ell":13,
        }

    french_to_int = {
        'вандем’єр'  : 1,    'брюмер'   : 2,
        'фрімер'     : 3,    'нівоз'    : 4,
        'плювіоз'    : 5,    'вентоз'   : 6,
        'жерміналь'  : 7,    'флореаль' : 8,
        'преріаль'   : 9,    'мессідор' : 10,
        'термідор'   : 11,   'фрюктідор': 12,
        'додатковий' : 13,
        #short
        'ванд' : 1,    'брюм' : 2,
        'фрім' : 3,    'нів'  : 4,
        'плюв' : 5,    'вент' : 6,
        'жерм' : 7,    'флор' : 8,
        'прер' : 9,    'месс' : 10,
        'терм' : 11,   'фрюкт': 12,
        'дод'  : 13,
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
        "мухаррам"           : 1,  "мухаррем"           : 1,
        "сафар"              : 2,  "рабі-аль-авваль"    : 3,
        "рабі-ассані"        : 4,
        "джумада-аль-уля"    : 5,  "джумада-аль-авваль" : 5,
        "джумада-аль-ахіра"  : 6,  "джумада-ас-сані"    : 6,
        "раджаб"             : 7,  "шаабан"             : 8,
        "рамадан"            : 9,  "рамазан"            : 9,
        "шавваль"            : 10, "зуль-каада"         : 11,
        "зуль-хіджжа"        : 12,
        }

    persian_to_int = {
        "фарвардін" : 1,  "ордібехешт"  : 2,
        "хордад"    : 3,  "тир"         : 4,
        "мордад"    : 5,  "шахрівар"    : 6,
        "мехр"      : 7,  "абан"        : 8,
        "азар"      : 9,  "дей"         : 10,
        "бахман"    : 11, "есфанд"      : 12,
        }

    bce = ['до нашої ери', 'до н. е.', 'до н.е.']

    calendar_to_int = {
        'григоріанський'              : Date.CAL_GREGORIAN,
        'г'                           : Date.CAL_GREGORIAN,
        'юліанський'                  : Date.CAL_JULIAN,
        'ю'                           : Date.CAL_JULIAN,
        'єврейський'                  : Date.CAL_HEBREW,
        'є'                           : Date.CAL_HEBREW,
        'ісламський'                  : Date.CAL_ISLAMIC,
        'і'                           : Date.CAL_ISLAMIC,
        'французький'                 : Date.CAL_FRENCH,
        'французький республіканський': Date.CAL_FRENCH,
        'французький революційний'    : Date.CAL_FRENCH,
        'ф'                           : Date.CAL_FRENCH,
        'іранський'                   : Date.CAL_PERSIAN,
        'перський'                    : Date.CAL_PERSIAN,
        'п'                           : Date.CAL_PERSIAN,
        'шведський'                   : Date.CAL_SWEDISH,
        'ш'                           : Date.CAL_SWEDISH,
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

    def init_strings(self):
        """
        This method compiles regular expression strings for matching dates.

        See DateParser.init_strings()
        """
        DateParser.init_strings(self)

        _span_1 = ['з', 'від']
        # b.c.e. pattern also have "до" so skip "до н."
        _span_2 = ['по', 'до?!\sн\.']
        self._span = re.compile("(%s)\s+(?P<start>.+)\s+(%s)\s+(?P<stop>.+)" %
                                    ('|'.join(_span_1), '|'.join(_span_2)),
                                    re.IGNORECASE)
        _range_1 = ['між']
        _range_2 = ['і', 'та']
        self._range = re.compile("(%s)\s+(?P<start>.+)\s+(%s)\s+(?P<stop>.+)" %
                                    ('|'.join(_range_1), '|'.join(_range_2)),
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

# the months as the noun or as the genitive???

# as the genitive:
    long_months = (
        "", "січня", "лютого", "березня", "квітня",
        "травня", "червня", "липня", "серпня",
        "вересня", "жовтня", "листопада", "грудня"
        )

# as the noun:
#    long_months = (
#        "", "січень", "лютий", "березень", "квітень",
#        "травень", "червень", "липень", "серпень",
#        "вересень", "жовтень", "листопад", "грудень"
#        )

    short_months = (
        "", "січ.", "лют.", "бер.", "квіт.", "трав.", "черв.",
        "лип.", "серп.", "вер.", "жовт.", "лист.", "груд."
        )

    hebrew = (
        "", "тішрі", "хешвен", "кіслев", "тевет", "шват",
        "адар", "адара", "нісан", "іяр", "сиван", "таммуз",
        "ав", "елул"
        )

    french = (
        '', 'вандем’єр', 'брюмер', 'фрімер', 'нівоз',
        'плювіоз', 'вентоз', 'жерміналь', 'флореаль',
        'преріаль', 'мессідор', 'термідор', 'фрюктідор',
        'додатковий'
        )

    persian = (
        "", "фарвардін", "ордібехешт", "хордад", "тир",
        "мордад", "шахрівар", "мехр", "абан",
        "азар", "дей", "бахман", "есфанд"
        )

    islamic = (
        "", "мухаррам", "сафар",  "рабі-аль-авваль",
        "рабі-ассані", "джумада-аль-уля", "джумада-аль-ахіра",
        "раджаб",  "шаабан", "рамадан", "шавваль", "зуль-каада",
        "зуль-хіджжа",
        )

    # Replace the previous "Numerical" by a string which
    # do have an explicit meaning: "System default (format)"
    _locale_tformat = _grampslocale.tformat
    _locale_tformat = _locale_tformat.replace('%d', "д")
    _locale_tformat = _locale_tformat.replace('%m', "м")
    _locale_tformat = _locale_tformat.replace('%Y', "р")

    formats = (
        "рррр-мм-дд (ISO)", #0
        "стандартний для системи (" + _locale_tformat + ")", #1
        "місяць день, рік", #2
        "міс. дд, рррр",    #3
        "день місяць рік",  #4
        "дд міс. рррр"      #5
        )

    calendar = (
        "", "юліанський", "єврейський", "французький республіканський",
        "іранський", "ісламський", "шведський"
        )

    _mod_str = ("", "до ", "після ", "близько ", "", "", "")

    _qual_str = ("", "орієнтовно ", "розрахунково ")

    _bce_str = "%s до н.е."

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
            return "%sз %s %s %s%s" % (qual_str, d1, 'по', d2,
                                       scal)
        elif mod == Date.MOD_RANGE:
            d1 = self.display_cal[cal](start)
            d2 = self.display_cal[cal](date.get_stop_date())
            scal = self.format_extras(cal, newyear)
            return "%s%s %s %s %s%s" % (qual_str, 'між', d1, 'та',
                                        d2, scal)
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
register_datehandler(('uk_UA', 'uk', 'ukrainian', 'Ukrainian'),
                        DateParserUK, DateDisplayUK)

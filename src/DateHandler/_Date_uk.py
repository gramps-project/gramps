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

# $Id: _Date_uk.py 18361 2011-10-23 03:13:50Z paul-franklin $

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
# GRAMPS modules
#
#-------------------------------------------------------------------------
from gen.lib import Date
from _DateParser import DateParser
from _DateDisplay import DateDisplay
from _DateHandler import register_datehandler

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
    month_to_int[u"січня"] = 1
    month_to_int[u"лютого"] = 2
    month_to_int[u"березня"] = 3
    month_to_int[u"квітня"] = 4
    month_to_int[u"травня"] = 5
    month_to_int[u"червня"] = 6
    month_to_int[u"липня"] = 7
    month_to_int[u"серпня"] = 8
    month_to_int[u"вересня"] = 9
    month_to_int[u"жовтня"] = 10
    month_to_int[u"листопада"] = 11
    month_to_int[u"грудня"] = 12

    # some short variants of the months
    month_to_int[u"січ."] = 1
    month_to_int[u"січ"] = 1
    month_to_int[u"лют."] = 2
    month_to_int[u"лют"] = 2
    month_to_int[u"бер."] = 3
    month_to_int[u"бер"] = 3
    month_to_int[u"квіт."] = 4
    month_to_int[u"квіт"] = 4
    month_to_int[u"трав."] = 5
    month_to_int[u"трав"] = 5
    month_to_int[u"черв."] = 6
    month_to_int[u"черв"] = 6
    month_to_int[u"лип."] = 7
    month_to_int[u"лип"] = 7
    month_to_int[u"серп."] = 8
    month_to_int[u"серп"] = 8
    month_to_int[u"вер."] = 9
    month_to_int[u"вер"] = 9
    month_to_int[u"жовт."] = 10
    month_to_int[u"жовт"] = 10
    month_to_int[u"лист."] = 11
    month_to_int[u"лист"] = 11
    month_to_int[u"груд."] = 12
    month_to_int[u"груд"] = 12


    # modifiers before the date
    modifier_to_int = {
        u'перед'    : Date.MOD_BEFORE,
        u'до'       : Date.MOD_BEFORE,
        u'раніше'   : Date.MOD_BEFORE,

        u'після'    : Date.MOD_AFTER,
        u'п.'       : Date.MOD_AFTER,
        u'за'       : Date.MOD_AFTER,

        u'приблизно': Date.MOD_ABOUT,
        u'прибл.'   : Date.MOD_ABOUT,
        u'приб.'    : Date.MOD_ABOUT,
        u'близько'  : Date.MOD_ABOUT,
        u'бл.'      : Date.MOD_ABOUT,
        u'біля'     : Date.MOD_ABOUT,
        }

    hebrew_to_int = {
        u"тішрі"    : 1,    u"хешвен"   : 2,    u"кіслев"   : 3,
        u"тевет"    : 4,    u"шват"     : 5,    u"адар"     : 6,
        u"адара"    : 7,    u"нісан"    : 8,    u"іяр"      : 9,
        u"сиван"    : 10,   u"таммуз"   : 11,   u"ав"       : 12,
        u"елул"     : 13,
        #alternative spelling
        u"мархешван": 2, u"ве адар"  : 7,
        #GEDCOM months
        u"tsh" : 1, u"csh": 5, u"ksl": 3, u"tvt": 4, u"shv": 5, u"adr": 6,
        u"ads" : 7, u"nsn": 8, u"iyr": 9, u"svn":10, u"tmz":11, u"aav":12,
        u"ell":13,
        }

    french_to_int = {
        u'вандем’єр'  : 1,    u'брюмер'   : 2,
        u'фрімер'     : 3,    u'нівоз'    : 4,
        u'плювіоз'    : 5,    u'вентоз'   : 6,
        u'жерміналь'  : 7,    u'флореаль' : 8,
        u'преріаль'   : 9,    u'мессідор' : 10,
        u'термідор'   : 11,   u'фрюктідор': 12,
        u'додатковий' : 13,
        #short
        u'ванд' : 1,    u'брюм' : 2,
        u'фрім' : 3,    u'нів'  : 4,
        u'плюв' : 5,    u'вент' : 6,
        u'жерм' : 7,    u'флор' : 8,
        u'прер' : 9,    u'месс' : 10,
        u'терм' : 11,   u'фрюкт': 12,
        u'дод'  : 13,
        #GEDCOM months
        u'vend'    : 1,    u'brum' : 2,
        u'frim'    : 3,    u'nivo' : 4,
        u'pluv'    : 5,    u'vent' : 6,
        u'germ'    : 7,    u'flor' : 8,
        u'prai'    : 9,    u'mess' : 10,
        u'ther'    : 11,   u'fruc' : 12,
        u'comp'    : 13,
        }

    islamic_to_int = {
        u"мухаррам"           : 1,  u"мухаррем"           : 1,
        u"сафар"              : 2,  u"рабі-аль-авваль"    : 3,
        u"рабі-ассані"        : 4,
        u"джумада-аль-уля"    : 5,  u"джумада-аль-авваль" : 5,
        u"джумада-аль-ахіра"  : 6,  u"джумада-ас-сані"    : 6,
        u"раджаб"             : 7,  u"шаабан"             : 8,
        u"рамадан"            : 9,  u"рамазан"            : 9,
        u"шавваль"            : 10, u"зуль-каада"         : 11,
        u"зуль-хіджжа"        : 12,
        }

    persian_to_int = {
        u"фарвардін" : 1,  u"ордібехешт"  : 2,
        u"хордад"    : 3,  u"тир"         : 4,
        u"мордад"    : 5,  u"шахрівар"    : 6,
        u"мехр"      : 7,  u"абан"        : 8,
        u"азар"      : 9,  u"дей"         : 10,
        u"бахман"    : 11, u"есфанд"      : 12,
        }

    bce = [u'до нашої ери', u'до н. е.', u'до н.е.']

    calendar_to_int = {
        u'григоріанський'              : Date.CAL_GREGORIAN,
        u'г'                           : Date.CAL_GREGORIAN,
        u'юліанський'                  : Date.CAL_JULIAN,
        u'ю'                           : Date.CAL_JULIAN,
        u'єврейський'                  : Date.CAL_HEBREW,
        u'є'                           : Date.CAL_HEBREW,
        u'ісламський'                  : Date.CAL_ISLAMIC,
        u'і'                           : Date.CAL_ISLAMIC,
        u'французький'                 : Date.CAL_FRENCH,
        u'французький республіканський': Date.CAL_FRENCH,
        u'французький революційний'    : Date.CAL_FRENCH,
        u'ф'                           : Date.CAL_FRENCH,
        u'іранський'                   : Date.CAL_PERSIAN,
        u'перський'                    : Date.CAL_PERSIAN,
        u'п'                           : Date.CAL_PERSIAN,
        u'шведський'                   : Date.CAL_SWEDISH,
        u'ш'                           : Date.CAL_SWEDISH,
        }

    quality_to_int = {
        u'за оцінкою'  : Date.QUAL_ESTIMATED,
        u'за оц.'      : Date.QUAL_ESTIMATED,
        u'оцінено'     : Date.QUAL_ESTIMATED,
        u'орієнтовно'  : Date.QUAL_ESTIMATED,
        u'приблизно'   : Date.QUAL_ESTIMATED,
        u'прибл.'      : Date.QUAL_ESTIMATED,
        u'підраховано' : Date.QUAL_CALCULATED,
        u'підрах.'     : Date.QUAL_CALCULATED,
        u'розраховано' : Date.QUAL_CALCULATED,
        u'розрахунково' : Date.QUAL_CALCULATED,
        u'розрах.'     : Date.QUAL_CALCULATED,
        }

    def init_strings(self):
        """
        This method compiles regular expression strings for matching dates.

        See DateParser.init_strings()
        """
        DateParser.init_strings(self)

        _span_1 = [u'з', u'від']
        # b.c.e. pattern also have "до" so skip "до н."
        _span_2 = [u'по', u'до?!\sн\.']
        self._span     = re.compile("(%s)\s+(?P<start>.+)\s+(%s)\s+(?P<stop>.+)" %
                                    ('|'.join(_span_1), '|'.join(_span_2)),
                                    re.IGNORECASE)
        _range_1 = [u'між']
        _range_2 = [u'і', u'та']
        self._range    = re.compile("(%s)\s+(?P<start>.+)\s+(%s)\s+(?P<stop>.+)" %
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
        u"", u"січня", u"лютого", u"березня", u"квітня",
        u"травня", u"червня", u"липня", u"серпня",
        u"вересня", u"жовтня", u"листопада", u"грудня"
        )

# as the noun:
#    long_months = (
#        u"", u"січень", u"лютий", u"березень", u"квітень",
#        u"травень", u"червень", u"липень", u"серпень",
#        u"вересень", u"жовтень", u"листопад", u"грудень"
#        )

    short_months = (
        u"", u"січ.", u"лют.", u"бер.", u"квіт.", u"трав.", u"черв.",
        u"лип.", u"серп.", u"вер.", u"жовт.", u"лист.", u"груд."
        )

    hebrew = (
        u"", u"тішрі", u"хешвен", u"кіслев", u"тевет", u"шват",
        u"адар", u"адара", u"нісан", u"іяр", u"сиван", u"таммуз",
        u"ав", u"елул"
        )

    french = (
        u'', u'вандем’єр', u'брюмер', u'фрімер', u'нівоз',
        u'плювіоз', u'вентоз', u'жерміналь', u'флореаль',
        u'преріаль', u'мессідор', u'термідор', u'фрюктідор',
        u'додатковий'
        )

    persian = (
        u"", u"фарвардін", u"ордібехешт", u"хордад", u"тир",
        u"мордад", u"шахрівар", u"мехр", u"абан",
        u"азар", u"дей", u"бахман", u"есфанд"
        )

    islamic = (
        u"", u"мухаррам", u"сафар",  u"рабі-аль-авваль",
        u"рабі-ассані", u"джумада-аль-уля", u"джумада-аль-ахіра",
        u"раджаб",  u"шаабан", u"рамадан", u"шавваль", u"зуль-каада",
        u"зуль-хіджжа",
        )

    # Replace the previous "Numerical" by a string which
    # do have an explicit meaning: "System default (format)"
    import GrampsLocale
    _locale_tformat = GrampsLocale.tformat
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
        u"", u"юліанський", u"єврейський", u"французький республіканський",
        u"іранський", u"ісламський", u"шведський"
        )

    _mod_str = (u"", u"до ", u"після ", u"близько ", u"", u"", u"")

    _qual_str = (u"", u"орієнтовно ", u"розрахунково ")

    _bce_str = u"%s до н.е."

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
            return "%sз %s %s %s%s" % (qual_str, d1, u'по', d2,
                                       scal)
        elif mod == Date.MOD_RANGE:
            d1 = self.display_cal[cal](start)
            d2 = self.display_cal[cal](date.get_stop_date())
            scal = self.format_extras(cal, newyear)
            return "%s%s %s %s %s%s" % (qual_str, u'між', d1, u'та',
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
register_datehandler(('uk_UA', 'uk', 'ukrainian', 'Ukrainian'), DateParserUK, DateDisplayUK)

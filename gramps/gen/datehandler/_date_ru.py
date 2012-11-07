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
Russian-specific classes for parsing and displaying dates.
"""
from __future__ import unicode_literals
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
from ..lib.date import Date
from ._dateparser import DateParser
from ._datedisplay import DateDisplay
from ._datehandler import register_datehandler

#-------------------------------------------------------------------------
#
# Russian parser
#
#-------------------------------------------------------------------------
class DateParserRU(DateParser):

    modifier_to_int = {
        'перед'    : Date.MOD_BEFORE, 
        'по'    : Date.MOD_BEFORE, 
        'после' : Date.MOD_AFTER, 
        'п.'    : Date.MOD_AFTER, 
        'п'    : Date.MOD_AFTER, 
        'с'     : Date.MOD_AFTER, 
        'ок' : Date.MOD_ABOUT, 
        'ок.'   : Date.MOD_ABOUT, 
        'около'    : Date.MOD_ABOUT, 
        'примерно'  : Date.MOD_ABOUT, 
        'прим'     : Date.MOD_ABOUT, 
        'прим.'     : Date.MOD_ABOUT, 
        'приблизительно'  : Date.MOD_ABOUT, 
        'приб.'  : Date.MOD_ABOUT, 
        'прибл.'  : Date.MOD_ABOUT, 
        'приб'  : Date.MOD_ABOUT, 
        'прибл'  : Date.MOD_ABOUT, 
        }

    calendar_to_int = {
        'григорианский' : Date.CAL_GREGORIAN, 
        'г'            : Date.CAL_GREGORIAN, 
        'юлианский'     : Date.CAL_JULIAN, 
        'ю'            : Date.CAL_JULIAN, 
        'еврейский'         : Date.CAL_HEBREW, 
        'е'         : Date.CAL_HEBREW, 
        'исламский'         : Date.CAL_ISLAMIC, 
        'и'                 : Date.CAL_ISLAMIC, 
        'республиканский': Date.CAL_FRENCH, 
        'р'                 : Date.CAL_FRENCH, 
        'персидский'             : Date.CAL_PERSIAN, 
        'п'             : Date.CAL_PERSIAN, 
        'swedish'      : Date.CAL_SWEDISH, 
        's'            : Date.CAL_SWEDISH, 
        }

    quality_to_int = {
        'оценено'  : Date.QUAL_ESTIMATED, 
        'оцен.'       : Date.QUAL_ESTIMATED, 
        'оц.'        : Date.QUAL_ESTIMATED, 
        'оцен'       : Date.QUAL_ESTIMATED, 
        'оц'        : Date.QUAL_ESTIMATED, 
        'вычислено'      : Date.QUAL_CALCULATED, 
        'вычисл.'       : Date.QUAL_CALCULATED, 
        'выч.' : Date.QUAL_CALCULATED, 
        'вычисл'       : Date.QUAL_CALCULATED, 
        'выч' : Date.QUAL_CALCULATED, 
        }

    hebrew_to_int = {
        "тишрей":1, 
        "тишрея":1, 
        "хешван":2, 
        "хешвана":2, 
        "кислев":3, 
        "кислева":3, 
        "тевет":4, 
        "тевета":4, 
        "шеват":5, 
        "шевата":5, 
        "адар":6, 
        "адара":6, 
        "адара бет":7, 
        "нисан":8, 
        "нисана":8, 
        "ниссан":8, 
        "ниссана":8, 
        "ияр":9, 
        "ияра":9, 
        "сиван":10, 
        "сивана":10, 
        "тамуз":11, 
        "тамуза":11, 
        "таммуз":11, 
        "таммуза":11, 
        "ав":12, 
        "ава":12, 
        "элул":13, 
        "элула":13, 
        "элуль":13, 
        "элуля":13, 
    }

    islamic_to_int = {
        "мухаррам":1, 
        "мухаррама":1, 
        "сафар":2, 
        "сафара":2, 
        "раби-аль-авваль":3, 
        "раби-аль-авваля":3, 
        "раби-ассани":4, 
        "джумада-аль-уля":5, 
        "джумада-аль-ахира":6, 
        "раджаб":7, 
        "раджаба":7, 
        "шаабан":8, 
        "шаабана":8, 
        "рамадан":9, 
        "рамадана":9, 
        "шавваль":10, 
        "шавваля":10, 
        "зуль-каада":11, 
        "зуль-хиджжа":12, 
        }

    persian_to_int = {
        "фарвардин":1, 
        "фарвардина":1, 
        "урдбихишт":2, 
        "урдбихишта":2, 
        "хурдад":3, 
        "хурдада":3, 
        "тир":4, 
        "тира":4, 
        "мурдад":5, 
        "мурдада":5, 
        "шахривар":6, 
        "шахривара":6, 
        "михр":7, 
        "михра":7, 
        "абан":8, 
        "абана":8, 
        "азар":9, 
        "азара":9, 
        "дай":10, 
        "дая":10, 
        "бахман":11, 
        "бахмана":11, 
        "исфаидармуз":12, 
        "исфаидармуза":12, 
        }

    french_to_int = {
        "вандемьер":1, 
        "вандемьера":1, 
        "брюмер":2, 
        "брюмера":2, 
        "фример":3, 
        "фримера":3, 
        "нивоз":4, 
        "нивоза":4, 
        "плювиоз":5, 
        "плювиоза":5, 
        "вантоз":6, 
        "вантоза":6, 
        "жерминаль":7, 
        "жерминаля":7, 
        "флореаль":8, 
        "флореаля":8, 
        "прериаль":9, 
        "прериаля":9, 
        "мессидор":10, 
        "мессидора":10, 
        "термидор":11, 
        "термидора":11, 
        "фрюктидор":12, 
        "фрюктидора":12, 
        "доп.":13, 
        "дополн.":13, 
        "дополнит.":13, 
        }

    bce = [
        'до нашей эры', 'до н. э.', 'до н.э.', 
        'до н э', 'до нэ'] + DateParser.bce

    def init_strings(self):
        DateParser.init_strings(self)
        _span_1 = ['с', 'от']
        _span_2 = ['по']
        _range_1 = ['между', 'меж\.', 'меж']
        _range_2 = ['и']
        self._span     = re.compile("(%s)\s+(?P<start>.+)\s+(%s)\s+(?P<stop>.+)" % 
                                    ('|'.join(_span_1), '|'.join(_span_2)), 
                                    re.IGNORECASE)
        self._range    = re.compile("(%s)\s+(?P<start>.+)\s+(%s)\s+(?P<stop>.+)" %
                                    ('|'.join(_range_1), '|'.join(_range_2)), 
                                    re.IGNORECASE)
        
#-------------------------------------------------------------------------
#
# Russian displayer
#
#-------------------------------------------------------------------------
class DateDisplayRU(DateDisplay):
    """
    Russian language date display class. 
    """
    long_months = ( "", "января", "февраля", "марта", "апреля", "мая", 
                    "июня", "июля", "августа", "сентября", "октября", 
                    "ноября", "декабря" )
    
    short_months = ( "", "янв", "фев", "мар", "апр", "мая", "июн", 
                     "июл", "авг", "сен", "окт", "ноя", "дек" )
    
    calendar = (
        "", 
        "юлианский", 
        "еврейский", 
        "республиканский", 
        "персидский", 
        "исламский", 
        "шведский" 
        )

    _mod_str = (
        "", 
        "перед ", 
        "после ", 
        "около ", 
        "", "", "")
    
    _qual_str = ("", "оцен ", "вычисл ")

    _bce_str = "%s до н.э."

    formats = (
        "ГГГГ-ММ-ДД (ISO)", "Численный", "Месяц День, Год", 
        "МЕС ДД, ГГГГ", "День Месяц, Год", "ДД МЕС, ГГГГ"
        )

    hebrew = ( "", 
        "тишрея", 
        "хешвана", 
        "кислева", 
        "тевета", 
        "шевата", 
        "адара", 
        "адара бет", 
        "нисана", 
        "ияра", 
        "сивана", 
        "таммуза", 
        "ава", 
        "элула", 
        )

    islamic = ( "", 
        "мухаррама", 
        "сафара", 
        "раби-аль-авваля", 
        "раби-ассани", 
        "джумада-аль-уля", 
        "джумада-аль-ахира", 
        "раджаба", 
        "шаабана", 
        "рамадана", 
        "шавваля", 
        "зуль-каада", 
        "зуль-хиджжа", 
        )

    persian = ( "", 
        "фарвардина", 
        "урдбихишта", 
        "хурдада", 
        "тира", 
        "мурдада", 
        "шахривара", 
        "михра", 
        "абана", 
        "азара", 
        "дая", 
        "бахмана", 
        "исфаидармуза", 
        )

    french = ( "", 
        "вандемьера", 
        "брюмера", 
        "фримера", 
        "нивоза", 
        "плювиоза", 
        "вантоза", 
        "жерминаля", 
        "флореаля", 
        "прериаля", 
        "мессидора", 
        "термидора", 
        "фрюктидора", 
        "дополнит."
        )

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
            return "%sс %s %s %s%s" % (qual_str, d1, 'по', d2, 
                                       scal)
        elif mod == Date.MOD_RANGE:
            d1 = self.display_cal[cal](start)
            d2 = self.display_cal[cal](date.get_stop_date())
            scal = self.format_extras(cal, newyear)
            return "%s%s %s %s %s%s" % (qual_str, 'между', d1, 'и', 
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
register_datehandler(('ru_RU', 'ru', 'russian', 'Russian'), DateParserRU, DateDisplayRU)

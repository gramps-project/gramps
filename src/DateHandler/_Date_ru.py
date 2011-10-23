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
# Russian parser
#
#-------------------------------------------------------------------------
class DateParserRU(DateParser):

    modifier_to_int = {
        u'перед'    : Date.MOD_BEFORE, 
        u'по'    : Date.MOD_BEFORE, 
        u'после' : Date.MOD_AFTER, 
        u'п.'    : Date.MOD_AFTER, 
        u'п'    : Date.MOD_AFTER, 
        u'с'     : Date.MOD_AFTER, 
        u'ок' : Date.MOD_ABOUT, 
        u'ок.'   : Date.MOD_ABOUT, 
        u'около'    : Date.MOD_ABOUT, 
        u'примерно'  : Date.MOD_ABOUT, 
        u'прим'     : Date.MOD_ABOUT, 
        u'прим.'     : Date.MOD_ABOUT, 
        u'приблизительно'  : Date.MOD_ABOUT, 
        u'приб.'  : Date.MOD_ABOUT, 
        u'прибл.'  : Date.MOD_ABOUT, 
        u'приб'  : Date.MOD_ABOUT, 
        u'прибл'  : Date.MOD_ABOUT, 
        }

    calendar_to_int = {
        u'григорианский' : Date.CAL_GREGORIAN, 
        u'г'            : Date.CAL_GREGORIAN, 
        u'юлианский'     : Date.CAL_JULIAN, 
        u'ю'            : Date.CAL_JULIAN, 
        u'еврейский'         : Date.CAL_HEBREW, 
        u'е'         : Date.CAL_HEBREW, 
        u'исламский'         : Date.CAL_ISLAMIC, 
        u'и'                 : Date.CAL_ISLAMIC, 
        u'республиканский': Date.CAL_FRENCH, 
        u'р'                 : Date.CAL_FRENCH, 
        u'персидский'             : Date.CAL_PERSIAN, 
        u'п'             : Date.CAL_PERSIAN, 
        u'swedish'      : Date.CAL_SWEDISH, 
        u's'            : Date.CAL_SWEDISH, 
        }

    quality_to_int = {
        u'оценено'  : Date.QUAL_ESTIMATED, 
        u'оцен.'       : Date.QUAL_ESTIMATED, 
        u'оц.'        : Date.QUAL_ESTIMATED, 
        u'оцен'       : Date.QUAL_ESTIMATED, 
        u'оц'        : Date.QUAL_ESTIMATED, 
        u'вычислено'      : Date.QUAL_CALCULATED, 
        u'вычисл.'       : Date.QUAL_CALCULATED, 
        u'выч.' : Date.QUAL_CALCULATED, 
        u'вычисл'       : Date.QUAL_CALCULATED, 
        u'выч' : Date.QUAL_CALCULATED, 
        }

    hebrew_to_int = {
        u"тишрей":1, 
        u"тишрея":1, 
        u"хешван":2, 
        u"хешвана":2, 
        u"кислев":3, 
        u"кислева":3, 
        u"тевет":4, 
        u"тевета":4, 
        u"шеват":5, 
        u"шевата":5, 
        u"адар":6, 
        u"адара":6, 
        u"адара бет":7, 
        u"нисан":8, 
        u"нисана":8, 
        u"ниссан":8, 
        u"ниссана":8, 
        u"ияр":9, 
        u"ияра":9, 
        u"сиван":10, 
        u"сивана":10, 
        u"тамуз":11, 
        u"тамуза":11, 
        u"таммуз":11, 
        u"таммуза":11, 
        u"ав":12, 
        u"ава":12, 
        u"элул":13, 
        u"элула":13, 
        u"элуль":13, 
        u"элуля":13, 
    }

    islamic_to_int = {
        u"мухаррам":1, 
        u"мухаррама":1, 
        u"сафар":2, 
        u"сафара":2, 
        u"раби-аль-авваль":3, 
        u"раби-аль-авваля":3, 
        u"раби-ассани":4, 
        u"джумада-аль-уля":5, 
        u"джумада-аль-ахира":6, 
        u"раджаб":7, 
        u"раджаба":7, 
        u"шаабан":8, 
        u"шаабана":8, 
        u"рамадан":9, 
        u"рамадана":9, 
        u"шавваль":10, 
        u"шавваля":10, 
        u"зуль-каада":11, 
        u"зуль-хиджжа":12, 
        }

    persian_to_int = {
        u"фарвардин":1, 
        u"фарвардина":1, 
        u"урдбихишт":2, 
        u"урдбихишта":2, 
        u"хурдад":3, 
        u"хурдада":3, 
        u"тир":4, 
        u"тира":4, 
        u"мурдад":5, 
        u"мурдада":5, 
        u"шахривар":6, 
        u"шахривара":6, 
        u"михр":7, 
        u"михра":7, 
        u"абан":8, 
        u"абана":8, 
        u"азар":9, 
        u"азара":9, 
        u"дай":10, 
        u"дая":10, 
        u"бахман":11, 
        u"бахмана":11, 
        u"исфаидармуз":12, 
        u"исфаидармуза":12, 
        }

    french_to_int = {
        u"вандемьер":1, 
        u"вандемьера":1, 
        u"брюмер":2, 
        u"брюмера":2, 
        u"фример":3, 
        u"фримера":3, 
        u"нивоз":4, 
        u"нивоза":4, 
        u"плювиоз":5, 
        u"плювиоза":5, 
        u"вантоз":6, 
        u"вантоза":6, 
        u"жерминаль":7, 
        u"жерминаля":7, 
        u"флореаль":8, 
        u"флореаля":8, 
        u"прериаль":9, 
        u"прериаля":9, 
        u"мессидор":10, 
        u"мессидора":10, 
        u"термидор":11, 
        u"термидора":11, 
        u"фрюктидор":12, 
        u"фрюктидора":12, 
        u"доп.":13, 
        u"дополн.":13, 
        u"дополнит.":13, 
        }

    bce = [
        u'до нашей эры', u'до н. э.', u'до н.э.', 
        u'до н э', u'до нэ'] + DateParser.bce

    def init_strings(self):
        DateParser.init_strings(self)
        _span_1 = [u'с', u'от']
        _span_2 = [u'по']
        _range_1 = [u'между', u'меж\.', u'меж']
        _range_2 = [u'и']
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
    long_months = ( u"", u"января", u"февраля", u"марта", u"апреля", u"мая", 
                    u"июня", u"июля", u"августа", u"сентября", u"октября", 
                    u"ноября", u"декабря" )
    
    short_months = ( u"", u"янв", u"фев", u"мар", u"апр", u"мая", u"июн", 
                     u"июл", u"авг", u"сен", u"окт", u"ноя", u"дек" )
    
    calendar = (
        u"", 
        u"юлианский", 
        u"еврейский", 
        u"республиканский", 
        u"персидский", 
        u"исламский", 
        u"шведский" 
        )

    _mod_str = (
        u"", 
        u"перед ", 
        u"после ", 
        u"около ", 
        u"", u"", u"")
    
    _qual_str = (u"", u"оцен ", u"вычисл ")

    _bce_str = u"%s до н.э."

    formats = (
        "ГГГГ-ММ-ДД (ISO)", "Численный", "Месяц День, Год", 
        "МЕС ДД, ГГГГ", "День Месяц, Год", "ДД МЕС, ГГГГ"
        )

    hebrew = ( u"", 
        u"тишрея", 
        u"хешвана", 
        u"кислева", 
        u"тевета", 
        u"шевата", 
        u"адара", 
        u"адара бет", 
        u"нисана", 
        u"ияра", 
        u"сивана", 
        u"таммуза", 
        u"ава", 
        u"элула", 
        )

    islamic = ( u"", 
        u"мухаррама", 
        u"сафара", 
        u"раби-аль-авваля", 
        u"раби-ассани", 
        u"джумада-аль-уля", 
        u"джумада-аль-ахира", 
        u"раджаба", 
        u"шаабана", 
        u"рамадана", 
        u"шавваля", 
        u"зуль-каада", 
        u"зуль-хиджжа", 
        )

    persian = ( u"", 
        u"фарвардина", 
        u"урдбихишта", 
        u"хурдада", 
        u"тира", 
        u"мурдада", 
        u"шахривара", 
        u"михра", 
        u"абана", 
        u"азара", 
        u"дая", 
        u"бахмана", 
        u"исфаидармуза", 
        )

    french = ( u"", 
        u"вандемьера", 
        u"брюмера", 
        u"фримера", 
        u"нивоза", 
        u"плювиоза", 
        u"вантоза", 
        u"жерминаля", 
        u"флореаля", 
        u"прериаля", 
        u"мессидора", 
        u"термидора", 
        u"фрюктидора", 
        u"дополнит."
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
            return "%sс %s %s %s%s" % (qual_str, d1, u'по', d2, 
                                       scal)
        elif mod == Date.MOD_RANGE:
            d1 = self.display_cal[cal](start)
            d2 = self.display_cal[cal](date.get_stop_date())
            scal = self.format_extras(cal, newyear)
            return "%s%s %s %s %s%s" % (qual_str, u'между', d1, u'и', 
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

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
Bulgarian-specific classes for parsing and displaying dates.
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
# Bulgarian parser
#
#-------------------------------------------------------------------------
class DateParserBG(DateParser):

    modifier_to_int = {
        u'преди'          : Date.MOD_BEFORE, 
        u'пр.'            : Date.MOD_BEFORE,
        u'пр'             : Date.MOD_BEFORE,
        u'след'           : Date.MOD_AFTER,
        u'сл.'            : Date.MOD_AFTER,
        u'сл'             : Date.MOD_AFTER,
        u'ок'             : Date.MOD_ABOUT,
        u'ок.'            : Date.MOD_ABOUT,
        u'около'          : Date.MOD_ABOUT,
        u'примерно'       : Date.MOD_ABOUT,
        u'прим'           : Date.MOD_ABOUT,
        u'прим.'          : Date.MOD_ABOUT,
        u'приблизително'  : Date.MOD_ABOUT,
        u'приб.'          : Date.MOD_ABOUT,
        u'прибл.'         : Date.MOD_ABOUT,
        u'приб'           : Date.MOD_ABOUT,
        u'прибл'          : Date.MOD_ABOUT,
        }

    calendar_to_int = {
        u'григориански'          : Date.CAL_GREGORIAN, 
        u'г'                     : Date.CAL_GREGORIAN, 
        u'юлиански'              : Date.CAL_JULIAN, 
        u'ю'                     : Date.CAL_JULIAN, 
        u'еврейски'              : Date.CAL_HEBREW, 
        u'е'                     : Date.CAL_HEBREW, 
        u'ислямски'              : Date.CAL_ISLAMIC, 
        u'и'                     : Date.CAL_ISLAMIC, 
        u'френски републикански' : Date.CAL_FRENCH, 
        u'републикански'         : Date.CAL_FRENCH,
        u'фр.реп.'               : Date.CAL_FRENCH,
        u'р'                     : Date.CAL_FRENCH,
        u'френски'               : Date.CAL_FRENCH,
        u'фр.'                   : Date.CAL_FRENCH,
        u'персийски'             : Date.CAL_PERSIAN, 
        u'п'                     : Date.CAL_PERSIAN, 
        }

    quality_to_int = {
        u'приблизително'  : Date.QUAL_ESTIMATED,
        u'прибл.'         : Date.QUAL_ESTIMATED,
        u'изчислено'      : Date.QUAL_CALCULATED,
        u'изчисл.'        : Date.QUAL_CALCULATED,
        u'изч.'           : Date.QUAL_CALCULATED,
        }

    hebrew_to_int = {
        u"тишрей":1, 
        u"мархешван":2, 
        u"кислев":3, 
        u"тевет":4, 
        u"шват":5, 
        u"адар":6, 
        u"адар бет":7, 
        u"нисан":8, 
        u"ияр":9, 
        u"сиван":10, 
        u"тамуз":11, 
        u"ав":12, 
        u"eлул":13, 
    }

    islamic_to_int = { 
        u"мухаррам":1, 
        u"саффар":2, 
        u"рабиу-л-ауал":3, 
        u"рабиу-с-сани":4, 
        u"джумадал-уля":5, 
        u"джумада-с-сания":6, 
        u"раджаб":7, 
        u"шаабан":8, 
        u"рамадан":9, 
        u"шауал":10, 
        u"зу-л-кида":11, 
        u"зул-л-хиджа":12, 
        }

    persian_to_int = {
        u"фарвардин":1, 
        u"урдбихищ":2, 
        u"хурдад":3, 
        u"тир":4, 
        u"мурдад":5, 
        u"шахривар":6, 
        u"михр":7, 
        u"абан":8, 
        u"азар":9, 
        u"дай":10, 
        u"бахман":11, 
        u"исфаидармуз":12, 
        }

    french_to_int = {
        u"вандемер":1, 
        u"брюмер":2, 
        u"фример":3, 
        u"нивоз":4, 
        u"плювиоз":5, 
        u"вантоз":6, 
        u"жерминал":7, 
        u"флореал":8, 
        u"прериал":9, 
        u"месидор":10, 
        u"термидор":11, 
        u"фрюктидор":12, 
        u"допълнителен":13, 
        }

    bce = [
        u'преди Христа', u'пр. Хр.', u'пр.Хр.'
        ] + DateParser.bce

    def init_strings(self):
        DateParser.init_strings(self)
        _span_1 = [u'от']
        _span_2 = [u'до']
        _range_1 = [u'между']
        _range_2 = [u'и']
        self._span =  re.compile("(%s)\s+(?P<start>.+)\s+(%s)\s+(?P<stop>.+)" %
                                 ('|'.join(_span_1), '|'.join(_span_2)), 
                                 re.IGNORECASE)
        self._range = re.compile("(%s)\s+(?P<start>.+)\s+(%s)\s+(?P<stop>.+)" %
                                 ('|'.join(_range_1), '|'.join(_range_2)), 
                                 re.IGNORECASE)
        
#-------------------------------------------------------------------------
#
# Bulgarian displayer
#
#-------------------------------------------------------------------------
class DateDisplayBG(DateDisplay):
    """
    Bulgarian language date display class. 
    """
    long_months = ( u"", u"януари", u"февруари", u"март", u"април", u"май", 
                    u"юни", u"юли", u"август", u"септември", u"октомври", 
                    u"ноември", u"декември" )
    
    short_months = ( u"", u"яну", u"февр", u"март", u"апр", u"май", u"юни", 
                     u"юли", u"авг", u"септ", u"окт", u"ное", u"дек" )
    

    calendar = (
        u"", 
        u"юлиански", 
        u"еврейски", 
        u"републикански", 
        u"персийски", 
        u"ислямски",
        u"шведски"
        )

    _mod_str = ("", "преди ", "след ", "около ", "", "", "")
    
    _qual_str = ("", "приблизително ", "изчислено ")

    _bce_str = u"%s пр. Хр."

    formats = (
        "ГГГГ-ММ-ДД (ISO)", "Числов", "Месец Ден, Година", "Мес. Ден, Година", "Ден Месец Година", "Ден Мес. Година"
        )
        # this must agree with DateDisplayEn's "formats" definition
        # (since no locale-specific _display_gregorian exists, here)

    hebrew = ( u"", 
        u"Тишрей", 
        u"Мархешван", 
        u"Кислев", 
        u"Тевет", 
        u"Шват", 
        u"Адар", 
        u"Адар бет", 
        u"Нисан", 
        u"Ияр", 
        u"Сиван", 
        u"Тамуз", 
        u"Ав", 
        u"Елул", 
        )

    islamic = ( u"", 
        u"Мухаррам", 
        u"Саффар", 
        u"Рабиу-л-ауал", 
        u"Рабиу-с-сани", 
        u"Джумадал-уля", 
        u"Джумада-с-сания", 
        u"Раджаб", 
        u"Шаабан", 
        u"Рамадан", 
        u"Шауал", 
        u"Зу-л-кида", 
        u"Зул-л-хиджа", 
        )

    persian = ( u"", 
        u"Фарвардин", 
        u"Урдбихищ", 
        u"Хурдад", 
        u"Тир", 
        u"Мурдад", 
        u"Шахривар", 
        u"Михр", 
        u"Абан", 
        u"Азар", 
        u"Дай", 
        u"Бахман", 
        u"Исфаидармуз", 
        )

    french = ( u"", 
        u"Вандемер", 
        u"Брюмер", 
        u"Фример", 
        u"Нивоз", 
        u"Плювиоз", 
        u"Вантоз", 
        u"Жерминал", 
        u"Флореал", 
        u"Прериал", 
        u"Мессидор", 
        u"Термидор", 
        u"Фрюктидор", 
        u"Допълнителен"
        )

    def display(self, date):
        """
        Returns a text string representing the date.
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
            return "%s%s %s %s %s%s" % (qual_str, u'от', d1, u'до', d2, scal)
        elif mod == Date.MOD_RANGE:
            d1 = self.display_cal[cal](start)
            d2 = self.display_cal[cal](date.get_stop_date())
            scal = self.format_extras(cal, newyear)
            return "%s%s %s %s %s%s" % (qual_str, u'между', d1, u'и', d2, scal)
        else:
            text = self.display_cal[date.get_calendar()](start)
            scal = self.format_extras(cal, newyear)
            return "%s%s%s%s" % (qual_str, self._mod_str[mod], text, scal)

#-------------------------------------------------------------------------
#
# Register classes
#
#-------------------------------------------------------------------------
register_datehandler(('bg_BG', 'bg', 'bulgarian', 'Bulgarian'), 
    DateParserBG, DateDisplayBG)

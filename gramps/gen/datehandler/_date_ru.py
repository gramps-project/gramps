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
        'до'    : Date.MOD_BEFORE, 
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

    bce = [
        'до нашей эры', 'до н. э.', 'до н.э.', 
        'до н э', 'до нэ'] + DateParser.bce

    def init_strings(self):
        DateParser.init_strings(self)
        DateParser.calendar_to_int.update({
            'персидский'    : Date.CAL_PERSIAN, 
            'п'             : Date.CAL_PERSIAN, 
        })
        _span_1 = ['с', 'от']
        #_span_2 = ['по', 'до'] # <-- clashes with bce parsing :-(
        _span_2 = ['по']
        _range_1 = ['между', 'меж\.', 'меж']
        _range_2 = ['и']
        self._span =  re.compile("(%s)\s+(?P<start>.+)\s+(%s)\s+(?P<stop>.+)" %
                                 ('|'.join(_span_1), '|'.join(_span_2)),
                                 re.IGNORECASE)
        self._range = re.compile("(%s)\s+(?P<start>.+)\s+(%s)\s+(?P<stop>.+)" %
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

    # TODO fix BUG 7064: non-Gregorian calendars wrongly use BCE notation for negative dates
    # not refactoring _bce_str into base class because it'll be gone under #7064
    _bce_str = "%s до н.э."

    display = DateDisplay.display_formatted

#-------------------------------------------------------------------------
#
# Register classes
#
#-------------------------------------------------------------------------
register_datehandler(('ru_RU', 'ru', 'russian', 'Russian'), DateParserRU, DateDisplayRU)

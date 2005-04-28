# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2005  Donald N. Allingham
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
Finnish-specific classes for parsing and displaying dates.
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
import Date
from DateParser import DateParser
from DateDisplay import DateDisplay

#-------------------------------------------------------------------------
#
# Finnish parser
#
#-------------------------------------------------------------------------
class DateParserFI(DateParser):

    modifier_to_int = {
        u'ennen'   : Date.MOD_BEFORE, 
        u'e.'      : Date.MOD_BEFORE, 
        u'jälkeen' : Date.MOD_AFTER,
        u'j.'      : Date.MOD_AFTER,
        u'noin'    : Date.MOD_ABOUT,
        u'n.'      : Date.MOD_ABOUT,
        }

    calendar_to_int = {
        u'gregoriaaninen'  : Date.CAL_GREGORIAN,
        u'greg.'           : Date.CAL_GREGORIAN,
        u'juliaaninen'     : Date.CAL_JULIAN,
        u'jul.'            : Date.CAL_JULIAN,
        u'heprealainen'    : Date.CAL_HEBREW,
        u'hepr.'           : Date.CAL_HEBREW,
        u'islamilainen'    : Date.CAL_ISLAMIC,
        u'isl.'            : Date.CAL_ISLAMIC,
        u'ranskan vallankumouksen aikainen': Date.CAL_FRENCH,
        u'ranskan v.'      : Date.CAL_FRENCH,
        u'persialainen'    : Date.CAL_PERSIAN,
        u'pers.'           : Date.CAL_PERSIAN,
        }

    quality_to_int = {
        u'arvioitu'   : Date.QUAL_ESTIMATED,
        u'arv.'       : Date.QUAL_ESTIMATED,
        u'laskettu'   : Date.QUAL_CALCULATED,
        u'lask.'      : Date.QUAL_CALCULATED,
        }

    def init_strings(self):
        DateParser.init_strings(self)
        _span_1 = [u'de']
        _span_2 = [u'a']
        _range_1 = [u'ent.',u'ent',u'entre']
        _range_2 = [u'y']
        self._span     = re.compile("(%s)\s+(.+)\s+(%s)\s+(.+)" % 
                                   ('|'.join(_span_1),'|'.join(_span_2)),
                           re.IGNORECASE)
        self._range    = re.compile("(%s)\s+(.+)\s+(%s)\s+(.+)" %
                                   ('|'.join(_range_1),'|'.join(_range_2)),
                           re.IGNORECASE)

#-------------------------------------------------------------------------
#
# Finnish display
#
#-------------------------------------------------------------------------
class DateDisplayFI(DateDisplay):

    calendar = ("",
        u" (Juliaaninen)",
	u" (Heprealainen)", 
        u" (Ranskan v.)",
	u" (Persialainen)",
	u" (Islamilainen)")

    _mod_str = ("", u"ennen ", u"jälkeen ", u"noin ", "", "", "")

    _qual_str = ("", "laskettu ", "arvioitu ")

    formats = (
        "VVVV-KK-PP (ISO)",
	"Numeroina",
	"Kuukausi Päivä, Vuosi",
        "KUUKAUSI Päivä, Vuosi",
        "Päivä Kuukausi, Vuosi",
        "Päivä KUUKAUSI, Vuosi"
        )
    
    def display(self,date):
        """
        Returns a text string representing the date.
        """
        mod = date.get_modifier()
        cal = date.get_calendar()
        qual = date.get_quality()
        start = date.get_start_date()

        qual_str = self._qual_str[qual]
        
        if mod == Date.MOD_TEXTONLY:
            return date.get_text()
        elif start == Date.EMPTY:
            return ""
        elif mod == Date.MOD_SPAN:
            d1 = self.display_cal[cal](start)
            d2 = self.display_cal[cal](date.get_stop_date())
            return "%s%s %s %s %s%s" % (qual_str,u'de',d1,u'a',d2,self.calendar[cal])
        elif mod == Date.MOD_RANGE:
            d1 = self.display_cal[cal](start)
            d2 = self.display_cal[cal](date.get_stop_date())
            return "%s%s %s %s %s%s" % (qual_str,u'entre',d1,u'y',d2,self.calendar[cal])
        else:
            text = self.display_cal[date.get_calendar()](start)
            return "%s%s%s%s" % (qual_str,self._mod_str[mod],text,self.calendar[cal])

#-------------------------------------------------------------------------
#
# Register classes
#
#-------------------------------------------------------------------------
from DateHandler import register_datehandler
register_datehandler(('fi_FI','finnish'), DateParserFI, DateDisplayFI)


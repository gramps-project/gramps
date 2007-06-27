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
from RelLib import Date
from _DateParser import DateParser
from _DateDisplay import DateDisplay
from _DateHandler import register_datehandler

#-------------------------------------------------------------------------
#
# Finnish parser
#
# This handles only dates where days and months are given as numeric, as:
# - That's how they are normally used in Finland
# - Parsing Finnish is much more complicated than English
#-------------------------------------------------------------------------
class DateParserFI(DateParser):

    # NOTE: these need to be in lower case because the "key" comparison
    # is done as lower case.  In the display method correct capitalization
    # can be used.
    
    modifier_to_int = {
        # examples:
	# - ennen 1.1.2005
	# - noin 1.1.2005
        u'ennen'   : Date.MOD_BEFORE, 
        u'e.'      : Date.MOD_BEFORE, 
        u'noin'    : Date.MOD_ABOUT, 
        u'n.'      : Date.MOD_ABOUT, 
        }
    modifier_after_to_int = {
        # examples:
	# - 1.1.2005 jälkeen
        u'jälkeen' : Date.MOD_AFTER, 
        u'j.'      : Date.MOD_AFTER, 
        }

    bce = [u"ekr.", u"ekr"]

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
        u'arviolta'   : Date.QUAL_ESTIMATED, 
        u'arv.'       : Date.QUAL_ESTIMATED, 
        u'laskettuna' : Date.QUAL_CALCULATED, 
        u'lask.'      : Date.QUAL_CALCULATED, 
        }

    def init_strings(self):
        DateParser.init_strings(self)
	# date, whitespace
        self._span = re.compile(u"(?P<start>.+)\s+(-)\s+(?P<stop>.+)", 
                           re.IGNORECASE)
        self._range = re.compile(
            u"(vuosien\s*)?(?P<start>.+)\s+ja\s+(?P<stop>.+)\s+välillä", 
            re.IGNORECASE)

#-------------------------------------------------------------------------
#
# Finnish display
#
#-------------------------------------------------------------------------
class DateDisplayFI(DateDisplay):

    calendar = ("", 
        u"(juliaaninen)", 
	u"(heprealainen)", 
        u"(ranskan v.)", 
	u"(persialainen)", 
	u"(islamilainen)")

    _qual_str = (u"", u"arviolta", u"laskettuna")
    
    _bce_str = u"%s ekr."

    formats = (
        "VVVV-KK-PP (ISO)", 
	"PP.KK.VVVV"
        )
    
    def display(self, date):
        """
        Returns a text string representing the date.
        """
        mod = date.get_modifier()
        qual = date.get_quality()
        cal = date.get_calendar()
        start = date.get_start_date()
        
        if mod == Date.MOD_TEXTONLY:
            return date.get_text()
        if start == Date.EMPTY:
            return u""

	# select numerical date format
	self.format = 1
	
        if mod == Date.MOD_SPAN:
            d1 = self.display_cal[cal](start)
            d2 = self.display_cal[cal](date.get_stop_date())
            text = u"%s - %s" % (d1, d2)
        elif mod == Date.MOD_RANGE:
            stop = date.get_stop_date()
            if start[0] == 0 and start[1] == 0 and stop[0] == 0 and stop[1] == 0:
                d1 = self.display_cal[cal](start)
                d2 = self.display_cal[cal](stop)
                text = u"vuosien %s ja %s välillä" % (d1, d2)
            else:
                d1 = self.display_cal[cal](start)
                d2 = self.display_cal[cal](stop)
                text = u"%s ja %s välillä" % (d1, d2)
        else:
            text = self.display_cal[date.get_calendar()](start)
            if mod == Date.MOD_AFTER:
                text = text + u" jälkeen"
            elif mod == Date.MOD_ABOUT:
                text = u"noin " + text
            elif mod == Date.MOD_BEFORE:
                text = u"ennen " + text
	
        if qual:
            # prepend quality
            text = u"%s %s" % (self._qual_str[qual], text)
        if cal:
            # append calendar type
            text = u"%s %s" % (text, self.calendar[cal])
	    
	return text

#-------------------------------------------------------------------------
#
# Register classes
#
#-------------------------------------------------------------------------
register_datehandler(('fi_FI', 'fi', 'finnish'), DateParserFI, DateDisplayFI)

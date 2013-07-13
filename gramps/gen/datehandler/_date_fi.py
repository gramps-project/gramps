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
        'ennen'   : Date.MOD_BEFORE, 
        'e.'      : Date.MOD_BEFORE, 
        'noin'    : Date.MOD_ABOUT, 
        'n.'      : Date.MOD_ABOUT, 
        }
    modifier_after_to_int = {
        # examples:
	# - 1.1.2005 jälkeen
        'jälkeen' : Date.MOD_AFTER, 
        'j.'      : Date.MOD_AFTER, 
        }

    bce = ["ekr.", "ekr"]

    calendar_to_int = {
        'gregoriaaninen'  : Date.CAL_GREGORIAN, 
        'greg.'           : Date.CAL_GREGORIAN, 
        'juliaaninen'     : Date.CAL_JULIAN, 
        'jul.'            : Date.CAL_JULIAN, 
        'heprealainen'    : Date.CAL_HEBREW, 
        'hepr.'           : Date.CAL_HEBREW, 
        'islamilainen'    : Date.CAL_ISLAMIC, 
        'isl.'            : Date.CAL_ISLAMIC, 
        'ranskan vallankumouksen aikainen': Date.CAL_FRENCH, 
        'ranskan v.'      : Date.CAL_FRENCH, 
        'persialainen'    : Date.CAL_PERSIAN, 
        'pers.'           : Date.CAL_PERSIAN, 
        'svensk'          : Date.CAL_SWEDISH, 
        's'               : Date.CAL_SWEDISH, 
        }

    quality_to_int = {
        'arviolta'   : Date.QUAL_ESTIMATED, 
        'arv.'       : Date.QUAL_ESTIMATED, 
        'laskettuna' : Date.QUAL_CALCULATED, 
        'lask.'      : Date.QUAL_CALCULATED, 
        }

    def init_strings(self):
        DateParser.init_strings(self)
    # date, whitespace
        self._span = re.compile("(?P<start>.+)\s+(-)\s+(?P<stop>.+)", 
                           re.IGNORECASE)
        self._range = re.compile(
            "(vuosien\s*)?(?P<start>.+)\s+ja\s+(?P<stop>.+)\s+välillä", 
            re.IGNORECASE)

#-------------------------------------------------------------------------
#
# Finnish display
#
#-------------------------------------------------------------------------
class DateDisplayFI(DateDisplay):
    """
    Finnish language date display class. 
    """
    long_months = ("", "Tammikuu", "Helmikuu", "Maaliskuu", "Huhtikuu",
                    "Toukokuu", "Kesäkuu", "Heinäkuu", "Elokuu",
                    "Syyskuu", "Lokakuu", "Marraskuu", "Joulukuu")
    
    short_months = ("", "Tammi", "Helmi", "Maali", "Huhti", "Touko",
                     "Kesäk", "Heinä", "Eloku", "Syysk", "Lokak", "Marra",
                     "Joulu")
    
    calendar = ("", 
        "juliaaninen", 
        "heprealainen", 
        "ranskan v.", 
        "persialainen", 
        "islamilainen", 
        "svensk" 
        )

    _qual_str = ("", "arviolta", "laskettuna")
    
    _bce_str = "%s ekr."

    formats = (
        "VVVV-KK-PP (ISO)", 
        "PP.KK.VVVV"
        )
        # this must agree with DateDisplayEn's "formats" definition
        # (since no locale-specific _display_gregorian exists, here)
    
    def display(self, date):
        """
        Return a text string representing the date.
        """
        mod = date.get_modifier()
        qual = date.get_quality()
        cal = date.get_calendar()
        start = date.get_start_date()
        newyear = date.get_new_year()
        
        if mod == Date.MOD_TEXTONLY:
            return date.get_text()
        if start == Date.EMPTY:
            return ""

        # select numerical date format
        self.format = 1

        if mod == Date.MOD_SPAN:
            d1 = self.display_cal[cal](start)
            d2 = self.display_cal[cal](date.get_stop_date())
            text = "%s - %s" % (d1, d2)
        elif mod == Date.MOD_RANGE:
            stop = date.get_stop_date()
            if start[0] == start[1] == 0 and stop[0] == 0 and stop[1] == 0:
                d1 = self.display_cal[cal](start)
                d2 = self.display_cal[cal](stop)
                text = "vuosien %s ja %s välillä" % (d1, d2)
            else:
                d1 = self.display_cal[cal](start)
                d2 = self.display_cal[cal](stop)
                text = "%s ja %s välillä" % (d1, d2)
        else:
            text = self.display_cal[date.get_calendar()](start)
            if mod == Date.MOD_AFTER:
                text = text + " jälkeen"
            elif mod == Date.MOD_ABOUT:
                text = "noin " + text
            elif mod == Date.MOD_BEFORE:
                text = "ennen " + text

        if qual:
            # prepend quality
            text = "%s %s" % (self._qual_str[qual], text)
            
        if cal or newyear:
            # append calendar type
            scal = self.format_extras(cal, newyear)
            text = "%s %s" % (text, scal)
    
        return text

#-------------------------------------------------------------------------
#
# Register classes
#
#-------------------------------------------------------------------------
register_datehandler(('fi_FI', 'fi', 'finnish', 'Finnish'), DateParserFI, DateDisplayFI)

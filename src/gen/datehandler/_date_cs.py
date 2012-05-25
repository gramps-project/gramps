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
#

"""
Czech-specific classes for parsing and displaying dates.
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
from _dateparser import DateParser
from _datedisplay import DateDisplay
from _datehandler import register_datehandler

#-------------------------------------------------------------------------
#
# Czech parser
#
#-------------------------------------------------------------------------
class DateParserCZ(DateParser):
    """
    Converts a text string into a Date object
    """ 
    month_to_int = DateParser.month_to_int
    
    month_to_int[u"leden"] = 1
    month_to_int[u"ledna"] = 1
    month_to_int[u"lednu"] = 1
    month_to_int[u"led"] = 1
    month_to_int[u"I"] = 1
    month_to_int[u"i"] = 1
    
    month_to_int[u"únor"] = 2
    month_to_int[u"února"] = 2
    month_to_int[u"únoru"] = 2
    month_to_int[u"ún"] = 2
    month_to_int[u"II"] = 2
    month_to_int[u"ii"]  = 2
    
    month_to_int[u"březen"] = 3
    month_to_int[u"března"] = 3
    month_to_int[u"březnu"] = 3
    month_to_int[u"bře"] = 3
    month_to_int[u"III"] = 3
    month_to_int[u"iii"]  = 3
    
    month_to_int[u"duben"] = 4
    month_to_int[u"dubna"] = 4
    month_to_int[u"dubnu"] = 4
    month_to_int[u"dub"] = 4
    month_to_int[u"IV"]  = 4
    month_to_int[u"iv"]  = 4

    month_to_int[u"květen"] = 5
    month_to_int[u"května"] = 5
    month_to_int[u"květnu"] = 5
    month_to_int[u"V"]  = 5
    month_to_int[u"v"]  = 5
    
    month_to_int[u"červen"] = 6
    month_to_int[u"června"] = 6
    month_to_int[u"červnu"] = 6
    month_to_int[u"čer"] = 6
    month_to_int[u"vi"]  = 6

    month_to_int[u"červenec"]  = 7
    month_to_int[u"července"]  = 7
    month_to_int[u"červenci"]  = 7
    month_to_int[u"čvc"]  = 7
    month_to_int[u"VII"]  = 7
    month_to_int[u"vii"]  = 7
    
    month_to_int[u"srpen"]  = 8
    month_to_int[u"srpna"]  = 8
    month_to_int[u"srpnu"]  = 8
    month_to_int[u"srp"]  = 8
    month_to_int[u"VIII"]  = 8
    month_to_int[u"viii"]  = 8
    
    month_to_int[u"září"]  = 9
    month_to_int[u"zář"]  = 9
    month_to_int[u"IX"]  = 9
    month_to_int[u"ix"]  = 9
    
    month_to_int[u"říjen"]  = 10
    month_to_int[u"října"]  = 10
    month_to_int[u"říjnu"]  = 10
    month_to_int[u"říj"]  = 10
    month_to_int[u"X"]  = 10
    month_to_int[u"x"]  = 10
    
    month_to_int[u"listopad"]  = 11
    month_to_int[u"listopadu"]  = 11
    month_to_int[u"lis"]  = 11
    month_to_int[u"XI"]  = 11
    month_to_int[u"xi"]  = 11
    
    month_to_int[u"prosinec"]  = 12
    month_to_int[u"prosince"]  = 12
    month_to_int[u"prosinci"]  = 12
    month_to_int[u"pro"]  = 12
    month_to_int[u"XII"]  = 12
    month_to_int[u"xii"]  = 12
    
    modifier_to_int = {
        u'před'   : Date.MOD_BEFORE, 
        u'do'     : Date.MOD_BEFORE, 
        u'po'     : Date.MOD_AFTER, 
        u'asi'    : Date.MOD_ABOUT, 
        u'kolem'  : Date.MOD_ABOUT, 
        u'přibl.' : Date.MOD_ABOUT, 
        }

    calendar_to_int = {
        u'gregoriánský'  : Date.CAL_GREGORIAN,
        u'greg.'         : Date.CAL_GREGORIAN,
        u'g'             : Date.CAL_GREGORIAN, 
        u'juliánský'     : Date.CAL_JULIAN, 
        u'jul.'          : Date.CAL_JULIAN, 
        u'j'             : Date.CAL_JULIAN, 
        u'hebrejský'     : Date.CAL_HEBREW, 
        u'hebr.'         : Date.CAL_HEBREW, 
        u'h'             : Date.CAL_HEBREW, 
        u'islámský'      : Date.CAL_ISLAMIC, 
        u'isl.'          : Date.CAL_ISLAMIC, 
        u'i'             : Date.CAL_ISLAMIC, 
        u'francouzský republikánský'    : Date.CAL_FRENCH, 
        u'fr.'           : Date.CAL_FRENCH, 
        u'perský'        : Date.CAL_PERSIAN, 
        u'per.'          : Date.CAL_PERSIAN, 
        u'p'             : Date.CAL_PERSIAN, 
        u'švédský'       : Date.CAL_SWEDISH, 
        u'sve.'          : Date.CAL_SWEDISH, 
        u's'             : Date.CAL_SWEDISH, 
        }

    quality_to_int = {
        u'odhadované' : Date.QUAL_ESTIMATED, 
        u'odh.'       : Date.QUAL_ESTIMATED, 
        u'vypočtené'  : Date.QUAL_CALCULATED, 
        u'vyp.'       : Date.QUAL_CALCULATED, 
        }
        
    def init_strings(self):
        DateParser.init_strings(self)
        self._span  = re.compile(
            u"(od)\s+(?P<start>.+)\s+(do)\s+(?P<stop>.+)",
            re.IGNORECASE)
        self._range = re.compile(
            u"(mezi)\s+(?P<start>.+)\s+(a)\s+(?P<stop>.+)", 
            re.IGNORECASE)


#-------------------------------------------------------------------------
#
# Czech display
#
#-------------------------------------------------------------------------
class DateDisplayCZ(DateDisplay):
    """
    Czech language date display class. 
    """
    long_months = ( u"", u"leden", u"únor", u"březen", u"duben", u"květen", 
                    u"červen", u"červenec", u"srpen", u"září", u"říjen", 
                    u"listopad", u"prosinec" )
    
    short_months = ( u"", u"led", u"úno", u"bře", u"dub", u"kvě", u"čer", 
                     u"čvc", u"srp", u"zář", u"říj", u"lis", u"pro" )

    calendar = (
        "", u"juliánský", u"hebrejský", 
        u"francouzský republikánský", u"perský", u"islámský", 
        u"švédský" 
        )

    _mod_str = ("", u"před ", u"po ", u"kolem ", "", "", "")
    
    _qual_str = ("", "přibližně ", "vypočteno ")

    bce = ["před naším letopočtem", "před Kristem",
           "př. n. l.", "př. Kr."] + DateParser.bce

    formats = (
        "ISO (rrrr-mm-dd)", 
        "numerický",
        "měsíc den, Rok",
        "měs den, Rok",
        "den. měsíc rok",
        "den. měs rok"
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
        elif mod == Date.MOD_NONE:
            date_decl_string = self.display_cal[cal](start)
            date_decl_string = date_decl_string.replace(u"den ", u"dna ")
            date_decl_string = date_decl_string.replace(u"or ", u"ora ")
            date_decl_string = date_decl_string.replace(u"en ", u"na ")
            date_decl_string = date_decl_string.replace(u"ad ", u"adu ")
            date_decl_string = date_decl_string.replace(u"ec ", u"ce ")
            return date_decl_string
        elif mod == Date.MOD_SPAN:
            dat1 = self.display_cal[cal](start)
            dat2 = self.display_cal[cal](date.get_stop_date())
            scal = self.format_extras(cal, newyear)
            return "%s%s %s %s %s%s" % (qual_str, u'od', dat1, 
                                        u'do', dat2, scal)
        elif mod == Date.MOD_RANGE:
            dat1 = self.display_cal[cal](start)
            dat2 = self.display_cal[cal](date.get_stop_date())
            scal = self.format_extras(cal, newyear)
            return "%s%s %s %s %s%s" % (qual_str, u'mezi', 
                                        dat1, u'a', dat2, scal)
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
register_datehandler(("cs", "CS", "cs_CZ", "Czech"), DateParserCZ, DateDisplayCZ)

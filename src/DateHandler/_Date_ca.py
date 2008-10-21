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

# Catalan Version, 2008 

"""
Catalan-specific classes for parsing and displaying dates.
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
# Catalan parser
#
#-------------------------------------------------------------------------
class DateParserCA(DateParser):

    modifier_to_int = {
        u'abans de'     : Date.MOD_BEFORE, 
        u'abans'        : Date.MOD_BEFORE, 
        u'ab.'          : Date.MOD_BEFORE, 
        u'després de'   : Date.MOD_AFTER, 
        u'després'      : Date.MOD_AFTER, 
        u'desp.'        : Date.MOD_AFTER, 
        u'desp'         : Date.MOD_AFTER, 
        u'aprox.'       : Date.MOD_ABOUT, 
        u'aprox'        : Date.MOD_ABOUT, 
        u'circa'        : Date.MOD_ABOUT, 
        u'ca.'          : Date.MOD_ABOUT, 
        u'ca'           : Date.MOD_ABOUT, 
        u'c.'           : Date.MOD_ABOUT, 
        u'cap a'        : Date.MOD_ABOUT, 
        u'al voltant'   : Date.MOD_ABOUT, 
        u'al voltant de': Date.MOD_ABOUT, 
        }

    calendar_to_int = {
        u'gregorià'     : Date.CAL_GREGORIAN, 
        u'g'            : Date.CAL_GREGORIAN, 
        u'julià'        : Date.CAL_JULIAN, 
        u'j'            : Date.CAL_JULIAN, 
        u'hebreu'       : Date.CAL_HEBREW, 
        u'h'            : Date.CAL_HEBREW, 
        u'islàmic'      : Date.CAL_ISLAMIC, 
        u'i'            : Date.CAL_ISLAMIC, 
        u'revolucionari': Date.CAL_FRENCH, 
        u'r'            : Date.CAL_FRENCH, 
        u'persa'        : Date.CAL_PERSIAN, 
        u'p'            : Date.CAL_PERSIAN, 
        }

    quality_to_int = {
        u'estimat'   : Date.QUAL_ESTIMATED, 
        u'est.'      : Date.QUAL_ESTIMATED, 
        u'est'       : Date.QUAL_ESTIMATED, 
        u'calc.'     : Date.QUAL_CALCULATED, 
        u'calc'      : Date.QUAL_CALCULATED, 
        u'calculat'  : Date.QUAL_CALCULATED, 
        }

    def init_strings(self):
        DateParser.init_strings(self)
        _span_1 = [u'des de']
        _span_2 = [u'fins a']
        _range_1 = [u'entre', u'ent\.', u'ent']
        _range_2 = [u'i']
        self._span  = re.compile("(%s)\s+(?P<start>.+)\s+(%s)\s+(?P<stop>.+)" % 
                                 ('|'.join(_span_1), '|'.join(_span_2)), 
                                 re.IGNORECASE)
        self._range = re.compile("(%s)\s+(?P<start>.+)\s+(%s)\s+(?P<stop>.+)" %
                                 ('|'.join(_range_1), '|'.join(_range_2)), 
                                 re.IGNORECASE)

#-------------------------------------------------------------------------
#
# Catalan display
#
#-------------------------------------------------------------------------
class DateDisplayCA(DateDisplay):

    calendar = (
        "", u" (Julià)", u" (Hebreu)", 
        u" (Revolucionari)", u" (Persa)", u" (Islàmic)"
        )

    _mod_str = ("", u"abans de ", u"després de ", u"cap a ", "", "", "")

    _qual_str = ("", "estimat ", "calculat ")

    french = (
        u'', 
        u"Vendemiari", 
        u'Brumari', 
        u'Frimari', 
        u"Nivós", 
        u"Pluviós", 
        u"Ventós", 
        u'Germinal', 
        u"Floreal", 
        u'Pradial', 
        u'Messidor', 
        u'Termidor', 
        u'Fructidor', 
        u'Extra', 
        )
    
    formats = (
        "AAAA-MM-DD (ISO)", "Numèrica", "Mes Dia, Any", 
        "MES Dia, Any", "Dia Mes, Any", "Dia MES, Any"
        )
    
    def display(self, date):
        """
        Return a text string representing the date.
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
            return "%s%s %s %s %s%s" % (qual_str, u'des de', d1, u'fins a', d2, self.calendar[cal])
        elif mod == Date.MOD_RANGE:
            d1 = self.display_cal[cal](start)
            d2 = self.display_cal[cal](date.get_stop_date())
            return "%s%s %s %s %s%s" % (qual_str, u'entre', d1, u'i', d2, self.calendar[cal])
        else:
            text = self.display_cal[date.get_calendar()](start)
            return "%s%s%s%s" % (qual_str, self._mod_str[mod], text, self.calendar[cal])

#-------------------------------------------------------------------------
#
# Register classes
#
#-------------------------------------------------------------------------
register_datehandler(('ca_ES', 'ca', 'català','ca_FR','ca_AD','ca_IT',), DateParserCA, DateDisplayCA)

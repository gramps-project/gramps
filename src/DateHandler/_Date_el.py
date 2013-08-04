# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2006  Donald N. Allingham
# Copyright (C) 2013       Zissis Papadopoulos <zissis@mail.com>
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
Greek-specific classes for parsing and displaying dates.
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
# Greek parser class
#
#-------------------------------------------------------------------------
class DateParserEL(DateParser):
    """
    Convert a text string into a Date object. If the date cannot be
    converted, the text string is assigned.
    """

    # modifiers before the date
    modifier_to_int = {
        'προ του' : Date.MOD_BEFORE,
        'προ'       : Date.MOD_BEFORE,
        'πρ.'       : Date.MOD_BEFORE,
        'μετά το'   : Date.MOD_AFTER,
        'μετά'      : Date.MOD_AFTER, 
        'μετ.'      : Date.MOD_AFTER,
        'γύρω στο'  : Date.MOD_ABOUT, 
        'περίπου το': Date.MOD_ABOUT,
        'περ.'      : Date.MOD_ABOUT, 
        '~'         : Date.MOD_ABOUT,
        }
    # in some languages some of above listed modifiers are after the date,
    # in that case the subclass should put them into this dictionary instead
    modifier_after_to_int = {}

    bce = ["π.Χ.", "π.Κ.Χ.", "π.Κ.Ε.", "π.Χ" ]

    calendar_to_int = {
        'γρηγοριανό'          : Date.CAL_GREGORIAN,
        'γ'                   : Date.CAL_GREGORIAN,
        'ιουλιανό'            : Date.CAL_JULIAN,
        'ι'                   : Date.CAL_JULIAN,
        'εβραϊκό'             : Date.CAL_HEBREW,
        'ε'                   : Date.CAL_HEBREW,
        'ισλαμικό'            : Date.CAL_ISLAMIC,
        'ισλ'                  : Date.CAL_ISLAMIC,
        'γαλλικό'             : Date.CAL_FRENCH,
        'γαλλικής δημοκρατίας': Date.CAL_FRENCH,
        'γ'                   : Date.CAL_FRENCH,
        'περσικό'             : Date.CAL_PERSIAN,
        'π'                   : Date.CAL_PERSIAN, 
        'σουηδικό'            : Date.CAL_SWEDISH,
        'σ'                   : Date.CAL_SWEDISH,
        }
    
    quality_to_int = {
        'κατʼ εκτίμηση' : Date.QUAL_ESTIMATED,
        'εκτ.'          : Date.QUAL_ESTIMATED,
        'εκτ'           : Date.QUAL_ESTIMATED,
        'υπολογ'        : Date.QUAL_CALCULATED,
        'υπολογ.'       : Date.QUAL_CALCULATED,
        'με υπολογισμό' : Date.QUAL_CALCULATED,
        }
    
    def init_strings(self):
        """
        This method compiles regular expression strings for matching dates.
        """
        DateParser.init_strings(self)
        _span_1 = [u'από']
        _span_2 = [u'έως']
        _range_1 = [u'μετ', u'μετ\.', u'μεταξύ']
        _range_2 = [u'και']
        self._span =  re.compile("(%s)\s+(?P<start>.+)\s+(%s)\s+(?P<stop>.+)" %
                                 ('|'.join(_span_1), '|'.join(_span_2)),
                                 re.IGNORECASE)
        self._range = re.compile("(%s)\s+(?P<start>.+)\s+(%s)\s+(?P<stop>.+)" %
                                 ('|'.join(_range_1), '|'.join(_range_2)), 
                                 re.IGNORECASE)

#-------------------------------------------------------------------------
#
# Greek display
#
#-------------------------------------------------------------------------
class DateDisplayEL(DateDisplay):
    """
    Greek language date display class. 
    """
    # this is used to display the 12 gregorian months
    long_months = ( u"", u"Ιανουάριος", u"Φεβρουάριος", u"Μάρτιος",
                    u"Απρίλιος", u"Μάιος", u"Ιούνιος",
                    u"Ιούλιος", u"Αύγουστος", u"Σεπτέμβριος",
                    u"Οκτώβριος", u"Νοέμβριος", u"Δεκέμβριος" )
    
    short_months = ( u"", u"Ιαν", u"Φεβ", u"Μαρ", u"Απρ", u"Μάι", u"Ιουν",
                     u"Ιουλ", u"Αύγ", u"Σεπ", u"Οκτ", u"Νοε", u"Δεκ" )

    _mod_str = ("", "ðñï ôïõ ", "ìåôÜ ôï ", "ãýñù óôï ", "", "", "")

    _qual_str = ("", "åêôéìþìåíç ", "õðïëïãéóìÝíç ")

    _bce_str = "%s ð.×."

    #Following are the formats for date display you can set in the preferences
    formats = (
        "ΕΕΕΕ-ΜΜ-ΗΗ (ISO)", "Αριθμητικά", "Ημερομηνία, Έτος", 
        "ΗΜ/ΝΙΑ, ΕΤΟΣ", "Ημέρα Μήνας Έτος", "ΗΜ ΜΗΝ ΕΤΟΣ"
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
            return "%s%s %s %s %s%s" % (qual_str, u'από', d1, u'έως', d2, scal)
        elif mod == Date.MOD_RANGE:
            d1 = self.display_cal[cal](start)
            d2 = self.display_cal[cal](date.get_stop_date())
            scal = self.format_extras(cal, newyear)
            return "%s%s %s %s %s%s" % (qual_str, u'μεταξύ', d1, u'και', d2, scal)
        else:
            text = self.display_cal[date.get_calendar()](start)
            scal = self.format_extras(cal, newyear)
            return "%s%s%s%s" % (qual_str, self._mod_str[mod], text, scal)

#-------------------------------------------------------------------------
#
# Register classes
#
#-------------------------------------------------------------------------
register_datehandler(('el_GR', 'el_CY', 'el', 'Greek', 'greek'), 
    DateParserEL, DateDisplayEL)

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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Attempt to parse dates for Icelandic, Sveinn í Felli 2016

"""
Icelandic-specific classes for parsing and displaying dates.
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
from ..lib.date import Date
from ._dateparser import DateParser
from ._datedisplay import DateDisplay
from ._datehandler import register_datehandler

#-------------------------------------------------------------------------
#
# Icelandic parser class
#
#-------------------------------------------------------------------------
class DateParserIs(DateParser):
    """
    Convert a text string into a Date object, expecting a date
    notation in the Icelandic language. If the date cannot be converted, 
    the text string is assigned.
    """

    # modifiers before the date
    modifier_to_int = {
        'fyrir'    : Date.MOD_BEFORE, 
        'á undan'  : Date.MOD_BEFORE, 
        'eftir'   : Date.MOD_AFTER, 
        'í kringum' : Date.MOD_ABOUT, 
        'uþb'      : Date.MOD_ABOUT
        }

    bce = ["f Kr"]

    calendar_to_int = {
        'gregoríanskt   '      : Date.CAL_GREGORIAN, 
        'g'                   : Date.CAL_GREGORIAN, 
        'júlíanskt'            : Date.CAL_JULIAN, 
        'j'                   : Date.CAL_JULIAN, 
        'hebreskt'            : Date.CAL_HEBREW, 
        'h'                   : Date.CAL_HEBREW, 
        'íslamskt'            : Date.CAL_ISLAMIC, 
        'múslimskt'            : Date.CAL_ISLAMIC, 
        'i'                   : Date.CAL_ISLAMIC, 
        'franskt'              : Date.CAL_FRENCH, 
        'franska lýðveldisins' : Date.CAL_FRENCH, 
        'f'                   : Date.CAL_FRENCH, 
        'persneskt'             : Date.CAL_PERSIAN, 
        'p'                   : Date.CAL_PERSIAN, 
        'sænskt'              : Date.CAL_SWEDISH, 
        's'                   : Date.CAL_SWEDISH, 
        }
    
    quality_to_int = {
        'áætlað' : Date.QUAL_ESTIMATED, 
        'reiknað'   : Date.QUAL_CALCULATED, 
        }
    
    def init_strings(self):
        DateParser.init_strings(self)
        self._span     = re.compile("(frá)?\s*(?P<start>.+)\s*(til|--|–)\s*(?P<stop>.+)", 
                                    re.IGNORECASE)
        self._range    = re.compile("(milli)\s+(?P<start>.+)\s+og\s+(?P<stop>.+)", 
                                    re.IGNORECASE)

#-------------------------------------------------------------------------
#
# Icelandic display class
#
#-------------------------------------------------------------------------
class DateDisplayIs(DateDisplay):
    """
    Icelandic language date display class. 
    """

    long_months = ( "", "janúar", "febrúar", "mars", "apríl", "maí", 
                    "júní", "júlí", "ágúst", "september", "október", 
                    "nóvember", "desember" )
    
    short_months = ( "", "jan", "feb", "mar", "apr", "maí", "jún", 
                     "júl", "ágú", "sep", "okt", "nóv", "des" )

    formats = (
        "ÁÁÁÁ-MM-DD (ISO)", 
        "Tölulegt", 
        "Mánuður dagur, ár", 
        "Mán Dag Ár", 
        "Dagur mánuður ár", 
        "Dag Mán Ár", 
        )
        # this must agree with DateDisplayEn's "formats" definition
        # (since no locale-specific _display_gregorian exists, here)

    calendar = (
        "", 
        "júlíanskt", 
        "hebreskt", 
        "franska lýðveldisins", 
        "persneskt", 
        "íslamskt", 
        "sænskt" 
        )
    
    _mod_str = ("", "fyrir ", "eftir ", "uþb ", "", "", "")

    _qual_str = ("", "reiknað ", "reiknað ")
    
    _bce_str = "%s f. Kr"

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
            return "%sfrá %s til %s%s" % (qual_str, d1, d2, scal)
        elif mod == Date.MOD_RANGE:
            d1 = self.display_cal[cal](start)
            d2 = self.display_cal[cal](date.get_stop_date())
            scal = self.format_extras(cal, newyear)
            return "%smilli %s og %s%s" % (qual_str, d1, d2, 
                                              scal)
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
register_datehandler(('is_IS', 'is', 'íslenskt', 'Icelandic'), DateParserIs, DateDisplayIs)

# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2007  Donald N. Allingham
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
# $Id: _date_hr.py 22672 2013-07-13 18:01:08Z paul-franklin $
#

# Croatian version 2008 by Josip

"""
Croatian-specific classes for parsing and displaying dates.
"""

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import re

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from ..lib.date import Date
from ._dateparser import DateParser
from ._datedisplay import DateDisplay
from ._datehandler import register_datehandler

#-------------------------------------------------------------------------
#
# Croatian parser
#
#-------------------------------------------------------------------------
class DateParserHR(DateParser):
    modifier_to_int = {
        'prije'    : Date.MOD_BEFORE,
        'pr. '    : Date.MOD_BEFORE,
        'poslije'   : Date.MOD_AFTER,
        'po. '   : Date.MOD_AFTER,
        'okolo'  : Date.MOD_ABOUT,
        'ok. '     : Date.MOD_ABOUT,

        }

    quality_to_int = {
        'približno' : Date.QUAL_ESTIMATED,
        'prb.'      : Date.QUAL_ESTIMATED,
        'izračunato'  : Date.QUAL_CALCULATED,
        'izr.'       : Date.QUAL_CALCULATED,
        }

    bce = ["prije nove ere", "prije Krista",
           "p.n.e."] + DateParser.bce

    def init_strings(self):
        """
        compiles regular expression strings for matching dates
        """
        DateParser.init_strings(self)
        #~ DateParser.calendar_to_int.update({
            #~ 'персидский'    : Date.CAL_PERSIAN,
            #~ 'п'             : Date.CAL_PERSIAN,
        #~ })
        _span_1 = ['od']
        _span_2 = ['do']
        _range_1 = ['između']
        _range_2 = ['i']
        self._span =  re.compile("(%s)\s+(?P<start>.+)\s+(%s)\s+(?P<stop>.+)" %
                                 ('|'.join(_span_1), '|'.join(_span_2)),
                                 re.IGNORECASE)
        self._range = re.compile("(%s)\s+(?P<start>.+)\s+(%s)\s+(?P<stop>.+)" %
                                 ('|'.join(_range_1), '|'.join(_range_2)),
                                 re.IGNORECASE)

#-------------------------------------------------------------------------
#
# Croatian display
#
#-------------------------------------------------------------------------
class DateDisplayHR(DateDisplay):
    """
    Croatian language date display class.
    """
     # TODO fix BUG 7064: non-Gregorian calendars wrongly use BCE notation for negative dates
    # not refactoring _bce_str into base class because it'll be gone under #7064
    _bce_str = "%s p.n.e."

    display = DateDisplay.display_formatted

#-------------------------------------------------------------------------
#
# Register classes
#
#-------------------------------------------------------------------------
register_datehandler(('hr', 'HR', 'croatian', 'Croatian', 'hrvatski', 'hr_HR'),
                                    DateParserHR, DateDisplayHR)

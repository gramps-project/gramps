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
# Gramps modules
#
#-------------------------------------------------------------------------
from ..lib.date import Date
from ._dateparser import DateParser
from ._datedisplay import DateDisplay
from ._datehandler import register_datehandler

#-------------------------------------------------------------------------
#
# Czech parser
#
#-------------------------------------------------------------------------
class DateParserCZ(DateParser):
    """
    Converts a text string into a Date object
    """

    bce = ["před naším letopočtem", "před Kristem",
           "př. n. l.", "př. Kr."] + DateParser.bce

    def dhformat_changed(self):
        """ Allow overriding so a subclass can modify it """
        # bug 9739 grampslocale.py gets '%-d.%-m.%Y' -- makes it be '%/d.%/m.%Y'
        self.dhformat = self.dhformat.replace('/', '') # so counteract that

#-------------------------------------------------------------------------
#
# Czech display
#
#-------------------------------------------------------------------------
class DateDisplayCZ(DateDisplay):
    """
    Czech language date display class.
    """

    display = DateDisplay.display_formatted

    def formats_changed(self):
        """ Allow overriding so a subclass can modify """

        # bug 9537 grampslocale.py gets '%-d.%-m.%Y' -- makes it be '%/d.%/m.%Y'
        self.dhformat = self.dhformat.replace('/', '') # so counteract that


#-------------------------------------------------------------------------
#
# Register classes
#
#-------------------------------------------------------------------------
register_datehandler(
    ("cs_CZ", "cs", "CS", "Czech", ('%-d.%-m.%Y',)),
    DateParserCZ, DateDisplayCZ)

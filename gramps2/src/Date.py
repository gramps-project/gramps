#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2004  Donald N. Allingham
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

"Support for dates"

__author__ = "Donald N. Allingham"
__version__ = "$Revision$"

from CalSdn import *

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------

MOD_NONE       = 0
MOD_BEFORE     = 1
MOD_AFTER      = 2
MOD_ABOUT      = 3
MOD_RANGE      = 4
MOD_SPAN       = 5
MOD_TEXTONLY   = 6

QUAL_NONE      = 0
QUAL_ESTIMATED = 1
QUAL_CALCULATED= 2

CAL_GREGORIAN  = 0
CAL_JULIAN     = 1
CAL_HEBREW     = 2
CAL_FRENCH     = 3
CAL_PERSIAN    = 4
CAL_ISLAMIC    = 5

EMPTY = (0,0,0,False)

_POS_DAY  = 0
_POS_MON  = 1
_POS_YR   = 2
_POS_SL   = 3
_POS_RDAY = 4
_POS_RMON = 5
_POS_RYR  = 6
_POS_RSL  = 7

_calendar_convert = [
    gregorian_sdn,
    julian_sdn,
    hebrew_sdn,
    french_sdn,
    persian_sdn,
    islamic_sdn,
    ]

_calendar_change = [
    gregorian_ymd,
    julian_ymd,
    hebrew_ymd,
    french_ymd,
    persian_ymd,
    islamic_ymd,
    ]

#-------------------------------------------------------------------------
#
# Date class
#
#-------------------------------------------------------------------------
class Date:
    """
    The core date handling class for GRAMPs. Supports partial dates,
    compound dates and alternate calendars.
    """

    calendar_names = ["Gregorian",
                      "Julian",
                      "Hebrew",
                      "French Republican",
                      "Persian",
                      "Islamic"]

    def __init__(self,source=None):
        """
        Creates a new Date instance.
        """
        if source:
            self.calendar = source.calendar
            self.modifier = source.modifier
            self.quality  = source.quality
            self.dateval  = source.dateval
            self.text     = source.text
            self.sortval  = source.sortval
        else:
            self.calendar = CAL_GREGORIAN
            self.modifier = MOD_TEXTONLY
            self.quality  = QUAL_NONE
            self.dateval  = EMPTY
            self.text     = u""
            self.sortval  = 0

    def copy(self,source):
        """
        Copy all the attributes of the given Date instance
        to the present instance, without creating a new object.
        """
        self.calendar = source.calendar
        self.modifier = source.modifier
        self.quality  = source.quality
        self.dateval  = source.dateval
        self.text     = source.text
        self.sortval  = source.sortval

    def __cmp__(self,other):
        """
        Comparison function. Allows the usage of equality tests.
        This allows you do run statements like 'date1 <= date2'
        """
        return cmp(self.sortval,other.sortval)

    def is_equal(self,other):
        """
        Return 1 if the given Date instance is the same as the present
        instance IN ALL REGARDS. Needed, because the __cmp__ only looks
        at the sorting value, and ignores the modifiers/comments.
        """
        
        return (self.calendar == other.calendar and 
                self.modifier == other.modifier and 
                self.quality == other.quality and 
                self.dateval == other.dateval and 
                self.text == other.text and 
                self.sortval == other.sortval)
            
    def __str__(self):
        """
        Produces a string representation of the Date object. If the
        date is not valid, the text representation is displayed. If
        the date is a range or a span, a string in the form of
        'YYYY-MM-DD - YYYY-MM-DD' is returned. Otherwise, a string in
        the form of 'YYYY-MM-DD' is returned.
        """
        if self.quality == QUAL_ESTIMATED:
            qual = "est "
        elif self.quality == QUAL_CALCULATED:
            qual = "calc "
        else:
            qual = ""

        if self.modifier == MOD_BEFORE:
            pref = "bef "
        elif self.modifier == MOD_AFTER:
            pref = "aft "
        elif self.modifier == MOD_ABOUT:
            pref = "abt "
        else:
            pref = ""

        if self.calendar != CAL_GREGORIAN:
            cal = " (%s)" % self.calendar_names[self.calendar]
        else:
            cal = ""
        
            
        if self.modifier == MOD_TEXTONLY:
            val = self.text
        elif self.modifier == MOD_RANGE or self.modifier == MOD_SPAN:
            val = "%04d-%02d-%02d - %04d-%02d-%02d" % (
                self.dateval[_POS_YR],self.dateval[_POS_MON],self.dateval[_POS_DAY],
                self.dateval[_POS_RYR],self.dateval[_POS_RMON],self.dateval[_POS_RDAY])
        else:
            val = "%04d-%02d-%02d" % (
                self.dateval[_POS_YR],self.dateval[_POS_MON],self.dateval[_POS_DAY])
        return "%s%s%s%s" % (qual,pref,val,cal)

    def get_sort_value(self):
        """
        Returns the sort value of Date object. If the value is a
        text string, 0 is returned. Otherwise, the calculated sort
        date is returned. The sort date is rebuilt on every assignment.

        The sort value is an integer representing the value. A date of
        March 5, 1990 would have the value of 19900305.
        """
        return self.sortval

    def get_modifier(self):
        """
        Returns an integer indicating the calendar selected. The valid
        values are:
        
           MOD_NONE       = no modifier (default)
           MOD_BEFORE     = before
           MOD_AFTER      = after
           MOD_ABOUT      = about
           MOD_RANGE      = date range
           MOD_SPAN       = date span
           MOD_TEXTONLY   = text only
        """
        return self.modifier

    def set_modifier(self,val):
        """
        Sets the modifier for the date.
        """
        self.modifier = val

    def get_quality(self):
        """
        Returns an integer indicating the calendar selected. The valid
        values are:
        
           QUAL_NONE       = normal (default)
           QUAL_ESTIMATED  = estimated
           QUAL_CALCULATED = calculated
        """
        return self.quality

    def set_quality(self,val):
        """
        Sets the quality selected for the date.
        """
        self.quality = val
    
    def get_calendar(self):
        """
        Returns an integer indicating the calendar selected. The valid
        values are:

           CAL_GREGORIAN  - Gregorian calendar
           CAL_JULIAN     - Julian calendar
           CAL_HEBREW     - Hebrew (Jewish) calendar
           CAL_FRENCH     - French Republican calendar
           CAL_PERSIAN    - Persian calendar
           CAL_ISLAMIC    - Islamic calendar
        """
        return self.calendar

    def set_calendar(self,val):
        """
        Sets the calendar selected for the date.
        """
        self.calendar = val

    def get_start_date(self):
        """
        Returns a tuple representing the start date. If the date is a
        compound date (range or a span), it is the first part of the
        compound date. If the date is a text string, a tuple of
        (0,0,0,False) is returned. Otherwise, a date of (DD,MM,YY,slash)
        is returned. If slash is True, then the date is in the form of 1530/1.
        """
        if self.modifier == MOD_TEXTONLY:
            val = EMPTY
        else:
            val = self.dateval[0:4]
        return val

    def get_stop_date(self):
        """
        Returns a tuple representing the second half of a compound date. 
        If the date is not a compound date, (including text strings) a tuple
        of (0,0,0,False) is returned. Otherwise, a date of (DD,MM,YY,slash)
        is returned. If slash is True, then the date is in the form of 1530/1.
        """
        if self.modifier == MOD_RANGE or self.modifier == MOD_SPAN:
            val = self.dateval[4:8]
        else:
            val = EMPTY
        return val

    def _get_low_item(self,index):
        if self.modifier == MOD_TEXTONLY:
            val = 0
        else:
            val = self.dateval[index]
        return val

    def _get_low_item_valid(self,index):
        if self.modifier == MOD_TEXTONLY:
            val = False
        else:
            val = self.dateval[index] != 0
        return val
        
    def _get_high_item(self,index):
        if self.modifier == MOD_SPAN or self.modifier == MOD_RANGE:
            val = self.dateval[index]
        else:
            val = 0
        return val

    def get_year(self):
        """
        Returns the year associated with the date. If the year is
        not defined, a zero is returned. If the date is a compound
        date, the lower date year is returned.
        """
        return self._get_low_item(_POS_YR)

    def get_year_valid(self):
        return self._get_low_item_valid(_POS_YR)

    def get_month(self):
        """
        Returns the month associated with the date. If the month is
        not defined, a zero is returned. If the date is a compound
        date, the lower date month is returned.
        """
        return self._get_low_item(_POS_MON)

    def get_month_valid(self):
        return self._get_low_item_valid(_POS_MON)

    def get_day(self):
        """
        Returns the day of the month associated with the date. If
        the day is not defined, a zero is returned. If the date is
        a compound date, the lower date day is returned.
        """
        return self._get_low_item(_POS_DAY)

    def get_day_valid(self):
        return self._get_low_item_valid(_POS_DAY)

    def get_valid(self):
        """ Returns true if any part of the date is valid"""
        return self.modifier != MOD_TEXTONLY

    def get_incomplete(self):
        pass

    def get_stop_year(self):
        """
        Returns the day of the year associated with the second
        part of a compound date. If the year is not defined, a zero
        is returned. 
        """
        return self._get_high_item(_POS_RYR)

    def get_stop_month(self):
        """
        Returns the month of the month associated with the second
        part of a compound date. If the month is not defined, a zero
        is returned. 
        """
        return self._get_high_item(_POS_RMON)

    def get_stop_day(self):
        """
        Returns the day of the month associated with the second
        part of a compound date. If the day is not defined, a zero
        is returned. 
        """
        return self._get_high_item(_POS_RDAY)

    def get_high_year(self):
        """
        Returns the high year estimate. For compound dates with non-zero 
        stop year, the stop year is returned. Otherwise, the start year 
        is returned.
        """
        if self.is_compound():
            ret = self.get_stop_year()
            if ret:
                return ret
        else:
            return self.get_year()

    def get_text(self):
        """
        Returns the text value associated with an invalid date.
        """
        return self.text

    def set(self,quality,modifier,calendar,value,text=None):
        """
        Sets the date to the specified value. Parameters are:

        quality  - The date quality for the date (see get_quality
                   for more information)
        modified - The date modifier for the date (see get_modifier
                   for more information)
        calendar - The calendar associated with the date (see
                   get_calendar for more information).
        value    - A tuple representing the date information. For a
                   non-compound date, the format is (DD,MM,YY,slash)
                   and for a compound date the tuple stores data as
                   (DD,MM,YY,slash1,DD,MM,YY,slash2)
        text     - A text string holding either the verbatim user input
                   or a comment relating to the date.

        The sort value is recalculated.
        """
        self.quality = quality
        self.modifier = modifier
        self.calendar = calendar
        self.dateval = value
        year = max(value[_POS_YR],1)
        month = max(value[_POS_MON],1)
        day = max(value[_POS_DAY],1)
        self.sortval = _calendar_convert[calendar](year,month,day)
        if text:
            self.text = text

    def convert_calendar(self,calendar):
        """
        Converts the date from the current calendar to the specified
        calendar.
        """
        if calendar == self.calendar:
            return
        (y,m,d) = _calendar_change[calendar](self.sortval)
        if self.is_compound():
            ry = max(self.dateval[_POS_RYR],1)
            rm = max(self.dateval[_POS_RMON],1)
            rd = max(self.dateval[_POS_RDAY],1)
            sdn = _calendar_convert[self.calendar](ry,rm,rd)
            (ny,nm,nd) = _calendar_change[calendar](sdn)
            self.dateval = (d,m,y,self.dateval[_POS_SL],
                            nd,nm,ny,self.dateval[_POS_RSL])
        else:
            self.dateval = (d,m,y,self.dateval[_POS_SL])
        self.calendar = calendar

    def set_as_text(self,text):
        """
        Sets the day to a text string, and assigns the sort value
        to zero.
        """
        self.modifier = MOD_TEXTONLY
        self.text = text
        self.sortval = 0

    def set_text_value(self,text):
        """
        Sets the text string to a given text.
        """
        self.text = text

    def is_empty(self):
        """
        Returns True if the date is a date range or a date span.
        """
        return self.modifier == MOD_TEXTONLY
        
    def is_compound(self):
        """
        Returns True if the date is a date range or a date span.
        """
        return self.modifier == MOD_RANGE or self.modifier == MOD_SPAN

    def is_regular(self):
        """
        Returns True if the date is a regular date.
        
        The regular date is a single exact date, i.e. not text-only, not 
        a range or a span, not estimated/calculated, not about/before/after 
        date, and having year, month, and day all non-zero.
        """
        return self.modifier == MOD_NONE and self.quality == QUAL_NONE\
                    and self.get_year_valid() and self.get_month_valid()\
                    and self.get_day_valid()

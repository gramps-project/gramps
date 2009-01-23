#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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

"""Support for dates."""

#------------------------------------------------------------------------
#
# Python modules
#
#------------------------------------------------------------------------
from gettext import gettext as _

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
log = logging.getLogger(".Date")

#-------------------------------------------------------------------------
#
# Gnome/GTK modules
#
#-------------------------------------------------------------------------


#------------------------------------------------------------------------
#
# Gramps modules
#
#------------------------------------------------------------------------
from gen.lib.calendar import (gregorian_sdn, julian_sdn, hebrew_sdn, 
                              french_sdn, persian_sdn, islamic_sdn, 
                              gregorian_ymd, julian_ymd, hebrew_ymd, 
                              french_ymd, persian_ymd, islamic_ymd)
import Config

#-------------------------------------------------------------------------
#
# DateError exception
#
#-------------------------------------------------------------------------
class DateError(Exception):
    """Error used to report Date errors."""
    def __init__(self, value=""):
        Exception.__init__(self)
        self.value = value

    def __str__(self):
        return self.value

#-------------------------------------------------------------------------
#
# Date class
#
#-------------------------------------------------------------------------
class Date:
    """
    The core date handling class for GRAMPs. 
    
    Supports partial dates, compound dates and alternate calendars.
    """
    MOD_NONE       = 0
    MOD_BEFORE     = 1
    MOD_AFTER      = 2
    MOD_ABOUT      = 3
    MOD_RANGE      = 4
    MOD_SPAN       = 5
    MOD_TEXTONLY   = 6

    QUAL_NONE       = 0
    QUAL_ESTIMATED  = 1
    QUAL_CALCULATED = 2

    CAL_GREGORIAN  = 0
    CAL_JULIAN     = 1
    CAL_HEBREW     = 2
    CAL_FRENCH     = 3
    CAL_PERSIAN    = 4
    CAL_ISLAMIC    = 5

    EMPTY = (0, 0, 0, False)

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

    calendar_names = ["Gregorian", 
                      "Julian", 
                      "Hebrew", 
                      "French Republican", 
                      "Persian", 
                      "Islamic"]


    ui_calendar_names = [_("Gregorian"), 
                         _("Julian"), 
                         _("Hebrew"), 
                         _("French Republican"), 
                         _("Persian"), 
                         _("Islamic")]

    def __init__(self, *source, **kwargs):
        """
        Create a new Date instance.
        """
        calendar = kwargs.get("calendar", None)
        modifier = kwargs.get("modifier", None)
        quality = kwargs.get("quality", None)
        #### setup None, Date, or numbers
        if len(source) == 0:
            source = None
        elif len(source) == 1:
            if type(source[0]) == int:
                source = (source[0], 0, 0)
            else:
                source = source[0]
        elif len(source) == 2:
            source = (source[0], source[1], 0)
        elif len(source) == 3:
            pass # source is ok
        else:
            raise AttributeError, "invalid args to Date: %s" % source
        #### ok, process either date or tuple
        if type(source) == tuple:
            if calendar == None:
                self.calendar = Date.CAL_GREGORIAN
            else:
                self.calendar = self.lookup_calendar(calendar)
            if modifier == None:
                self.modifier = Date.MOD_NONE
            else:
                self.modifier = self.lookup_modifier(modifier)
            if quality == None:
                self.quality  = Date.QUAL_NONE
            else:
                self.quality = self.lookup_quality(quality)
            self.dateval  = Date.EMPTY
            self.text     = u""
            self.sortval  = 0
            self.set_yr_mon_day(*source)
        elif type(source) == str:
            if (calendar != None or 
                modifier != None or 
                quality != None):
                raise AttributeError("can't set calendar, modifier, or "
                                     "quality with string date")
            import DateHandler
            source = DateHandler.parser.parse(source)
            self.calendar = source.calendar
            self.modifier = source.modifier
            self.quality  = source.quality
            self.dateval  = source.dateval
            self.text     = source.text
            self.sortval  = source.sortval
        elif source:
            self.calendar = source.calendar
            self.modifier = source.modifier
            self.quality  = source.quality
            self.dateval  = source.dateval
            self.text     = source.text
            self.sortval  = source.sortval
        else:
            self.calendar = Date.CAL_GREGORIAN
            self.modifier = Date.MOD_NONE
            self.quality  = Date.QUAL_NONE
            self.dateval  = Date.EMPTY
            self.text     = u""
            self.sortval  = 0

    def serialize(self, no_text_date=False):
        """
        Convert to a series of tuples for data storage.
        """
        if no_text_date:
            text = u''
        else:
            text = self.text
        
        return (self.calendar, self.modifier, self.quality, 
                self.dateval, text, self.sortval)

    def unserialize(self, data):
        """
        Load from the format created by serialize.
        """
        (self.calendar, self.modifier, self.quality, 
         self.dateval, self.text, self.sortval) = data
        return self

    def copy(self, source):
        """
        Copy all the attributes of the given Date instance to the present 
        instance, without creating a new object.
        """
        self.calendar = source.calendar
        self.modifier = source.modifier
        self.quality  = source.quality
        self.dateval  = source.dateval
        self.text     = source.text
        self.sortval  = source.sortval

    def __cmp__(self, other):
        """
        Compare two dates.
        
        Comparison function. Allows the usage of equality tests.
        This allows you do run statements like 'date1 <= date2'
        """
        if isinstance(other, Date):
            return cmp(self.sortval, other.sortval)
        else:
            return -1

    def __add__(self, other):
        """
        Date arithmetic: Date() + years, or Date() + (years, [months, [days]]).
        """
        if type(other) == int:
            return self.copy_offset_ymd(other)
        elif type(other) in [tuple, list]:
            return self.copy_offset_ymd(*other)
        else:
            raise AttributeError, "unknown date add type: %s " % type(other)

    def __radd__(self, other):
        """
        Add a number + Date() or (years, months, days) + Date().
        """
        return self + other

    def __sub__(self, other):
        """
        Date arithmetic: Date() - years, Date - (y,m,d), or Date() - Date().
        """
        if type(other) == int:                # Date - value -> Date
            return self.copy_offset_ymd(-other)
        elif type(other) in [tuple, list]:    # Date - (y, m, d) -> Date
            return self.copy_offset_ymd(*map(lambda x: -x, other))
        elif type(other) == type(self):       # Date1 - Date2 -> tuple
            # We should make sure that Date2 + tuple -> Date1 and
            #                          Date1 - tuple -> Date2
            d1 = map(lambda i: i or 1, self.get_ymd())
            d2 = map(lambda i: i or 1, other.get_ymd())
            date1 = self
            date2 = other
            if d1 < d2:
                d1, d2 = d2, d1
                date1, date2 = date2, date1
            # d1 - d2 (1998, 12, 32) - (1982, 12, 15)
            if self.calendar != other.calendar:
                diff = date1.sortval - date2.sortval
                return (diff/365, (diff % 365)/30, (diff % 365) % 30)
            # days:
            if d2[2] > d1[2]:
                # months:
                if d2[1] > d1[1]:
                    d1[0] -= 1
                    d1[1] += 12
                d1[1] -= 1
                d1[2] += 31
            # months:
            if d2[1] > d1[1]:
                d1[0] -= 1  # from years
                d1[1] += 12 # to months
            days = d1[2] - d2[2]
            months = d1[1] - d2[1]
            years = d1[0] - d2[0]
            if days > 31: 
                months += days / 31
                days = days % 31
            if months > 12:
                years += months / 12
                months = months % 12
            # estimate: (years, months, days)
            # Check transitivity:
            eDate = date1 - (years, months, days)
            if eDate < date2: # too small
                diff = 0
                while eDate < date2 and diff < 60:
                    diff += 1
                    eDate = eDate + (0, 0, diff)
                if diff == 60:
                    return None
                return (years, months, days - diff)
            elif eDate > date2:
                diff = 0
                while eDate > date2 and diff > -60:
                    diff -= 1
                    eDate = eDate - (0, 0, abs(diff))
                if diff == -60:
                    return None
                return (years, months, days + diff)
            else:
                return (years, months, days)
        else:
            raise AttributeError, "unknown date sub type: %s " % type(other)

    # Can't use this (as is) as this breaks comparing dates to None
    #def __eq__(self, other):
    #    return self.sortval == other.sortval

    def __lt__(self, other):
        return self.sortval < other.sortval

    def __gt__(self, other):
        return self.sortval > other.sortval

    def is_equal(self, other):
        """
        Return 1 if the given Date instance is the same as the present
        instance IN ALL REGARDS. 
        
        Needed, because the __cmp__ only looks at the sorting value, and 
        ignores the modifiers/comments.
        """
        if self.modifier == other.modifier \
               and self.modifier == Date.MOD_TEXTONLY:
            value = self.text == other.text
        else:
            value = (self.calendar == other.calendar and 
                     self.modifier == other.modifier and 
                     self.quality == other.quality and 
                     self.dateval == other.dateval)
        return value

    def get_start_stop_range(self):
        """
        Return the minimal start_date, and a maximal stop_date corresponding 
        to this date, given in Gregorian calendar.
        
        Useful in doing range overlap comparisons between different dates.

        Note that we stay in (YR,MON,DAY) 
        """
        
        def yr_mon_day(dateval):
            """
            Local function to swap order for easy comparisons, and correct 
            year of slash date.
            
            Slash date is given as year1/year2, where year1 is Julian year, 
            and year2=year1+1 the Gregorian year.

            Slash date is already taken care of.
            """
            return (dateval[Date._POS_YR], dateval[Date._POS_MON], 
                    dateval[Date._POS_DAY])
        def date_offset(dateval, offset):
            """
            Local function to do date arithmetic: add the offset, return 
            (year,month,day) in the Gregorian calendar.
            """
            new_date = Date()
            new_date.set_yr_mon_day(dateval[0], dateval[1], dateval[2])
            return new_date.offset(offset)
        
        datecopy = Date(self)
        #we do all calculation in Gregorian calendar
        datecopy.convert_calendar(Date.CAL_GREGORIAN)
        start     = yr_mon_day(datecopy.get_start_date())
        stop      = yr_mon_day(datecopy.get_stop_date())

        if stop == (0, 0, 0):
            stop = start
            
        stopmax  = list(stop)
        if stopmax[0] == 0: # then use start_year, if one
            stopmax[0] = start[Date._POS_YR]
        if stopmax[1] == 0:
            stopmax[1] = 12
        if stopmax[2] == 0: 
            stopmax[2] = 31
        startmin  = list(start)
        if startmin[1] == 0:
            startmin[1] = 1
        if startmin[2] == 0:
            startmin[2] = 1
        # if BEFORE, AFTER, or ABOUT/EST, adjust:
        if self.modifier == Date.MOD_BEFORE:
            stopmax = date_offset(startmin, -1)
            fdiff = Config.get(Config.DATE_BEFORE_RANGE)
            startmin = (stopmax[0] - fdiff, stopmax[1], stopmax[2])
        elif self.modifier == Date.MOD_AFTER:
            startmin = date_offset(stopmax, 1)
            fdiff = Config.get(Config.DATE_AFTER_RANGE)
            stopmax = (startmin[0] + fdiff, startmin[1], startmin[2])
        elif (self.modifier == Date.MOD_ABOUT or
              self.quality == Date.QUAL_ESTIMATED):
            fdiff = Config.get(Config.DATE_ABOUT_RANGE)
            startmin = (startmin[0] - fdiff, startmin[1], startmin[2])
            stopmax = (stopmax[0] + fdiff, stopmax[1], stopmax[2])
        # return tuples not lists, for comparisons
        return (tuple(startmin), tuple(stopmax))
        
    def match(self, other_date, comparison="="):
        """
        Compare two dates using sophisticated techniques looking for any match 
        between two possible dates, date spans and qualities.
        
        The other comparisons for Date (is_equal() and __cmp() don't actually 
        look for anything other than a straight match, or a simple comparison 
        of the sortval.

        comparison =,== :
            Returns True if any part of other_date matches any part of self
        comparison < :
            Returns True if any part of other_date < any part of self
        comparison << :
            Returns True if all parts of other_date < all parts of self
        comparison > :
            Returns True if any part of other_date > any part of self
        comparison >> :
            Returns True if all parts of other_date > all parts of self
        """
        if (other_date.modifier == Date.MOD_TEXTONLY or
            self.modifier == Date.MOD_TEXTONLY):
            if comparison in ["=", "=="]:
                return (self.text.upper().find(other_date.text.upper()) != -1)
            else:
                return False

        # Obtain minimal start and maximal stop in Gregorian calendar
        other_start, other_stop = other_date.get_start_stop_range()
        self_start,  self_stop  = self.get_start_stop_range()

        if comparison in ["=", "=="]:
            # If some overlap then match is True, otherwise False.
            return ((self_start <= other_start <= self_stop) or
                    (self_start <= other_stop <= self_stop) or 
                    (other_start <= self_start <= other_stop) or 
                    (other_start <= self_stop <= other_stop))
        elif comparison == "<":
            # If any < any
            return self_start < other_stop
        elif comparison == "<<":
            # If all < all
            return self_stop < other_start
        elif comparison == ">":
            # If any > any
            return self_stop > other_start
        elif comparison == ">>":
            # If all > all
            return self_start > other_stop
        else:
            raise AttributeError, ("invalid match comparison operator: '%s'" % 
                                   comparison)
            
    def __str__(self):
        """
        Produce a string representation of the Date object. 
        
        If the date is not valid, the text representation is displayed. If
        the date is a range or a span, a string in the form of
        'YYYY-MM-DD - YYYY-MM-DD' is returned. Otherwise, a string in
        the form of 'YYYY-MM-DD' is returned.
        """
        if self.quality == Date.QUAL_ESTIMATED:
            qual = "est "
        elif self.quality == Date.QUAL_CALCULATED:
            qual = "calc "
        else:
            qual = ""

        if self.modifier == Date.MOD_BEFORE:
            pref = "bef "
        elif self.modifier == Date.MOD_AFTER:
            pref = "aft "
        elif self.modifier == Date.MOD_ABOUT:
            pref = "abt "
        else:
            pref = ""

        if self.calendar != Date.CAL_GREGORIAN:
            cal = " (%s)" % Date.calendar_names[self.calendar]
        else:
            cal = ""
            
        if self.modifier == Date.MOD_TEXTONLY:
            val = self.text
        elif self.modifier == Date.MOD_RANGE or self.modifier == Date.MOD_SPAN:
            val = "%04d-%02d-%02d - %04d-%02d-%02d" % (
                self.dateval[Date._POS_YR], self.dateval[Date._POS_MON], 
                self.dateval[Date._POS_DAY], self.dateval[Date._POS_RYR], 
                self.dateval[Date._POS_RMON], self.dateval[Date._POS_RDAY])
        else:
            val = "%04d-%02d-%02d" % (
                self.dateval[Date._POS_YR], self.dateval[Date._POS_MON], 
                self.dateval[Date._POS_DAY])
        return "%s%s%s%s" % (qual, pref, val, cal)

    def get_sort_value(self):
        """
        Return the sort value of Date object. 
        
        If the value is a text string, 0 is returned. Otherwise, the 
        calculated sort date is returned. The sort date is rebuilt on every 
        assignment.

        The sort value is an integer representing the value. A date of
        March 5, 1990 would have the value of 19900305.
        """
        return self.sortval

    def get_modifier(self):
        """
        Return an integer indicating the calendar selected. 
        
        The valid values are::
        
           MOD_NONE       = no modifier (default)
           MOD_BEFORE     = before
           MOD_AFTER      = after
           MOD_ABOUT      = about
           MOD_RANGE      = date range
           MOD_SPAN       = date span
           MOD_TEXTONLY   = text only
        """
        return self.modifier

    def set_modifier(self, val):
        """
        Set the modifier for the date.
        """
        if val not in (Date.MOD_NONE, Date.MOD_BEFORE, Date.MOD_AFTER, 
                       Date.MOD_ABOUT, Date.MOD_RANGE, Date.MOD_SPAN, 
                       Date.MOD_TEXTONLY):
            raise DateError("Invalid modifier")
        self.modifier = val

    def get_quality(self):
        """
        Return an integer indicating the calendar selected. 
        
        The valid values are::
        
           QUAL_NONE       = normal (default)
           QUAL_ESTIMATED  = estimated
           QUAL_CALCULATED = calculated
        """
        return self.quality

    def set_quality(self, val):
        """
        Set the quality selected for the date.
        """
        if val not in (Date.QUAL_NONE, Date.QUAL_ESTIMATED, 
                       Date.QUAL_CALCULATED):
            raise DateError("Invalid quality")
        self.quality = val
    
    def get_calendar(self):
        """
        Return an integer indicating the calendar selected. 
        
        The valid values are::

           CAL_GREGORIAN  - Gregorian calendar
           CAL_JULIAN     - Julian calendar
           CAL_HEBREW     - Hebrew (Jewish) calendar
           CAL_FRENCH     - French Republican calendar
           CAL_PERSIAN    - Persian calendar
           CAL_ISLAMIC    - Islamic calendar
        """
        return self.calendar

    def set_calendar(self, val):
        """
        Set the calendar selected for the date.
        """
        if val not in (Date.CAL_GREGORIAN, Date.CAL_JULIAN, Date.CAL_HEBREW, 
                       Date.CAL_FRENCH, Date.CAL_PERSIAN, Date.CAL_ISLAMIC):
            raise DateError("Invalid calendar")
        self.calendar = val

    def get_start_date(self):
        """
        Return a tuple representing the start date. 
        
        If the date is a compound date (range or a span), it is the first part 
        of the compound date. If the date is a text string, a tuple of
        (0, 0, 0, False) is returned. Otherwise, a date of (DD, MM, YY, slash)
        is returned. If slash is True, then the date is in the form of 1530/1.
        """
        if self.modifier == Date.MOD_TEXTONLY:
            val = Date.EMPTY
        else:
            val = self.dateval[0:4]
        return val

    def get_stop_date(self):
        """
        Return a tuple representing the second half of a compound date. 
        
        If the date is not a compound date, (including text strings) a tuple
        of (0, 0, 0, False) is returned. Otherwise, a date of (DD, MM, YY, slash)
        is returned. If slash is True, then the date is in the form of 1530/1.
        """
        if self.modifier == Date.MOD_RANGE or self.modifier == Date.MOD_SPAN:
            val = self.dateval[4:8]
        else:
            val = Date.EMPTY
        return val

    def _get_low_item(self, index):
        """
        Return the item specified.
        """
        if self.modifier == Date.MOD_TEXTONLY:
            val = 0
        else:
            val = self.dateval[index]
        return val

    def _get_low_item_valid(self, index):
        """
        Determine if the item specified is valid.
        """
        if self.modifier == Date.MOD_TEXTONLY:
            val = False
        else:
            val = self.dateval[index] != 0
        return val
        
    def _get_high_item(self, index):
        """
        Return the item specified.
        """
        if self.modifier == Date.MOD_SPAN or self.modifier == Date.MOD_RANGE:
            val = self.dateval[index]
        else:
            val = 0
        return val

    def get_year(self):
        """
        Return the year associated with the date. 
        
        If the year is not defined, a zero is returned. If the date is a 
        compound date, the lower date year is returned.
        """
        return self._get_low_item(Date._POS_YR)

    def set_yr_mon_day(self, year, month, day):
        """
        Set the year, month, and day values.
        """
        dv = list(self.dateval)
        dv[Date._POS_YR] = year
        dv[Date._POS_MON] = month
        dv[Date._POS_DAY] = day
        self.dateval = tuple(dv)
        self._calc_sort_value()

    def set_yr_mon_day_offset(self, year=0, month=0, day=0):
        """
        Set the year, month, and day values by offset.
        """
        dv = list(self.dateval)
        if dv[Date._POS_YR]:
            dv[Date._POS_YR] += year
        elif year:
            dv[Date._POS_YR] = year
        if dv[Date._POS_MON]:
            dv[Date._POS_MON] += month
        elif month:
            if month < 0:
                dv[Date._POS_MON] = 1 + month
            else:
                dv[Date._POS_MON] = month
        # Fix if month out of bounds:
        if month != 0: # only check if changed
            if dv[Date._POS_MON] == 0: # subtraction
                dv[Date._POS_MON] = 12
                dv[Date._POS_YR] -= 1
            elif dv[Date._POS_MON] < 0: # subtraction
                dv[Date._POS_YR] -= int((-dv[Date._POS_MON]) / 12) + 1
                dv[Date._POS_MON] = (dv[Date._POS_MON] % 12)
            elif dv[Date._POS_MON] > 12 or dv[Date._POS_MON] < 1:
                dv[Date._POS_YR] += int(dv[Date._POS_MON] / 12)
                dv[Date._POS_MON] = dv[Date._POS_MON] % 12
        self.dateval = tuple(dv)
        self._calc_sort_value()
        if day != 0 or dv[Date._POS_DAY] > 28:
            self.set_yr_mon_day(*self.offset(day))

    def copy_offset_ymd(self, year=0, month=0, day=0):
        """
        Return a Date copy based on year, month, and day offset.
        """
        orig_cal = self.calendar
        if self.calendar != 0:
            new_date = self.to_calendar("gregorian")
        else:
            new_date = self
        retval = Date(new_date)
        retval.set_yr_mon_day_offset(year, month, day)
        if orig_cal == 0:
            return retval
        else:
            retval.convert_calendar(orig_cal)
            return retval

    def copy_ymd(self, year=0, month=0, day=0):
        """
        Return a Date copy with year, month, and day set.
        """
        retval = Date(self)
        retval.set_yr_mon_day(year, month, day)
        return retval

    def set_year(self, year):
        """
        Set the year value.
        """
        self.dateval = self.dateval[0:2] + (year, ) + self.dateval[3:]
        self._calc_sort_value()

    def get_year_valid(self):
        """
        Return true if the year is valid.
        """
        return self._get_low_item_valid(Date._POS_YR)

    def get_month(self):
        """
        Return the month associated with the date. 
        
        If the month is not defined, a zero is returned. If the date is a 
        compound date, the lower date month is returned.
        """
        return self._get_low_item(Date._POS_MON)

    def get_month_valid(self):
        """
        Return true if the month is valid
        """
        return self._get_low_item_valid(Date._POS_MON)

    def get_day(self):
        """
        Return the day of the month associated with the date. 
        
        If the day is not defined, a zero is returned. If the date is a 
        compound date, the lower date day is returned.
        """
        return self._get_low_item(Date._POS_DAY)

    def get_day_valid(self):
        """
        Return true if the day is valid.
        """
        return self._get_low_item_valid(Date._POS_DAY)

    def get_valid(self):
        """ 
        Return true if any part of the date is valid.
        """
        return self.modifier != Date.MOD_TEXTONLY

    def get_stop_year(self):
        """
        Return the day of the year associated with the second part of a 
        compound date. 
        
        If the year is not defined, a zero is returned. 
        """
        return self._get_high_item(Date._POS_RYR)

    def get_stop_month(self):
        """
        Return the month of the month associated with the second part of a 
        compound date. 
        
        If the month is not defined, a zero is returned. 
        """
        return self._get_high_item(Date._POS_RMON)

    def get_stop_day(self):
        """
        Return the day of the month associated with the second part of a 
        compound date. 
        
        If the day is not defined, a zero is returned. 
        """
        return self._get_high_item(Date._POS_RDAY)

    def get_high_year(self):
        """
        Return the high year estimate. 
        
        For compound dates with non-zero stop year, the stop year is returned. 
        Otherwise, the start year is returned.
        """
        if self.is_compound():
            ret = self.get_stop_year()
            if ret:
                return ret
        else:
            return self.get_year()

    def get_text(self):
        """
        Return the text value associated with an invalid date.
        """
        return self.text

    def set(self, quality, modifier, calendar, value, text=None):
        """
        Set the date to the specified value. 
        
        Parameters are::

          quality  - The date quality for the date (see get_quality
                     for more information)
          modified - The date modifier for the date (see get_modifier
                     for more information)
          calendar - The calendar associated with the date (see
                     get_calendar for more information).
          value    - A tuple representing the date information. For a
                     non-compound date, the format is (DD, MM, YY, slash)
                     and for a compound date the tuple stores data as
                     (DD, MM, YY, slash1, DD, MM, YY, slash2)
          text     - A text string holding either the verbatim user input
                     or a comment relating to the date.

        The sort value is recalculated.
        """
        
        if modifier in (Date.MOD_NONE, Date.MOD_BEFORE, 
                        Date.MOD_AFTER, Date.MOD_ABOUT) and len(value) < 4:
            raise DateError("Invalid value. Should be: (DD, MM, YY, slash)")
        if modifier in (Date.MOD_RANGE, Date.MOD_SPAN) and len(value) < 8:
            raise DateError("Invalid value. Should be: (DD, MM, "
                            "YY, slash1, DD, MM, YY, slash2)")
        if modifier not in (Date.MOD_NONE, Date.MOD_BEFORE, Date.MOD_AFTER, 
                            Date.MOD_ABOUT, Date.MOD_RANGE, Date.MOD_SPAN, 
                            Date.MOD_TEXTONLY):
            raise DateError("Invalid modifier")
        if quality not in (Date.QUAL_NONE, Date.QUAL_ESTIMATED, 
                           Date.QUAL_CALCULATED):
            raise DateError("Invalid quality")
        if calendar not in (Date.CAL_GREGORIAN, Date.CAL_JULIAN,
                            Date.CAL_HEBREW, Date.CAL_FRENCH,
                            Date.CAL_PERSIAN, Date.CAL_ISLAMIC):
            raise DateError("Invalid calendar")

        self.quality = quality
        self.modifier = modifier
        self.calendar = calendar
        self.dateval = value
        year = max(value[Date._POS_YR], 1)
        month = max(value[Date._POS_MON], 1)
        day = max(value[Date._POS_DAY], 1)

        if year == 0 and month == 0 and day == 0:
            self.sortval = 0
        else:
            func = Date._calendar_convert[calendar]
            self.sortval = func(year, month, day)

        if self.get_slash() and self.get_calendar() != Date.CAL_JULIAN:
            self.set_calendar(Date.CAL_JULIAN)
            self.recalc_sort_value()

        if text:
            self.text = text

    def recalc_sort_value(self):
        """
        Recalculates the numerical sort value associated with the date
        and returns it. Public method.
        """
        self._calc_sort_value()
        return self.sortval

    def _calc_sort_value(self):
        """
        Calculate the numerical sort value associated with the date.
        """
        year = max(self.dateval[Date._POS_YR], 1)
        month = max(self.dateval[Date._POS_MON], 1)
        day = max(self.dateval[Date._POS_DAY], 1)
        if year == 0 and month == 0 and day == 0:
            self.sortval = 0
        else:
            func = Date._calendar_convert[self.calendar]
            self.sortval = func(year, month, day)

    def convert_calendar(self, calendar):
        """
        Convert the date from the current calendar to the specified calendar.
        """
        if calendar == self.calendar:
            return
        (year, month, day) = Date._calendar_change[calendar](self.sortval)
        if self.is_compound():
            ryear = max(self.dateval[Date._POS_RYR], 1)
            rmonth = max(self.dateval[Date._POS_RMON], 1)
            rday = max(self.dateval[Date._POS_RDAY], 1)
            sdn = Date._calendar_convert[self.calendar](ryear, rmonth, rday)
            (nyear, nmonth, nday) = Date._calendar_change[calendar](sdn)
            self.dateval = (day, month, year, self.dateval[Date._POS_SL], 
                            nday, nmonth, nyear, self.dateval[Date._POS_RSL])
        else:
            self.dateval = (day, month, year, self.dateval[Date._POS_SL])
        self.calendar = calendar

    def set_as_text(self, text):
        """
        Set the day to a text string, and assign the sort value to zero.
        """
        self.modifier = Date.MOD_TEXTONLY
        self.text = text
        self.sortval = 0

    def set_text_value(self, text):
        """
        Set the text string to a given text.
        """
        self.text = text

    def is_empty(self):
        """
        Return True if the date contains no information (empty text).
        """
        return (self.modifier == Date.MOD_TEXTONLY and not self.text) or \
               (self.get_start_date()==Date.EMPTY
                and self.get_stop_date()==Date.EMPTY)
        
    def is_compound(self):
        """
        Return True if the date is a date range or a date span.
        """
        return self.modifier == Date.MOD_RANGE \
               or self.modifier == Date.MOD_SPAN

    def is_regular(self):
        """
        Return True if the date is a regular date.
        
        The regular date is a single exact date, i.e. not text-only, not 
        a range or a span, not estimated/calculated, not about/before/after 
        date, and having year, month, and day all non-zero.
        """
        return self.modifier == Date.MOD_NONE \
               and self.quality == Date.QUAL_NONE \
               and self.get_year_valid() and self.get_month_valid() \
               and self.get_day_valid()

    def get_ymd(self):
        """
        Return (year, month, day).
        """
        return (self.get_year(), self.get_month(), self.get_day())

    def offset(self, value):
        """
        Return (year, month, day) of this date +- value.
        """
        return Date._calendar_change[Date.CAL_GREGORIAN](self.sortval + value)

    def offset_date(self, value):
        """
        Return (year, month, day) of this date +- value.
        """
        return Date(Date._calendar_change[Date.CAL_GREGORIAN](self.sortval + value))

    def lookup_calendar(self, calendar):
        """
        Lookup calendar name in the list of known calendars, even if translated.
        """
        calendar_lower = [n.lower() for n in Date.calendar_names]
        ui_lower = [n.lower() for n in Date.ui_calendar_names]
        if calendar.lower() in calendar_lower:
            return calendar_lower.index(calendar.lower())
        elif calendar.lower() in ui_lower:
            return ui_lower.index(calendar.lower())
        else:
            raise AttributeError("invalid calendar: '%s'" % calendar)

    def lookup_quality(self, quality):
        """
        Lookup date quality keyword, even if translated.
        """
        qualities = ["none", "estimated", "calculated"]
        ui_qualities = [_("none"), _("estimated"), _("calculated")]
        if quality.lower() in qualities:
            return qualities.index(quality.lower())
        elif quality.lower() in ui_qualities:
            return ui_qualities.index(quality.lower())
        else:
            raise AttributeError("invalid quality: '%s'" % quality)

    def lookup_modifier(self, modifier):
        """
        Lookup date modifier keyword, even if translated.
        """
        mods = ["none", "before", "after", "about", 
                "range", "span", "textonly"]
        ui_mods = [_("none"), _("before"), _("after"), _("about"), 
                   _("range"), _("span"), _("textonly")]
        if modifier.lower() in mods:
            return mods.index(modifier.lower())
        elif modifier.lower() in ui_mods:
            return ui_mods.index(modifier.lower())
        else:
            raise AttributeError("invalid modifier: '%s'" % modifier)
    
    def to_calendar(self, calendar_name):
        """
        Return a new Date object in the calendar calendar_name.
        
        >>> Date("Jan 1 1591").to_calendar("julian")
        1590-12-22 (Julian)
        """
        cal = self.lookup_calendar(calendar_name)
        retval = Date(self)
        retval.convert_calendar(cal)
        return retval

    def get_slash(self):
        """
        Return true if the date is a slash-date.
        """
        return self._get_low_item_valid(Date._POS_SL)



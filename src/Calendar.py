#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001  Donald N. Allingham
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
"""
Calendar conversion routines for GRAMPS. 

The original algorithms for this module came from Scott E. Lee's
C implementation. The original C source can be found at Scott's
web site at http://www.scottlee.com
"""

__author__ = "Donald N. Allingham"
__version__ = "$Revision$"

import math
from intl import gettext as _
import re

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
UNDEF = -999999
EXACT = 0
ABOUT = 1
BEFORE = 2
AFTER = 3

#-------------------------------------------------------------------------
#
# Regular expressions for parsing
#
#-------------------------------------------------------------------------
_modifiers = '(' + \
             _("abt\.?") + '|' + \
             _("about") + '|' + \
             _("est\.?") + '|' + \
             _("circa") + '|' + \
             _("around") + '|' + \
             _("before") + '|' + \
             _("after") + '|' + \
             _("aft\.?") + '|' + \
             _("bef\.?") + \
             '|abt|aft|after|before|bef)'
_start = "^\s*" + _modifiers + "?\s*"
fmt1 = re.compile(_start+"(\S+)(\s+\d+\s*,)?\s*([?\d]+)?\s*$", re.IGNORECASE)
fmt2 = re.compile(_start+"(\d+)\.?\s+([^\d]+)(\s+\d+)?\s*$", re.IGNORECASE)
fmt3 = re.compile(_start+r"([?\d]+)\s*[./-]\s*([?\d]+)\s*[./-]\s*([?\d]+)\s*$",
               re.IGNORECASE)
fmt7 = re.compile(_start+r"([?\d]+)\s*[./-]\s*([?\d]+)\s*$", re.IGNORECASE)
fmt4 = re.compile(_start+"(\S+)\s+(\d+)\s*$", re.IGNORECASE)
fmt5 = re.compile(_start+"(\d+)\s*$", re.IGNORECASE)
fmt6 = re.compile(_start+"(\S+)\s*$", re.IGNORECASE)


#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def set_format_code(code):
    Calendar.FORMATCODE = code
    
#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def get_format_code():
    return Calendar.FORMATCODE

#-------------------------------------------------------------------------
#
# Calendar - base calendar
#
#-------------------------------------------------------------------------
class Calendar:

    ENTRYCODE = 0
    FORMATCODE = 0

    MONTHS = [
        _("January"),   _("February"),  _("March"),    _("April"),
        _("May"),       _("June"),      _("July"),     _("August"),
        _("September"), _("October"),   _("November"), _("December")]

    M2NUM = {
        (MONTHS[0][0:3]).lower(): 1,   (MONTHS[1][0:3]).lower(): 2,
        (MONTHS[2][0:3]).lower(): 3,   (MONTHS[3][0:3]).lower(): 4,
        (MONTHS[4][0:3]).lower(): 5,   (MONTHS[5][0:3]).lower(): 6,
        (MONTHS[6][0:3]).lower(): 7,   (MONTHS[7][0:3]).lower(): 8,
        (MONTHS[8][0:3]).lower(): 9,   (MONTHS[9][0:3]).lower(): 10,
        (MONTHS[10][0:3]).lower(): 11, (MONTHS[11][0:3]).lower(): 12
        }

    M2V = {
        _("abt")    : ABOUT,        _("about")  : ABOUT,
        _("abt.")   : ABOUT,        _("est")    : ABOUT,
        _("est.")   : ABOUT,        _("circa")  : ABOUT,
        _("around") : ABOUT,        _("before") : BEFORE,
        _("bef")    : BEFORE,       _("bef.")   : BEFORE,
        _("after")  : AFTER,        _("aft.")   : AFTER,
        _("aft")    : AFTER,
            # And the untranslated versions for reading saved data from XML.
        "abt"	    : ABOUT,        "about"	: ABOUT,
        "bef"       : BEFORE,       "bef."      : BEFORE,
        "aft."      : AFTER,        "abt."      : ABOUT,
        "est."      : ABOUT,        "est"       : ABOUT,
        "after"	    : AFTER,        "before"    : BEFORE,
        "aft"       : AFTER,
        }

    MODE = {
        ABOUT : _("about"),
        BEFORE : _("before"),
        AFTER : _("after")}

    EM2NUM ={
        "jan" : 1, "feb" : 2, "mar" : 3, "apr" : 4,
        "may" : 5, "jun" : 6, "jul" : 7, "aug" : 8,
        "sep" : 9, "oct" :10, "nov" : 11,"dec" : 12
        }

    NAME  = "Undefined Calendar"
    TNAME = _("Undefined Calendar")

    def mlen(self):
        return -1

    def __init__(self,source=None):
        if source:
            self.get_ymd(source.get_sdn())

    def month(self,val):
        try:
            return Calendar.MONTHS[val-1]
        except:
            return "Illegal Month"

    def check(self):
        return 0

    def quote_display(self,year,month,day,mode):
        return "%s (%s)" % (text,Calendar.NAME)

    def display(self,year,month,day,mode):
        return _FMT_FUNC[Calendar.FORMATCODE](self,year,month,day,mode)

    def format_yymmdd(self,year,month,day,mode):
        if month == UNDEF and day == UNDEF and year == UNDEF :
            return ""
        elif day == UNDEF:
            if month == UNDEF:
                retval = str(self.year)
            elif self.year == UNDEF:
                retval = "????-%02d-??" % (month)
            else:
                retval = "%04d-%02d" % (year,month)
        elif month == UNDEF:
            retval = "%04d-??-%02d" % (year,day)
        else:
            if year == UNDEF:
                retval = "????-%02d-%02d" % (month,day)
            else:
                retval = "%04d-%02d-%02d" % (year,month,day)
        return self.fmt_mode(retval,mode)

    def format_mon_dd_year(self,year,month,day,mode):
        """
        Formats the date in the form of DD Month Year, such as
        January 20, 2000
        """
        if month == UNDEF and day == UNDEF and year == UNDEF:
            return ""
        elif day == UNDEF:
            if month == UNDEF:
                retval = str(year)
            elif year == UNDEF:
                retval = self.month(month)
            else:
                retval = "%s %d" % (self.month(month),year)
        elif month == UNDEF:
            retval = str(year)
        else:
            if year == UNDEF:
                retval = "%s %d, ????" % (self.month(month),day)
            else:
                retval = "%s %d, %d" % (self.month(month),day,year)

        return self.fmt_mode(retval,mode)


    def format_MON_dd_year(self,year,month,day,mode):
        """
        Formats the date in the form of DD Month Year, such as
        January 20, 2000
        """
        if month == UNDEF and day == UNDEF and year == UNDEF:
            return ""
        elif day == UNDEF:
            if month == UNDEF:
                retval = str(year)
            elif year == UNDEF:
                retval = self.month(month).upper()[0:3]
            else:
                retval = "%s %d" % (self.month(month).upper()[0:3],year)
        elif month == UNDEF:
            retval = str(year)
        else:
            if year == UNDEF:
                retval = "%s %d, ????" % (self.month(month).upper()[0:3],day)
            else:
                retval = "%s %d, %d" % (self.month(month).upper()[0:3],day,year)

        return self.fmt_mode(retval,mode)

    def format_dd_mon_year(self,year,month,day,mode):
        """
        Formats the date in the form of DD Month Year, such as
        20 January 2000
        """
        if year==UNDEF:
            if month == UNDEF:
                d = ""
            elif day == UNDEF:
                d = self.month(month)
            else:
                d = "%02d %s" % (day,self.month(month))
        elif month == UNDEF:
            d = str(year)
        elif day == UNDEF:
            d = "%s %d" % (self.month(month),year)
        else:
            d = "%02d %s %d" % (day,self.month(month),year)

        return self.fmt_mode(d,mode)

    def format_dd_MON_year(self,year,month,day,mode):
        """
        Formats the date in the form of DD. Month Year, such as
        20. January 2000
        """
        if month == UNDEF and day == UNDEF and year == UNDEF :
            return ""
        elif day == UNDEF:
            if month == UNDEF:
                retval = str(year)
            elif year == UNDEF:
                retval = self.month(month).upper()[0:3]
            else:
                retval = "%s %d" % (self.month(month).upper()[0:3],year)
        elif month == UNDEF:
            retval = str(year)
        else:
            month_str = self.month(month).upper()[0:3]
            if self.year == UNDEF:
                retval = "%d %s ????" % (day,month_str)
            else:
                retval = "%d %s %d" % (day,month_str,year)

        return self.fmt_mode(retval,mode)

    def format_dd_dot_MON_year(self,year,month,day,mode):
        """
        Formats the date in the form of DD. Month Year, such as
        20. January 2000
        """
        if month == UNDEF and day == UNDEF and year == UNDEF :
            return ""
        elif day == UNDEF:
            if month == UNDEF:
                retval = str(year)
            elif year == UNDEF:
                retval = self.month(month).upper()[0:3]
            else:
                retval = "%s %d" % (self.month(month).upper()[0:3],year)
        elif month == UNDEF:
            retval = str(year)
        else:
            month_str = self.month(month).upper()[0:3]
            if self.year == UNDEF:
                retval = "%d. %s ????" % (day,month_str)
            else:
                retval = "%d. %s %d" % (day,month_str,year)

        return self.fmt_mode(retval,mode)

    def format4(self,year,month,day,mode):
        return self._get_mmddyyyy(year,month,day,mode,"/")

    def format5(self,year,month,day,mode):
        return self._get_mmddyyyy(year,month,day,mode,"-")

    def format6(self,year,month,day,mode):
        return self._get_ddmmyyyy(year,month,day,mode,"/")

    def format7(self,year,month,day,mode):
        return self._get_ddmmyyyy(year,month,day,mode,"-")

    def format8(self,year,month,day,mode):
        return self._get_mmddyyyy(year,month,day,mode,".")

    def format9(self,year,month,day,mode):
        return self._get_ddmmyyyy(year,month,day,mode,".")

    def format11(self,year,month,day,mode):
        return self._get_yyyymmdd(year,month,day,mode,"/")

    def format12(self,year,month,day,mode):
        return self._get_yyyymmdd(year,month,day,mode,"-")

    def format13(self,year,month,day,mode):
        return self._get_yyyymmdd(year,month,day,mode,".")

    def _get_mmddyyyy(self,year,month,day,mode,sep):
        if month == UNDEF and day == UNDEF and year == UNDEF :
            return ""
        elif day == UNDEF:
            if month == UNDEF:
                retval = str(year)
            elif year == UNDEF:
                retval = "%02d%s??%s??" % (month+1,sep,sep)
            else:
                retval = "%02d%s??%s%04d" % (month+1,sep,sep,year)
        elif month == UNDEF:
            retval = "??%s%02d%s%04d" % (sep,day,sep,year)
        else:
            if year == UNDEF:
                retval = "%02d%s%02d%s????" % (month+1,sep,day,sep)
            else:
                retval = "%02d%s%02d%s%04d" % (month+1,sep,day,sep,year)

        return self.fmt_mode(retval,mode)

    def _get_yyyymmdd(self,year,month,day,mode,sep):
        retval = ""
        
        if month == UNDEF and day == UNDEF and year == UNDEF :
            pass
        elif day == UNDEF:
            if month == UNDEF:
                retval = str(self.year)
            elif year == UNDEF:
                retval = "????%s%02d%s??" % (sep,month+1,sep)
            else:
                retval = "%04d%s%02d" % (year,sep,month+1)
        elif month == UNDEF:
            retval = "%04d%s??%s%02d" % (year,sep,sep,day)
        else:
            if year == UNDEF:
                retval = "????%s%02d%s%02d" % (sep,month+1,sep,day)
            else:
                retval = "%02d%s%02d%s%02d" % (year,sep,month+1,sep,day)

        return self.fmt_mode(retval,mode)

    def _get_ddmmyyyy(self,year,month,day,mode,sep):
        retval = ""
        
        if month == UNDEF and day == UNDEF and year == UNDEF :
            pass
        elif day == UNDEF:
            if month == UNDEF:
                retval = str(year)
            elif year == UNDEF:
                retval = "??%s%02d%s??" % (sep,month+1,sep)
            else:
                retval = "??%s%02d%s%04d" % (sep,month+1,sep,year)
        elif month == UNDEF:
            retval = "%02d%s??%s%04d" % (day,sep,sep,year)
        else:
            if year == UNDEF:
                retval = "%02d%s%02d%s????" % (day,sep,month+1,sep)
            else:
                retval = "%02d%s%02d%s%04d" % (day,sep,month+1,sep,year)

        return self.fmt_mode(retval,mode)

    def fmt_mode(self,val,mode):
        if Calendar.MODE.has_key(mode):
            return "%s %s" % (Calendar.MODE[mode],val)
        else:
            return val

    def get_ymd(self,val):
        return (0,0,0)

    def get_sdn(self,y,m,d):
        return 0

    def set_mode_value(self,val):
        if not val:
            return EXACT
        else:
            try:
                return Calendar.M2V[val.lower()]
            except KeyError:
                return EXACT

    def set_value(self,s):
        try:
            return int(s)
        except:
            return UNDEF

    def set_month_string(self,text):
        val = unicode(text[0:self.mlen()]).lower()
        try:
            return Calendar.M2NUM[val]
        except KeyError:
            if Calendar.EM2NUM.has_key(val):
                return Calendar.EM2NUM[val]
            else:
                return UNDEF

    def set(self,text):
        mode = UNDEF
        year = UNDEF
        month = UNDEF
        day = UNDEF
        
        match = fmt2.match(text)
        if match != None:
            matches = match.groups()
            mode = self.set_mode_value(matches[0])
            month = self.set_month_string(matches[2])
            day = self.set_value(matches[1])
            if len(matches) == 4 and matches[3] != None:
                year = self.set_value(matches[3])
            return (year,month,day,mode)
        
        match = fmt5.match(text)
        if match != None:
            matches = match.groups()
            mode = self.set_mode_value(matches[0]) 
            year = self.set_value(matches[1])
            return (year,month,day,mode)

        match = fmt7.match(text)
        if match != None:
            matches = match.groups()
            mode = self.set_mode_value(matches[0])
            if Calendar.ENTRYCODE == 2:
                month = self.set_value(matches[2])
                year = self.set_value(matches[1])
            else:
                month = self.set_value(matches[1])
                year = self.set_value(matches[2])
            return (year,month,day,mode)

        match = fmt3.match(text)
        if match != None:
            matches = match.groups()
            mode = self.set_mode_value(matches[0])
            if Calendar.ENTRYCODE == 0:
                month = self.set_value(matches[1])
                day = self.set_value(matches[2])
                year = self.set_value(matches[3])
            elif Calendar.ENTRYCODE == 1:
                month = self.set_value(matches[2])
                day = self.set_value(matches[1])
                year = self.set_value(matches[3])
            else:
                month = self.set_value(matches[2])
                day = self.set_value(matches[3])
                year = self.set_value(matches[1])
            return (year,month,day,mode)

        match = fmt1.match(text)
        if match != None:
            matches = match.groups()
            mode = self.set_mode_value(matches[0])
            month = self.set_month_string(unicode(matches[1]))
            if matches[2]:
                val = matches[2].replace(',','')
                day = self.set_value(val)
            year = self.set_value(matches[3])
            return (year,month,day,mode)

        match = fmt4.match(text)
        if match != None:
            matches = match.groups()
            mode = self.set_mode_value(matches[0])
            month = self.set_month_string(unicode(matches[1]))
            if len(matches) == 4:
                year = self.set_value(matches[3])
            return (year,month,day,mode)

        match = fmt6.match(text)
        if match != None:
            matches = match.groups()
            mode = self.set_mode_value(matches[0])
            month = self.set_value(matches[1])

        return (year,month,day,mode)

#-------------------------------------------------------------------------
#
# Hebrew calendar
#
#-------------------------------------------------------------------------
class Hebrew(Calendar):
    """Jewish Calendar"""
    
    HALAKIM_PER_HOUR = 1080
    HALAKIM_PER_DAY  = 25920
    HALAKIM_PER_LUNAR_CYCLE = ((29 * HALAKIM_PER_DAY) + 13753)
    HALAKIM_PER_METONIC_CYCLE = (HALAKIM_PER_LUNAR_CYCLE * (12 * 19 + 7))
    
    SDN_OFFSET = 347997
    NEW_MOON_OF_CREATION = 31524

    SUNDAY   = 0
    MONDAY   = 1
    TUESDAY  = 2
    WEDNESDAY= 3
    FRIDAY   = 5

    NOON = (18 * HALAKIM_PER_HOUR)
    AM3_11_20 = ((9 * HALAKIM_PER_HOUR) + 204)
    AM9_32_43 = ((15 * HALAKIM_PER_HOUR) + 589)

    monthsPerYear = [
        12, 12, 13, 12, 12, 13, 12, 13, 12, 12,
        13, 12, 12, 13, 12, 12, 13, 12, 13 ]

    yearOffset = [
        0, 12, 24, 37, 49, 61, 74, 86, 99, 111, 123,
        136, 148, 160, 173, 185, 197, 210, 222 ]

    MONTHS = [
        "Tishri", "Heshvan", "Kislev", "Tevet",  "Shevat", "AdarI",
        "AdarII", "Nisan",  "Iyyar",   "Sivan",  "Tammuz", "Av",
        "Elul",]

    M2NUM = {
        "tishri" : 1, "heshvan" : 2, "kislev" : 3, "tevet" : 4,
        "shevat" : 5, "adari"   : 6, "adarii" : 7, "nisan" : 8,
        "iyyar"  : 9, "sivan"   :10, "tammuz" :11, "av"    : 12,
        "elul"   : 13,"tsh"     : 1, "csh"    : 2, "ksl"   : 3,
        "tvt"    : 4, "shv"     : 5, "adr"    : 6, "ads"   : 7,
        "nsn"    : 8, "iyr"     : 9, "svn"    :10, "tmz"   : 11,
        "aav"    :12, "ell"     :13,
        }

    NAME = "Hebrew"
    TNAME = _("Hebrew")
    
    def quote_display(self,year,month,day,mode):
        return "%s (%s)" % (self.display(year,month,day,mode),Hebrew.NAME)

    def month(self,val):
        try:
            return Hebrew.MONTHS[val-1]
        except:
            return "Illegal Month"

    def set_month_string(self,text):
        try:
            return Hebrew.M2NUM[unicode(text.lower())]
        except KeyError:
            return UNDEF

    def Tishri1(self,metonicYear, moladDay, moladHalakim):

        tishri1 = moladDay
        dow = tishri1 % 7
        leapYear = metonicYear in [ 2, 5, 7, 10, 13, 16, 18]
        lastWasLeapYear = metonicYear in [ 3, 6, 8, 11, 14, 17, 0]

        # Apply rules 2, 3 and 4.
        if ((moladHalakim >= Hebrew.NOON) or
            ((not leapYear) and dow == Hebrew.TUESDAY and
             moladHalakim >= Hebrew.AM3_11_20) or
            (lastWasLeapYear and dow == Hebrew.MONDAY and moladHalakim >= Hebrew.AM9_32_43)) :
            tishri1 = tishri1 + 1
            dow = dow + 1
            if dow == 7:
                dow = 0

        # Apply rule 1 after the others because it can cause an additional
        # delay of one day

        if dow == Hebrew.WEDNESDAY or dow == Hebrew.FRIDAY or dow == Hebrew.SUNDAY:
            tishri1 = tishri1 + 1

        return tishri1

    def MoladOfMetonicCycle(self,metonicCycle):

        # Start with the time of the first molad after creation.

        r1 = Hebrew.NEW_MOON_OF_CREATION

        # Calculate metonicCycle * HALAKIM_PER_METONIC_CYCLE.  The upper 32
        # bits of the result will be in r2 and the lower 16 bits will be
        # in r1.

        r1 = r1 + (metonicCycle * (Hebrew.HALAKIM_PER_METONIC_CYCLE & 0xFFFF))
        r2 = r1 >> 16
        r2 = r2 + (metonicCycle * ((Hebrew.HALAKIM_PER_METONIC_CYCLE >> 16) & 0xFFFF))
        
        # Calculate r2r1 / HALAKIM_PER_DAY.  The remainder will be in r1, the
        # upper 16 bits of the quotient will be in d2 and the lower 16 bits
        # will be in d1.
        
        d2 = r2 / Hebrew.HALAKIM_PER_DAY
        r2 = r2 - (d2 * Hebrew.HALAKIM_PER_DAY)
        r1 = (r2 << 16) | (r1 & 0xFFFF)
        d1 = r1 / Hebrew.HALAKIM_PER_DAY
        r1 = r1 - ( d1 * Hebrew.HALAKIM_PER_DAY)
        
        MoladDay = (d2 << 16) | d1
        MoladHalakim = r1
        
        return (MoladDay,MoladHalakim)

    def TishriMolad(self,inputDay):

        # Estimate the metonic cycle number.  Note that this may be an under
        # estimate because there are 6939.6896 days in a metonic cycle not
        # 6940, but it will never be an over estimate.  The loop below will
        # correct for any error in this estimate. */
        
        metonicCycle = (inputDay + 310) / 6940
        
        # Calculate the time of the starting molad for this metonic cycle. */
        
        (moladDay, moladHalakim) = self.MoladOfMetonicCycle(metonicCycle)
        
        # If the above was an under estimate, increment the cycle number until
        # the correct one is found.  For modern dates this loop is about 98.6%
        # likely to not execute, even once, because the above estimate is
        # really quite close.
        
        while moladDay < (inputDay - 6940 + 310): 
            metonicCycle = metonicCycle + 1
            moladHalakim = moladHalakim + Hebrew.HALAKIM_PER_METONIC_CYCLE
            moladDay = moladDay + ( moladHalakim / Hebrew.HALAKIM_PER_DAY)
            moladHalakim = moladHalakim % Hebrew.HALAKIM_PER_DAY

        # Find the molad of Tishri closest to this date.

        for metonicYear in range(0,18):
            if moladDay > inputDay - 74:
                break

            moladHalakim = moladHalakim + \
                           (Hebrew.HALAKIM_PER_LUNAR_CYCLE * Hebrew.monthsPerYear[metonicYear])
            moladDay =  moladDay + (moladHalakim / Hebrew.HALAKIM_PER_DAY)
            moladHalakim = moladHalakim % Hebrew.HALAKIM_PER_DAY
        else:
            metonicYear = metonicYear + 1
        return (metonicCycle, metonicYear, moladDay, moladHalakim)

    def StartOfYear(self,year):

        MetonicCycle = (year - 1) / 19;
        MetonicYear = (year - 1) % 19;
        (MoladDay, MoladHalakim) = self.MoladOfMetonicCycle(MetonicCycle)

        MoladHalakim = MoladHalakim + (Hebrew.HALAKIM_PER_LUNAR_CYCLE * Hebrew.yearOffset[MetonicYear])
        MoladDay = MoladDay + (MoladHalakim / Hebrew.HALAKIM_PER_DAY)
        MoladHalakim = MoladHalakim % Hebrew.HALAKIM_PER_DAY
        
        pTishri1 = self.Tishri1(MetonicYear, MoladDay, MoladHalakim);
        
        return (MetonicCycle, MetonicYear, MoladDay, MoladHalakim, pTishri1)

    def get_ymd(self,sdn):
        """Converts an SDN number to a Julian calendar date"""
        
        if sdn <= Hebrew.SDN_OFFSET :
            return (0,0,0)
        
        inputDay = sdn - Hebrew.SDN_OFFSET

        (metonicCycle, metonicYear, day, halakim) = self.TishriMolad(inputDay)
        tishri1 = self.Tishri1(metonicYear, day, halakim);
        
        if inputDay >= tishri1:
            # It found Tishri 1 at the start of the year
        
            Year = (metonicCycle * 19) + metonicYear + 1
            if inputDay < tishri1 + 59:
                if inputDay < tishri1 + 30:
                    Month = 1
                    Day = inputDay - tishri1 + 1
                else:
                    Month = 2
                    Day = inputDay - tishri1 - 29
                return (Year, Month, Day)

            # We need the length of the year to figure this out, so find
            # Tishri 1 of the next year. */

            halakim = halakim + (Hebrew.HALAKIM_PER_LUNAR_CYCLE * Hebrew.monthsPerYear[metonicYear])
            day = day + (halakim / Hebrew.HALAKIM_PER_DAY)
            halakim = halakim % Hebrew.HALAKIM_PER_DAY;
            tishri1After = self.Tishri1((metonicYear + 1) % 19, day, halakim);
        else:
            # It found Tishri 1 at the end of the year.

            Year = metonicCycle * 19 + metonicYear
            if inputDay >= tishri1 - 177:
                # It is one of the last 6 months of the year.
                if inputDay > tishri1 - 30:
                    Month = 13
                    Day = inputDay - tishri1 + 30
                elif inputDay > tishri1 - 60:
                    Month = 12
                    Day = inputDay - tishri1 + 60
                elif inputDay > tishri1 - 89:
                    Month = 11
                    Day = inputDay - tishri1 + 89
                elif inputDay > tishri1 - 119:
                    Month = 10
                    Day = inputDay - tishri1 + 119
                elif inputDay > tishri1 - 148:
                    Month = 9
                    Day = inputDay - tishri1 + 148
                else:
                    Month = 8
                    Day = inputDay - tishri1 + 178
                return (Year,Month,Day)
            else:
                if Hebrew.monthsPerYear[(Year - 1) % 19] == 13:
                    Month = 7
                    Day = inputDay - tishri1 + 207
                    if Day > 0:
                        return (Year,Month,Day)
                    Month = Month - 1
                    Day = Day + 30
                    if Day > 0:
                        return (Year,Month,Day)
                    Month = Month - 1
                    Day = Day + 30
                else:
                    Month = 6
                    Day = inputDay - tishri1 + 207
                    if Day > 0:
                        return (Year,Month,Day)
                    Month = Month - 1
                    Day = Day + 30
                    
                if Day > 0:
                    return (Year,Month,Day)
                Month = Month - 1
                Day = Day + 29
                if Day > 0:
                    return (Year,Month,Day)

                # We need the length of the year to figure this out, so find
                # Tishri 1 of this year
                tishri1After = tishri1;
                (metonicCycle,metonicYear,day,halakim) = self.TishriMolad(day-365)
                tishri1 = self.Tishri1(metonicYear, day, halakim)

        yearLength = tishri1After - tishri1;
        cday = inputDay - tishri1 - 29;
        if yearLength == 355 or yearLength == 385 :
            # Heshvan has 30 days 
            if day <= 30:
                Month = 2
                Day = cday
                return (Year,Month,Day)
            day = day - 30
        else:
            # Heshvan has 29 days
            if day <= 29:
                Month = 2
                Day = cday
                return (Year,Month,Day)

            cday = cday - 29

        # It has to be Kislev
        return (Year,3,cday)

    def get_sdn(self,year, month, day):
        """Converts a Jewish calendar date to an SDN number"""
        if year <= 0 or day <= 0 or day > 30 : 
            return 0
        
        if month == 1 or month == 2:
            # It is Tishri or Heshvan - don't need the year length. 
            (metonicCycle,metonicYear,moladDay,moladHalakim,tishri1) = self.StartOfYear(year)
            if month == 1:
                sdn = tishri1 + day - 1
            else:
                sdn = tishri1 + day + 29
        elif month == 3:
            # It is Kislev - must find the year length.

            # Find the start of the year. 
            (metonicCycle,metonicYear,moladDay,moladHalakim,tishri1) = self.StartOfYear(year)

            # Find the end of the year.
            moladHalakim = moladHalakim + (Hebrew.HALAKIM_PER_LUNAR_CYCLE*Hebrew.monthsPerYear[metonicYear])
            moladDay = moladDay + (moladHalakim / Hebrew.HALAKIM_PER_DAY)
            moladHalakim = moladHalakim % Hebrew.HALAKIM_PER_DAY
            tishri1After = self.Tishri1((metonicYear + 1) % 19, moladDay, moladHalakim)
            
            yearLength = tishri1After - tishri1
            
            if yearLength == 355 or yearLength == 385:
                sdn = tishri1 + day + 59
            else:
                sdn = tishri1 + day + 58
        elif month == 4 or month == 5 or month == 6:
            # It is Tevet, Shevat or Adar I - don't need the year length

            (metonicCycle,metonicYear,moladDay,moladHalakim,tishri1After) = self.StartOfYear(year+1)
            
            if Hebrew.monthsPerYear[(year - 1) % 19] == 12:
                lengthOfAdarIAndII = 29
            else:
                lengthOfAdarIAndII = 59

                if month == 4:
                    sdn = tishri1After + day - lengthOfAdarIAndII - 237
                elif month == 5:
                    sdn = tishri1After + day - lengthOfAdarIAndII - 208
                else:
                    sdn = tishri1After + day - lengthOfAdarIAndII - 178
        else:
            # It is Adar II or later - don't need the year length.
            (metonicCycle,metonicYear,moladDay,moladHalakim,tishri1After) = self.StartOfYear(year+1)
            
            if month == 7:
                sdn = tishri1After + day - 207
            elif month == 8:
                sdn = tishri1After + day - 178
            elif month == 9:
                sdn = tishri1After + day - 148
            elif month == 10:
                sdn = tishri1After + day - 119
            elif month == 11:
                sdn = tishri1After + day - 89
            elif month == 12:
                sdn = tishri1After + day - 60
            elif month == 13:
                sdn = tishri1After + day - 30
            else:
                return 0
            return sdn + Hebrew.SDN_OFFSET

#-------------------------------------------------------------------------
#
# Persian
#
#-------------------------------------------------------------------------
class Persian(Calendar):
    """Persian Calendar"""

    EPOCH = 1948320.5
    SDN_475_1_1 = 2121446

    MONTHS = [ "Farvardin", "Ordibehesht", "Khordad", "Tir", "Mordad",
               "Shahrivar", "Mehr", "Aban", "Azar", "Dey", "Bahman", "Esfand" ]

    M2NUM = {
        "farvardin" : 1,   "ordibehesht" : 2,     "khordad" : 3,
        "tir" : 4,         "mordad" : 5,          "shahrivar" : 6,
        "mehr" : 7,        "aban" : 8,            "azar" : 9,
        "dey" : 10,        "bahman" : 11,         "esfand" : 12
        }

    NAME = "Persian"
    TNAME = _("Persian")

    def quote_display(self,year,month,day,mode):
        return "%s (%s)" % (self.display(year,month,day,mode),Persian.NAME)

    def set_month_string(self,text):
        try:
            return Persian.M2NUM[unicode(text.lower())]
        except KeyError:
            return UNDEF

    def month(self,val):
        try:
            return Persian.MONTHS[val-1]
        except:
            return "Illegal Month"

    def get_sdn(self,year, month, day):
        if year >= 0:
            epbase = year - 474
        else:
            epbase = year - 473
        
        epyear = 474 + epbase % 2820

        if month <= 7:
            v1 = (month - 1) * 31
        else:
            v1 = ((month - 1) * 30) + 6
        v2 = math.floor(((epyear * 682) - 110) / 2816)
        v3 = (epyear - 1) * 365 + day
        v4 = math.floor(epbase / 2820) * 1029983
        
        return int(math.ceil(v1 + v2 + v3 + v4 + Persian.EPOCH - 1))

    def get_ymd(self,sdn):
        sdn = math.floor(sdn) + 0.5
        
        depoch = sdn - self.get_sdn(475,1,1)
        cycle = math.floor(depoch / 1029983)
        cyear = depoch % 1029983
        if cyear == 1029982:
            ycycle = 2820
        else:
            aux1 = math.floor(cyear / 366)
            aux2 = cyear % 366
            ycycle = math.floor(((2134 * aux1) + (2816 * aux2) + 2815) / 1028522) + aux1 + 1;
            
        year = ycycle + (2820 * cycle) + 474
        if year <= 0:
            year = year - 1;

        yday = sdn - self.get_sdn(year, 1, 1) + 1
        if yday < 186:
            month = math.ceil(yday / 31)
        else:
            month = math.ceil((yday - 6) / 30)
        day = (sdn - self.get_sdn(year, month, 1)) + 1
        return (int(year), int(month), int(day))

#-------------------------------------------------------------------------
#
# FrenchRepublic
#
#-------------------------------------------------------------------------
class FrenchRepublic(Calendar):
    """French Republic Calendar"""

    SDN_OFFSET         = 2375474
    DAYS_PER_4_YEARS   = 1461
    DAYS_PER_MONTH     = 30
    FIRST_VALID        = 2375840
    LAST_VALID         = 2380952

    MONTHS = [
        unicode("Vendémiaire",'latin-1'),  unicode("Brumaire",'latin-1'),
        unicode("Frimaire",'latin-1'),     unicode("Nivôse",'latin-1'),
        unicode("Pluviôse",'latin-1'),     unicode("Ventôse",'latin-1'),
        unicode("Germinal",'latin-1'),     unicode("Floréal",'latin-1'),
        unicode("Prairial",'latin-1'),     unicode("Messidor",'latin-1'),
        unicode("Thermidor",'latin-1'),    unicode("Fructidor",'latin-1'),
        unicode("Extra",'latin-1'),]

    M2NUM = {
        "vend" : 1, "brum" : 2, "frim" : 3, "nivo" : 4, "pluv" : 5, "vent" : 6,
        "germ" : 7, "flor" : 8, "prai" : 9, "mess" :10, "ther" :11, "fruc" :12,
        "extr" : 13,"comp" :13, unicode("nivô",'latin-1') : 4
        }

    NAME = "French Republican"
    TNAME = _("French Republican")

    def quote_display(self,year,month,day,mode):
        return "%s (%s)" % (self.display(year,month,day,mode),FrenchRepublic.NAME)

    def mlen(self):
        return 4

    def month(self,val):
        try:
            return FrenchRepublic.MONTHS[val-1]
        except:
            return "Illegal Month"

    def set_month_string(self,text):
        val = (unicode(text)[0:4]).lower()
        try:
            return FrenchRepublic.M2NUM[val]
        except KeyError:
            return UNDEF

    def get_sdn(self,y,m,d):
        """Converts a French Republican Calendar date to an SDN number"""
        if (y < 1 or y > 14 or m < 1 or m > 13 or d < 1 or d > 30):
            return 0
        return (y*FrenchRepublic.DAYS_PER_4_YEARS)/4 + \
               (m-1)*FrenchRepublic.DAYS_PER_MONTH + \
               d + FrenchRepublic.SDN_OFFSET

    def get_ymd(self,sdn):
        """Converts an SDN number to a French Republican Calendar date"""
        if (sdn < FrenchRepublic.FIRST_VALID or sdn > FrenchRepublic.LAST_VALID) :
            return (0,0,0)
        temp = (sdn-FrenchRepublic.SDN_OFFSET)*4 - 1
        year = temp/FrenchRepublic.DAYS_PER_4_YEARS
        dayOfYear = (temp%FrenchRepublic.DAYS_PER_4_YEARS)/4
        month = (dayOfYear/FrenchRepublic.DAYS_PER_MONTH)+1
        day = (dayOfYear%FrenchRepublic.DAYS_PER_MONTH)+1
        return (year,month,day)

#-------------------------------------------------------------------------
#
# Gregorian
#
#-------------------------------------------------------------------------
class Gregorian(Calendar):
    """Gregorian Calendar"""

    SDN_OFFSET         = 32045
    DAYS_PER_5_MONTHS  = 153
    DAYS_PER_4_YEARS   = 1461
    DAYS_PER_400_YEARS = 146097

    NAME = "Gregorian"
    TNAME = _("Gregorian")

    def quote_display(self,year,month,day,mode):
        return self.display(year,month,day,mode)

    def mlen(self):
        return 3

    def get_ymd(self,sdn):
        """Converts an SDN number to a gregorial date"""
        if sdn <= 0:
            return (0,0,0)

        temp = (Gregorian.SDN_OFFSET + sdn) * 4 - 1

        # Calculate the century (year/100)
        century = temp / Gregorian.DAYS_PER_400_YEARS

        # Calculate the year and day of year (1 <= dayOfYear <= 366)

        temp = ((temp % Gregorian.DAYS_PER_400_YEARS) / 4) * 4 + 3
        year = (century * 100) + (temp / Gregorian.DAYS_PER_4_YEARS)
        dayOfYear = (temp % Gregorian.DAYS_PER_4_YEARS) / 4 + 1
        
        # Calculate the month and day of month
        temp = dayOfYear * 5 - 3
        month = temp / Gregorian.DAYS_PER_5_MONTHS
        day = (temp % Gregorian.DAYS_PER_5_MONTHS) / 5 + 1
        
        # Convert to the normal beginning of the year
        if month < 10 :
            month = month + 3
        else:
            year = year + 1
            month = month - 9
            
        # Adjust to the B.C./A.D. type numbering

        year = year - 4800
        if year <= 0:
            year = year - 1

        return (year,month,day)

    def get_sdn(self,iyear,imonth,iday):
        """Converts a gregorian date to an SDN number"""
        # check for invalid dates 
        if iyear==0 or iyear<-4714 or imonth<=0 or imonth>12 or iday<=0 or iday>31:
            return 0

        # check for dates before SDN 1 (Nov 25, 4714 B.C.)
        if iyear == -4714:
            if imonth < 11 or imonth == 11 and iday < 25:
                return 0

        if iyear < 0:
            year = iyear + 4801
        else:
            year = iyear + 4800

        # Adjust the start of the year

        if imonth > 2:
            month = imonth - 3
        else:
            month = imonth + 9
            year = year - 1

        return( ((year / 100) * Gregorian.DAYS_PER_400_YEARS) / 4
                + ((year % 100) * Gregorian.DAYS_PER_4_YEARS) / 4
                + (month * Gregorian.DAYS_PER_5_MONTHS + 2) / 5
                + iday
                - Gregorian.SDN_OFFSET );

#-------------------------------------------------------------------------
#
# Julian
#
#-------------------------------------------------------------------------
class Julian(Calendar):
    """Julian calendar"""

    SDN_OFFSET        = 32083
    DAYS_PER_5_MONTHS = 153
    DAYS_PER_4_YEARS  = 1461

    NAME = "Julian"
    TNAME = _("Julian")

    def quote_display(self,year,month,day,mode):
        return "%s (%s)" % (self.display(year,month,day,mode),Julian.NAME)

    def mlen(self):
        return 3

    def get_ymd(self,sdn):
        """Converts an SDN number to a Julian date"""
        if sdn <= 0 :
            return (0,0,0)

        temp = (sdn + Julian.SDN_OFFSET) * 4 - 1

        # Calculate the year and day of year (1 <= dayOfYear <= 366)
        year = temp / Julian.DAYS_PER_4_YEARS
        dayOfYear = (temp % Julian.DAYS_PER_4_YEARS) / 4 + 1

        # Calculate the month and day of month
        temp = dayOfYear * 5 - 3;
        month = temp / Julian.DAYS_PER_5_MONTHS;
        day = (temp % Julian.DAYS_PER_5_MONTHS) / 5 + 1;
        
        # Convert to the normal beginning of the year
        if month < 10:
            month = month + 3
        else:
            year = year + 1
            month = month - 9

        # Adjust to the B.C./A.D. type numbering
        year = year - 4800
        if year <= 0:
            year = year - 1

        return (year,month,day)

    def get_sdn(self,iyear,imonth,iday):
        """Converts a Julian calendar date to an SDN number"""

        # check for invalid dates
        if iyear==0 or iyear<-4713 or imonth<=0 or imonth>12 or iday<=0 or iday>31:
            return 0

        # check for dates before SDN 1 (Jan 2, 4713 B.C.)
        if iyear == -4713:
            if imonth == 1 and iday == 1:
                return 0

        # Make year always a positive number
        if iyear < 0:
            year = iyear + 4801
        else:
            year = iyear + 4800

        # Adjust the start of the year
        if imonth > 2:
            month = imonth - 3
        else:
            month = imonth + 9
            year = year - 1

        return (year*Julian.DAYS_PER_4_YEARS)/4 + \
               (month*Julian.DAYS_PER_5_MONTHS+2)/5 + \
               iday - Julian.SDN_OFFSET

#-------------------------------------------------------------------------
#
# Islamic
#
#-------------------------------------------------------------------------
class Islamic(Calendar):
    """Islamic calendar"""

    EPOCH = 1948439.5

    MONTHS = [
        "Muharram",     "Safar",          "Rabi`al-Awwal", "Rabi`ath-Thani",
        "Jumada l-Ula", "Jumada t-Tania", "Rajab",         "Sha`ban",
        "Ramadan",      "Shawwal",        "Dhu l-Qa`da",   "Dhu l-Hijja"
        ]

    M2NUM = {
        "muharram" : 1,       "safar" : 2,         "rabi`al-awwal" : 3,
        "rabi`ath-thani" : 4, "jumada l-ula" : 5 , "jumada t-tania" : 6,
        "rajab" : 7,          "sha`ban" : 8,       "ramadan" : 9,
        "shawwal" : 10,       "dhu l-qa`da" : 11,  "dhu l-hijja" : 12
        }

    NAME = "Islamic"
    TNAME = _("Islamic")

    def quote_display(self,year,month,day,mode):
        return "%s (%s)" % (self.display(year,month,day,mode),Islamic.NAME)

    def set_month_string(self,text):
        try:
            return Islamic.M2NUM[unicode(text.lower())]
        except KeyError:
            return UNDEF

    def month(self,val):
        try:
            return Islamic.MONTHS[val-1]
        except:
            return "Illegal Month"

    def get_sdn(self,year, month, day):
        v1 = math.ceil(29.5 * (month - 1))
        v2 = (year - 1) * 354
        v3 = math.floor((3 + (11 *year)) / 30)

        return int(math.ceil((day + v1 + v2 + v3 + Islamic.EPOCH) - 1))

    def get_ymd(self,sdn):
        sdn = math.floor(sdn) + 0.5
        year = int(math.floor(((30*(sdn-Islamic.EPOCH))+10646)/10631))
        month = int(min(12, math.ceil((sdn-(29+self.get_sdn(year,1,1)))/29.5) + 1))
        day = int((sdn - self.get_sdn(year,month,1)) + 1)
        return (year,month,day)

_FMT_FUNC = [
    Calendar.format_mon_dd_year,
    Calendar.format_MON_dd_year,
    Calendar.format_dd_MON_year,
    Calendar.format4,
    Calendar.format5,
    Calendar.format6,
    Calendar.format7,
    Calendar.format9,
    Calendar.format_dd_dot_MON_year,
    Calendar.format11,
    Calendar.format12,
    Calendar.format13,
    ]

#-------------------------------------------------------------------------
#
# Calendar registration
#
#-------------------------------------------------------------------------

_calendars = {}

def register( class_obj ):
    _calendars[class_obj.NAME] = class_obj

def find_calendar(name):
    try:
        return _calendars[name]
    except:
        return None

def calendar_names():
    list = []
    for n in _calendars.values():
        list.append(n)
    list.sort()
    return list

register(Gregorian)
register(FrenchRepublic)
register(Julian)
register(Persian)
register(Hebrew)
register(Islamic)


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
Gregorian calendar module for GRAMPS. 

The original algorithms for this module came from Scott E. Lee's
C implementation. The original C source can be found at Scott's
web site at http://www.scottlee.com
"""

__author__ = "Donald N. Allingham"
__version__ = "$Revision$"

#-------------------------------------------------------------------------
#
# Gramps Modules
#
#-------------------------------------------------------------------------
import Calendar
from intl import gettext as _

#-------------------------------------------------------------------------
#
# Hebrew calendar
#
#-------------------------------------------------------------------------
class Hebrew(Calendar.Calendar):
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
            return Calendar.UNDEF

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

Calendar.register(Hebrew)

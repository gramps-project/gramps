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

_FR_SDN_OFFSET         = 2375474
_FR_DAYS_PER_4_YEARS   = 1461
_FR_DAYS_PER_MONTH     = 30
_FR_FIRST_VALID        = 2375840
_FR_LAST_VALID         = 2380952
_GR_SDN_OFFSET         = 32045
_GR_DAYS_PER_5_MONTHS  = 153
_GR_DAYS_PER_4_YEARS   = 1461
_GR_DAYS_PER_400_YEARS = 146097
_J_SDN_OFFSET          = 32083
_J_DAYS_PER_5_MONTHS   = 153
_J_DAYS_PER_4_YEARS    = 1461

_HALAKIM_PER_HOUR = 1080
_HALAKIM_PER_DAY  = 25920
_HALAKIM_PER_LUNAR_CYCLE = ((29 * _HALAKIM_PER_DAY) + 13753)
_HALAKIM_PER_METONIC_CYCLE = (_HALAKIM_PER_LUNAR_CYCLE * (12 * 19 + 7))

_H_SDN_OFFSET = 347997
_NEW_MOON_OF_CREATION = 31524

_SUNDAY   = 0
_MONDAY   = 1
_TUESDAY  = 2
_WEDNESDAY= 3
#_THURSDAY = 4
_FRIDAY   = 5
#_SATURDAY = 6

_NOON = (18 * _HALAKIM_PER_HOUR)
_AM3_11_20 = ((9 * _HALAKIM_PER_HOUR) + 204)
_AM9_32_43 = ((15 * _HALAKIM_PER_HOUR) + 589)

#-------------------------------------------------------------------------
#
# Conversion tables
#
#-------------------------------------------------------------------------
monthsPerYear = [
    12, 12, 13, 12, 12, 13, 12, 13, 12,
    12, 13, 12, 12, 13, 12, 12, 13, 12, 13
]

yearOffset = [
    0, 12, 24, 37, 49, 61, 74, 86, 99, 111, 123,
    136, 148, 160, 173, 185, 197, 210, 222
]

#-------------------------------------------------------------------------
#
# Tasks
#
#-------------------------------------------------------------------------

def french_to_sdn(y,m,d):
    """Converts a French Republican Calendar date to an SDN number"""
    if (y < 1 or y > 14 or m < 1 or m > 13 or d < 1 or d > 30):
	return 0
    return (y*_FR_DAYS_PER_4_YEARS)/4+(m-1)*_FR_DAYS_PER_MONTH+d+_FR_SDN_OFFSET

def sdn_to_french(sdn):
    """Converts an SDN number to a French Republican Calendar date"""
    if (sdn < _FR_FIRST_VALID or sdn > _FR_LAST_VALID) :
	return (0,0,0)
    temp = (sdn-_FR_SDN_OFFSET)*4 - 1
    year = temp/_FR_DAYS_PER_4_YEARS
    dayOfYear = (temp%_FR_DAYS_PER_4_YEARS)/4
    month = (dayOfYear/_FR_DAYS_PER_MONTH)+1
    day = (dayOfYear%_FR_DAYS_PER_MONTH)+1
    return (year,month,day)


def sdn_to_gregorian(sdn):
    """Converts an SDN number to a gregorial date"""
    if sdn <= 0:
        return (0,0,0)

    temp = (sdn + _GR_SDN_OFFSET) * 4 - 1

    # Calculate the century (year/100)
    century = temp / _GR_DAYS_PER_400_YEARS

    # Calculate the year and day of year (1 <= dayOfYear <= 366)

    temp = ((temp % _GR_DAYS_PER_400_YEARS) / 4) * 4 + 3
    year = (century * 100) + (temp / _GR_DAYS_PER_4_YEARS)
    dayOfYear = (temp % _GR_DAYS_PER_4_YEARS) / 4 + 1

    # Calculate the month and day of month
    temp = dayOfYear * 5 - 3
    month = temp / _GR_DAYS_PER_5_MONTHS
    day = (temp % _GR_DAYS_PER_5_MONTHS) / 5 + 1

    # Convert to the normal beginning of the year
    if month < 10 :
	month = month + 3
    else:
	year = year + 1
	month = month + 9

    # Adjust to the B.C./A.D. type numbering
    year = year - 4800
    if year <= 0:
        year = year - 1

    return (year,month,day)

def gregorian_to_sdn(iyear,imonth,iday):
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

    return( ((year / 100) * _GR_DAYS_PER_400_YEARS) / 4
	    + ((year % 100) * _GR_DAYS_PER_4_YEARS) / 4
	    + (month * _GR_DAYS_PER_5_MONTHS + 2) / 5
	    + iday
	    - _GR_SDN_OFFSET );


def sdn_to_julian(sdn):
    """Converts an SDN number to a Julian date"""
    if sdn <= 0 :
        return (0,0,0)

    temp = (sdn + _J_SDN_OFFSET) * 4 - 1

    # Calculate the year and day of year (1 <= dayOfYear <= 366)
    year = temp / _J_DAYS_PER_4_YEARS
    dayOfYear = (temp % _J_DAYS_PER_4_YEARS) / 4 + 1

    # Calculate the month and day of month
    temp = dayOfYear * 5 - 3;
    month = temp / _J_DAYS_PER_5_MONTHS;
    day = (temp % _J_DAYS_PER_5_MONTHS) / 5 + 1;

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

def julian_to_sdn(iyear,imonth,iday):
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

    return (year*_J_DAYS_PER_4_YEARS)/4 + (month*_J_DAYS_PER_5_MONTHS+2)/5 + iday - _J_SDN_OFFSET

def Tishri1(metonicYear, moladDay, moladHalakim):

    tishri1 = moladDay
    dow = tishri1 % 7
    leapYear = metonicYear == 2 or metonicYear == 5 or metonicYear == 7 or \
               metonicYear == 10 or metonicYear == 13 or metonicYear == 16 or \
               metonicYear == 18
    lastWasLeapYear = metonicYear == 3 or metonicYear == 6 or metonicYear == 8 or \
                      metonicYear == 11 or metonicYear == 14 or metonicYear == 17 or \
                      metonicYear == 0

    # Apply rules 2, 3 and 4.
    if ((moladHalakim >= _NOON) or
	((not leapYear) and dow == _TUESDAY and moladHalakim >= _AM3_11_20) or
        (lastWasLeapYear and dow == _MONDAY and moladHalakim >= _AM9_32_43)) :
	tishri1 = tishri1 + 1
	dow = dow + 1
        if dow == 7:
	    dow = 0

    # Apply rule 1 after the others because it can cause an additional
    # delay of one day

    if dow == _WEDNESDAY or dow == _FRIDAY or dow == _SUNDAY:
	tishri1 = tishri1 + 1

    return tishri1


def MoladOfMetonicCycle(metonicCycle):

    # Start with the time of the first molad after creation.

    r1 = _NEW_MOON_OF_CREATION;

    # Calculate metonicCycle * HALAKIM_PER_METONIC_CYCLE.  The upper 32
    # bits of the result will be in r2 and the lower 16 bits will be
    # in r1.

    r1 = r1 + (metonicCycle * (_HALAKIM_PER_METONIC_CYCLE & 0xFFFF))
    r2 = r1 >> 16
    r2 = r2 + (metonicCycle * ((_HALAKIM_PER_METONIC_CYCLE >> 16) & 0xFFFF))

    # Calculate r2r1 / HALAKIM_PER_DAY.  The remainder will be in r1, the
    # upper 16 bits of the quotient will be in d2 and the lower 16 bits
    # will be in d1.
    
    d2 = r2 / _HALAKIM_PER_DAY
    r2 = r2 - (d2 * _HALAKIM_PER_DAY)
    r1 = (r2 << 16) | (r1 & 0xFFFF)
    d1 = r1 / _HALAKIM_PER_DAY
    r1 = r1 - ( d1 * _HALAKIM_PER_DAY)

    MoladDay = (d2 << 16) | d1
    MoladHalakim = r1

    return (MoladDay,MoladHalakim)

def FindTishriMolad(inputDay):

    # Estimate the metonic cycle number.  Note that this may be an under
    # estimate because there are 6939.6896 days in a metonic cycle not
    # 6940, but it will never be an over estimate.  The loop below will
    # correct for any error in this estimate. */

    metonicCycle = (inputDay + 310) / 6940

    # Calculate the time of the starting molad for this metonic cycle. */

    (moladDay, moladHalakim) = MoladOfMetonicCycle(metonicCycle)

    # If the above was an under estimate, increment the cycle number until
    # the correct one is found.  For modern dates this loop is about 98.6%
    # likely to not execute, even once, because the above estimate is
    # really quite close.
    
    while moladDay < (inputDay - 6940 + 310): 
	metonicCycle = metonicCycle + 1
	moladHalakim = moladHalakim + _HALAKIM_PER_METONIC_CYCLE
	moladDay = moladDay + ( moladHalakim / _HALAKIM_PER_DAY)
	moladHalakim = moladHalakim % _HALAKIM_PER_DAY

    # Find the molad of Tishri closest to this date.

    for metonicYear in range(0,18):
        if moladDay > inputDay - 74:
	    break

	moladHalakim = moladHalakim + \
                       (_HALAKIM_PER_LUNAR_CYCLE * monthsPerYear[metonicYear])
	moladDay =  moladDay + (moladHalakim / _HALAKIM_PER_DAY)
	moladHalakim = moladHalakim % _HALAKIM_PER_DAY
    else:
        metonicYear = metonicYear + 1
    return (metonicCycle, metonicYear, moladDay, moladHalakim)

def FindStartOfYear(year):

    pMetonicCycle = (year - 1) / 19;
    pMetonicYear = (year - 1) % 19;
    (pMoladDay, pMoladHalakim) = MoladOfMetonicCycle(pMetonicCycle)

    pMoladHalakim = pMoladHalakim + (_HALAKIM_PER_LUNAR_CYCLE * yearOffset[pMetonicYear])
    pMoladDay = pMoladDay + (pMoladHalakim / _HALAKIM_PER_DAY)
    pMoladHalakim = pMoladHalakim % _HALAKIM_PER_DAY

    pTishri1 = Tishri1(pMetonicYear, pMoladDay, pMoladHalakim);

    return (pMetonicCycle, pMetonicYear, pMoladDay, pMoladHalakim, pTishri1)

def sdn_to_jewish(sdn):
    """Converts an SDN number to a Julian calendar date"""

    if sdn <= _H_SDN_OFFSET :
        return (0,0,0)

    inputDay = sdn - _H_SDN_OFFSET

    (metonicCycle, metonicYear, day, halakim) = FindTishriMolad(inputDay)
    tishri1 = Tishri1(metonicYear, day, halakim);

    if inputDay >= tishri1:
	# It found Tishri 1 at the start of the year
        
	pYear = (metonicCycle * 19) + metonicYear + 1
        if inputDay < tishri1 + 59:
            if inputDay < tishri1 + 30:
		pMonth = 1
		pDay = inputDay - tishri1 + 1
            else:
		pMonth = 2
		pDay = inputDay - tishri1 - 29
	    return (pYear, pMonth, pDay)

	# We need the length of the year to figure this out, so find
        # Tishri 1 of the next year. */

	halakim = halakim + (_HALAKIM_PER_LUNAR_CYCLE * monthsPerYear[metonicYear])
	day = day + (halakim / _HALAKIM_PER_DAY)
	halakim = halakim % _HALAKIM_PER_DAY;
	tishri1After = Tishri1((metonicYear + 1) % 19, day, halakim);
    else:
	# It found Tishri 1 at the end of the year.

	pYear = metonicCycle * 19 + metonicYear
        if inputDay >= tishri1 - 177:
	    # It is one of the last 6 months of the year.
            if inputDay > tishri1 - 30:
		pMonth = 13
		pDay = inputDay - tishri1 + 30
            elif inputDay > tishri1 - 60:
		pMonth = 12
		pDay = inputDay - tishri1 + 60
            elif inputDay > tishri1 - 89:
		pMonth = 11
		pDay = inputDay - tishri1 + 89
            elif inputDay > tishri1 - 119:
		pMonth = 10
		pDay = inputDay - tishri1 + 119
            elif inputDay > tishri1 - 148:
		pMonth = 9
		pDay = inputDay - tishri1 + 148
            else:
		pMonth = 8
		pDay = inputDay - tishri1 + 178
	    return (pYear,pMonth,pDay)
        else:
            if monthsPerYear[(pYear - 1) % 19] == 13:
		pMonth = 7
		pDay = inputDay - tishri1 + 207
                if pDay > 0:
                    return (pYear,pMonth,pDay)
		pMonth = pMonth - 1
		pDay = pDay + 30
                if pDay > 0:
                    return (pYear,pMonth,pDay)
		pMonth = pMonth - 1
		pDay = pDay + 30
            else:
		pMonth = 6
		pDay = inputDay - tishri1 + 207
                if pDay > 0:
                    return (pYear,pMonth,pDay)
		pMonth = pMonth - 1
		pDay = pDay + 30

            if pDay > 0:
                return (pYear,pMonth,pDay)
	    pMonth = pMonth - 1
            pDay = pDay + 29
            if pDay > 0:
                return (pYear,pMonth,pDay)

	    # We need the length of the year to figure this out, so find
	    # Tishri 1 of this year. */
	    tishri1After = tishri1;
	    (metonicCycle,metonicYear,day,halakim) = FindTishriMolad(day-365)
	    tishri1 = Tishri1(metonicYear, day, halakim)

    yearLength = tishri1After - tishri1;
    day = inputDay - tishri1 - 29;
    if yearLength == 355 or yearLength == 385 :
	# Heshvan has 30 days 
        if day <= 30:
	    pMonth = 2
	    pDay = day
	    return (pYear,pMonth,pDay)
	day = day - 30
    else:
	# Heshvan has 29 days
        if day <= 29:
	    pMonth = 2
	    pDay = day
	    return (pYear,pMonth,pDay)

	day = day - 29

    # It has to be Kislev
    return (pYear,3,day)


def jewish_to_sdn(year, month, day):
    """Converts a Jewish calendar date to an SDN number"""
    if year <= 0 or day <= 0 or day > 30 : 
	return 0

    if month == 1 or month == 2:
	# It is Tishri or Heshvan - don't need the year length. 
	(metonicCycle,metonicYear,moladDay,moladHalakim,tishri1) = FindStartOfYear(year)
        if month == 1:
	    sdn = tishri1 + day - 1
        else:
	    sdn = tishri1 + day + 29
    elif month == 3:
	# It is Kislev - must find the year length.

	# Find the start of the year. 
	(metonicCycle,metonicYear,moladDay,moladHalakim,tishri1) = FindStartOfYear(year)

	# Find the end of the year.
	moladHalakim = moladHalakim + (_HALAKIM_PER_LUNAR_CYCLE*monthsPerYear[metonicYear])
	moladDay = moladDay + (moladHalakim / _HALAKIM_PER_DAY)
	moladHalakim = moladHalakim % _HALAKIM_PER_DAY
	tishri1After = Tishri1((metonicYear + 1) % 19, moladDay, moladHalakim)

	yearLength = tishri1After - tishri1

        if yearLength == 355 or yearLength == 385:
	    sdn = tishri1 + day + 59
        else:
	    sdn = tishri1 + day + 58
    elif month == 4 or month == 5 or month == 6:
	# It is Tevet, Shevat or Adar I - don't need the year length

        (metonicCycle,metonicYear,moladDay,moladHalakim,tishri1After) = FindStartOfYear(year+1)

        if monthsPerYear[(year - 1) % 19] == 12:
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
	(metonicCycle,metonicYear,moladDay,moladHalakim,tishri1After) = FindStartOfYear(year+1)

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
    return sdn + _H_SDN_OFFSET

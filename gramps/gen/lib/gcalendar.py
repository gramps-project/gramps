#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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
Provide calendar to sdn (serial date number) conversion.
"""

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import math

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
_GRG_SDN_OFFSET = 32045
_GRG_DAYS_PER_5_MONTHS = 153
_GRG_DAYS_PER_4_YEARS = 1461
_GRG_DAYS_PER_400_YEARS = 146097

_JLN_SDN_OFFSET = 32083
_JLN_DAYS_PER_5_MONTHS = 153
_JLN_DAYS_PER_4_YEARS = 1461

_HBR_HALAKIM_PER_HOUR = 1080
_HBR_HALAKIM_PER_DAY = 25920
_HBR_HALAKIM_PER_LUNAR_CYCLE = 29 * _HBR_HALAKIM_PER_DAY + 13753
_HBR_HALAKIM_PER_METONIC_CYCLE = _HBR_HALAKIM_PER_LUNAR_CYCLE * (12 * 19 + 7)
_HBR_SDN_OFFSET = 347997
_HBR_NEW_MOON_OF_CREATION = 31524
_HBR_NOON = 18 * _HBR_HALAKIM_PER_HOUR
_HBR_AM3_11_20 = (9 * _HBR_HALAKIM_PER_HOUR) + 204
_HBR_AM9_32_43 = (15 * _HBR_HALAKIM_PER_HOUR) + 589

_HBR_SUNDAY = 0
_HBR_MONDAY = 1
_HBR_TUESDAY = 2
_HBR_WEDNESDAY = 3
_HBR_FRIDAY = 5

_HBR_MONTHS_PER_YEAR = [
    12, 12, 13, 12, 12, 13, 12, 13, 12, 12,
    13, 12, 12, 13, 12, 12, 13, 12, 13
    ]

_HBR_YEAR_OFFSET = [
    0, 12, 24, 37, 49, 61, 74, 86, 99, 111, 123,
    136, 148, 160, 173, 185, 197, 210, 222
    ]

_FR_SDN_OFFSET = 2375474
_FR_DAYS_PER_4_YEARS = 1461
_FR_DAYS_PER_MONTH = 30
_PRS_EPOCH = 1948320.5
_ISM_EPOCH = 1948439.5

def _tishri1(metonic_year, molad_day, molad_halakim):

    tishri1 = molad_day
    dow = tishri1 % 7
    leap_year = metonic_year in [2, 5, 7, 10, 13, 16, 18]
    last_was_leap_year = metonic_year in [3, 6, 8, 11, 14, 17, 0]

    # Apply rules 2, 3 and 4.
    if ((molad_halakim >= _HBR_NOON) or
            ((not leap_year) and dow == _HBR_TUESDAY and
             molad_halakim >= _HBR_AM3_11_20) or
            (last_was_leap_year and dow == _HBR_MONDAY
             and molad_halakim >= _HBR_AM9_32_43)):
        tishri1 += 1
        dow += 1
        if dow == 7:
            dow = 0

    # Apply rule 1 after the others because it can cause an additional
    # delay of one day
    if dow == _HBR_WEDNESDAY or dow == _HBR_FRIDAY or dow == _HBR_SUNDAY:
        tishri1 += 1

    return tishri1

def _tishri_molad(input_day):
    """
    Estimate the metonic cycle number.

    Note that this may be an under estimate because there are 6939.6896 days
    in a metonic cycle not 6940, but it will never be an over estimate. The
    loop below will correct for any error in this estimate.
    """

    metonic_cycle = (input_day + 310) // 6940

    # Calculate the time of the starting molad for this metonic cycle.

    (molad_day, molad_halakim) = _molad_of_metonic_cycle(metonic_cycle)

    # If the above was an under estimate, increment the cycle number until
    # the correct one is found.  For modern dates this loop is about 98.6%
    # likely to not execute, even once, because the above estimate is
    # really quite close.

    while molad_day < (input_day - 6940 + 310):
        metonic_cycle += 1
        molad_halakim += _HBR_HALAKIM_PER_METONIC_CYCLE
        molad_day += molad_halakim // _HBR_HALAKIM_PER_DAY
        molad_halakim = molad_halakim % _HBR_HALAKIM_PER_DAY

    # Find the molad of Tishri closest to this date.

    for metonic_year in range(0, 20):
        if molad_day > input_day - 74:
            break

        molad_halakim += (_HBR_HALAKIM_PER_LUNAR_CYCLE
                          * _HBR_MONTHS_PER_YEAR[metonic_year])
        molad_day += molad_halakim // _HBR_HALAKIM_PER_DAY
        molad_halakim = molad_halakim % _HBR_HALAKIM_PER_DAY

    return (metonic_cycle, metonic_year, molad_day, molad_halakim)

def _molad_of_metonic_cycle(metonic_cycle):
    """
    Start with the time of the first molad after creation.
    """

    r1 = _HBR_NEW_MOON_OF_CREATION

    # Calculate metonic_cycle * HALAKIM_PER_METONIC_CYCLE.  The upper 32
    # bits of the result will be in r2 and the lower 16 bits will be
    # in r1.

    r1 = r1 + (metonic_cycle * (_HBR_HALAKIM_PER_METONIC_CYCLE & 0xFFFF))
    r2 = r1 >> 16
    r2 = r2 + (metonic_cycle * ((_HBR_HALAKIM_PER_METONIC_CYCLE >> 16)&0xFFFF))

    # Calculate r2r1 / HALAKIM_PER_DAY.  The remainder will be in r1, the
    # upper 16 bits of the quotient will be in d2 and the lower 16 bits
    # will be in d1.

    d2 = r2 // _HBR_HALAKIM_PER_DAY
    r2 -= d2 * _HBR_HALAKIM_PER_DAY
    r1 = (r2 << 16) | (r1 & 0xFFFF)
    d1 = r1 // _HBR_HALAKIM_PER_DAY
    r1 -= d1 * _HBR_HALAKIM_PER_DAY

    molad_day = (d2 << 16) | d1
    molad_halakim = r1

    return (molad_day, molad_halakim)

def _start_of_year(year):
    """
    Calculate the start of the year.
    """
    metonic_cycle = (year - 1) // 19
    metonic_year = (year - 1) % 19
    (molad_day, molad_halakim) = _molad_of_metonic_cycle(metonic_cycle)

    molad_halakim = molad_halakim + (_HBR_HALAKIM_PER_LUNAR_CYCLE
                                     * _HBR_YEAR_OFFSET[metonic_year])
    molad_day = molad_day + (molad_halakim // _HBR_HALAKIM_PER_DAY)
    molad_halakim = molad_halakim % _HBR_HALAKIM_PER_DAY

    ptishri1 = _tishri1(metonic_year, molad_day, molad_halakim)

    return (metonic_cycle, metonic_year, molad_day, molad_halakim, ptishri1)

def hebrew_sdn(year, month, day):
    """Convert a Jewish calendar date to an SDN number."""

    if month == 1 or month == 2:
        # It is Tishri or Heshvan - don't need the year length.
        (metonic_cycle, metonic_year,
         molad_day, molad_halakim, tishri1) = _start_of_year(year)
        if month == 1:
            sdn = tishri1 + day - 1
        else:
            sdn = tishri1 + day + 29
    elif month == 3:
        # It is Kislev - must find the year length.

        # Find the start of the year.
        (metonic_cycle, metonic_year,
         molad_day, molad_halakim, tishri1) = _start_of_year(year)

        # Find the end of the year.
        molad_halakim = molad_halakim + (_HBR_HALAKIM_PER_LUNAR_CYCLE
                                         *_HBR_MONTHS_PER_YEAR[metonic_year])
        molad_day = molad_day + (molad_halakim // _HBR_HALAKIM_PER_DAY)
        molad_halakim = molad_halakim % _HBR_HALAKIM_PER_DAY
        tishri1_after = _tishri1((metonic_year + 1)
                                 % 19, molad_day, molad_halakim)

        year_length = tishri1_after - tishri1

        if year_length == 355 or year_length == 385:
            sdn = tishri1 + day + 59
        else:
            sdn = tishri1 + day + 58
    elif month == 4 or month == 5 or month == 6:
        # It is Tevet, Shevat or Adar I - don't need the year length

        (metonic_cycle, metonic_year,
         molad_day, molad_halakim, tishri1_after) = _start_of_year(year+1)

        if _HBR_MONTHS_PER_YEAR[(year - 1) % 19] == 12:
            length_of_adar_1and2 = 29
        else:
            length_of_adar_1and2 = 59

        if month == 4:
            sdn = tishri1_after + day - length_of_adar_1and2 - 237
        elif month == 5:
            sdn = tishri1_after + day - length_of_adar_1and2 - 208
        else:
            sdn = tishri1_after + day - length_of_adar_1and2 - 178
    else:
        # It is Adar II or later - don't need the year length.
        (metonic_cycle, metonic_year,
         molad_day, molad_halakim, tishri1_after) = _start_of_year(year+1)

        if month == 7:
            sdn = tishri1_after + day - 207
        elif month == 8:
            sdn = tishri1_after + day - 178
        elif month == 9:
            sdn = tishri1_after + day - 148
        elif month == 10:
            sdn = tishri1_after + day - 119
        elif month == 11:
            sdn = tishri1_after + day - 89
        elif month == 12:
            sdn = tishri1_after + day - 60
        elif month == 13:
            sdn = tishri1_after + day - 30
        else:
            return 0
    return sdn + _HBR_SDN_OFFSET

def hebrew_ymd(sdn):
    """Convert an SDN number to a Hebrew calendar date."""

    input_day = sdn - _HBR_SDN_OFFSET
    # TODO if input_day <= 0, the result is a date invalid in Hebrew calendar!

    (metonic_cycle, metonic_year, day1, halakim) = _tishri_molad(input_day)
    tishri1 = _tishri1(metonic_year, day1, halakim)

    if input_day >= tishri1:
        # It found Tishri 1 at the start of the year

        year = (metonic_cycle * 19) + metonic_year + 1
        if input_day < tishri1 + 59:
            if input_day < tishri1 + 30:
                month = 1
                day = input_day - tishri1 + 1
            else:
                month = 2
                day = input_day - tishri1 - 29
            return (year, month, day)

        # We need the length of the year to figure this out, so find
        # Tishri 1 of the next year.

        halakim += (_HBR_HALAKIM_PER_LUNAR_CYCLE
                    * _HBR_MONTHS_PER_YEAR[metonic_year])
        day1 += halakim // _HBR_HALAKIM_PER_DAY
        halakim = halakim % _HBR_HALAKIM_PER_DAY
        tishri1_after = _tishri1((metonic_year + 1) % 19, day1, halakim)
    else:
        # It found Tishri 1 at the end of the year.

        year = metonic_cycle * 19 + metonic_year
        if input_day >= tishri1 - 177:
            # It is one of the last 6 months of the year.
            if input_day > tishri1 - 30:
                month = 13
                day = input_day - tishri1 + 30
            elif input_day > tishri1 - 60:
                month = 12
                day = input_day - tishri1 + 60
            elif input_day > tishri1 - 89:
                month = 11
                day = input_day - tishri1 + 89
            elif input_day > tishri1 - 119:
                month = 10
                day = input_day - tishri1 + 119
            elif input_day > tishri1 - 148:
                month = 9
                day = input_day - tishri1 + 148
            else:
                month = 8
                day = input_day - tishri1 + 178
            return (year, month, day)
        else:
            if _HBR_MONTHS_PER_YEAR[(year - 1) % 19] == 13:
                month = 7
                day = input_day - tishri1 + 207
                if day > 0:
                    return (year, month, day)
                month -= 1
                day += 30
                if day > 0:
                    return (year, month, day)
                month -= 1
                day += 30
            else:
                month = 6
                day = input_day - tishri1 + 207
                if day > 0:
                    return (year, month, day)
                month -= 1
                day += 30

            if day > 0:
                return (year, month, day)
            month -= 1
            day += 29
            if day > 0:
                return (year, month, day)

            # We need the length of the year to figure this out, so find
            # Tishri 1 of this year
            tishri1_after = tishri1
            (metonic_cycle, metonic_year, day1, halakim) = _tishri_molad(day1-365)
            tishri1 = _tishri1(metonic_year, day1, halakim)

    year_length = tishri1_after - tishri1
    day = input_day - tishri1 - 29
    if year_length == 355 or year_length == 385:
        # Heshvan has 30 days
        if day <= 30:
            month = 2
            return (year, month, day)
        day -= 30
    else:
        # Heshvan has 29 days
        if day <= 29:
            month = 2
            return (year, month, day)

        day -= 29

    # It has to be Kislev
    return (year, 3, day)

def julian_sdn(year, month, day):
    """Convert a Julian calendar date to an SDN number."""

    if year < 0:
        year += 4801
    else:
        year += 4800

    # Adjust the start of the year
    if month > 2:
        month -= 3
    else:
        month += 9
        year -= 1

    return (year * _JLN_DAYS_PER_4_YEARS) // 4 \
           + (month * _JLN_DAYS_PER_5_MONTHS + 2) // 5 \
           + day - _JLN_SDN_OFFSET

def julian_ymd(sdn):
    """Convert an SDN number to a Julian date."""
    temp = (sdn + _JLN_SDN_OFFSET) * 4 - 1

    # Calculate the year and day of year (1 <= day_of_year <= 366)
    year = temp // _JLN_DAYS_PER_4_YEARS
    day_of_year = (temp % _JLN_DAYS_PER_4_YEARS) // 4 + 1

    # Calculate the month and day of month
    temp = day_of_year * 5 - 3
    month = temp // _JLN_DAYS_PER_5_MONTHS
    day = (temp % _JLN_DAYS_PER_5_MONTHS) // 5 + 1

    # Convert to the normal beginning of the year
    if month < 10:
        month += 3
    else:
        year += 1
        month -= 9

    # Adjust to the B.C./A.D. type numbering
    year -= 4800
    if year <= 0:
        year -= 1

    return (year, month, day)

def gregorian_sdn(year, month, day):
    """Convert a gregorian date to an SDN number."""
    if year < 0:
        year += 4801
    else:
        year += 4800

    # Adjust the start of the year
    if month > 2:
        month -= 3
    else:
        month += 9
        year -= 1

    return(((year // 100) * _GRG_DAYS_PER_400_YEARS) // 4
           + ((year % 100) * _GRG_DAYS_PER_4_YEARS) // 4
           + (month * _GRG_DAYS_PER_5_MONTHS + 2) // 5
           + day
           - _GRG_SDN_OFFSET)

def gregorian_ymd(sdn):
    """Convert an SDN number to a gregorian date."""
    temp = (_GRG_SDN_OFFSET + sdn) * 4 - 1

    # Calculate the century (year/100)
    century = temp // _GRG_DAYS_PER_400_YEARS

    # Calculate the year and day of year (1 <= day_of_year <= 366)
    temp = ((temp % _GRG_DAYS_PER_400_YEARS) // 4) * 4 + 3
    year = (century * 100) + (temp // _GRG_DAYS_PER_4_YEARS)
    day_of_year = (temp % _GRG_DAYS_PER_4_YEARS) // 4 + 1

    # Calculate the month and day of month
    temp = day_of_year * 5 - 3
    month = temp // _GRG_DAYS_PER_5_MONTHS
    day = (temp % _GRG_DAYS_PER_5_MONTHS) // 5 + 1

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
    return (year, month, day)

def _check_republican_period(sdn, restrict_period):
    # French Republican calendar wasn't in use before 22.9.1792 or after 1.1.1806
    if restrict_period and (sdn < 2375840 or sdn > 2380688):
        raise ValueError("Outside of the French Republican period")

def french_sdn(year, month, day, restrict_period=False):
    """Convert a French Republican Calendar date to an SDN number."""
    sdn = (year*_FR_DAYS_PER_4_YEARS) // 4 + \
           (month-1)*_FR_DAYS_PER_MONTH + \
           day + _FR_SDN_OFFSET
    _check_republican_period(sdn, restrict_period)
    return sdn

def french_ymd(sdn, restrict_period=False):
    """Convert an SDN number to a French Republican Calendar date."""
    _check_republican_period(sdn, restrict_period)
    temp = (sdn-_FR_SDN_OFFSET)*4 - 1
    year = temp // _FR_DAYS_PER_4_YEARS
    day_of_year = (temp % _FR_DAYS_PER_4_YEARS) // 4
    month = (day_of_year // _FR_DAYS_PER_MONTH) + 1
    day = (day_of_year % _FR_DAYS_PER_MONTH) + 1
    return (year, month, day)

def persian_sdn(year, month, day):
    """Convert a Persian date to an SDN number."""
    if year >= 0:
        epbase = year - 474
    else:
        epbase = year - 473

    epyear = 474 + epbase % 2820

    if month <= 7:
        v1 = (month - 1) * 31
    else:
        v1 = ((month - 1) * 30) + 6
    v2 = ((epyear * 682) - 110) // 2816
    v3 = (epyear - 1) * 365 + day
    v4 = (epbase // 2820) * 1029983

    return int(math.ceil(v1 + v2 + v3 + v4 + _PRS_EPOCH - 1))

def persian_ymd(sdn):
    """Convert an SDN number to a Persian calendar date."""
    sdn = math.floor(sdn) + 0.5  #float

    depoch = sdn - 2121446       #float
    cycle = math.floor(depoch / 1029983) #int
    cyear = depoch % 1029983             #int
    if cyear == 1029982:
        ycycle = 2820
    else:
        aux1 = cyear // 366 #int
        aux2 = cyear % 366  #int
        ycycle = (((2134*aux1)+(2816*aux2)+2815) // 1028522) + aux1 + 1

    year = ycycle + (2820 * cycle) + 474
    if year <= 0:
        year = year - 1

    yday = sdn - persian_sdn(year, 1, 1) + 1   #float !
    if yday < 186:
        month = math.ceil(yday / 31)
    else:
        month = math.ceil((yday - 6) / 30)
    day = (sdn - persian_sdn(year, month, 1)) + 1
    return (int(year), int(month), int(day))

def islamic_sdn(year, month, day):
    """Convert an Islamic date to an SDN number."""
    v1 = math.ceil(29.5 * (month - 1))
    v2 = (year - 1) * 354
    v3 = math.floor((3 + (11 *year)) // 30)

    return int(math.ceil((day + v1 + v2 + v3 + _ISM_EPOCH) - 1))

def islamic_ymd(sdn):
    """Convert an SDN number to an Islamic calendar date."""
    sdn = math.floor(sdn) + 0.5
    year = int(math.floor(((30*(sdn-_ISM_EPOCH))+10646) / 10631))
    month = int(min(12, math.ceil((sdn-(29+islamic_sdn(year, 1, 1))) / 29.5) + 1))
    day = int((sdn - islamic_sdn(year, month, 1)) + 1)
    return (year, month, day)

def swedish_sdn(year, month, day):
    """Convert a Swedish date to an SDN number."""
    datum = (year, month, day)
    # Swedish Calendar
    if (1700, 3, 1) <= datum <= (1712, 2, 30):
        return julian_sdn(year, month, day) -1
    # Gregorian Calendar (1753-03-01)
    elif (1753, 3, 1) <= datum:
        return gregorian_sdn(year, month, day)
    else:
        return julian_sdn(year, month, day)

def swedish_ymd(sdn):
    """Convert an SDN number to a Swedish calendar date."""
    if sdn == 2346425:
        return (1712, 2, 30)
    # Swedish Calendar
    elif 2342042 <= sdn < 2346425:
        return julian_ymd(sdn+1)
    # Gregorian Calendar (1753-03-01)
    elif sdn >= 2361390:
        return gregorian_ymd(sdn)
    else:
        return julian_ymd(sdn)

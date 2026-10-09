#!/usr/bin/env python3
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Doug Blank
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
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
"""
Generate the Korean and Vietnamese lunar year tables for
gramps/gen/lib/lunartables.py (KOREAN_YEAR_INFOS, VIETNAMESE_YEAR_INFOS).

Korea's and Vietnam's lunar calendars follow China's rules, but are
computed for their own meridian: Korea UTC+9 (today), Vietnam UTC+7 (since
1968; China's UTC+8 before).  Where a new moon falls near midnight, a month
starts on a different day than in China, and leap months can move.  So each
gets its own table, in the encoding of lunartables.py, for the lunar years where
it has its own data; other years use the Chinese table.  Each table must
start and end on the same New Year's day as the Chinese table, which this
script checks, along with every day of the result against its source.

Sources:
  korean      KASI (Korea Astronomy and Space Science Institute) data for
              lunar years 1000-2049, via the korean_lunar_calendar package
              (MIT licence); Ho Ngoc Duc's computation at UTC+9 for 2050 on.
  vietnamese  The Chinese table before 1968-01-01; Ho Ngoc Duc's computation
              at UTC+7 from then on.

Ho Ngoc Duc's algorithm (https://www.informatik.uni-leipzig.de/~duc/amlich/)
is the one Vietnamese calendar software uses; it reproduces the Chinese
table (at UTC+8) and KASI's (at UTC+9) for 1900-2050 apart from a few new
moons within minutes of midnight.

Usage:
    python3 scripts/gen_lunar_variant_tables.py korean|vietnamese [FIRST [LAST]]
    (defaults: korean 1000 2199, vietnamese 1967 2199)

Requirements (korean):
    pip install korean_lunar_calendar
"""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
import sys
from math import floor, pi, sin

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.lib.gcalendar import (
    _CHN_BASE_YEAR,
    _CHN_YEAR_INFOS,
    _chn_iter_months,
    chinese_lunar_sdn,
    chinese_lunar_ymd,
    gregorian_sdn,
    gregorian_ymd,
)

KASI_LAST_YEAR = 2049  # KASI's lunar 2050 is cut off at Gregorian 2050-12-31
VIETNAM_UTC7_FROM = gregorian_sdn(1968, 1, 1)


# -------------------------------------------------------------------------
#
# Ho Ngoc Duc's lunar calendar computation, for a time zone (hours east of
# UTC).  Days are Julian day numbers (= SDN).
#
# -------------------------------------------------------------------------
def _new_moon(k):
    """Julian date of the k-th new moon after 1900-01-01."""
    T = k / 1236.85
    T2 = T * T
    T3 = T2 * T
    dr = pi / 180
    jd1 = 2415020.75933 + 29.53058868 * k + 0.0001178 * T2 - 0.000000155 * T3
    jd1 += 0.00033 * sin((166.56 + 132.87 * T - 0.009173 * T2) * dr)
    M = 359.2242 + 29.10535608 * k - 0.0000333 * T2 - 0.00000347 * T3
    Mpr = 306.0253 + 385.81691806 * k + 0.0107306 * T2 + 0.00001236 * T3
    F = 21.2964 + 390.67050646 * k - 0.0016528 * T2 - 0.00000239 * T3
    C1 = (0.1734 - 0.000393 * T) * sin(M * dr) + 0.0021 * sin(2 * dr * M)
    C1 = C1 - 0.4068 * sin(Mpr * dr) + 0.0161 * sin(dr * 2 * Mpr)
    C1 = C1 - 0.0004 * sin(dr * 3 * Mpr)
    C1 = C1 + 0.0104 * sin(dr * 2 * F) - 0.0051 * sin(dr * (M + Mpr))
    C1 = C1 - 0.0074 * sin(dr * (M - Mpr)) + 0.0004 * sin(dr * (2 * F + M))
    C1 = C1 - 0.0004 * sin(dr * (2 * F - M)) - 0.0006 * sin(dr * (2 * F + Mpr))
    C1 = C1 + 0.0010 * sin(dr * (2 * F - Mpr)) + 0.0005 * sin(dr * (2 * Mpr + M))
    if T < -11:
        deltat = (
            0.001
            + 0.000839 * T
            + 0.0002261 * T2
            - 0.00000845 * T3
            - 0.000000081 * T * T3
        )
    else:
        deltat = -0.000278 + 0.000265 * T + 0.000262 * T2
    return jd1 + C1 - deltat


def _sun_longitude(jdn):
    """The sun's longitude (radians) at Julian date jdn."""
    T = (jdn - 2451545.0) / 36525
    T2 = T * T
    dr = pi / 180
    M = 357.52910 + 35999.05030 * T - 0.0001559 * T2 - 0.00000048 * T * T2
    L0 = 280.46645 + 36000.76983 * T + 0.0003032 * T2
    DL = (1.914600 - 0.004817 * T - 0.000014 * T2) * sin(dr * M)
    DL += (0.019993 - 0.000101 * T) * sin(dr * 2 * M) + 0.000290 * sin(dr * 3 * M)
    L = (L0 + DL) * dr
    return L - pi * 2 * floor(L / (pi * 2))


def _sun_sector(day, tz):
    """Which 30-degree sector the sun is in at the start of local day `day`."""
    return floor(_sun_longitude(day - 0.5 - tz / 24) / pi * 6)


def _new_moon_day(k, tz):
    return floor(_new_moon(k) + 0.5 + tz / 24)


def _lunar_month11(year, tz):
    """The day month 11 (containing the winter solstice) starts, for year."""
    k = floor((gregorian_sdn(year, 12, 31) - 2415021) / 29.530588853)
    nm = _new_moon_day(k, tz)
    if _sun_sector(nm, tz) >= 9:
        nm = _new_moon_day(k - 1, tz)
    return nm


def _leap_month_offset(a11, tz):
    k = floor((a11 - 2415021.076998695) / 29.530588853 + 0.5)
    i = 1
    arc = _sun_sector(_new_moon_day(k + i, tz), tz)
    while True:
        last = arc
        i += 1
        arc = _sun_sector(_new_moon_day(k + i, tz), tz)
        if arc == last or i >= 14:
            return i - 1


def computed_lunar(sdn, tz):
    """(year, month, day, is_leap) of the lunar date for sdn, at UTC+tz."""
    year = gregorian_ymd(sdn)[0]
    j = floor((sdn - 2415021.076998695) / 29.530588853) + 1
    month_start = _new_moon_day(j, tz)
    while month_start > sdn:  # (Duc's code steps back once; j can be 2 ahead)
        j -= 1
        month_start = _new_moon_day(j, tz)
    a11 = _lunar_month11(year, tz)
    b11 = a11
    if a11 >= month_start:
        lunar_year = year
        a11 = _lunar_month11(year - 1, tz)
    else:
        lunar_year = year + 1
        b11 = _lunar_month11(year + 1, tz)
    diff = floor((month_start - a11) / 29)
    leap = False
    month = diff + 11
    if b11 - a11 > 365:
        leap_diff = _leap_month_offset(a11, tz)
        if diff >= leap_diff:
            month = diff + 10
            leap = diff == leap_diff
    if month > 12:
        month -= 12
    if month >= 11 and diff < 4:
        lunar_year -= 1
    return lunar_year, month, sdn - month_start + 1, leap


# -------------------------------------------------------------------------
#
# Sources: sdn -> (year, month, day, is_leap)
#
# -------------------------------------------------------------------------
def chinese(sdn):
    year, month, day = chinese_lunar_ymd(sdn)
    return year, month % 100, day, month > 100


def korean(sdn):
    from korean_lunar_calendar import KoreanLunarCalendar

    kasi = korean.kasi = getattr(korean, "kasi", None) or KoreanLunarCalendar()
    y, m, d = gregorian_ymd(sdn)
    if kasi.setSolarDate(y, m, d) and kasi.lunarYear <= KASI_LAST_YEAR:
        return (
            kasi.lunarYear,
            kasi.lunarMonth,
            kasi.lunarDay,
            bool(kasi.isIntercalation),
        )
    gap = gregorian_sdn(1582, 10, 4)
    if gap < sdn <= gap + 10:
        # KASI is proleptic Gregorian but rejects 1582-10-05..14: count on
        # from 10-04 (lunar 9/8; the month runs past the 18th).
        year, month, day, leap = korean(gap)
        return year, month, day + sdn - gap, leap
    if y < 2050:
        return None  # before KASI's first day (1000-02-13)
    return computed_lunar(sdn, 9)


def vietnamese(sdn):
    if sdn < VIETNAM_UTC7_FROM:
        return chinese(sdn)
    return computed_lunar(sdn, 7)


SOURCES = {"korean": (korean, 1000, 2199), "vietnamese": (vietnamese, 1967, 2199)}


# -------------------------------------------------------------------------
#
# Tables
#
# -------------------------------------------------------------------------
def new_year_sdn(source, year):
    """SDN of the source's lunar year/1/1, searched near the Chinese one."""
    guess = chinese_lunar_sdn(year, 1, 1)
    for sdn in range(guess - 40, guess + 40):
        if source(sdn) == (year, 1, 1, False):
            return sdn
    raise ValueError(f"no lunar new year {year}")


def encode_year(source, year):
    """One lunar year in _CHN_YEAR_INFOS' encoding."""
    sdn, end = new_year_sdn(source, year), new_year_sdn(source, year + 1)
    info, regular = 0, []
    while sdn < end:
        _year, month, day, leap = source(sdn)
        assert day == 1, (year, sdn, source(sdn))
        length = 0
        while sdn < end and source(sdn)[1] == month and source(sdn)[3] == leap:
            sdn += 1
            length += 1
        assert length in (29, 30), (year, month, leap, length)
        if leap:
            info |= month | ((length == 30) << 16)
        else:
            regular.append(month)
            info |= (length == 30) << (16 - month)
    assert regular == list(range(1, 13)), (year, regular)
    return info


def generate(name, first, last):
    source = SOURCES[name][0]
    for year in (first, last + 1):
        if new_year_sdn(source, year) != chinese_lunar_sdn(year, 1, 1):
            sys.exit(
                f"{name}: lunar {year} starts on a different day than in China; "
                "pick another end year"
            )
    infos = [encode_year(source, year) for year in range(first, last + 1)]

    # Every day of the table, decoded as gcalendar does, against the source.
    sdn = chinese_lunar_sdn(first, 1, 1)
    for i, info in enumerate(infos):
        for month, leap, days in _chn_iter_months(info):
            for day in range(1, days + 1):
                assert source(sdn) == (first + i, month, day, leap), (sdn, source(sdn))
                sdn += 1
    differ = sum(
        info != _CHN_YEAR_INFOS[first + i - _CHN_BASE_YEAR]
        for i, info in enumerate(infos)
    )
    print(
        f"# {name}: lunar years {first}-{last}, checked day by day; "
        f"{differ} of {len(infos)} years differ from the Chinese table",
        file=sys.stderr,
    )

    # The table for gramps/gen/lib/lunartables.py: ten years to a row.
    table = name.upper()
    print(f"{table}_BASE_YEAR = {first}")
    print(f"{table}_YEAR_INFOS = _years(")
    print(f"    {table}_BASE_YEAR,")
    print('    """')
    for i in range(0, len(infos), 10):
        row = "".join(f" {info:>5X}" for info in infos[i : i + 10])
        print(f"{first + i:>4}:{row}")
    print('""",')
    print(")")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in SOURCES:
        sys.exit(__doc__)
    _source, default_first, default_last = SOURCES[sys.argv[1]]
    first = int(sys.argv[2]) if len(sys.argv) > 2 else default_first
    last = int(sys.argv[3]) if len(sys.argv) > 3 else default_last
    generate(sys.argv[1], first, last)

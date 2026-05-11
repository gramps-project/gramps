#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2024-2025  Gabriel Rios
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
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

from __future__ import annotations
from typing import Optional

from gramps.gen.lib import Date
from gramps.gen.lib.date import gregorian


def fs_date_to_gramps_date(fs_date) -> Optional[Date]:
    """Convert a FamilySearch (custom) date object to a Gramps :class:`Date`.
    -------
    Date or None
        A populated Gramps Date, or None when no numeric components found.
    """
    if not fs_date:
        return None

    gr_date = Date()
    gr_date.set_calendar(Date.CAL_GREGORIAN)

    year = month = day = 0
    year2 = month2 = day2 = 0

    formal = getattr(fs_date, "formal", None)
    if formal:
        # Prefer start date; fall back to end date
        first = getattr(formal, "start_date", None)
        last = getattr(formal, "end_date", None)

        if first and getattr(first, "year", None):
            year = getattr(first, "year", 0)
            month = getattr(first, "month", 0)
            day = getattr(first, "day", 0)
        elif last and getattr(last, "year", None):
            year = getattr(last, "year", 0)
            month = getattr(last, "month", 0)
            day = getattr(last, "day", 0)

        if getattr(formal, "approximate", False):
            gr_date.set_modifier(Date.MOD_ABOUT)

        if getattr(formal, "is_range", False):
            if not first or not getattr(first, "year", None):
                gr_date.set_modifier(Date.MOD_BEFORE)
            elif not last or not getattr(last, "year", None):
                gr_date.set_modifier(Date.MOD_AFTER)
            else:
                gr_date.set_modifier(Date.MOD_RANGE)
                year2 = getattr(last, "year", 0)
                month2 = getattr(last, "month", 0)
                day2 = getattr(last, "day", 0)

    if (year, month, day) == (0, 0, 0):
        return None

    original_text = getattr(fs_date, "original", "") or ""

    if gr_date.modifier == Date.MOD_RANGE:
        gr_date.set(
            value=(day, month, year, 0, day2, month2, year2, 0),
            text=original_text,
            newyear=Date.NEWYEAR_JAN1,
        )
    else:
        gr_date.set(
            value=(day, month, year, 0),
            text=original_text,
            newyear=Date.NEWYEAR_JAN1,
        )

    return gr_date


def gramps_date_to_formal(date_obj: Date) -> str:
    """Convert a Gramps :class:Date to a GEDCOM "formal" date string.

    Spec: https://github.com/FamilySearch/gedcomx/blob/master/specifications/date-format-specification.md
    """
    if not date_obj:
        return ""

    gd = gregorian(date_obj)
    res = ""

    if gd.modifier == Date.MOD_ABOUT:
        res = "A"
    elif gd.modifier == Date.MOD_BEFORE:
        res = "/"

    if gd.dateval[Date._POS_YR] < 0:
        res += "-"
    else:
        res += "+"

    # build primary value
    if gd.dateval[Date._POS_DAY] > 0:
        val = "%04d-%02d-%02d" % (
            gd.dateval[Date._POS_YR],
            gd.dateval[Date._POS_MON],
            gd.dateval[Date._POS_DAY],
        )
    elif gd.dateval[Date._POS_MON] > 0:
        val = "%04d-%02d" % (
            gd.dateval[Date._POS_YR],
            gd.dateval[Date._POS_MON],
        )
    elif gd.dateval[Date._POS_YR] > 0:
        val = "%04d" % (gd.dateval[Date._POS_YR])
    else:
        return gd.text or ""

    res += val

    if gd.modifier == Date.MOD_AFTER:
        res += "/"

    if gd.modifier == Date.MOD_RANGE:
        res += "/"
        # Sign + year for range end
        if gd.dateval[Date._POS_RYR] < 0:
            res += "-"
        else:
            res += "+"
        # Build range end value if present
        if gd.dateval[Date._POS_RDAY] > 0:
            val = "%04d-%02d-%02d" % (
                gd.dateval[Date._POS_RYR],
                gd.dateval[Date._POS_RMON],
                gd.dateval[Date._POS_RDAY],
            )
        elif gd.dateval[Date._POS_RMON] > 0:
            val = "%04d-%02d" % (
                gd.dateval[Date._POS_RYR],
                gd.dateval[Date._POS_RMON],
            )
        elif gd.dateval[Date._POS_RYR] > 0:
            val = "%04d" % (gd.dateval[Date._POS_RYR])
        else:
            val = ""
        res += val

    return res

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

from gramps.gen.fs import utils as fs_utilities
from gramps.gen.lib import Date, EventType
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext


def person_dates_str(db, gr_person) -> str:
    """
    Returns a compact YYYY-YYYY string for a GRAMPS person using their
    Birth/Death (or placeholders when missing). Includes date modifiers.
    """
    if not gr_person:
        return ""

    birth_evt = fs_utilities.get_gramps_event(db, gr_person, EventType(EventType.BIRTH))
    if birth_evt:
        if birth_evt.date.modifier == Date.MOD_ABOUT:
            res = "~"
        elif birth_evt.date.modifier == Date.MOD_BEFORE:
            res = "/"
        else:
            res = " "
        val = f"{birth_evt.date.dateval[Date._POS_YR]:04d}"
        if val == "0000":
            val = "...."
        if birth_evt.date.modifier == Date.MOD_AFTER:
            res = res + val + "/-"
        else:
            res = res + val + "-"
    else:
        res = " ....-"

    death_evt = fs_utilities.get_gramps_event(db, gr_person, EventType(EventType.DEATH))
    if death_evt:
        if death_evt.date.modifier == Date.MOD_ABOUT:
            res = res + "~"
        elif death_evt.date.modifier == Date.MOD_BEFORE:
            res = res + "/"
        val = f"{death_evt.date.dateval[Date._POS_YR]:04d}"
        if val == "0000":
            val = "...."
        if death_evt.date.modifier == Date.MOD_AFTER:
            res = res + val + "/"
        else:
            res = res + val
    else:
        res = res + "...."
    return res


def fs_person_dates_str(db, fs_person) -> str:
    """
    Returns a compact YYYY-YYYY string for a FamilySearch (GEDCOM) person
    using Birth/Death formal dates (or placeholders).
    """
    if not fs_person:
        return ""

    fs_fact = fs_utilities.get_fs_fact(fs_person, "http://gedcomx.org/Birth")
    if (
        fs_fact
        and getattr(fs_fact, "date", None)
        and getattr(fs_fact.date, "formal", None)
    ):
        if fs_fact.date.formal.approximate:
            res = "~"
        else:
            res = " "
        if fs_fact.date.formal.start_date:
            res = res + str(fs_fact.date.formal.start_date.year)
        if fs_fact.date.formal.is_range and fs_fact.date.formal.end_date:
            res = res + "/" + str(fs_fact.date.formal.end_date.year)
        res = res + "-"
    else:
        res = " ....-"

    fs_fact = fs_utilities.get_fs_fact(fs_person, "http://gedcomx.org/Death")
    if (
        fs_fact
        and getattr(fs_fact, "date", None)
        and getattr(fs_fact.date, "formal", None)
    ):
        if fs_fact.date.formal.approximate:
            res = res + "~"
        else:
            res = res + " "
        if fs_fact.date.formal.start_date:
            res = res + str(fs_fact.date.formal.start_date.year)
        if fs_fact.date.formal.is_range:
            if fs_fact.date.formal.end_date and fs_fact.date.formal.end_date.year:
                res = res + "/" + str(fs_fact.date.formal.end_date.year)
            elif fs_fact.date.formal.start_date and fs_fact.date.formal.start_date.year:
                res = res + "/" + str(fs_fact.date.formal.start_date.year)
    else:
        res = res + "...."
    return res

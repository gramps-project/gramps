# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007-2009  Douglas S. Blank <doug.blank@gmail.com>
# Copyright (C) 2026  Brian Caudill
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

"""
Shared surname tallying for the surname gramplets.

The Top Surnames, Surname Cloud and Statistics gramplets all report a "unique
surnames" total.  Historically each computed it by a different rule, so the
same tree produced different totals (bug #6793).  This module is the single
canonical rule: a *unique surname* is a distinct, **non-empty** surname **group
name**, taken from a person's primary and alternate names (a person with no
surname contributes none).  Every gramplet that reports the figure builds its
tally with :func:`record_surnames` here, so the totals always agree.
"""

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.lib import Person
from gramps.gen.types import PersonHandle


# ------------------------------------------------------------------------
#
# Functions
#
# ------------------------------------------------------------------------
def record_surnames(
    person: Person,
    surnames: dict[str, int],
    representative_handle: dict[str, PersonHandle],
) -> None:
    """
    Tally one person's surnames and choose representatives for them.

    The person is counted under every group name taken from their primary and
    alternate names.  They become the representative for a surname only when it
    is their primary group name, or when no representative has been chosen yet.
    The Same Surnames quick view re-derives the surname from the
    representative's primary name, so a representative whose primary surname
    differs would open a report for a different surname than the one clicked.

    A person with no surname (an empty group name) is not counted: the empty
    string is not a surname, so it never contributes a "unique surname" (#6793).
    """
    primary_name = person.get_primary_name()
    primary_surname = primary_name.get_group_name().strip()
    allnames = set(
        name.get_group_name().strip()
        for name in [primary_name] + person.get_alternate_names()
    )
    for surname in allnames:
        if not surname:
            continue  # empty group name (no surname) is not a unique surname
        surnames[surname] += 1
        if surname == primary_surname or surname not in representative_handle:
            representative_handle[surname] = person.handle

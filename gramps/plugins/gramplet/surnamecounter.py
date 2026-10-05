#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Gramps developers
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

"""
Shared surname-counting helper for the surname gramplets.

The "Total unique surnames" / "Unique surnames" tallies of the Surname Cloud
and Statistics gramplets keyed off the *full* multi-component surname string
(``Name.get_surname()``).  A person whose name carries a primary family surname
plus a separate patronymic-origin surname therefore produced a distinct entry
per patronymic ("Иванов Петрович", "Иванов Сергеевич", ...) instead of the one
family surname "Иванов" they share (bug #6988).

:func:`get_counting_surname` derives the surname string under which such a name
should be counted, dropping non-primary surname components of patronymic or
matronymic origin while leaving every other surname component (e.g. a Spanish
maternal name) untouched.
"""

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.lib import Name
from gramps.gen.lib.nameorigintype import NameOriginType

# Non-primary surname components of these origins are excluded from the count:
# they identify the individual (a patronymic/matronymic), not the shared family
# surname the tally is meant to group people by.
_EXCLUDED_ORIGINS = (NameOriginType.PATRONYMIC, NameOriginType.MATRONYMIC)


def get_counting_surname(name):
    """
    Return the surname string used to count/identify *name*'s surname.

    Non-primary surname components of patronymic or matronymic origin are
    dropped before the surname is formatted, so that people who share a family
    surname but carry different patronymics are counted as one surname.  When
    there is nothing patronymic to drop (or it is the only component), the
    unchanged :meth:`~.surnamebase.SurnameBase.get_surname` string is returned.

    :param name: the name to derive the counting surname from
    :type name: :class:`~.name.Name`
    :returns: the family-surname string used for counting
    :rtype: str
    """
    surname_list = name.get_surname_list()
    kept = [
        surname
        for surname in surname_list
        if surname.get_primary() or surname.get_origintype() not in _EXCLUDED_ORIGINS
    ]
    if not kept or len(kept) == len(surname_list):
        # nothing to drop, or only patronymic components: defer to the
        # existing full-surname formatting unchanged.
        return name.get_surname()
    # Reuse the production surname formatting on the filtered list rather than
    # re-implementing it: build a throwaway Name over the kept components.
    counted = Name()
    counted.set_surname_list(kept)
    return counted.get_surname()

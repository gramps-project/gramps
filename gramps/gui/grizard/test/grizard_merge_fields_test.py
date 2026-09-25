#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Grizard Merge Field Tests
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
Tests for the field rows built by the Grizard merge dialog.

These cover the surname rows, where a GEDCOM surname prefix (``SPFX``)
and additional surnames must not be mistaken for a match.
"""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
from __future__ import annotations
import unittest

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.lib import Name, Person, Surname
from gramps.gen.grizard.grizard import surname_prefix_text, surname_text
from gramps.gui.grizard.grizardmergedialog import field_values_differ


def _person(first: str, surnames: list[tuple[str, str]]) -> Person:
    """
    Build a person with one primary name from (surname, prefix) pairs.

    :param first: The given name.
    :param surnames: Sequence of ``(surname, prefix)`` tuples.
    :returns: The constructed person.
    :rtype: Person
    """
    name = Name()
    name.first_name = first
    for surname, prefix in surnames:
        surn = Surname()
        surn.set_surname(surname)
        surn.set_prefix(prefix)
        name.add_surname(surn)
    person = Person()
    person.set_primary_name(name)
    return person


class GrizardMergeFieldRowsTest(unittest.TestCase):
    """Field row values for names that differ only by prefix or extra surname."""

    def test_surname_prefix_difference_is_flagged(self) -> None:
        """
        A SPFX-only difference must mark the Surname Prefix row as different.
        """
        source = _person("Anna", [("Hansdotter", "")])
        target = _person("Anna", [("Hansdotter", "Vrow")])
        self.assertFalse(
            field_values_differ(
                surname_text(source.get_primary_name()),
                surname_text(target.get_primary_name()),
            )
        )
        self.assertTrue(
            field_values_differ(
                surname_prefix_text(source.get_primary_name()),
                surname_prefix_text(target.get_primary_name()),
            )
        )
        self.assertEqual(surname_prefix_text(source.get_primary_name()), "")
        self.assertEqual(surname_prefix_text(target.get_primary_name()), "Vrow")

    def test_additional_surname_is_flagged(self) -> None:
        """
        An extra surname on the target must mark the Surname row as different.
        """
        source = _person("Anna", [("Hansdotter", "")])
        target = _person("Anna", [("Hansdotter", "Vrow"), ("Smith", "")])
        self.assertTrue(
            field_values_differ(
                surname_text(source.get_primary_name()),
                surname_text(target.get_primary_name()),
            )
        )
        self.assertEqual(surname_text(source.get_primary_name()), "Hansdotter")
        self.assertEqual(surname_text(target.get_primary_name()), "Hansdotter Smith")

    def test_shared_prefix_is_not_flagged(self) -> None:
        """
        Equal prefixes and surnames must not be reported as a difference.
        """
        source = _person("Anna", [("Hansdotter", "Vrow")])
        target = _person("Anna", [("Hansdotter", "Vrow")])
        self.assertFalse(
            field_values_differ(
                surname_prefix_text(source.get_primary_name()),
                surname_prefix_text(target.get_primary_name()),
            )
        )

    def test_empty_source_prefix_still_differs_from_target(self) -> None:
        """
        An empty source value compares as different from a populated target.
        """
        self.assertTrue(field_values_differ("", "Vrow"))
        self.assertFalse(field_values_differ(None, ""))
        self.assertFalse(field_values_differ("Vrow", "Vrow"))


if __name__ == "__main__":
    unittest.main()

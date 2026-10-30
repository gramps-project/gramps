#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Gramps Development Team
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
Unit test for the spouse-name selection of
:meth:`gramps.plugins.lib.libnarrate.Narrator.get_married_string`.

Bug 0004862: in the marriage sentence of a narrative report
("He married <name> on <date>.") the spouse was rendered with the spouse's
*currently preferred* (primary) name. When the spouse later divorced and
remarried, that preferred name became a later married name, so the sentence
about the *earlier* marriage silently changed to the new name -- ambiguous.

The fix names the spouse by a stable Birth Name when one exists, falling back
to the preferred name only when the spouse has no Birth Name. These tests
drive the production ``get_married_string`` path (not a copy) through a
real :class:`~.Narrator` over in-memory Gramps objects.
"""

import unittest

from gramps.gen.lib import (
    Family,
    FamilyRelType,
    Name,
    NameType,
    Person,
    Surname,
)
from gramps.plugins.lib.libnarrate import Narrator


def _make_name(name_type, given, surname):
    """Build a :class:`~.Name` of the given type, given name and surname."""
    surname_obj = Surname()
    surname_obj.set_surname(surname)
    name = Name()
    name.set_type(name_type)
    name.set_first_name(given)
    name.add_surname(surname_obj)
    return name


def _make_person(handle, gender, primary_name, alternate_names=()):
    person = Person()
    person.set_handle(handle)
    person.set_gender(gender)
    person.set_primary_name(primary_name)
    for alt in alternate_names:
        person.add_alternate_name(alt)
    return person


class _FakeDb:
    """Minimal db: the narrator only needs to resolve the spouse handle."""

    def __init__(self, people):
        self._people = {p.get_handle(): p for p in people}

    def get_person_from_handle(self, handle):
        return self._people.get(handle)


def _married_sentence(subject, spouse):
    """Run the production get_married_string() path and return its sentence."""
    family = Family()
    family.set_father_handle(subject.get_handle())
    family.set_mother_handle(spouse.get_handle())
    family.set_relationship(FamilyRelType(FamilyRelType.MARRIED))

    narrator = Narrator(_FakeDb([subject, spouse]), verbose=True)
    narrator.set_subject(subject)
    return narrator.get_married_string(family)


class TestMarriedStringSpouseName(unittest.TestCase):
    def setUp(self):
        # The narrated subject; a plain Birth-named husband.
        self.subject = _make_person(
            "subj", Person.MALE, _make_name(NameType.BIRTH, "Peter", "Black")
        )

    def test_uses_birth_name_not_later_preferred_married_name(self):
        """
        Spouse whose *preferred* (primary) name is a later Married Name but who
        still carries her Birth Name as an alternate must be named by the
        stable Birth Name in the marriage sentence -- not the later name.
        """
        spouse = _make_person(
            "sp",
            Person.FEMALE,
            _make_name(NameType.MARRIED, "Agnes", "White"),  # later preferred
            [_make_name(NameType.BIRTH, "Agnes", "Red")],  # birth name
        )

        sentence = _married_sentence(self.subject, spouse)

        self.assertIn("Red", sentence)
        self.assertNotIn("White", sentence)

    def test_stable_when_a_later_preferred_name_is_acquired(self):
        """
        Acquiring a later preferred (married) name must not change the name the
        marriage sentence uses: it stays the spouse's Birth Name.
        """
        birth = _make_name(NameType.BIRTH, "Agnes", "Red")
        before = _make_person("sp", Person.FEMALE, birth)
        sentence_before = _married_sentence(self.subject, before)

        # Same person later divorces and remarries: the preferred name becomes a
        # later Married Name and the Birth Name is demoted to an alternate.
        after = _make_person(
            "sp",
            Person.FEMALE,
            _make_name(NameType.MARRIED, "Agnes", "White"),
            [_make_name(NameType.BIRTH, "Agnes", "Red")],
        )
        sentence_after = _married_sentence(self.subject, after)

        self.assertEqual(sentence_before, sentence_after)

    def test_falls_back_to_preferred_name_without_a_birth_name(self):
        """
        When the spouse has no Birth Name the historical behaviour is kept: the
        preferred (primary) name is used.
        """
        spouse = _make_person(
            "sp",
            Person.FEMALE,
            _make_name(NameType.MARRIED, "Agnes", "White"),
        )

        sentence = _married_sentence(self.subject, spouse)

        self.assertIn("White", sentence)


if __name__ == "__main__":
    unittest.main()

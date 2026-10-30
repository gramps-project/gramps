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
Unittest for bug #6988: the surname gramplets must count a person carrying a
primary family surname plus a separate patronymic-origin surname under the one
family surname ("Иванов"), not one entry per patronymic combination.

The test drives the production counting routine
(:func:`~.surnamecounter.get_counting_surname`) that both the Surname Cloud and
the Statistics gramplets route through — not a copy of it.
"""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
import unittest

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.lib import Name, Surname
from gramps.gen.lib.nameorigintype import NameOriginType
from gramps.plugins.gramplet.surnamecounter import get_counting_surname


# -------------------------------------------------------------------------
#
# Test helpers
#
# -------------------------------------------------------------------------
def make_surname(text, origin=None, primary=False):
    """
    Build a single Surname component with the given text/origin/primary flag.
    """
    surname = Surname()
    surname.set_surname(text)
    surname.set_primary(primary)
    if origin is not None:
        surname.set_origintype(origin)
    return surname


def make_name(*surnames):
    """
    Build a Name carrying the given ordered Surname components.
    """
    name = Name()
    name.set_surname_list(list(surnames))
    return name


# -------------------------------------------------------------------------
#
# PatronymicSurnameCountTest
#
# -------------------------------------------------------------------------
class PatronymicSurnameCountTest(unittest.TestCase):
    """
    Bug #6988: patronymic-origin surnames must not fragment the surname count.
    """

    def test_patronymic_collapses_to_family_surname(self):
        """
        A name with primary "Иванов" plus a patronymic-origin "Петрович" is
        counted under the family surname "Иванов" alone.
        """
        name = make_name(
            make_surname("Иванов", origin=NameOriginType.INHERITED, primary=True),
            make_surname("Петрович", origin=NameOriginType.PATRONYMIC),
        )
        # Document the bug: the full surname string fragments the count.
        self.assertEqual(name.get_surname(), "Иванов Петрович")
        # The fix: the counting routine yields the family surname only.
        self.assertEqual(get_counting_surname(name), "Иванов")

    def test_different_patronymics_share_one_counting_surname(self):
        """
        People sharing "Иванов" but with different patronymics map to the same
        counting surname, so they tally as one unique surname.
        """
        surnames = {
            get_counting_surname(
                make_name(
                    make_surname(
                        "Иванов", origin=NameOriginType.INHERITED, primary=True
                    ),
                    make_surname(patronymic, origin=NameOriginType.PATRONYMIC),
                )
            )
            for patronymic in ("Петрович", "Сергеевич", "Андреевич")
        }
        self.assertEqual(surnames, {"Иванов"})

    def test_matronymic_also_collapses(self):
        """
        Matronymic-origin non-primary components are dropped as well.
        """
        name = make_name(
            make_surname("Иванов", origin=NameOriginType.INHERITED, primary=True),
            make_surname("Марьевич", origin=NameOriginType.MATRONYMIC),
        )
        self.assertEqual(get_counting_surname(name), "Иванов")

    def test_plain_single_surname_unchanged(self):
        """
        A name without any patronymic component is counted exactly as before.
        """
        name = make_name(
            make_surname("Smith", origin=NameOriginType.INHERITED, primary=True)
        )
        self.assertEqual(get_counting_surname(name), "Smith")
        self.assertEqual(get_counting_surname(name), name.get_surname())

    def test_non_patronymic_secondary_surname_preserved(self):
        """
        A non-primary surname of a non-patronymic origin (e.g. a Spanish
        maternal name) is kept, so only patronymics are collapsed.
        """
        name = make_name(
            make_surname("García", origin=NameOriginType.INHERITED, primary=True),
            make_surname("Pérez", origin=NameOriginType.INHERITED),
        )
        self.assertEqual(get_counting_surname(name), name.get_surname())
        self.assertIn("Pérez", get_counting_surname(name))

    def test_only_patronymic_component_falls_back(self):
        """
        When the patronymic is the *only* surname component there is nothing
        else to count, so the unchanged surname string is returned rather than
        an empty key.
        """
        name = make_name(
            make_surname("Петрович", origin=NameOriginType.PATRONYMIC, primary=True)
        )
        self.assertEqual(get_counting_surname(name), "Петрович")


if __name__ == "__main__":
    unittest.main()

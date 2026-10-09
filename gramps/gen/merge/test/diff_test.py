#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  David Straub
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
Unit tests for the object difference engine.
"""

# ------------------------
# Python modules
# ------------------------
import unittest

# ------------------------
# Gramps modules
# ------------------------
from gramps.gen.lib import Person
from gramps.gen.lib.json_utils import object_to_dict
from gramps.gen.merge.diff import diff_items


# ------------------------------------------------------------
#
# DiffItemsTest
#
# ------------------------------------------------------------
class DiffItemsTest(unittest.TestCase):
    """
    Tests for diff_items.
    """

    def test_familysearch_sync_is_ignored(self) -> None:
        """
        FamilySearch sync metadata is not a genealogical difference.
        """
        person1 = Person()
        person1.set_handle("person-1")
        person2 = Person(person1.serialize())
        person2.set_familysearch_sync({"fsid": "ABCD-EFG"})

        self.assertFalse(
            diff_items("Person", object_to_dict(person1), object_to_dict(person2))
        )
        self.assertFalse(
            diff_items("Person", object_to_dict(person2), object_to_dict(person1))
        )

    def test_familysearch_sync_missing_on_one_side(self) -> None:
        """
        Data without the optional FamilySearch sync key can be compared.
        """
        person = Person()
        person.set_familysearch_sync({"fsid": "ABCD-EFG"})
        data1 = object_to_dict(person)
        data2 = object_to_dict(person)
        del data2["familysearch_sync"]

        self.assertFalse(diff_items("Person", data1, data2))

    def test_other_differences_are_reported(self) -> None:
        """
        Differences in other fields are still reported.
        """
        person1 = Person()
        person2 = Person(person1.serialize())
        person2.set_gramps_id("I0001")

        self.assertTrue(
            diff_items("Person", object_to_dict(person1), object_to_dict(person2))
        )


if __name__ == "__main__":
    unittest.main()

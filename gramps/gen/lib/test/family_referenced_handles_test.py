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
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

"""Tests for Family.get_referenced_handles including child handles.

Regression test for the removal of child_ref_list from get_referenced_handles()
which broke callman.py and any other caller using the non-recursive form.

# python3 -m unittest gramps.gen.lib.test.family_referenced_handles_test -v
"""

import unittest

from gramps.gen.lib.childref import ChildRef
from gramps.gen.lib.family import Family


# -------------------------------------------------------------------------
#
# TestFamilyGetReferencedHandles
#
# -------------------------------------------------------------------------
class TestFamilyGetReferencedHandles(unittest.TestCase):
    """Tests for Family.get_referenced_handles."""

    def _make_child_ref(self, handle: str) -> ChildRef:
        """Return a ChildRef pointing at handle."""
        cr = ChildRef()
        cr.ref = handle
        return cr

    def test_empty_family_returns_no_person_handles(self):
        """An empty family has no father, mother, or children."""
        fam = Family()
        handles = [h for cls, h in fam.get_referenced_handles() if cls == "Person"]
        self.assertEqual(handles, [])

    def test_father_handle_included(self):
        """Father handle appears in get_referenced_handles."""
        fam = Family()
        fam.set_father_handle("father-h1")
        result = fam.get_referenced_handles()
        self.assertIn(("Person", "father-h1"), result)

    def test_mother_handle_included(self):
        """Mother handle appears in get_referenced_handles."""
        fam = Family()
        fam.set_mother_handle("mother-h1")
        result = fam.get_referenced_handles()
        self.assertIn(("Person", "mother-h1"), result)

    def test_single_child_handle_included(self):
        """A single child's handle appears in get_referenced_handles."""
        fam = Family()
        fam.add_child_ref(self._make_child_ref("child-h1"))
        result = fam.get_referenced_handles()
        self.assertIn(("Person", "child-h1"), result)

    def test_multiple_children_all_included(self):
        """All children's handles appear in get_referenced_handles."""
        fam = Family()
        for h in ("child-h1", "child-h2", "child-h3"):
            fam.add_child_ref(self._make_child_ref(h))
        result = fam.get_referenced_handles()
        for h in ("child-h1", "child-h2", "child-h3"):
            self.assertIn(("Person", h), result)

    def test_full_family_all_handles_included(self):
        """Father, mother, and children all appear in get_referenced_handles."""
        fam = Family()
        fam.set_father_handle("father-h1")
        fam.set_mother_handle("mother-h1")
        fam.add_child_ref(self._make_child_ref("child-h1"))
        fam.add_child_ref(self._make_child_ref("child-h2"))
        result = fam.get_referenced_handles()
        self.assertIn(("Person", "father-h1"), result)
        self.assertIn(("Person", "mother-h1"), result)
        self.assertIn(("Person", "child-h1"), result)
        self.assertIn(("Person", "child-h2"), result)


if __name__ == "__main__":
    unittest.main()

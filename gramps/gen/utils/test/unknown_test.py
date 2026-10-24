#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Ian Davis
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
Tests for make_unknown in gramps.gen.utils.unknown.
"""

import unittest

from ...lib import DNAMatch, DNATest
from ..unknown import make_unknown


class MakeUnknownDNATest(unittest.TestCase):
    """
    make_unknown builds and commits placeholder DNATest and DNAMatch objects.
    """

    def _make(self, cls):
        """Run make_unknown for cls and return the objects it committed."""
        committed = []

        def class_func(handle):
            obj = cls()
            obj.set_handle(handle)
            return obj

        def commit_func(obj, transaction, change):
            committed.append(obj)

        retval = make_unknown("h0001", "n0001", class_func, commit_func, None)
        self.assertEqual(retval, committed)
        return committed

    def test_dnatest(self):
        objs = self._make(DNATest)
        self.assertEqual(len(objs), 1)
        self.assertEqual(objs[0].get_handle(), "h0001")
        self.assertEqual(objs[0].get_account_name(), "Unknown")
        self.assertEqual(objs[0].get_note_list(), ["n0001"])

    def test_dnamatch(self):
        objs = self._make(DNAMatch)
        self.assertEqual(len(objs), 1)
        self.assertEqual(objs[0].get_handle(), "h0001")
        self.assertEqual(objs[0].get_note_list(), ["n0001"])


if __name__ == "__main__":
    unittest.main()

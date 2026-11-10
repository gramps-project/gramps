# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  pcc0x
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

"""Unittest for relationship.py"""

# ------------------------
# Python modules
# ------------------------
import unittest
from unittest.mock import patch

# ------------------------
# Gramps modules
# ------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.lib import Person

# ------------------------
# Gramps specific
# ------------------------
from ..relationship import RelationshipCalculator

_ = glocale.translation.sgettext
LOOP = _("Relationship loop detected")


# ------------------------------------------------------------
#
# RelationshipLoopTest
#
# ------------------------------------------------------------
class RelationshipLoopTest(unittest.TestCase):
    """
    The distance search gives up with "Relationship loop detected" when the
    ancestor walk raises RuntimeError. No test data reaches that point, so the
    walk is made to raise.
    """

    def setUp(self) -> None:
        """
        Two unrelated people and a calculator whose ancestor walk raises.
        """
        self.calc = RelationshipCalculator()
        self.orig = Person()
        self.orig.set_handle("A")
        self.other = Person()
        self.other.set_handle("B")
        walk = patch.object(
            RelationshipCalculator,
            "_RelationshipCalculator__apply_filter",
            side_effect=RuntimeError,
        )
        walk.start()
        self.addCleanup(walk.stop)

    def test_all_dist_gives_a_list(self) -> None:
        """
        With all_dist, the loop result is a list of tuples like every other.
        """
        data, msg = self.calc.get_relationship_distance_new(
            None, self.orig, self.other, all_dist=True
        )
        self.assertEqual(data, [(-1, None, -1, [], -1, [])])
        self.assertEqual(msg, [LOOP])

    def test_shortest_gives_a_tuple(self) -> None:
        """
        Without all_dist, the loop result stays a single tuple.
        """
        data, msg = self.calc.get_relationship_distance_new(None, self.orig, self.other)
        self.assertEqual(data, (-1, None, -1, [], -1, []))
        self.assertEqual(msg, [LOOP])

    def test_all_relationships_finds_none(self) -> None:
        """
        get_all_relationships reports no relationship instead of raising
        TypeError.
        """
        with patch.object(self.calc, "is_spouse", return_value=None):
            result = self.calc.get_all_relationships(None, self.orig, self.other)
        self.assertEqual(result, ([], []))


if __name__ == "__main__":
    unittest.main()

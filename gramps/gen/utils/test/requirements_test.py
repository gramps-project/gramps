#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Eduard Ralph
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
Tests for :class:`gramps.gen.utils.requirements.Requirements`.
"""

# -------------------------------------------------------------------------
#
# Standard python modules
#
# -------------------------------------------------------------------------
import unittest

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ..requirements import Requirements


# ------------------------------------------------------------
#
# TestRequirementsInfoOmitsEmptyPairs
#
# ------------------------------------------------------------
class TestRequirementsInfoOmitsEmptyPairs(unittest.TestCase):
    """
    ``Requirements.info`` must return only label + populated-table pairs.

    A present-but-empty requires list - e.g. an addon listing carrying
    ``"re": []`` because its .gpr.py declares ``requires_exe=[]`` - must
    not produce a labelled section with an empty table. The previous
    contract emitted the label + empty table, which (a) rendered an
    empty labelled section in the core Addon Manager's Requirements
    dialog, and (b) was the shape that crashed the Plugin Manager
    Enhanced addon's row-click handler (Mantis 13979, fixed
    addon-side in addons-source PR 916).
    """

    def setUp(self):
        self.req = Requirements()

    # ----- single shapes -------------------------------------------------

    def test_no_requires_keys(self):
        """An addon with no requires keys returns an empty list."""
        self.assertEqual(self.req.info({"i": "x"}), [])

    def test_present_but_empty_re_omits_pair(self):
        """``"re": []`` must not produce an ``Executables`` pair."""
        self.assertEqual(self.req.info({"i": "x", "re": []}), [])

    def test_present_but_empty_rm_omits_pair(self):
        """``"rm": []`` must not produce a ``Python modules`` pair."""
        self.assertEqual(self.req.info({"i": "x", "rm": []}), [])

    def test_present_but_empty_rg_omits_pair(self):
        """``"rg": []`` must not produce a GI pair."""
        self.assertEqual(self.req.info({"i": "x", "rg": []}), [])

    def test_all_three_present_but_empty_omits_all_pairs(self):
        """All three keys present-but-empty returns an empty list."""
        self.assertEqual(
            self.req.info({"i": "x", "rm": [], "rg": [], "re": []}),
            [],
        )

    # ----- the live trigger shape ----------------------------------------

    def test_postgresql_enhanced_listing_shape(self):
        """
        The live PostgreSQL Enhanced listing shape - ``rm`` populated,
        ``re`` empty - must produce only the Python-modules pair, with
        no trailing Executables pair to crash downstream consumers.
        """
        result = self.req.info({"i": "postgresqlenhanced", "rm": ["psycopg"], "re": []})
        self.assertEqual(len(result), 2, result)
        label, table = result
        self.assertIn("Python modules", label)
        self.assertEqual(len(table), 1)
        self.assertEqual(table[0][0], "psycopg")

    # ----- positive cases: existing behaviour preserved ------------------

    def test_non_empty_rm_still_renders(self):
        """A populated ``rm`` still produces its label + table unchanged."""
        result = self.req.info({"i": "x", "rm": ["psycopg", "Pillow"]})
        self.assertEqual(len(result), 2, result)
        label, table = result
        self.assertIn("Python modules", label)
        self.assertEqual([row[0] for row in table], ["psycopg", "Pillow"])

    def test_non_empty_rm_and_re_both_render_in_order(self):
        """
        Multiple populated sections still emit their pairs in the same
        rm / rg / re order Requirements.info has always used - the change
        only suppresses empty sections, it does not reorder anything.
        """
        result = self.req.info({"i": "x", "rm": ["psycopg"], "re": ["dot"]})
        self.assertEqual(len(result), 4, result)
        self.assertIn("Python modules", result[0])
        self.assertEqual(result[1][0][0], "psycopg")
        self.assertIn("Executables", result[2])
        self.assertEqual(result[3][0][0], "dot")


if __name__ == "__main__":
    unittest.main()

# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2024  Gramps developers
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
Regression test for Mantis 12539.

In the Families view, after a filter/Find narrows the family list the
previously active family can be filtered out.  ``ListView.build_tree`` left it
active even though it was no longer selectable, so the bottombar "Children" tab
kept showing the hidden family (or nothing) until the user manually re-clicked a
row.

``FamilyView.build_tree`` now routes the post-rebuild selection decision through
:func:`gramps.plugins.view.familyview_selection.resolve_active_after_filter`
(the exact function this test drives -- not a copy of it), then calls
``change_active`` on the resolved handle so the ``active-changed`` signal fires
and the Children gramplet rebuilds for the now-current, visible family.

This unit covers that decision headlessly (no Gtk import); the end-to-end GUI
behaviour is characterised by the committed AT-SPI repro
``engine/interface/test_bug_12539_families-children-refresh.py``.
"""

import unittest

from gramps.plugins.view.familyview_selection import resolve_active_after_filter


class ResolveActiveAfterFilterTest(unittest.TestCase):
    """The selection that the Children tab must follow after a list rebuild."""

    def test_active_filtered_out_falls_back_to_first_visible(self):
        # The Mantis 12539 scenario: the active family ("F_old") is no longer
        # in the filtered list, so the active family must move to the first
        # visible row -- NOT stay on the hidden family (which left the Children
        # tab stale).
        result = resolve_active_after_filter("F_old", ["F_a", "F_b", "F_c"])
        self.assertEqual(result, "F_a")
        self.assertNotEqual(
            result,
            "F_old",
            "active family stayed on the filtered-out family -- the Children "
            "tab would keep showing the hidden family (bug 12539)",
        )

    def test_active_still_visible_is_kept(self):
        # When the active family survives the filter, it must stay active so no
        # spurious active-changed fires and the selection does not jump.
        result = resolve_active_after_filter("F_b", ["F_a", "F_b", "F_c"])
        self.assertEqual(result, "F_b")

    def test_no_active_does_not_autoselect(self):
        # A plain build / startup with nothing active must not auto-select the
        # first row.
        self.assertIsNone(resolve_active_after_filter(None, ["F_a", "F_b"]))
        self.assertIsNone(resolve_active_after_filter("", ["F_a", "F_b"]))

    def test_active_filtered_out_with_empty_list_clears(self):
        # A filter that matches nothing leaves no family to show.
        self.assertIsNone(resolve_active_after_filter("F_old", []))

    def test_active_visible_with_empty_list(self):
        # Defensive: an active handle but an empty visible set yields None.
        self.assertIsNone(resolve_active_after_filter("F_old", []))


if __name__ == "__main__":
    unittest.main()

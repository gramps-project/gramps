#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026       The Gramps project
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

"""Unittest for gramps.gui.viewmanagerutils.views_to_show.

Regression test for bug 8796: hiding **every** view plugin in the Plugin
Manager makes Gramps crash at startup with
``IndexError: list assignment index out of range``.

Root cause: with no view plugins available ``ViewManager.get_available_views()``
returns ``[]``, so ``views_to_show([])`` used to yield ``(0, 0, [])`` -- claiming
category 0 exists.  ``ViewManager.init_interface`` then called
``goto_page(0, 0)``, whose ``self.current_views[cat_num] = view_num`` indexed the
empty ``current_views`` list and raised.

This test drives the **production** ``views_to_show`` -- the exact function
``viewmanager.init_interface`` calls (``viewmanager`` re-imports it from
``viewmanagerutils``) -- not a re-implementation.  ``viewmanagerutils`` carries no
``gi`` / GTK import, so the genuine production decision logic is exercised here
under the headless test runner without launching the GTK ``ViewManager``.

The fix makes ``views_to_show`` total over the empty view set: it reports "no
category" (``current_cat is None``) so ``init_interface`` leaves the interface
with no active page instead of navigating into the empty set.
"""

import unittest

from ..viewmanagerutils import views_to_show


class TestViewsToShowEmpty(unittest.TestCase):
    """views_to_show must be total over zero available views (bug 8796)."""

    def test_empty_views_reports_no_category(self):
        """views_to_show([]) reports no category instead of collapsing to (0, 0, []).

        Pre-fix this returns ``(0, 0, [])``; the caller then ran
        ``goto_page(0, 0)`` -> ``self.current_views[0] = 0`` on an empty list and
        raised ``IndexError: list assignment index out of range`` at startup.
        Post-fix it returns ``(None, None, [])`` so ``init_interface`` skips
        navigation and the app opens with no active page.
        """
        self.assertEqual(views_to_show([], use_last=False), (None, None, []))

    def test_empty_views_use_last(self):
        """The empty-view set is total under use_last=True as well."""
        self.assertEqual(views_to_show([], use_last=True), (None, None, []))


if __name__ == "__main__":
    unittest.main()

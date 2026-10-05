#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2025  The Gramps project
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
Regression tests for the Addon Manager refresh against a missing listing
(Mantis 13174).

These are headless, GUI-import-free: the dangling-window crash is reproduced
through the same liveness gate the real Addon Manager refresh routes its
delivery through (:class:`AddonRefreshDispatch`), so no ``gi`` / ``gramps.gui``
import is needed.
"""

import os
import tempfile
import unittest

from gramps.gen.plug.utils import get_addons
from gramps.gen.plug._addonrefresh import AddonRefreshDispatch


class MissingListingFetchTest(unittest.TestCase):
    """The fetch surfaces a missing listing as a handled empty result."""

    def test_missing_listing_returns_empty_without_raising(self):
        """A project whose listing .json is absent yields [] (no exception)."""
        empty_dir = tempfile.mkdtemp()  # no listings/ subdir -> every lookup 404s
        url = "file://" + empty_dir
        result = get_addons("TestProject", url)
        self.assertEqual(result, [])


class AddonRefreshDispatchTest(unittest.TestCase):
    """
    The dispatch gate that stops a late refresh result from touching a
    destroyed window (the dangling-window crash, Mantis 13174).
    """

    def setUp(self):
        self.delivered = []

    def _apply(self, addon_list):
        self.delivered.append(addon_list)

    def test_live_dispatch_delivers(self):
        """A result delivered while the window is open is applied."""
        dispatch = AddonRefreshDispatch(self._apply)
        self.assertTrue(dispatch.alive)
        applied = dispatch.deliver(["addon"])
        self.assertTrue(applied)
        self.assertEqual(self.delivered, [["addon"]])

    def test_cancelled_dispatch_drops_late_result(self):
        """
        A result that arrives after the window was closed is dropped.

        This is the dangling-window guard: without it, deliver would call back
        into the destroyed Addon Manager window during the Gtk draw cycle.
        """
        dispatch = AddonRefreshDispatch(self._apply)
        dispatch.cancel()  # window closed mid-refresh
        self.assertFalse(dispatch.alive)
        applied = dispatch.deliver([])  # the slow/failed 404 refresh completes
        self.assertFalse(applied)
        self.assertEqual(self.delivered, [])

    def test_subsequent_valid_refresh_still_works(self):
        """After a cancelled (failed) refresh, a fresh refresh delivers."""
        stale = AddonRefreshDispatch(self._apply)
        stale.cancel()
        stale.deliver([])  # dropped
        # A new refresh creates a new dispatch which delivers normally.
        fresh = AddonRefreshDispatch(self._apply)
        applied = fresh.deliver(["addon"])
        self.assertTrue(applied)
        self.assertEqual(self.delivered, [["addon"]])


if __name__ == "__main__":
    unittest.main()

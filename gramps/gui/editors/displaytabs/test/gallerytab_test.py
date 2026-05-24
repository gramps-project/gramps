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

"""Unittests for the GalleryTab display tab."""

# ------------------------
# Python modules
# ------------------------
import tempfile
import unittest
from unittest.mock import Mock

# ------------------------
# Gramps modules
# ------------------------
from gi.repository import GObject

from gramps.gen.db.utils import make_database
from gramps.gen.dbstate import DbState
from gramps.gui.editors.displaytabs import GalleryTab


# ------------------------------------------------------------
#
# TestGalleryTabCleanup
#
# ------------------------------------------------------------
class TestGalleryTabCleanup(unittest.TestCase):
    """
    Regression tests for the GalleryTab teardown path.
    """

    def _make_gallery(self):
        """
        Build a minimal GalleryTab against a fresh sqlite db.
        """
        dbstate = DbState()
        db = make_database("sqlite")
        tmpdir = tempfile.mkdtemp()
        db.load(tmpdir)
        dbstate.change_database(db)
        uistate = Mock()
        uistate.window = Mock()
        gallery = GalleryTab(dbstate, uistate, [], [])
        return gallery, db

    def test_clean_up_disconnects_selection_changed(self):
        """
        Regression for bug 13326.

        GalleryTab.clean_up() must disconnect the iconlist
        'selection-changed' signal handler before super().clean_up() deletes
        the iconlist attribute via track_ref_for_deletion. Otherwise a late
        selection-changed emission (which happens when the parent dialog
        tears down on Cancel, e.g. when the Forms addon hosts a GalleryTab)
        re-enters _selection_changed -> get_selected() ->
        self.iconlist.get_selected_items() and crashes with AttributeError:
        'GalleryTab' object has no attribute 'iconlist'.

        PyGObject prints but does not propagate exceptions raised inside a
        signal handler, so this test asserts on the connection state
        directly rather than trying to observe the AttributeError from an
        emit() call.
        """
        gallery, db = self._make_gallery()
        try:
            iconlist = gallery.iconlist
            signal_id, _detail = GObject.signal_parse_name(
                "selection-changed", iconlist, True
            )

            self.assertGreater(
                GObject.signal_handler_find(
                    iconlist,
                    GObject.SignalMatchType.ID,
                    signal_id,
                    0,
                    None,
                    None,
                    None,
                ),
                0,
                "Sanity: a 'selection-changed' handler should be wired "
                "during build_interface().",
            )

            gallery.clean_up()

            self.assertEqual(
                GObject.signal_handler_find(
                    iconlist,
                    GObject.SignalMatchType.ID,
                    signal_id,
                    0,
                    None,
                    None,
                    None,
                ),
                0,
                "Bug 13326: GalleryTab.clean_up() must disconnect the "
                "iconlist 'selection-changed' handler so a late emission "
                "cannot fire _selection_changed after self.iconlist has "
                "been deleted by track_ref_for_deletion.",
            )
        finally:
            db.close()


if __name__ == "__main__":
    unittest.main()

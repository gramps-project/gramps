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
import os
import tempfile
import unittest
import warnings
from unittest.mock import Mock

# ------------------------
# Gramps modules
# ------------------------
from gi.repository import GObject

from gramps.gen.db.utils import make_database
from gramps.gen.dbstate import DbState
from gramps.gui.editors.displaytabs import GalleryTab


def _has_gtk_display():
    """
    Return True only if a real Gtk display is available.

    The gramps CI exports GDK_BACKEND=- and runs without an X server, so
    constructing a Gtk.IconView "succeeds" against a NULL screen and then
    segfaults at process cleanup. Skip cleanly on those hosts; run when
    the test is invoked under xvfb-run or on a real desktop.
    """
    if not os.environ.get("DISPLAY"):
        return False
    if os.environ.get("GDK_BACKEND") == "-":
        return False
    try:
        import gi

        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk

        return bool(Gtk.init_check([])[0])
    except Exception:
        return False


_HAS_GTK_DISPLAY = _has_gtk_display()


# ------------------------------------------------------------
#
# TestGalleryTabCleanup
#
# ------------------------------------------------------------
@unittest.skipUnless(
    _HAS_GTK_DISPLAY,
    "needs a real Gtk display (run under xvfb-run); "
    "gramps CI sets GDK_BACKEND=- and constructing a Gtk.IconView "
    "against a NULL screen segfaults at process cleanup.",
)
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

    def test_clean_up_after_iconlist_destroyed_emits_no_warning(self):
        """
        Regression guard for the warning commit 37395da262 silenced.

        That 2023 commit removed the disconnect in clean_up() because GTK
        emitted a critical when the disconnect ran on an iconlist whose
        underlying GObject had already been disposed (the normal close
        path). Restoring the disconnect for bug 13326 must not bring that
        warning back. The fix gates the disconnect with
        GObject.signal_handler_is_connected, which returns False on a
        disposed widget.

        Simulate the normal-close path by destroying the iconlist widget
        before clean_up(), then assert that no PyGObject warning of the
        shape ``instance '...' has no handler with id '...'`` is raised.
        PyGObject promotes the underlying GObject critical to a Python
        Warning, so warnings.catch_warnings is sufficient.
        """
        gallery, db = self._make_gallery()
        try:
            gallery.iconlist.destroy()

            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                gallery.clean_up()

            stale_handler_warnings = [
                w for w in caught if "has no handler with id" in str(w.message)
            ]
            self.assertEqual(
                stale_handler_warnings,
                [],
                "GalleryTab.clean_up() must stay silent when the iconlist "
                "widget has already been disposed (the case commit "
                "37395da262 was working around). Got: %r"
                % [str(w.message) for w in stale_handler_warnings],
            )
        finally:
            db.close()


if __name__ == "__main__":
    unittest.main()

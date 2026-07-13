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
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Tests for the 'New' button logic added to the selector classes.

These tests bypass GTK initialisation by instantiating selector objects
via ``object.__new__`` and injecting mock attributes, so they run without
a display.  When the GTK widget stack cannot be imported (e.g. a GTK4
environment where ``Gtk.IconSize.MENU`` is absent), the test cases are
skipped rather than erroring.
"""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
import unittest
from unittest.mock import MagicMock, patch

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
try:
    from gramps.gui.selectors.baseselector import BaseSelector
    from gramps.gui.selectors.selectplace import SelectPlace
    from gramps.gui.selectors.selectsource import SelectSource
    from gramps.gui.selectors.selectcitation import SelectCitation

    _IMPORT_OK = True
except Exception:
    _IMPORT_OK = False

_SKIP_MSG = "GTK widget stack unavailable (likely GTK4 environment)"


def _make_selector(cls):
    """
    Return a bare instance of *cls* without calling ``__init__``.

    A ``new_button`` mock and the minimum attributes needed for the
    'New' button methods are injected onto the instance.

    :param cls: A BaseSelector subclass.
    :type cls: type
    :returns: Partially-initialised selector instance.
    :rtype: cls
    """
    sel = object.__new__(cls)
    sel.new_button = MagicMock()
    sel.dbstate = MagicMock()
    sel.uistate = MagicMock()
    sel.track = []
    sel.build_tree = MagicMock()
    sel.goto_handle = MagicMock()
    sel.window = MagicMock()
    sel.model = None
    sel.tree = None
    return sel


# -------------------------------------------------------------------------
#
# TestEnableNewButton
#
# -------------------------------------------------------------------------
@unittest.skipUnless(_IMPORT_OK, _SKIP_MSG)
class TestEnableNewButton(unittest.TestCase):
    """enable_new_button() must call show() on new_button."""

    def test_enable_calls_show(self):
        """enable_new_button shows the button."""
        sel = _make_selector(SelectPlace)
        sel.enable_new_button()
        sel.new_button.show.assert_called_once()

    def test_base_cb_new_button_clicked_is_noop(self):
        """BaseSelector.cb_new_button_clicked does nothing by default."""
        sel = _make_selector(SelectPlace)
        BaseSelector.cb_new_button_clicked(sel, MagicMock())


# -------------------------------------------------------------------------
#
# TestSelectPlaceNewButton
#
# -------------------------------------------------------------------------
@unittest.skipUnless(_IMPORT_OK, _SKIP_MSG)
class TestSelectPlaceNewButton(unittest.TestCase):
    """Tests for SelectPlace 'New' button callbacks."""

    def test_cb_after_new_saved_rebuilds_tree(self):
        """cb_after_new_saved rebuilds the tree."""
        sel = _make_selector(SelectPlace)
        place = MagicMock()
        place.get_handle.return_value = "P0001"
        sel.cb_after_new_saved(place)
        sel.build_tree.assert_called_once()

    def test_cb_after_new_saved_navigates_to_handle(self):
        """cb_after_new_saved navigates to the new place's handle."""
        sel = _make_selector(SelectPlace)
        place = MagicMock()
        place.get_handle.return_value = "P0001"
        sel.cb_after_new_saved(place)
        sel.goto_handle.assert_called_once_with("P0001")

    def test_cb_new_button_clicked_opens_editor(self):
        """cb_new_button_clicked opens EditPlace."""
        sel = _make_selector(SelectPlace)
        with patch("gramps.gui.selectors.selectplace.EditPlace") as MockEdit:
            sel.cb_new_button_clicked(MagicMock())
            MockEdit.assert_called_once()

    def test_cb_new_button_clicked_swallows_window_active_error(self):
        """cb_new_button_clicked ignores WindowActiveError (editor already open)."""
        from gramps.gen.errors import WindowActiveError

        sel = _make_selector(SelectPlace)
        with patch(
            "gramps.gui.selectors.selectplace.EditPlace",
            side_effect=WindowActiveError("already open"),
        ):
            sel.cb_new_button_clicked(MagicMock())


# -------------------------------------------------------------------------
#
# TestSelectSourceNewButton
#
# -------------------------------------------------------------------------
@unittest.skipUnless(_IMPORT_OK, _SKIP_MSG)
class TestSelectSourceNewButton(unittest.TestCase):
    """Tests for SelectSource 'New' button callbacks."""

    def test_cb_after_new_saved_rebuilds_tree(self):
        """cb_after_new_saved rebuilds the tree."""
        sel = _make_selector(SelectSource)
        source = MagicMock()
        source.get_handle.return_value = "S0001"
        sel.cb_after_new_saved(source)
        sel.build_tree.assert_called_once()

    def test_cb_after_new_saved_navigates_to_handle(self):
        """cb_after_new_saved navigates to the new source's handle."""
        sel = _make_selector(SelectSource)
        source = MagicMock()
        source.get_handle.return_value = "S0001"
        sel.cb_after_new_saved(source)
        sel.goto_handle.assert_called_once_with("S0001")

    def test_cb_new_button_clicked_opens_editor(self):
        """cb_new_button_clicked opens EditSource."""
        sel = _make_selector(SelectSource)
        with patch("gramps.gui.selectors.selectsource.EditSource") as MockEdit:
            sel.cb_new_button_clicked(MagicMock())
            MockEdit.assert_called_once()

    def test_cb_new_button_clicked_swallows_window_active_error(self):
        """cb_new_button_clicked ignores WindowActiveError."""
        from gramps.gen.errors import WindowActiveError

        sel = _make_selector(SelectSource)
        with patch(
            "gramps.gui.selectors.selectsource.EditSource",
            side_effect=WindowActiveError("already open"),
        ):
            sel.cb_new_button_clicked(MagicMock())


# -------------------------------------------------------------------------
#
# TestSelectCitationNewButton
#
# -------------------------------------------------------------------------
@unittest.skipUnless(_IMPORT_OK, _SKIP_MSG)
class TestSelectCitationNewButton(unittest.TestCase):
    """Tests for SelectCitation 'New' button callbacks."""

    def test_cb_after_new_saved_rebuilds_tree(self):
        """cb_after_new_saved rebuilds the tree."""
        sel = _make_selector(SelectCitation)
        obj = MagicMock()
        obj.get_handle.return_value = "C0001"
        sel.cb_after_new_saved(obj)
        sel.build_tree.assert_called_once()

    def test_cb_after_new_saved_navigates_to_handle(self):
        """cb_after_new_saved navigates to the new object's handle."""
        sel = _make_selector(SelectCitation)
        obj = MagicMock()
        obj.get_handle.return_value = "C0001"
        sel.cb_after_new_saved(obj)
        sel.goto_handle.assert_called_once_with("C0001")

    def test_new_source_opens_editor(self):
        """_new_source opens EditSource."""
        sel = _make_selector(SelectCitation)
        with patch("gramps.gui.selectors.selectcitation.EditSource") as MockEdit:
            sel._new_source()
            MockEdit.assert_called_once()

    def test_new_source_swallows_window_active_error(self):
        """_new_source ignores WindowActiveError."""
        from gramps.gen.errors import WindowActiveError

        sel = _make_selector(SelectCitation)
        with patch(
            "gramps.gui.selectors.selectcitation.EditSource",
            side_effect=WindowActiveError("already open"),
        ):
            sel._new_source()

    def test_new_citation_opens_editor(self):
        """_new_citation opens EditCitation."""
        sel = _make_selector(SelectCitation)
        with patch("gramps.gui.selectors.selectcitation.EditCitation") as MockEdit:
            sel._new_citation()
            MockEdit.assert_called_once()

    def test_new_citation_swallows_window_active_error(self):
        """_new_citation ignores WindowActiveError."""
        from gramps.gen.errors import WindowActiveError

        sel = _make_selector(SelectCitation)
        with patch(
            "gramps.gui.selectors.selectcitation.EditCitation",
            side_effect=WindowActiveError("already open"),
        ):
            sel._new_citation()

    def test_cb_new_button_clicked_new_source_path(self):
        """cb_new_button_clicked calls _new_source when user picks 'New Source'."""
        sel = _make_selector(SelectCitation)
        sel._new_source = MagicMock()
        sel._new_citation = MagicMock()
        with patch("gramps.gui.selectors.selectcitation.Gtk.MessageDialog") as MockDlg:
            instance = MockDlg.return_value
            instance.run.return_value = 1
            sel.cb_new_button_clicked(MagicMock())
        sel._new_source.assert_called_once()
        sel._new_citation.assert_not_called()

    def test_cb_new_button_clicked_new_citation_path(self):
        """cb_new_button_clicked calls _new_citation when user picks 'New Citation'."""
        sel = _make_selector(SelectCitation)
        sel._new_source = MagicMock()
        sel._new_citation = MagicMock()
        with patch("gramps.gui.selectors.selectcitation.Gtk.MessageDialog") as MockDlg:
            instance = MockDlg.return_value
            instance.run.return_value = 2
            sel.cb_new_button_clicked(MagicMock())
        sel._new_citation.assert_called_once()
        sel._new_source.assert_not_called()

    def test_cb_new_button_clicked_cancel(self):
        """cb_new_button_clicked does nothing when user cancels."""
        from gi.repository import Gtk as _Gtk

        sel = _make_selector(SelectCitation)
        sel._new_source = MagicMock()
        sel._new_citation = MagicMock()
        with patch("gramps.gui.selectors.selectcitation.Gtk.MessageDialog") as MockDlg:
            instance = MockDlg.return_value
            instance.run.return_value = _Gtk.ResponseType.CANCEL
            sel.cb_new_button_clicked(MagicMock())
        sel._new_source.assert_not_called()
        sel._new_citation.assert_not_called()


if __name__ == "__main__":
    unittest.main()

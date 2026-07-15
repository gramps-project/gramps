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

"""Tests for ManagedWindow's OK/Cancel shortcut wiring."""

# python3 -m unittest gramps.gui.test.managedwindow_test -v

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
import os
import unittest
from unittest.mock import MagicMock

os.environ.setdefault("GDK_BACKEND", "-")
os.environ.setdefault("LANG", "en_US.utf-8")

import gi

gi.require_version("Gtk", "3.0")

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk
from gramps.gui.managedwindow import ManagedWindow

DEFAULT_ACCELS = {"app.dialog-ok": "<Alt>o", "app.dialog-cancel": "<Alt>c"}


def _make_dialog(ok_label="_OK", cancel_label="_Cancel"):
    """A mock standing in for a Gtk.Dialog, with mock OK/Cancel buttons
    registered the way glade's <action-widgets> would wire them up.
    Real Gtk widgets can't be instantiated under this project's headless
    (GDK_BACKEND=-) test convention, so behavior is verified against
    these mocks instead.
    """
    ok_button = MagicMock(name="ok_button")
    ok_button.get_label.return_value = ok_label
    cancel_button = MagicMock(name="cancel_button")
    cancel_button.get_label.return_value = cancel_label

    dialog = MagicMock(spec=Gtk.Dialog)
    buttons_by_response = {
        Gtk.ResponseType.OK: ok_button,
        Gtk.ResponseType.CANCEL: cancel_button,
    }
    dialog.get_widget_for_response.side_effect = buttons_by_response.get
    return dialog, ok_button, cancel_button


def _make_managed_window(dialog, current_accels):
    """A ManagedWindow with only the attributes _wire_dialog_accels needs."""
    managed_window = ManagedWindow.__new__(ManagedWindow)
    managed_window.window = dialog
    uimanager = MagicMock()
    uimanager.default_accels = DEFAULT_ACCELS
    uimanager.get_accel.side_effect = lambda action_id: current_accels.get(
        action_id, DEFAULT_ACCELS.get(action_id, "")
    )
    managed_window.uistate = MagicMock(uimanager=uimanager)
    return managed_window


#
# WireDialogAccelsTest
#
class WireDialogAccelsTest(unittest.TestCase):
    def test_default_accel_leaves_mnemonic_and_tooltip_untouched(self):
        dialog, ok_button, cancel_button = _make_dialog()
        _make_managed_window(dialog, {})._wire_dialog_accels()
        ok_button.set_label.assert_not_called()
        cancel_button.set_label.assert_not_called()
        ok_button.set_tooltip_text.assert_not_called()

    def test_custom_accel_strips_mnemonic_and_sets_tooltip(self):
        dialog, ok_button, cancel_button = _make_dialog()
        current = {"app.dialog-ok": "F9"}
        _make_managed_window(dialog, current)._wire_dialog_accels()
        ok_button.set_label.assert_called_once_with("OK")
        (tooltip,), _kwargs = ok_button.set_tooltip_text.call_args
        self.assertIn("F9", tooltip)
        ok_button.add_accelerator.assert_called_once()
        # Cancel was not customized, so it is left alone.
        cancel_button.set_label.assert_not_called()
        cancel_button.set_tooltip_text.assert_not_called()

    def test_cleared_accel_strips_mnemonic_with_no_tooltip(self):
        dialog, ok_button, _cancel_button = _make_dialog()
        current = {"app.dialog-ok": ""}
        _make_managed_window(dialog, current)._wire_dialog_accels()
        ok_button.set_label.assert_called_once_with("OK")
        ok_button.set_tooltip_text.assert_called_once_with(None)
        ok_button.add_accelerator.assert_not_called()

    def test_non_dialog_window_is_a_no_op(self):
        managed_window = ManagedWindow.__new__(ManagedWindow)
        managed_window.window = MagicMock(spec=Gtk.Window)
        managed_window.uistate = MagicMock()
        managed_window._wire_dialog_accels()
        managed_window.uistate.uimanager.get_accel.assert_not_called()


if __name__ == "__main__":
    unittest.main()

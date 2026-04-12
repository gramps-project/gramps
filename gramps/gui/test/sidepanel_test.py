#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2025 Doug Blank
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

"""Tests for gramps/gui/sidepanel.py"""

import unittest
from unittest.mock import MagicMock, patch, call

from gramps.gen.plug import START, END


# -------------------------------------------------------------------------
#
# SidePanelManagerTest class
#
# -------------------------------------------------------------------------
class SidePanelManagerTest(unittest.TestCase):
    """Tests for SidePanelManager."""

    def setUp(self):
        """Set up a SidePanelManager with a mock viewmanager and GTK mocks."""
        gtk_patcher = patch.dict(
            "sys.modules",
            {
                "gi": MagicMock(),
                "gi.repository": MagicMock(),
                "gi.repository.Gtk": MagicMock(),
                "gi.repository.GObject": MagicMock(),
            },
        )
        gtk_patcher.start()
        self.addCleanup(gtk_patcher.stop)

        from gramps.gui.sidepanel import SidePanelManager

        self.viewmanager = MagicMock()
        self.manager = SidePanelManager(self.viewmanager)
        self.manager.pages = {}
        self.manager._active_page = None
        self.manager.active_cat = None
        self.manager.active_view = None

    def test_has_plugins_empty(self):
        """has_plugins returns False when no plugins loaded."""
        self.assertFalse(self.manager.has_plugins())

    def test_has_plugins_with_panel(self):
        """has_plugins returns True after a panel is added."""
        panel = MagicMock()
        panel.get_top.return_value = MagicMock()
        self.manager.stack.get_children.return_value = []
        self.manager.add("Test", panel, END)
        self.assertTrue(self.manager.has_plugins())

    def test_view_changed_updates_state(self):
        """view_changed stores cat and view numbers."""
        self.manager.stack.get_visible_child_name.return_value = None
        self.manager.view_changed(2, 3)
        self.assertEqual(self.manager.active_cat, 2)
        self.assertEqual(self.manager.active_view, 3)

    def test_view_changed_delegates_to_active_panel(self):
        """view_changed calls view_changed on the active panel."""
        panel = MagicMock()
        self.manager.pages["MyPanel"] = panel
        self.manager.stack.get_visible_child_name.return_value = "MyPanel"
        self.manager.view_changed(1, 0)
        panel.view_changed.assert_called_once_with(1, 0)

    def test_view_changed_no_active_panel(self):
        """view_changed does not raise when no panel is active."""
        self.manager.stack.get_visible_child_name.return_value = "Missing"
        self.manager.view_changed(0, 0)  # should not raise

    def test_on_database_changed_delegates(self):
        """_on_database_changed calls db_changed on the visible panel."""
        panel = MagicMock()
        db = MagicMock()
        self.manager.pages["P"] = panel
        self.manager.stack.get_visible_child_name.return_value = "P"
        self.manager._on_database_changed(db)
        panel.db_changed.assert_called_once_with(db)

    def test_on_database_changed_no_panel(self):
        """_on_database_changed does not raise when no panel is visible."""
        self.manager.stack.get_visible_child_name.return_value = "Missing"
        self.manager._on_database_changed(MagicMock())  # should not raise

    def test_add_start_order_prepends(self):
        """add() with START order prepends the entry."""
        panel = MagicMock()
        panel.get_top.return_value = MagicMock()
        self.manager.stack.get_children.return_value = []
        self.manager.add("First", panel, START)
        self.manager.select_button.prepend.assert_called_once_with(
            id="First", text="First"
        )
        self.manager.select_button.set_active_id.assert_called_once_with("First")

    def test_add_end_order_appends(self):
        """add() with END order appends the entry."""
        panel = MagicMock()
        panel.get_top.return_value = MagicMock()
        self.manager.stack.get_children.return_value = []
        self.manager.add("Last", panel, END)
        self.manager.select_button.append.assert_called_once_with(
            id="Last", text="Last"
        )

    def test_cb_switch_page_deactivates_old(self):
        """cb_switch_page calls inactive() on the previously active panel."""
        old_panel = MagicMock()
        new_panel = MagicMock()
        self.manager.pages = {"Old": old_panel, "New": new_panel}
        self.manager._active_page = "Old"
        self.manager.active_cat = 0
        self.manager.active_view = 1
        self.manager.stack.get_visible_child_name.return_value = "New"
        self.manager.cb_switch_page(self.manager.stack, MagicMock())
        old_panel.inactive.assert_called_once()
        new_panel.active.assert_called_once_with(0, 1)

    def test_cb_switch_page_none_title(self):
        """cb_switch_page returns early when visible child name is None."""
        self.manager._active_page = None
        self.manager.stack.get_visible_child_name.return_value = None
        self.manager.cb_switch_page(self.manager.stack, MagicMock())
        # No error, no panel calls


# -------------------------------------------------------------------------
#
# BaseSidePanelTest class
#
# -------------------------------------------------------------------------
class BaseSidePanelTest(unittest.TestCase):
    """Tests for BaseSidePanel interface contract."""

    def setUp(self):
        """Patch GTK so BaseSidePanel can be imported without a display."""
        gtk_patcher = patch.dict(
            "sys.modules",
            {
                "gi": MagicMock(),
                "gi.repository": MagicMock(),
                "gi.repository.Gtk": MagicMock(),
                "gi.repository.GObject": MagicMock(),
            },
        )
        gtk_patcher.start()
        self.addCleanup(gtk_patcher.stop)

    def test_init_raises(self):
        """BaseSidePanel.__init__ raises NotImplementedError."""
        from gramps.gui.sidepanel import BaseSidePanel

        with self.assertRaises(NotImplementedError):
            BaseSidePanel(MagicMock(), MagicMock())

    def test_get_top_raises(self):
        """BaseSidePanel.get_top raises NotImplementedError."""
        from gramps.gui.sidepanel import BaseSidePanel

        panel = BaseSidePanel.__new__(BaseSidePanel)
        with self.assertRaises(NotImplementedError):
            panel.get_top()

    def test_view_changed_raises(self):
        """BaseSidePanel.view_changed raises NotImplementedError."""
        from gramps.gui.sidepanel import BaseSidePanel

        panel = BaseSidePanel.__new__(BaseSidePanel)
        with self.assertRaises(NotImplementedError):
            panel.view_changed(0, 0)

    def test_db_changed_is_noop(self):
        """BaseSidePanel.db_changed is a no-op by default."""
        from gramps.gui.sidepanel import BaseSidePanel

        panel = BaseSidePanel.__new__(BaseSidePanel)
        panel.db_changed(MagicMock())  # should not raise

    def test_active_is_noop(self):
        """BaseSidePanel.active is a no-op by default."""
        from gramps.gui.sidepanel import BaseSidePanel

        panel = BaseSidePanel.__new__(BaseSidePanel)
        panel.active(0, 0)  # should not raise

    def test_inactive_is_noop(self):
        """BaseSidePanel.inactive is a no-op by default."""
        from gramps.gui.sidepanel import BaseSidePanel

        panel = BaseSidePanel.__new__(BaseSidePanel)
        panel.inactive()  # should not raise


if __name__ == "__main__":
    unittest.main()

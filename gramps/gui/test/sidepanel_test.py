#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026 Doug Blank
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
from unittest.mock import MagicMock, patch

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
        self.manager.add("plugin.test", "Test", panel, END)
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
        self.manager.pages["plugin.mypanel"] = panel
        self.manager.stack.get_visible_child_name.return_value = "plugin.mypanel"
        self.manager.view_changed(1, 0)
        panel.view_changed.assert_called_once_with(1, 0)

    def test_view_changed_no_active_panel(self):
        """view_changed does not raise when no panel is active."""
        self.manager.stack.get_visible_child_name.return_value = "plugin.missing"
        self.manager.view_changed(0, 0)  # should not raise

    def test_on_database_changed_notifies_all_panels(self):
        """_on_database_changed calls db_changed on every loaded panel."""
        panel_a = MagicMock()
        panel_b = MagicMock()
        db = MagicMock()
        self.manager.pages["plugin.a"] = panel_a
        self.manager.pages["plugin.b"] = panel_b
        self.manager._on_database_changed(db)
        panel_a.db_changed.assert_called_once_with(db)
        panel_b.db_changed.assert_called_once_with(db)

    def test_on_database_changed_no_panels(self):
        """_on_database_changed does not raise when no panels are loaded."""
        self.manager._on_database_changed(MagicMock())  # should not raise

    def test_add_start_order_prepends(self):
        """add() with START order prepends the entry using plugin_id."""
        panel = MagicMock()
        panel.get_top.return_value = MagicMock()
        self.manager.stack.get_children.return_value = []
        self.manager.add("plugin.first", "First", panel, START)
        self.manager.select_button.prepend.assert_called_once_with(
            id="plugin.first", text="First"
        )
        self.manager.select_button.set_active_id.assert_called_once_with("plugin.first")

    def test_add_end_order_appends(self):
        """add() with END order appends the entry using plugin_id."""
        panel = MagicMock()
        panel.get_top.return_value = MagicMock()
        self.manager.stack.get_children.return_value = []
        self.manager.add("plugin.last", "Last", panel, END)
        self.manager.select_button.append.assert_called_once_with(
            id="plugin.last", text="Last"
        )

    def test_add_two_panels_shows_selector(self):
        """add() shows the selector combo when a second panel is added."""
        self.manager.stack.get_children.return_value = [MagicMock(), MagicMock()]
        panel = MagicMock()
        panel.get_top.return_value = MagicMock()
        self.manager.add("plugin.second", "Second", panel, END)
        self.manager.select_button.show_all.assert_called()

    def test_add_uses_plugin_id_as_page_key(self):
        """add() stores the panel keyed by plugin_id, not by display title."""
        panel = MagicMock()
        panel.get_top.return_value = MagicMock()
        self.manager.stack.get_children.return_value = []
        self.manager.add("plugin.unique_id", "Display Title", panel, END)
        self.assertIn("plugin.unique_id", self.manager.pages)
        self.assertNotIn("Display Title", self.manager.pages)

    def test_cb_switch_page_deactivates_old(self):
        """cb_switch_page calls inactive() on the previously active panel."""
        old_panel = MagicMock()
        new_panel = MagicMock()
        self.manager.pages = {"plugin.old": old_panel, "plugin.new": new_panel}
        self.manager._active_page = "plugin.old"
        self.manager.active_cat = 0
        self.manager.active_view = 1
        self.manager.stack.get_visible_child_name.return_value = "plugin.new"
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

        from gramps.gui.sidepanel import BaseSidePanel

        class _ConcretePanel(BaseSidePanel):
            """Minimal concrete subclass for testing optional default methods."""

            def __init__(self, dbstate, uistate):
                pass

            def get_top(self):
                pass

            def view_changed(self, cat_num, view_num):
                pass

        self.BaseSidePanel = BaseSidePanel
        self.ConcretePanel = _ConcretePanel

    def test_cannot_instantiate_directly(self):
        """BaseSidePanel cannot be instantiated — it has abstract methods."""
        with self.assertRaises(TypeError):
            self.BaseSidePanel(MagicMock(), MagicMock())

    def test_subclass_missing_get_top_raises(self):
        """Subclass that omits get_top cannot be instantiated."""
        BaseSidePanel = self.BaseSidePanel

        class _Missing(BaseSidePanel):
            def __init__(self, dbstate, uistate):
                pass

            def view_changed(self, cat_num, view_num):
                pass

        with self.assertRaises(TypeError):
            _Missing(MagicMock(), MagicMock())

    def test_subclass_missing_view_changed_raises(self):
        """Subclass that omits view_changed cannot be instantiated."""
        BaseSidePanel = self.BaseSidePanel

        class _Missing(BaseSidePanel):
            def __init__(self, dbstate, uistate):
                pass

            def get_top(self):
                pass

        with self.assertRaises(TypeError):
            _Missing(MagicMock(), MagicMock())

    def test_db_changed_is_noop(self):
        """BaseSidePanel.db_changed is a no-op by default."""
        panel = self.ConcretePanel(MagicMock(), MagicMock())
        panel.db_changed(MagicMock())  # should not raise

    def test_active_is_noop(self):
        """BaseSidePanel.active is a no-op by default."""
        panel = self.ConcretePanel(MagicMock(), MagicMock())
        panel.active(0, 0)  # should not raise

    def test_inactive_is_noop(self):
        """BaseSidePanel.inactive is a no-op by default."""
        panel = self.ConcretePanel(MagicMock(), MagicMock())
        panel.inactive()  # should not raise


if __name__ == "__main__":
    unittest.main()

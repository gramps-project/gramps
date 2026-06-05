#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Himanshu Gohel
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

import gi
import unittest
from unittest.mock import MagicMock, patch

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from gramps.gui.dbman import DbManager, NAME_COL


class TestDbManSelection(unittest.TestCase):
    def setUp(self):
        # Mocking the dependencies of DbManager to avoid initializing the full GUI
        self.uistate = MagicMock()
        self.uistate.gwm = MagicMock()
        self.uistate.gwm.get_item_from_id.return_value = None
        self.uistate.gwm.add_item.return_value = []
        self.uistate.pulse_progressbar = MagicMock()
        self.dbstate = MagicMock()
        self.viewmanager = MagicMock()

        # Patch Glade and PersistentTreeView to avoid GTK errors during init
        with (
            patch("gramps.gui.dbman.Glade"),
            patch("gramps.gui.dbman.PersistentTreeView"),
            patch("gramps.gui.dbman.User"),
            patch("gramps.gui.dbman.ManagedWindow.setup_configs"),
            patch("gramps.gui.dbman.DbManager._select_default"),
        ):
            self.dbman = DbManager(self.uistate, self.dbstate, self.viewmanager)

        # Mock the model and selection
        self.dbman.model = MagicMock(spec=Gtk.TreeStore)
        self.dbman.selection = MagicMock()
        self.dbman.selection.get_selected.return_value = (None, None)
        self.dbman.dblist = MagicMock()

    def test_select_next_after_deletion_happy_path(self):
        """
        Test that the correct item is selected when a successor exists.
        """
        # Setup model: Item A, Item B, Item C
        # We simulate the model's behavior with a list of values
        mock_iters = [MagicMock(), MagicMock(), MagicMock()]
        self.dbman.model.get_iter_first.return_value = mock_iters[0]
        self.dbman.model.iter_next.side_effect = [mock_iters[1], mock_iters[2], None]

        # Mock get_value for NAME_COL
        self.dbman.model.get_value.side_effect = lambda it, col: (
            {mock_iters[0]: "Tree A", mock_iters[1]: "Tree B", mock_iters[2]: "Tree C"}[
                it
            ]
            if col == NAME_COL
            else None
        )

        # Mock get_path with deterministic strings
        path_map = {
            mock_iters[0]: "path_a",
            mock_iters[1]: "path_b",
            mock_iters[2]: "path_c",
        }
        self.dbman.model.get_path.side_effect = lambda it: path_map[it]

        # Act: Select "Tree B"
        self.dbman._select_next_after_deletion("Tree B")

        # Assert
        self.dbman.selection.select_path.assert_called_with("path_b")

    def test_select_next_after_deletion_only_item(self):
        """
        Test that nothing is selected when next_item_name is None.
        """
        self.dbman._select_next_after_deletion(None)
        self.dbman.selection.select_path.assert_not_called()

    def test_select_next_after_deletion_model_none(self):
        """
        Test that the method returns gracefully when self.model is None.
        """
        self.dbman.model = None
        self.dbman._select_next_after_deletion("Some Tree")
        self.dbman.selection.select_path.assert_not_called()


if __name__ == "__main__":
    unittest.main()

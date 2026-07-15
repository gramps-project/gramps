#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026       The Gramps Project
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

"""Unittest for restartstate.py"""

import json
import os
import unittest
from unittest.mock import Mock

from ..restartstate import capture_state, write_state_file
from ..editors.editprimary import EditPrimary


def make_history(handle):
    history = Mock()
    history.present.return_value = handle
    return history


def make_editor(object_type, handle):
    obj = Mock()
    obj.get_handle.return_value = handle
    obj.__class__ = type(object_type, (), {})
    editor = Mock(spec=EditPrimary)
    editor.obj = obj
    return editor


class CaptureStateTest(unittest.TestCase):
    def setUp(self):
        self.dbstate = Mock()
        self.uistate = Mock()
        self.uistate.history_lookup = {}
        self.uistate.gwm.id2item = {}
        self.viewmanager = Mock()
        self.viewmanager.get_active_view_id.return_value = "PersonView"

    def test_tree_is_none_when_no_db_open(self):
        self.dbstate.is_open.return_value = False
        state = capture_state(self.dbstate, self.uistate, self.viewmanager)
        self.assertIsNone(state["tree"])

    def test_tree_is_save_path_when_db_open(self):
        self.dbstate.is_open.return_value = True
        self.dbstate.db.get_save_path.return_value = "/home/user/.gramps/tree1"
        state = capture_state(self.dbstate, self.uistate, self.viewmanager)
        self.assertEqual(state["tree"], "/home/user/.gramps/tree1")

    def test_active_view_captured(self):
        self.dbstate.is_open.return_value = False
        state = capture_state(self.dbstate, self.uistate, self.viewmanager)
        self.assertEqual(state["active_view"], "PersonView")

    def test_selected_captures_only_nav_group_zero_with_a_handle(self):
        self.dbstate.is_open.return_value = False
        self.uistate.history_lookup = {
            ("Person", 0): make_history("person-handle"),
            ("Person", 1): make_history("other-group-handle"),
            ("Family", 0): make_history(None),
        }
        state = capture_state(self.dbstate, self.uistate, self.viewmanager)
        self.assertEqual(state["selected"], {"Person": "person-handle"})

    def test_open_editors_captures_only_editprimary_instances_with_a_handle(self):
        self.dbstate.is_open.return_value = False
        unsaved_editor = make_editor("Person", None)
        saved_editor = make_editor("Family", "family-handle")
        self.uistate.gwm.id2item = {
            "id(unsaved)": unsaved_editor,
            "family-handle": saved_editor,
            "other-window": Mock(),
        }
        state = capture_state(self.dbstate, self.uistate, self.viewmanager)
        self.assertEqual(
            state["open_editors"],
            [{"object_type": "Family", "handle": "family-handle"}],
        )


class WriteStateFileTest(unittest.TestCase):
    def test_round_trips_through_json(self):
        state = {"version": 1, "language": "fr_FR.UTF-8", "tree": "My Tree"}
        path = write_state_file(state)
        self.addCleanup(os.remove, path)
        with open(path, encoding="utf-8") as state_file:
            self.assertEqual(json.load(state_file), state)


if __name__ == "__main__":
    unittest.main()

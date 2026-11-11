#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026       The Gramps Developers
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
Unit tests for :mod:`gramps.gui.editors.dependentsave`: reference and
secondary editors taking part in the "resolve dependent child editors
before a parent commits" cascade (Mantis #12008).

The editors are real :class:`EditReference` / :class:`EditSecondary`
instances on a real database. Only the window plumbing is stubbed: the
window, ``ManagedWindow.close`` (which needs a live window manager) and the
window tree the cascade walks. The "Save Changes?" dialog is replaced by a stand-in that
answers as the test says.
"""

import tempfile
import unittest
from types import SimpleNamespace
from typing import Any
from unittest.mock import Mock, patch

from gramps.gen.db.utils import make_database
from gramps.gen.dbstate import DbState
from gi.repository import Gdk

from gramps.gen.lib import Address, Place, PlaceRef
from gramps.gui.managedwindow import ManagedWindow
from gramps.gui.editors.editreference import EditReference
from gramps.gui.editors.editsecondary import EditSecondary

DIALOG = "gramps.gui.editors.dependentsave.SaveDialog"
CONFIG = "gramps.gui.editors.dependentsave.config"


# -------------------------------------------------------------------------
#
# MockWindow
#
# -------------------------------------------------------------------------
class MockWindow:
    """The few Gtk.Window calls ManagedWindow makes during setup."""

    def set_transient_for(self, *args: Any, **kwargs: Any) -> None:
        """
        :param args: Ignored.
        :param kwargs: Ignored.
        """

    def show_all(self) -> None:
        """Do nothing."""


class _StubEditorMixin:
    """
    Window plumbing shared by the stand-in editors. The OK handler records
    the save, hands the result to the parent like the real editors do, then
    closes. ``result`` keeps the completion callback, which the editor
    clears when it closes.
    """

    opened: bool
    saves: int
    result: Any

    def _stub_init(self, tree: Any = None) -> None:
        """
        :param tree: The window-tree node returned for this editor, or None
            for an editor with no children.
        """
        self.opened = True
        self.saves = 0
        self.uistate = SimpleNamespace(
            gwm=SimpleNamespace(get_item_from_track=lambda track: tree or self)
        )
        self._wire_ok_button(Mock(), self.ok)  # type: ignore[attr-defined]

    def set_tree(self, tree: Any) -> None:
        """
        :param tree: The window-tree node to return for this editor.
        """
        self.uistate.gwm.get_item_from_track = lambda track: tree


def _close_window(window: Any, *args: Any) -> None:
    """
    Stand in for ManagedWindow.close, which needs a live window manager.

    :param window: The window being closed.
    :param args: Ignored.
    """
    window.opened = False


# -------------------------------------------------------------------------
#
# RefEditor
#
# -------------------------------------------------------------------------
class RefEditor(_StubEditorMixin, EditReference):
    """An EditReference on a Place and a PlaceRef."""

    def __init__(self, dbstate: DbState, place: Any, ref: Any, update: Any) -> None:
        """
        :param dbstate: The database state.
        :param place: The referenced place.
        :param ref: The place reference being edited.
        :param update: The completion callback, or None.
        """
        self.window = MockWindow()
        self.result = update
        EditReference.__init__(self, dbstate, None, [], place, ref, update)
        self._stub_init()

    def build_menu_names(self, obj: Any) -> tuple[str, None]:
        """
        :param obj: Ignored.
        :returns: Window menu labels.
        """
        return ("ref", None)

    def ok(self, *args: Any) -> None:
        """
        :param args: Ignored.
        """
        self.saves += 1
        if self.update:
            self.update(self.source_ref, self.source)
        self.close()


# -------------------------------------------------------------------------
#
# SecondaryEditor
#
# -------------------------------------------------------------------------
class SecondaryEditor(_StubEditorMixin, EditSecondary):
    """An EditSecondary on an Address."""

    def __init__(self, dbstate: DbState, addr: Any, callback: Any) -> None:
        """
        :param dbstate: The database state.
        :param addr: The address being edited.
        :param callback: The completion callback, or None.
        """
        self.window = MockWindow()
        self.result = callback
        EditSecondary.__init__(self, dbstate, None, [], addr, callback)
        self._stub_init()

    def build_menu_names(self, obj: Any) -> tuple[str, None]:
        """
        :param obj: Ignored.
        :returns: Window menu labels.
        """
        return ("secondary", None)

    def ok(self, *args: Any) -> None:
        """
        :param args: Ignored.
        """
        self.saves += 1
        if self.callback:
            self.callback(self.obj)
        self.close()


def _answer(choice: str) -> Any:
    """
    Build a stand-in for SaveDialog that answers with ``choice``.

    :param choice: "save", "discard" or "cancel".
    :returns: A callable with SaveDialog's signature.
    """

    def dialog(msg1: str, msg2: str, discard: Any, save: Any, parent: Any = None):
        if choice == "save":
            save()
        elif choice == "discard":
            discard()

    return dialog


# -------------------------------------------------------------------------
#
# DependentSaveTest
#
# -------------------------------------------------------------------------
class DependentSaveTest(unittest.TestCase):
    """Reference and secondary editors in the save cascade."""

    tmpdir: tempfile.TemporaryDirectory
    db: Any
    dbstate: DbState
    config: Any

    @classmethod
    def setUpClass(cls) -> None:
        """Open an empty database shared by the tests."""
        cls.tmpdir = tempfile.TemporaryDirectory()
        cls.db = make_database("sqlite")
        cls.db.load(cls.tmpdir.name)
        cls.dbstate = DbState()
        cls.dbstate.change_database(cls.db)

    @classmethod
    def tearDownClass(cls) -> None:
        """Close and remove the database."""
        cls.db.close()
        cls.tmpdir.cleanup()

    def setUp(self) -> None:
        """Ask in the "Save Changes?" dialog unless a test says otherwise."""
        patcher = patch(CONFIG)
        self.config = patcher.start()
        self.config.get.return_value = False
        self.addCleanup(patcher.stop)
        closer = patch.object(ManagedWindow, "close", _close_window)
        closer.start()
        self.addCleanup(closer.stop)

    def _ref_editor(self, update: Any = None) -> RefEditor:
        """
        :param update: The completion callback; a Mock by default.
        :returns: A reference editor on a new place and reference.
        """
        return RefEditor(self.dbstate, Place(), PlaceRef(), update or Mock())

    def _parent(self) -> RefEditor:
        """
        :returns: An editor standing in for the parent being confirmed.
        """
        return self._ref_editor()

    def test_dirty_reference_child_is_saved_before_parent(self) -> None:
        """A new reference with edits is handed over before the parent saves."""
        parent = self._parent()
        child = self._ref_editor()
        child.source.set_title("Pittsburgh")
        parent.set_tree([parent, child])
        with patch(DIALOG, _answer("save")):
            parent._save_with_dependent_children(None)
        self.assertEqual(child.saves, 1)
        child.result.assert_called_once()
        self.assertEqual(parent.saves, 1)

    def test_cancel_keeps_child_open_and_parent_unsaved(self) -> None:
        """Cancel on the child's prompt abandons the parent's save."""
        parent = self._parent()
        child = self._ref_editor()
        child.source.set_title("Pittsburgh")
        parent.set_tree([parent, child])
        with patch(DIALOG, _answer("cancel")):
            parent._save_with_dependent_children(None)
        self.assertTrue(child.opened)
        self.assertEqual(parent.saves, 0)

    def test_clean_child_is_left_alone(self) -> None:
        """A reference editor nobody typed into is not prompted for."""
        parent = self._parent()
        child = self._ref_editor()
        parent.set_tree([parent, child])
        with patch(DIALOG) as dialog:
            parent._save_with_dependent_children(None)
        dialog.assert_not_called()
        self.assertEqual(child.saves, 0)
        self.assertEqual(parent.saves, 1)

    def test_discard_restores_existing_reference_in_place(self) -> None:
        """
        "Close without saving" undoes the edits on the parent's own
        reference object, which keeps its identity.
        """
        ref = PlaceRef()
        ref.ref = "handle-1"
        parent = self._parent()
        child = RefEditor(self.dbstate, Place(), ref, Mock())
        ref.ref = "handle-2"  # edited in place, as the editor's widgets do
        parent.set_tree([parent, child])
        with patch(DIALOG, _answer("discard")):
            parent._save_with_dependent_children(None)
        self.assertEqual(ref.ref, "handle-1")
        self.assertFalse(child.opened)
        self.assertEqual(parent.saves, 1)

    def test_dont_ask_saves_child_without_prompt(self) -> None:
        """With interface.dont-ask set the child is saved, not dropped."""
        self.config.get.return_value = True
        parent = self._parent()
        child = self._ref_editor()
        child.source.set_title("Pittsburgh")
        parent.set_tree([parent, child])
        with patch(DIALOG) as dialog:
            parent._save_with_dependent_children(None)
        dialog.assert_not_called()
        self.assertEqual(child.saves, 1)
        self.assertEqual(parent.saves, 1)

    def test_nested_chain_resolves_innermost_first(self) -> None:
        """
        Person -> Event Reference -> Place: the inner editor's result lands
        on the middle one before the middle one is handed to the parent.
        """
        order: list[str] = []
        parent = self._parent()
        middle = self._ref_editor(update=lambda *a: order.append("middle"))
        inner = self._ref_editor(update=lambda *a: order.append("inner"))
        middle.source.set_title("Birth")
        inner.source.set_title("Pittsburgh")
        parent.set_tree([parent, [middle, inner]])
        with patch(DIALOG, _answer("save")):
            parent._save_with_dependent_children(None)
        self.assertEqual(order, ["inner", "middle"])
        self.assertEqual(parent.saves, 1)

    def test_reference_editor_ok_resolves_its_own_children(self) -> None:
        """
        OK on a reference editor first resolves editors it spawned, e.g. a
        new place opened from an event's place field.
        """
        ref_editor = self._ref_editor()
        child = self._ref_editor()
        child.source.set_title("Pittsburgh")
        ref_editor.set_tree([ref_editor, child])
        with patch(DIALOG, _answer("save")):
            ref_editor._save_with_dependent_children(None)
        self.assertEqual(child.saves, 1)
        self.assertEqual(ref_editor.saves, 1)

    def test_reference_cancel_restores_in_place(self) -> None:
        """Cancel on an existing reference leaves the parent's copy as it was."""
        ref = PlaceRef()
        ref.ref = "handle-1"
        editor = RefEditor(self.dbstate, Place(), ref, Mock())
        ref.ref = "handle-2"
        editor.close_and_cancel(None)
        self.assertEqual(ref.ref, "handle-1")
        self.assertFalse(editor.opened)

    def test_secondary_child_is_saved_before_parent(self) -> None:
        """A new address with edits is handed over before the parent saves."""
        added: list[Address] = []
        parent = self._parent()
        addr = Address()
        child = SecondaryEditor(self.dbstate, addr, added.append)
        addr.set_city("Pittsburgh")
        parent.set_tree([parent, child])
        with patch(DIALOG, _answer("save")):
            parent._save_with_dependent_children(None)
        self.assertEqual(added, [addr])
        self.assertEqual(parent.saves, 1)

    def test_secondary_cancel_restores_in_place(self) -> None:
        """
        Cancel on an existing address restores the parent's own object
        instead of swapping in a copy the parent never sees.
        """
        addr = Address()
        addr.set_city("Pittsburgh")
        editor = SecondaryEditor(self.dbstate, addr, Mock())
        addr.set_city("Philadelphia")
        editor.canceledits()
        self.assertEqual(addr.get_city(), "Pittsburgh")
        self.assertFalse(editor.opened)

    def test_close_after_save_keeps_edits(self) -> None:
        """The close that follows a save does not undo the saved edits."""
        addr = Address()
        editor = SecondaryEditor(self.dbstate, addr, Mock())
        addr.set_city("Pittsburgh")
        editor._save_with_dependent_children(None)
        self.assertEqual(editor.saves, 1)
        self.assertEqual(addr.get_city(), "Pittsburgh")

    def test_teardown_close_restores_in_place(self) -> None:
        """
        A close without a save (an ancestor closing, the referenced object
        being deleted) undoes the edits on the parent's own object.
        """
        addr = Address()
        editor = SecondaryEditor(self.dbstate, addr, Mock())
        addr.set_city("Pittsburgh")
        editor.close()
        self.assertEqual(addr.get_city(), "")

    def test_window_close_button_asks_when_changed(self) -> None:
        """
        The window's close button on a changed editor asks "Save Changes?";
        Cancel keeps the editor open and the edits in place.
        """
        addr = Address()
        editor = SecondaryEditor(self.dbstate, addr, Mock())
        addr.set_city("Pittsburgh")
        with patch(DIALOG, _answer("cancel")):
            handled = editor.close(editor.window, Gdk.Event())
        self.assertTrue(handled)
        self.assertTrue(editor.opened)
        self.assertEqual(addr.get_city(), "Pittsburgh")

    def test_window_close_button_save(self) -> None:
        """Save in that dialog saves the editor."""
        addr = Address()
        editor = SecondaryEditor(self.dbstate, addr, Mock())
        addr.set_city("Pittsburgh")
        with patch(DIALOG, _answer("save")):
            editor.close(editor.window, Gdk.Event())
        self.assertEqual(editor.saves, 1)
        self.assertEqual(addr.get_city(), "Pittsburgh")

    def test_window_close_button_without_changes_just_closes(self) -> None:
        """An unchanged editor closes without a prompt."""
        editor = SecondaryEditor(self.dbstate, Address(), Mock())
        with patch(DIALOG) as dialog:
            editor.close(editor.window, Gdk.Event())
        dialog.assert_not_called()
        self.assertFalse(editor.opened)

    def test_child_without_window_is_not_resolved(self) -> None:
        """
        A child whose window was already destroyed (a cancelled teardown
        prompt) is not shown or saved again.
        """
        parent = self._parent()
        child = self._ref_editor()
        child.source.set_title("Pittsburgh")
        child.window = None
        parent.set_tree([parent, child])
        with patch(DIALOG) as dialog:
            parent._save_with_dependent_children(None)
        dialog.assert_not_called()
        self.assertEqual(parent.saves, 1)

    def test_open_descendants_are_settled_before_commit(self) -> None:
        """Editors left open below the parent are told before it commits."""
        parent = self._parent()
        child = self._ref_editor()
        parent.set_tree([parent, child])
        with patch.object(RefEditor, "_before_ancestor_commit") as settle:
            parent._save_with_dependent_children(None)
        settle.assert_called_once_with()
        self.assertEqual(parent.saves, 1)

    def test_editor_without_callback_is_not_resolved(self) -> None:
        """An editor nobody waits on is left to the normal close path."""
        parent = self._parent()
        child = SecondaryEditor(self.dbstate, Address(), None)
        child.obj.set_city("Pittsburgh")
        parent.set_tree([parent, child])
        with patch(DIALOG) as dialog:
            parent._save_with_dependent_children(None)
        dialog.assert_not_called()
        self.assertEqual(parent.saves, 1)


if __name__ == "__main__":
    unittest.main()

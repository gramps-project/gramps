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
Unit tests for :mod:`gramps.gui.savecascade`, the "resolve dependent child
editors before a parent commits" decision behind the #7924 fix.

These exercise the same functions the live save path calls
(``EditPrimary._resolve_dependent_children`` uses ``children_to_resolve``
and ``has_pending_reference``), on fabricated ``GrampsWindowManager`` trees
and stand-in editors, so they run headless without GTK or the editor stack.
"""

import unittest
from collections.abc import Callable
from typing import Any

from gramps.gen.lib import Address, Attribute, AttributeType, EventRef
from gramps.gui.savecascade import (
    InPlaceSnapshot,
    children_to_resolve,
    descendant_leaves,
    has_pending_reference,
)


def _refresh(*args: Any) -> None:
    """
    Stand in for a completion callback.

    :param args: Ignored.
    """


# -------------------------------------------------------------------------
#
# FakeWindow
#
# -------------------------------------------------------------------------
class FakeWindow:
    """
    A stand-in for a managed editor window in the window tree.

    It carries the attributes :func:`has_pending_reference` reads off a
    real ``EditPrimary``: ``opened``, ``callback``, ``writes_back`` and
    ``data_has_changed()``. ``primary`` stands in for the
    ``isinstance(window, EditPrimary)`` check done by the editor.
    """

    def __init__(
        self,
        name: str,
        primary: bool = True,
        opened: bool = True,
        callback: Callable[..., None] | None = _refresh,
        writes_back: bool = True,
        dirty: bool = True,
        shares: bool = False,
    ) -> None:
        """
        :param name: Label used in failure messages.
        :param primary: Whether the window is a primary editor.
        :param opened: Whether the window is still open.
        :param callback: The completion callback, or None.
        :param writes_back: Whether a parent commit without this editor
            would lose its work.
        :param dirty: Whether the editor holds unsaved changes.
        :param shares: Whether it is a new reference to an existing object.
        """
        self.name = name
        self.primary = primary
        self.opened = opened
        self.shares_existing_object = shares
        self.callback = callback
        self.writes_back = writes_back
        self.dirty = dirty

    def data_has_changed(self) -> bool:
        """
        :returns: Whether the editor holds unsaved changes.
        """
        return self.dirty

    def __repr__(self) -> str:
        """
        :returns: A short description for failure messages.
        """
        return "FakeWindow(%r)" % self.name


def _needs_resolving(win: FakeWindow) -> bool:
    """
    Mirror ``EditPrimary._is_unresolved_dependent_child`` over fake windows.

    :param win: The candidate window.
    :returns: True if the window is a primary editor owing a reference.
    """
    return win.primary and has_pending_reference(win)


# -------------------------------------------------------------------------
#
# DescendantLeavesTest
#
# -------------------------------------------------------------------------
class DescendantLeavesTest(unittest.TestCase):
    """``descendant_leaves`` walks the GrampsWindowManager tree correctly."""

    def test_leaf_node_has_no_descendants(self) -> None:
        """A parent editor that spawned nothing is stored as a bare leaf."""
        parent = FakeWindow("parent")
        self.assertEqual(descendant_leaves(parent), [])

    def test_branch_with_only_head_has_no_descendants(self) -> None:
        """A branch whose head has no children yields nothing."""
        parent = FakeWindow("parent")
        self.assertEqual(descendant_leaves([parent]), [])

    def test_head_window_is_excluded(self) -> None:
        """The parent itself is never one of its own descendants."""
        parent = FakeWindow("parent")
        child = FakeWindow("child")
        self.assertNotIn(parent, descendant_leaves([parent, child]))

    def test_single_child_returned(self) -> None:
        """A single spawned window is returned."""
        parent = FakeWindow("parent")
        child = FakeWindow("child")
        self.assertEqual(descendant_leaves([parent, child]), [child])

    def test_nested_chain_is_deepest_first(self) -> None:
        """In parent -> mid -> deep, 'deep' comes before 'mid'."""
        deep = FakeWindow("deep")
        mid = FakeWindow("mid")
        parent = FakeWindow("parent")
        self.assertEqual(descendant_leaves([parent, [mid, deep]]), [deep, mid])

    def test_siblings_each_resolved_deepest_first(self) -> None:
        """Each sibling branch is ordered deepest first, in sibling order."""
        parent = FakeWindow("parent")
        a_head = FakeWindow("a_head")
        a_deep = FakeWindow("a_deep")
        b = FakeWindow("b")
        tree = [parent, [a_head, a_deep], b]
        self.assertEqual(descendant_leaves(tree), [a_deep, a_head, b])


# -------------------------------------------------------------------------
#
# HasPendingReferenceTest
#
# -------------------------------------------------------------------------
class HasPendingReferenceTest(unittest.TestCase):
    """``has_pending_reference`` picks out editors that owe a reference."""

    def test_new_dirty_object_with_callback_is_pending(self) -> None:
        """The #7924 case: "add a new person as the mother", with a name."""
        self.assertTrue(has_pending_reference(FakeWindow("mother")))

    def test_existing_object_with_refresh_callback_is_not_pending(self) -> None:
        """
        An existing object edited from an object entry (``after_edit``) or a
        family's child list (``child_ref_edited``) carries a callback, but
        the parent already holds its handle.
        """
        existing = FakeWindow("existing_place", writes_back=False)
        self.assertFalse(has_pending_reference(existing))

    def test_object_without_callback_is_not_pending(self) -> None:
        """EditFamily.edit_person opens an existing person with no callback."""
        existing = FakeWindow("existing_person", callback=None)
        self.assertFalse(has_pending_reference(existing))

    def test_unchanged_new_object_is_not_pending(self) -> None:
        """A new editor nobody typed into has nothing to save."""
        self.assertFalse(has_pending_reference(FakeWindow("blank", dirty=False)))

    def test_unchanged_shared_object_is_pending(self) -> None:
        """
        "Share existing": a new reference to an existing object is owed to
        the parent even when nothing else was edited.
        """
        shared = FakeWindow("shared_event", dirty=False, shares=True)
        self.assertTrue(has_pending_reference(shared))

    def test_closed_editor_is_not_pending(self) -> None:
        """An editor that has already closed has nothing to resolve."""
        self.assertFalse(has_pending_reference(FakeWindow("gone", opened=False)))

    def test_window_without_editor_attributes_is_not_pending(self) -> None:
        """A selector or other plain window lacks the attributes entirely."""

        class PlainWindow:
            """A managed window that is not an editor."""

            opened = True

        self.assertFalse(has_pending_reference(PlainWindow()))


# -------------------------------------------------------------------------
#
# ChildrenToResolveTest
#
# -------------------------------------------------------------------------
class ChildrenToResolveTest(unittest.TestCase):
    """``children_to_resolve`` selects and orders the windows to resolve."""

    def test_no_children_returns_empty(self) -> None:
        """A parent with no spawned windows resolves nothing."""
        parent = FakeWindow("parent")
        self.assertEqual(list(children_to_resolve([parent], _needs_resolving)), [])

    def test_dependent_child_is_selected(self) -> None:
        """EditFamily with an open "new mother" EditPerson resolves it."""
        family = FakeWindow("family")
        mother = FakeWindow("mother")
        self.assertEqual(
            list(children_to_resolve([family, mother], _needs_resolving)), [mother]
        )

    def test_non_editor_child_is_skipped(self) -> None:
        """Selectors and other plain windows are not part of the cascade."""
        family = FakeWindow("family")
        ref_editor = FakeWindow("selector", primary=False)
        self.assertEqual(
            list(children_to_resolve([family, ref_editor], _needs_resolving)), []
        )

    def test_existing_object_child_is_skipped(self) -> None:
        """An edited existing object is left for the normal close path."""
        event = FakeWindow("event")
        place = FakeWindow("existing_place", writes_back=False)
        self.assertEqual(
            list(children_to_resolve([event, place], _needs_resolving)), []
        )

    def test_selection_preserves_deepest_first_order(self) -> None:
        """Dependent windows keep deepest-first order; others drop out."""
        parent = FakeWindow("parent")
        deep = FakeWindow("deep")
        mid = FakeWindow("mid")
        clean_sibling = FakeWindow("clean_sibling", dirty=False)
        tree = [parent, [mid, deep], clean_sibling]
        self.assertEqual(list(children_to_resolve(tree, _needs_resolving)), [deep, mid])

    def test_decision_uses_state_at_resolve_time(self) -> None:
        """
        A window that changes state while an earlier one is resolved is
        judged on its new state, not on a snapshot taken up front.
        """
        parent = FakeWindow("parent")
        first = FakeWindow("first")
        second = FakeWindow("second")
        resolved = []
        for win in children_to_resolve([parent, first, second], _needs_resolving):
            resolved.append(win)
            # Resolving 'first' also closes 'second' (e.g. it was discarded).
            second.opened = False
        self.assertEqual(resolved, [first])


# -------------------------------------------------------------------------
#
# InPlaceSnapshotTest
#
# -------------------------------------------------------------------------
class InPlaceSnapshotTest(unittest.TestCase):
    """``InPlaceSnapshot`` detects and undoes edits on a shared object."""

    def test_unchanged_object_is_clean(self) -> None:
        """Taking a snapshot does not count as an edit."""
        addr = Address()
        addr.set_city("Pittsburgh")
        self.assertFalse(InPlaceSnapshot(addr).has_changed())

    def test_edit_is_detected(self) -> None:
        """Changing a field after the snapshot is detected."""
        addr = Address()
        snap = InPlaceSnapshot(addr)
        addr.set_city("Pittsburgh")
        self.assertTrue(snap.has_changed())

    def test_restore_keeps_identity(self) -> None:
        """Restoring puts the old state back into the same instance."""
        addr = Address()
        addr.set_city("Pittsburgh")
        holder = [addr]  # the parent's list holding the object
        snap = InPlaceSnapshot(addr)
        addr.set_city("Philadelphia")
        snap.restore()
        self.assertIs(holder[0], addr)
        self.assertEqual(addr.get_city(), "Pittsburgh")
        self.assertFalse(snap.has_changed())

    def test_restore_can_be_repeated(self) -> None:
        """The snapshot itself is not handed out, so it survives a restore."""
        addr = Address()
        snap = InPlaceSnapshot(addr)
        addr.set_city("Pittsburgh")
        snap.restore()
        addr.set_city("Philadelphia")
        snap.restore()
        self.assertEqual(addr.get_city(), "")

    def test_restore_keeps_nested_identity(self) -> None:
        """
        Lists and objects inside the restored object stay the same
        instances, so an open tab or child editor holding them still writes
        onto the parent's object.
        """
        addr = Address()
        citations = addr.get_citation_list()
        date = addr.get_date_object()
        snap = InPlaceSnapshot(addr)
        addr.add_citation("c-1")
        date.set_yr_mon_day(1900, 1, 1)
        snap.restore()
        self.assertIs(addr.get_citation_list(), citations)
        self.assertIs(addr.get_date_object(), date)
        self.assertEqual(citations, [])
        self.assertFalse(snap.has_changed())
        addr.add_citation("c-2")  # a child saved after the restore
        self.assertEqual(addr.get_citation_list(), ["c-2"])

    def test_restore_undoes_reordering_by_identity(self) -> None:
        """
        Reordered list items go back to their places as the same
        instances, each with its own state, not swapped with each other.
        """
        ref = EventRef()
        first, second = Attribute(), Attribute()
        first.set_value("first")
        second.set_value("second")
        ref.add_attribute(first)
        ref.add_attribute(second)
        attributes = ref.get_attribute_list()
        snap = InPlaceSnapshot(ref)
        attributes.reverse()
        first.set_value("edited")
        snap.restore()
        self.assertIs(ref.get_attribute_list(), attributes)
        self.assertIs(attributes[0], first)
        self.assertIs(attributes[1], second)
        self.assertEqual(first.get_value(), "first")
        self.assertEqual(second.get_value(), "second")

    def test_restore_brings_back_removed_items_and_drops_added(self) -> None:
        """A removed item returns as the same instance; an added one goes."""
        ref = EventRef()
        kept = Attribute()
        ref.add_attribute(kept)
        snap = InPlaceSnapshot(ref)
        ref.get_attribute_list().remove(kept)
        ref.add_attribute(Attribute())
        snap.restore()
        self.assertEqual(len(ref.get_attribute_list()), 1)
        self.assertIs(ref.get_attribute_list()[0], kept)
        self.assertFalse(snap.has_changed())

    def test_restore_resets_types_kept_in_slots(self) -> None:
        """
        A ``GrampsType`` keeps its value in slots, not ``__dict__``; Cancel
        must still put the old type back, on the same instance.
        """
        attr = Attribute()
        attr.set_type(AttributeType.AGE)
        attr_type = attr.get_type()
        snap = InPlaceSnapshot(attr)
        attr_type.set(AttributeType.NICKNAME)
        snap.restore()
        self.assertIs(attr.get_type(), attr_type)
        self.assertEqual(attr_type, AttributeType.AGE)
        self.assertFalse(snap.has_changed())

    def test_restore_replaces_changed_structure(self) -> None:
        """A nested object of a different type is replaced, not merged."""
        addr = Address()
        snap = InPlaceSnapshot(addr)
        addr.date = None
        snap.restore()
        self.assertFalse(snap.has_changed())

    def test_none_is_never_changed(self) -> None:
        """A missing object (e.g. no reference yet) is treated as clean."""
        snap = InPlaceSnapshot(None)
        self.assertFalse(snap.has_changed())
        snap.restore()


if __name__ == "__main__":
    unittest.main()

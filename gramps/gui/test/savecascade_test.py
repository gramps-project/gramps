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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

"""
Unit tests for :mod:`gramps.gui.savecascade` -- the pure "resolve dependent
child editors before a parent commits" decision behind the #7924 fix.

This exercises the SAME functions the live save path drives
(``EditPrimary._resolve_dependent_children`` calls ``children_to_resolve``;
``descendant_leaves`` walks the window tree), but on fabricated
``GrampsWindowManager`` tree structures, so the ordering and selection logic
is proven headless -- without a display, GTK, or the GUI editor stack. The
reference-survival end-state itself is exercised by the committed
AT-SPI/dogtail interface repro
(``engine/interface/test_bug_7924_child_editor_data_loss.py``).
"""

import unittest

from gramps.gui.savecascade import descendant_leaves, children_to_resolve


class FakeWindow:
    """A stand-in for a managed window leaf in the window tree.

    ``primary``/``opened``/``has_callback``/``dirty`` mirror the facts the
    production predicate (``EditPrimary._is_unresolved_dependent_child``)
    reads off a real editor: it is an EditPrimary, still open, opened WITH a
    completion callback, and holding changed data.
    """

    def __init__(self, name, primary=True, opened=True, has_callback=True, dirty=True):
        self.name = name
        self.primary = primary
        self.opened = opened
        self.has_callback = has_callback
        self.dirty = dirty

    def __repr__(self):
        return "FakeWindow(%r)" % self.name


def _needs_resolving(win):
    """Predicate mirroring the production one, over FakeWindow facts:
    a primary editor, still open, opened with a completion callback, dirty."""
    return win.primary and win.opened and win.has_callback and win.dirty


class DescendantLeavesTest(unittest.TestCase):
    """``descendant_leaves`` walks the GrampsWindowManager tree correctly."""

    def test_leaf_node_has_no_descendants(self):
        # A parent editor that spawned nothing is stored as a bare leaf.
        parent = FakeWindow("parent")
        self.assertEqual(descendant_leaves(parent), [])

    def test_branch_with_only_head_has_no_descendants(self):
        # A branch node: item[0] is the head window, no children yet.
        parent = FakeWindow("parent")
        self.assertEqual(descendant_leaves([parent]), [])

    def test_head_window_is_excluded(self):
        parent = FakeWindow("parent")
        child = FakeWindow("child")
        self.assertNotIn(parent, descendant_leaves([parent, child]))

    def test_single_child_returned(self):
        parent = FakeWindow("parent")
        child = FakeWindow("child")
        self.assertEqual(descendant_leaves([parent, child]), [child])

    def test_nested_chain_is_deepest_first(self):
        # parent -> mid -> deep : resolving must reach 'deep' before 'mid'
        # so 'mid's completion callback has already landed when 'mid' saves.
        deep = FakeWindow("deep")
        mid = FakeWindow("mid")
        parent = FakeWindow("parent")
        tree = [parent, [mid, deep]]
        self.assertEqual(descendant_leaves(tree), [deep, mid])

    def test_siblings_each_resolved_deepest_first(self):
        parent = FakeWindow("parent")
        a_head = FakeWindow("a_head")
        a_deep = FakeWindow("a_deep")
        b = FakeWindow("b")
        tree = [parent, [a_head, a_deep], b]
        # Within branch 'a', a_deep precedes a_head; sibling 'b' follows.
        self.assertEqual(descendant_leaves(tree), [a_deep, a_head, b])


class ChildrenToResolveTest(unittest.TestCase):
    """``children_to_resolve`` selects + orders the windows to resolve."""

    def test_no_children_returns_empty(self):
        parent = FakeWindow("parent")
        self.assertEqual(children_to_resolve([parent], _needs_resolving), [])

    def test_dirty_child_is_selected(self):
        # The #7924 case: EditFamily with an open, dirty EditPerson child
        # opened as "add a new mother" (so it carries a completion callback).
        family = FakeWindow("family")
        mother = FakeWindow("mother", primary=True, opened=True, dirty=True)
        self.assertEqual(
            children_to_resolve([family, mother], _needs_resolving), [mother]
        )

    def test_clean_child_is_skipped(self):
        family = FakeWindow("family")
        clean = FakeWindow("clean", dirty=False)
        self.assertEqual(children_to_resolve([family, clean], _needs_resolving), [])

    def test_non_primary_child_is_skipped(self):
        # e.g. a selector or secondary window carries no completion callback.
        family = FakeWindow("family")
        selector = FakeWindow("selector", primary=False)
        self.assertEqual(children_to_resolve([family, selector], _needs_resolving), [])

    def test_child_without_callback_is_skipped(self):
        # EditFamily.edit_person opens an EXISTING person's editor with no
        # completion callback -- committing the family drops nothing, so the
        # dirty-but-callback-less child must NOT be force-resolved (#7924
        # over-trigger guard).
        family = FakeWindow("family")
        existing = FakeWindow("existing_person", has_callback=False, dirty=True)
        self.assertEqual(children_to_resolve([family, existing], _needs_resolving), [])

    def test_already_closed_child_is_skipped(self):
        family = FakeWindow("family")
        gone = FakeWindow("gone", opened=False)
        self.assertEqual(children_to_resolve([family, gone], _needs_resolving), [])

    def test_selection_preserves_deepest_first_order(self):
        parent = FakeWindow("parent")
        deep = FakeWindow("deep", dirty=True)
        mid = FakeWindow("mid", dirty=True)
        clean_sibling = FakeWindow("clean_sibling", dirty=False)
        tree = [parent, [mid, deep], clean_sibling]
        # deep before mid (deepest-first); the clean sibling is filtered out.
        self.assertEqual(children_to_resolve(tree, _needs_resolving), [deep, mid])


if __name__ == "__main__":
    unittest.main()

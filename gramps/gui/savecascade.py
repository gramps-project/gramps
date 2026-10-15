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
Pure logic for the "resolve dependent child editors before a parent editor
commits" decision (Mantis #7924).

This module is deliberately free of any GTK / ``gramps.gui`` imports so the
decision it embodies -- *which* open child windows a parent editor must
resolve before it persists its object graph, and *in what order* -- can be
unit-tested headless while the live save path (:class:`gramps.gui.editors.
editprimary.EditPrimary`) drives the very same functions on the real window
tree.

The window tree is the structure :class:`gramps.gui.managedwindow.
GrampsWindowManager` maintains: a *branch* is a list whose first element is
the head (parent) window of a group and whose remaining elements are the
windows spawned from it (each itself a branch or a leaf); a *leaf* is any
non-list item (a single managed window). See ``GrampsWindowManager`` for the
authoritative description of the tree.
"""


def descendant_leaves(item):
    """Return the leaf windows spawned *below* the tree node ``item``.

    ``item`` is a node of the ``GrampsWindowManager`` window tree (obtained
    e.g. via ``get_item_from_track``). If it is a branch, its head window
    (``item[0]``) is excluded and every descendant leaf is returned ordered
    **deepest-child-first**, so a caller resolving a save cascade processes
    the innermost spawned editor before the editor that spawned it (the
    nested Place -> enclosing-Place -> ... chain in #7924). A leaf node (a
    window with no spawned children) yields an empty list.
    """
    leaves = []
    if isinstance(item, list):
        for sub_item in item[1:]:
            _collect(sub_item, leaves)
    return leaves


def _collect(item, leaves):
    """Append the leaf windows under ``item`` to ``leaves``, deepest-first."""
    if isinstance(item, list):
        for sub_item in item[1:]:
            _collect(sub_item, leaves)
        # The head of this sub-branch comes *after* the windows it spawned,
        # so children are always resolved before their own parent.
        _collect(item[0], leaves)
    else:
        leaves.append(item)


def children_to_resolve(item, needs_resolving):
    """Return the descendant windows a parent editor must resolve before it
    commits, deepest-child-first.

    ``item`` is the parent editor's node in the window tree; ``needs_resolving``
    is a predicate ``needs_resolving(window) -> bool`` the caller supplies. In
    production it is true for an open, dirty child *primary* editor that still
    carries a completion callback (one whose callback still has to land a
    reference on the parent's object); being a plain callable keeps this
    decision fully unit-testable with fakes.
    """
    return [win for win in descendant_leaves(item) if needs_resolving(win)]

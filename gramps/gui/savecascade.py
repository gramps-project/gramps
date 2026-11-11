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

from collections.abc import Callable, Iterator
from typing import Any


def descendant_leaves(item: Any) -> list[Any]:
    """
    Return the windows spawned *below* a node of the window tree.

    If ``item`` is a branch, its head window (``item[0]``) is excluded and
    every descendant window is returned **deepest-child-first**, so a caller
    resolving a save cascade processes the innermost spawned editor before
    the editor that spawned it (e.g. a nested Place -> enclosing-Place
    chain). A leaf node (a window with no spawned children) yields an empty
    list.

    :param item: A node of the ``GrampsWindowManager`` window tree, as
        returned by ``get_item_from_track``.
    :returns: The descendant windows, deepest first.
    """
    leaves: list[Any] = []
    if isinstance(item, list):
        for sub_item in item[1:]:
            _collect(sub_item, leaves)
    return leaves


def _collect(item: Any, leaves: list[Any]) -> None:
    """
    Append the windows under ``item`` to ``leaves``, deepest first.

    :param item: A branch or leaf of the window tree.
    :param leaves: The list being filled, modified in place.
    """
    if isinstance(item, list):
        for sub_item in item[1:]:
            _collect(sub_item, leaves)
        # The head of this sub-branch comes *after* the windows it spawned,
        # so children are always resolved before their own parent.
        _collect(item[0], leaves)
    else:
        leaves.append(item)


def has_pending_reference(window: Any) -> bool:
    """
    Tell whether an editor window still owes its parent a reference.

    A primary editor writes a handle back onto the editor that spawned it
    only when it was opened on a *new* object together with a completion
    callback (e.g. ``EditFamily.new_mother_added``), and only once it saves.
    Editors opened on an *existing* object may also carry a callback (for
    instance ``ObjEntry.after_edit`` or ``EditFamily.child_ref_edited``), but
    that callback merely refreshes the parent's display: the parent already
    holds the handle, so committing the parent drops nothing and the child
    is left alone.

    :param window: The candidate editor. It is read through the attributes
        ``opened``, ``callback`` and ``opened_as_new`` and the method
        ``data_has_changed()``.
    :returns: True if the window is open, was opened on a new object with a
        completion callback, and holds unsaved changes.
    """
    return bool(
        getattr(window, "opened", False)
        and getattr(window, "callback", None) is not None
        and getattr(window, "opened_as_new", False)
        and window.data_has_changed()
    )


def children_to_resolve(
    item: Any, needs_resolving: Callable[[Any], bool]
) -> Iterator[Any]:
    """
    Yield the descendant windows a parent editor must resolve before it
    commits, deepest-child-first.

    The set of descendant windows is taken once, but ``needs_resolving`` is
    evaluated lazily, just before each window is yielded. Resolving one
    window can change the state of another (saving it closes it, or its
    callback marks its parent as changed), so the decision is made against
    the current state rather than a snapshot taken before any child ran.

    :param item: The parent editor's node in the window tree.
    :param needs_resolving: Predicate deciding whether a window must be
        resolved. In production it combines an ``EditPrimary`` type check
        with :func:`has_pending_reference`.
    :returns: An iterator over the windows to resolve, deepest first.
    """
    for win in descendant_leaves(item):
        if needs_resolving(win):
            yield win

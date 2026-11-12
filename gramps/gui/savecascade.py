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
from copy import deepcopy
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
    Tell whether an editor window still owes its parent unsaved work.

    An editor owes its parent work when committing the parent without it
    would lose or half-apply its edits (``writes_back``), it has a completion
    callback handing its result to the parent, and it holds unsaved changes.

    ``writes_back`` depends on the kind of editor:

    * A primary editor writes back only when it was opened on a *new*
      object: its callback hands the new handle to the parent (e.g.
      ``EditFamily.new_mother_added``). An editor opened on an *existing*
      object may also carry a callback (``ObjEntry.after_edit``,
      ``EditFamily.child_ref_edited``), but that only refreshes the parent,
      which already holds the handle.
    * A reference or secondary editor always writes back: a new object
      reaches the parent only through the callback, and an existing one is
      edited in place on the parent's own object.

    A reference editor opened on a new reference to an object that already
    exists ("share existing", ``shares_existing_object``) owes the parent
    that reference even if nothing was edited: picking the object was the
    user's edit.

    :param window: The candidate editor. It is read through the attributes
        ``opened``, ``callback`` and ``writes_back`` and the method
        ``data_has_changed()``.
    :returns: True if the window is open, writes back, has a completion
        callback, and holds unsaved changes or shares an existing object.
    """
    return bool(
        getattr(window, "opened", False)
        and getattr(window, "callback", None) is not None
        and getattr(window, "writes_back", False)
        and (
            window.data_has_changed()
            or getattr(window, "shares_existing_object", False)
        )
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
        resolved. In production it combines a cascade-editor type check
        with :func:`has_pending_reference`.
    :returns: An iterator over the windows to resolve, deepest first.
    """
    for win in descendant_leaves(item):
        if needs_resolving(win):
            yield win


class InPlaceSnapshot:
    """
    A copy of an object being edited in place, for change detection and
    for undoing the edits without replacing the object.

    Reference and secondary editors edit the very object the parent holds
    (an existing ``EventRef``, ``Address``, ...). Undoing their edits must
    therefore restore that same instance, not swap in a new one the parent
    never sees.
    """

    def __init__(self, obj: Any) -> None:
        """
        :param obj: The object to snapshot; may be None.
        """
        self.obj = obj
        memo: dict[int, Any] = {}
        self.copy = deepcopy(obj, memo)
        # Map each copied list or object back to the live one it was copied
        # from, so a restore can put the live instances back where they were.
        originals = {id(orig): orig for orig in memo.get(id(memo), [])}
        self._origin: dict[int, Any] = {
            id(copied): originals[key]
            for key, copied in memo.items()
            if key in originals and copied is not originals[key]
        }

    def has_changed(self) -> bool:
        """
        :returns: True if the object now serializes differently from the
            snapshot.
        """
        if self.obj is None:
            return False
        return bool(self.obj.serialize() != self.copy.serialize())

    def restore(self) -> None:
        """
        Put the snapshot's state back into the original object, keeping its
        identity and that of every list and object that was inside it when
        the snapshot was taken.

        Open tabs and child editors hold those nested lists and objects
        (e.g. a citation tab holds the citation list, a child editor holds a
        reference in it), so they must stay the parent's own instances: each
        goes back to where it was, with its old state, even if the edits
        reordered, removed or replaced it. Anything added since is dropped.
        """
        if self.obj is None:
            return
        self._restore(self.copy)

    def _restore(self, saved: Any) -> Any:
        """
        :param saved: A value inside the snapshot; it is not modified.
        :returns: The live value to put in its place: the live instance it
            was copied from, set back to the snapshot's state, or a fresh
            copy if there is none.
        """
        live = self._origin.get(id(saved))
        if isinstance(saved, list):
            items = [self._restore(item) for item in saved]
            if not isinstance(live, list):
                return items
            live[:] = items
            return live
        state = getattr(saved, "__dict__", None)
        if state is None or isinstance(saved, type) or type(live) is not type(saved):
            return deepcopy(saved)
        restored = {key: self._restore(value) for key, value in state.items()}
        live.__dict__.clear()
        live.__dict__.update(restored)
        return live

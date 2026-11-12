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
Resolve open dependent child editors before a parent editor commits.

Editors are non-modal, so a parent editor can be confirmed while an editor
it spawned is still open with unsaved data. That child's data reaches the
parent only when the child itself is saved: a new object's handle, or a new
reference or secondary object, is handed over by the child's completion
callback, and an existing reference or secondary object is edited in place
on the parent's own object. Committing the parent first therefore drops the
child's work, or persists it half-finished (Mantis #7924, #12008).

:class:`DependentSaveMixin` is shared by primary, reference and secondary
editors. It resolves such children deepest-first, through each child's own
"Save Changes?" dialog, before the parent's save handler runs. The decision
of which windows to resolve, and in what order, lives in the GTK-free
:mod:`gramps.gui.savecascade`.
"""

# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------
from collections.abc import Callable
from typing import Any

# -------------------------------------------------------------------------
#
# GTK modules
#
# -------------------------------------------------------------------------
from gi.repository import Gdk

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.config import config
from gramps.gen.const import GRAMPS_LOCALE as glocale
from ..dialog import SaveDialog
from ..savecascade import (
    children_to_resolve,
    descendant_leaves,
    has_pending_reference,
)

_ = glocale.translation.sgettext


# -------------------------------------------------------------------------
#
# DependentSaveMixin
#
# -------------------------------------------------------------------------
class DependentSaveMixin:
    """
    Resolve open dependent child editors before this editor commits.

    The class using this mixin must be a managed window (``uistate``,
    ``track``, ``opened``, ``window``) and provide:

    * ``callback`` -- the completion callback handing this editor's result
      to its parent, or None;
    * ``writes_back`` -- True if committing the parent without this editor
      would lose or half-apply its edits;
    * ``data_has_changed()`` -- whether there are unsaved edits;
    * ``_discard_for_parent()`` -- drop the edits and close.

    It wires the OK button through :meth:`_save_with_dependent_children`
    (see :meth:`_wire_ok_button`) and remembers the editor's own confirm
    handler in ``_ok_function``.
    """

    _ok_function: Callable[..., Any] | None = None
    # True while the editor's own confirm handler runs, so a close() it
    # triggers is known to follow a save rather than a discard.
    _saving = False

    def _wire_ok_button(self, button: Any, function: Callable[..., Any]) -> None:
        """
        Connect the OK button through the dependent-children guard.

        :param button: The editor's OK button.
        :param function: The editor's own confirm handler.
        """
        self._ok_function = function
        button.connect("clicked", self._save_with_dependent_children)

    def _save_with_dependent_children(self, *args: Any) -> None:
        """
        Resolve open dependent child editors, then run this editor's save.

        Each dependent child is resolved first, through its own "Save
        Changes?" dialog. If one is left open (the user chose Cancel, or its
        save failed validation), this editor's save is abandoned and the
        editor stays open. Children resolved before that point have already
        been saved, and their results have landed on this editor's object,
        so confirming this editor again completes the graph.

        :param args: Signal arguments, passed through to the save handler.
        """
        if not self._resolve_dependent_children():
            return
        self._settle_open_descendants()
        self._run_ok_function(*args)

    def _run_ok_function(self, *args: Any) -> None:
        """
        Run the editor's own confirm handler, flagging that any close() it
        triggers follows a save.

        :param args: Arguments for the confirm handler.
        """
        if self._ok_function is None:
            return
        self._saving = True
        self._ok_function(*args)
        # Not reset in a ``finally``: if the handler raises, it may already
        # have committed and handed part of the result to the parent, and a
        # later Cancel must not undo that half of it.
        self._saving = False

    def _tree_item(self) -> Any:
        """
        :returns: This editor's node in the window tree, or None if it is
            not in the tree.
        """
        uistate = getattr(self, "uistate", None)
        if uistate is None:
            return None
        try:
            return uistate.gwm.get_item_from_track(self.track)  # type: ignore[attr-defined]
        except (IndexError, KeyError):
            return None

    def _settle_open_descendants(self) -> None:
        """
        Let the editors still open below this one drop display-only state
        from the objects they edit in place, before this editor commits.
        """
        for window in descendant_leaves(self._tree_item()):
            if (
                window is not self
                and isinstance(window, DependentSaveMixin)
                and getattr(window, "opened", False)
            ):
                window._before_ancestor_commit()

    def _before_ancestor_commit(self) -> None:
        """
        Called while this editor is open and an editor above it is about to
        commit. Editors that put display-only values on the object they edit
        in place remove them here; the default does nothing.
        """

    def _dependent_children(self) -> Any:
        """
        Iterate over the open child editors that must be resolved before
        this editor commits, deepest first.

        :returns: An iterator over the child editors; empty if this editor
            is not in the window tree.
        """
        item = self._tree_item()
        if item is None:
            return iter(())
        return children_to_resolve(item, self._is_unresolved_dependent_child)

    def _has_dependent_children(self) -> bool:
        """
        :returns: True if at least one open child editor must be resolved
            before this editor commits.
        """
        return next(self._dependent_children(), None) is not None

    def _resolve_dependent_children(self) -> bool:
        """
        Resolve the open child editors that must be resolved before this
        editor commits.

        Children are resolved deepest-first, so in a nested chain each
        level's result has landed on its own parent before that parent is
        resolved. Whether a child needs resolving is decided just before it
        is resolved, against the current state.

        :returns: True if the save may proceed: every dependent child was
            saved or discarded by the user, or there were none. False if a
            child was left open, in which case the caller must not commit.
        """
        for child in self._dependent_children():
            if not child._resolve_before_parent_commit():
                return False
        return True

    def _is_unresolved_dependent_child(self, window: Any) -> bool:
        """
        Tell whether a window is a child editor that must be resolved
        before this editor commits.

        :param window: A window from this editor's part of the window tree.
        :returns: True if ``window`` is another editor taking part in the
            cascade, still has its GTK window and a confirm handler, and
            still owes its parent work
            (see :func:`~gramps.gui.savecascade.has_pending_reference`).
            An editor whose window was already destroyed (a teardown whose
            "Save Changes?" prompt was cancelled) cannot be shown or saved
            safely and is left alone.
        """
        return (
            window is not self
            and isinstance(window, DependentSaveMixin)
            and window._ok_function is not None
            and getattr(window, "window", None) is not None
            and has_pending_reference(window)
        )

    def _resolve_before_parent_commit(self) -> bool:
        """
        Run this child editor's save guard because its parent is being
        confirmed.

        "Save" runs this editor's confirm handler, so its result lands on
        the parent; "Close without saving" discards the edits; Cancel keeps
        this editor open. With ``interface.dont-ask`` set, the editor is
        saved without asking: discarding it instead would lose the user's
        work, which is the defect being fixed.

        :returns: True if this editor is now closed and the parent may
            commit; False if it is still open and the parent must not.
        """
        if config.get("interface.dont-ask"):
            self._commit_for_parent()
        else:
            SaveDialog(
                _("Save Changes?"),
                _(
                    "If you close without saving, the changes you "
                    "have made will be lost"
                ),
                self._discard_for_parent,
                self._commit_for_parent,
                parent=getattr(self, "window", None),
            )
        return not getattr(self, "opened", False)

    def _prompt_on_window_close(self, args: tuple[Any, ...]) -> bool:
        """
        Ask "Save Changes?" when the user closes a changed editor with the
        window's close button, as primary editors do.

        Reference and secondary editors edit existing objects in place, so
        closing one must either save or undo the edits; doing either
        silently would surprise the user (#6910). The same applies when the
        editor itself is unchanged but an editor it opened still owes it
        work: closing tears that editor down too.

        :param args: The arguments ``close()`` was called with. A close
            from the window's close button carries the Gdk event.
        :returns: True if the dialog was shown; ``close()`` must then return
            True so GTK does not destroy the window itself.
        """
        from_window = any(isinstance(arg, Gdk.Event) for arg in args)
        if (
            not from_window
            or not getattr(self, "opened", False)
            or config.get("interface.dont-ask")
            or not (
                self.data_has_changed()  # type: ignore[attr-defined]
                or self._has_dependent_children()
            )
        ):
            return False
        SaveDialog(
            _("Save Changes?"),
            _("If you close without saving, the changes you have made will be lost"),
            self._discard_for_parent,
            lambda: self._save_with_dependent_children(None),
            parent=getattr(self, "window", None),
        )
        return True

    def _commit_for_parent(self) -> None:
        """
        Run this editor's own confirm handler, as its OK button would.
        """
        self._run_ok_function(None)

    def _discard_for_parent(self) -> None:
        """
        Drop this editor's edits and close it.
        """
        raise NotImplementedError

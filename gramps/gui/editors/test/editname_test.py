#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Gramps developers
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

"""Regression test for bug 12110: the Call-name validity indicator must be
re-evaluated when the *Given* name changes, not only when the Call field changes.

The indicator is a function of *both* fields (a call name is valid iff it is part
of the given name), so a change to the given name must re-fire the Call field's
validation.  The fix wires the given field's ``changed`` callback to a new
``_revalidate_call`` method on the editor (``editname.py`` and ``editperson.py``),
which re-runs the Call field's ``validate(force=True)``.

This test is import-light by design: it imports the editor *classes* (which load
fine headlessly) but never constructs a GUI window.  It drives the **production**
predicate ``_validate_call`` and the **production** trigger ``_revalidate_call``
(bound to a lightweight stub editor) through a **real** ``MonitoredEntry`` whose
``changed`` hook is wired exactly as ``_setup_fields`` wires it.  The only objects
faked are the GTK widgets themselves: the call field is a faithful re-creation of
``ValidatableMaskedEntry.validate()``'s dispatch *around the real predicate* — see
``gramps/gui/widgets/validatedmaskedentry.py`` validate() (empty text → valid,
otherwise emit "validate" → custom predicate → ``ValidationError`` ⇒ invalid).

Without the fix the editor class has no ``_revalidate_call`` method, so building the
harness raises ``AttributeError`` and the test goes red — exactly the regression
contract C4 asserts (red without the production change, green with it).
"""

import types
import unittest
from typing import ClassVar, Optional

from gramps.gui.editors.editname import EditName
from gramps.gui.editors.editperson import EditPerson
from gramps.gui.widgets.monitoredwidgets import MonitoredEntry


class _FakeEntry:
    """Stand-in for a plain Gtk.Entry (the Given field)."""

    def __init__(self, text=""):
        self._text = text

    def get_text(self):
        return self._text

    def set_text(self, text):
        self._text = text

    # MonitoredEntry.__init__ wires these on its obj; no-ops here.
    def connect(self, *args, **kwargs):
        return 0

    def set_editable(self, *args, **kwargs):
        pass


class _FakeValidatable:
    """Stand-in for the Call field's ValidatableMaskedEntry.

    Reproduces production ``validate()`` dispatch (validatedmaskedentry.py:1075)
    around the *real* editor predicate: empty text is always valid; otherwise the
    predicate is consulted and a returned ``ValidationError`` flips the field to
    invalid (red).  ``self.valid`` mirrors the red/black indicator.
    """

    def __init__(self, text, predicate):
        self._text = text
        self._predicate = predicate
        self.valid = None  # None = not yet validated

    def get_text(self):
        return self._text

    def set_text(self, text):
        self._text = text

    def validate(self, force=False):
        if not self._text:  # is_empty() branch -> valid
            self.valid = True
            return self._text
        error = self._predicate(self, self._text)
        if error:  # ValidationError -> set_invalid
            self.valid = False
            return None
        self.valid = True
        return self._text


def _build_harness(editor_cls, given_attr, call_attr, given="", call=""):
    """Assemble a stub editor that routes through the production methods.

    Binds the real ``_validate_call`` and ``_revalidate_call`` from *editor_cls*
    to a stub, and wires the given field as a **real** ``MonitoredEntry`` with
    ``changed=editor._revalidate_call`` — exactly as ``_setup_fields`` does.
    """
    editor = types.SimpleNamespace()
    # Real production predicate + trigger. If the fix is reverted, the class has
    # no _revalidate_call and this raises AttributeError -> the test goes red.
    editor._validate_call = editor_cls._validate_call.__get__(editor)
    editor._revalidate_call = editor_cls._revalidate_call.__get__(editor)

    given_entry = _FakeEntry(given)
    call_obj = _FakeValidatable(call, editor._validate_call)
    # The editor's call attribute exposes `.obj` (the validatable widget).
    setattr(editor, call_attr, types.SimpleNamespace(obj=call_obj))

    # The given field is a real MonitoredEntry, wired like production.
    given_field = MonitoredEntry(
        given_entry,
        lambda value: None,  # set_val: irrelevant to the validity indicator
        given_entry.get_text,  # get_val
        False,  # read_only
        changed=editor._revalidate_call,
    )
    setattr(editor, given_attr, given_field)
    return editor, given_entry, call_obj, given_field


def _edit_given(given_entry, given_field, new_text):
    """Simulate the user editing the Given field, driving the real
    MonitoredEntry._on_change -> changed -> _revalidate_call dispatch."""
    given_entry.set_text(new_text)
    given_field._on_change(given_entry)


class _CallNameRevalidationMixin:
    """Shared cases parameterised over the two editors that carry the bug."""

    editor_cls: ClassVar[Optional[type]] = None
    given_attr: ClassVar[Optional[str]] = None
    call_attr: ClassVar[Optional[str]] = None

    def test_given_change_clears_stale_red(self):
        # Case 1: Call="Jon" with empty Given is invalid (red)...
        editor, ge, call_obj, gf = _build_harness(
            self.editor_cls, self.given_attr, self.call_attr, given="", call="Jon"
        )
        call_obj.validate(force=True)
        self.assertFalse(call_obj.valid, "Call should start invalid (empty given)")

        # ...then filling Given to match must clear the red without touching Call.
        _edit_given(ge, gf, "Jon")
        self.assertTrue(
            call_obj.valid, "Editing Given to match must re-validate Call to black"
        )

    def test_given_change_sets_stale_black_to_red(self):
        # Case 2: Given="Marc", Call="Marc" is valid (black)...
        editor, ge, call_obj, gf = _build_harness(
            self.editor_cls,
            self.given_attr,
            self.call_attr,
            given="Marc",
            call="Marc",
        )
        call_obj.validate(force=True)
        self.assertTrue(call_obj.valid, "Call should start valid (given matches)")

        # ...then changing Given so it no longer contains the call name -> red.
        _edit_given(ge, gf, "Paul")
        self.assertFalse(
            call_obj.valid, "Changing Given away from the call name must turn Call red"
        )

    def test_hyphenated_given_part_is_valid(self):
        # The predicate also splits hyphenated given parts; exercise that the
        # revalidation honours it (Given "Jean-Marc" -> call "Marc" valid).
        editor, ge, call_obj, gf = _build_harness(
            self.editor_cls, self.given_attr, self.call_attr, given="", call="Marc"
        )
        call_obj.validate(force=True)
        self.assertFalse(call_obj.valid)
        _edit_given(ge, gf, "Jean-Marc")
        self.assertTrue(call_obj.valid)


class TestEditNameCallRevalidation(_CallNameRevalidationMixin, unittest.TestCase):
    editor_cls = EditName
    given_attr = "given_field"
    call_attr = "call_field"


class TestEditPersonCallRevalidation(_CallNameRevalidationMixin, unittest.TestCase):
    editor_cls = EditPerson
    given_attr = "given"
    call_attr = "call"


if __name__ == "__main__":
    unittest.main()

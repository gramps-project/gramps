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

"""
Regression test for Mantis 13716 — sidebar-filter "Type" selector is stale.

A view's sidebar filter ("Type" selector — the same widget the Filter Gramplet
hosts) reads the database's custom types only once, when the filter widget is
built, and never refreshes them.  A custom type added to the already-open
database (for example the "GEDCOM import" Note type created by importing a
GEDCOM with errors) therefore never appears in the selector until the
gramplet/view is torn down and rebuilt.  The editor dialogs avoid this by
rebuilding their type selector from the database every time they are shown.

The fix moves the repopulate orchestration into the GUI-free
:class:`~gramps.gui.filters.sidebar._typefilterlist.TypeFilterList`, which the
shared :class:`~gramps.gui.filters.sidebar.SidebarFilter` wires every
database-derived type selector to via :meth:`SidebarFilter.add_type_filter` /
:meth:`SidebarFilter._register_type_filters`.  Each refresh re-reads the *live*
database, so types added after construction are offered.

This test drives the **production** repopulate path:

* :class:`TypeFilterList.refresh` is the shared unit the production
  ``SidebarFilter`` routes through; and
* the production ``NoteSidebarFilter._register_type_filters`` /
  ``SidebarFilter.add_type_filter`` wiring is exercised directly, with test
  doubles standing in only for the GUI selector widget and the database state
  (so the test runs headless, without a display).

It must be GUI-import-free at instantiation: it imports the sidebar classes
(which only *define* widget classes at import time) but never *constructs* a Gtk
widget, building the filter object via ``__new__`` instead.
"""

import unittest

from gramps.gui.filters.sidebar._typefilterlist import TypeFilterList
from gramps.gui.filters.sidebar import SidebarFilter, NoteSidebarFilter
from gramps.gui.filters.sidebar import RepoSidebarFilter


class _FakeDb:
    """Minimal stand-in for the database's custom-type accessors.

    ``note_types`` mutates to model a custom type added to the already-open
    database (e.g. by a GEDCOM import) after the filter was built.
    ``repository_types`` does the same for the repository sidebar filter, and is
    deliberately *disjoint* from ``event_types`` so a test can prove the
    repository filter reads its own (repository) type set, not the event one.
    """

    def __init__(self, note_types, repository_types=None, event_types=None):
        self.note_types = list(note_types)
        self.repository_types = list(
            repository_types if repository_types is not None else []
        )
        self.event_types = list(event_types if event_types is not None else [])

    def get_note_types(self):
        # Returns the *current* set every call — like the real db, which
        # recomputes custom types from the objects it holds.
        return list(self.note_types)

    def get_repository_types(self):
        return list(self.repository_types)

    def get_event_types(self):
        return list(self.event_types)


class _FakeDbState:
    def __init__(self, db):
        self.db = db

    def is_open(self):
        return True


class _RecordingCombo:
    """Stand-in for the Gtk combo box the type selector wraps.

    Only ``connect`` is used by ``add_type_filter`` (to hook the drop-down's
    popup); recording it is enough — no GUI is created.
    """

    def __init__(self):
        self.connected = []

    def connect(self, signal, handler):
        self.connected.append(signal)


class _RecordingMenu:
    """Stand-in for the ``MonitoredDataType`` wrapping the selector.

    ``rebuild`` is the production ``apply`` callable; it records the custom
    values it was last handed, which are exactly the custom types the selector
    would offer.
    """

    def __init__(self):
        self.obj = _RecordingCombo()
        self.offered = None

    def rebuild(self, custom_values):
        self.offered = list(custom_values)


class SidebarFilterTypeRefreshTest(unittest.TestCase):
    """Mantis 13716: the Type selector must reflect the database's current
    custom types after they change, via the production repopulate path."""

    def _make_note_filter(self, db):
        """Build a NoteSidebarFilter without running ``__init__``.

        ``__init__`` builds real Gtk widgets, which needs a live display.  The
        repopulate path under test only needs the type-filter registry, the
        db state and the (doubled) selector menu, so we set just those and run
        the production ``_register_type_filters`` wiring.
        """
        flt = NoteSidebarFilter.__new__(NoteSidebarFilter)
        flt.dbstate = _FakeDbState(db)
        flt._type_filters = TypeFilterList()
        flt.event_menu = _RecordingMenu()
        flt._register_type_filters()  # production registration wiring
        return flt

    def test_type_selector_reflects_new_custom_type_after_refresh(self):
        """A custom Note type added to the open db is offered after a refresh,
        but is absent beforehand (the bug)."""
        db = _FakeDb(["General", "Research", "Citation"])
        flt = self._make_note_filter(db)

        # Initial presentation: the selector offers the current custom types.
        flt._type_filters.refresh()
        self.assertIn("Research", flt.event_menu.offered)
        self.assertNotIn("GEDCOM import", flt.event_menu.offered)

        # A GEDCOM import creates a new custom Note type in the *already-open*
        # database.
        db.note_types.append("GEDCOM import")

        # Re-presenting the selector (the production repopulate path) must now
        # offer the new custom type — without recreating the filter widget.
        flt._type_filters.refresh()
        self.assertIn(
            "GEDCOM import",
            flt.event_menu.offered,
            "Type selector did not pick up a custom type added to the open "
            "database (Mantis 13716).",
        )

    def test_refresh_reflects_removed_custom_type(self):
        """The selector also drops a custom type no longer in the database —
        it tracks the current set, not an ever-growing snapshot."""
        db = _FakeDb(["General", "Obsolete"])
        flt = self._make_note_filter(db)

        flt._type_filters.refresh()
        self.assertIn("Obsolete", flt.event_menu.offered)

        db.note_types.remove("Obsolete")
        flt._type_filters.refresh()
        self.assertNotIn("Obsolete", flt.event_menu.offered)

    def test_typefilterlist_refetches_live_source(self):
        """The shared TypeFilterList unit re-reads its source on every refresh
        rather than caching a construction-time snapshot."""
        source = {"types": ["a"]}
        applied = []
        tfl = TypeFilterList()
        tfl.register(lambda: list(source["types"]), applied.append)

        tfl.refresh()
        self.assertEqual(applied[-1], ["a"])

        source["types"] = ["a", "b"]
        tfl.refresh()
        self.assertEqual(applied[-1], ["a", "b"])

    def _make_repo_filter(self, db):
        """Build a RepoSidebarFilter without running ``__init__`` (same headless
        seam as ``_make_note_filter``)."""
        flt = RepoSidebarFilter.__new__(RepoSidebarFilter)
        flt.dbstate = _FakeDbState(db)
        flt._type_filters = TypeFilterList()
        flt.event_menu = _RecordingMenu()
        flt._register_type_filters()  # production registration wiring
        return flt

    def test_repo_filter_reads_repository_types_not_event_types(self):
        """The repository sidebar filter's Type selector must offer the
        database's *repository* custom types — not the event types (the
        pre-existing wrong source carried by the first 13716 attempt)."""
        db = _FakeDb(
            note_types=[],
            repository_types=["Web Archive"],
            event_types=["Baptism"],
        )
        flt = self._make_repo_filter(db)

        flt._type_filters.refresh()
        self.assertIn(
            "Web Archive",
            flt.event_menu.offered,
            "Repository Type selector did not offer the database's repository "
            "custom types.",
        )
        self.assertNotIn(
            "Baptism",
            flt.event_menu.offered,
            "Repository Type selector offered event types — wrong db source.",
        )


if __name__ == "__main__":
    unittest.main()

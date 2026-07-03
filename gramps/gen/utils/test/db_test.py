#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Doug Blank
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

"""Tests for event_creates_cycle in gen/utils/db.py.

# python3 -m unittest gramps.gen.utils.test.db_test -v
"""

# -------------------------------------------------------------------------
#
# Standard python modules
#
# -------------------------------------------------------------------------
import unittest

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.errors import HandleError
from gramps.gen.lib import Event
from gramps.gen.utils.db import event_creates_cycle


# -------------------------------------------------------------------------
#
# FakeCycleDb
#
# -------------------------------------------------------------------------
class FakeCycleDb:
    """
    Minimal database stub exposing only get_event_from_handle, keyed on
    a plain dict of handle -> Event.
    """

    def __init__(self, events):
        self.events = events

    def get_event_from_handle(self, handle):
        if handle not in self.events:
            raise HandleError(f"Handle {handle} not found")
        return self.events[handle]


def _make_event(handle, super_event_list=None):
    event = Event()
    event.set_handle(handle)
    event.set_super_event_list(super_event_list or [])
    return event


# -------------------------------------------------------------------------
#
# TestEventCreatesCycle
#
# -------------------------------------------------------------------------
class TestEventCreatesCycle(unittest.TestCase):
    """Tests for event_creates_cycle."""

    def test_no_cycle_for_unrelated_events(self):
        db = FakeCycleDb(
            {
                "a": _make_event("a"),
                "b": _make_event("b"),
            }
        )
        self.assertFalse(event_creates_cycle(db, "a", "b"))

    def test_direct_self_reference_is_a_cycle(self):
        db = FakeCycleDb({"a": _make_event("a")})
        self.assertTrue(event_creates_cycle(db, "a", "a"))

    def test_direct_cycle_detected(self):
        # b is already a super-event of a; making b a sub-event of a
        # (i.e. a a super-event of b) would close a 2-cycle.
        db = FakeCycleDb(
            {
                "a": _make_event("a", ["b"]),
                "b": _make_event("b"),
            }
        )
        self.assertTrue(event_creates_cycle(db, "b", "a"))

    def test_indirect_cycle_detected(self):
        # a -> b -> c (c is a's ancestor via b). Making c a sub-event of a
        # would close the loop a -> b -> c -> a.
        db = FakeCycleDb(
            {
                "a": _make_event("a", ["b"]),
                "b": _make_event("b", ["c"]),
                "c": _make_event("c"),
            }
        )
        self.assertTrue(event_creates_cycle(db, "c", "a"))

    def test_dag_shared_ancestor_is_not_a_cycle(self):
        # Both b and c are sub-events of a (a DAG, not a cycle):
        # a
        # |-- b
        # |-- c
        # Adding a as a super-event of neither b nor c creates a cycle;
        # proposing b as a super-event of c (unrelated branch) is fine too.
        db = FakeCycleDb(
            {
                "a": _make_event("a"),
                "b": _make_event("b", ["a"]),
                "c": _make_event("c", ["a"]),
            }
        )
        self.assertFalse(event_creates_cycle(db, "c", "b"))

    def test_missing_handle_is_ignored(self):
        db = FakeCycleDb({"a": _make_event("a", ["missing"])})
        self.assertFalse(event_creates_cycle(db, "z", "a"))


if __name__ == "__main__":
    unittest.main()

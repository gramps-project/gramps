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

"""Tests for Event.super_event_list (sub-events feature).

# python3 -m unittest gramps.gen.lib.test.event_test -v
"""

import unittest

from gramps.gen.lib.event import Event
from gramps.gen.lib.json_utils import data_to_object, object_to_data, remove_object


# -------------------------------------------------------------------------
#
# TestEventSuperEventList
#
# -------------------------------------------------------------------------
class TestEventSuperEventList(unittest.TestCase):
    """Tests for Event.super_event_list."""

    def test_new_event_has_empty_super_event_list(self):
        """A freshly created Event has an empty super_event_list."""
        event = Event()
        self.assertEqual(event.get_super_event_list(), [])

    def test_copy_constructor_copies_super_event_list(self):
        """Copying an Event copies its super_event_list, not a shared reference."""
        source = Event()
        source.add_super_event("super-h1")
        copy = Event(source)
        self.assertEqual(copy.get_super_event_list(), ["super-h1"])
        copy.add_super_event("super-h2")
        self.assertEqual(source.get_super_event_list(), ["super-h1"])

    def test_add_super_event(self):
        """add_super_event appends a new handle."""
        event = Event()
        event.add_super_event("super-h1")
        self.assertEqual(event.get_super_event_list(), ["super-h1"])

    def test_add_super_event_no_duplicate(self):
        """add_super_event does not add the same handle twice."""
        event = Event()
        event.add_super_event("super-h1")
        event.add_super_event("super-h1")
        self.assertEqual(event.get_super_event_list(), ["super-h1"])

    def test_add_super_event_rejects_self_reference(self):
        """add_super_event refuses to add the event's own handle."""
        event = Event()
        event.set_handle("self-h1")
        event.add_super_event("self-h1")
        self.assertEqual(event.get_super_event_list(), [])

    def test_set_super_event_list(self):
        """set_super_event_list replaces the whole list."""
        event = Event()
        event.set_super_event_list(["h1", "h2"])
        self.assertEqual(event.get_super_event_list(), ["h1", "h2"])

    def test_has_handle_reference(self):
        """has_handle_reference("Event", ...) checks super_event_list."""
        event = Event()
        event.add_super_event("super-h1")
        self.assertTrue(event.has_handle_reference("Event", "super-h1"))
        self.assertFalse(event.has_handle_reference("Event", "super-h2"))

    def test_remove_handle_references(self):
        """remove_handle_references("Event", ...) drops matching handles."""
        event = Event()
        event.set_super_event_list(["h1", "h2", "h3"])
        event.remove_handle_references("Event", ["h1", "h3"])
        self.assertEqual(event.get_super_event_list(), ["h2"])

    def test_replace_handle_reference(self):
        """replace_handle_reference("Event", ...) swaps a super-event handle."""
        event = Event()
        event.set_super_event_list(["h1", "h2"])
        event.replace_handle_reference("Event", "h1", "h3")
        self.assertEqual(event.get_super_event_list(), ["h3", "h2"])

    def test_replace_handle_reference_dedups(self):
        """Replacing a handle that collides with an existing one is deduped."""
        event = Event()
        event.set_super_event_list(["h1", "h2"])
        event.replace_handle_reference("Event", "h1", "h2")
        self.assertEqual(event.get_super_event_list(), ["h2"])

    def test_get_referenced_handles_includes_super_events(self):
        """get_referenced_handles reports ("Event", handle) for super-events."""
        event = Event()
        event.set_super_event_list(["h1", "h2"])
        refs = event.get_referenced_handles()
        self.assertIn(("Event", "h1"), refs)
        self.assertIn(("Event", "h2"), refs)

    def test_merge_unions_super_event_list(self):
        """merge() unions the acquisition's super_event_list into self."""
        phoenix = Event()
        phoenix.set_super_event_list(["h1"])
        titanic = Event()
        titanic.set_super_event_list(["h2"])
        phoenix.merge(titanic)
        self.assertEqual(phoenix.get_super_event_list(), ["h1", "h2"])

    def test_merge_dedups_super_event_list(self):
        """merge() does not duplicate a super-event present on both sides."""
        phoenix = Event()
        phoenix.set_super_event_list(["h1"])
        titanic = Event()
        titanic.set_super_event_list(["h1"])
        phoenix.merge(titanic)
        self.assertEqual(phoenix.get_super_event_list(), ["h1"])

    def test_merge_drops_self_reference(self):
        """merge() will not let the merged event become its own super-event."""
        phoenix = Event()
        phoenix.set_handle("new-h1")
        phoenix.set_super_event_list([])
        titanic = Event()
        titanic.set_super_event_list(["new-h1"])
        phoenix.merge(titanic)
        self.assertEqual(phoenix.get_super_event_list(), [])

    def test_serialize_round_trip(self):
        """super_event_list survives a serialize()/unserialize() round trip."""
        event = Event()
        event.set_super_event_list(["h1", "h2"])
        restored = Event()
        restored.unserialize(event.serialize())
        self.assertEqual(restored.get_super_event_list(), ["h1", "h2"])

    def test_json_round_trip(self):
        """super_event_list survives get_object_state/set_object_state (JSON path)."""
        event = Event()
        event.set_super_event_list(["h1", "h2"])
        data = remove_object(object_to_data(event))
        restored = data_to_object(data)
        self.assertEqual(restored.get_super_event_list(), ["h1", "h2"])

    def test_get_schema_declares_super_event_list(self):
        """get_schema() documents the super_event_list field."""
        schema = Event.get_schema()
        self.assertIn("super_event_list", schema["properties"])


if __name__ == "__main__":
    unittest.main()

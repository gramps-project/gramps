#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026      John Vitlin
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#

"""Tests for the Records calculations."""

import unittest
from unittest.mock import MagicMock

from gramps.gen.lib import EventType
from gramps.plugins.lib.librecords import _count_person_marriages


class TestPersonMarriageCount(unittest.TestCase):
    """Test the counting of marriage events in family records."""

    def test_one_marriage(self):
        """A family with one Marriage event counts as one marriage."""
        db = MagicMock()
        person = MagicMock()
        family = MagicMock()
        event_ref = MagicMock()
        event = MagicMock()

        person.get_family_handle_list.return_value = ["family1"]
        db.get_family_from_handle.return_value = family

        family.get_event_ref_list.return_value = [event_ref]
        event_ref.get_role.return_value.is_family.return_value = True
        event_ref.ref = "event1"

        db.get_event_from_handle.return_value = event
        event.get_type.return_value = EventType(EventType.MARRIAGE)

        self.assertEqual(_count_person_marriages(db, person), 1)

    def test_alternate_marriage(self):
        """An Alternate Marriage event counts as one marriage."""
        db = MagicMock()
        person = MagicMock()
        family = MagicMock()
        event_ref = MagicMock()
        event = MagicMock()

        person.get_family_handle_list.return_value = ["family1"]
        db.get_family_from_handle.return_value = family

        family.get_event_ref_list.return_value = [event_ref]
        event_ref.get_role.return_value.is_family.return_value = True
        event_ref.ref = "event1"

        db.get_event_from_handle.return_value = event
        event.get_type.return_value = EventType(EventType.MARR_ALT)

        self.assertEqual(_count_person_marriages(db, person), 1)

    def test_engagement_not_counted(self):
        """An Engagement event does not count as a marriage."""
        db = MagicMock()
        person = MagicMock()
        family = MagicMock()
        event_ref = MagicMock()
        event = MagicMock()

        person.get_family_handle_list.return_value = ["family1"]
        db.get_family_from_handle.return_value = family

        family.get_event_ref_list.return_value = [event_ref]
        event_ref.get_role.return_value.is_family.return_value = True
        event_ref.ref = "event1"

        db.get_event_from_handle.return_value = event
        event.get_type.return_value = EventType(EventType.ENGAGEMENT)

        self.assertEqual(_count_person_marriages(db, person), 0)

    def test_multiple_marriage_events_one_family(self):
        """Multiple marriage events in one family count as one marriage."""
        db = MagicMock()
        person = MagicMock()
        family = MagicMock()

        person.get_family_handle_list.return_value = ["family1"]
        db.get_family_from_handle.return_value = family

        marriage_ref = MagicMock()
        marriage_ref.ref = "event1"
        marriage_ref.get_role.return_value.is_family.return_value = True

        alternate_ref = MagicMock()
        alternate_ref.ref = "event2"
        alternate_ref.get_role.return_value.is_family.return_value = True

        family.get_event_ref_list.return_value = [
            marriage_ref,
            alternate_ref,
        ]

        marriage_event = MagicMock()
        marriage_event.get_type.return_value = EventType(EventType.MARRIAGE)

        alternate_event = MagicMock()
        alternate_event.get_type.return_value = EventType(EventType.MARR_ALT)

        db.get_event_from_handle.side_effect = {
            "event1": marriage_event,
            "event2": alternate_event,
        }.get

        self.assertEqual(_count_person_marriages(db, person), 1)

    def test_two_separate_married_families(self):
        """Two married family records count as two marriages."""
        db = MagicMock()
        person = MagicMock()

        person.get_family_handle_list.return_value = [
            "family1",
            "family2",
        ]

        families = {}
        events = {}

        for number in (1, 2):
            family = MagicMock()
            event_ref = MagicMock()
            event = MagicMock()

            event_ref.ref = f"event{number}"
            event_ref.get_role.return_value.is_family.return_value = True
            family.get_event_ref_list.return_value = [event_ref]
            event.get_type.return_value = EventType(EventType.MARRIAGE)

            families[f"family{number}"] = family
            events[f"event{number}"] = event

        db.get_family_from_handle.side_effect = families.get
        db.get_event_from_handle.side_effect = events.get

        self.assertEqual(_count_person_marriages(db, person), 2)

    def test_family_without_marriage_event(self):
        """A family without a marriage event does not count."""
        db = MagicMock()
        person = MagicMock()
        family = MagicMock()
        event_ref = MagicMock()
        event = MagicMock()

        person.get_family_handle_list.return_value = ["family1"]
        db.get_family_from_handle.return_value = family

        family.get_event_ref_list.return_value = [event_ref]
        event_ref.get_role.return_value.is_family.return_value = True
        event_ref.ref = "event1"

        db.get_event_from_handle.return_value = event
        event.get_type.return_value = EventType(EventType.DIVORCE)

        self.assertEqual(_count_person_marriages(db, person), 0)

    def test_missing_family(self):
        """A family that cannot be retrieved does not count."""
        db = MagicMock()
        person = MagicMock()

        person.get_family_handle_list.return_value = ["family1"]
        db.get_family_from_handle.return_value = None

        self.assertEqual(_count_person_marriages(db, person), 0)

    def test_missing_event(self):
        """An event that cannot be retrieved does not count."""
        db = MagicMock()
        person = MagicMock()
        family = MagicMock()
        event_ref = MagicMock()

        person.get_family_handle_list.return_value = ["family1"]
        db.get_family_from_handle.return_value = family

        family.get_event_ref_list.return_value = [event_ref]
        event_ref.get_role.return_value.is_family.return_value = True
        event_ref.ref = "event1"

        db.get_event_from_handle.return_value = None

        self.assertEqual(_count_person_marriages(db, person), 0)


if __name__ == "__main__":
    unittest.main()

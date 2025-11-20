# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2025       David Straub
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

"""Test that ...Like union types work with both actual objects and DataDict."""

import unittest

from ..types import (
    PersonLike,
    FamilyLike,
    EventLike,
    SourceLike,
    CitationLike,
    MediaLike,
    PlaceLike,
    RepositoryLike,
    NoteLike,
    TagLike,
    AddressLike,
)


def get_handle(
    obj: (
        PersonLike
        | FamilyLike
        | EventLike
        | SourceLike
        | CitationLike
        | MediaLike
        | PlaceLike
        | RepositoryLike
        | NoteLike
        | TagLike
    ),
) -> str:
    """Helper function that accepts any primary object type and returns handle."""
    return obj.handle


def get_gramps_id(
    obj: (
        PersonLike
        | FamilyLike
        | EventLike
        | SourceLike
        | CitationLike
        | MediaLike
        | PlaceLike
        | RepositoryLike
        | NoteLike
    ),
) -> str:
    """Helper to get gramps_id from objects that have it."""
    return obj.gramps_id


def get_first_address_city(person: PersonLike) -> str | None:
    """Get city from first address if it exists."""
    if person.address_list:
        return person.address_list[0].city
    return None


def create_person(handle: str, gramps_id: str) -> PersonLike:
    """Create and return a Person as PersonLike."""
    from ..lib.person import Person

    person = Person()
    person.handle = handle
    person.gramps_id = gramps_id
    return person


def create_event(handle: str, gramps_id: str) -> EventLike:
    """Create and return an Event as EventLike."""
    from ..lib.event import Event

    event = Event()
    event.handle = handle
    event.gramps_id = gramps_id
    return event


class ProtocolTest(unittest.TestCase):
    """Test that ...Like types work with both actual objects and DataDict."""

    def test_person_like(self):
        """Test PersonLike accepts Person and DataDict, with attribute access."""
        from ..lib.person import Person
        from ..lib.address import Address
        from ..lib.json_utils import object_to_data

        # Create person with address
        person = Person()
        person.handle = "test123"
        person.gramps_id = "I0001"
        addr = Address()
        addr.city = "Boston"
        person.address_list.append(addr)

        # Test with actual Person
        self.assertEqual(get_handle(person), "test123")
        self.assertEqual(get_gramps_id(person), "I0001")
        self.assertEqual(get_first_address_city(person), "Boston")

        # Test with DataDict - object_to_data not typed, so cast
        data_dict = object_to_data(person)
        self.assertEqual(get_handle(data_dict), "test123")  # type: ignore[arg-type]
        self.assertEqual(get_gramps_id(data_dict), "I0001")  # type: ignore[arg-type]
        self.assertEqual(get_first_address_city(data_dict), "Boston")  # type: ignore[arg-type]

        # Test return types
        result: PersonLike = create_person("p1", "P0001")
        self.assertEqual(result.handle, "p1")

    def test_event_like(self):
        """Test EventLike accepts Event and DataDict."""
        from ..lib.event import Event
        from ..lib.json_utils import object_to_data

        event = Event()
        event.handle = "evt123"
        event.gramps_id = "E0001"

        self.assertEqual(get_handle(event), "evt123")
        self.assertEqual(get_gramps_id(event), "E0001")

        data_dict = object_to_data(event)
        self.assertEqual(get_handle(data_dict), "evt123")  # type: ignore[arg-type]
        self.assertEqual(get_gramps_id(data_dict), "E0001")  # type: ignore[arg-type]

        result: EventLike = create_event("e1", "E0001")
        self.assertEqual(result.handle, "e1")

    def test_all_primary_types(self):
        """Test that all primary types work with get_handle."""
        from ..lib.person import Person
        from ..lib.family import Family
        from ..lib.event import Event
        from ..lib.src import Source
        from ..lib.citation import Citation
        from ..lib.media import Media
        from ..lib.place import Place
        from ..lib.repo import Repository
        from ..lib.note import Note
        from ..lib.tag import Tag

        objects = [
            Person(),
            Family(),
            Event(),
            Source(),
            Citation(),
            Media(),
            Place(),
            Repository(),
            Note(),
            Tag(),
        ]

        for i, obj in enumerate(objects):
            obj.handle = f"handle{i}"
            self.assertEqual(get_handle(obj), f"handle{i}")

    def test_runtime_protocol_checks(self):
        """Test that actual objects match their protocols at runtime."""
        from ..lib.person import Person
        from ..lib.family import Family
        from ..lib.event import Event
        from ..lib.address import Address
        from ..lib.json_utils import DataDict

        # Test Person matches PersonLike protocol
        person = Person()
        person.handle = "p1"
        self.assertIsInstance(person, PersonLike)

        # Test DataDict provides attribute access through __getattr__
        person_dict = DataDict(person)
        # DataDict won't pass isinstance check because protocols check actual attributes,
        # not __getattr__, but we can verify attribute access works
        self.assertEqual(person_dict.handle, "p1")
        self.assertTrue(hasattr(person_dict, "handle"))

        # Test Family matches FamilyLike protocol
        family = Family()
        family.handle = "f1"
        self.assertIsInstance(family, FamilyLike)

        family_dict = DataDict(family)
        self.assertEqual(family_dict.handle, "f1")

        # Test Event matches EventLike protocol
        event = Event()
        event.handle = "e1"
        self.assertIsInstance(event, EventLike)

        event_dict = DataDict(event)
        self.assertEqual(event_dict.handle, "e1")

        # Test nested protocol: Address matches AddressLike
        address = Address()
        address.city = "Boston"
        self.assertIsInstance(address, AddressLike)


if __name__ == "__main__":
    unittest.main()

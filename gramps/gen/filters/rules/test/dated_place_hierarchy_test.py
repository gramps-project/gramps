#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Doug Blank <doug.blank@gmail.com>
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
Regression tests for filter rules that match a Place by substring on a
date-ranged place hierarchy (e.g. Schleswig-Holstein was part of Denmark
before 1865, Prussia from 1867 to 1871, and Germany after 1871).

These rules resolve the displayed place name by walking the place's
PlaceRef list, and must use the event's own date to pick the historically
correct parent, rather than defaulting to today's date.
"""

import unittest

from ....datehandler import parser
from ....db import DbTxn
from ....db.utils import make_database
from ....lib import (
    Event,
    EventRef,
    EventType,
    Family,
    Person,
    Place,
    PlaceName,
    PlaceRef,
)
from ..event import HasData, HasEvent as EventHasEvent
from ..person import HasBirth, HasDeath, HasFamilyEvent


def _make_db():
    """Create and return a fresh in-memory SQLite database."""
    db = make_database("sqlite")
    db.load(":memory:")
    return db


class DatedPlaceHierarchyTest(unittest.TestCase):
    """
    Tests that place-substring filters use the event's date, not today's
    date, to resolve a date-ranged place hierarchy.
    """

    def setUp(self):
        """Build the Schleswig-Holstein / Denmark / Prussia / Germany hierarchy."""
        self.db = _make_db()
        with DbTxn("build hierarchy", self.db) as trans:
            self.denmark_handle = self._add_place(trans, "Denmark")
            self.prussia_handle = self._add_place(trans, "Prussia")
            self.germany_handle = self._add_place(trans, "Germany")

            sh = Place()
            sh.set_name(PlaceName(value="Schleswig-Holstein"))
            sh.add_placeref(self._make_placeref(self.denmark_handle, "before 1865"))
            sh.add_placeref(
                self._make_placeref(self.prussia_handle, "from 1867 to 1871")
            )
            sh.add_placeref(self._make_placeref(self.germany_handle, "after 1871"))
            self.sh_handle = self.db.add_place(sh, trans)

    def tearDown(self):
        """Close the in-memory database."""
        self.db.close()

    def _add_place(self, trans, name):
        """Create a place with the given name and return its handle."""
        place = Place()
        place.set_name(PlaceName(value=name))
        return self.db.add_place(place, trans)

    def _make_placeref(self, handle, date_str):
        """Return a PlaceRef to handle, valid over the given date string."""
        placeref = PlaceRef()
        placeref.set_reference_handle(handle)
        placeref.set_date_object(parser.parse(date_str))
        return placeref

    def _add_event(self, trans, event_type, date_str):
        """Create an event of event_type at Schleswig-Holstein and return its handle."""
        event = Event()
        event.set_type(EventType(event_type))
        event.set_date_object(parser.parse(date_str))
        event.set_place_handle(self.sh_handle)
        return self.db.add_event(event, trans)

    def test_hasbirth_before_1865_matches_denmark_not_germany(self):
        """A person born in 1854 should match Place=Denmark, not Germany."""
        with DbTxn("add person", self.db) as trans:
            birth_handle = self._add_event(trans, EventType.BIRTH, "1854")
            person = Person()
            birth_ref = EventRef()
            birth_ref.set_reference_handle(birth_handle)
            person.set_birth_ref(birth_ref)
            person_handle = self.db.add_person(person, trans)
        person = self.db.get_person_from_handle(person_handle)

        rule = HasBirth(["", "Germany", ""])
        rule.prepare(self.db, None)
        self.assertFalse(rule.apply_to_one(self.db, person))

        rule = HasBirth(["", "Denmark", ""])
        rule.prepare(self.db, None)
        self.assertTrue(rule.apply_to_one(self.db, person))

    def test_hasbirth_after_1871_matches_germany_not_denmark(self):
        """A person born in 1880 should match Place=Germany, not Denmark."""
        with DbTxn("add person", self.db) as trans:
            birth_handle = self._add_event(trans, EventType.BIRTH, "1880")
            person = Person()
            birth_ref = EventRef()
            birth_ref.set_reference_handle(birth_handle)
            person.set_birth_ref(birth_ref)
            person_handle = self.db.add_person(person, trans)
        person = self.db.get_person_from_handle(person_handle)

        rule = HasBirth(["", "Germany", ""])
        rule.prepare(self.db, None)
        self.assertTrue(rule.apply_to_one(self.db, person))

        rule = HasBirth(["", "Denmark", ""])
        rule.prepare(self.db, None)
        self.assertFalse(rule.apply_to_one(self.db, person))

    def test_hasdeath_before_1865_matches_denmark_not_germany(self):
        """A person who died in 1860 should match Place=Denmark, not Germany."""
        with DbTxn("add person", self.db) as trans:
            death_handle = self._add_event(trans, EventType.DEATH, "1860")
            person = Person()
            death_ref = EventRef()
            death_ref.set_reference_handle(death_handle)
            person.set_death_ref(death_ref)
            person_handle = self.db.add_person(person, trans)
        person = self.db.get_person_from_handle(person_handle)

        rule = HasDeath(["", "Germany", ""])
        rule.prepare(self.db, None)
        self.assertFalse(rule.apply_to_one(self.db, person))

        rule = HasDeath(["", "Denmark", ""])
        rule.prepare(self.db, None)
        self.assertTrue(rule.apply_to_one(self.db, person))

    def test_hasfamilyevent_before_1865_matches_denmark_not_germany(self):
        """A marriage in 1854 should match Place=Denmark, not Germany."""
        with DbTxn("add family", self.db) as trans:
            marriage_handle = self._add_event(trans, EventType.MARRIAGE, "1854")
            family = Family()
            marriage_ref = EventRef()
            marriage_ref.set_reference_handle(marriage_handle)
            family.add_event_ref(marriage_ref)
            family_handle = self.db.add_family(family, trans)

            person = Person()
            person.add_family_handle(family_handle)
            person_handle = self.db.add_person(person, trans)
        person = self.db.get_person_from_handle(person_handle)

        rule = HasFamilyEvent(["", "", "Germany", ""])
        rule.prepare(self.db, None)
        self.assertFalse(rule.apply_to_one(self.db, person))

        rule = HasFamilyEvent(["", "", "Denmark", ""])
        rule.prepare(self.db, None)
        self.assertTrue(rule.apply_to_one(self.db, person))

    def test_hasevent_before_1865_matches_denmark_not_germany(self):
        """A generic event in 1854 should match Place=Denmark, not Germany."""
        with DbTxn("add event", self.db) as trans:
            event_handle = self._add_event(trans, EventType.CENSUS, "1854")
        event = self.db.get_event_from_handle(event_handle)

        rule = EventHasEvent(["", "", "Germany", "", ""])
        rule.prepare(self.db, None)
        self.assertFalse(rule.apply_to_one(self.db, event))

        rule = EventHasEvent(["", "", "Denmark", "", ""])
        rule.prepare(self.db, None)
        self.assertTrue(rule.apply_to_one(self.db, event))

    def test_hasdata_before_1865_matches_denmark_not_germany(self):
        """HasData (event/_hasdata.py) should also resolve by the event's date."""
        with DbTxn("add event", self.db) as trans:
            event_handle = self._add_event(trans, EventType.CENSUS, "1854")
        event = self.db.get_event_from_handle(event_handle)

        rule = HasData(["", "", "Germany", ""])
        rule.prepare(self.db, None)
        self.assertFalse(rule.apply_to_one(self.db, event))

        rule = HasData(["", "", "Denmark", ""])
        rule.prepare(self.db, None)
        self.assertTrue(rule.apply_to_one(self.db, event))


if __name__ == "__main__":
    unittest.main()

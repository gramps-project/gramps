#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2025
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
Tests for the get_age birth/death date-fallback behaviour
(gramps.gen.utils.db.get_age).
"""

import unittest

from ...db import DbTxn
from ...db.utils import make_database
from ...lib import Date, Event, EventRef, EventType, Person, Place
from ..db import get_age


def _make_db():
    """Create and return a fresh in-memory SQLite database."""
    db = make_database("sqlite")
    db.load(":memory:")
    return db


def _add_event(db, trans, event_type, year=0, month=0, day=0, place=None):
    """Create an event of *event_type* with the given date; return its handle."""
    event = Event()
    event.set_type(EventType(event_type))
    date = Date()
    if year or month or day:
        date.set_yr_mon_day(year, month, day)
    event.set_date_object(date)
    if place is not None:
        event.set_place_handle(place)
    return db.add_event(event, trans)


class TestGetAgeFallback(unittest.TestCase):
    """
    A dateless primary Birth event must not mask a dated Baptism
    (birth-fallback) event when computing a person's age.
    """

    def setUp(self):
        self.db = _make_db()

    def tearDown(self):
        self.db.close()

    def _age(self, person_handle):
        return get_age(self.db, self.db.get_person_from_handle(person_handle))

    def test_dateless_birth_falls_back_to_dated_baptism(self):
        """
        Person with a dateless (place-only) Birth event, a dated Baptism
        event, and a dated Death event: get_age must compute the age from the
        Baptism date rather than returning None.
        """
        with DbTxn("test", self.db) as trans:
            place = Place()
            place.set_title("Somewhere")
            place_handle = self.db.add_place(place, trans)

            # Primary Birth event: a place, but no date.
            birth_handle = _add_event(
                self.db, trans, EventType.BIRTH, place=place_handle
            )
            birth_ref = EventRef()
            birth_ref.set_reference_handle(birth_handle)

            # Baptism (birth-fallback) event with a usable date.
            baptism_handle = _add_event(
                self.db, trans, EventType.BAPTISM, year=1850, month=3, day=15
            )
            baptism_ref = EventRef()
            baptism_ref.set_reference_handle(baptism_handle)

            # Dated Death event.
            death_handle = _add_event(
                self.db, trans, EventType.DEATH, year=1900, month=3, day=15
            )
            death_ref = EventRef()
            death_ref.set_reference_handle(death_handle)

            person = Person()
            person.set_birth_ref(birth_ref)
            person.add_event_ref(baptism_ref)
            person.set_death_ref(death_ref)
            handle = self.db.add_person(person, trans)

        age = self._age(handle)
        self.assertIsNotNone(age, "Expected age from dated baptism fallback, got None")
        # 1850-03-15 .. 1900-03-15 == 50 years.
        self.assertEqual(age[0], 50)

    def test_dated_primary_birth_unaffected(self):
        """A person whose primary Birth event has a date is unaffected."""
        with DbTxn("test", self.db) as trans:
            birth_handle = _add_event(
                self.db, trans, EventType.BIRTH, year=1850, month=3, day=15
            )
            birth_ref = EventRef()
            birth_ref.set_reference_handle(birth_handle)

            # A baptism with a *different* date that must NOT be used.
            baptism_handle = _add_event(
                self.db, trans, EventType.BAPTISM, year=1849, month=1, day=1
            )
            baptism_ref = EventRef()
            baptism_ref.set_reference_handle(baptism_handle)

            death_handle = _add_event(
                self.db, trans, EventType.DEATH, year=1900, month=3, day=15
            )
            death_ref = EventRef()
            death_ref.set_reference_handle(death_handle)

            person = Person()
            person.set_birth_ref(birth_ref)
            person.add_event_ref(baptism_ref)
            person.set_death_ref(death_ref)
            handle = self.db.add_person(person, trans)

        age = self._age(handle)
        self.assertIsNotNone(age)
        self.assertEqual(age[0], 50)


if __name__ == "__main__":
    unittest.main()

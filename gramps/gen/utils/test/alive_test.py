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
Tests for the ProbablyAlive (probably_alive_range) utility.
"""

import unittest

from ...db import DbTxn
from ...db.utils import make_database
from ...lib import ChildRef, Date, Event, EventRef, EventType, Family, Person
from ...lib.date import Today
from ...proxy import PrivateProxyDb
from ..alive import probably_alive, probably_alive_range


def _make_db():
    """Create and return a fresh in-memory SQLite database."""
    db = make_database("sqlite")
    db.load(":memory:")
    return db


def _add_event(db, trans, event_type, year=0, month=0, day=0):
    """Create an event with the given type and date, add it to db, return handle."""
    event = Event()
    event.set_type(EventType(event_type))
    date = Date()
    date.set_yr_mon_day(year, month, day)
    event.set_date_object(date)
    return db.add_event(event, trans)


def _add_person_with_events(
    db,
    trans,
    birth_year=0,
    birth_month=0,
    birth_day=0,
    baptism_year=0,
    baptism_month=0,
    baptism_day=0,
    include_birth=True,
    include_baptism=False,
):
    """
    Create a person, optionally adding birth and baptism events.
    Returns the committed person handle.
    """
    person = Person()
    person.set_gender(Person.MALE)

    if include_birth:
        birth_handle = _add_event(
            db,
            trans,
            EventType.BIRTH,
            year=birth_year,
            month=birth_month,
            day=birth_day,
        )
        birth_ref = EventRef()
        birth_ref.set_reference_handle(birth_handle)
        person.set_birth_ref(birth_ref)

    if include_baptism:
        baptism_handle = _add_event(
            db,
            trans,
            EventType.BAPTISM,
            year=baptism_year,
            month=baptism_month,
            day=baptism_day,
        )
        baptism_ref = EventRef()
        baptism_ref.set_reference_handle(baptism_handle)
        person.add_event_ref(baptism_ref)

    person_handle = db.add_person(person, trans)
    return person_handle


class TestProbablyAliveRange(unittest.TestCase):
    """Tests for probably_alive_range birth-date fallback behaviour."""

    def setUp(self):
        self.db = _make_db()

    def tearDown(self):
        self.db.close()

    def _get_birth_year(self, person_handle):
        """Run probably_alive_range and return the birth year (0 if not valid)."""
        person = self.db.get_person_from_handle(person_handle)
        birth, _death, _explain, _who = probably_alive_range(person, self.db)
        if birth is None:
            return None
        return birth.get_year() if birth.get_year_valid() else None

    # ------------------------------------------------------------------
    # Normal / regression cases
    # ------------------------------------------------------------------

    def test_birth_with_valid_year(self):
        """Birth event with a full date is used directly."""
        with DbTxn("test", self.db) as trans:
            handle = _add_person_with_events(
                self.db,
                trans,
                include_birth=True,
                birth_year=1850,
                birth_month=3,
                birth_day=15,
            )
        year = self._get_birth_year(handle)
        self.assertEqual(year, 1850)

    def test_no_birth_event_falls_back_to_baptism(self):
        """Person with no birth event falls back to baptism date."""
        with DbTxn("test", self.db) as trans:
            handle = _add_person_with_events(
                self.db,
                trans,
                include_birth=False,
                include_baptism=True,
                baptism_year=1852,
            )
        year = self._get_birth_year(handle)
        self.assertIsNotNone(year)
        self.assertEqual(year, 1852)

    # ------------------------------------------------------------------
    # The bug: birth event with month/day but no year blocked fallback
    # ------------------------------------------------------------------

    def test_birth_event_with_no_year_falls_back_to_baptism(self):
        """
        Birth event with only month/day (year=0) must be ignored so that
        a Baptism event with a valid year is used as the birth-date fallback.

        Before the fix, is_valid() returned True for a month/day-only date
        (because _calc_sort_value treats year=0 as year=1, giving sortval!=0).
        This caused birth_date to be set to the useless partial date and the
        fallback loop was never entered.
        """
        with DbTxn("test", self.db) as trans:
            handle = _add_person_with_events(
                self.db,
                trans,
                include_birth=True,
                birth_year=0,
                birth_month=2,
                birth_day=3,  # "February 3" - no year
                include_baptism=True,
                baptism_year=1855,  # valid fallback
            )
        year = self._get_birth_year(handle)
        self.assertIsNotNone(year, "Expected fallback to baptism year, got None")
        self.assertEqual(year, 1855, "Expected baptism year 1855, got %r" % year)

    def test_birth_event_with_empty_date_falls_back_to_baptism(self):
        """Birth event with a completely empty date falls back to baptism."""
        with DbTxn("test", self.db) as trans:
            handle = _add_person_with_events(
                self.db,
                trans,
                include_birth=True,
                birth_year=0,
                birth_month=0,
                birth_day=0,  # fully empty date
                include_baptism=True,
                baptism_year=1860,
            )
        year = self._get_birth_year(handle)
        self.assertIsNotNone(year, "Expected fallback to baptism year, got None")
        self.assertEqual(year, 1860)

    def test_birth_event_with_year_takes_precedence_over_baptism(self):
        """When birth event has a valid year, it wins over the baptism date."""
        with DbTxn("test", self.db) as trans:
            handle = _add_person_with_events(
                self.db,
                trans,
                include_birth=True,
                birth_year=1848,
                include_baptism=True,
                baptism_year=1849,
            )
        year = self._get_birth_year(handle)
        self.assertEqual(year, 1848)


def _add_death(db, trans, person, event_type=EventType.DEATH, date=None, private=False):
    """Add a death or death fallback event to person; commit the person."""
    event = Event()
    event.set_type(EventType(event_type))
    if date is not None:
        event.set_date_object(date)
    event.set_privacy(private)
    event_ref = EventRef()
    event_ref.set_reference_handle(db.add_event(event, trans))
    if event_type == EventType.DEATH:
        person.set_death_ref(event_ref)
    else:
        person.add_event_ref(event_ref)
    db.commit_person(person, trans)


class TestProbablyAliveKnownDead(unittest.TestCase):
    """
    A person with a recorded death is not alive today or later, whether or
    not the death has a date.
    """

    def setUp(self):
        self.db = _make_db()

    def tearDown(self):
        self.db.close()

    def _person(self, trans, **kwargs):
        """Add a person and return the Person object."""
        handle = _add_person_with_events(self.db, trans, **kwargs)
        return self.db.get_person_from_handle(handle)

    def _alive(self, person, db=None, **kwargs):
        """Reload the person and run probably_alive."""
        person = self.db.get_person_from_handle(person.handle)
        return probably_alive(person, db or self.db, **kwargs)

    def test_undated_death_without_other_evidence(self):
        """An undated death with no other dates means not alive today."""
        with DbTxn("test", self.db) as trans:
            person = self._person(trans, include_birth=False)
            _add_death(self.db, trans, person)
        self.assertFalse(self._alive(person))
        self.assertFalse(self._alive(person, current_date=Today()))

    def test_undated_death_with_estimate_from_child(self):
        """
        An undated death is not overridden by a birth estimate from a child
        whose dates would keep the person alive today.
        """
        with DbTxn("test", self.db) as trans:
            person = self._person(trans, include_birth=False)
            _add_death(self.db, trans, person)
            child = self._person(trans, birth_year=Today().get_year() - 30)
            family = Family()
            family.set_father_handle(person.handle)
            child_ref = ChildRef()
            child_ref.set_reference_handle(child.handle)
            family.add_child_ref(child_ref)
            self.db.add_family(family, trans)
            person.add_family_handle(family.handle)
            self.db.commit_person(person, trans)
            child.add_parent_family_handle(family.handle)
            self.db.commit_person(child, trans)
        self.assertFalse(self._alive(person))

    def test_undated_death_with_recent_birth(self):
        """An undated death with a birth date this century is not alive."""
        with DbTxn("test", self.db) as trans:
            person = self._person(trans, birth_year=Today().get_year() - 40)
            _add_death(self.db, trans, person)
        self.assertFalse(self._alive(person))

    def test_undated_death_with_estimated_birth(self):
        """An undated death with an estimated birth date is not alive."""
        with DbTxn("test", self.db) as trans:
            person = self._person(trans, birth_year=Today().get_year() - 90)
            birth = self.db.get_event_from_handle(person.get_birth_ref().ref)
            birth.get_date_object().set_quality(Date.QUAL_ESTIMATED)
            self.db.commit_event(birth, trans)
            _add_death(self.db, trans, person)
        self.assertFalse(self._alive(person))

    def test_about_death_in_recent_years(self):
        """A death dated "about" a recent year is not alive today."""
        date = Date()
        date.set(modifier=Date.MOD_ABOUT, value=(0, 0, Today().get_year() - 5, False))
        with DbTxn("test", self.db) as trans:
            person = self._person(trans, include_birth=False)
            _add_death(self.db, trans, person, date=date)
        self.assertFalse(self._alive(person))

    def test_undated_burial_only(self):
        """An undated death fallback event, such as burial, also counts."""
        with DbTxn("test", self.db) as trans:
            person = self._person(trans, include_birth=False)
            _add_death(self.db, trans, person, event_type=EventType.BURIAL)
        self.assertFalse(self._alive(person))

    def test_undated_death_future_date(self):
        """A person with a recorded death stays not alive in the future."""
        future = Date()
        future.set_yr_mon_day(Today().get_year() + 10, 1, 1)
        with DbTxn("test", self.db) as trans:
            person = self._person(trans, include_birth=False)
            _add_death(self.db, trans, person)
        self.assertFalse(self._alive(person, current_date=future))

    def test_undated_death_past_date_unchanged(self):
        """
        For a date in the past an undated death cannot decide, so the
        estimate is used as before.
        """
        past = Date()
        past.set_yr_mon_day(Today().get_year() - 10, 1, 1)
        with DbTxn("test", self.db) as trans:
            person = self._person(trans, birth_year=Today().get_year() - 40)
            _add_death(self.db, trans, person)
        self.assertTrue(self._alive(person, current_date=past))

    def test_undated_death_with_limit_unchanged(self):
        """With years after death to check, an undated death cannot decide."""
        with DbTxn("test", self.db) as trans:
            person = self._person(trans, include_birth=False)
            _add_death(self.db, trans, person)
        self.assertTrue(self._alive(person, limit=20))

    def test_private_death_hidden_by_proxy(self):
        """A death hidden by the private proxy does not count."""
        with DbTxn("test", self.db) as trans:
            person = self._person(trans, include_birth=False)
            _add_death(self.db, trans, person, private=True)
        self.assertTrue(self._alive(person, db=PrivateProxyDb(self.db)))
        self.assertFalse(self._alive(person))

    def test_no_death_recent_birth_still_alive(self):
        """Without a recorded death a recently born person stays alive."""
        with DbTxn("test", self.db) as trans:
            person = self._person(trans, birth_year=Today().get_year() - 40)
        self.assertTrue(self._alive(person))

    def test_return_range_reports_not_alive(self):
        """The return_range form gives the same answer."""
        with DbTxn("test", self.db) as trans:
            person = self._person(trans, include_birth=False)
            _add_death(self.db, trans, person)
        result = self._alive(person, return_range=True)
        self.assertFalse(result[0])
        self.assertEqual(len(result), 5)


if __name__ == "__main__":
    unittest.main()

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
from ...proxy import LivingProxyDb, PrivateProxyDb
from ..alive import get_alive_db, probably_alive, probably_alive_range


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


class TestProbablyAlivePrivacy(unittest.TestCase):
    """Tests that private records stay hidden from probably alive estimates."""

    def setUp(self):
        self.db = _make_db()
        with DbTxn("test", self.db) as trans:
            self.child_handle = _add_person_with_events(self.db, trans, birth_year=1700)
            child = self.db.get_person_from_handle(self.child_handle)
            event = self.db.get_event_from_handle(child.get_birth_ref().ref)
            event.set_privacy(True)
            self.db.commit_event(event, trans)

            parent = Person()
            parent.set_gender(Person.MALE)
            self.parent_handle = self.db.add_person(parent, trans)

            family = Family()
            family.set_father_handle(self.parent_handle)
            child_ref = ChildRef()
            child_ref.ref = self.child_handle
            family.add_child_ref(child_ref)
            family_handle = self.db.add_family(family, trans)

            parent = self.db.get_person_from_handle(self.parent_handle)
            parent.add_family_handle(family_handle)
            self.db.commit_person(parent, trans)
            child = self.db.get_person_from_handle(self.child_handle)
            child.add_parent_family_handle(family_handle)
            self.db.commit_person(child, trans)

    def tearDown(self):
        self.db.close()

    def test_base_db_uses_private_records(self):
        """Without a PrivateProxyDb, the child's private birth is used."""
        parent = self.db.get_person_from_handle(self.parent_handle)
        self.assertFalse(probably_alive(parent, self.db))

    def test_private_proxy_hides_private_records(self):
        """With a PrivateProxyDb, the child's private birth is not used."""
        private_db = PrivateProxyDb(self.db)
        parent = private_db.get_person_from_handle(self.parent_handle)
        birth, death, _explain, _who = probably_alive_range(parent, private_db)
        self.assertIsNone(birth)
        self.assertIsNone(death)
        self.assertTrue(probably_alive(parent, private_db))

    def test_private_proxy_below_living_proxy(self):
        """A PrivateProxyDb below a LivingProxyDb still hides private records."""
        living_db = LivingProxyDb(
            PrivateProxyDb(self.db), LivingProxyDb.MODE_EXCLUDE_ALL
        )
        self.assertIsNone(living_db.get_person_from_handle(self.parent_handle))

    def test_unsanitized_person_is_sanitized(self):
        """A person passed with private parts is sanitized first."""
        child = self.db.get_person_from_handle(self.child_handle)
        private_db = PrivateProxyDb(self.db)
        birth, _death, _explain, _who = probably_alive_range(child, private_db)
        self.assertIsNone(birth)

    def test_private_person_is_ignored(self):
        """A private person passed under a PrivateProxyDb gives no estimate."""
        with DbTxn("test", self.db) as trans:
            child = self.db.get_person_from_handle(self.child_handle)
            child.set_privacy(True)
            self.db.commit_person(child, trans)
        child = self.db.get_person_from_handle(self.child_handle)
        self.assertEqual(
            probably_alive_range(child, PrivateProxyDb(self.db)),
            (None, None, "", None),
        )

    def test_get_alive_db(self):
        """Proxies are removed, but a PrivateProxyDb is put back on top."""
        self.assertIs(get_alive_db(self.db), self.db)
        self.assertIs(
            get_alive_db(LivingProxyDb(self.db, LivingProxyDb.MODE_EXCLUDE_ALL)),
            self.db,
        )
        alive_db = get_alive_db(
            LivingProxyDb(PrivateProxyDb(self.db), LivingProxyDb.MODE_EXCLUDE_ALL)
        )
        self.assertIsInstance(alive_db, PrivateProxyDb)
        self.assertIs(alive_db.db, self.db)


if __name__ == "__main__":
    unittest.main()

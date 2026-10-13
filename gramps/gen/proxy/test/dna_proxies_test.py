#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Ian Davis
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

"""Tests of DNATest and DNAMatch objects seen through the proxy databases."""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
import os
import shutil
import tempfile
import unittest

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ...db import DbTxn
from ...db.utils import make_database
from ...filters import GenericFilter, GenericFilterFactory
from ...filters.rules.note import HasIdOf as NoteHasIdOf
from ...filters.rules.person import HasIdOf as PersonHasIdOf
from ...lib import (
    Citation,
    Date,
    DNAAttribute,
    DNAAttributeType,
    DNAMatch,
    DNATest,
    Event,
    EventRef,
    EventType,
    Note,
    Person,
    PredictedRelationship,
    SharedAncestor,
    Source,
)
from ...user import User
from .. import (
    FilterProxyDb,
    LivingProxyDb,
    PrivateProxyDb,
    ReferencedBySelectionProxyDb,
)


# -------------------------------------------------------------------------
#
# DNAProxyTestCase
#
# -------------------------------------------------------------------------
class DNAProxyTestCase(unittest.TestCase):
    """
    Base class holding a small tree of people, kits and matches.

    The kits are named after their owner: ``dead``, ``living`` and
    ``privperson`` belong to the person of that description, ``private`` is
    itself private, and ``unlinked``, ``orphan_a`` and ``orphan_b`` have no
    person. Each match is named ``<subject kit>_<match kit>``, and
    ``hidden`` is a private match from ``dead`` to ``unlinked``.
    """

    @classmethod
    def setUpClass(cls):
        cls.tmpdir = tempfile.mkdtemp()
        dbdir = os.path.join(cls.tmpdir, "db")
        os.mkdir(dbdir)
        cls.base = make_database("sqlite")
        cls.base.load(dbdir)
        cls.people = {}
        cls.notes = {}
        cls.tests = {}
        cls.matches = {}
        with DbTxn("add DNA", cls.base) as trans:
            cls._populate(trans)

    @classmethod
    def tearDownClass(cls):
        cls.base.close()
        shutil.rmtree(cls.tmpdir)

    @classmethod
    def _add_event(cls, person, event_type, year, trans):
        """Add an event of the given type and year and return a reference."""
        event = Event()
        event.set_type(event_type)
        date = Date()
        date.set_yr_mon_day(year, 1, 1)
        event.set_date_object(date)
        event_ref = EventRef()
        event_ref.set_reference_handle(cls.base.add_event(event, trans))
        person.add_event_ref(event_ref)
        return event_ref

    @classmethod
    def _add_person(cls, key, born, died, trans, private=False):
        """Add a person born and, unless died is None, dead in the given years."""
        person = Person()
        person.set_privacy(private)
        person.set_birth_ref(cls._add_event(person, EventType.BIRTH, born, trans))
        if died is not None:
            person.set_death_ref(cls._add_event(person, EventType.DEATH, died, trans))
        cls.people[key] = cls.base.add_person(person, trans)

    @classmethod
    def _add_note(cls, key, trans, private=False):
        """Add a note."""
        note = Note()
        note.set(key)
        note.set_privacy(private)
        cls.notes[key] = cls.base.add_note(note, trans)

    @classmethod
    def _add_test(cls, key, trans, person=None, private=False):
        """Add a kit and return the object that was stored."""
        dnatest = DNATest()
        dnatest.set_account_name(key)
        dnatest.set_privacy(private)
        if person:
            dnatest.set_person_handle(cls.people[person])
        cls.tests[key] = cls.base.add_dnatest(dnatest, trans)
        return dnatest

    @classmethod
    def _add_match(cls, subject, other, trans, key=None, private=False):
        """Add a match between two kits and return the object that was stored."""
        dnamatch = DNAMatch()
        dnamatch.set_subject_test_handle(cls.tests[subject])
        dnamatch.set_match_test_handle(cls.tests[other])
        dnamatch.set_privacy(private)
        key = key or "%s_%s" % (subject, other)
        cls.matches[key] = cls.base.add_dnamatch(dnamatch, trans)
        return dnamatch

    @classmethod
    def _populate(cls, trans):
        """Add the people, notes, kits and matches under test."""
        db = cls.base
        cls._add_person("dead", 1800, 1870, trans)
        cls._add_person("living", 1990, None, trans)
        cls._add_person("private", 1810, 1880, trans, private=True)
        cls._add_note("public", trans)
        cls._add_note("secret", trans, private=True)
        both_notes = [cls.notes["public"], cls.notes["secret"]]
        source = db.add_source(Source(), trans)
        citation = Citation()
        citation.set_reference_handle(source)
        cls.citation = db.add_citation(citation, trans)

        dnatest = cls._add_test("dead", trans, person="dead")
        dnatest.set_note_list(list(both_notes))
        dnatest.add_citation(cls.citation)
        for marker, private in (("DYS393", False), ("DYS390", True)):
            attribute = DNAAttribute()
            attribute.set_type((DNAAttributeType.CUSTOM, marker))
            attribute.set_value("13")
            attribute.set_privacy(private)
            attribute.set_note_list(list(both_notes))
            dnatest.add_attribute(attribute)
        db.commit_dnatest(dnatest, trans)

        cls._add_test("living", trans, person="living")
        cls._add_test("privperson", trans, person="private")
        cls._add_test("private", trans, private=True)
        for key in ("unlinked", "orphan_a", "orphan_b"):
            cls._add_test(key, trans)

        dnamatch = cls._add_match("dead", "unlinked", trans)
        dnamatch.set_note_list(list(both_notes))
        for key in ("dead", "private", "living"):
            ancestor = SharedAncestor()
            ancestor.set_person_handle(cls.people[key])
            ancestor.set_description(key)
            ancestor.set_note_list(list(both_notes))
            dnamatch.add_shared_ancestor(ancestor)
        relationship = PredictedRelationship()
        relationship.set_note_list(list(both_notes))
        dnamatch.add_predicted_relationship(relationship)
        db.commit_dnamatch(dnamatch, trans)

        cls._add_match("dead", "living", trans)
        cls._add_match("dead", "private", trans)
        cls._add_match("dead", "unlinked", trans, key="hidden", private=True)
        cls._add_match("living", "dead", trans)
        cls._add_match("orphan_a", "orphan_b", trans)

    def assert_tests(self, db, *keys):
        """Assert that db holds exactly the kits named by keys."""
        expected = {self.tests[key] for key in keys}
        self.assertEqual(set(db.get_dnatest_handles()), expected)
        self.assertEqual(set(db.iter_dnatest_handles()), expected)
        self.assertEqual({obj.handle for obj in db.iter_dnatests()}, expected)
        self.assertEqual({hdl for hdl, _ in db.get_dnatest_cursor()}, expected)
        self.assertEqual(db.get_number_of_dnatests(), len(expected))
        for key, handle in self.tests.items():
            self.assertEqual(db.has_dnatest_handle(handle), key in keys, key)

    def assert_matches(self, db, *keys):
        """Assert that db holds exactly the matches named by keys."""
        expected = {self.matches[key] for key in keys}
        self.assertEqual(set(db.get_dnamatch_handles()), expected)
        self.assertEqual(set(db.iter_dnamatch_handles()), expected)
        self.assertEqual({obj.handle for obj in db.iter_dnamatches()}, expected)
        self.assertEqual({hdl for hdl, _ in db.get_dnamatch_cursor()}, expected)
        self.assertEqual(db.get_number_of_dnamatches(), len(expected))
        for key, handle in self.matches.items():
            self.assertEqual(db.has_dnamatch_handle(handle), key in keys, key)

    def backlinks(self, db, handle, class_name):
        """Return the handles of one class that refer to handle in db."""
        return {
            hdl
            for cls_name, hdl in db.find_backlink_handles(handle)
            if cls_name == class_name
        }

    def ancestors(self, db):
        """Return the shared ancestor person handles of the dead_unlinked match."""
        dnamatch = db.get_dnamatch_from_handle(self.matches["dead_unlinked"])
        return [sa.get_person_handle() for sa in dnamatch.get_shared_ancestor_list()]


# -------------------------------------------------------------------------
#
# PrivateProxyDNATest
#
# -------------------------------------------------------------------------
class PrivateProxyDNATest(DNAProxyTestCase):
    """DNA records seen through PrivateProxyDb."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.db = PrivateProxyDb(cls.base)

    def test_private_test_is_hidden(self):
        self.assert_tests(
            self.db, "dead", "living", "privperson", "unlinked", "orphan_a", "orphan_b"
        )
        handle = self.tests["private"]
        self.assertIsNone(self.db.get_dnatest_from_handle(handle))
        self.assertIsNone(self.db.get_raw_dnatest_data(handle))

    def test_private_match_and_match_with_private_test_are_hidden(self):
        self.assert_matches(
            self.db, "dead_unlinked", "dead_living", "living_dead", "orphan_a_orphan_b"
        )
        self.assertIsNone(self.db.get_dnamatch_from_handle(self.matches["hidden"]))
        self.assertIsNone(
            self.db.get_dnamatch_from_handle(self.matches["dead_private"])
        )

    def test_lookup_by_gramps_id(self):
        base = self.base
        public = base.get_dnatest_from_handle(self.tests["dead"])
        private = base.get_dnatest_from_handle(self.tests["private"])
        found = self.db.get_dnatest_from_gramps_id(public.gramps_id)
        self.assertEqual(found.handle, public.handle)
        self.assertIsNone(self.db.get_dnatest_from_gramps_id(private.gramps_id))
        self.assertIsNone(self.db.get_dnatest_from_gramps_id("no such id"))
        public = base.get_dnamatch_from_handle(self.matches["dead_unlinked"])
        private = base.get_dnamatch_from_handle(self.matches["hidden"])
        found = self.db.get_dnamatch_from_gramps_id(public.gramps_id)
        self.assertEqual(found.handle, public.handle)
        self.assertIsNone(self.db.get_dnamatch_from_gramps_id(private.gramps_id))

    def test_test_of_private_person_loses_person(self):
        dnatest = self.db.get_dnatest_from_handle(self.tests["privperson"])
        self.assertIsNone(dnatest.get_person_handle())
        self.assertEqual(dnatest.get_account_name(), "privperson")
        dnatest = self.db.get_dnatest_from_handle(self.tests["dead"])
        self.assertEqual(dnatest.get_person_handle(), self.people["dead"])

    def test_test_is_sanitized(self):
        dnatest = self.db.get_dnatest_from_handle(self.tests["dead"])
        self.assertEqual(dnatest.get_note_list(), [self.notes["public"]])
        self.assertEqual(dnatest.get_citation_list(), [self.citation])
        attributes = dnatest.get_attribute_list()
        self.assertEqual([str(attr.get_type()) for attr in attributes], ["DYS393"])
        self.assertEqual(attributes[0].get_note_list(), [self.notes["public"]])

    def test_match_is_sanitized(self):
        dnamatch = self.db.get_dnamatch_from_handle(self.matches["dead_unlinked"])
        self.assertEqual(dnamatch.get_subject_test_handle(), self.tests["dead"])
        self.assertEqual(dnamatch.get_match_test_handle(), self.tests["unlinked"])
        self.assertEqual(dnamatch.get_note_list(), [self.notes["public"]])
        self.assertEqual(
            self.ancestors(self.db), [self.people["dead"], None, self.people["living"]]
        )
        for child in (
            dnamatch.get_shared_ancestor_list()
            + dnamatch.get_predicted_relationship_list()
        ):
            self.assertEqual(child.get_note_list(), [self.notes["public"]])

    def test_backlinks(self):
        self.assertEqual(
            self.backlinks(self.db, self.people["dead"], "DNATest"),
            {self.tests["dead"]},
        )
        self.assertEqual(
            self.backlinks(self.db, self.tests["dead"], "DNAMatch"),
            {
                self.matches["dead_unlinked"],
                self.matches["dead_living"],
                self.matches["living_dead"],
            },
        )

    def test_bookmarks_and_attribute_types(self):
        self.assertIs(self.db.get_dnatest_bookmarks(), self.base.dnatest_bookmarks)
        self.assertIs(self.db.get_dnamatch_bookmarks(), self.base.dnamatch_bookmarks)
        self.assertEqual(
            self.db.get_dnatest_attribute_types(),
            self.base.get_dnatest_attribute_types(),
        )
        self.assertEqual(
            self.db.get_dnamatch_attribute_types(),
            self.base.get_dnamatch_attribute_types(),
        )


# -------------------------------------------------------------------------
#
# LivingProxyDNATest
#
# -------------------------------------------------------------------------
class LivingProxyDNATest(DNAProxyTestCase):
    """DNA records seen through LivingProxyDb."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.db = LivingProxyDb(
            cls.base, LivingProxyDb.MODE_EXCLUDE_ALL, current_year=2006
        )
        cls.named = LivingProxyDb(
            cls.base, LivingProxyDb.MODE_INCLUDE_FULL_NAME_ONLY, current_year=2006
        )

    def test_test_of_living_person_is_hidden(self):
        kept = ("dead", "privperson", "private", "unlinked", "orphan_a", "orphan_b")
        self.assert_tests(self.db, *kept)
        self.assert_tests(self.named, *kept)

    def test_match_with_test_of_living_person_is_hidden(self):
        kept = ("dead_unlinked", "dead_private", "hidden", "orphan_a_orphan_b")
        self.assert_matches(self.db, *kept)
        self.assert_matches(self.named, *kept)

    def test_living_shared_ancestor(self):
        dead, private, living = (
            self.people[key] for key in ("dead", "private", "living")
        )
        # Living people are absent when excluded, and present when restricted.
        self.assertEqual(self.ancestors(self.db), [dead, private, None])
        self.assertEqual(self.ancestors(self.named), [dead, private, living])

    def test_backlinks(self):
        self.assertEqual(
            self.backlinks(self.db, self.people["living"], "DNATest"), set()
        )
        self.assertEqual(
            self.backlinks(self.db, self.tests["dead"], "DNAMatch"),
            {
                self.matches["dead_unlinked"],
                self.matches["dead_private"],
                self.matches["hidden"],
            },
        )

    def test_include_all_mode_keeps_everything(self):
        db = LivingProxyDb(self.base, LivingProxyDb.MODE_INCLUDE_ALL, current_year=2006)
        self.assert_tests(db, *self.tests)
        self.assert_matches(db, *self.matches)


# -------------------------------------------------------------------------
#
# FilterProxyDNATest
#
# -------------------------------------------------------------------------
class FilterProxyDNATest(DNAProxyTestCase):
    """DNA records seen through FilterProxyDb."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        person = cls.base.get_person_from_handle(cls.people["dead"])
        person_filter = GenericFilter()
        person_filter.add_rule(PersonHasIdOf([person.gramps_id]))
        cls.db = FilterProxyDb(cls.base, person_filter, user=User())
        note = cls.base.get_note_from_handle(cls.notes["public"])
        note_filter = GenericFilterFactory("Note")()
        note_filter.add_rule(NoteHasIdOf([note.gramps_id]))
        cls.noted = FilterProxyDb(cls.base, note_filter=note_filter, user=User())

    def test_person_filter_keeps_tests_of_kept_matches(self):
        self.assert_tests(self.db, "dead", "unlinked", "living", "private")

    def test_person_filter_keeps_matches_of_kept_subject(self):
        self.assert_matches(
            self.db, "dead_unlinked", "dead_living", "dead_private", "hidden"
        )

    def test_person_filter_clears_filtered_people(self):
        dnatest = self.db.get_dnatest_from_handle(self.tests["dead"])
        self.assertEqual(dnatest.get_person_handle(), self.people["dead"])
        dnatest = self.db.get_dnatest_from_handle(self.tests["living"])
        self.assertIsNone(dnatest.get_person_handle())
        self.assertEqual(self.ancestors(self.db), [self.people["dead"], None, None])

    def test_note_filter_keeps_every_record(self):
        self.assert_tests(self.noted, *self.tests)
        self.assert_matches(self.noted, *self.matches)
        dnatest = self.noted.get_dnatest_from_handle(self.tests["living"])
        self.assertEqual(dnatest.get_person_handle(), self.people["living"])

    def test_note_filter_removes_notes(self):
        public = [self.notes["public"]]
        dnatest = self.noted.get_dnatest_from_handle(self.tests["dead"])
        self.assertEqual(dnatest.get_note_list(), public)
        for attribute in dnatest.get_attribute_list():
            self.assertEqual(attribute.get_note_list(), public)
        dnamatch = self.noted.get_dnamatch_from_handle(self.matches["dead_unlinked"])
        self.assertEqual(dnamatch.get_note_list(), public)
        for child in (
            dnamatch.get_shared_ancestor_list()
            + dnamatch.get_predicted_relationship_list()
        ):
            self.assertEqual(child.get_note_list(), public)


# -------------------------------------------------------------------------
#
# ReferencedBySelectionProxyDNATest
#
# -------------------------------------------------------------------------
class ReferencedBySelectionProxyDNATest(DNAProxyTestCase):
    """DNA records seen through ReferencedBySelectionProxyDb."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.db = ReferencedBySelectionProxyDb(cls.base, all_people=True)

    def test_tests_reached_from_people_are_kept(self):
        self.assert_tests(
            self.db, "dead", "living", "privperson", "private", "unlinked"
        )

    def test_matches_reached_from_people_are_kept(self):
        self.assert_matches(
            self.db,
            "dead_unlinked",
            "dead_living",
            "dead_private",
            "hidden",
            "living_dead",
        )

    def test_references_of_dna_records_are_kept(self):
        self.assertTrue(self.db.has_note_handle(self.notes["public"]))
        self.assertTrue(self.db.has_citation_handle(self.citation))

    def test_backlinks(self):
        self.assertEqual(
            self.backlinks(self.db, self.people["dead"], "DNATest"),
            {self.tests["dead"]},
        )
        self.assertEqual(
            self.backlinks(self.db, self.tests["orphan_a"], "DNAMatch"), set()
        )


if __name__ == "__main__":
    unittest.main()

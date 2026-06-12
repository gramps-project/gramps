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

"""Tests for CSV importer _parse_event and _parse_citation methods."""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
import unittest

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.db import DbTxn
from gramps.gen.db.utils import make_database
from gramps.gen.lib import (
    Citation,
    Event,
    EventRoleType,
    EventType,
    Family,
    NoteType,
    Person,
    Place,
    Source,
)
from gramps.plugins.importer.importcsv import CSVParser

# -------------------------------------------------------------------------
#
# Helpers
#
# -------------------------------------------------------------------------


class _MockUser:
    """Minimal user stub — CSVParser stores it but parse methods don't call it."""

    def notify_error(self, *args):
        """Silently ignore errors."""


def _col(*col_names):
    """Build a column-name→index dict from an ordered list of names."""
    return {name: i for i, name in enumerate(col_names)}


# -------------------------------------------------------------------------
#
# TestParseEvent
#
# -------------------------------------------------------------------------
class TestParseEvent(unittest.TestCase):
    """Tests for CSVParser._parse_event."""

    @classmethod
    def setUpClass(cls):
        """Create a single in-memory DB shared by all event tests."""
        cls.db = make_database("sqlite")
        cls.db.load(":memory:")

    def setUp(self):
        """Fresh parser for every test; resets all sheet-local ref dicts."""
        self.parser = CSVParser(self.db, _MockUser())

    def _run(self, row, col):
        """Run _parse_event inside a transaction."""
        self.db.disable_signals()
        with DbTxn("test", self.db, batch=True) as self.parser.trans:
            self.parser._parse_event(1, row, col)
        self.db.enable_signals()

    # ------------------------------------------------------------------
    # Creation
    # ------------------------------------------------------------------

    def test_create_minimal(self):
        """New event with type and date is stored and retrievable."""
        self._run(["E_MIN", "Birth", "1900-01-01"], _col("event", "eventtype", "date"))

        event = self.parser.lookup("event", "E_MIN")
        self.assertIsNotNone(event)
        self.assertEqual(int(event.get_type()), EventType.BIRTH)
        self.assertEqual(event.get_date_object().get_year(), 1900)

    def test_create_with_place_name(self):
        """Place name creates the place and links it to the event."""
        self._run(["E_PLACE", "Death", "London"], _col("event", "eventtype", "place"))

        event = self.parser.lookup("event", "E_PLACE")
        place = self.db.get_place_from_handle(event.get_place_handle())
        self.assertIsNotNone(place)
        self.assertEqual(place.get_title(), "London")

    def test_create_with_description(self):
        """Description is stored on the event."""
        self._run(
            ["E_DESCR", "Census", "Household of five"],
            _col("event", "eventtype", "description"),
        )

        event = self.parser.lookup("event", "E_DESCR")
        self.assertEqual(event.get_description(), "Household of five")

    def test_create_with_source_adds_citation(self):
        """Source column creates a citation on the event."""
        self._run(
            ["E_SRC", "Census", "1901 Census"], _col("event", "eventtype", "source")
        )

        event = self.parser.lookup("event", "E_SRC")
        self.assertGreater(len(event.get_citation_list()), 0)
        citation = self.db.get_citation_from_handle(event.get_citation_list()[0])
        source = self.db.get_source_from_handle(citation.get_reference_handle())
        self.assertEqual(source.get_title(), "1901 Census")

    def test_create_with_tag(self):
        """Tag is created and attached to the event."""
        self._run(["E_TAG", "Census", "Verified"], _col("event", "eventtype", "tag"))

        event = self.parser.lookup("event", "E_TAG")
        self.assertGreater(len(event.get_tag_list()), 0)
        tag = self.db.get_tag_from_handle(event.get_tag_list()[0])
        self.assertEqual(tag.get_name(), "Verified")

    def test_create_with_media(self):
        """Media path creates a Media object and attaches it to the event."""
        self._run(
            ["E_MEDIA", "Census", "/scans/page1.jpg"],
            _col("event", "eventtype", "media"),
        )

        event = self.parser.lookup("event", "E_MEDIA")
        self.assertGreater(len(event.get_media_list()), 0)
        media = self.db.get_media_from_handle(event.get_media_list()[0].ref)
        self.assertEqual(media.get_path(), "/scans/page1.jpg")

    # ------------------------------------------------------------------
    # Type resolution
    # ------------------------------------------------------------------

    def test_custom_event_type(self):
        """Unknown event type string becomes EventType CUSTOM (0)."""
        self._run(["E_CTYPE", "DNA Match"], _col("event", "eventtype"))

        event = self.parser.lookup("event", "E_CTYPE")
        self.assertEqual(int(event.get_type()), 0)
        self.assertEqual(str(event.get_type()), "DNA Match")

    # ------------------------------------------------------------------
    # Notes
    # ------------------------------------------------------------------

    def test_note_default_type_is_event(self):
        """Note without note_type column defaults to NoteType.EVENT."""
        self._run(
            ["E_NOTE", "Census", "Check handwriting"],
            _col("event", "eventtype", "note"),
        )

        event = self.parser.lookup("event", "E_NOTE")
        note = self.db.get_note_from_handle(event.get_note_list()[0])
        self.assertEqual(int(note.get_type()), NoteType.EVENT)
        self.assertEqual(note.get(), "Check handwriting")

    def test_note_explicit_type(self):
        """Explicit note_type column is resolved and set."""
        self._run(
            ["E_NOTETYPE", "Census", "Verbatim copy", "Transcript"],
            _col("event", "eventtype", "note", "note_type"),
        )

        event = self.parser.lookup("event", "E_NOTETYPE")
        note = self.db.get_note_from_handle(event.get_note_list()[0])
        self.assertEqual(int(note.get_type()), NoteType.TRANSCRIPT)

    def test_note_custom_type(self):
        """Unknown note_type string becomes NoteType CUSTOM (0)."""
        self._run(
            ["E_CNOTE", "Census", "Some note", "MyCustomType"],
            _col("event", "eventtype", "note", "note_type"),
        )

        event = self.parser.lookup("event", "E_CNOTE")
        note = self.db.get_note_from_handle(event.get_note_list()[0])
        self.assertEqual(int(note.get_type()), 0)

    # ------------------------------------------------------------------
    # Person linking
    # ------------------------------------------------------------------

    def test_link_to_person(self):
        """Person gets an EventRef pointing to the new event."""
        with DbTxn("setup", self.db) as trans:
            person = Person()
            self.db.add_person(person, trans)
        person_gid = "[%s]" % person.get_gramps_id()

        self._run(
            ["E_PERS", "Census", person_gid], _col("event", "eventtype", "person")
        )

        event = self.parser.lookup("event", "E_PERS")
        person = self.db.get_person_from_handle(person.get_handle())
        self.assertIn(event.get_handle(), [r.ref for r in person.get_event_ref_list()])

    def test_link_to_person_default_role_is_primary(self):
        """Person EventRef defaults to EventRoleType.PRIMARY."""
        with DbTxn("setup", self.db) as trans:
            person = Person()
            self.db.add_person(person, trans)
        person_gid = "[%s]" % person.get_gramps_id()

        self._run(["E_PROL", "Birth", person_gid], _col("event", "eventtype", "person"))

        event = self.parser.lookup("event", "E_PROL")
        person = self.db.get_person_from_handle(person.get_handle())
        role = next(
            r.get_role()
            for r in person.get_event_ref_list()
            if r.ref == event.get_handle()
        )
        self.assertEqual(int(role), EventRoleType.PRIMARY)

    def test_link_to_person_explicit_role(self):
        """Explicit role string is resolved and set on the EventRef."""
        with DbTxn("setup", self.db) as trans:
            person = Person()
            self.db.add_person(person, trans)
        person_gid = "[%s]" % person.get_gramps_id()

        self._run(
            ["E_ROLE", "Census", person_gid, "Witness"],
            _col("event", "eventtype", "person", "role"),
        )

        event = self.parser.lookup("event", "E_ROLE")
        person = self.db.get_person_from_handle(person.get_handle())
        role = next(
            r.get_role()
            for r in person.get_event_ref_list()
            if r.ref == event.get_handle()
        )
        self.assertEqual(int(role), EventRoleType.WITNESS)

    def test_link_to_person_custom_role(self):
        """Unknown role string becomes EventRoleType CUSTOM (0)."""
        with DbTxn("setup", self.db) as trans:
            person = Person()
            self.db.add_person(person, trans)
        person_gid = "[%s]" % person.get_gramps_id()

        self._run(
            ["E_CROLE", "Census", person_gid, "Transcriber"],
            _col("event", "eventtype", "person", "role"),
        )

        event = self.parser.lookup("event", "E_CROLE")
        person = self.db.get_person_from_handle(person.get_handle())
        role = next(
            r.get_role()
            for r in person.get_event_ref_list()
            if r.ref == event.get_handle()
        )
        self.assertEqual(int(role), 0)
        self.assertEqual(str(role), "Transcriber")

    # ------------------------------------------------------------------
    # Family linking
    # ------------------------------------------------------------------

    def test_link_to_family(self):
        """Family gets an EventRef pointing to the new event."""
        with DbTxn("setup", self.db) as trans:
            family = Family()
            self.db.add_family(family, trans)
        family_gid = "[%s]" % family.get_gramps_id()

        self._run(
            ["E_FAM", "Marriage", family_gid], _col("event", "eventtype", "family")
        )

        event = self.parser.lookup("event", "E_FAM")
        family = self.db.get_family_from_handle(family.get_handle())
        self.assertIn(event.get_handle(), [r.ref for r in family.get_event_ref_list()])

    def test_link_to_family_default_role_is_family(self):
        """Family EventRef defaults to EventRoleType.FAMILY."""
        with DbTxn("setup", self.db) as trans:
            family = Family()
            self.db.add_family(family, trans)
        family_gid = "[%s]" % family.get_gramps_id()

        self._run(
            ["E_FROL", "Marriage", family_gid], _col("event", "eventtype", "family")
        )

        event = self.parser.lookup("event", "E_FROL")
        family = self.db.get_family_from_handle(family.get_handle())
        role = next(
            r.get_role()
            for r in family.get_event_ref_list()
            if r.ref == event.get_handle()
        )
        self.assertEqual(int(role), EventRoleType.FAMILY)

    # ------------------------------------------------------------------
    # Update existing
    # ------------------------------------------------------------------

    def test_update_existing_via_bracket_ref(self):
        """Bracket ref finds an existing DB event and updates it."""
        with DbTxn("setup", self.db) as trans:
            event = Event()
            event.set_type(EventType(EventType.BIRTH))
            self.db.add_event(event, trans)
        bracket_ref = "[%s]" % event.get_gramps_id()

        self._run(
            [bracket_ref, "Birth", "Updated description"],
            _col("event", "eventtype", "description"),
        )

        updated = self.db.get_event_from_handle(event.get_handle())
        self.assertEqual(updated.get_description(), "Updated description")

    # ------------------------------------------------------------------
    # Gramps ID preservation (regression)
    # ------------------------------------------------------------------

    def test_gramps_id_preserved_from_bracket_ref(self):
        """New event created via [E9991] gets that gramps_id, not the auto-ID."""
        expected_id = self.db.eid2user_format("E9991")
        self._run(["[E9991]", "Birth"], _col("event", "eventtype"))

        event = self.parser.lookup("event", "[E9991]")
        self.assertIsNotNone(event)
        self.assertEqual(event.get_gramps_id(), expected_id)
        self.assertIsNotNone(self.db.get_event_from_gramps_id(expected_id))

    # ------------------------------------------------------------------
    # Error / skip cases
    # ------------------------------------------------------------------

    def test_missing_eventtype_skips_new_event(self):
        """Row with no eventtype for an unknown ref creates no event."""
        count_before = len(list(self.db.get_event_handles()))
        self._run(["E_NOTYPE", "1900-01-01"], _col("event", "date"))
        self.assertEqual(len(list(self.db.get_event_handles())), count_before)

    def test_unknown_person_ref_logs_warning(self):
        """Unknown person ref is skipped without raising an exception."""
        self._run(
            ["E_BADP", "Census", "NONEXISTENT_PERSON"],
            _col("event", "eventtype", "person"),
        )
        event = self.parser.lookup("event", "E_BADP")
        self.assertIsNotNone(event)


# -------------------------------------------------------------------------
#
# TestParseCitation
#
# -------------------------------------------------------------------------
class TestParseCitation(unittest.TestCase):
    """Tests for CSVParser._parse_citation."""

    @classmethod
    def setUpClass(cls):
        """Create a single in-memory DB shared by all citation tests."""
        cls.db = make_database("sqlite")
        cls.db.load(":memory:")

    def setUp(self):
        """Fresh parser for every test."""
        self.parser = CSVParser(self.db, _MockUser())

    def _run(self, row, col):
        """Run _parse_citation inside a transaction."""
        self.db.disable_signals()
        with DbTxn("test", self.db, batch=True) as self.parser.trans:
            self.parser._parse_citation(1, row, col)
        self.db.enable_signals()

    # ------------------------------------------------------------------
    # Creation
    # ------------------------------------------------------------------

    def test_create_minimal(self):
        """New citation with source is created and retrievable."""
        self._run(["C_MIN", "1901 Census"], _col("citation", "source"))

        citation = self.parser.lookup("citation", "C_MIN")
        self.assertIsNotNone(citation)
        source = self.db.get_source_from_handle(citation.get_reference_handle())
        self.assertEqual(source.get_title(), "1901 Census")

    def test_create_with_page(self):
        """Page is stored on the citation."""
        self._run(["C_PAGE", "Census", "12b"], _col("citation", "source", "page"))

        citation = self.parser.lookup("citation", "C_PAGE")
        self.assertEqual(citation.get_page(), "12b")

    def test_create_with_date(self):
        """Date is parsed and stored on the citation."""
        self._run(
            ["C_DATE", "Register", "1885-06-20"], _col("citation", "source", "date")
        )

        citation = self.parser.lookup("citation", "C_DATE")
        self.assertEqual(citation.get_date_object().get_year(), 1885)

    def test_create_with_media(self):
        """Media path creates a Media object and attaches it to the citation."""
        self._run(
            ["C_MEDIA", "Source", "/scans/cert.jpg"],
            _col("citation", "source", "media"),
        )

        citation = self.parser.lookup("citation", "C_MEDIA")
        self.assertGreater(len(citation.get_media_list()), 0)
        media = self.db.get_media_from_handle(citation.get_media_list()[0].ref)
        self.assertEqual(media.get_path(), "/scans/cert.jpg")

    # ------------------------------------------------------------------
    # Confidence
    # ------------------------------------------------------------------

    def test_confidence_integer(self):
        """Integer string '3' maps to CONF_HIGH."""
        self._run(["C_CINT", "Source", "3"], _col("citation", "source", "confidence"))

        citation = self.parser.lookup("citation", "C_CINT")
        self.assertEqual(citation.get_confidence_level(), Citation.CONF_HIGH)

    def test_confidence_string_very_high(self):
        """String 'Very High' maps to CONF_VERY_HIGH."""
        self._run(
            ["C_CSTRH", "Source", "Very High"],
            _col("citation", "source", "confidence"),
        )

        citation = self.parser.lookup("citation", "C_CSTRH")
        self.assertEqual(citation.get_confidence_level(), Citation.CONF_VERY_HIGH)

    def test_confidence_string_very_low(self):
        """String 'Very Low' maps to CONF_VERY_LOW."""
        self._run(
            ["C_CSTRL", "Source", "Very Low"],
            _col("citation", "source", "confidence"),
        )

        citation = self.parser.lookup("citation", "C_CSTRL")
        self.assertEqual(citation.get_confidence_level(), Citation.CONF_VERY_LOW)

    def test_confidence_invalid_defaults_to_normal(self):
        """Unrecognised confidence string defaults to CONF_NORMAL."""
        self._run(
            ["C_CBAD", "Source", "bogus"], _col("citation", "source", "confidence")
        )

        citation = self.parser.lookup("citation", "C_CBAD")
        self.assertEqual(citation.get_confidence_level(), Citation.CONF_NORMAL)

    # ------------------------------------------------------------------
    # Notes
    # ------------------------------------------------------------------

    def test_note_default_type_is_citation(self):
        """Note without note_type defaults to NoteType.CITATION."""
        self._run(
            ["C_NOTE", "Source", "Original at TNA"],
            _col("citation", "source", "note"),
        )

        citation = self.parser.lookup("citation", "C_NOTE")
        note = self.db.get_note_from_handle(citation.get_note_list()[0])
        self.assertEqual(int(note.get_type()), NoteType.CITATION)
        self.assertEqual(note.get(), "Original at TNA")

    def test_note_explicit_type(self):
        """Explicit note_type column is resolved and set."""
        self._run(
            ["C_NOTETYPE", "Source", "Verbatim text", "Transcript"],
            _col("citation", "source", "note", "note_type"),
        )

        citation = self.parser.lookup("citation", "C_NOTETYPE")
        note = self.db.get_note_from_handle(citation.get_note_list()[0])
        self.assertEqual(int(note.get_type()), NoteType.TRANSCRIPT)

    def test_note_custom_type(self):
        """Unknown note_type string becomes NoteType CUSTOM (0)."""
        self._run(
            ["C_CNOTE", "Source", "Some note", "MyNoteType"],
            _col("citation", "source", "note", "note_type"),
        )

        citation = self.parser.lookup("citation", "C_CNOTE")
        note = self.db.get_note_from_handle(citation.get_note_list()[0])
        self.assertEqual(int(note.get_type()), 0)

    # ------------------------------------------------------------------
    # Attaching citation to objects
    # ------------------------------------------------------------------

    def test_attach_to_person(self):
        """Citation handle is added to the person's citation list."""
        with DbTxn("setup", self.db) as trans:
            person = Person()
            self.db.add_person(person, trans)
        person_gid = "[%s]" % person.get_gramps_id()

        self._run(
            ["C_PERS", "Source", person_gid], _col("citation", "source", "person")
        )

        citation = self.parser.lookup("citation", "C_PERS")
        person = self.db.get_person_from_handle(person.get_handle())
        self.assertIn(citation.get_handle(), person.get_citation_list())

    def test_attach_to_family(self):
        """Citation handle is added to the family's citation list."""
        with DbTxn("setup", self.db) as trans:
            family = Family()
            self.db.add_family(family, trans)
        family_gid = "[%s]" % family.get_gramps_id()

        self._run(["C_FAM", "Source", family_gid], _col("citation", "source", "family"))

        citation = self.parser.lookup("citation", "C_FAM")
        family = self.db.get_family_from_handle(family.get_handle())
        self.assertIn(citation.get_handle(), family.get_citation_list())

    def test_attach_to_event_via_gramps_id(self):
        """Citation is attached to an existing event via bracketed Gramps ID."""
        with DbTxn("setup", self.db) as trans:
            event = Event()
            event.set_type(EventType(EventType.BIRTH))
            self.db.add_event(event, trans)
        event_gid = "[%s]" % event.get_gramps_id()

        self._run(["C_EVT", "Source", event_gid], _col("citation", "source", "event"))

        citation = self.parser.lookup("citation", "C_EVT")
        event = self.db.get_event_from_handle(event.get_handle())
        self.assertIn(citation.get_handle(), event.get_citation_list())

    def test_attach_to_event_via_sheet_ref(self):
        """Citation is attached to an event defined earlier in the same sheet."""
        with DbTxn("setup", self.db) as trans:
            event = Event()
            event.set_type(EventType(EventType.CENSUS))
            self.db.add_event(event, trans)
        # Simulate a prior _parse_event having stored the sheet-local ref
        self.parser.eventref[self.db.eid2user_format("E_PRIOR").lower()] = event

        self._run(
            ["C_EVTREF", "1901 Census", "E_PRIOR"],
            _col("citation", "source", "event"),
        )

        citation = self.parser.lookup("citation", "C_EVTREF")
        event = self.db.get_event_from_handle(event.get_handle())
        self.assertIn(citation.get_handle(), event.get_citation_list())

    def test_attach_to_place_via_sheet_ref(self):
        """Citation is attached to a place defined earlier in the same sheet."""
        with DbTxn("setup", self.db) as trans:
            place = Place()
            self.db.add_place(place, trans)
        self.parser.placeref[self.db.pid2user_format("P_PRIOR").lower()] = place

        self._run(["C_PLREF", "Source", "P_PRIOR"], _col("citation", "source", "place"))

        citation = self.parser.lookup("citation", "C_PLREF")
        place = self.db.get_place_from_handle(place.get_handle())
        self.assertIn(citation.get_handle(), place.get_citation_list())

    # ------------------------------------------------------------------
    # Update existing
    # ------------------------------------------------------------------

    def test_update_existing_via_bracket_ref(self):
        """Bracket ref finds an existing DB citation and updates its page."""
        with DbTxn("setup", self.db) as trans:
            source = Source()
            source.set_title("Old Source")
            self.db.add_source(source, trans)
            citation = Citation()
            citation.set_reference_handle(source.get_handle())
            self.db.add_citation(citation, trans)
        bracket_ref = "[%s]" % citation.get_gramps_id()

        self._run([bracket_ref, "42a"], _col("citation", "page"))

        updated = self.db.get_citation_from_handle(citation.get_handle())
        self.assertEqual(updated.get_page(), "42a")

    # ------------------------------------------------------------------
    # Gramps ID preservation (regression)
    # ------------------------------------------------------------------

    def test_gramps_id_preserved_from_bracket_ref(self):
        """New citation created via [C9991] gets that gramps_id, not the auto-ID."""
        expected_id = self.db.cid2user_format("C9991")
        self._run(["[C9991]", "Test Source"], _col("citation", "source"))

        citation = self.parser.lookup("citation", "[C9991]")
        self.assertIsNotNone(citation)
        self.assertEqual(citation.get_gramps_id(), expected_id)
        self.assertIsNotNone(self.db.get_citation_from_gramps_id(expected_id))

    # ------------------------------------------------------------------
    # Error / skip cases
    # ------------------------------------------------------------------

    def test_missing_source_skips_new_citation(self):
        """Row with no source for a new citation creates nothing."""
        count_before = len(list(self.db.get_citation_handles()))
        self._run(["C_NOSRC", "12b"], _col("citation", "page"))
        self.assertEqual(len(list(self.db.get_citation_handles())), count_before)

    def test_unknown_event_ref_logs_warning(self):
        """Unknown event ref is skipped without raising an exception."""
        self._run(
            ["C_BADEV", "Source", "NONEXISTENT_EVENT"],
            _col("citation", "source", "event"),
        )
        citation = self.parser.lookup("citation", "C_BADEV")
        self.assertIsNotNone(citation)
        self.assertEqual(citation.get_citation_list(), [])


# -------------------------------------------------------------------------
#
# TestParsePerson
#
# -------------------------------------------------------------------------
class TestParsePerson(unittest.TestCase):
    """Tests for CSVParser._parse_person."""

    @classmethod
    def setUpClass(cls):
        """Create a single in-memory DB shared by all person tests."""
        cls.db = make_database("sqlite")
        cls.db.load(":memory:")

    def setUp(self):
        """Fresh parser for every test."""
        self.parser = CSVParser(self.db, _MockUser())

    def _run(self, row, col):
        """Run _parse_person inside a transaction."""
        self.db.disable_signals()
        with DbTxn("test", self.db, batch=True) as self.parser.trans:
            self.parser._parse_person(1, row, col)
        self.db.enable_signals()

    # ------------------------------------------------------------------
    # Creation
    # ------------------------------------------------------------------

    def test_create_minimal(self):
        """New person with surname and firstname is stored and retrievable."""
        self._run(["PERS_MIN", "Doe", "Jane"], _col("person", "surname", "firstname"))

        person = self.parser.lookup("person", "PERS_MIN")
        self.assertIsNotNone(person)
        name = person.get_primary_name()
        self.assertEqual(name.get_first_name(), "Jane")
        self.assertEqual(name.get_primary_surname().get_surname(), "Doe")

    def test_create_with_gender(self):
        """Gender column is parsed and set on the person."""
        self._run(
            ["PERS_GENDER", "Smith", "Bob", "male"],
            _col("person", "surname", "firstname", "gender"),
        )

        person = self.parser.lookup("person", "PERS_GENDER")
        from gramps.gen.lib import Person as _Person

        self.assertEqual(person.get_gender(), _Person.MALE)

    # ------------------------------------------------------------------
    # Gramps ID preservation (regression)
    # ------------------------------------------------------------------

    def test_gramps_id_from_grampsid_column(self):
        """grampsid column value is stored as gramps_id, not the auto-ID."""
        self._run(
            ["PERS_GID", "Smith", "SMITH-001"],
            _col("person", "surname", "grampsid"),
        )

        person = self.parser.lookup("person", "PERS_GID")
        self.assertIsNotNone(person)
        self.assertEqual(person.get_gramps_id(), "SMITH-001")

    def test_gramps_id_from_bracket_ref(self):
        """Bracket ref [I9991] becomes the person gramps_id, not the auto-ID."""
        expected_id = self.db.id2user_format("I9991")
        self._run(["[I9991]", "Jones"], _col("person", "surname"))

        person = self.parser.lookup("person", "[I9991]")
        self.assertIsNotNone(person)
        self.assertEqual(person.get_gramps_id(), expected_id)
        self.assertIsNotNone(self.db.get_person_from_gramps_id(expected_id))

    def test_grampsid_column_takes_precedence_over_bracket_ref(self):
        """Explicit grampsid column overrides the ID implied by a bracket ref."""
        self._run(
            ["[I9992]", "Brown", "BROWN-CUSTOM"],
            _col("person", "surname", "grampsid"),
        )

        person = self.parser.lookup("person", "[I9992]")
        self.assertIsNotNone(person)
        self.assertEqual(person.get_gramps_id(), "BROWN-CUSTOM")

    # ------------------------------------------------------------------
    # Update existing
    # ------------------------------------------------------------------

    def test_update_existing_via_bracket_ref(self):
        """Bracket ref finds an existing DB person and updates their name."""
        with DbTxn("setup", self.db) as trans:
            person = Person()
            self.db.add_person(person, trans)
        bracket_ref = "[%s]" % person.get_gramps_id()

        self._run([bracket_ref, "UpdatedSurname"], _col("person", "surname"))

        updated = self.db.get_person_from_handle(person.get_handle())
        self.assertEqual(
            updated.get_primary_name().get_primary_surname().get_surname(),
            "UpdatedSurname",
        )


# -------------------------------------------------------------------------
#
# TestParsePlace
#
# -------------------------------------------------------------------------
class TestParsePlace(unittest.TestCase):
    """Tests for CSVParser._parse_place."""

    @classmethod
    def setUpClass(cls):
        """Create a single in-memory DB shared by all place tests."""
        cls.db = make_database("sqlite")
        cls.db.load(":memory:")

    def setUp(self):
        """Fresh parser for every test."""
        self.parser = CSVParser(self.db, _MockUser())

    def _run(self, row, col):
        """Run _parse_place inside a transaction."""
        self.db.disable_signals()
        with DbTxn("test", self.db, batch=True) as self.parser.trans:
            self.parser._parse_place(1, row, col)
        self.db.enable_signals()

    # ------------------------------------------------------------------
    # Creation
    # ------------------------------------------------------------------

    def test_create_minimal(self):
        """New place with title is stored and retrievable."""
        self._run(["PLACE_MIN", "Springfield"], _col("place", "title"))

        place = self.parser.lookup("place", "PLACE_MIN")
        self.assertIsNotNone(place)
        self.assertEqual(place.get_title(), "Springfield")

    def test_create_with_latitude_longitude(self):
        """Latitude and longitude are stored on the place."""
        self._run(
            ["PLACE_LL", "Ocean", "51.5", "-0.1"],
            _col("place", "title", "latitude", "longitude"),
        )

        place = self.parser.lookup("place", "PLACE_LL")
        self.assertEqual(place.lat, "51.5")
        self.assertEqual(place.long, "-0.1")

    # ------------------------------------------------------------------
    # Gramps ID preservation (regression)
    # ------------------------------------------------------------------

    def test_gramps_id_from_bracket_ref(self):
        """Bracket ref [P9991] becomes the place gramps_id, not the auto-ID."""
        expected_id = self.db.pid2user_format("P9991")
        self._run(["[P9991]", "London Test"], _col("place", "title"))

        place = self.parser.lookup("place", "[P9991]")
        self.assertIsNotNone(place)
        self.assertEqual(place.get_gramps_id(), expected_id)
        self.assertIsNotNone(self.db.get_place_from_gramps_id(expected_id))

    def test_enclosed_by_stub_gramps_id_preserved(self):
        """Stub created for an unknown enclosed_by ref gets the correct gramps_id."""
        expected_enc_id = self.db.pid2user_format("P9993")
        self._run(
            ["[P9992]", "Bow", "[P9993]"],
            _col("place", "title", "enclosed_by"),
        )

        enc_place = self.parser.lookup("place", "[P9993]")
        self.assertIsNotNone(enc_place)
        self.assertEqual(enc_place.get_gramps_id(), expected_enc_id)

    # ------------------------------------------------------------------
    # Update existing
    # ------------------------------------------------------------------

    def test_update_existing_via_bracket_ref(self):
        """Bracket ref finds an existing DB place and updates its title."""
        with DbTxn("setup", self.db) as trans:
            place = Place()
            self.db.add_place(place, trans)
        bracket_ref = "[%s]" % place.get_gramps_id()

        self._run([bracket_ref, "Updated Title"], _col("place", "title"))

        updated = self.db.get_place_from_handle(place.get_handle())
        self.assertEqual(updated.get_title(), "Updated Title")


if __name__ == "__main__":
    unittest.main()

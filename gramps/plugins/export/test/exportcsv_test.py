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

"""Tests for CSV exporter _write_events, _write_citations, and helper methods."""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
import csv
import sys
import unittest
from io import StringIO
from unittest.mock import MagicMock

# -------------------------------------------------------------------------
#
# Gramps modules (gen only — safe to import before GUI mocks are in place)
#
# -------------------------------------------------------------------------
# These must be imported first: gramps.gen.plug._gramplet imports
# gramps.gui.dbguielement, which loads the real gramps.gui package.  Doing
# these imports here lets that chain succeed with the real package.  The
# problematic gramps.gui.plug sub-package is NOT loaded by this chain.
from gramps.gen.db import DbTxn
from gramps.gen.db.utils import make_database
from gramps.gen.lib import (
    Citation,
    Date,
    Event,
    EventRef,
    EventRoleType,
    EventType,
    Family,
    Note,
    NoteType,
    Person,
    Place,
    Source,
    Tag,
)

# Now stub out the GUI plug modules so that importing exportcsv.py does not
# trigger the transitive GTK chain (gui.plug → gui.widgets → buttons.py →
# GTK3 API that no longer exists in GTK4).
for _gui_mod in [
    "gramps.gui.plug",
    "gramps.gui.plug.export",
    "gramps.gui.glade",
]:
    sys.modules[_gui_mod] = MagicMock()

from gramps.plugins.export.exportcsv import CSVWriter

# -------------------------------------------------------------------------
#
# Helpers
#
# -------------------------------------------------------------------------


def _make_writer(db, translate=False):
    """
    Build a minimal CSVWriter backed by a StringIO, bypassing __init__.

    Only the attributes needed by _write_events, _write_citations, _first_note,
    and _first_tag are set.
    """
    writer = CSVWriter.__new__(CSVWriter)
    writer.db = db
    writer.include_places = True
    writer.translate_headers = translate
    writer.update = lambda: None
    output = StringIO()
    writer.g = csv.writer(output)
    return writer, output


def _read_csv(output):
    """Rewind output and return all rows as a list of lists."""
    output.seek(0)
    return list(csv.reader(output))


# -------------------------------------------------------------------------
#
# TestFirstNote
#
# -------------------------------------------------------------------------
class TestFirstNote(unittest.TestCase):
    """Tests for CSVWriter._first_note helper."""

    @classmethod
    def setUpClass(cls):
        """Single in-memory DB shared by all _first_note tests."""
        cls.db = make_database("sqlite")
        cls.db.load(":memory:")

    def test_no_notes_returns_empty_tuple(self):
        """Object with no notes returns ('', '')."""
        writer, _ = _make_writer(self.db)
        event = Event()
        self.assertEqual(writer._first_note(event), ("", ""))

    def test_single_note_returns_text_and_type(self):
        """Object with one note returns its text and type string."""
        writer, _ = _make_writer(self.db)
        with DbTxn("setup", self.db) as trans:
            note = Note()
            note.set("Hello world")
            note.set_type(NoteType(NoteType.EVENT))
            self.db.add_note(note, trans)
        event = Event()
        event.add_note(note.get_handle())
        text, type_str = writer._first_note(event)
        self.assertEqual(text, "Hello world")
        self.assertEqual(type_str, str(NoteType(NoteType.EVENT)))

    def test_returns_only_first_note(self):
        """When multiple notes exist only the first is returned."""
        writer, _ = _make_writer(self.db)
        with DbTxn("setup", self.db) as trans:
            note1 = Note()
            note1.set("First")
            self.db.add_note(note1, trans)
            note2 = Note()
            note2.set("Second")
            self.db.add_note(note2, trans)
        event = Event()
        event.add_note(note1.get_handle())
        event.add_note(note2.get_handle())
        text, _ = writer._first_note(event)
        self.assertEqual(text, "First")


# -------------------------------------------------------------------------
#
# TestFirstTag
#
# -------------------------------------------------------------------------
class TestFirstTag(unittest.TestCase):
    """Tests for CSVWriter._first_tag helper."""

    @classmethod
    def setUpClass(cls):
        """Single in-memory DB shared by all _first_tag tests."""
        cls.db = make_database("sqlite")
        cls.db.load(":memory:")

    def test_no_tags_returns_empty_string(self):
        """Object with no tags returns ''."""
        writer, _ = _make_writer(self.db)
        event = Event()
        self.assertEqual(writer._first_tag(event), "")

    def test_single_tag_returns_name(self):
        """Object with one tag returns its name."""
        writer, _ = _make_writer(self.db)
        with DbTxn("setup", self.db) as trans:
            tag = Tag()
            tag.set_name("Verified")
            self.db.add_tag(tag, trans)
        event = Event()
        event.add_tag(tag.get_handle())
        self.assertEqual(writer._first_tag(event), "Verified")

    def test_returns_only_first_tag(self):
        """When multiple tags exist only the first is returned."""
        writer, _ = _make_writer(self.db)
        with DbTxn("setup", self.db) as trans:
            tag1 = Tag()
            tag1.set_name("Alpha")
            self.db.add_tag(tag1, trans)
            tag2 = Tag()
            tag2.set_name("Beta")
            self.db.add_tag(tag2, trans)
        event = Event()
        event.add_tag(tag1.get_handle())
        event.add_tag(tag2.get_handle())
        self.assertEqual(writer._first_tag(event), "Alpha")


# -------------------------------------------------------------------------
#
# TestWriteEvents
#
# -------------------------------------------------------------------------
class TestWriteEvents(unittest.TestCase):
    """Tests for CSVWriter._write_events."""

    def setUp(self):
        """Fresh in-memory DB and writer for every test."""
        self.db = make_database("sqlite")
        self.db.load(":memory:")
        self.writer, self.output = _make_writer(self.db)

    def tearDown(self):
        self.db.close()

    def _rows(self):
        return _read_csv(self.output)

    def test_header_untranslated(self):
        """Untranslated header contains canonical lowercase column names."""
        self.writer._write_events()
        self.assertEqual(
            self._rows()[0],
            [
                "event",
                "eventtype",
                "date",
                "place",
                "description",
                "source",
                "note",
                "note_type",
                "tag",
                "person",
                "family",
                "role",
            ],
        )

    def test_header_translated_differs_from_untranslated(self):
        """Translated header first column is not 'event'."""
        writer, output = _make_writer(self.db, translate=True)
        writer._write_events()
        output.seek(0)
        rows = list(csv.reader(output))
        self.assertNotEqual(rows[0][0], "event")

    def test_empty_db_writes_header_and_blank_line(self):
        """With no events, output is header row followed by one blank row."""
        self.writer._write_events()
        rows = self._rows()
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[1], [])

    def test_event_id_and_type(self):
        """Event row has bracketed gramps_id and type string."""
        with DbTxn("setup", self.db) as trans:
            event = Event()
            event.set_type(EventType(EventType.BIRTH))
            self.db.add_event(event, trans)
        self.writer._write_events()
        rows = self._rows()
        self.assertEqual(rows[1][0], "[%s]" % event.get_gramps_id())
        self.assertEqual(rows[1][1], str(EventType(EventType.BIRTH)))

    def test_event_date(self):
        """Date column is non-empty when the event has a date."""
        with DbTxn("setup", self.db) as trans:
            event = Event()
            event.set_type(EventType(EventType.BIRTH))
            date_obj = Date()
            date_obj.set_yr_mon_day(1900, 6, 15)
            event.set_date_object(date_obj)
            self.db.add_event(event, trans)
        self.writer._write_events()
        rows = self._rows()
        self.assertIn("1900", rows[1][2])

    def test_event_place(self):
        """Place column contains bracketed place gramps_id."""
        with DbTxn("setup", self.db) as trans:
            place = Place()
            place.set_title("London")
            self.db.add_place(place, trans)
            event = Event()
            event.set_type(EventType(EventType.BIRTH))
            event.set_place_handle(place.get_handle())
            self.db.add_event(event, trans)
        self.writer._write_events()
        rows = self._rows()
        self.assertEqual(rows[1][3], "[%s]" % place.get_gramps_id())

    def test_event_description(self):
        """Description column holds the event description."""
        with DbTxn("setup", self.db) as trans:
            event = Event()
            event.set_type(EventType(EventType.CENSUS))
            event.set_description("Household of five")
            self.db.add_event(event, trans)
        self.writer._write_events()
        rows = self._rows()
        self.assertEqual(rows[1][4], "Household of five")

    def test_event_source(self):
        """Source column contains the title of the first source citation."""
        with DbTxn("setup", self.db) as trans:
            source = Source()
            source.set_title("1901 Census")
            self.db.add_source(source, trans)
            citation = Citation()
            citation.set_reference_handle(source.get_handle())
            self.db.add_citation(citation, trans)
            event = Event()
            event.set_type(EventType(EventType.CENSUS))
            event.add_citation(citation.get_handle())
            self.db.add_event(event, trans)
        self.writer._write_events()
        rows = self._rows()
        self.assertEqual(rows[1][5], "1901 Census")

    def test_event_note_text_and_type(self):
        """Note and note_type columns hold the first note's text and type."""
        with DbTxn("setup", self.db) as trans:
            note = Note()
            note.set("Check handwriting")
            note.set_type(NoteType(NoteType.EVENT))
            self.db.add_note(note, trans)
            event = Event()
            event.set_type(EventType(EventType.CENSUS))
            event.add_note(note.get_handle())
            self.db.add_event(event, trans)
        self.writer._write_events()
        rows = self._rows()
        self.assertEqual(rows[1][6], "Check handwriting")
        self.assertEqual(rows[1][7], str(NoteType(NoteType.EVENT)))

    def test_event_tag(self):
        """Tag column holds the first tag name."""
        with DbTxn("setup", self.db) as trans:
            tag = Tag()
            tag.set_name("Verified")
            self.db.add_tag(tag, trans)
            event = Event()
            event.set_type(EventType(EventType.CENSUS))
            event.add_tag(tag.get_handle())
            self.db.add_event(event, trans)
        self.writer._write_events()
        rows = self._rows()
        self.assertEqual(rows[1][8], "Verified")

    def test_event_person_backlink(self):
        """Person backlink writes person gramps_id in person column."""
        with DbTxn("setup", self.db) as trans:
            event = Event()
            event.set_type(EventType(EventType.BIRTH))
            self.db.add_event(event, trans)
            eref = EventRef()
            eref.ref = event.get_handle()
            eref.set_role(EventRoleType(EventRoleType.PRIMARY))
            person = Person()
            person.add_event_ref(eref)
            self.db.add_person(person, trans)
        self.writer._write_events()
        rows = self._rows()
        self.assertEqual(rows[1][9], "[%s]" % person.get_gramps_id())
        self.assertEqual(rows[1][10], "")
        self.assertEqual(rows[1][11], str(EventRoleType(EventRoleType.PRIMARY)))

    def test_event_family_backlink(self):
        """Family backlink writes family gramps_id in family column."""
        with DbTxn("setup", self.db) as trans:
            event = Event()
            event.set_type(EventType(EventType.MARRIAGE))
            self.db.add_event(event, trans)
            eref = EventRef()
            eref.ref = event.get_handle()
            eref.set_role(EventRoleType(EventRoleType.FAMILY))
            family = Family()
            family.add_event_ref(eref)
            self.db.add_family(family, trans)
        self.writer._write_events()
        rows = self._rows()
        self.assertEqual(rows[1][9], "")
        self.assertEqual(rows[1][10], "[%s]" % family.get_gramps_id())
        self.assertEqual(rows[1][11], str(EventRoleType(EventRoleType.FAMILY)))

    def test_event_no_backlinks_writes_empty_ref_columns(self):
        """Event with no person or family refs has empty person/family/role."""
        with DbTxn("setup", self.db) as trans:
            event = Event()
            event.set_type(EventType(EventType.DEATH))
            self.db.add_event(event, trans)
        self.writer._write_events()
        rows = self._rows()
        self.assertEqual(rows[1][9], "")
        self.assertEqual(rows[1][10], "")
        self.assertEqual(rows[1][11], "")

    def test_event_multiple_person_refs_produce_continuation_rows(self):
        """Two person refs yield a data row plus one continuation row."""
        with DbTxn("setup", self.db) as trans:
            event = Event()
            event.set_type(EventType(EventType.CENSUS))
            self.db.add_event(event, trans)
            eref1 = EventRef()
            eref1.ref = event.get_handle()
            eref1.set_role(EventRoleType(EventRoleType.PRIMARY))
            person1 = Person()
            person1.add_event_ref(eref1)
            self.db.add_person(person1, trans)
            eref2 = EventRef()
            eref2.ref = event.get_handle()
            eref2.set_role(EventRoleType(EventRoleType.WITNESS))
            person2 = Person()
            person2.add_event_ref(eref2)
            self.db.add_person(person2, trans)
        self.writer._write_events()
        rows = self._rows()
        # header + data row + continuation + blank
        self.assertEqual(len(rows), 4)
        event_id = "[%s]" % event.get_gramps_id()
        self.assertEqual(rows[1][0], event_id)
        self.assertEqual(rows[2][0], event_id)
        # First data row has the type; continuation row leaves it empty
        self.assertNotEqual(rows[1][1], "")
        self.assertEqual(rows[2][1], "")


# -------------------------------------------------------------------------
#
# TestWriteCitations
#
# -------------------------------------------------------------------------
class TestWriteCitations(unittest.TestCase):
    """Tests for CSVWriter._write_citations."""

    def setUp(self):
        """Fresh in-memory DB and writer for every test."""
        self.db = make_database("sqlite")
        self.db.load(":memory:")
        self.writer, self.output = _make_writer(self.db)

    def tearDown(self):
        self.db.close()

    def _rows(self):
        return _read_csv(self.output)

    def _add_citation(self, trans, title="Test Source", page="", confidence=None):
        """Add a source and linked citation; return (source, citation)."""
        source = Source()
        source.set_title(title)
        self.db.add_source(source, trans)
        citation = Citation()
        citation.set_reference_handle(source.get_handle())
        if page:
            citation.set_page(page)
        if confidence is not None:
            citation.set_confidence_level(confidence)
        self.db.add_citation(citation, trans)
        return source, citation

    def test_header_untranslated(self):
        """Untranslated header contains canonical lowercase column names."""
        self.writer._write_citations()
        self.assertEqual(
            self._rows()[0],
            [
                "citation",
                "source",
                "page",
                "date",
                "confidence",
                "note",
                "note_type",
                "tag",
                "person",
                "family",
                "event",
                "place",
            ],
        )

    def test_empty_db_writes_header_and_blank_line(self):
        """With no citations, output is header row followed by one blank row."""
        self.writer._write_citations()
        rows = self._rows()
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[1], [])

    def test_citation_id_and_source(self):
        """Citation row has bracketed gramps_id and source title."""
        with DbTxn("setup", self.db) as trans:
            source, citation = self._add_citation(trans, "1901 Census")
        self.writer._write_citations()
        rows = self._rows()
        self.assertEqual(rows[1][0], "[%s]" % citation.get_gramps_id())
        self.assertEqual(rows[1][1], "1901 Census")

    def test_citation_page(self):
        """Page column holds the citation page value."""
        with DbTxn("setup", self.db) as trans:
            _, citation = self._add_citation(trans, page="12b")
        self.writer._write_citations()
        rows = self._rows()
        self.assertEqual(rows[1][2], "12b")

    def test_citation_confidence(self):
        """Confidence column holds the integer confidence level."""
        with DbTxn("setup", self.db) as trans:
            _, citation = self._add_citation(trans, confidence=Citation.CONF_HIGH)
        self.writer._write_citations()
        rows = self._rows()
        self.assertEqual(int(rows[1][4]), Citation.CONF_HIGH)

    def test_citation_date(self):
        """Date column is non-empty when the citation has a date."""
        with DbTxn("setup", self.db) as trans:
            source = Source()
            source.set_title("Register")
            self.db.add_source(source, trans)
            date_obj = Date()
            date_obj.set_yr_mon_day(1885, 6, 20)
            citation = Citation()
            citation.set_reference_handle(source.get_handle())
            citation.set_date_object(date_obj)
            self.db.add_citation(citation, trans)
        self.writer._write_citations()
        rows = self._rows()
        self.assertIn("1885", rows[1][3])

    def test_citation_note(self):
        """Note and note_type columns hold the first note's text and type."""
        with DbTxn("setup", self.db) as trans:
            note = Note()
            note.set("Original at TNA")
            note.set_type(NoteType(NoteType.CITATION))
            self.db.add_note(note, trans)
            source = Source()
            source.set_title("Source")
            self.db.add_source(source, trans)
            citation = Citation()
            citation.set_reference_handle(source.get_handle())
            citation.add_note(note.get_handle())
            self.db.add_citation(citation, trans)
        self.writer._write_citations()
        rows = self._rows()
        self.assertEqual(rows[1][5], "Original at TNA")
        self.assertEqual(rows[1][6], str(NoteType(NoteType.CITATION)))

    def test_citation_tag(self):
        """Tag column holds the first tag name."""
        with DbTxn("setup", self.db) as trans:
            tag = Tag()
            tag.set_name("Verified")
            self.db.add_tag(tag, trans)
            source = Source()
            source.set_title("Source")
            self.db.add_source(source, trans)
            citation = Citation()
            citation.set_reference_handle(source.get_handle())
            citation.add_tag(tag.get_handle())
            self.db.add_citation(citation, trans)
        self.writer._write_citations()
        rows = self._rows()
        self.assertEqual(rows[1][7], "Verified")

    def test_citation_person_backlink(self):
        """Person backlink writes person gramps_id in person column."""
        with DbTxn("setup", self.db) as trans:
            _, citation = self._add_citation(trans)
            person = Person()
            person.add_citation(citation.get_handle())
            self.db.add_person(person, trans)
        self.writer._write_citations()
        rows = self._rows()
        self.assertEqual(rows[1][8], "[%s]" % person.get_gramps_id())
        self.assertEqual(rows[1][9], "")
        self.assertEqual(rows[1][10], "")
        self.assertEqual(rows[1][11], "")

    def test_citation_family_backlink(self):
        """Family backlink writes family gramps_id in family column."""
        with DbTxn("setup", self.db) as trans:
            _, citation = self._add_citation(trans)
            family = Family()
            family.add_citation(citation.get_handle())
            self.db.add_family(family, trans)
        self.writer._write_citations()
        rows = self._rows()
        self.assertEqual(rows[1][8], "")
        self.assertEqual(rows[1][9], "[%s]" % family.get_gramps_id())
        self.assertEqual(rows[1][10], "")
        self.assertEqual(rows[1][11], "")

    def test_citation_event_backlink(self):
        """Event backlink writes event gramps_id in event column."""
        with DbTxn("setup", self.db) as trans:
            _, citation = self._add_citation(trans)
            event = Event()
            event.set_type(EventType(EventType.CENSUS))
            event.add_citation(citation.get_handle())
            self.db.add_event(event, trans)
        self.writer._write_citations()
        rows = self._rows()
        self.assertEqual(rows[1][8], "")
        self.assertEqual(rows[1][9], "")
        self.assertEqual(rows[1][10], "[%s]" % event.get_gramps_id())
        self.assertEqual(rows[1][11], "")

    def test_citation_place_backlink(self):
        """Place backlink writes place gramps_id in place column."""
        with DbTxn("setup", self.db) as trans:
            _, citation = self._add_citation(trans)
            place = Place()
            place.add_citation(citation.get_handle())
            self.db.add_place(place, trans)
        self.writer._write_citations()
        rows = self._rows()
        self.assertEqual(rows[1][8], "")
        self.assertEqual(rows[1][9], "")
        self.assertEqual(rows[1][10], "")
        self.assertEqual(rows[1][11], "[%s]" % place.get_gramps_id())

    def test_citation_no_backlinks_writes_empty_ref_columns(self):
        """Citation with no backlinks has empty person/family/event/place."""
        with DbTxn("setup", self.db) as trans:
            self._add_citation(trans)
        self.writer._write_citations()
        rows = self._rows()
        self.assertEqual(rows[1][8], "")
        self.assertEqual(rows[1][9], "")
        self.assertEqual(rows[1][10], "")
        self.assertEqual(rows[1][11], "")

    def test_citation_multiple_backlinks_produce_continuation_rows(self):
        """Two person backlinks yield a data row plus one continuation row."""
        with DbTxn("setup", self.db) as trans:
            _, citation = self._add_citation(trans)
            person1 = Person()
            person1.add_citation(citation.get_handle())
            self.db.add_person(person1, trans)
            person2 = Person()
            person2.add_citation(citation.get_handle())
            self.db.add_person(person2, trans)
        self.writer._write_citations()
        rows = self._rows()
        # header + data row + continuation + blank
        self.assertEqual(len(rows), 4)
        citation_id = "[%s]" % citation.get_gramps_id()
        self.assertEqual(rows[1][0], citation_id)
        self.assertEqual(rows[2][0], citation_id)
        # First data row has the source title; continuation row leaves it empty
        self.assertNotEqual(rows[1][1], "")
        self.assertEqual(rows[2][1], "")


if __name__ == "__main__":
    unittest.main()

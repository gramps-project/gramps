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

"""Gramps XML export and re-import tests for DNATest and DNAMatch objects."""

import os
import shutil
import tempfile
import unittest

from gramps.gen.db import DbTxn
from gramps.gen.db.utils import import_as_dict, make_database
from gramps.gen.lib import (
    Citation,
    Date,
    DNAAttribute,
    DNAAttributeType,
    DNAGenomeBuildType,
    DNAMatch,
    DNAProviderType,
    DNASegment,
    DNATest,
    DNATestType,
    Media,
    MediaRef,
    Note,
    Person,
    PredictedRelationship,
    SharedAncestor,
    Source,
    Tag,
)
from gramps.gen.lib.json_utils import object_to_dict
from gramps.gen.user import User

# The XML writer imports gramps.gui, so these tests need GTK 3.
try:
    import gi

    gi.require_version("Gtk", "3.0")
    from gramps.plugins.export.exportxml import XmlWriter

    _WRITER_AVAILABLE = True
except (ImportError, ValueError):
    _WRITER_AVAILABLE = False


@unittest.skipUnless(_WRITER_AVAILABLE, "GTK 3 not available for the XML writer")
class TestDNARoundTrip(unittest.TestCase):
    """DNA objects read back from an XML export equal the objects written."""

    maxDiff = None

    @classmethod
    def setUpClass(cls):
        cls.tmpdir = tempfile.mkdtemp()
        dbdir = os.path.join(cls.tmpdir, "db")
        os.mkdir(dbdir)
        db = make_database("sqlite")
        db.load(dbdir)
        try:
            cls._populate(db)
            cls.written = {
                handle: object_to_dict(db.get_dnatest_from_handle(handle))
                for handle in db.get_dnatest_handles()
            }
            cls.written.update(
                (handle, object_to_dict(db.get_dnamatch_from_handle(handle)))
                for handle in db.get_dnamatch_handles()
            )
            filename = os.path.join(cls.tmpdir, "export.gramps")
            XmlWriter(db, User(), 0, compress=0).write(filename)
        finally:
            db.close()
        imported = import_as_dict(filename, User())
        cls.read = {obj.handle: object_to_dict(obj) for obj in imported.iter_dnatests()}
        cls.read.update(
            (obj.handle, object_to_dict(obj)) for obj in imported.iter_dnamatches()
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmpdir)

    @classmethod
    def _populate(cls, db):
        """Add the referenced objects and the DNA objects under test to db."""
        with DbTxn("add DNA", db) as trans:
            person = db.add_person(Person(), trans)
            note = Note()
            note.set("A note")
            note = db.add_note(note, trans)
            source = db.add_source(Source(), trans)
            citation = Citation()
            citation.set_reference_handle(source)
            citation = db.add_citation(citation, trans)
            media = Media()
            media.set_path("kit.png")
            media = db.add_media(media, trans)
            tag = Tag()
            tag.set_name("DNA")
            tag = db.add_tag(tag, trans)
            refs = (note, citation, media, tag)

            cls.test_full = db.add_dnatest(cls._full_test(person, refs), trans)
            cls.test_custom = db.add_dnatest(cls._custom_test(), trans)
            cls.test_empty = db.add_dnatest(cls._empty_test(), trans)
            cls.test_default = db.add_dnatest(DNATest(), trans)

            match = cls._full_match(cls.test_full, cls.test_custom, person, refs)
            cls.match_full = db.add_dnamatch(match, trans)
            match = cls._empty_match(cls.test_empty, cls.test_default)
            cls.match_empty = db.add_dnamatch(match, trans)
            cls.match_default = db.add_dnamatch(DNAMatch(), trans)

    @staticmethod
    def _add_refs(obj, refs):
        """Attach the note, citation, media and tag in refs to obj."""
        note, citation, media, tag = refs
        obj.add_note(note)
        obj.add_citation(citation)
        media_ref = MediaRef()
        media_ref.set_reference_handle(media)
        obj.add_media_reference(media_ref)
        obj.add_tag(tag)

    @staticmethod
    def _attribute(refs):
        """Return a DNA attribute with a custom type, a note and a citation."""
        note, citation, _media, _tag = refs
        attribute = DNAAttribute()
        attribute.set_type((DNAAttributeType.CUSTOM, "DYS393"))
        attribute.set_value("13")
        attribute.add_note(note)
        attribute.add_citation(citation)
        return attribute

    @classmethod
    def _full_test(cls, person, refs):
        """Return a DNATest with every field set to a standard value."""
        test = DNATest()
        test.set_person_handle(person)
        test.set_account_name("Alice Smith")
        test.set_provider(DNAProviderType.ANCESTRY)
        test.set_kit_id("KIT12345")
        test.set_test_type(DNATestType.AUTOSOMAL)
        test.set_genome_build(DNAGenomeBuildType.GRCH37)
        date = Date()
        date.set_yr_mon_day(2022, 3, 15)
        test.set_date_object(date)
        test.set_y_haplogroup("R-L21")
        test.set_mt_haplogroup("H1a")
        test.add_attribute(cls._attribute(refs))
        cls._add_refs(test, refs)
        test.set_privacy(True)
        return test

    @staticmethod
    def _custom_test():
        """Return a DNATest with custom types and a text-only date."""
        test = DNATest()
        test.set_provider((DNAProviderType.CUSTOM, "Nebula Genomics"))
        test.set_test_type((DNATestType.CUSTOM, "Y-DNA 500"))
        test.set_genome_build((DNAGenomeBuildType.CUSTOM, "CHM13"))
        date = Date()
        date.set_as_text("spring 2020")
        test.set_date_object(date)
        return test

    @staticmethod
    def _empty_test():
        """Return a DNATest with empty custom types and an empty text-only date."""
        test = DNATest()
        test.set_provider((DNAProviderType.CUSTOM, ""))
        test.set_test_type((DNATestType.CUSTOM, ""))
        test.set_genome_build((DNAGenomeBuildType.CUSTOM, ""))
        date = Date()
        date.set_as_text("")
        test.set_date_object(date)
        return test

    @classmethod
    def _full_match(cls, subject, other, person, refs):
        """Return a DNAMatch with every field set and floats beyond six digits."""
        note, citation, _media, _tag = refs
        match = DNAMatch()
        match.set_subject_test_handle(subject)
        match.set_match_test_handle(other)
        match.set_provider(DNAProviderType.ANCESTRY)
        match.set_shared_cm(8.811977)
        match.set_shared_cm_weighted(9.634006)
        match.set_percent_shared(0.12345678)
        match.set_segment_count(2)
        match.set_largest_segment_cm(6.0497923)
        match.set_largest_segment_cm_weighted(5.9876543)
        relationship = PredictedRelationship()
        relationship.set_description("2nd cousin")
        relationship.set_subject_mrca_gens(3)
        relationship.set_subject_side(1)
        relationship.set_match_mrca_gens(3)
        relationship.set_match_side(2)
        relationship.set_full_or_half(1)
        relationship.set_probability(0.87654321)
        relationship.add_note(note)
        relationship.add_citation(citation)
        match.add_predicted_relationship(relationship)
        ancestor = SharedAncestor()
        ancestor.set_person_handle(person)
        ancestor.set_description("Great-grandfather")
        ancestor.set_confidence(2)
        ancestor.add_note(note)
        ancestor.add_citation(citation)
        match.add_shared_ancestor(ancestor)
        segment = DNASegment()
        segment.set_chromosome("1")
        segment.set_start_bp(1000)
        segment.set_end_bp(2000)
        segment.set_start_rsid("rs123")
        segment.set_end_rsid("rs456")
        segment.set_shared_cm(12.3456789)
        segment.set_shared_cm_weighted(11.2345678)
        segment.set_snp_count(700)
        segment.set_origin(DNASegment.ORIGIN_MATERNAL)
        segment.set_ibd_state(DNASegment.IBD_FIR)
        segment.set_genome_build(DNAGenomeBuildType.GRCH37)
        match.add_segment(segment)
        segment = DNASegment()
        segment.set_chromosome("X")
        segment.set_start_bp(5000)
        segment.set_end_bp(6000)
        segment.set_shared_cm(7.25)
        segment.set_genome_build((DNAGenomeBuildType.CUSTOM, "CHM13"))
        match.add_segment(segment)
        match.add_attribute(cls._attribute(refs))
        cls._add_refs(match, refs)
        match.set_privacy(True)
        return match

    @staticmethod
    def _empty_match(subject, other):
        """Return a DNAMatch with empty custom types and zero statistics."""
        match = DNAMatch()
        match.set_subject_test_handle(subject)
        match.set_match_test_handle(other)
        match.set_provider((DNAProviderType.CUSTOM, ""))
        segment = DNASegment()
        segment.set_chromosome("2")
        segment.set_genome_build((DNAGenomeBuildType.CUSTOM, ""))
        match.add_segment(segment)
        return match

    def _assert_round_trip(self, handle):
        """Assert that the object with handle reads back as it was written."""
        self.assertIn(handle, self.read)
        self.assertEqual(self.read[handle], self.written[handle])

    def test_dnatest_all_fields(self):
        self._assert_round_trip(self.test_full)

    def test_dnatest_custom_values(self):
        self._assert_round_trip(self.test_custom)

    def test_dnatest_empty_values(self):
        self._assert_round_trip(self.test_empty)

    def test_dnatest_defaults(self):
        self._assert_round_trip(self.test_default)

    def test_dnamatch_all_fields(self):
        self._assert_round_trip(self.match_full)

    def test_dnamatch_empty_values(self):
        self._assert_round_trip(self.match_empty)

    def test_dnamatch_defaults(self):
        self._assert_round_trip(self.match_default)


@unittest.skipUnless(_WRITER_AVAILABLE, "GTK 3 not available for the XML writer")
class TestDNAFloatExport(unittest.TestCase):
    """DNA float fields are written as floats or the export fails."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        dbdir = os.path.join(self.tmpdir, "db")
        os.mkdir(dbdir)
        self.db = make_database("sqlite")
        self.db.load(dbdir)
        self.filename = os.path.join(self.tmpdir, "export.gramps")

    def tearDown(self):
        self.db.close()
        shutil.rmtree(self.tmpdir)

    def _export_segment_cm(self, value):
        """Export a match whose one segment has shared_cm set to value."""
        match = DNAMatch()
        segment = DNASegment()
        segment.set_chromosome("1")
        segment.set_shared_cm(value)
        match.add_segment(segment)
        with DbTxn("add match", self.db) as trans:
            self.db.add_dnamatch(match, trans)
        XmlWriter(self.db, User(), 0, compress=0).write(self.filename)

    def test_none_fails_export(self):
        with self.assertRaises(TypeError):
            self._export_segment_cm(None)

    def test_int_written_as_float(self):
        self._export_segment_cm(70)
        with open(self.filename, encoding="utf-8") as xml:
            self.assertIn('shared_cm="70.0"', xml.read())


if __name__ == "__main__":
    unittest.main()

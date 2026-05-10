#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026 Ian Davis
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

"""Gramps XML 1.8.0 import tests for DNATest and DNAMatch objects."""

import os
import tempfile
import unittest

from gramps.gen.db.utils import import_as_dict
from gramps.gen.lib import DNASegment, SharedAncestor
from gramps.gen.user import User

# Minimal Gramps XML 1.8.0 document with a DNATest.
_DNATEST_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE database PUBLIC "-//Gramps//DTD Gramps XML 1.8.0//EN"
"http://gramps-project.org/xml/1.8.0/grampsxml.dtd">
<database xmlns="http://gramps-project.org/xml/1.8.0/">
  <header>
    <created date="2026-01-01" version="6.1.0"/>
    <researcher/>
  </header>
  <people>
    <person handle="_pa0001" change="0" id="I0001">
      <gender>M</gender>
      <name type="Birth Name">
        <first>Test</first>
        <surname>Person</surname>
      </name>
    </person>
  </people>
  <dnatests>
    <dnatest handle="_dt0001" change="0" id="T00001">
      <person hlink="_pa0001"/>
      <account_name>Alice Smith</account_name>
      <provider>AncestryDNA</provider>
      <kit_id>KIT12345</kit_id>
      <test_type>Autosomal</test_type>
      <genome_build>GRCh37</genome_build>
      <dateval val="2022-03-15"/>
      <haplogroup>H1a</haplogroup>
    </dnatest>
  </dnatests>
</database>
"""

# Minimal Gramps XML 1.8.0 document with a DNAMatch that references two
# DNATests, includes a shared ancestor and a DNA segment.
_DNAMATCH_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE database PUBLIC "-//Gramps//DTD Gramps XML 1.8.0//EN"
"http://gramps-project.org/xml/1.8.0/grampsxml.dtd">
<database xmlns="http://gramps-project.org/xml/1.8.0/">
  <header>
    <created date="2026-01-01" version="6.1.0"/>
    <researcher/>
  </header>
  <people>
    <person handle="_pa0001" change="0" id="I0001">
      <gender>M</gender>
      <name type="Birth Name"><first>Subject</first><surname>Person</surname></name>
    </person>
    <person handle="_pa0002" change="0" id="I0002">
      <gender>F</gender>
      <name type="Birth Name"><first>Match</first><surname>Person</surname></name>
    </person>
    <person handle="_pa0003" change="0" id="I0003">
      <gender>M</gender>
      <name type="Birth Name"><first>Ancestor</first><surname>Person</surname></name>
    </person>
  </people>
  <dnatests>
    <dnatest handle="_dt0001" change="0" id="T00001">
      <person hlink="_pa0001"/>
    </dnatest>
    <dnatest handle="_dt0002" change="0" id="T00002">
      <person hlink="_pa0002"/>
    </dnatest>
  </dnatests>
  <dnamatches>
    <dnamatch handle="_dm0001" change="0" id="M00001">
      <subject_test hlink="_dt0001"/>
      <match_test hlink="_dt0002"/>
      <shared_cm val="45.3"/>
      <percent_shared val="0.67"/>
      <segment_count val="3"/>
      <largest_segment_cm val="20.1"/>
      <predicted_relationship>2nd cousin</predicted_relationship>
      <predicted_generations val="3.5"/>
      <shared_ancestor confidence="1">
        <description>Through maternal line</description>
        <person hlink="_pa0003"/>
      </shared_ancestor>
      <dna_segment chromosome="3" start_bp="10000000" end_bp="20000000"
                   shared_cm="12.5" snp_count="1200" phase="2"
                   start_rsid="rs123456" end_rsid="rs789012"/>
    </dnamatch>
  </dnamatches>
</database>
"""


def _import_xml_string(xml):
    """Write xml to a temp .gramps file and import it; return the database."""
    user = User()
    with tempfile.NamedTemporaryFile(
        suffix=".gramps", delete=False, mode="w", encoding="utf-8"
    ) as fh:
        fh.write(xml)
        tmpfile = fh.name
    try:
        return import_as_dict(tmpfile, user)
    finally:
        os.unlink(tmpfile)


class TestDNATestImport(unittest.TestCase):
    """Import a DNATest XML document and verify all fields."""

    @classmethod
    def setUpClass(cls):
        cls.db = _import_xml_string(_DNATEST_XML)

    def test_import_succeeded(self):
        self.assertIsNotNone(self.db)

    def test_one_dnatest(self):
        self.assertEqual(len(list(self.db.get_dnatest_handles())), 1)

    def test_gramps_id(self):
        dt = self.db.get_dnatest_from_handle(list(self.db.get_dnatest_handles())[0])
        self.assertEqual(dt.get_gramps_id(), "T00001")

    def test_person_handle(self):
        dt = self.db.get_dnatest_from_handle(list(self.db.get_dnatest_handles())[0])
        self.assertIsNotNone(dt.get_person_handle())

    def test_account_name(self):
        dt = self.db.get_dnatest_from_handle(list(self.db.get_dnatest_handles())[0])
        self.assertEqual(dt.get_account_name(), "Alice Smith")

    def test_provider(self):
        dt = self.db.get_dnatest_from_handle(list(self.db.get_dnatest_handles())[0])
        self.assertEqual(dt.get_provider().xml_str(), "AncestryDNA")

    def test_kit_id(self):
        dt = self.db.get_dnatest_from_handle(list(self.db.get_dnatest_handles())[0])
        self.assertEqual(dt.get_kit_id(), "KIT12345")

    def test_test_type(self):
        dt = self.db.get_dnatest_from_handle(list(self.db.get_dnatest_handles())[0])
        self.assertEqual(dt.get_test_type().xml_str(), "Autosomal")

    def test_genome_build(self):
        dt = self.db.get_dnatest_from_handle(list(self.db.get_dnatest_handles())[0])
        self.assertEqual(dt.get_genome_build().xml_str(), "GRCh37")

    def test_date(self):
        dt = self.db.get_dnatest_from_handle(list(self.db.get_dnatest_handles())[0])
        date = dt.get_date_object()
        self.assertFalse(date.is_empty())
        self.assertEqual(date.get_year(), 2022)
        self.assertEqual(date.get_month(), 3)
        self.assertEqual(date.get_day(), 15)

    def test_haplogroup(self):
        dt = self.db.get_dnatest_from_handle(list(self.db.get_dnatest_handles())[0])
        self.assertEqual(dt.get_haplogroup(), "H1a")


class TestDNAMatchImport(unittest.TestCase):
    """Import a DNAMatch XML document and verify all fields."""

    @classmethod
    def setUpClass(cls):
        cls.db = _import_xml_string(_DNAMATCH_XML)

    def _dm(self):
        return self.db.get_dnamatch_from_handle(list(self.db.get_dnamatch_handles())[0])

    def test_import_succeeded(self):
        self.assertIsNotNone(self.db)

    def test_counts(self):
        self.assertEqual(len(list(self.db.get_dnamatch_handles())), 1)
        self.assertEqual(len(list(self.db.get_dnatest_handles())), 2)

    def test_gramps_id(self):
        self.assertEqual(self._dm().get_gramps_id(), "M00001")

    def test_test_handles(self):
        dm = self._dm()
        self.assertIsNotNone(dm.get_subject_test_handle())
        self.assertIsNotNone(dm.get_match_test_handle())

    def test_statistics(self):
        dm = self._dm()
        self.assertAlmostEqual(dm.get_shared_cm(), 45.3, places=4)
        self.assertAlmostEqual(dm.get_percent_shared(), 0.67, places=4)
        self.assertEqual(dm.get_segment_count(), 3)
        self.assertAlmostEqual(dm.get_largest_segment_cm(), 20.1, places=4)

    def test_predicted_fields(self):
        dm = self._dm()
        self.assertEqual(dm.get_predicted_relationship(), "2nd cousin")
        self.assertAlmostEqual(dm.get_predicted_generations(), 3.5, places=4)

    def test_shared_ancestor(self):
        ancestors = self._dm().get_shared_ancestor_list()
        self.assertEqual(len(ancestors), 1)
        sa = ancestors[0]
        self.assertEqual(sa.get_confidence(), SharedAncestor.CONF_PROBABLE)
        self.assertEqual(sa.get_description(), "Through maternal line")
        self.assertIsNotNone(sa.get_person_handle())

    def test_segment(self):
        segments = self._dm().get_segment_list()
        self.assertEqual(len(segments), 1)
        seg = segments[0]
        self.assertEqual(seg.get_chromosome(), "3")
        self.assertEqual(seg.get_start_bp(), 10000000)
        self.assertEqual(seg.get_end_bp(), 20000000)
        self.assertAlmostEqual(seg.get_shared_cm(), 12.5, places=4)
        self.assertEqual(seg.get_snp_count(), 1200)
        self.assertEqual(seg.get_phase(), DNASegment.PHASE_MATERNAL)
        self.assertEqual(seg.get_start_rsid(), "rs123456")
        self.assertEqual(seg.get_end_rsid(), "rs789012")


# DNATest with no person element - kit owner not yet identified.
_DNATEST_UNIDENTIFIED_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE database PUBLIC "-//Gramps//DTD Gramps XML 1.8.0//EN"
"http://gramps-project.org/xml/1.8.0/grampsxml.dtd">
<database xmlns="http://gramps-project.org/xml/1.8.0/">
  <header>
    <created date="2026-01-01" version="6.1.0"/>
    <researcher/>
  </header>
  <dnatests>
    <dnatest handle="_dt0001" change="0" id="T00001">
      <account_name>jcbrown52</account_name>
      <provider>GEDmatch</provider>
      <kit_id>MM2847A</kit_id>
      <test_type>Autosomal</test_type>
      <genome_build>GRCh37</genome_build>
    </dnatest>
  </dnatests>
</database>
"""


class TestDNATestUnidentified(unittest.TestCase):
    """Import a DNATest with no person handle and verify it round-trips cleanly."""

    @classmethod
    def setUpClass(cls):
        cls.db = _import_xml_string(_DNATEST_UNIDENTIFIED_XML)

    def _dt(self):
        return self.db.get_dnatest_from_handle(list(self.db.get_dnatest_handles())[0])

    def test_import_succeeded(self):
        self.assertIsNotNone(self.db)

    def test_one_dnatest(self):
        self.assertEqual(len(list(self.db.get_dnatest_handles())), 1)

    def test_no_person_handle(self):
        self.assertFalse(self._dt().get_person_handle())

    def test_fields_intact(self):
        dt = self._dt()
        self.assertEqual(dt.get_account_name(), "jcbrown52")
        self.assertEqual(dt.get_provider().xml_str(), "GEDmatch")
        self.assertEqual(dt.get_kit_id(), "MM2847A")
        self.assertEqual(dt.get_test_type().xml_str(), "Autosomal")
        self.assertEqual(dt.get_genome_build().xml_str(), "GRCh37")


if __name__ == "__main__":
    unittest.main()

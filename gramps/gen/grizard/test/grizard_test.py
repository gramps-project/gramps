#
# Gramps - a GTK+/GNOME based genealogy program
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
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Unit tests for the Grizard import framework and GEDCOM implementation.
"""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
from __future__ import annotations
import os
import shutil
import tempfile
import unittest

# Set up test resources environment variables before importing any Gramps module
ROOT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..")
)
resource_path = os.environ.get("GRAMPS_RESOURCES")
if not resource_path or not os.path.exists(
    os.path.join(resource_path, "gramps", "authors.xml")
):
    resource_path = tempfile.mkdtemp(prefix="gramps-resources-")
    os.makedirs(os.path.join(resource_path, "gramps", "images"), exist_ok=True)
    os.makedirs(os.path.join(resource_path, "doc", "gramps"), exist_ok=True)
    os.makedirs(os.path.join(resource_path, "locale"), exist_ok=True)

    shutil.copyfile(
        os.path.join(ROOT_DIR, "data", "authors.xml"),
        os.path.join(resource_path, "gramps", "authors.xml"),
    )
    shutil.copyfile(
        os.path.join(ROOT_DIR, "images", "gramps.png"),
        os.path.join(resource_path, "gramps", "images", "gramps.png"),
    )
    shutil.copyfile(
        os.path.join(ROOT_DIR, "COPYING"),
        os.path.join(resource_path, "doc", "gramps", "COPYING"),
    )

os.environ["GRAMPS_RESOURCES"] = resource_path
os.environ["HOME"] = os.environ.get("HOME") or tempfile.mkdtemp(prefix="gramps-home-")

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.db.base import DbWriteBase
from gramps.gen.db.txn import DbTxn
from gramps.gen.db.utils import make_database
from gramps.gen.lib import (
    Person,
    Event,
    Place,
    Surname,
    Name,
    Date,
    EventRef,
    EventType,
)
from gramps.gen.types import PersonHandle

# -------------------------------------------------------------------------
#
# Local imports
#
# -------------------------------------------------------------------------
from ..grizard import GrizardCompareRow, CandidateMatcher
from ..gedcom import GedGrizard


def _has_gtk_display() -> bool:
    """
    Return True only if a real Gtk display is available.
    """
    if not os.environ.get("DISPLAY"):
        return False
    if os.environ.get("GDK_BACKEND") == "-":
        return False
    try:
        import gi

        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk

        return bool(Gtk.init_check([])[0])
    except Exception:
        return False


_HAS_GTK_DISPLAY = _has_gtk_display()


# ------------------------------------------------------------
#
# GrizardTest
#
# ------------------------------------------------------------
class GrizardTest(unittest.TestCase):
    """
    Test cases for Grizard core framework, CandidateMatcher, and GedGrizard.
    """

    def setUp(self) -> None:
        """
        Set up the in-memory databases and test entities.
        """
        self.db = make_database("sqlite")
        self.db.load(":memory:")

        # Create basic target person in self.db
        with DbTxn("Add target person", self.db) as trans:
            self.target_person = Person()
            self.target_person.set_gender(Person.MALE)
            name = Name()
            name.first_name = "John"
            s1 = Surname()
            s1.set_surname("Doe")
            name.add_surname(s1)
            self.target_person.set_primary_name(name)
            self.db.add_person(self.target_person, trans)

            # Add Birth Event
            self.birth_event = Event()
            self.birth_event.set_type(EventType.BIRTH)
            d = Date()
            d.set_yr_mon_day(1980, 6, 15)
            self.birth_event.set_date_object(d)

            # Add Birth Place
            self.birth_place = Place()
            self.birth_place.set_title("Springfield")
            self.db.add_place(self.birth_place, trans)
            self.birth_event.set_place_handle(self.birth_place.handle)

            self.db.add_event(self.birth_event, trans)

            eref = EventRef()
            eref.ref = self.birth_event.handle
            self.target_person.set_birth_ref(eref)
            self.db.commit_person(self.target_person, trans)

    def tearDown(self) -> None:
        """
        Close the target database connection.
        """
        self.db.close()

    def test_candidate_matcher(self) -> None:
        """
        Verify that CandidateMatcher successfully matches similar records
        and flags gender mismatches.
        """
        matcher = CandidateMatcher(self.db)

        # Create matching person in memory
        source_person = Person()
        source_person.set_gender(Person.MALE)
        name = Name()
        name.first_name = "John"
        s1 = Surname()
        s1.set_surname("Doe")
        name.add_surname(s1)
        source_person.set_primary_name(name)

        # Exact gender & name match
        score = matcher.score_match(source_person, self.target_person)
        self.assertGreater(score, 1.0)

        # Gender mismatch
        source_person.set_gender(Person.FEMALE)
        score = matcher.score_match(source_person, self.target_person)
        self.assertEqual(score, -1.0)

    def test_ged_grizard_flow(self) -> None:
        """
        Test the end-to-end GedGrizard workflow sequence (connect, load, match, compare, apply).
        """
        # Create a simple valid minimal GEDCOM file
        gedcom_data = """0 HEAD
1 CHAR UTF-8
0 @I1@ INDI
1 NAME John /Doe/
2 GIVN John
2 SURN Doe
1 SEX M
1 BIRT
2 DATE 15 JUN 1980
2 PLAC Springfield
0 TRLR
"""
        with tempfile.NamedTemporaryFile(suffix=".ged", mode="w", delete=False) as f:
            f.write(gedcom_data)
            temp_path = f.name

        try:
            grizard = GedGrizard(self.db)

            # 1. Connect
            self.assertTrue(grizard.run_step("connect", gedcom_path=temp_path))

            # 2. Load
            people = grizard.run_step("load")
            self.assertEqual(len(people), 1)
            source_person = people[0]
            self.assertEqual(source_person.get_primary_name().first_name, "John")

            # 3. Match
            matches = grizard.run_step(
                "match", source_person_handle=source_person.handle
            )
            self.assertEqual(len(matches), 1)
            match = matches[0]
            self.assertEqual(match["handle"], self.target_person.handle)
            self.assertGreater(match["score"], 1.0)

            # 4. Compare
            comparison = grizard.run_step(
                "compare",
                source_person_handle=source_person.handle,
                target_person_handle=self.target_person.handle,
            )
            self.assertGreater(len(comparison), 0)

            given_name_row = [r for r in comparison if r.field_type == "given_name"][0]
            self.assertEqual(given_name_row.status, "match")
            self.assertEqual(given_name_row.source_val, "John")
            self.assertEqual(given_name_row.target_val, "John")

            # 5. Apply (Merge Overwrite given name with target, add birth)
            resolutions = {
                "given_name": "source",
                "surname": "target",
                "gender": "target",
                "birth_event": "source",
            }
            success = grizard.run_step(
                "apply",
                source_person_handle=source_person.handle,
                target_person_handle=self.target_person.handle,
                resolutions=resolutions,
            )
            self.assertTrue(success)

            # Verify target person has successfully updated primary details
            updated_person = self.db.get_person_from_handle(self.target_person.handle)
            self.assertEqual(updated_person.get_primary_name().first_name, "John")

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_format_diff_line(self) -> None:
        """
        Test the GrizardMergeDialog's static method for rendering
        Pango-highlighted differences between values.
        """
        from gramps.gui.grizard.grizardmergedialog import GrizardMergeDialog

        # Exact match (should be plain)
        res = GrizardMergeDialog._format_diff_line(
            "Given Name", "John", "John", show_label=False, is_left=True
        )
        self.assertEqual(res, "John")

        # Differ (one word differs)
        res_diff = GrizardMergeDialog._format_diff_line(
            "Given Name", "John James", "John Paul", show_label=False, is_left=True
        )
        # "James" differs, so it should be bolded, while "John" is matched and just italicized
        self.assertIn("James", res_diff)

        # Show label
        res_label = GrizardMergeDialog._format_diff_line(
            "Given Name", "John", "John", show_label=True, is_left=True
        )
        self.assertEqual(res_label, "Given Name: John")

    def test_ged_grizard_apply_merge_relationships(self) -> None:
        """
        Test merging complex family relationships (spouse, child, parents)
        where the relative is mapped using best_target_person lookup.
        """
        # Create relative (spouse) in self.db
        with DbTxn("Add spouse and child", self.db) as trans:
            self.spouse_person = Person()
            self.spouse_person.set_gender(Person.FEMALE)
            name = Name()
            name.first_name = "Jane"
            s1 = Surname()
            s1.set_surname("Doe")
            name.add_surname(s1)
            self.spouse_person.set_primary_name(name)
            self.db.add_person(self.spouse_person, trans)

        # GEDCOM data with John Doe having a spouse Jane Doe
        gedcom_data = """0 HEAD
1 CHAR UTF-8
0 @I1@ INDI
1 NAME John /Doe/
2 GIVN John
2 SURN Doe
1 SEX M
1 FAMS @F1@
0 @I2@ INDI
1 NAME Jane /Doe/
2 GIVN Jane
2 SURN Doe
1 SEX F
1 FAMS @F1@
0 @F1@ FAM
1 HUSB @I1@
1 WIFE @I2@
0 TRLR
"""
        with tempfile.NamedTemporaryFile(suffix=".ged", mode="w", delete=False) as f:
            f.write(gedcom_data)
            temp_path = f.name

        try:
            grizard = GedGrizard(self.db)
            grizard.run_step("connect", gedcom_path=temp_path)
            people = grizard.run_step("load")
            source_john = [
                p for p in people if p.get_primary_name().first_name == "John"
            ][0]
            source_jane = [
                p for p in people if p.get_primary_name().first_name == "Jane"
            ][0]

            # Merge spouse relation
            resolutions = {
                f"spouse:{source_jane.handle}": "source",
            }
            success = grizard.run_step(
                "apply",
                source_person_handle=source_john.handle,
                target_person_handle=self.target_person.handle,
                resolutions=resolutions,
            )
            self.assertTrue(success)

            # Verify that John now has a family link in self.db, and Jane is the spouse
            updated_john = self.db.get_person_from_handle(self.target_person.handle)
            self.assertTrue(len(updated_john.get_family_handle_list()) > 0)
            fam_handle = updated_john.get_family_handle_list()[0]
            fam = self.db.get_family_from_handle(fam_handle)
            self.assertIsNotNone(fam)
            self.assertEqual(fam.get_father_handle(), updated_john.handle)
            self.assertEqual(fam.get_mother_handle(), self.spouse_person.handle)

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_ged_grizard_resolve_dangling_references(self) -> None:
        """
        Verify that dangling references (Notes, Citations, Sources) are
        recursively copied and linked correctly when merging a person or event.
        """
        # GEDCOM file containing nested note, citation, source structure
        gedcom_data = """0 HEAD
1 CHAR UTF-8
0 @I1@ INDI
1 NAME John /Doe/
2 GIVN John
2 SURN Doe
1 SEX M
1 BIRT
2 DATE 15 JUN 1980
2 SOUR @S1@
3 PAGE 42
0 @S1@ SOUR
1 TITL Famous Book of Doe
1 NOTE @N1@
0 @N1@ NOTE This is a linked note for a source.
0 TRLR
"""
        with tempfile.NamedTemporaryFile(suffix=".ged", mode="w", delete=False) as f:
            f.write(gedcom_data)
            temp_path = f.name

        try:
            grizard = GedGrizard(self.db)
            grizard.run_step("connect", gedcom_path=temp_path)
            people = grizard.run_step("load")
            source_person = people[0]

            resolutions = {
                "given_name": "source",
                "surname": "source",
                "gender": "source",
                "birth_event": "source",
            }
            success = grizard.run_step(
                "apply",
                source_person_handle=source_person.handle,
                target_person_handle=self.target_person.handle,
                resolutions=resolutions,
            )
            self.assertTrue(success)

            # Get the merged birth event from the target database
            updated_person = self.db.get_person_from_handle(self.target_person.handle)
            birth_ref = updated_person.get_birth_ref()
            self.assertIsNotNone(birth_ref)
            birth_event = self.db.get_event_from_handle(birth_ref.ref)
            self.assertIsNotNone(birth_event)

            # Verify that the birth event has a Citation
            citation_handles = birth_event.get_citation_list()
            self.assertTrue(len(citation_handles) > 0)
            citation = self.db.get_citation_from_handle(citation_handles[0])
            self.assertIsNotNone(citation)

            # Verify that the Citation references the correct Source in the target DB
            source_handle = citation.get_reference_handle()
            self.assertIsNotNone(source_handle)
            source = self.db.get_source_from_handle(source_handle)
            self.assertIsNotNone(source)
            self.assertEqual(source.title, "Famous Book of Doe")

            # Verify that the Source references the Note in the target DB
            note_handles = source.get_note_list()
            self.assertTrue(len(note_handles) > 0)
            note = self.db.get_note_from_handle(note_handles[0])
            self.assertIsNotNone(note)
            self.assertIn("linked note", str(note.get_styledtext()))

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    @unittest.skipUnless(
        _HAS_GTK_DISPLAY,
        "needs a real Gtk display (run under xvfb-run); "
        "gramps CI sets GDK_BACKEND=- so Gtk.Dialog cannot init.",
    )
    def test_dialog_find_dangling_references(self) -> None:
        """
        Verify that GrizardMergeDialog._find_dangling_references correctly
        detects and categorizes missing references prior to merge.
        """
        from gramps.gui.grizard.grizardmergedialog import GrizardMergeDialog

        gedcom_data = """0 HEAD
1 CHAR UTF-8
0 @I1@ INDI
1 NAME John /Doe/
2 GIVN John
2 SURN Doe
1 SEX M
1 BIRT
2 DATE 15 JUN 1980
2 SOUR @S1@
3 PAGE 42
0 @S1@ SOUR
1 TITL Famous Book of Doe
1 NOTE @N1@
0 @N1@ NOTE This is a linked note for a source.
0 TRLR
"""
        with tempfile.NamedTemporaryFile(suffix=".ged", mode="w", delete=False) as f:
            f.write(gedcom_data)
            temp_path = f.name

        try:
            grizard = GedGrizard(self.db)
            grizard.run_step("connect", gedcom_path=temp_path)
            people = grizard.run_step("load")
            source_person = people[0]

            # Construct mock/real DbState
            class MockDbState:
                def __init__(self, db):
                    self.db = db

            # GrizardMergeDialog needs a real display (skipped otherwise).
            dbstate = MockDbState(self.db)
            dialog = GrizardMergeDialog(
                dbstate=dbstate,
                grizard=grizard,
                source_handle=source_person.handle,
                target_handle=self.target_person.handle,
            )

            # Select birth event resolution as 'source'
            dialog._resolutions = {
                "birth_event": "source",
            }

            missing = dialog._find_dangling_references()

            # Assert that the dialog correctly finds missing citation, source, and note
            self.assertTrue(len(missing["citation"]) > 0)
            self.assertTrue(len(missing["source"]) > 0)
            self.assertTrue(len(missing["note"]) > 0)

            # If birth_event is not resolved, no missing references should be detected for birth
            dialog._resolutions = {}
            missing_empty = dialog._find_dangling_references()
            self.assertEqual(len(missing_empty["citation"]), 0)
            self.assertEqual(len(missing_empty["source"]), 0)
            self.assertEqual(len(missing_empty["note"]), 0)

            # Cleanup dialog
            dialog.destroy()

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

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

"""Tests for FSToGrampsImporter in gramps/gen/fs/fs_import/importer.py."""

# python3 -m unittest gramps.gen.fs.fs_import.test.importer_test -v

import os
import shutil
import tempfile
import types
import unittest
from unittest.mock import MagicMock, patch

ROOT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..")
)


def _ensure_test_resources():
    """Ensure GRAMPS_RESOURCES points to a directory with required files."""
    resource_path = os.environ.get("GRAMPS_RESOURCES")
    if resource_path and os.path.exists(
        os.path.join(resource_path, "gramps", "authors.xml")
    ):
        return resource_path

    build_share = os.path.join(ROOT_DIR, "build", "share")
    if os.path.exists(os.path.join(build_share, "gramps", "authors.xml")):
        return build_share

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
    return resource_path


os.environ["GRAMPS_RESOURCES"] = _ensure_test_resources()
os.environ["HOME"] = os.environ.get("HOME") or tempfile.mkdtemp(prefix="gramps-home-")

from gramps.gen.fs.fs_import.importer import FSToGrampsImporter
from gramps.gen.fs.fs_import import deserializer as deserialize
from gramps.gen.fs import utils as fs_utilities
from gramps.gen.lib import Person


def _make_ref(resource_id):
    """Return a minimal GEDCOM-X style reference SimpleNamespace."""
    return types.SimpleNamespace(resourceId=resource_id)


def _make_importer_with_mocks(person_map=None, gender_map=None):
    """
    Return a minimal FSToGrampsImporter with db/dbstate mocked out.

    :param person_map: dict mapping fsid -> handle for importable persons.
    :param gender_map: dict mapping fsid -> Person.MALE/FEMALE/UNKNOWN.
    """
    person_map = person_map or {}
    gender_map = gender_map or {}

    importer = FSToGrampsImporter.__new__(FSToGrampsImporter)
    importer.noreimport = False
    importer.asc = 1
    importer.desc = 1
    importer.include_spouses = False
    importer.include_notes = False
    importer.include_sources = False
    importer.verbosity = 0
    importer.added_person = False
    importer.refresh_signals = True
    importer.fs_TreeImp = None
    importer.active_handle = None
    importer.import_cpr = True

    mock_db = MagicMock()
    mock_dbstate = MagicMock()
    mock_dbstate.db = mock_db
    importer.dbstate = mock_dbstate
    importer.txn = MagicMock()

    importer._ensure_imported_person_handle = lambda fsid: person_map.get(
        (fsid or "").strip()
    )
    importer._fs_gender_for_id = lambda fsid: gender_map.get(
        (fsid or "").strip(), Person.UNKNOWN
    )

    return importer, mock_db


# -------------------------------------------------------------------------
#
# TestParentHandlesFromRefs
#
# -------------------------------------------------------------------------
class TestParentHandlesFromRefs(unittest.TestCase):
    """Tests for FSToGrampsImporter._parent_handles_from_refs."""

    def test_both_parents_found_sets_father_and_mother(self):
        """Both resolvable parents populate father_h and mother_h; missing is empty."""
        importer, _ = _make_importer_with_mocks(
            person_map={"P1": "handle-p1", "P2": "handle-p2"},
            gender_map={"P1": Person.MALE, "P2": Person.FEMALE},
        )
        father_h, mother_h, missing = importer._parent_handles_from_refs(
            _make_ref("P1"), _make_ref("P2")
        )
        self.assertEqual(father_h, "handle-p1")
        self.assertEqual(mother_h, "handle-p2")
        self.assertEqual(missing, set())

    def test_parent1_found_parent2_absent_returns_missing(self):
        """When parent2 is not importable, it lands in missing; father_h is set."""
        importer, _ = _make_importer_with_mocks(
            person_map={"P1": "handle-p1"},
            gender_map={"P1": Person.MALE},
        )
        father_h, mother_h, missing = importer._parent_handles_from_refs(
            _make_ref("P1"), _make_ref("P2")
        )
        self.assertEqual(father_h, "handle-p1")
        self.assertIsNone(mother_h)
        self.assertEqual(missing, {"P2"})

    def test_both_parents_absent_fills_missing_set(self):
        """When neither parent can be resolved, missing contains both ids."""
        importer, _ = _make_importer_with_mocks()
        father_h, mother_h, missing = importer._parent_handles_from_refs(
            _make_ref("P1"), _make_ref("P2")
        )
        self.assertIsNone(father_h)
        self.assertIsNone(mother_h)
        self.assertEqual(missing, {"P1", "P2"})

    def test_unknown_gender_falls_back_to_father_slot(self):
        """A person with UNKNOWN gender fills the father slot when it is empty."""
        importer, _ = _make_importer_with_mocks(
            person_map={"P1": "handle-p1"},
            gender_map={"P1": Person.UNKNOWN},
        )
        father_h, mother_h, missing = importer._parent_handles_from_refs(
            _make_ref("P1"), _make_ref("")
        )
        self.assertEqual(father_h, "handle-p1")
        self.assertIsNone(mother_h)


# -------------------------------------------------------------------------
#
# TestAddChild
#
# -------------------------------------------------------------------------
class TestAddChild(unittest.TestCase):
    """Tests for FSToGrampsImporter.add_child (issue 3 fix)."""

    def _make_cpr(self, parent1_id, parent2_id, child_id):
        """Build a minimal child-and-parents relationship SimpleNamespace."""
        return types.SimpleNamespace(
            parent1=_make_ref(parent1_id),
            parent2=_make_ref(parent2_id),
            child=_make_ref(child_id),
        )

    def test_both_parents_resolvable_creates_family(self):
        """When both parents are found, a family is created and the child added."""
        person_map = {
            "P1": "handle-p1",
            "P2": "handle-p2",
            "C1": "handle-c1",
        }
        gender_map = {"P1": Person.MALE, "P2": Person.FEMALE}
        importer, mock_db = _make_importer_with_mocks(person_map, gender_map)

        # No existing family — _find_couple_family returns None
        importer._find_couple_family = MagicMock(return_value=None)

        mock_family = MagicMock()
        mock_family.get_handle.return_value = "fam-handle"
        mock_family.get_child_ref_list.return_value = []
        mock_db.add_family.return_value = None
        mock_db.commit_family.return_value = None

        mock_father = MagicMock()
        mock_mother = MagicMock()
        mock_child = MagicMock()
        mock_db.get_person_from_handle.side_effect = lambda h: {
            "handle-p1": mock_father,
            "handle-p2": mock_mother,
            "handle-c1": mock_child,
        }[h]

        cpr = self._make_cpr("P1", "P2", "C1")

        with patch("gramps.gen.fs.fs_import.importer.Family") as MockFamily:
            MockFamily.return_value = mock_family
            importer.add_child(cpr)

        mock_db.add_family.assert_called_once()
        mock_db.commit_family.assert_called()

    def test_one_parent_missing_still_creates_single_parent_family(self):
        """
        Issue 3 fix: when one parent is resolvable and the other is not in any
        index, a single-parent family is created rather than skipping.
        """
        person_map = {"P1": "handle-p1", "C1": "handle-c1"}
        gender_map = {"P1": Person.MALE}
        importer, mock_db = _make_importer_with_mocks(person_map, gender_map)

        importer._find_couple_family = MagicMock(return_value=None)

        mock_family = MagicMock()
        mock_family.get_handle.return_value = "fam-handle"
        mock_family.get_child_ref_list.return_value = []

        mock_father = MagicMock()
        mock_child = MagicMock()
        mock_db.get_person_from_handle.side_effect = lambda h: {
            "handle-p1": mock_father,
            "handle-c1": mock_child,
        }[h]

        cpr = self._make_cpr("P1", "P2", "C1")

        # P2 not present in FS_INDEX_PEOPLE or deserialize.Person.index
        with patch.dict(fs_utilities.FS_INDEX_PEOPLE, {}, clear=False):
            with patch.dict(deserialize.Person.index, {}, clear=False):
                with patch("gramps.gen.fs.fs_import.importer.Family") as MockFamily:
                    MockFamily.return_value = mock_family
                    importer.add_child(cpr)

        # Family creation was attempted (not skipped)
        mock_db.add_family.assert_called_once()

    def test_both_parents_missing_skips_family_creation(self):
        """When both parents are unresolvable, add_child returns without creating a family."""
        importer, mock_db = _make_importer_with_mocks()

        cpr = self._make_cpr("P1", "P2", "C1")

        with patch.dict(fs_utilities.FS_INDEX_PEOPLE, {}, clear=False):
            with patch.dict(deserialize.Person.index, {}, clear=False):
                importer.add_child(cpr)

        mock_db.add_family.assert_not_called()


if __name__ == "__main__":
    unittest.main()

#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026      Gabriel Rios
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

"""Integration tests for FamilySearch sync storage and schema upgrade."""

# python3 -m unittest discover -s test -p 'test_familysearch_sync_schema.py' -v

from __future__ import annotations

import copy
import os
import shutil
import sys
import tempfile
import types
import unittest

from gramps.gen.db import DbTxn
from gramps.gen.db.dbconst import PERSON_KEY
from gramps.gen.fs.db_familysearch import FSStatusDB
from gramps.gen.lib import FamilySearchSync, Person
from gramps.plugins.db.dbapi.sqlite import SQLite

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _ensure_test_resources():
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

dialog_module = types.ModuleType("gramps.gui.dialog")
setattr(dialog_module, "InfoDialog", object)
sys.modules.setdefault("gramps.gui.dialog", dialog_module)


class _SQLiteIntegrationMixin:
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.dbdir = self.tempdir.name
        self.db = SQLite()
        self.db.load(self.dbdir)

    def tearDown(self):
        try:
            if getattr(self.db, "db_is_open", False):
                self.db.close()
        finally:
            self.tempdir.cleanup()

    def _open_db(self, *, force_schema_upgrade=False):
        db = SQLite()
        db.load(self.dbdir, force_schema_upgrade=force_schema_upgrade)
        return db

    def _create_person(self):
        person = Person()
        with DbTxn("Add test person", self.db) as txn:
            self.db.add_person(person, txn)
        return person


class FamilySearchSyncSQLiteIntegrationTest(_SQLiteIntegrationMixin, unittest.TestCase):
    def test_person_table_has_no_familysearch_sync_column(self):
        self.assertFalse(
            self.db.dbapi.column_exists("person", "familysearch_sync_data")
        )

    def test_db_api_round_trip_and_delete_updates_raw_person_json(self):
        person = self._create_person()
        status = {
            "fsid": "ABCD-EFG",
            "is_root": True,
            "status_ts": 111,
            "confirmed_ts": 222,
            "gramps_modified_ts": 333,
            "fs_modified_ts": 444,
            "essential_conflict": True,
            "conflict": False,
        }

        self.db.set_familysearch_person_status(person.handle, status)

        self.assertEqual(
            self.db.get_familysearch_person_status(person.handle, {}),
            {
                "fsid": "ABCD-EFG",
                "is_root": True,
                "status_ts": 111,
                "confirmed_ts": 222,
                "gramps_modified_ts": 333,
                "fs_modified_ts": 444,
                "essential_conflict": True,
            },
        )
        self.assertEqual(
            self.db.get_raw_person_data(person.handle)["familysearch_sync"],
            {
                "_class": "FamilySearchSync",
                "fsid": "ABCD-EFG",
                "is_root": True,
                "status_ts": 111,
                "confirmed_ts": 222,
                "gramps_modified_ts": 333,
                "fs_modified_ts": 444,
                "essential_conflict": True,
                "conflict": False,
            },
        )

        self.db.delete_familysearch_person_status(person.handle)

        self.assertEqual(self.db.get_familysearch_person_status(person.handle, {}), {})
        self.assertIsNone(
            self.db.get_raw_person_data(person.handle)["familysearch_sync"]
        )

    def test_person_object_round_trip(self):
        person = self._create_person()

        self.db.set_familysearch_person_status(
            person.handle,
            {
                "fsid": "WXYZ-123",
                "is_root": True,
                "status_ts": 1000,
                "confirmed_ts": 2000,
                "gramps_modified_ts": 3000,
                "fs_modified_ts": 4000,
                "essential_conflict": True,
                "conflict": True,
            },
        )

        loaded = self.db.get_person_from_handle(person.handle)

        self.assertEqual(
            loaded.get_familysearch_sync().to_status_dict(),
            {
                "fsid": "WXYZ-123",
                "is_root": True,
                "status_ts": 1000,
                "confirmed_ts": 2000,
                "gramps_modified_ts": 3000,
                "fs_modified_ts": 4000,
                "essential_conflict": True,
                "conflict": True,
            },
        )

    def test_fsstatusdb_integration_round_trip(self):
        person = self._create_person()

        status = FSStatusDB(self.db, person.handle)
        status.fsid = "WXYZ-123"
        status.is_root = True
        status.status_ts = 1000
        status.confirmed_ts = 2000
        status.gramps_modified_ts = 3000
        status.fs_modified_ts = 4000
        status.essential_conflict = True
        status.conflict = True
        status.commit()

        loaded = FSStatusDB(self.db)
        loaded.get(person.handle)

        self.assertEqual(loaded.p_handle, person.handle)
        self.assertEqual(loaded.fsid, "WXYZ-123")
        self.assertTrue(loaded.is_root)
        self.assertEqual(loaded.status_ts, 1000)
        self.assertEqual(loaded.confirmed_ts, 2000)
        self.assertEqual(loaded.gramps_modified_ts, 3000)
        self.assertEqual(loaded.fs_modified_ts, 4000)
        self.assertTrue(loaded.essential_conflict)
        self.assertTrue(loaded.conflict)

        cleared = FSStatusDB(self.db, person.handle)
        cleared.commit()

        self.assertEqual(self.db.get_familysearch_person_status(person.handle, {}), {})
        self.assertIsNone(
            self.db.get_raw_person_data(person.handle)["familysearch_sync"]
        )


class FamilySearchSyncUpgradeIntegrationTest(
    _SQLiteIntegrationMixin, unittest.TestCase
):
    def _set_familysearch_sync_in_person_json(self, handle, sync_data):
        with DbTxn("Set FamilySearch sync in raw JSON", self.db):
            person_data = copy.deepcopy(self.db.get_raw_person_data(handle))
            if sync_data is ...:
                person_data.pop("familysearch_sync", None)
            else:
                person_data["familysearch_sync"] = sync_data
            self.db._commit_raw(person_data, PERSON_KEY)

    def test_new_person_has_null_familysearch_sync(self):
        person = self._create_person()

        self.assertEqual(self.db.get_schema_version(), 21)
        self.assertIsNone(
            self.db.get_raw_person_data(person.handle)["familysearch_sync"]
        )

    def test_v21_person_without_familysearch_sync_loads_without_upgrade(self):
        person = self._create_person()
        self._set_familysearch_sync_in_person_json(person.handle, ...)
        self.db.close(update=False)

        self.db = self._open_db()

        self.assertEqual(self.db.get_schema_version(), 21)
        self.assertNotIn(
            "familysearch_sync", self.db.get_raw_person_data(person.handle)
        )
        loaded = self.db.get_person_from_handle(person.handle)
        self.assertIsNone(loaded.get_familysearch_sync())
        self.assertEqual(self.db.get_familysearch_person_status(person.handle), {})

    def test_v22_beta_db_is_reverted_to_v21(self):
        empty = self._create_person()
        linked = self._create_person()
        empty_sync = FamilySearchSync().serialize()
        linked_sync = FamilySearchSync({"fsid": "ABCD-EFG"}).serialize()
        self._set_familysearch_sync_in_person_json(empty.handle, empty_sync)
        self._set_familysearch_sync_in_person_json(linked.handle, linked_sync)
        self.db.set_schema_version(22)
        self.db.close(update=False)

        self.db = self._open_db()

        self.assertEqual(self.db.get_schema_version(), 21)
        self.assertIsNone(
            self.db.get_raw_person_data(empty.handle)["familysearch_sync"]
        )
        self.assertEqual(
            self.db.get_raw_person_data(linked.handle)["familysearch_sync"],
            linked_sync,
        )

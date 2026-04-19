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

"""Tests for FamilySearch status storage in DBAPI."""

# python3 -m unittest gramps.plugins.db.dbapi.test.familysearch_status_test -v

import copy
import os
import shutil
import tempfile
import unittest

ROOT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..")
)


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


from gramps.gen.db.dbconst import PERSON_KEY, TXNUPD
from gramps.gen.errors import HandleError
from gramps.plugins.db.dbapi.dbapi import DBAPI

DEFAULT_FAMILYSEARCH_SYNC = {
    "_class": "FamilySearchSync",
    "fsid": None,
    "is_root": False,
    "status_ts": None,
    "confirmed_ts": None,
    "gramps_modified_ts": None,
    "fs_modified_ts": None,
    "essential_conflict": False,
    "conflict": False,
}


class FakeTransaction:
    def __init__(self):
        self.batch = False
        self.entries = []

    def add(self, *args):
        self.entries.append(args)


class FakeDbApiStatusStore:
    def __init__(self, people):
        self.people = copy.deepcopy(people)
        self.commits = []

    def get_raw_person_data(self, handle):
        if handle is None:
            raise HandleError("Handle is None")
        if handle not in self.people:
            raise HandleError(f"Handle {handle} not found")
        return self.people[handle]

    def get_person_from_handle(self, handle):
        raise AssertionError("FamilySearch status helpers should use raw person data")

    def _commit_raw(self, data, obj_key):
        self.commits.append((copy.deepcopy(data), obj_key))
        self.people[data["handle"]] = copy.deepcopy(data)

    def _commit_familysearch_person_raw(self, handle, old_data, new_data, transaction):
        DBAPI._commit_familysearch_person_raw(
            self, handle, old_data, new_data, transaction
        )


class FamilySearchStatusDbApiTest(unittest.TestCase):
    def test_get_familysearch_person_status_reads_raw_json(self):
        db = FakeDbApiStatusStore(
            {
                "person-1": {
                    "_class": "Person",
                    "handle": "person-1",
                    "gramps_id": "I0001",
                    "familysearch_sync": {
                        "_class": "FamilySearchSync",
                        "fsid": " FS-123 ",
                        "is_root": True,
                        "status_ts": 10,
                        "confirmed_ts": 0,
                        "gramps_modified_ts": None,
                        "fs_modified_ts": None,
                        "essential_conflict": False,
                        "conflict": True,
                    },
                }
            }
        )

        data = DBAPI.get_familysearch_person_status(db, "person-1", {})

        self.assertEqual(
            data,
            {
                "fsid": "FS-123",
                "is_root": True,
                "status_ts": 10,
                "conflict": True,
            },
        )

    def test_set_familysearch_person_status_writes_raw_json(self):
        db = FakeDbApiStatusStore(
            {
                "person-1": {
                    "_class": "Person",
                    "handle": "person-1",
                    "gramps_id": "I0001",
                    "familysearch_sync": copy.deepcopy(DEFAULT_FAMILYSEARCH_SYNC),
                }
            }
        )
        txn = FakeTransaction()

        DBAPI.set_familysearch_person_status(
            db,
            "person-1",
            {
                "fsid": " FS-123 ",
                "is_root": True,
                "status_ts": 10,
                "confirmed_ts": None,
                "gramps_modified_ts": None,
                "fs_modified_ts": 15,
                "essential_conflict": True,
                "conflict": False,
            },
            txn,
        )

        self.assertEqual(
            db.people["person-1"]["familysearch_sync"],
            {
                "_class": "FamilySearchSync",
                "fsid": "FS-123",
                "is_root": True,
                "status_ts": 10,
                "confirmed_ts": None,
                "gramps_modified_ts": None,
                "fs_modified_ts": 15,
                "essential_conflict": True,
                "conflict": False,
            },
        )
        self.assertEqual(len(db.commits), 1)
        self.assertEqual(db.commits[0][1], PERSON_KEY)
        self.assertEqual(len(txn.entries), 1)
        self.assertEqual(txn.entries[0][0], PERSON_KEY)
        self.assertEqual(txn.entries[0][1], TXNUPD)

    def test_delete_familysearch_person_status_clears_raw_json(self):
        db = FakeDbApiStatusStore(
            {
                "person-1": {
                    "_class": "Person",
                    "handle": "person-1",
                    "gramps_id": "I0001",
                    "familysearch_sync": {
                        "_class": "FamilySearchSync",
                        "fsid": "FS-123",
                        "is_root": True,
                        "status_ts": 10,
                        "confirmed_ts": 20,
                        "gramps_modified_ts": 30,
                        "fs_modified_ts": 40,
                        "essential_conflict": True,
                        "conflict": True,
                    },
                }
            }
        )
        txn = FakeTransaction()

        DBAPI.delete_familysearch_person_status(db, "person-1", txn)

        self.assertEqual(
            db.people["person-1"]["familysearch_sync"],
            DEFAULT_FAMILYSEARCH_SYNC,
        )
        self.assertEqual(len(db.commits), 1)
        self.assertEqual(db.commits[0][1], PERSON_KEY)
        self.assertEqual(len(txn.entries), 1)
        self.assertEqual(txn.entries[0][0], PERSON_KEY)
        self.assertEqual(txn.entries[0][1], TXNUPD)


if __name__ == "__main__":
    unittest.main()

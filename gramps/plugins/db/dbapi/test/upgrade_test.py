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

"""
Tests for database schema upgrades.
"""

# python3 -m unittest gramps.plugins.db.dbapi.test.upgrade_test -v

import copy
import os
import shutil
import sys
import tempfile
import types
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

dialog_module = types.ModuleType("gramps.gui.dialog")
setattr(dialog_module, "InfoDialog", object)
sys.modules.setdefault("gramps.gui.dialog", dialog_module)


from gramps.gen.db.dbconst import PERSON_KEY
from gramps.gen.db.upgrade import gramps_upgrade_22

DEFAULT_FAMILYSEARCH_SYNC_JSON = {
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


class FakeUpgradeDb:
    """
    Minimal database stub for testing schema upgrade functions.
    """

    def __init__(self, people):
        self.people = copy.deepcopy(people)
        self.metadata = {}
        self.total = None
        self.serializer_name = None
        self.commits = []
        self.updates = 0
        self.txn_started = False
        self.txn_committed = False
        self.txn_aborted = False

    def set_serializer(self, name):
        self.serializer_name = name

    def get_number_of_people(self):
        return len(self.people)

    def set_total(self, total):
        self.total = total

    def _txn_begin(self):
        self.txn_started = True

    def get_person_handles(self):
        return list(self.people.keys())

    def get_raw_person_data(self, handle):
        return self.people[handle]

    def get_person_from_handle(self, handle):
        raise AssertionError("gramps_upgrade_22 should use raw person JSON only")

    def _commit_raw(self, data, obj_key):
        self.commits.append((copy.deepcopy(data), obj_key))
        self.people[data["handle"]] = copy.deepcopy(data)

    def update(self):
        self.updates += 1

    def _set_metadata(self, key, value, use_txn=False):
        self.metadata[key] = value

    def _txn_commit(self):
        self.txn_committed = True

    def _txn_abort(self):
        self.txn_aborted = True


class DbUpgradeTest(unittest.TestCase):
    """
    Tests for schema upgrades.
    """

    def test_upgrade_22_updates_raw_person_json_without_person_model(self):
        existing_sync = {
            "_class": "FamilySearchSync",
            "fsid": "FS-123",
            "is_root": True,
            "status_ts": 10,
            "confirmed_ts": 20,
            "gramps_modified_ts": 30,
            "fs_modified_ts": 40,
            "essential_conflict": True,
            "conflict": True,
        }
        db = FakeUpgradeDb(
            {
                "person-1": {
                    "_class": "Person",
                    "handle": "person-1",
                    "gramps_id": "I0001",
                },
                "person-2": {
                    "_class": "Person",
                    "handle": "person-2",
                    "gramps_id": "I0002",
                    "familysearch_sync": existing_sync,
                },
            }
        )

        gramps_upgrade_22(db)

        self.assertEqual(db.serializer_name, "json")
        self.assertEqual(db.total, 2)
        self.assertTrue(db.txn_started)
        self.assertTrue(db.txn_committed)
        self.assertFalse(db.txn_aborted)
        self.assertEqual(db.updates, 2)
        self.assertEqual(db.metadata["version"], 22)
        self.assertEqual(len(db.commits), 1)
        self.assertEqual(db.commits[0][1], PERSON_KEY)
        self.assertEqual(
            db.people["person-1"]["familysearch_sync"],
            DEFAULT_FAMILYSEARCH_SYNC_JSON,
        )
        self.assertEqual(db.people["person-2"]["familysearch_sync"], existing_sync)


if __name__ == "__main__":
    unittest.main()

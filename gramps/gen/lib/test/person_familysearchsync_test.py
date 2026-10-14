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

"""Tests for Person FamilySearch sync JSON handling."""

import os
import shutil
import tempfile
import unittest
from gramps.gen.lib import FamilySearchSync, Person
from gramps.gen.lib.json_utils import (
    data_to_object,
    object_to_data,
    object_to_dict,
    remove_object,
)

ROOT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
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


class PersonFamilySearchSyncJsonTest(unittest.TestCase):
    def test_new_person_has_no_familysearch_sync(self):
        person = Person()

        self.assertIsNone(person.get_familysearch_sync())
        self.assertFalse(person.has_familysearch_sync_data())
        self.assertIsNone(object_to_dict(person)["familysearch_sync"])
        self.assertIsNone(person.serialize()[21])

    def test_person_restores_json_without_familysearch_sync(self):
        person_data = remove_object(object_to_data(Person()))
        del person_data["familysearch_sync"]

        person = data_to_object(person_data)

        self.assertIsInstance(person, Person)
        self.assertIsNone(person.get_familysearch_sync())
        self.assertIsNone(object_to_dict(person)["familysearch_sync"])

    def test_person_restores_familysearch_sync_from_json_state(self):
        person = Person()
        person.set_familysearch_sync({"fsid": "FS-123", "is_root": True})
        person_data = remove_object(object_to_data(person))

        person = data_to_object(person_data)
        sync = person.get_familysearch_sync()

        self.assertIsInstance(sync, FamilySearchSync)
        self.assertEqual(sync.to_status_dict(), {"fsid": "FS-123", "is_root": True})
        self.assertTrue(person.has_familysearch_sync_data())

    def test_person_copy_and_clear_familysearch_sync(self):
        person = Person()
        person.set_familysearch_sync({"fsid": "FS-123"})

        copied = Person(person.serialize())
        person.clear_familysearch_sync()

        self.assertIsNone(person.get_familysearch_sync())
        self.assertEqual(copied.get_familysearch_sync().fsid, "FS-123")

    def test_person_tuple_round_trip(self):
        person = Person()
        self.assertIsNone(Person().unserialize(person.serialize()).familysearch_sync)

        person.set_familysearch_sync({"fsid": "FS-123"})
        restored = Person().unserialize(person.serialize())
        self.assertEqual(restored.get_familysearch_sync().fsid, "FS-123")


if __name__ == "__main__":
    unittest.main()

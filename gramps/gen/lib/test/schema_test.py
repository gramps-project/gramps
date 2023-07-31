#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2017      Nick Hall
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
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

""" Unittest for JSON schema """

import os
import unittest
import json
import jsonschema

from .. import (
    Person,
    Family,
    Event,
    Place,
    Repository,
    Source,
    Citation,
    Media,
    Note,
    Tag,
)
from ..serialize import to_json
from ...db.utils import import_as_dict
from ...const import DATA_DIR
from ...user import User

TEST_DIR = os.path.abspath(os.path.join(DATA_DIR, "tests"))
EXAMPLE = os.path.join(TEST_DIR, "example.gramps")


class BaseTest(unittest.TestCase):
    def _schema_test(self, obj):
        instance = json.loads(to_json(obj))
        try:
            jsonschema.validate(instance, self.schema)
        except jsonschema.exceptions.ValidationError:
            self.fail("JSON Schema validation error")


class PersonTest(BaseTest):
    @classmethod
    def setUpClass(cls):
        cls.schema = Person.get_schema()


class FamilyTest(BaseTest):
    @classmethod
    def setUpClass(cls):
        cls.schema = Family.get_schema()


class EventTest(BaseTest):
    @classmethod
    def setUpClass(cls):
        cls.schema = Event.get_schema()


class PlaceTest(BaseTest):
    @classmethod
    def setUpClass(cls):
        cls.schema = Place.get_schema()


class RepositoryTest(BaseTest):
    @classmethod
    def setUpClass(cls):
        cls.schema = Repository.get_schema()


class SourceTest(BaseTest):
    @classmethod
    def setUpClass(cls):
        cls.schema = Source.get_schema()


class CitationTest(BaseTest):
    @classmethod
    def setUpClass(cls):
        cls.schema = Citation.get_schema()


class MediaTest(BaseTest):
    @classmethod
    def setUpClass(cls):
        cls.schema = Media.get_schema()


class NoteTest(BaseTest):
    @classmethod
    def setUpClass(cls):
        cls.schema = Note.get_schema()


class TagTest(BaseTest):
    @classmethod
    def setUpClass(cls):
        cls.schema = Tag.get_schema()


def generate_case(obj, test_class):
    """
    Dynamically generate tests.
    """

    def test(self):
        self._schema_test(obj)

    name = "test_schema_%s_%s" % (obj.__class__.__name__, obj.handle)
    setattr(test_class, name, test)


db = import_as_dict(EXAMPLE, User())
for obj in db.iter_people():
    generate_case(obj, PersonTest)
for obj in db.iter_families():
    generate_case(obj, FamilyTest)
for obj in db.iter_events():
    generate_case(obj, EventTest)
for obj in db.iter_places():
    generate_case(obj, PlaceTest)
for obj in db.iter_repositories():
    generate_case(obj, RepositoryTest)
for obj in db.iter_sources():
    generate_case(obj, SourceTest)
for obj in db.iter_citations():
    generate_case(obj, CitationTest)
for obj in db.iter_media():
    generate_case(obj, MediaTest)
for obj in db.iter_notes():
    generate_case(obj, NoteTest)
for obj in db.iter_tags():
    generate_case(obj, TagTest)

if __name__ == "__main__":
    unittest.main()

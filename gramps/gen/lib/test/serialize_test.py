#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2013 Doug Blank <doug.blank@gmail.com>
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

""" Unittest for to_json, from_json """

import unittest
import os

from .. import (
    Person,
    Family,
    Event,
    Source,
    Place,
    Citation,
    Repository,
    Media,
    Note,
    Tag,
)
from ..serialize import to_json, from_json
from ...db.utils import import_as_dict
from ...const import DATA_DIR
from ...user import User

TEST_DIR = os.path.abspath(os.path.join(DATA_DIR, "tests"))
EXAMPLE = os.path.join(TEST_DIR, "example.gramps")


class BaseCheck:
    def test_from_json(self):
        data = to_json(self.object)
        obj = from_json(data)
        self.assertEqual(self.object.serialize(), obj.serialize())

    def test_from_empty_json(self):
        data = '{"_class": "%s"}' % self.cls.__name__
        obj = from_json(data)
        self.assertEqual(self.object.serialize(), obj.serialize())


class PersonCheck(unittest.TestCase, BaseCheck):
    def setUp(self):
        self.cls = Person
        self.object = self.cls()


class FamilyCheck(unittest.TestCase, BaseCheck):
    def setUp(self):
        self.cls = Family
        self.object = self.cls()


class EventCheck(unittest.TestCase, BaseCheck):
    def setUp(self):
        self.cls = Event
        self.object = self.cls()


class SourceCheck(unittest.TestCase, BaseCheck):
    def setUp(self):
        self.cls = Source
        self.object = self.cls()


class PlaceCheck(unittest.TestCase, BaseCheck):
    def setUp(self):
        self.cls = Place
        self.object = self.cls()


class CitationCheck(unittest.TestCase, BaseCheck):
    def setUp(self):
        self.cls = Citation
        self.object = self.cls()


class RepositoryCheck(unittest.TestCase, BaseCheck):
    def setUp(self):
        self.cls = Repository
        self.object = self.cls()


class MediaCheck(unittest.TestCase, BaseCheck):
    def setUp(self):
        self.cls = Media
        self.object = self.cls()


class NoteCheck(unittest.TestCase, BaseCheck):
    def setUp(self):
        self.cls = Note
        self.object = self.cls()


class TagCheck(unittest.TestCase, BaseCheck):
    def setUp(self):
        self.cls = Tag
        self.object = self.cls()


class DatabaseCheck(unittest.TestCase):
    maxDiff = None


def generate_case(obj):
    """
    Dynamically generate tests and attach to DatabaseCheck.
    """
    data = to_json(obj)
    obj2 = from_json(data)

    def test(self):
        self.assertEqual(obj.serialize(), obj2.serialize())

    name = "test_serialize_%s_%s" % (obj.__class__.__name__, obj.handle)
    setattr(DatabaseCheck, name, test)
    ####
    # def test2(self):
    #    self.assertEqual(obj.serialize(), from_struct(struct).serialize())
    # name = "test_create_%s_%s" % (obj.__class__.__name__, obj.handle)
    # setattr(DatabaseCheck, name, test2)


db = import_as_dict(EXAMPLE, User())
for obj_class in (
    "Person",
    "Family",
    "Event",
    "Place",
    "Repository",
    "Source",
    "Citation",
    "Media",
    "Note",
):
    for handle in db.method("get_%s_handles", obj_class)():
        obj = db.method("get_%s_from_handle", obj_class)(handle)
        generate_case(obj)

if __name__ == "__main__":
    unittest.main()

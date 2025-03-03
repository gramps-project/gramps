#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2016 Tom Samstag
# Copyright (C) 2025 Doug Blank
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

"""
Unittest that tests person-specific filter rules
"""
import unittest
import os

from ...db.utils import import_as_dict
from ...const import DATA_DIR
from ...user import User
from ...lib.person import Person
from ...lib.json_utils import remove_object

from ...proxy import PrivateProxyDb, LivingProxyDb

TEST_DIR = os.path.abspath(os.path.join(DATA_DIR, "tests"))
EXAMPLE = os.path.join(TEST_DIR, "example.gramps")


class PrivateProxyTest(unittest.TestCase):
    """
    Person rule tests.
    """

    @classmethod
    def setUpClass(cls):
        """
        Import example database.
        """
        cls.db = PrivateProxyDb(import_as_dict(EXAMPLE, User()))

    def assertDataEquals(self, data1, data2):
        self.assertIsInstance(data1, dict)
        self.assertIsInstance(data2, dict)
        self.assertEqual(
            remove_object(data1),
            remove_object(data2),
        )

    def test_person_count(self):
        count = self.db.get_number_of_people()
        # One private person:
        self.assertEqual(count, 2127)
        # No proxy:
        count = self.db.basedb.get_number_of_people()
        self.assertEqual(count, 2128)

    def test_private_person_data(self):
        # A private person:
        handle = "0GDKQC54XKSWZKEBWW"
        data = self.db.get_raw_person_data(handle)
        self.assertIs(data, None)
        # But they are visible without proxy:
        data = self.db.basedb.get_raw_person_data(handle)
        self.assertIsNot(data, None)

    def test_not_private_person_data(self):
        # A non-private person:
        handle = "0FWJQCLYEP736P3YZK"
        data = self.db.get_raw_person_data(handle)
        self.assertIsNot(data, None)
        self.assertIsInstance(data, dict)
        self.assertEqual(data.handle, handle)
        # Should be same:
        data_orig = self.db.basedb.get_raw_person_data(handle)
        self.assertDataEquals(data, data_orig)

    def test_private_person(self):
        # A private person:
        handle = "0GDKQC54XKSWZKEBWW"
        person = self.db.get_person_from_handle(handle)
        self.assertIs(person, None)
        # But they are visible without proxy:
        person = self.db.basedb.get_person_from_handle(handle)
        self.assertIsNot(person, None)

    def test_not_private_person(self):
        # A non-private person:
        handle = "0FWJQCLYEP736P3YZK"
        person = self.db.get_person_from_handle(handle)
        self.assertIsNot(person, None)
        self.assertIsInstance(person, Person)
        person_orig = self.db.basedb.get_person_from_handle(handle)
        # Same person:
        self.assertEqual(person.gramps_id, person_orig.gramps_id)

    def test_person_with_private_data(self):
        # A person with private data:
        handle = "GNUJQCL9MD64AM56OH"
        person = self.db.get_person_from_handle(handle)
        self.assertTrue(len(person.attribute_list) == 2)
        # Unfiltered person has three attributes
        person = self.db.basedb.get_person_from_handle(handle)
        self.assertTrue(len(person.attribute_list) == 3)


class LivingProxyTest(unittest.TestCase):
    """
    Person rule tests.
    """

    @classmethod
    def setUpClass(cls):
        """
        Import example database.
        """
        cls.db = LivingProxyDb(
            import_as_dict(EXAMPLE, User()),
            mode=LivingProxyDb.MODE_EXCLUDE_ALL,
            current_year=2006,
            years_after_death=10,
        )

    def test_person_count(self):
        count = self.db.get_number_of_people()
        self.assertEqual(count, 1245)

    def test_live_person_data(self):
        handle = "004KQCGYT27EEPQHK"
        data = self.db.get_raw_person_data(handle)
        self.assertIsInstance(data, dict)
        self.assertEqual(data.primary_name.first_name, "Martha")

    def test_dead_person_data(self):
        handle = "66TJQC6CC7ZWL9YZ64"
        data = self.db.get_raw_person_data(handle)
        self.assertIs(data, None)

    def test_live_person(self):
        handle = "004KQCGYT27EEPQHK"
        person = self.db.get_person_from_handle(handle)
        self.assertIsInstance(person, Person)

    def test_dead_person(self):
        handle = "66TJQC6CC7ZWL9YZ64"
        person = self.db.get_person_from_handle(handle)
        self.assertIs(person, None)


class LivingPrivateProxyTest(unittest.TestCase):
    """
    Person rule tests.
    """

    @classmethod
    def setUpClass(cls):
        """
        Import example database.
        """
        cls.db = LivingProxyDb(
            PrivateProxyDb(import_as_dict(EXAMPLE, User())),
            mode=LivingProxyDb.MODE_EXCLUDE_ALL,
            current_year=2006,
            years_after_death=10,
        )

    def test_person_count(self):
        count = self.db.get_number_of_people()
        self.assertEqual(count, 1244)

    def test_private_person(self):
        # A private person:
        handle = "0GDKQC54XKSWZKEBWW"
        person = self.db.get_person_from_handle(handle)
        self.assertIs(person, None)
        # But they are visible without proxy:
        person = self.db.basedb.get_person_from_handle(handle)
        self.assertIsNot(person, None)

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

from gramps.gen.db.utils import import_as_dict
from gramps.gen.const import DATA_DIR
from gramps.gen.user import User

from gramps.gen.proxy import PrivateProxyDb, LivingProxyDb

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

    def test_person_count(self):
        count = self.db.get_number_of_people()
        self.assertEqual(count, 2127)

    def test_person_raw(self):
        data = self.db._get_raw_person_from_id_data("I0552")
        self.assertIsInstance(data, dict)


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
        self.assertEqual(count, 1316)

    def test_person_raw(self):
        data = self.db._get_raw_person_from_id_data("I0552")
        self.assertIsInstance(data, dict)


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
        self.assertEqual(count, 1315)

    def test_person_raw(self):
        data = self.db._get_raw_person_from_id_data("I0552")
        self.assertIsInstance(data, dict)

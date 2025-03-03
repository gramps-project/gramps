#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2025      Doug Blank
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

"""Unittest for DataDict"""

# See also tests in ./serialize_test.py

import unittest

from gramps.gen.lib.json_utils import DataDict, DataList, object_to_data, data_to_object
from gramps.gen.lib import (
    Person,
    Family,
)


class DataDictTest(unittest.TestCase):
    def test_person(self):
        p = Person()
        d = DataDict(p)
        # Get the object from the dict:
        self.assertEqual(id(p), id(data_to_object(d)))

    def test_person_to_data(self):
        p = Person()
        d = object_to_data(p)
        self.assertFalse(hasattr(d, "_object"))

    def test_family(self):
        p = Family()
        d = DataDict(p)
        # Get the object from the dict:
        self.assertEqual(id(p), id(data_to_object(d)))

    def test_family_to_data(self):
        p = Family()
        d = object_to_data(p)
        self.assertFalse(hasattr(d, "_object"))


class DataListTest(unittest.TestCase):
    def test_empty_1(self):
        dl = DataList()
        self.assertIsInstance(dl, DataList)
        self.assertEqual(len(dl), 0)

    def test_empty_2(self):
        dl = DataList([])
        self.assertIsInstance(dl, DataList)
        self.assertEqual(len(dl), 0)

    def test_value_1(self):
        dl = DataList([42])
        self.assertIsInstance(dl, DataList)
        self.assertIsInstance(dl[0], int)
        self.assertEqual(dl[0], 42)

    def test_value_exception(self):
        with self.assertRaises(TypeError):
            dl = DataList(42)

    def test_access_exception(self):
        dl = DataList([1, 2, 3])
        self.assertIsInstance(dl, DataList)
        self.assertEqual(dl[0], 1)
        self.assertEqual(dl[1], 2)
        self.assertEqual(dl[2], 3)
        with self.assertRaises(IndexError):
            dl[3]

    def test_nested(self):
        dl = DataList([[42]])
        self.assertIsInstance(dl, DataList)
        self.assertIsInstance(dl[0], DataList)
        self.assertEqual(dl[0][0], 42)

    def test_data(self):
        p = Person()
        p_data = object_to_data(p)
        dl = DataList([p_data])
        self.assertIsInstance(dl, DataList)
        self.assertIsInstance(dl[0], DataDict)
        self.assertEqual(dl[0], p_data)
        self.assertEqual(dl[0].gender, 2)

    def test_append_list(self):
        dl = DataList([])
        dl.append([])
        self.assertIsInstance(dl, DataList)
        self.assertEqual(dl[0], [])
        self.assertIsInstance(dl[0], DataList)

    def test_append_value(self):
        dl = DataList([])
        dl.append(42)
        self.assertIsInstance(dl, DataList)
        self.assertEqual(dl[0], 42)
        self.assertIsInstance(dl[0], int)

    def test_combined_list(self):
        dl = DataList([])
        self.assertIsInstance(dl + [], DataList)

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

""" Unittest for DataDict """

# See also tests in ./serialize_test.py

import unittest

from gramps.gen.lib.serialize import DataDict, to_dict, from_dict
from gramps.gen.lib import (
    Person,
    Family,
)


class DataDictTest(unittest.TestCase):
    def test_person(self):
        p = Person()
        d = DataDict(p)
        # Get the object from the dict:
        assert id(p) == id(from_dict(d))

    def test_person_to_dict(self):
        p = Person()
        d = to_dict(p)
        assert not hasattr(d, "_object")

    def test_family(self):
        p = Family()
        d = DataDict(p)
        # Get the object from the dict:
        assert id(p) == id(from_dict(d))

    def test_family_to_dict(self):
        p = Family()
        d = to_dict(p)
        assert not hasattr(d, "_object")

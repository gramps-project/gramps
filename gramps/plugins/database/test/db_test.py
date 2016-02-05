#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2016  Gramps Development Team
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

import unittest
import os

from gramps.test.test_util import Gramps
from gramps.gen.db import open_database
from gramps.gen.lib import *

ddir = os.path.dirname(__file__)
example = os.path.join(ddir, "..", "..", "..", "..",
                       "example", "gramps", "data.gramps")

class BSDDB(object):
    NAME = "Example BSDDB Test"
    backend = "bsddb"

    def __init__(self):
        self.gramps = Gramps()
        self.call("--config=behavior.database-backend:" + self.backend,
                  "-C", self.NAME, "--import", example)
        self.db = open_database(self.NAME, force_unlock=True)

    def call(self, *args, stdin=None):
        return self.gramps.run(*args, stdin=stdin)

    def close(self):
        self.db.close()
        self.call("-r", self.NAME)

class DBAPI(BSDDB):
    NAME = "Example DBAPI Test"
    backend = "dbapi"

class BSDDBTest(unittest.TestCase):
    dbwrap = BSDDB()

    def setUp(self):
        self.db = self.dbwrap.db

    @classmethod
    def tearDownClass(cls):
        cls.dbwrap.close()

    def test_open(self):
        self.assertTrue(self.db is not None)

    def test_default_person(self):
        person = self.db.get_default_person()
        self.assertTrue(person is not None)

    def test_get_field_1(self):
        person = self.db.get_default_person()
        gramps_id = person.get_field("gramps_id")
        self.assertTrue(gramps_id == "I0037", gramps_id)

    def test_get_field_2(self):
        person = self.db.get_default_person()
        result = person.get_field("event_ref_list")
        self.assertTrue(len(result) == 4, result)
        self.assertTrue(all([isinstance(r, EventRef) for r in result]), result)

    def test_select_1(self):
        result = self.db._select("Person", ["gramps_id"])
        self.assertTrue(len(result) == 60, len(result))

    def test_select_2(self):
        result = self.db._select("Person", ["gramps_id"],
                                where=("gramps_id", "LIKE", "I000%"))
        self.assertTrue(len(result) == 10, len(result))

    def test_select_3(self):
        result = self.db._select("Family", ["mother_handle.gramps_id"],
                                where=("mother_handle.gramps_id", "LIKE", "I003%"))
        self.assertTrue(len(result) == 6, result)

    def test_select_4(self):
        result = self.db._select("Family", ["mother_handle.event_ref_list.ref.gramps_id"])
        self.assertTrue(len(result) == 23, len(result))

    def test_select_4(self):
        result = self.db._select("Family", ["mother_handle.event_ref_list.ref.gramps_id"],
                                where=("mother_handle.event_ref_list.ref.gramps_id", "=", 'E0156'))
        self.assertTrue(len(result) == 1, len(result))

    def test_select_5(self):
        result = self.db._select("Family", ["mother_handle.event_ref_list.ref.self.gramps_id"])
        self.assertTrue(len(result) == 23, len(result))

    def test_select_6(self):
        result = self.db._select("Family", ["mother_handle.event_ref_list.0"])
        self.assertTrue(all([isinstance(r["mother_handle.event_ref_list.0"], (EventRef, type(None))) for r in result]),
                        [r["mother_handle.event_ref_list.0"] for r in result])

    def test_select_7(self):
        result = self.db._select("Family", ["mother_handle.event_ref_list.0"],
                                where=("mother_handle.event_ref_list.0", "!=", None))
        self.assertTrue(len(result) == 21, len(result))


class DBAPITest(BSDDBTest):
    dbwrap = DBAPI()

if __name__ == "__main__":
    unittest.main()

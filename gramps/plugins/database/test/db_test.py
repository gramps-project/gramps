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
        result = list(self.db._select("Person", ["gramps_id"]))
        self.assertTrue(len(result) == 60, len(result))

    def test_select_2(self):
        result = list(self.db._select("Person", ["gramps_id"],
                                      where=("gramps_id", "LIKE", "I000%")))
        self.assertTrue(len(result) == 10, len(result))

    def test_select_3(self):
        result = list(self.db._select("Family", ["mother_handle.gramps_id"],
                        where=("mother_handle.gramps_id", "LIKE", "I003%")))
        self.assertTrue(len(result) == 6, result)

    def test_select_4(self):
        result = list(self.db._select("Family",
              ["mother_handle.event_ref_list.ref.gramps_id"]))
        self.assertTrue(len(result) == 23, len(result))

    def test_select_5(self):
        result = list(self.db._select("Family",
              ["mother_handle.event_ref_list.ref.self.gramps_id"]))
        self.assertTrue(len(result) == 23, len(result))

    def test_select_6(self):
        result = list(self.db._select("Family", ["mother_handle.event_ref_list.0"]))
        self.assertTrue(all([isinstance(r["mother_handle.event_ref_list.0"],
                                        (EventRef, type(None))) for r in result]),
                        [r["mother_handle.event_ref_list.0"] for r in result])

    def test_select_7(self):
        result = list(self.db._select("Family", ["mother_handle.event_ref_list.0"],
                                where=("mother_handle.event_ref_list.0", "!=", None)))
        self.assertTrue(len(result) == 21, len(result))

    def test_select_8(self):
        result = list(self.db._select("Family", ["mother_handle.event_ref_list.ref.gramps_id"],
                                where=("mother_handle.event_ref_list.ref.gramps_id", "=", 'E0156')))
        self.assertTrue(len(result) == 1, len(result))

    def test_queryset_1(self):
        result = list(self.db.Person.select())
        self.assertTrue(len(result) == 60, len(result))

    def test_queryset_2(self):
        result = list(self.db.Person.where(lambda person: LIKE(person.gramps_id, "I000%")).select())
        self.assertTrue(len(result) == 10, len(result))

    def test_queryset_3(self):
        result = list(self.db.Family
                      .where(lambda family: LIKE(family.mother_handle.gramps_id, "I003%"))
                      .select())
        self.assertTrue(len(result) == 6, result)

    def test_queryset_4a(self):
        result = list(self.db.Family.select())
        self.assertTrue(len(result) == 23, len(result))

    def test_queryset_4b(self):
        result = list(self.db.Family
                      .where(lambda family: family.mother_handle.event_ref_list.ref.gramps_id == 'E0156')
                      .select())
        self.assertTrue(len(result) == 1, len(result))

    def test_queryset_5(self):
        result = list(self.db.Family
                      .select("mother_handle.event_ref_list.ref.self.gramps_id"))
        self.assertTrue(len(result) == 23, len(result))

    def test_queryset_6(self):
        result = list(self.db.Family.select("mother_handle.event_ref_list.0"))
        self.assertTrue(all([isinstance(r["mother_handle.event_ref_list.0"],
                                        (EventRef, type(None))) for r in result]),
                        [r["mother_handle.event_ref_list.0"] for r in result])

    def test_queryset_7(self):
        result = list(self.db.Family
                      .where(lambda family: family.mother_handle.event_ref_list[0] != None)
                      .select())
        self.assertTrue(len(result) == 21, len(result))

    def test_order_1(self):
        result = list(self.db.Person.order("gramps_id").select())
        self.assertTrue(len(result) == 60, len(result))

    def test_order_2(self):
        result = list(self.db.Person.order("-gramps_id").select())
        self.assertTrue(len(result) == 60, len(result))

    def test_proxy_1(self):
        result = list(self.db.Person.proxy("living", False).select())
        self.assertTrue(len(result) == 31, len(result))

    def test_proxy_2(self):
        result = list(self.db.Person.proxy("living", True).select())
        self.assertTrue(len(result) == 60, len(result))

    def test_proxy_3(self):
        result = len(list(self.db.Person
                          .proxy("private")
                          .order("-gramps_id")
                          .select("gramps_id")))
        self.assertTrue(result == 59, result)

    def test_map_1(self):
        result = sum(list(self.db.Person.map(lambda p: 1).select()))
        self.assertTrue(result == 60, result)

    def test_tag_1(self):
        self.db.Person.where(lambda person: person.gramps_id == "I0001").tag("Test")
        result = self.db.Person.where(lambda person: person.tag_list.name == "Test").count()
        self.assertTrue(result == 1, result)

    def test_filter_1(self):
        from gramps.gen.filters.rules.person import (IsDescendantOf,
                                                     IsAncestorOf)
        from gramps.gen.filters import GenericFilter
        filter = GenericFilter()
        filter.set_logical_op("or")
        filter.add_rule(IsDescendantOf([self.db.get_default_person().gramps_id,
                                        True]))
        filter.add_rule(IsAncestorOf([self.db.get_default_person().gramps_id,
                                      True]))
        result = self.db.Person.filter(filter).count()
        self.assertTrue(result == 15, result)
        filter.where = lambda person: person.private == True
        result = self.db.Person.filter(filter).count()
        self.assertTrue(result == 1, result)
        filter.where = lambda person: person.private != True
        result = self.db.Person.filter(filter).count()
        self.assertTrue(result == 14, result)

    def test_filter_2(self):
        result = self.db.Person.filter(lambda p: p.private).count()
        self.assertTrue(result == 1, result)

    def test_filter_3(self):
        result = self.db.Person.filter(lambda p: not p.private).count()
        self.assertTrue(result == 59, result)

    def test_limit_1(self):
        result = self.db.Person.limit(count=50).count()
        self.assertTrue(result == 50, result)

    def test_limit_2(self):
        result = self.db.Person.limit(start=50, count=50).count()
        self.assertTrue(result == 10, result)

    def test_ordering_1(self):
        worked = None
        try:
            result = list(self.db.Person
                          .filter(lambda p: p.private)
                          .order("private")
                          .select())
            worked = True
        except:
            worked = False
        self.assertTrue(not worked, "should have failed")

    def test_ordering_2(self):
        worked = None
        try:
            result = list(self.db.Person.order("private")
                          .filter(lambda p: p.private)
                          .select())
            worked = True
        except:
            worked = False
        self.assertTrue(worked, "should have worked")

class DBAPITest(BSDDBTest):
    dbwrap = DBAPI()

if __name__ == "__main__":
    unittest.main()

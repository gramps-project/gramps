#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Doug Blank
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
Tests for reading the raw data of many objects at once.
"""

# -------------------------------------------------------------------------
#
# Standard python modules
#
# -------------------------------------------------------------------------
import unittest
from unittest.mock import patch

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.db import DbTxn
from gramps.gen.db.utils import make_database
from gramps.gen.lib import ChildRef, Family, Person
from gramps.gen.lib.json_utils import data_to_object, object_to_dict
from gramps.gen.proxy import LivingProxyDb, PrivateProxyDb
from gramps.plugins.db.dbapi import dbapi


def _plain(found):
    """
    Return raw data by handle as plain values, without the objects that
    proxies keep in it.
    """
    return {handle: object_to_dict(data_to_object(data)) for handle, data in found}


class RawDataManyTest(unittest.TestCase):
    """
    get_raw_person_data_many and get_raw_family_data_many return what
    reading each handle on its own returns.
    """

    @classmethod
    def setUpClass(cls):
        cls.db = make_database("sqlite")
        cls.db.load(":memory:")
        cls.people = [f"P{index}" for index in range(10)]
        cls.families = [f"F{index}" for index in range(3)]
        with DbTxn("Add test objects", cls.db) as trans:
            for index, handle in enumerate(cls.people):
                person = Person()
                person.set_handle(handle)
                person.set_gramps_id(f"I{index}")
                person.set_gender(Person.MALE if index % 2 else Person.FEMALE)
                # every third person is private
                person.set_privacy(index % 3 == 0)
                cls.db.add_person(person, trans)
            for index, handle in enumerate(cls.families):
                family = Family()
                family.set_handle(handle)
                family.set_gramps_id(f"F{index}")
                family.set_father_handle(cls.people[3 * index + 1])
                family.set_mother_handle(cls.people[3 * index + 2])
                ref = ChildRef()
                ref.set_reference_handle(cls.people[3 * index + 3])
                # a private reference to a visible child
                ref.set_privacy(index == 1)
                family.add_child_ref(ref)
                cls.db.add_family(family, trans)

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def _check(self, db, people, families):
        """
        Reading many at once gives the same as reading one by one.
        """
        self.assertEqual(
            _plain(db.get_raw_person_data_many(people)),
            _plain(
                (handle, db.get_raw_person_data(handle))
                for handle in dict.fromkeys(people)
                if db.get_raw_person_data(handle) is not None
            ),
        )
        self.assertEqual(
            _plain(db.get_raw_family_data_many(families)),
            _plain(
                (handle, db.get_raw_family_data(handle))
                for handle in dict.fromkeys(families)
                if db.get_raw_family_data(handle) is not None
            ),
        )

    def test_same_as_one_by_one(self):
        """
        Missing handles are left out, and repeated ones read once.
        """
        people = self.people + ["missing", self.people[0]]
        families = self.families + ["missing", self.families[0]]
        self._check(self.db, people, families)
        self.assertEqual(
            sorted(dict(self.db.get_raw_person_data_many(people))), sorted(self.people)
        )
        self.assertEqual(list(self.db.get_raw_person_data_many([])), [])
        # each found handle is yielded once
        self.assertEqual(
            len(list(self.db.get_raw_person_data_many(people))), len(self.people)
        )
        self.assertEqual(
            len(list(PrivateProxyDb(self.db).get_raw_person_data_many(people))),
            len(dict(PrivateProxyDb(self.db).get_raw_person_data_many(people))),
        )

    def test_one_query(self):
        """
        DBAPI reads a batch in one query, and a longer list in several.
        """
        with patch.object(
            self.db.dbapi, "execute", wraps=self.db.dbapi.execute
        ) as execute:
            list(self.db.get_raw_person_data_many(self.people))
            self.assertEqual(execute.call_count, 1)
        with patch.object(dbapi, "RAW_DATA_BATCH_SIZE", 3):
            with patch.object(
                self.db.dbapi, "execute", wraps=self.db.dbapi.execute
            ) as execute:
                found = dict(self.db.get_raw_person_data_many(self.people))
                self.assertEqual(execute.call_count, 4)
        self.assertEqual(sorted(found), sorted(self.people))

    def test_subclass_reading_one_object(self):
        """
        A backend that changes how one object is read is used for many.
        """

        class OnlyMen(type(self.db)):
            def _get_raw_data(self, obj_key, handle):
                data = super()._get_raw_data(obj_key, handle)
                if data is not None and data.get("gender") == Person.FEMALE:
                    return None
                return data

        db = self.db
        db.__class__ = OnlyMen
        try:
            found = dict(db.get_raw_person_data_many(self.people))
        finally:
            db.__class__ = OnlyMen.__mro__[1]
        self.assertEqual(sorted(found), self.people[1::2])

    def test_proxies(self):
        """
        Proxies decide which objects are read, and clean them.
        """
        private = PrivateProxyDb(self.db)
        self._check(private, self.people, self.families)
        found = dict(private.get_raw_person_data_many(self.people))
        self.assertEqual(
            sorted(found),
            [handle for index, handle in enumerate(self.people) if index % 3],
        )
        # the private child reference is left out
        family = dict(private.get_raw_family_data_many([self.families[1]]))
        self.assertEqual(family[self.families[1]]["child_ref_list"], [])
        living = LivingProxyDb(private, LivingProxyDb.MODE_EXCLUDE_ALL)
        self._check(living, self.people, self.families)


if __name__ == "__main__":
    unittest.main()

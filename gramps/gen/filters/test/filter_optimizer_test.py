#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2025 Doug Blank <doug.blank@gmail.com>
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

import tempfile
import os
import unittest

from ...const import DATA_DIR
from ...db.utils import import_as_dict
from ...user import User
from ...filters import reload_custom_filters, FilterList, set_custom_filters
from ....gen import filters

custom_filters_xml = """<?xml version="1.0" encoding="utf-8"?>
<filters>
  <object type="Person">
    <filter name="Ancestors of" function="and">
      <rule class="IsAncestorOf" use_regex="False" use_case="False">
        <arg value="I0044"/>
        <arg value="1"/>
      </rule>
    </filter>
    <filter name="Family and their Spouses" function="or">
      <rule class="MatchesFilter" use_regex="False" use_case="False">
        <arg value="Ancestors of"/>
      </rule>
      <rule class="MatchesFilter" use_regex="False" use_case="False">
        <arg value="Siblings of Ancestors"/>
      </rule>
    </filter>
    <filter name="Siblings of Ancestors" function="and">
      <rule class="IsSiblingOfFilterMatch" use_regex="False" use_case="False">
        <arg value="Ancestors of"/>
      </rule>
    </filter>
    <filter name="Everyone" function="or">
      <rule class="Everyone" use_regex="False" use_case="False">
      </rule>
    </filter>
    <filter name="F1" function="or">
      <rule class="Everyone" use_regex="False" use_case="False">
      </rule>
      <rule class="MatchesFilter" use_regex="False" use_case="False">
        <arg value="F2"/>
      </rule>
    </filter>
    <filter name="F2" function="and">
      <rule class="MatchesFilter" use_regex="False" use_case="False">
        <arg value="F3"/>
      </rule>
    </filter>
    <filter name="F3" function="and">
      <rule class="IsAncestorOf" use_regex="False" use_case="False">
        <arg value="I0041"/>
        <arg value="0"/>
      </rule>
    </filter>
    <filter name="I0001 xor I0002" function="one">
      <rule class="HasIdOf" use_regex="False" use_case="False">
        <arg value="I0001"/>
      </rule>
      <rule class="HasIdOf" use_regex="False" use_case="False">
        <arg value="I0002"/>
      </rule>
    </filter>
    <filter name="I0001 or I0002" function="or">
      <rule class="HasIdOf" use_regex="False" use_case="False">
        <arg value="I0001"/>
      </rule>
      <rule class="HasIdOf" use_regex="False" use_case="False">
        <arg value="I0002"/>
      </rule>
    </filter>
    <filter name="I0001 and I0002" function="and">
      <rule class="HasIdOf" use_regex="False" use_case="False">
        <arg value="I0001"/>
      </rule>
      <rule class="HasIdOf" use_regex="False" use_case="False">
        <arg value="I0002"/>
      </rule>
    </filter>
    <filter name="I0001" function="or">
      <rule class="HasIdOf" use_regex="False" use_case="False">
        <arg value="I0001"/>
      </rule>
    </filter>
    <filter name="I0002" function="or">
      <rule class="HasIdOf" use_regex="False" use_case="False">
        <arg value="I0002"/>
      </rule>
    </filter>
    <filter name="not I0001" function="or" invert="1">
      <rule class="HasIdOf" use_regex="False" use_case="False">
        <arg value="I0001"/>
      </rule>
    </filter>
    <filter name="not I0002" function="or" invert="1">
      <rule class="HasIdOf" use_regex="False" use_case="False">
        <arg value="I0002"/>
      </rule>
    </filter>
    <filter name="(not I0001) and (not I0002)" function="and">
      <rule class="MatchesFilter" use_regex="False" use_case="False">
        <arg value="not I0001"/>
      </rule>
      <rule class="MatchesFilter" use_regex="False" use_case="False">
        <arg value="not I0002"/>
      </rule>
    </filter>
    <filter name="(not I0001) or (not I0002)" function="or">
      <rule class="MatchesFilter" use_regex="False" use_case="False">
        <arg value="not I0001"/>
      </rule>
      <rule class="MatchesFilter" use_regex="False" use_case="False">
        <arg value="not I0002"/>
      </rule>
    </filter>

    <filter name="not ((not I0001) and (not I0002))" function="and" invert="1">
      <rule class="MatchesFilter" use_regex="False" use_case="False">
        <arg value="not I0001"/>
      </rule>
      <rule class="MatchesFilter" use_regex="False" use_case="False">
        <arg value="not I0002"/>
      </rule>
    </filter>

    <filter name="not (I0001 and I0002)" function="and" invert="1">
      <rule class="MatchesFilter" use_regex="False" use_case="False">
        <arg value="I0001"/>
      </rule>
      <rule class="MatchesFilter" use_regex="False" use_case="False">
        <arg value="I0002"/>
      </rule>
    </filter>
    <filter name="Empty Filter and" function="and">
    </filter>
    <filter name="Empty Filter and invert" function="and" invert="1">
    </filter>
    <filter name="Empty Filter or" function="or">
    </filter>
    <filter name="Empty Filter or invert" function="or" invert="1">
    </filter>
    <filter name="Empty Filter one" function="one">
    </filter>
    <filter name="Empty Filter one invert" function="one" invert="1">
    </filter>
    <filter name="Tag = ToDo" function="and">
      <rule class="HasTag" use_regex="False" use_case="False">
        <arg value="ToDo"/>
      </rule>
    </filter>
    <filter name="Tag = ToDo Invert" function="and" invert="1">
      <rule class="HasTag" use_regex="False" use_case="False">
        <arg value="ToDo"/>
      </rule>
    </filter>
    <filter name="Family Name" function="and">
      <rule class="HasNameOf" use_regex="False" use_case="False">
        <arg value=""/>
        <arg value=""/>
        <arg value=""/>
        <arg value=""/>
        <arg value=""/>
        <arg value=""/>
        <arg value=""/>
        <arg value="Garner"/>
        <arg value=""/>
        <arg value=""/>
        <arg value=""/>
      </rule>
    </filter>
    <filter name="NOT Family Name" function="and" invert="1">
      <rule class="MatchesFilter" use_regex="False" use_case="False">
        <arg value="Family Name"/>
      </rule>
    </filter>
    <filter name="Person I1041" function="and">
      <rule class="HasIdOf" use_regex="False" use_case="False">
        <arg value="I1041"/>
      </rule>
    </filter>
    <filter name="Parents of Person I1041" function="or">
      <rule class="IsParentOfFilterMatch" use_regex="False" use_case="False">
        <arg value="Person I1041"/>
      </rule>
    </filter>
    <filter name="not Parents of Person I1041" function="or" invert="1">
      <rule class="IsParentOfFilterMatch" use_regex="False" use_case="False">
        <arg value="Person I1041"/>
      </rule>
    </filter>
  </object>
</filters>
"""
TEST_DIR = os.path.abspath(os.path.join(DATA_DIR, "tests"))
EXAMPLE = os.path.join(TEST_DIR, "example.gramps")


class OptimizerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Import example database.
        """
        cls.db = import_as_dict(EXAMPLE, User())

        fl = FilterList("")
        fl.loadString(custom_filters_xml)

        filters.set_custom_filters(fl)
        cls.the_custom_filters = filters.CustomFilters.get_filters_dict("Person")
        cls.filters = fl.get_filters_dict("Person")
        for filter_name in cls.filters:
            cls.the_custom_filters[filter_name] = cls.filters[filter_name]

    @classmethod
    def tearDownClass(self):
        reload_custom_filters()

    def test_ancestors_of(self):
        filter = self.filters["Ancestors of"]
        results = filter.apply(self.db)
        self.assertEqual(len(results), 7)

    def test_siblings_of_ancestors(self):
        filter = self.filters["Siblings of Ancestors"]
        results = filter.apply(self.db)
        self.assertEqual(len(results), 18)

    def test_family_and_their_spouses(self):
        filter = self.filters["Family and their Spouses"]
        results = filter.apply(self.db)
        self.assertEqual(len(results), 25)

    def test_everyone(self):
        filter = self.filters["Everyone"]
        results = filter.apply(self.db)
        self.assertEqual(len(results), 2128)

    def test_everyone_with_id_list(self):
        filter = self.filters["Everyone"]
        id_list = [self.db.get_default_handle()]
        results = filter.apply(self.db, id_list=id_list)
        self.assertEqual(len(results), 1)

    def test_everyone_with_id_list_tupleind_0(self):
        filter = self.filters["Everyone"]
        default_person = self.db.get_default_person()
        id_list = [(default_person.handle, default_person)]
        results = filter.apply(self.db, id_list=id_list, tupleind=0)
        self.assertEqual(results[0], id_list[0])
        self.assertEqual(len(results), 1)

    def test_everyone_with_id_list_tupleind_1(self):
        filter = self.filters["Everyone"]
        default_person = self.db.get_default_person()
        id_list = [(default_person, default_person.handle)]
        results = filter.apply(self.db, id_list=id_list, tupleind=1)
        self.assertEqual(results[0], id_list[0])
        self.assertEqual(len(results), 1)

    def test_everyone_with_id_list_tupleind_3(self):
        filter = self.filters["Everyone"]
        default_person = self.db.get_default_person()
        id_list = [(default_person, default_person.handle)]
        self.assertRaises(
            IndexError, filter.apply, self.db, id_list=id_list, tupleind=3
        )

    def test_everyone_with_id_list_empty(self):
        filter = self.filters["Everyone"]
        id_list = []
        results = filter.apply(self.db, id_list=id_list)
        self.assertEqual(len(results), 0)

    def test_f1(self):
        filter = self.filters["F1"]
        results = filter.apply(self.db)
        self.assertEqual(len(results), 2128)

    def test_f2(self):
        filter = self.filters["F2"]
        results = filter.apply(self.db)
        self.assertEqual(len(results), 16)

    def test_f3(self):
        filter = self.filters["F3"]
        results = filter.apply(self.db)
        self.assertEqual(len(results), 16)

    def test_I0001xorI0002(self):
        filter = self.filters["I0001 xor I0002"]
        results = filter.apply(self.db)
        self.assertEqual(len(results), 2)

    def test_I0001orI0002(self):
        filter = self.filters["I0001 or I0002"]
        results = filter.apply(self.db)
        self.assertEqual(len(results), 2)

    def test_I0001andI0002(self):
        filter = self.filters["I0001 and I0002"]
        results = filter.apply(self.db)
        self.assertEqual(len(results), 0)

    def test_EmptyFilter_and(self):
        filter = self.filters["Empty Filter and"]
        results = filter.apply(self.db)
        self.assertEqual(len(results), 2128)

    def test_EmptyFilter_and_invert(self):
        filter = self.filters["Empty Filter and invert"]
        results = filter.apply(self.db)
        self.assertEqual(len(results), 0)

    def test_EmptyFilter_or(self):
        filter = self.filters["Empty Filter or"]
        results = filter.apply(self.db)
        self.assertEqual(len(results), 0)

    def test_EmptyFilter_or_invert(self):
        filter = self.filters["Empty Filter or invert"]
        results = filter.apply(self.db)
        self.assertEqual(len(results), 2128)

    def test_EmptyFilter_one(self):
        filter = self.filters["Empty Filter one"]
        results = filter.apply(self.db)
        self.assertEqual(len(results), 0)

    def test_EmptyFilter_one_invert(self):
        filter = self.filters["Empty Filter one invert"]
        results = filter.apply(self.db)
        self.assertEqual(len(results), 2128)

    def test_TagToDo(self):
        filter = self.filters["Tag = ToDo"]
        results = filter.apply(self.db)
        self.assertEqual(len(results), 1)

    def test_TagToDo_invert(self):
        filter = self.filters["Tag = ToDo Invert"]
        results = filter.apply(self.db)
        self.assertEqual(len(results), 2127)

    def test_family_name(self):
        filter = self.filters["Family Name"]
        results = filter.apply(self.db)
        self.assertEqual(len(results), 71)

    def test_not_family_name(self):
        filter = self.filters["NOT Family Name"]
        results = filter.apply(self.db)
        self.assertEqual(len(results), 2128 - 71)

    def test_not_i0001_and_not_i0002(self):
        filter = self.filters["(not I0001) and (not I0002)"]
        results = filter.apply(self.db)
        self.assertEqual(len(results), 2128 - 2)

    def test_not_i0001_or_not_i0002(self):
        filter = self.filters["(not I0001) or (not I0002)"]
        results = filter.apply(self.db)
        self.assertEqual(len(results), 2128)

    def test_not_not_i0001_and_not_i0002(self):
        filter = self.filters["not ((not I0001) and (not I0002))"]
        results = filter.apply(self.db)
        self.assertEqual(len(results), 2)

    def test_not_i0001_and_i0002(self):
        filter = self.filters["not (I0001 and I0002)"]
        results = filter.apply(self.db)
        self.assertEqual(len(results), 2128)

    def test_i0001(self):
        filter = self.filters["I0001"]
        results = filter.apply(self.db)
        self.assertEqual(len(results), 1)

    def test_not_i0001(self):
        filter = self.filters["not I0001"]
        results = filter.apply(self.db)
        self.assertEqual(len(results), 2127)

    def test_i0002(self):
        filter = self.filters["I0002"]
        results = filter.apply(self.db)
        self.assertEqual(len(results), 1)

    def test_not_i0002(self):
        filter = self.filters["not I0002"]
        results = filter.apply(self.db)
        self.assertEqual(len(results), 2127)

    def test_person_I1041(self):
        filter = self.filters["Person I1041"]
        results = filter.apply(self.db)
        self.assertEqual(len(results), 1)

    def test_parents_of_person_I1041(self):
        filter = self.filters["Parents of Person I1041"]
        results = filter.apply(self.db)
        self.assertEqual(len(results), 2)

    def test_not_parents_of_person_I1041(self):
        filter = self.filters["not Parents of Person I1041"]
        results = filter.apply(self.db)
        self.assertEqual(len(results), 2128 - 2)

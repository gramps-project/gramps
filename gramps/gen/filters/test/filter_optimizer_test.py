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

        # filters.set_custom_filters(fl)
        # cls.the_custom_filters = filters.CustomFilters.get_filters_dict("Person")
        # cls.filters = fl.get_filters_dict("Person")
        # for filter_name in cls.filters:
        #     cls.the_custom_filters[filter_name] = cls.filters[filter_name]

    @classmethod
    def tearDownClass(self):
        # filters.set_custom_filters(None)
        pass

    def test_ancestors_of(self):
        pass
    #     filter = self.filters["Ancestors of"]
    #     results = filter.apply(self.db)
    #     self.assertEqual(len(results), 7)

    # def test_siblings_of_ancestors(self):
    #     filter = self.filters["Siblings of Ancestors"]
    #     results = filter.apply(self.db)
    #     self.assertEqual(len(results), 18)

    # def test_family_and_their_spouses(self):
    #     filter = self.filters["Family and their Spouses"]
    #     results = filter.apply(self.db)
    #     self.assertEqual(len(results), 25)

    # def test_everyone(self):
    #     filter = self.filters["Everyone"]
    #     results = filter.apply(self.db)
    #     self.assertEqual(len(results), 2128)

    # def test_f1(self):
    #     filter = self.filters["F1"]
    #     results = filter.apply(self.db)
    #     self.assertEqual(len(results), 2128)

    # def test_f2(self):
    #     filter = self.filters["F2"]
    #     results = filter.apply(self.db)
    #     self.assertEqual(len(results), 16)

    # def test_f3(self):
    #     filter = self.filters["F3"]
    #     results = filter.apply(self.db)
    #     self.assertEqual(len(results), 16)

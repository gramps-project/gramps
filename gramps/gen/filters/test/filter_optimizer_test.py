import tempfile
import os
import unittest

from ...const import DATA_DIR
from ...db.utils import import_as_dict
from ...user import User
from ...filters import reload_custom_filters, CustomFilters, FilterList

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

        with tempfile.NamedTemporaryFile(mode="w+", encoding="utf8") as tmp_file:
            tmp_file.write(custom_filters_xml)
            tmp_file.seek(0)
            fl = FilterList(tmp_file.name)
            fl.load()

        cls.the_custom_filters = CustomFilters.get_filters_dict("Person")
        cls.filters = fl.get_filters_dict("Person")

    def setUp(self):
        for filter_name in self.filters:
            self.the_custom_filters[filter_name] = self.filters[filter_name]

    def tearDown(self):
        for filter_name in self.filters:
            CustomFilters.remove("Person", filter_name)

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

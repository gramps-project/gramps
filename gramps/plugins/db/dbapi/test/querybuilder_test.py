#
# Gramps - a GTK+/GNOME based genealogy program
#
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
Unittest that tests QueryBuilder.get_sql_query() with the same parameters
used in person_select_test.py
"""
import unittest

import sqlglot

from gramps.gen.lib import Person, EventRoleType, FamilyRelType
from gramps.plugins.db.dbapi.query_builder import QueryBuilder


class QueryBuilderTestMixin:
    """
    Mixin class for QueryBuilder tests with common test methods.
    Subclasses should set self.dialect in setUp.
    """

    def setUp(self):
        """
        Set up QueryBuilder with proper environment.
        """
        # Environment dictionary with necessary classes and constants
        self.env = {
            "Person": Person,
            "EventRoleType": EventRoleType,
            "FamilyRelType": FamilyRelType,
        }
        # Subclasses should set self.dialect before calling super().setUp()
        self.query_builder = QueryBuilder(
            "person",
            env=self.env,
            dialect=self.dialect,
        )

    def _validate_sql(self, sql):
        """
        Validate SQL query using sqlglot with roundtrip parsing for the dialect.

        Args:
            sql: SQL query string to validate

        Raises:
            AssertionError: If SQL cannot be parsed or roundtrip fails
        """
        # Parse the original SQL
        tree = sqlglot.parse_one(sql)

        # Test roundtrip for the dialect - verify it can be parsed and regenerated
        roundtrip = tree.sql(dialect=self.dialect)
        tree_roundtrip = sqlglot.parse_one(roundtrip)
        roundtrip2 = tree_roundtrip.sql(dialect=self.dialect)
        # Compare SQL strings after roundtrip (trees may differ but SQL should be equivalent)
        assert roundtrip == roundtrip2, (
            f"{self.dialect.upper()} roundtrip failed. Original: {sql}, "
            f"First roundtrip: {roundtrip}, Second roundtrip: {roundtrip2}"
        )

    def test_order_by_1(self):
        """
        Test ORDER BY with descending surname and ascending gender.
        Uses same parameters as test_order_by_1 in person_select_test.py
        """
        what = ["person.primary_name.surname_list[0].surname", "person.gender"]
        where = "len(person.media_list) > 0"
        order_by = [
            "-person.primary_name.surname_list[0].surname",
            "person.gender",
        ]
        sql = self.query_builder.get_sql_query(what, where, order_by)

        # Validate SQL with sqlglot
        self._validate_sql(sql)

    def test_order_by_2(self):
        """
        Test ORDER BY with ascending surname and descending gender.
        Uses same parameters as test_order_by_2 in person_select_test.py
        """
        what = ["person.primary_name.surname_list[0].surname", "person.gender"]
        where = "len(person.media_list) > 0"
        order_by = [
            "person.primary_name.surname_list[0].surname",
            "-person.gender",
        ]
        sql = self.query_builder.get_sql_query(what, where, order_by)

        # Validate SQL with sqlglot
        self._validate_sql(sql)

    def test_HavePhotos(self):
        """
        Test selecting handles where person has photos.
        Uses same parameters as test_HavePhotos in person_select_test.py
        """
        what = "obj.handle"
        where = "len(person.media_list) > 0"
        order_by = None
        sql = self.query_builder.get_sql_query(what, where, order_by)

        # Validate SQL with sqlglot
        self._validate_sql(sql)

    def test_disconnected(self):
        """
        Test selecting handles for disconnected persons.
        Uses same parameters as test_disconnected in person_select_test.py
        """
        what = "person.handle"
        where = "len(person.family_list) == 0 and len(person.parent_family_list) == 0"
        order_by = None
        sql = self.query_builder.get_sql_query(what, where, order_by)

        # Validate SQL with sqlglot
        self._validate_sql(sql)

    def test_hasunknowngender(self):
        """
        Test selecting handles for persons with unknown gender.
        Uses same parameters as test_hasunknowngender in person_select_test.py
        """
        what = "person.handle"
        where = "person.gender == Person.UNKNOWN"
        order_by = None
        sql = self.query_builder.get_sql_query(what, where, order_by)

        # Validate SQL with sqlglot
        self._validate_sql(sql)

    def test_isfemale(self):
        """
        Test selecting handles for female persons.
        Uses same parameters as test_isfemale in person_select_test.py
        """
        what = "person.handle"
        where = "person.gender == Person.FEMALE"
        order_by = None
        sql = self.query_builder.get_sql_query(what, where, order_by)

        # Validate SQL with sqlglot
        self._validate_sql(sql)

    def test_ismale(self):
        """
        Test selecting handles for male persons.
        Uses same parameters as test_ismale in person_select_test.py
        """
        what = "person.handle"
        where = "person.gender == Person.MALE"
        order_by = None
        sql = self.query_builder.get_sql_query(what, where, order_by)

        # Validate SQL with sqlglot
        self._validate_sql(sql)

    def test_hasidof_matching(self):
        """
        Test selecting handles for persons with specific gramps_id.
        Uses same parameters as test_hasidof_matching in person_select_test.py
        """
        what = "person.handle"
        where = "person.gramps_id == 'I0044'"
        order_by = None
        sql = self.query_builder.get_sql_query(what, where, order_by)

        # Validate SQL with sqlglot
        self._validate_sql(sql)

    def test_hasidof_startswith(self):
        """
        Test selecting handles for persons with gramps_id starting with prefix.
        Uses same parameters as test_hasidof_startswith in person_select_test.py
        """
        what = "person.handle"
        where = "person.gramps_id.startswith('I00')"
        order_by = None
        sql = self.query_builder.get_sql_query(what, where, order_by)

        # Validate SQL with sqlglot
        self._validate_sql(sql)

    def test_multiplemarriages(self):
        """
        Test selecting handles for persons with multiple marriages.
        Uses same parameters as test_multiplemarriages in person_select_test.py
        """
        what = "person.handle"
        where = "len(person.family_list) > 1"
        order_by = None
        sql = self.query_builder.get_sql_query(what, where, order_by)

        # Validate SQL with sqlglot
        self._validate_sql(sql)

    def test_nevermarried(self):
        """
        Test selecting handles for persons who never married.
        Uses same parameters as test_nevermarried in person_select_test.py
        """
        what = "person.handle"
        where = "len(person.family_list) == 0"
        order_by = None
        sql = self.query_builder.get_sql_query(what, where, order_by)

        # Validate SQL with sqlglot
        self._validate_sql(sql)

    def test_peopleprivate(self):
        """
        Test selecting handles for private persons.
        Uses same parameters as test_peopleprivate in person_select_test.py
        """
        what = "person.handle"
        where = "person.private"
        order_by = None
        sql = self.query_builder.get_sql_query(what, where, order_by)

        # Validate SQL with sqlglot
        self._validate_sql(sql)

    def test_peoplepublic(self):
        """
        Test selecting handles for public persons.
        Uses same parameters as test_peoplepublic in person_select_test.py
        """
        what = "person.handle"
        where = "not person.private"
        order_by = None
        sql = self.query_builder.get_sql_query(what, where, order_by)

        # Validate SQL with sqlglot
        self._validate_sql(sql)

    def test_string_endswith(self):
        """
        Test selecting handles using string endswith method.
        Uses same parameters as test_string_endswith in person_select_test.py
        """
        what = "person.handle"
        where = "person.gramps_id.endswith('44')"
        order_by = None
        sql = self.query_builder.get_sql_query(what, where, order_by)

        # Validate SQL with sqlglot
        self._validate_sql(sql)

    def test_string_in_pattern(self):
        """
        Test selecting handles using 'string in attribute' pattern.
        Uses same parameters as test_string_in_pattern in person_select_test.py
        """
        what = "person.handle"
        where = "'I00' in person.gramps_id"
        order_by = None
        sql = self.query_builder.get_sql_query(what, where, order_by)

        # Validate SQL with sqlglot
        self._validate_sql(sql)

    def test_join_person_family_basic(self):
        """
        Test JOIN between person and family tables.
        Uses same parameters as test_join_person_family_basic in person_select_test.py
        """
        what = ["person.handle", "family.handle"]
        where = "person.handle == family.father_handle"
        order_by = None
        sql = self.query_builder.get_sql_query(what, where, order_by)

        # Validate SQL with sqlglot
        self._validate_sql(sql)

    def test_join_person_family_with_condition(self):
        """
        Test JOIN with additional condition on family table.
        Uses same parameters as test_join_person_family_with_condition in person_select_test.py
        """
        what = ["person.handle", "family.handle", "family.type.value"]
        where = "person.handle == family.father_handle and family.type.value == FamilyRelType.MARRIED"
        order_by = None
        sql = self.query_builder.get_sql_query(what, where, order_by)

        # Validate SQL with sqlglot
        self._validate_sql(sql)

    def test_join_with_variable_index_array_access(self):
        """
        Test JOIN with variable-index array access in join condition.
        Example: person.event_ref_list[person.birth_ref_index].ref == event.handle
        """
        what = ["person.handle", "event.handle"]
        where = "person.event_ref_list[person.birth_ref_index].ref == event.handle"
        order_by = None
        sql = self.query_builder.get_sql_query(what, where, order_by)

        # Validate SQL with sqlglot
        self._validate_sql(sql)

        # Verify that the join condition is present in the SQL
        self.assertIn("JOIN", sql.upper())
        self.assertIn("event", sql.lower())

    def test_join_with_variable_index_array_access_and_condition(self):
        """
        Test JOIN with variable-index array access and additional condition.
        Example: person.event_ref_list[person.birth_ref_index].ref == event.handle and event.type.value == 1
        """
        from gramps.gen.lib import EventType

        what = ["person.handle", "event.handle", "event.type.value"]
        where = "person.event_ref_list[person.birth_ref_index].ref == event.handle and event.type.value == EventType.BIRTH"
        order_by = None
        sql = self.query_builder.get_sql_query(what, where, order_by)

        # Validate SQL with sqlglot
        self._validate_sql(sql)

        # Verify that the join condition is present in the SQL
        self.assertIn("JOIN", sql.upper())
        self.assertIn("event", sql.lower())

    def test_list_comprehension_in_what_basic(self):
        """
        Test list comprehension in what clause.
        Uses same parameters as test_list_comprehension_in_what_basic in person_select_test.py
        """
        what = "[eref.role.value for eref in person.event_ref_list]"
        where = None
        order_by = None
        sql = self.query_builder.get_sql_query(what, where, order_by)

        # Validate SQL with sqlglot
        self._validate_sql(sql)

    def test_list_comprehension_in_what_basic_with_multiple_returns(self):
        """
        Test list comprehension in what clause.
        Uses same parameters as test_list_comprehension_in_what_basic in person_select_test.py
        """
        what = "[(eref.role.value, eref.ref) for eref in person.event_ref_list]"
        where = None
        order_by = None
        sql = self.query_builder.get_sql_query(what, where, order_by)

        # Validate SQL with sqlglot
        self._validate_sql(sql)

    def test_list_comprehension_concatenated_arrays(self):
        """
        Test list comprehension with concatenated arrays.
        Tests the pattern: [name.first_name for name in [person.primary_name] + person.alternate_names]
        """
        what = "[name.first_name for name in [person.primary_name] + person.alternate_names]"
        where = None
        order_by = None
        sql = self.query_builder.get_sql_query(what, where, order_by)

        # Validate SQL with sqlglot
        self._validate_sql(sql)

        # Verify the SQL contains UNION ALL for concatenated arrays
        self.assertIn("UNION ALL", sql.upper())

    def test_any_list_comprehension_in_where_basic(self):
        """
        Test any() with list comprehension in where clause.
        Uses same parameters as test_any_list_comprehension_in_where_basic in person_select_test.py
        """
        what = "person.handle"
        where = "any([eref for eref in person.event_ref_list])"
        order_by = None
        sql = self.query_builder.get_sql_query(what, where, order_by)

        # Validate SQL with sqlglot
        self._validate_sql(sql)

    def test_array_expansion_basic(self):
        """
        Test array expansion pattern.
        Uses same parameters as test_array_expansion_basic in person_select_test.py
        """
        what = "item.role.value"
        where = "item in person.event_ref_list"
        order_by = None
        sql = self.query_builder.get_sql_query(what, where, order_by)

        # Validate SQL with sqlglot
        self._validate_sql(sql)

    def test_simple_and_expression(self):
        """
        Test simple AND expression.
        Uses same parameters as test_simple_and_expression in person_select_test.py
        """
        what = "person.handle"
        where = "person.gender == Person.MALE and len(person.family_list) > 0"
        order_by = None
        sql = self.query_builder.get_sql_query(what, where, order_by)

        # Validate SQL with sqlglot
        self._validate_sql(sql)

    def test_simple_or_expression(self):
        """
        Test simple OR expression.
        Uses same parameters as test_simple_or_expression in person_select_test.py
        """
        what = "person.handle"
        where = "person.gender == Person.MALE or len(person.family_list) == 0"
        order_by = None
        sql = self.query_builder.get_sql_query(what, where, order_by)

        # Validate SQL with sqlglot
        self._validate_sql(sql)

    def test_variable_index_array_access_in_what(self):
        """
        Test variable-index array access in what clause.
        Example: person.event_ref_list[person.birth_ref_index]
        """
        what = "person.event_ref_list[person.birth_ref_index]"
        where = None
        order_by = None
        sql = self.query_builder.get_sql_query(what, where, order_by)

        # Validate SQL with sqlglot
        self._validate_sql(sql)

    def test_variable_index_array_access_with_attributes(self):
        """
        Test variable-index array access with subsequent attribute access.
        Example: person.event_ref_list[person.birth_ref_index].role.value
        """
        what = "person.event_ref_list[person.birth_ref_index].role.value"
        where = None
        order_by = None
        sql = self.query_builder.get_sql_query(what, where, order_by)

        # Validate SQL with sqlglot
        self._validate_sql(sql)

    def test_variable_index_array_access_in_where(self):
        """
        Test variable-index array access in where clause (truthiness check).
        Example: person.event_ref_list[person.birth_ref_index]
        """
        what = "person.handle"
        where = "person.event_ref_list[person.birth_ref_index]"
        order_by = None
        sql = self.query_builder.get_sql_query(what, where, order_by)

        # Validate SQL with sqlglot
        self._validate_sql(sql)

    def test_variable_index_array_access_with_attributes_in_where(self):
        """
        Test variable-index array access with attributes in where clause.
        Example: person.event_ref_list[person.birth_ref_index].role.value == 5
        """
        what = "person.handle"
        where = "person.event_ref_list[person.birth_ref_index].role.value == 5"
        order_by = None
        sql = self.query_builder.get_sql_query(what, where, order_by)

        # Validate SQL with sqlglot
        self._validate_sql(sql)


class QueryBuilderSQLiteTest(QueryBuilderTestMixin, unittest.TestCase):
    """
    Tests for QueryBuilder.get_sql_query() using SQLite dialect.
    """

    def setUp(self):
        """
        Set up QueryBuilder with SQLite dialect.
        """
        self.dialect = "sqlite"
        super().setUp()


class QueryBuilderPostgreSQLTest(QueryBuilderTestMixin, unittest.TestCase):
    """
    Tests for QueryBuilder.get_sql_query() using PostgreSQL dialect.
    """

    def setUp(self):
        """
        Set up QueryBuilder with PostgreSQL dialect.
        """
        self.dialect = "postgres"
        super().setUp()


if __name__ == "__main__":
    unittest.main()

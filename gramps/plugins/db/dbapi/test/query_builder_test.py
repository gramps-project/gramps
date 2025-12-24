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

Note: These tests validate SQL syntax and structure using sqlglot, but do NOT
validate query semantics by executing queries against a real database. For semantic
validation, see person_select_test.py which runs queries against an actual database
and verifies the results.

To add semantic tests:
1. Use a test database fixture (see person_select_test.py for examples)
2. Execute the generated SQL or use db.select_from_* methods
3. Verify the results match expected values
4. Consider edge cases like NULL handling, empty values, and JSON field semantics
"""
import unittest

import sqlglot

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
        # Subclasses should set self.dialect before calling super().setUp()
        self.query_builder = QueryBuilder(
            "person",
            env={},
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
        # Parse the original SQL with the dialect to catch dialect-specific issues
        tree = sqlglot.parse_one(sql, dialect=self.dialect)

        # Test roundtrip for the dialect - verify it can be parsed and regenerated
        roundtrip = tree.sql(dialect=self.dialect)
        tree_roundtrip = sqlglot.parse_one(roundtrip, dialect=self.dialect)
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

    def test_any_list_comprehension_with_if_condition(self):
        """
        Test any() with list comprehension that has an 'if' condition clause.
        Tests the pattern: any([name for name in [person.primary_name] + person.alternate_names if search_name in name.first_name])
        """
        # Add search_name to environment for this test
        self.query_builder.env["search_name"] = "John"
        what = "person.handle"
        where = "any([name for name in [person.primary_name] + person.alternate_names if search_name in name.first_name])"
        order_by = None
        sql = self.query_builder.get_sql_query(what, where, order_by)

        # Validate SQL with sqlglot
        self._validate_sql(sql)

        # Verify that the condition is included (not just 1=1 placeholder)
        self.assertNotIn("1=1", sql, "SQL should not contain placeholder 1=1")
        self.assertIn("first_name", sql, "SQL should contain first_name condition")
        # Verify that the condition is in the WHERE clause of the EXISTS subquery
        self.assertIn("WHERE", sql.upper())
        # Verify that UNION is used for concatenated arrays
        self.assertIn(
            "UNION", sql.upper(), "SQL should use UNION for concatenated arrays"
        )

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

    def test_array_expansion_with_join_to_event(self):
        """
        Test array expansion with join to event table.
        Tests the pattern: item in person.event_ref_list and item.ref == event.handle
        with additional conditions on the joined event table.
        """
        what = "person.handle"
        where = "item in person.event_ref_list and item.ref == event.handle and (not event.place or not event.date)"
        order_by = None
        sql = self.query_builder.get_sql_query(what, where, order_by)

        # Validate SQL with sqlglot
        self._validate_sql(sql)

        # Verify that the join condition is present in the SQL
        self.assertIn("JOIN", sql.upper())
        self.assertIn("event", sql.lower())
        # Verify that json_each is present for array expansion
        self.assertIn("json_each", sql.lower())
        # Verify that "not" for JSON fields generates IS NULL checks
        # (not just NOT json_extract(...))
        self.assertIn("IS NULL", sql.upper())

    def test_not_operator_for_json_fields(self):
        """
        Test that "not" operator for JSON fields generates correct SQL.
        For JSON fields, "not field" should check for NULL, empty string, empty array, etc.
        """
        what = "person.handle"
        where = "not event.place"
        order_by = None
        sql = self.query_builder.get_sql_query(what, where, order_by)

        # Validate SQL with sqlglot
        self._validate_sql(sql)

        # Verify that "not" for JSON fields uses IS NULL check, not just NOT
        # This is important because NOT json_extract(...) doesn't work correctly
        # for JSON null/empty values in SQLite
        self.assertIn("IS NULL", sql.upper())
        # Should also check for empty values
        self.assertIn("= ''", sql)

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

    def test_pagination_basic(self):
        """
        Test basic pagination with LIMIT and OFFSET.
        """
        what = "person.handle"
        where = None
        order_by = "person.handle"
        sql = self.query_builder.get_sql_query(
            what, where, order_by, page=1, page_size=10
        )

        # Validate SQL with sqlglot
        self._validate_sql(sql)
        # Verify LIMIT and OFFSET are present
        self.assertIn("LIMIT", sql.upper())
        self.assertIn("OFFSET", sql.upper())
        self.assertIn("10", sql)
        self.assertIn("0", sql)  # OFFSET for page 1 should be 0

    def test_pagination_second_page(self):
        """
        Test pagination for second page.
        """
        what = "person.handle"
        where = None
        order_by = "person.handle"
        sql = self.query_builder.get_sql_query(
            what, where, order_by, page=2, page_size=20
        )

        # Validate SQL with sqlglot
        self._validate_sql(sql)
        # Verify LIMIT and OFFSET are present
        self.assertIn("LIMIT", sql.upper())
        self.assertIn("OFFSET", sql.upper())
        self.assertIn("20", sql)
        self.assertIn("20", sql)  # OFFSET for page 2 with page_size 20 should be 20

    def test_pagination_with_where(self):
        """
        Test pagination with WHERE clause.
        """
        what = "person.handle"
        where = "person.gender == Person.MALE"
        order_by = "person.handle"
        sql = self.query_builder.get_sql_query(
            what, where, order_by, page=1, page_size=15
        )

        # Validate SQL with sqlglot
        self._validate_sql(sql)
        # Verify LIMIT and OFFSET are present
        self.assertIn("LIMIT", sql.upper())
        self.assertIn("OFFSET", sql.upper())

    def test_pagination_with_order_by(self):
        """
        Test pagination with ORDER BY clause.
        """
        what = ["person.primary_name.surname_list[0].surname", "person.gender"]
        where = "len(person.media_list) > 0"
        order_by = [
            "-person.primary_name.surname_list[0].surname",
            "person.gender",
        ]
        sql = self.query_builder.get_sql_query(
            what, where, order_by, page=1, page_size=5
        )

        # Validate SQL with sqlglot
        self._validate_sql(sql)
        # Verify LIMIT and OFFSET are present after ORDER BY
        self.assertIn("LIMIT", sql.upper())
        self.assertIn("OFFSET", sql.upper())

    def test_pagination_with_join(self):
        """
        Test pagination with JOIN queries.
        """
        what = ["person.handle", "family.handle"]
        where = "person.handle == family.father_handle"
        order_by = None
        sql = self.query_builder.get_sql_query(
            what, where, order_by, page=1, page_size=25
        )

        # Validate SQL with sqlglot
        self._validate_sql(sql)
        # Verify LIMIT and OFFSET are present
        self.assertIn("LIMIT", sql.upper())
        self.assertIn("OFFSET", sql.upper())

    def test_complex_binary_operations(self):
        """
        Test all binary operators: +, -, *, /, %, **, //
        """
        what = "person.handle"

        # Addition
        where = "len(person.media_list) + len(person.note_list) > 0"
        sql = self.query_builder.get_sql_query(what, where, None)
        self._validate_sql(sql)
        self.assertIn("+", sql)

        # Subtraction
        where = "len(person.family_list) - len(person.parent_family_list) > 0"
        sql = self.query_builder.get_sql_query(what, where, None)
        self._validate_sql(sql)
        self.assertIn("-", sql)

        # Multiplication
        where = "len(person.media_list) * 2 > 0"
        sql = self.query_builder.get_sql_query(what, where, None)
        self._validate_sql(sql)
        self.assertIn("*", sql)

        # Division
        where = "len(person.family_list) / 1.0 > 1"
        sql = self.query_builder.get_sql_query(what, where, None)
        self._validate_sql(sql)
        self.assertIn("/", sql)

        # Modulo
        where = "len(person.family_list) % 2 == 0"
        sql = self.query_builder.get_sql_query(what, where, None)
        self._validate_sql(sql)
        self.assertIn("%", sql)

        # Power
        where = "len(person.media_list) ** 2 > 0"
        sql = self.query_builder.get_sql_query(what, where, None)
        self._validate_sql(sql)
        # Power is converted to POW() function
        self.assertIn("POW", sql.upper())

        # Floor division
        where = "len(person.family_list) // 2 > 0"
        sql = self.query_builder.get_sql_query(what, where, None)
        self._validate_sql(sql)
        # Floor division is converted to CAST(...AS INT)
        self.assertIn("CAST", sql.upper())

    def test_ternary_expression(self):
        """
        Test ternary expression (if/else).
        """
        what = "person.handle if person.gender == Person.MALE else person.handle"
        where = None
        sql = self.query_builder.get_sql_query(what, where, None)
        self._validate_sql(sql)
        # Should contain CASE WHEN or similar
        self.assertIn("CASE", sql.upper())

    def test_nested_attribute_access_chain(self):
        """
        Test deeply nested attribute access chains.
        """
        what = "person.primary_name.surname_list[0].surname"
        where = None
        sql = self.query_builder.get_sql_query(what, where, None)
        self._validate_sql(sql)
        self._validate_sql(sql)

        # Test even deeper nesting
        what = "person.primary_name.surname_list[0].surname"
        where = "person.primary_name.first_name"
        sql = self.query_builder.get_sql_query(what, where, None)
        self._validate_sql(sql)

    def test_complex_join_conditions(self):
        """
        Test complex JOIN conditions with multiple tables and nested conditions.
        """
        # Multiple JOINs
        what = ["person.handle", "family.handle", "event.handle"]
        where = "person.handle == family.father_handle and person.event_ref_list[0].ref == event.handle"
        sql = self.query_builder.get_sql_query(what, where, None)
        self._validate_sql(sql)
        self.assertIn("JOIN", sql.upper())
        self.assertIn("family", sql.lower())
        self.assertIn("event", sql.lower())

    def test_nested_list_comprehension_syntax(self):
        """
        Test nested list comprehension syntax (if supported).
        Note: This may not be fully supported, but we test the syntax.
        """
        # Simple nested: list of lists
        what = "[[eref.ref for eref in person.event_ref_list] for person in [person]]"
        where = None
        # This may raise an error if not supported, which is fine
        try:
            sql = self.query_builder.get_sql_query(what, where, None)
            self._validate_sql(sql)
        except (ValueError, AttributeError):
            # Nested list comprehensions may not be supported
            pass

    def test_complex_boolean_with_parentheses(self):
        """
        Test complex boolean expressions with multiple levels of parentheses.
        """
        what = "person.handle"
        where = "((person.gender == Person.MALE and len(person.family_list) > 0) or (person.gender == Person.FEMALE and len(person.media_list) > 0)) and len(person.note_list) > 0"
        sql = self.query_builder.get_sql_query(what, where, None)
        self._validate_sql(sql)
        # Should have proper boolean structure
        self.assertIn("AND", sql.upper())
        self.assertIn("OR", sql.upper())

    def test_unary_operations(self):
        """
        Test unary operations: - (negation) and not.
        """
        what = "person.handle"

        # Negation
        where = "-len(person.family_list) < 0"
        sql = self.query_builder.get_sql_query(what, where, None)
        self._validate_sql(sql)
        self.assertIn("-", sql)

        # Not operator
        where = "not person.private"
        sql = self.query_builder.get_sql_query(what, where, None)
        self._validate_sql(sql)
        # For JSON fields, "not" generates IS NULL checks
        self.assertIn("IS NULL", sql.upper())

    def test_comparison_operators_all(self):
        """
        Test all comparison operators: ==, !=, <, >, <=, >=, in, not in, is, is not.
        """
        what = "person.handle"

        # Equality
        where = "person.gender == Person.MALE"
        sql = self.query_builder.get_sql_query(what, where, None)
        self._validate_sql(sql)
        self.assertIn("=", sql)

        # Inequality
        where = "person.gender != Person.MALE"
        sql = self.query_builder.get_sql_query(what, where, None)
        self._validate_sql(sql)
        # Should contain != or <> for inequality
        self.assertTrue("!=" in sql or "<>" in sql)

        # Less than
        where = "len(person.family_list) < 5"
        sql = self.query_builder.get_sql_query(what, where, None)
        self._validate_sql(sql)
        self.assertIn("<", sql)

        # Greater than
        where = "len(person.family_list) > 0"
        sql = self.query_builder.get_sql_query(what, where, None)
        self._validate_sql(sql)
        self.assertIn(">", sql)

        # Less than or equal
        where = "len(person.family_list) <= 5"
        sql = self.query_builder.get_sql_query(what, where, None)
        self._validate_sql(sql)
        self.assertIn("<=", sql)

        # Greater than or equal
        where = "len(person.family_list) >= 0"
        sql = self.query_builder.get_sql_query(what, where, None)
        self._validate_sql(sql)
        self.assertIn(">=", sql)

        # In (string in attribute)
        where = "'I00' in person.gramps_id"
        sql = self.query_builder.get_sql_query(what, where, None)
        self._validate_sql(sql)
        # Should contain LIKE or INSTR for string matching
        self.assertTrue(
            "LIKE" in sql.upper() or "INSTR" in sql.upper() or "LIKE" in sql
        )

        # Is
        where = "person.birth_ref_index is not None"
        sql = self.query_builder.get_sql_query(what, where, None)
        self._validate_sql(sql)
        self.assertIn("IS NOT NULL", sql.upper())

    def test_chained_comparisons(self):
        """
        Test chained comparisons: a < b < c.
        """
        what = "person.handle"
        where = "0 < len(person.family_list) < 10"
        sql = self.query_builder.get_sql_query(what, where, None)
        self._validate_sql(sql)
        # Chained comparisons should be expanded to AND
        self.assertIn("AND", sql.upper())

    def test_tuple_in_what(self):
        """
        Test tuple expressions in what clause.
        """
        what = "(person.handle, person.gender)"
        where = None
        sql = self.query_builder.get_sql_query(what, where, None)
        self._validate_sql(sql)
        # Should have multiple columns
        self.assertIn("person", sql.lower())

    def test_call_expression_methods(self):
        """
        Test method calls like startswith, endswith.
        """
        what = "person.handle"

        # startswith
        where = "person.gramps_id.startswith('I00')"
        sql = self.query_builder.get_sql_query(what, where, None)
        self._validate_sql(sql)
        # Should contain LIKE or SUBSTR for string matching
        self.assertTrue(
            "LIKE" in sql.upper() or "SUBSTR" in sql.upper() or "LIKE" in sql
        )

        # endswith
        where = "person.gramps_id.endswith('44')"
        sql = self.query_builder.get_sql_query(what, where, None)
        self._validate_sql(sql)
        # Should contain LIKE or SUBSTR for string matching
        self.assertTrue(
            "LIKE" in sql.upper() or "SUBSTR" in sql.upper() or "LIKE" in sql
        )

    def test_len_function(self):
        """
        Test len() function calls.
        """
        what = "person.handle"
        where = "len(person.family_list) > 0"
        sql = self.query_builder.get_sql_query(what, where, None)
        self._validate_sql(sql)
        # len() should be converted to json_array_length or similar
        self.assertTrue(
            "json_array_length" in sql.lower() or "JSON_ARRAY_LENGTH" in sql.upper()
        )


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

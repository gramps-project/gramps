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
Unittest that tests ExpressionBuilder methods (convert, convert_where_clause, get_order_by)
with the same parameters used in person_select_test.py and query_builder_test.py
"""
import unittest

from gramps.gen.lib import Person, EventRoleType, FamilyRelType
from gramps.plugins.db.dbapi.expression_builder import ExpressionBuilder


class ExpressionBuilderTestMixin:
    """
    Mixin class for ExpressionBuilder tests with common test methods.
    Subclasses should set self.dialect in setUp.
    """

    def setUp(self):
        """
        Set up ExpressionBuilder with proper environment.
        """
        # Environment dictionary with necessary classes and constants
        self.env = {
            "Person": Person,
            "EventRoleType": EventRoleType,
            "FamilyRelType": FamilyRelType,
        }
        # Subclasses should set self.dialect before calling super().setUp()
        # Set json_extract and json_array_length based on dialect
        if self.dialect == "sqlite":
            json_extract = "json_extract(json_data, '$.{attr}')"
            json_array_length = "json_array_length(json_extract(json_data, '$.{attr}'))"
        elif self.dialect == "postgres":
            json_extract = "JSON_EXTRACT_PATH(json_data, '{attr}')"
            json_array_length = (
                "JSON_ARRAY_LENGTH(JSON_EXTRACT_PATH(json_data, '{attr}'))"
            )
        else:
            # Default to SQLite format
            json_extract = "json_extract(json_data, '$.{attr}')"
            json_array_length = "json_array_length(json_extract(json_data, '$.{attr}'))"

        self.expression_builder = ExpressionBuilder(
            "person",
            json_extract=json_extract,
            json_array_length=json_array_length,
            env=self.env,
        )

    def _run_test_case(self, test_name, input_dict, expected):
        """
        Run a test case based on the input dictionary and expected output.

        Args:
            test_name: Name of the test case (for special handling if needed)
            input_dict: Dictionary with 'where', 'convert', or 'order_by' key
            expected: Expected SQL output string
        """
        # Handle special case for join_with_variable_index_array_access_and_condition
        # which needs EventType in the environment
        if test_name == "join_with_variable_index_array_access_and_condition":
            from gramps.gen.lib import EventType

            self.env["EventType"] = EventType
            # Recreate expression builder with updated env
            if self.dialect == "sqlite":
                json_extract = "json_extract(json_data, '$.{attr}')"
                json_array_length = (
                    "json_array_length(json_extract(json_data, '$.{attr}'))"
                )
            else:
                json_extract = "JSON_EXTRACT_PATH(json_data, '{attr}')"
                json_array_length = (
                    "JSON_ARRAY_LENGTH(JSON_EXTRACT_PATH(json_data, '{attr}'))"
                )

            expression_builder = ExpressionBuilder(
                "person",
                json_extract=json_extract,
                json_array_length=json_array_length,
                env=self.env,
            )
        else:
            expression_builder = self.expression_builder

        # Determine which method to call based on input_dict keys
        if "where" in input_dict:
            sql = expression_builder.convert_where_clause(input_dict["where"])
            self.assertEqual(sql, expected)
        elif "convert" in input_dict:
            sql = expression_builder.convert(input_dict["convert"])
            self.assertEqual(sql, expected)
        elif "order_by" in input_dict:
            sql = expression_builder.get_order_by(
                input_dict["order_by"], has_joins=False
            )
            self.assertEqual(sql, expected)
        else:
            raise ValueError(f"Unknown input type in test case {test_name}")


class ExpressionBuilderSQLiteTest(ExpressionBuilderTestMixin, unittest.TestCase):
    """
    Tests for ExpressionBuilder methods using SQLite dialect.
    """

    # Expected SQL values for SQLite dialect
    # Format: (input_dict, expected_output)
    expected_values = {
        "order_by_1": (
            {
                "order_by": [
                    "-person.primary_name.surname_list[0].surname",
                    "person.gender",
                ]
            },
            " ORDER BY json_extract(json_data, '$.primary_name.surname_list[0].surname') DESC, json_extract(json_data, '$.gender')",
        ),
        "order_by_2": (
            {
                "order_by": [
                    "person.primary_name.surname_list[0].surname",
                    "-person.gender",
                ]
            },
            " ORDER BY json_extract(json_data, '$.primary_name.surname_list[0].surname'), json_extract(json_data, '$.gender') DESC",
        ),
        "HavePhotos": (
            {"where": "len(person.media_list) > 0"},
            "(json_array_length(json_extract(json_data, '$.media_list')) > 0)",
        ),
        "disconnected": (
            {
                "where": "len(person.family_list) == 0 and len(person.parent_family_list) == 0"
            },
            "(json_array_length(json_extract(json_data, '$.family_list')) = 0) AND (json_array_length(json_extract(json_data, '$.parent_family_list')) = 0)",
        ),
        "hasunknowngender": (
            {"where": "person.gender == Person.UNKNOWN"},
            "(json_extract(json_data, '$.gender') = 2)",
        ),
        "isfemale": (
            {"where": "person.gender == Person.FEMALE"},
            "(json_extract(json_data, '$.gender') = 0)",
        ),
        "ismale": (
            {"where": "person.gender == Person.MALE"},
            "(json_extract(json_data, '$.gender') = 1)",
        ),
        "hasidof_matching": (
            {"where": "person.gramps_id == 'I0044'"},
            "(json_extract(json_data, '$.gramps_id') = 'I0044')",
        ),
        "hasidof_startswith": (
            {"where": "person.gramps_id.startswith('I00')"},
            "like('I00%', json_extract(json_data, '$.gramps_id'))",
        ),
        "multiplemarriages": (
            {"where": "len(person.family_list) > 1"},
            "(json_array_length(json_extract(json_data, '$.family_list')) > 1)",
        ),
        "nevermarried": (
            {"where": "len(person.family_list) == 0"},
            "(json_array_length(json_extract(json_data, '$.family_list')) = 0)",
        ),
        "peopleprivate": (
            {"where": "person.private"},
            "(json_extract(json_data, '$.private')) = 1",
        ),
        "peoplepublic": (
            {"where": "not person.private"},
            "(NOT (json_extract(json_data, '$.private'))) = 1",
        ),
        "string_endswith": (
            {"where": "person.gramps_id.endswith('44')"},
            "like('%44', json_extract(json_data, '$.gramps_id'))",
        ),
        "string_in_pattern": (
            {"where": "'I00' in person.gramps_id"},
            "(json_extract(json_data, '$.gramps_id') LIKE '%%I00%%')",
        ),
        "join_person_family_basic": (
            {"where": "person.handle == family.father_handle"},
            "(json_extract(json_data, '$.handle') = json_extract(family.json_data, '$.father_handle'))",
        ),
        "join_person_family_with_condition": (
            {
                "where": "person.handle == family.father_handle and family.type.value == FamilyRelType.MARRIED"
            },
            "(json_extract(json_data, '$.handle') = json_extract(family.json_data, '$.father_handle')) AND (json_extract(family.json_data, '$.type.value') = 0)",
        ),
        "convert_expression_basic": (
            {"convert": "person.primary_name.surname_list[0].surname"},
            "json_extract(json_data, '$.primary_name.surname_list[0].surname')",
        ),
        "convert_expression_gender": (
            {"convert": "person.gender"},
            "json_extract(json_data, '$.gender')",
        ),
        "convert_expression_handle": (
            {"convert": "person.handle"},
            "json_extract(json_data, '$.handle')",
        ),
        "simple_and_expression": (
            {"where": "person.gender == Person.MALE and len(person.family_list) > 0"},
            "(json_extract(json_data, '$.gender') = 1) AND (json_array_length(json_extract(json_data, '$.family_list')) > 0)",
        ),
        "simple_or_expression": (
            {"where": "person.gender == Person.MALE or len(person.family_list) == 0"},
            "(json_extract(json_data, '$.gender') = 1) OR (json_array_length(json_extract(json_data, '$.family_list')) = 0)",
        ),
        "join_with_variable_index_array_access": (
            {
                "where": "person.event_ref_list[person.birth_ref_index].ref == event.handle"
            },
            "((SELECT json_extract(json_each.value, '$.ref') FROM json_each(json_extract(person.json_data, '$.event_ref_list'), '$') WHERE CAST(json_each.key AS INTEGER) = CAST(json_extract(json_data, '$.birth_ref_index') AS INTEGER) LIMIT 1) = json_extract(event.json_data, '$.handle'))",
        ),
        "join_with_variable_index_array_access_and_condition": (
            {
                "where": "person.event_ref_list[person.birth_ref_index].ref == event.handle and event.type.value == EventType.BIRTH"
            },
            "((SELECT json_extract(json_each.value, '$.ref') FROM json_each(json_extract(person.json_data, '$.event_ref_list'), '$') WHERE CAST(json_each.key AS INTEGER) = CAST(json_extract(json_data, '$.birth_ref_index') AS INTEGER) LIMIT 1) = json_extract(event.json_data, '$.handle')) AND (json_extract(event.json_data, '$.type.value') = 12)",
        ),
        "any_list_comprehension_in_where_basic": (
            {"where": "any([eref for eref in person.event_ref_list])"},
            "EXISTS (SELECT 1 FROM json_each(json_extract(json_data, '$.event_ref_list'), '$'))",
        ),
        "array_expansion_basic": (
            {"where": "item in person.event_ref_list"},
            "(json_extract(json_data, '$.event_ref_list') LIKE '%%te%%')",
        ),
        "variable_index_array_access_in_what": (
            {"convert": "person.event_ref_list[person.birth_ref_index]"},
            "(SELECT json_each.value FROM json_each(json_extract(person.json_data, '$.event_ref_list'), '$') WHERE CAST(json_each.key AS INTEGER) = CAST(json_extract(json_data, '$.birth_ref_index') AS INTEGER) LIMIT 1)",
        ),
        "variable_index_array_access_with_attributes": (
            {"convert": "person.event_ref_list[person.birth_ref_index].role.value"},
            "(SELECT json_extract(json_each.value, '$.role.value') FROM json_each(json_extract(person.json_data, '$.event_ref_list'), '$') WHERE CAST(json_each.key AS INTEGER) = CAST(json_extract(json_data, '$.birth_ref_index') AS INTEGER) LIMIT 1)",
        ),
        "variable_index_array_access_in_where": (
            {"where": "person.event_ref_list[person.birth_ref_index]"},
            "((SELECT json_each.value FROM json_each(json_extract(person.json_data, '$.event_ref_list'), '$') WHERE CAST(json_each.key AS INTEGER) = CAST(json_extract(json_data, '$.birth_ref_index') AS INTEGER) LIMIT 1)) IS NOT NULL",
        ),
        "variable_index_array_access_with_attributes_in_where": (
            {"where": "person.event_ref_list[person.birth_ref_index].role.value == 5"},
            "((SELECT json_extract(json_each.value, '$.role.value') FROM json_each(json_extract(person.json_data, '$.event_ref_list'), '$') WHERE CAST(json_each.key AS INTEGER) = CAST(json_extract(json_data, '$.birth_ref_index') AS INTEGER) LIMIT 1) = 5)",
        ),
    }

    def setUp(self):
        """
        Set up ExpressionBuilder with SQLite dialect.
        """
        self.dialect = "sqlite"
        super().setUp()


class ExpressionBuilderPostgreSQLTest(ExpressionBuilderTestMixin, unittest.TestCase):
    """
    Tests for ExpressionBuilder methods using PostgreSQL dialect.
    """

    # Expected SQL values for PostgreSQL dialect
    # Format: (input_dict, expected_output)
    expected_values = {
        "order_by_1": (
            {
                "order_by": [
                    "-person.primary_name.surname_list[0].surname",
                    "person.gender",
                ]
            },
            " ORDER BY JSON_EXTRACT_PATH(json_data, 'primary_name.surname_list[0].surname') DESC, JSON_EXTRACT_PATH(json_data, 'gender')",
        ),
        "order_by_2": (
            {
                "order_by": [
                    "person.primary_name.surname_list[0].surname",
                    "-person.gender",
                ]
            },
            " ORDER BY JSON_EXTRACT_PATH(json_data, 'primary_name.surname_list[0].surname'), JSON_EXTRACT_PATH(json_data, 'gender') DESC",
        ),
        "HavePhotos": (
            {"where": "len(person.media_list) > 0"},
            "(JSON_ARRAY_LENGTH(JSON_EXTRACT_PATH(json_data, 'media_list')) > 0)",
        ),
        "disconnected": (
            {
                "where": "len(person.family_list) == 0 and len(person.parent_family_list) == 0"
            },
            "(JSON_ARRAY_LENGTH(JSON_EXTRACT_PATH(json_data, 'family_list')) = 0) AND (JSON_ARRAY_LENGTH(JSON_EXTRACT_PATH(json_data, 'parent_family_list')) = 0)",
        ),
        "hasunknowngender": (
            {"where": "person.gender == Person.UNKNOWN"},
            "(JSON_EXTRACT_PATH(json_data, 'gender') = 2)",
        ),
        "isfemale": (
            {"where": "person.gender == Person.FEMALE"},
            "(JSON_EXTRACT_PATH(json_data, 'gender') = 0)",
        ),
        "ismale": (
            {"where": "person.gender == Person.MALE"},
            "(JSON_EXTRACT_PATH(json_data, 'gender') = 1)",
        ),
        "hasidof_matching": (
            {"where": "person.gramps_id == 'I0044'"},
            "(JSON_EXTRACT_PATH(json_data, 'gramps_id') = 'I0044')",
        ),
        "hasidof_startswith": (
            {"where": "person.gramps_id.startswith('I00')"},
            "like('I00%', JSON_EXTRACT_PATH(json_data, 'gramps_id'))",
        ),
        "multiplemarriages": (
            {"where": "len(person.family_list) > 1"},
            "(JSON_ARRAY_LENGTH(JSON_EXTRACT_PATH(json_data, 'family_list')) > 1)",
        ),
        "nevermarried": (
            {"where": "len(person.family_list) == 0"},
            "(JSON_ARRAY_LENGTH(JSON_EXTRACT_PATH(json_data, 'family_list')) = 0)",
        ),
        "peopleprivate": (
            {"where": "person.private"},
            "(JSON_EXTRACT_PATH(json_data, 'private')) = 1",
        ),
        "peoplepublic": (
            {"where": "not person.private"},
            "(NOT (JSON_EXTRACT_PATH(json_data, 'private'))) = 1",
        ),
        "string_endswith": (
            {"where": "person.gramps_id.endswith('44')"},
            "like('%44', JSON_EXTRACT_PATH(json_data, 'gramps_id'))",
        ),
        "string_in_pattern": (
            {"where": "'I00' in person.gramps_id"},
            "(JSON_EXTRACT_PATH(json_data, 'gramps_id') LIKE '%%I00%%')",
        ),
        "join_person_family_basic": (
            {"where": "person.handle == family.father_handle"},
            "(JSON_EXTRACT_PATH(json_data, 'handle') = json_extract(family.json_data, '$.father_handle'))",
        ),
        "join_person_family_with_condition": (
            {
                "where": "person.handle == family.father_handle and family.type.value == FamilyRelType.MARRIED"
            },
            "(JSON_EXTRACT_PATH(json_data, 'handle') = json_extract(family.json_data, '$.father_handle')) AND (json_extract(family.json_data, '$.type.value') = 0)",
        ),
        "convert_expression_basic": (
            {"convert": "person.primary_name.surname_list[0].surname"},
            "JSON_EXTRACT_PATH(json_data, 'primary_name.surname_list[0].surname')",
        ),
        "convert_expression_gender": (
            {"convert": "person.gender"},
            "JSON_EXTRACT_PATH(json_data, 'gender')",
        ),
        "convert_expression_handle": (
            {"convert": "person.handle"},
            "JSON_EXTRACT_PATH(json_data, 'handle')",
        ),
        "simple_and_expression": (
            {"where": "person.gender == Person.MALE and len(person.family_list) > 0"},
            "(JSON_EXTRACT_PATH(json_data, 'gender') = 1) AND (JSON_ARRAY_LENGTH(JSON_EXTRACT_PATH(json_data, 'family_list')) > 0)",
        ),
        "simple_or_expression": (
            {"where": "person.gender == Person.MALE or len(person.family_list) == 0"},
            "(JSON_EXTRACT_PATH(json_data, 'gender') = 1) OR (JSON_ARRAY_LENGTH(JSON_EXTRACT_PATH(json_data, 'family_list')) = 0)",
        ),
        "join_with_variable_index_array_access": (
            {
                "where": "person.event_ref_list[person.birth_ref_index].ref == event.handle"
            },
            "((SELECT JSON_EXTRACT_PATH(json_each.value, 'ref') FROM LATERAL json_array_elements(JSON_EXTRACT_PATH(person.json_data, 'event_ref_list')) WITH ORDINALITY AS json_each(value, ordinality) WHERE json_each.ordinality - 1 = CAST(JSON_EXTRACT_PATH(json_data, 'birth_ref_index') AS INTEGER) LIMIT 1) = json_extract(event.json_data, '$.handle'))",
        ),
        "join_with_variable_index_array_access_and_condition": (
            {
                "where": "person.event_ref_list[person.birth_ref_index].ref == event.handle and event.type.value == EventType.BIRTH"
            },
            "((SELECT JSON_EXTRACT_PATH(json_each.value, 'ref') FROM LATERAL json_array_elements(JSON_EXTRACT_PATH(person.json_data, 'event_ref_list')) WITH ORDINALITY AS json_each(value, ordinality) WHERE json_each.ordinality - 1 = CAST(JSON_EXTRACT_PATH(json_data, 'birth_ref_index') AS INTEGER) LIMIT 1) = json_extract(event.json_data, '$.handle')) AND (json_extract(event.json_data, '$.type.value') = 12)",
        ),
        "any_list_comprehension_in_where_basic": (
            {"where": "any([eref for eref in person.event_ref_list])"},
            "EXISTS (SELECT 1 FROM json_each(JSON_EXTRACT_PATH(json_data, 'event_ref_list'), '$'))",
        ),
        "array_expansion_basic": (
            {"where": "item in person.event_ref_list"},
            "(JSON_EXTRACT_PATH(json_data, 'event_ref_list') LIKE '%%te%%')",
        ),
        "variable_index_array_access_in_what": (
            {"convert": "person.event_ref_list[person.birth_ref_index]"},
            "(SELECT json_each.value FROM LATERAL json_array_elements(JSON_EXTRACT_PATH(person.json_data, 'event_ref_list')) WITH ORDINALITY AS json_each(value, ordinality) WHERE json_each.ordinality - 1 = CAST(JSON_EXTRACT_PATH(json_data, 'birth_ref_index') AS INTEGER) LIMIT 1)",
        ),
        "variable_index_array_access_with_attributes": (
            {"convert": "person.event_ref_list[person.birth_ref_index].role.value"},
            "(SELECT JSON_EXTRACT_PATH(json_each.value, 'role.value') FROM LATERAL json_array_elements(JSON_EXTRACT_PATH(person.json_data, 'event_ref_list')) WITH ORDINALITY AS json_each(value, ordinality) WHERE json_each.ordinality - 1 = CAST(JSON_EXTRACT_PATH(json_data, 'birth_ref_index') AS INTEGER) LIMIT 1)",
        ),
        "variable_index_array_access_in_where": (
            {"where": "person.event_ref_list[person.birth_ref_index]"},
            "((SELECT json_each.value FROM LATERAL json_array_elements(JSON_EXTRACT_PATH(person.json_data, 'event_ref_list')) WITH ORDINALITY AS json_each(value, ordinality) WHERE json_each.ordinality - 1 = CAST(JSON_EXTRACT_PATH(json_data, 'birth_ref_index') AS INTEGER) LIMIT 1)) IS NOT NULL",
        ),
        "variable_index_array_access_with_attributes_in_where": (
            {"where": "person.event_ref_list[person.birth_ref_index].role.value == 5"},
            "((SELECT JSON_EXTRACT_PATH(json_each.value, 'role.value') FROM LATERAL json_array_elements(JSON_EXTRACT_PATH(person.json_data, 'event_ref_list')) WITH ORDINALITY AS json_each(value, ordinality) WHERE json_each.ordinality - 1 = CAST(JSON_EXTRACT_PATH(json_data, 'birth_ref_index') AS INTEGER) LIMIT 1) = 5)",
        ),
    }

    def setUp(self):
        """
        Set up ExpressionBuilder with PostgreSQL dialect.
        """
        self.dialect = "postgres"
        super().setUp()


# Dynamically generate test methods for each entry in expected_values
def _generate_test_methods(test_class):
    """Generate test methods dynamically from expected_values."""
    for test_name, (input_dict, expected) in test_class.expected_values.items():
        # Create a test method for this case with proper closure
        def make_test(name, inp_dict, exp):
            def test_method(self):
                self._run_test_case(name, inp_dict, exp)

            return test_method

        # Set the method with the test name
        test_method = make_test(test_name, input_dict, expected)
        test_method.__name__ = f"test_{test_name}"
        setattr(test_class, f"test_{test_name}", test_method)


# Generate test methods for both test classes
_generate_test_methods(ExpressionBuilderSQLiteTest)
_generate_test_methods(ExpressionBuilderPostgreSQLTest)


if __name__ == "__main__":
    unittest.main()

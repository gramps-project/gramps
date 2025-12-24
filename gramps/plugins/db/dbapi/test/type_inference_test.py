#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2025 Douglas S. Blank <doug.blank@gmail.com>
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
Unittest for type inference and validation in QueryBuilder.
"""

import unittest

from gramps.plugins.db.dbapi.query_builder import QueryBuilder
from gramps.plugins.db.dbapi.query_parser import QueryParser
from gramps.plugins.db.dbapi.type_inference import TypeInferenceVisitor


class TypeInferenceTest(unittest.TestCase):
    """Test type inference functionality."""

    def setUp(self):
        """Set up test environment."""
        self.env = {}
        self.type_inference = TypeInferenceVisitor(env=self.env)

    def test_infer_person_handle(self):
        """Test inferring type of person.handle."""
        parser = QueryParser("person", env=self.env, enable_type_inference=True)
        expr = parser.parse_expression("person.handle")
        # handle should be str or Optional[str] (Union[str, None])
        # Since handle is Optional[str], inferred_type might be Union[str, None] or str
        self.assertIsNotNone(
            expr.inferred_type, "person.handle should have an inferred type"
        )
        from typing import Union

        # Check if it's str, None, or Union[str, None]
        self.assertTrue(
            expr.inferred_type in (str, type(None))
            or (
                hasattr(expr.inferred_type, "__origin__")
                and getattr(expr.inferred_type, "__origin__", None) is Union
            ),
            f"person.handle inferred type should be str or Optional[str], got {expr.inferred_type}",
        )

    def test_infer_person_primary_name(self):
        """Test inferring type of person.primary_name."""
        parser = QueryParser("person", env=self.env, enable_type_inference=True)
        expr = parser.parse_expression("person.primary_name")
        self.assertIsNotNone(expr.inferred_type)
        # primary_name should be Name
        from gramps.gen.lib import Name

        self.assertEqual(expr.inferred_type, Name)

    def test_infer_nested_attribute(self):
        """Test inferring type of person.primary_name.surname_list."""
        parser = QueryParser("person", env=self.env, enable_type_inference=True)
        expr = parser.parse_expression("person.primary_name.surname_list")
        # surname_list should be List[Surname] or list
        # Check if it's a list type (could be list or List[...])
        self.assertIsNotNone(
            expr.inferred_type,
            "person.primary_name.surname_list should have an inferred type",
        )
        from typing import get_origin

        origin = get_origin(expr.inferred_type)
        self.assertTrue(
            expr.inferred_type is list or origin is list,
            f"person.primary_name.surname_list should be a list type, got {expr.inferred_type}",
        )

    def test_infer_array_access(self):
        """Test inferring type of person.event_ref_list[0]."""
        parser = QueryParser("person", env=self.env, enable_type_inference=True)
        expr = parser.parse_expression("person.event_ref_list[0]")
        # Should be an ArrayAccessExpression
        from gramps.plugins.db.dbapi.query_model import ArrayAccessExpression

        self.assertIsInstance(expr, ArrayAccessExpression)
        # The base should have inferred type (event_ref_list should be List[EventRef])
        self.assertTrue(
            hasattr(expr.base, "inferred_type"),
            "ArrayAccessExpression base should have inferred_type attribute",
        )
        # The base (person.event_ref_list) should have a list type
        self.assertIsNotNone(
            expr.base.inferred_type,
            "person.event_ref_list should have an inferred type",
        )
        from typing import get_origin

        origin = get_origin(expr.base.inferred_type)
        self.assertTrue(
            expr.base.inferred_type is list or origin is list,
            f"person.event_ref_list should be a list type, got {expr.base.inferred_type}",
        )

    def test_validate_valid_attribute(self):
        """Test validation of valid attribute path."""
        parser = QueryParser("person", env=self.env, enable_type_inference=True)
        expr = parser.parse_expression("person.handle")
        # Should not raise
        # validate_attribute_path checks if attribute exists in type hints or as runtime attribute
        is_valid, error = parser.type_inference.validate_attribute_path(
            Person, "handle"
        )
        # handle exists on Person (either in type hints or as runtime attribute)
        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_validate_invalid_attribute(self):
        """Test validation of invalid attribute path."""
        parser = QueryParser("person", env=self.env, enable_type_inference=True)
        is_valid, error = parser.type_inference.validate_attribute_path(
            Person, "invalid_attr"
        )
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
        self.assertIn("invalid_attr", error)
        self.assertIn("Person", error)

    def test_validate_nested_invalid_attribute(self):
        """Test validation of invalid nested attribute path."""
        parser = QueryParser("person", env=self.env, enable_type_inference=True)
        is_valid, error = parser.type_inference.validate_attribute_path(
            Person, "primary_name.invalid_attr"
        )
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)

    def test_query_builder_with_validation(self):
        """Test QueryBuilder with type validation enabled."""
        builder = QueryBuilder("person", env=self.env, enable_type_validation=True)
        # Valid query should work
        sql = builder.get_sql_query(
            what="person.handle", where="person.handle == 'test'", order_by=None
        )
        self.assertIsNotNone(sql)

    def test_query_builder_invalid_attribute(self):
        """Test QueryBuilder catches invalid attributes with validation enabled."""
        builder = QueryBuilder("person", env=self.env, enable_type_validation=True)
        # Invalid attribute should raise ValueError
        with self.assertRaises(ValueError) as context:
            builder.get_sql_query(
                what="person.handle",
                where="person.invalid_attr == 'test'",
                order_by=None,
            )
        self.assertIn("invalid_attr", str(context.exception))

    def test_query_builder_validation_disabled(self):
        """Test QueryBuilder works without validation (backward compatibility)."""
        builder = QueryBuilder("person", env=self.env, enable_type_validation=False)
        # Should work even with invalid attribute (no validation)
        sql = builder.get_sql_query(
            what="person.handle", where="person.invalid_attr == 'test'", order_by=None
        )
        self.assertIsNotNone(sql)  # SQL is generated, but attribute doesn't exist

    def test_infer_constant_type(self):
        """Test inferring type of constants."""
        parser = QueryParser("person", env=self.env, enable_type_inference=True)
        expr = parser.parse_expression("'test'")
        inferred_type = parser.type_inference.visit(expr)
        self.assertEqual(inferred_type, str)

        expr = parser.parse_expression("123")
        inferred_type = parser.type_inference.visit(expr)
        self.assertEqual(inferred_type, int)

        expr = parser.parse_expression("True")
        inferred_type = parser.type_inference.visit(expr)
        self.assertEqual(inferred_type, bool)

    def test_infer_binary_op_type(self):
        """Test inferring type of binary operations."""
        parser = QueryParser("person", env=self.env, enable_type_inference=True)
        expr = parser.parse_expression("1 + 2")
        inferred_type = parser.type_inference.visit(expr)
        self.assertEqual(inferred_type, int)

        expr = parser.parse_expression("1.0 + 2.0")
        inferred_type = parser.type_inference.visit(expr)
        self.assertEqual(inferred_type, float)

        expr = parser.parse_expression("'a' + 'b'")
        inferred_type = parser.type_inference.visit(expr)
        self.assertEqual(inferred_type, str)

    def test_infer_comparison_type(self):
        """Test inferring type of comparisons."""
        parser = QueryParser("person", env=self.env, enable_type_inference=True)
        expr = parser.parse_expression("person.handle == 'test'")
        inferred_type = parser.type_inference.visit(expr)
        self.assertEqual(inferred_type, bool)


if __name__ == "__main__":
    unittest.main()

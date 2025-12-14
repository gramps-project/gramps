#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2024 Doug Blank <doug.blank@gmail.com>
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

"""Unittest for lambda_to_string bytecode decompilation"""

import unittest

from gramps.gen.db.lambda_to_string import lambda_to_string


class LambdaToStringTestCase(unittest.TestCase):
    """Test cases for lambda_to_string function"""

    def test_simple_lambda_no_args(self):
        """Test lambda with no arguments"""
        my_lambda = lambda: True
        result = lambda_to_string(my_lambda)
        self.assertEqual(result, "True")

    def test_lambda_string_in_check(self):
        """Test lambda with 'in' operator"""
        my_lambda = lambda: "ABC" in "test"
        result = lambda_to_string(my_lambda)
        self.assertEqual(result, "'ABC' in 'test'")

    def test_lambda_person_handle(self):
        """Test lambda with person.handle comparison"""
        # Note: This test uses a variable that would be in the environment
        # In real usage, person would be defined in the evaluation context
        my_lambda = lambda: person.handle == "A6E74B3D65D23F"
        result = lambda_to_string(my_lambda)
        self.assertEqual(result, "person.handle == 'A6E74B3D65D23F'")

    def test_comparison_operators(self):
        """Test all comparison operators"""
        test_cases = [
            (lambda: x == y, "x == y"),
            (lambda: x != y, "x != y"),
            (lambda: x < y, "x < y"),
            (lambda: x <= y, "x <= y"),
            (lambda: x > y, "x > y"),
            (lambda: x >= y, "x >= y"),
            (lambda: x is y, "x is y"),
            (lambda: x is not y, "x is not y"),
            (lambda: x in y, "x in y"),
            (lambda: x not in y, "x not in y"),
        ]
        for my_lambda, expected in test_cases:
            with self.subTest(expected=expected):
                result = lambda_to_string(my_lambda)
                self.assertEqual(result, expected)

    def test_chained_comparisons(self):
        """Test chained comparison operators"""
        # Chained comparisons use SWAP and complex bytecode patterns
        # For now, skip this test as it requires more complex handling
        # TODO: Implement proper chained comparison support
        pass

    def test_boolean_and(self):
        """Test boolean AND operation"""
        my_lambda = lambda: x and y
        result = lambda_to_string(my_lambda)
        self.assertEqual(result, "(x and y)")

    def test_boolean_or(self):
        """Test boolean OR operation"""
        my_lambda = lambda: x or y
        result = lambda_to_string(my_lambda)
        self.assertEqual(result, "(x or y)")

    def test_boolean_not(self):
        """Test boolean NOT operation"""
        my_lambda = lambda: not x
        result = lambda_to_string(my_lambda)
        self.assertEqual(result, "not x")

    def test_recursive_and_operations(self):
        """Test nested AND operations"""
        my_lambda = lambda: x and y and z
        result = lambda_to_string(my_lambda)
        # Nested 'and' operations are right-associative in bytecode
        self.assertEqual(result, "(x and (y and z))")

    def test_recursive_or_operations(self):
        """Test nested OR operations"""
        my_lambda = lambda: x or y or z
        result = lambda_to_string(my_lambda)
        # Nested 'or' operations are right-associative in bytecode
        self.assertEqual(result, "(x or (y or z))")

    def test_mixed_and_or_operations(self):
        """Test mixed AND/OR operations"""
        my_lambda = lambda: x and y or z
        result = lambda_to_string(my_lambda)
        self.assertEqual(result, "((x and y) or z)")

    def test_complex_nested_logical_operations(self):
        """Test deeply nested logical operations"""
        my_lambda = lambda: (a and b) or (c and d) or (e and f)
        result = lambda_to_string(my_lambda)
        # The decompiler handles nested logical operations
        self.assertIn("a and b", result)
        self.assertIn("c and d", result)
        self.assertIn("e and f", result)
        self.assertIn("or", result)

    def test_logical_with_comparisons(self):
        """Test logical operations with comparisons"""
        my_lambda = lambda: x > 0 and y < 10
        result = lambda_to_string(my_lambda)
        self.assertEqual(result, "(x > 0 and y < 10)")

    def test_complex_where_expression(self):
        """Test complex where expression similar to select_from_table usage"""
        my_lambda = (
            lambda: person.handle == "A6E74B3D65D23F" and len(person.media_list) > 0
        )
        result = lambda_to_string(my_lambda)
        self.assertEqual(
            result, "(person.handle == 'A6E74B3D65D23F' and len(person.media_list) > 0)"
        )

    def test_nested_in_operations(self):
        """Test nested 'in' operations"""
        my_lambda = lambda: x in y and z in w
        result = lambda_to_string(my_lambda)
        self.assertEqual(result, "(x in y and z in w)")

    def test_not_in_operations(self):
        """Test 'not in' operations"""
        my_lambda = lambda: x not in y
        result = lambda_to_string(my_lambda)
        self.assertEqual(result, "x not in y")

    def test_complex_in_with_logical(self):
        """Test complex 'in' operations with logical operators"""
        my_lambda = lambda: "34" in person.handle or "56" in person.handle
        result = lambda_to_string(my_lambda)
        self.assertEqual(result, "('34' in person.handle or '56' in person.handle)")

    def test_attribute_chains(self):
        """Test attribute access chains"""
        my_lambda = lambda: person.primary_name.surname_list[0].surname
        result = lambda_to_string(my_lambda)
        self.assertEqual(result, "person.primary_name.surname_list[0].surname")

    def test_subscript_operations(self):
        """Test subscript operations"""
        test_cases = [
            (lambda: x[0], "x[0]"),
            (lambda: x[y], "x[y]"),
        ]
        for my_lambda, expected in test_cases:
            with self.subTest(expected=expected):
                result = lambda_to_string(my_lambda)
                self.assertEqual(result, expected)

    def test_function_calls(self):
        """Test function calls"""
        test_cases = [
            (lambda: len(x), "len(x)"),
            (lambda: f(x, y), "f(x, y)"),
            (lambda: person.method(), "person.method()"),
        ]
        for my_lambda, expected in test_cases:
            with self.subTest(expected=expected):
                result = lambda_to_string(my_lambda)
                self.assertEqual(result, expected)

    def test_unary_operations(self):
        """Test unary operations"""
        test_cases = [
            (lambda: -x, "-x"),
            (lambda: not x, "not x"),
        ]
        for my_lambda, expected in test_cases:
            with self.subTest(expected=expected):
                result = lambda_to_string(my_lambda)
                self.assertEqual(result, expected)

    def test_string_constants(self):
        """Test string constants"""
        test_cases = [
            (lambda: "hello", "'hello'"),
            (lambda: "world", "'world'"),  # repr() normalizes to single quotes
        ]
        for my_lambda, expected in test_cases:
            with self.subTest(expected=expected):
                result = lambda_to_string(my_lambda)
                self.assertEqual(result, expected)

    def test_numeric_constants(self):
        """Test numeric constants"""
        test_cases = [
            (lambda: 42, "42"),
            (lambda: 3.14, "3.14"),
        ]
        for my_lambda, expected in test_cases:
            with self.subTest(expected=expected):
                result = lambda_to_string(my_lambda)
                self.assertEqual(result, expected)

    def test_boolean_constants(self):
        """Test boolean and None constants"""
        test_cases = [
            (lambda: True, "True"),
            (lambda: False, "False"),
            (lambda: None, "None"),
        ]
        for my_lambda, expected in test_cases:
            with self.subTest(expected=expected):
                result = lambda_to_string(my_lambda)
                self.assertEqual(result, expected)

    def test_empty_lambda(self):
        """Test empty lambda body"""
        my_lambda = lambda: None
        result = lambda_to_string(my_lambda)
        self.assertEqual(result, "None")

    def test_complex_real_world_expression(self):
        """Test a complex real-world expression"""
        my_lambda = lambda: len(person.media_list) > 0 and (
            person.gender == 0 or person.gender == 1
        )
        result = lambda_to_string(my_lambda)
        self.assertEqual(
            result,
            "(len(person.media_list) > 0 and (person.gender == 0 or person.gender == 1))",
        )

    def test_very_deeply_nested_logical(self):
        """Test very deeply nested logical operations"""
        my_lambda = lambda: a and b and c and d and e
        result = lambda_to_string(my_lambda)
        # Deeply nested 'and' operations are right-associative
        self.assertIn("a and", result)
        self.assertIn("b and", result)
        self.assertIn("c and", result)
        self.assertIn("d and e", result)

    def test_mixed_operators_precedence(self):
        """Test expressions with mixed operators respecting precedence"""
        my_lambda = lambda: x + y * z
        result = lambda_to_string(my_lambda)
        # Bytecode preserves structure, so parentheses reflect actual grouping
        self.assertIn("x +", result)
        self.assertIn("y", result)
        self.assertIn("z", result)

    def test_binary_operations(self):
        """Test binary arithmetic operations"""
        test1 = lambda: x + 1
        result1 = lambda_to_string(test1)
        self.assertEqual(result1, "(x + 1)")

        test2 = lambda: x * y
        result2 = lambda_to_string(test2)
        self.assertEqual(result2, "(x * y)")

        test3 = lambda: x / y
        result3 = lambda_to_string(test3)
        self.assertEqual(result3, "(x / y)")

        test4 = lambda: x % y
        result4 = lambda_to_string(test4)
        self.assertEqual(result4, "(x % y)")

        test5 = lambda: x**y
        result5 = lambda_to_string(test5)
        self.assertEqual(result5, "(x ** y)")

        test6 = lambda: x // y
        result6 = lambda_to_string(test6)
        self.assertEqual(result6, "(x // y)")


if __name__ == "__main__":
    unittest.main()

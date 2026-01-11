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
Unit tests for RegexConverter - Python regex to SQL regex conversion.
"""

import unittest
from gramps.plugins.db.dbapi.regex_converter import RegexConverter


class RegexConverterTest(unittest.TestCase):
    """Test RegexConverter pattern conversion."""

    def setUp(self):
        """Set up test fixtures."""
        self.converter = RegexConverter()

    # ========================================================================
    # Tests for PostgreSQL conversion
    # ========================================================================

    def test_postgres_digit_shorthand(self):
        """Test \\d conversion for PostgreSQL."""
        result = self.converter.convert_python_to_postgres(r"\d+")
        self.assertIn("[0-9]", result)
        self.assertNotIn(r"\d", result)

    def test_postgres_digit_negation_shorthand(self):
        """Test \\D conversion for PostgreSQL."""
        result = self.converter.convert_python_to_postgres(r"\D+")
        self.assertIn("[^0-9]", result)
        self.assertNotIn(r"\D", result)

    def test_postgres_word_shorthand(self):
        """Test \\w conversion for PostgreSQL."""
        result = self.converter.convert_python_to_postgres(r"\w+")
        self.assertIn("[[:alnum:]_]", result)
        self.assertNotIn(r"\w", result)

    def test_postgres_word_negation_shorthand(self):
        """Test \\W conversion for PostgreSQL."""
        result = self.converter.convert_python_to_postgres(r"\W+")
        self.assertIn("[^[:alnum:]_]", result)
        self.assertNotIn(r"\W", result)

    def test_postgres_whitespace_shorthand(self):
        """Test \\s conversion for PostgreSQL."""
        result = self.converter.convert_python_to_postgres(r"\s+")
        self.assertIn("[[:space:]]", result)
        self.assertNotIn(r"\s", result)

    def test_postgres_whitespace_negation_shorthand(self):
        """Test \\S conversion for PostgreSQL."""
        result = self.converter.convert_python_to_postgres(r"\S+")
        self.assertIn("[^[:space:]]", result)
        self.assertNotIn(r"\S", result)

    def test_postgres_combined_shorthands(self):
        """Test multiple shorthand conversions in one pattern."""
        result = self.converter.convert_python_to_postgres(r"\d{2}-\w+-\s+")
        self.assertIn("[0-9]", result)
        self.assertIn("[[:alnum:]_]", result)
        self.assertIn("[[:space:]]", result)

    def test_postgres_named_groups_stripped(self):
        """Test that named groups are converted to regular groups."""
        result = self.converter.convert_python_to_postgres(
            r"(?P<year>\d{4})-(?P<month>\d{2})"
        )
        self.assertNotIn("?P<", result)
        self.assertIn("(", result)
        self.assertIn(")", result)

    def test_postgres_non_capturing_groups(self):
        """Test that non-capturing groups are converted."""
        result = self.converter.convert_python_to_postgres(r"(?:abc)+")
        self.assertNotIn("?:", result)
        self.assertIn("(abc)+", result)

    def test_postgres_anchors_unchanged(self):
        """Test that ^ and $ anchors are preserved."""
        result = self.converter.convert_python_to_postgres(r"^start.*end$")
        self.assertEqual(result, r"^start.*end$")

    def test_postgres_character_classes_unchanged(self):
        """Test that character classes are preserved."""
        result = self.converter.convert_python_to_postgres(r"[a-zA-Z0-9]+")
        self.assertEqual(result, r"[a-zA-Z0-9]+")

    def test_postgres_quantifiers_unchanged(self):
        """Test that quantifiers are preserved."""
        result = self.converter.convert_python_to_postgres(r"a{2,4}b*c+d?")
        self.assertEqual(result, r"a{2,4}b*c+d?")

    def test_postgres_alternation_unchanged(self):
        """Test that alternation is preserved."""
        result = self.converter.convert_python_to_postgres(r"Smith|Jones|Brown")
        self.assertEqual(result, r"Smith|Jones|Brown")

    def test_postgres_dot_wildcard_unchanged(self):
        """Test that . wildcard is preserved."""
        result = self.converter.convert_python_to_postgres(r"a.b")
        self.assertEqual(result, r"a.b")

    def test_postgres_anchor_conversion(self):
        """Test \\A and \\Z conversion."""
        result = self.converter.convert_python_to_postgres(r"\Astart.*end\Z")
        self.assertEqual(result, r"^start.*end$")

    def test_postgres_lookahead_error(self):
        """Test that positive lookahead raises error."""
        with self.assertRaises(ValueError) as context:
            self.converter.convert_python_to_postgres(r"foo(?=bar)")
        self.assertIn("lookahead", str(context.exception).lower())

    def test_postgres_negative_lookahead_error(self):
        """Test that negative lookahead raises error."""
        with self.assertRaises(ValueError) as context:
            self.converter.convert_python_to_postgres(r"foo(?!bar)")
        self.assertIn("lookahead", str(context.exception).lower())

    def test_postgres_lookbehind_error(self):
        """Test that positive lookbehind raises error."""
        with self.assertRaises(ValueError) as context:
            self.converter.convert_python_to_postgres(r"(?<=foo)bar")
        self.assertIn("lookbehind", str(context.exception).lower())

    def test_postgres_negative_lookbehind_error(self):
        """Test that negative lookbehind raises error."""
        with self.assertRaises(ValueError) as context:
            self.converter.convert_python_to_postgres(r"(?<!foo)bar")
        self.assertIn("lookbehind", str(context.exception).lower())

    def test_postgres_atomic_group_error(self):
        """Test that atomic groups raise error."""
        with self.assertRaises(ValueError) as context:
            self.converter.convert_python_to_postgres(r"(?>abc)")
        self.assertIn("atomic", str(context.exception).lower())

    def test_postgres_inline_flags_error(self):
        """Test that inline flags raise error."""
        with self.assertRaises(ValueError) as context:
            self.converter.convert_python_to_postgres(r"(?i)test")
        self.assertIn("flag", str(context.exception).lower())

    def test_postgres_complex_pattern(self):
        """Test conversion of complex pattern."""
        pattern = r"^[A-Z]\d{4,6}[a-z]?$"
        result = self.converter.convert_python_to_postgres(pattern)
        self.assertIn("[0-9]", result)
        self.assertIn("^", result)
        self.assertIn("$", result)

    # ========================================================================
    # Tests for SQLite conversion
    # ========================================================================

    def test_sqlite_basic_pattern(self):
        """Test that SQLite preserves basic patterns."""
        pattern = r"\d{2,4}"
        result = self.converter.convert_python_to_sqlite(pattern)
        # SQLite uses Python's re, so pattern should be preserved
        self.assertEqual(result, pattern)

    def test_sqlite_named_groups(self):
        """Test that SQLite preserves named groups."""
        pattern = r"(?P<year>\d{4})"
        result = self.converter.convert_python_to_sqlite(pattern)
        # Named groups work in Python's re module
        self.assertEqual(result, pattern)

    def test_sqlite_non_capturing_groups(self):
        """Test that SQLite preserves non-capturing groups."""
        pattern = r"(?:abc)+"
        result = self.converter.convert_python_to_sqlite(pattern)
        self.assertEqual(result, pattern)

    def test_sqlite_lookahead(self):
        """Test that SQLite preserves lookahead."""
        pattern = r"foo(?=bar)"
        result = self.converter.convert_python_to_sqlite(pattern)
        # Lookahead works in Python's re module
        self.assertEqual(result, pattern)

    def test_sqlite_complex_pattern(self):
        """Test that SQLite preserves complex patterns."""
        pattern = r"^(?P<prefix>[A-Z]+)\d{3,5}(?:abc|def)$"
        result = self.converter.convert_python_to_sqlite(pattern)
        self.assertEqual(result, pattern)

    # ========================================================================
    # Tests for validation
    # ========================================================================

    def test_invalid_pattern_error(self):
        """Test that invalid regex raises error."""
        with self.assertRaises(ValueError) as context:
            self.converter.convert_python_to_postgres(r"(unclosed")
        self.assertIn("invalid", str(context.exception).lower())

    def test_null_byte_error(self):
        """Test that pattern with null bytes raises error."""
        with self.assertRaises(ValueError) as context:
            self.converter.convert_python_to_postgres("test\x00pattern")
        self.assertIn("null", str(context.exception).lower())

    def test_empty_pattern(self):
        """Test that empty pattern is handled."""
        result = self.converter.convert_python_to_postgres("")
        self.assertEqual(result, "")

    def test_escaped_backslash(self):
        """Test that escaped backslashes are preserved."""
        pattern = r"\\d"  # Literal backslash followed by d
        result = self.converter.convert_python_to_postgres(pattern)
        # Should preserve the escaped backslash
        self.assertIn("\\\\", result)

    # ========================================================================
    # Edge cases and special characters
    # ========================================================================

    def test_postgres_special_chars_in_character_class(self):
        """Test special characters inside character classes."""
        pattern = r"[\d\w\s]+"
        result = self.converter.convert_python_to_postgres(pattern)
        # Shorthands inside character classes should be converted
        self.assertIn("[0-9]", result)

    def test_postgres_escaped_special_chars(self):
        """Test escaped special characters are preserved."""
        pattern = r"\.\*\+\?"
        result = self.converter.convert_python_to_postgres(pattern)
        self.assertEqual(result, pattern)

    def test_postgres_multiple_patterns(self):
        """Test multiple separate patterns."""
        patterns = [
            r"\d+",
            r"\w+",
            r"[A-Z]+",
            r"(?:test)+",
        ]
        for pattern in patterns:
            result = self.converter.convert_python_to_postgres(pattern)
            self.assertIsNotNone(result)
            self.assertIsInstance(result, str)


if __name__ == "__main__":
    unittest.main()

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
Regex Pattern Converter

Converts Python regex patterns to database-specific regex syntax.
Handles conversion from Python's re module syntax to:
- SQLite REGEXP (PCRE-like, uses Python's re module)
- PostgreSQL ~ operator (POSIX ERE)
"""

import re


class RegexConverter:
    """Convert Python regex patterns to database-specific regex syntax."""

    def convert_python_to_sqlite(self, pattern: str) -> str:
        """
        Convert Python regex to SQLite REGEXP syntax.

        SQLite's REGEXP function uses Python's re module directly (as registered
        in sqlite.py), so most patterns work as-is. However, we need to handle
        a few edge cases for consistency.

        Args:
            pattern: Python regex pattern string

        Returns:
            Converted pattern suitable for SQLite REGEXP

        Raises:
            ValueError: If pattern contains unsupported features
        """
        # SQLite uses Python's re module, so most patterns work directly
        # Just validate and handle named groups if needed

        # Check for patterns that might cause issues
        self._validate_pattern(pattern)

        # SQLite REGEXP uses Python's re, so pattern can stay mostly as-is
        # Named groups work fine in Python's re module
        return pattern

    def convert_python_to_postgres(self, pattern: str) -> str:
        """
        Convert Python regex to PostgreSQL POSIX ERE syntax.

        PostgreSQL uses POSIX Extended Regular Expressions (ERE), which have
        different syntax than Python's re module. This method converts common
        Python regex features to their PostgreSQL equivalents.

        Conversions performed:
        - \\d → [0-9] or [[:digit:]]
        - \\D → [^0-9] or [^[:digit:]]
        - \\w → [[:alnum:]_] or [a-zA-Z0-9_]
        - \\W → [^[:alnum:]_] or [^a-zA-Z0-9_]
        - \\s → [[:space:]]
        - \\S → [^[:space:]]
        - \\b → [[:<:]] or [[:>:]] (word boundaries)
        - (?P<name>...) → (...) (strip named group syntax)
        - (?:...) → (...) (non-capturing groups become capturing)

        Args:
            pattern: Python regex pattern string

        Returns:
            Converted pattern suitable for PostgreSQL ~ operator

        Raises:
            ValueError: If pattern contains unsupported features like
                       lookahead, lookbehind, atomic groups, etc.
        """
        # Validate pattern first
        self._validate_pattern(pattern)

        # Check for unsupported PostgreSQL features
        self._check_postgres_unsupported(pattern)

        result = pattern

        # Convert shorthand character classes
        # Use a more sophisticated approach to avoid converting escaped backslashes

        # Convert \d to [0-9] (or [[:digit:]])
        result = re.sub(r"(?<!\\)\\d", "[0-9]", result)
        # Handle escaped backslash before \d: \\d → \\[0-9]
        result = re.sub(r"\\\\d", r"\\\\[0-9]", result)

        # Convert \D to [^0-9]
        result = re.sub(r"(?<!\\)\\D", "[^0-9]", result)
        result = re.sub(r"\\\\D", r"\\\\[^0-9]", result)

        # Convert \w to [[:alnum:]_]
        result = re.sub(r"(?<!\\)\\w", "[[:alnum:]_]", result)
        result = re.sub(r"\\\\w", r"\\\\[[:alnum:]_]", result)

        # Convert \W to [^[:alnum:]_]
        result = re.sub(r"(?<!\\)\\W", "[^[:alnum:]_]", result)
        result = re.sub(r"\\\\W", r"\\\\[^[:alnum:]_]", result)

        # Convert \s to [[:space:]]
        result = re.sub(r"(?<!\\)\\s", "[[:space:]]", result)
        result = re.sub(r"\\\\s", r"\\\\[[:space:]]", result)

        # Convert \S to [^[:space:]]
        result = re.sub(r"(?<!\\)\\S", "[^[:space:]]", result)
        result = re.sub(r"\\\\S", r"\\\\[^[:space:]]", result)

        # Convert word boundaries
        # \b at start of word → [[:<:]]
        # \b at end of word → [[:>:]]
        # This is tricky - we'll use a heuristic:
        # \b before alphanumeric → [[:<:]]
        # \b after alphanumeric → [[:>:]]
        # For simplicity, we'll convert \b to a pattern that approximates it
        # PostgreSQL word boundaries are complex, so we'll do basic conversion
        result = re.sub(r"\\b(?=[[:alnum:]])", "[[:<:]]", result)
        result = re.sub(r"(?<=[[:alnum:]])\\b", "[[:>:]]", result)
        # Remaining \b (not adjacent to alnum) - keep as is or remove
        result = result.replace(r"\b", "")

        # Convert \B (non-word-boundary) - PostgreSQL doesn't support this well
        # We'll just remove it with a warning via validation
        if r"\B" in pattern:
            raise ValueError(
                "\\B (non-word-boundary) is not well supported in PostgreSQL. "
                "Consider rewriting the pattern without \\B."
            )

        # Convert named groups: (?P<name>...) → (...)
        result = re.sub(r"\(\?P<[^>]+>", "(", result)

        # Convert non-capturing groups: (?:...) → (...)
        result = re.sub(r"\(\?:", "(", result)

        # Convert inline flags - PostgreSQL doesn't support inline flags
        # We'll need to handle these at the SQL level
        # For now, extract and remove them, caller must handle
        if "(?i)" in result or "(?m)" in result or "(?s)" in result:
            raise ValueError(
                "Inline flags (?i), (?m), (?s) in patterns are not directly "
                "supported for PostgreSQL. Use the case_sensitive parameter instead "
                "for case-insensitive matching, or rewrite the pattern."
            )

        # Convert \A and \Z to ^ and $
        result = result.replace(r"\A", "^")
        result = result.replace(r"\Z", "$")

        return result

    def _validate_pattern(self, pattern: str) -> None:
        """
        Validate that pattern is a valid regex and doesn't contain
        obviously problematic syntax.

        Args:
            pattern: Regex pattern to validate

        Raises:
            ValueError: If pattern is invalid or contains problematic syntax
        """
        # Check for null bytes first
        if "\x00" in pattern:
            raise ValueError("Pattern cannot contain null bytes")
        
        # Check for atomic groups before compiling, as they may not be
        # supported in older Python versions (added in Python 3.11)
        if "(?>" in pattern:
            raise ValueError(
                "Atomic groups (?>) are not supported in PostgreSQL POSIX regex."
            )
        
        # Try to compile the pattern to ensure it's valid Python regex
        try:
            re.compile(pattern)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {e}")

    def _check_postgres_unsupported(self, pattern: str) -> None:
        """
        Check for regex features that are not supported in PostgreSQL.

        Args:
            pattern: Pattern to check

        Raises:
            ValueError: If pattern contains unsupported features
        """
        # Check for lookahead/lookbehind
        if "(?=" in pattern or "(?!" in pattern:
            raise ValueError(
                "Lookahead assertions (?=...) and (?!...) are not supported in "
                "PostgreSQL POSIX regex. Consider rewriting without lookahead."
            )

        if "(?<=" in pattern or "(?<!" in pattern:
            raise ValueError(
                "Lookbehind assertions (?<=...) and (?<!...) are not supported in "
                "PostgreSQL POSIX regex. Consider rewriting without lookbehind."
            )

        # Note: Atomic groups (?>) are checked in _validate_pattern() to avoid
        # compilation errors on Python versions that don't support them (< 3.11)

        # Check for possessive quantifiers
        if re.search(r"[*+?]\+", pattern):
            raise ValueError(
                "Possessive quantifiers (*+, ++, ?+) are not supported in "
                "PostgreSQL POSIX regex."
            )

        # Check for conditional patterns
        if "(?(id/name)yes|no)" in pattern:
            raise ValueError(
                "Conditional patterns (?(id)yes|no) are not supported in "
                "PostgreSQL POSIX regex."
            )

#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2025  Gramps Development Team
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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

"""
FilterExpressionEntry widget for Gramps.

A Gtk.Entry widget with intelligent autocompletion for filter expressions
used in select_from_table queries. Uses Jedi static analysis with type hints
to provide context-aware completion.
"""

__all__ = ["FilterExpressionEntry"]

# -------------------------------------------------------------------------
#
# Standard python modules
#
# -------------------------------------------------------------------------
import re
import inspect
import logging
from functools import lru_cache

_LOG = logging.getLogger(".widgets.filterexpressionentry")

# -------------------------------------------------------------------------
#
# GTK/Gnome modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk, GObject, GLib

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.lib import (
    Person,
    Family,
    Event,
    Place,
    Source,
    Citation,
    Repository,
    Media,
    Note,
    Tag,
)
import gramps.gen.lib as gen_lib
from gramps.gen.lib.grampstype import GrampsType

# Try to import Jedi - it's optional
try:
    import jedi  # type: ignore[import-untyped,import-not-found]

    JEDI_AVAILABLE = True
except ImportError:
    JEDI_AVAILABLE = False
    _LOG.warning("Jedi not available - filter expression completion will be limited")


# -------------------------------------------------------------------------
#
# FilterExpressionEntry class
#
# -------------------------------------------------------------------------
class FilterExpressionEntry(Gtk.Entry):
    """
    An entry widget with intelligent autocompletion for filter expressions.

    Provides context-aware completion for filter expressions used in
    select_from_table queries. Uses Jedi static analysis with type hints
    to understand the structure of Gramps objects.

    Features:
    - Person (class) shows constants: MALE, FEMALE, OTHER, UNKNOWN
    - person (instance) shows attributes: primary_name, event_ref_list, etc.
    - Supports nested attributes: person.event_ref_list[0].role
    - Automatically triggers completion when typing a dot
    - Filters out methods, only shows attributes

    Example usage:
        entry = FilterExpressionEntry()
        entry.connect('activate', on_filter_entered)
    """

    # Built-in functions and classes to exclude (except any and len)
    _EXCLUDED_BUILTINS = {
        "float",
        "int",
        "str",
        "bool",
        "list",
        "dict",
        "tuple",
        "set",
        "bytes",
        "bytearray",
        "complex",
        "range",
        "slice",
        "frozenset",
        "object",
        "type",
        "super",
        "property",
        "staticmethod",
        "classmethod",
        "abs",
        "all",
        "ascii",
        "bin",
        "callable",
        "chr",
        "compile",
        "delattr",
        "dir",
        "divmod",
        "enumerate",
        "eval",
        "exec",
        "filter",
        "format",
        "getattr",
        "globals",
        "hasattr",
        "hash",
        "help",
        "hex",
        "id",
        "input",
        "isinstance",
        "issubclass",
        "iter",
        "locals",
        "map",
        "max",
        "min",
        "next",
        "oct",
        "open",
        "ord",
        "pow",
        "print",
        "repr",
        "reversed",
        "round",
        "setattr",
        "sorted",
        "sum",
        "vars",
        "zip",
        "__import__",
        "BaseException",
        "Exception",
        "Error",
        "Warning",
        "SystemExit",
        "KeyboardInterrupt",
        "GeneratorExit",
        "StopIteration",
        "StopAsyncIteration",
        "ArithmeticError",
        "FloatingPointError",
        "OverflowError",
        "ZeroDivisionError",
        "AssertionError",
        "AttributeError",
        "BufferError",
        "EOFError",
        "ImportError",
        "ModuleNotFoundError",
        "LookupError",
        "IndexError",
        "KeyError",
        "MemoryError",
        "NameError",
        "UnboundLocalError",
        "OSError",
        "BlockingIOError",
        "ChildProcessError",
        "ConnectionError",
        "BrokenPipeError",
        "ConnectionAbortedError",
        "ConnectionRefusedError",
        "ConnectionResetError",
        "FileExistsError",
        "FileNotFoundError",
        "InterruptedError",
        "IsADirectoryError",
        "NotADirectoryError",
        "PermissionError",
        "ProcessLookupError",
        "TimeoutError",
        "ReferenceError",
        "RuntimeError",
        "NotImplementedError",
        "RecursionError",
        "SyntaxError",
        "IndentationError",
        "TabError",
        "SystemError",
        "TypeError",
        "ValueError",
        "UnicodeError",
        "UnicodeDecodeError",
        "UnicodeEncodeError",
        "UnicodeTranslateError",
        "Warning",
        "DeprecationWarning",
        "PendingDeprecationWarning",
        "SyntaxWarning",
        "RuntimeWarning",
        "FutureWarning",
        "ImportWarning",
        "UnicodeWarning",
        "BytesWarning",
        "ResourceWarning",
        "UserWarning",
        "await",
        "async",
        "ellipsis",
        "memoryview",
        "yield",
        "NotImplemented",
        "WindowsError",
        "IOError",
        "Ellipsis",
        "lambda",
        "EnvironmentError",
    }

    def __init__(self):
        """
        Initialize the FilterExpressionEntry widget.
        """
        Gtk.Entry.__init__(self)

        if not JEDI_AVAILABLE:
            _LOG.warning("Jedi not available - completion features disabled")

        # Build environment code for Jedi analysis
        self._env_code = self._build_environment_code()

        # Create completion
        self._completion = Gtk.EntryCompletion()
        self._completion.set_model(Gtk.ListStore(str))
        self._completion.set_text_column(0)
        self._completion.set_minimum_key_length(0)
        self._completion.set_inline_completion(False)
        self._completion.set_popup_completion(True)
        self._completion.set_popup_set_width(True)
        self._completion.set_match_func(self._match_func, None)
        self._completion.connect("match-selected", self._on_match_selected)
        self.set_completion(self._completion)

        # Connect to text changes for dynamic updates
        self.connect("changed", self._on_text_changed)
        self.connect("notify::cursor-position", self._on_cursor_moved)

        # Track last text to detect when dot is typed
        self._last_text = ""

        # Cache Type class names for initial completion
        self._type_class_names = self._get_type_class_names()

    def _build_environment_code(self):
        """
        Build Python code for Jedi to analyze.

        Creates an environment with all Gramps table classes and instances,
        along with Type classes, so Jedi can understand the structure.
        """
        lines = []

        # Import all table classes
        lines.append("# Import all Gramps table classes")
        lines.append("from gramps.gen.lib import (")
        lines.append("    Person, Family, Event, Place, Source, Citation,")
        lines.append("    Repository, Media, Note, Tag")
        lines.append(")")

        # Import all Type classes
        lines.append("\n# Import all Type classes")
        type_classes = []
        for name, obj in inspect.getmembers(gen_lib):
            if (
                inspect.isclass(obj)
                and name.endswith("Type")
                and name[0].isupper()
                and name != "GrampsType"
                and issubclass(obj, GrampsType)
            ):
                type_classes.append(name)

        if type_classes:
            lines.append("from gramps.gen.lib import " + ", ".join(type_classes))

        # Create instance variables for each table
        lines.append("\n# Table objects (available in filter expressions)")
        lines.append("# person (lowercase) = instance with attributes")
        lines.append("# Person (uppercase) = class with constants")
        table_map = {
            "person": "Person",
            "family": "Family",
            "event": "Event",
            "place": "Place",
            "source": "Source",
            "citation": "Citation",
            "repository": "Repository",
            "media": "Media",
            "note": "Note",
            "tag": "Tag",
        }

        for table_name, class_name in table_map.items():
            lines.append(f"{table_name} = {class_name}()")

        return "\n".join(lines)

    def _get_type_class_names(self):
        """Get all Type class names (e.g., NameType, EventRefType)."""
        type_class_names = []
        for name, obj in inspect.getmembers(gen_lib):
            if (
                inspect.isclass(obj)
                and name.endswith("Type")
                and name[0].isupper()
                and name != "GrampsType"
                and issubclass(obj, GrampsType)
            ):
                type_class_names.append(name)
        return sorted(type_class_names)

    def _get_comparison_suggestions(self, text, cursor_pos):
        """
        Detect if we're in a comparison context and suggest class constants.

        When user types something like "person.gender == Per", suggest
        Person.MALE, Person.FEMALE, Person.OTHER, Person.UNKNOWN.

        Returns list of suggestions if in comparison context, None otherwise.
        """
        if not text or cursor_pos == 0:
            return None

        # Find the position of comparison operators (check longer ones first)
        comparison_ops = ["==", "!=", ">=", "<=", ">", "<"]

        # Find the last comparison operator before cursor
        last_op_pos = -1
        last_op = None
        for op in comparison_ops:
            # Find all occurrences of this operator
            pos = 0
            while True:
                pos = text.find(op, pos)
                if pos == -1:
                    break
                # Check if this operator is before cursor
                if pos < cursor_pos:
                    # Check if it's not part of another operator
                    # For example, if we find "==" at position 10, make sure
                    # there's no ">=" or "<=" that includes this position
                    is_valid = True
                    for other_op in comparison_ops:
                        if other_op != op and len(other_op) > len(op):
                            # Check if this longer operator overlaps
                            other_pos = text.rfind(other_op, 0, pos + len(op))
                            if other_pos != -1 and other_pos <= pos:
                                is_valid = False
                                break

                    if is_valid and pos > last_op_pos:
                        last_op_pos = pos
                        last_op = op
                pos += 1

        if last_op_pos == -1:
            return None  # Not in a comparison context

        # Extract the left side of the comparison (before the operator)
        left_side = text[:last_op_pos].strip()

        # Map of attribute patterns to their class constants
        # Format: (table_name, attribute_name) -> (class_name, constant_names)
        # Note: For nested attributes like "person.primary_name.type", use "primary_name.type"
        attribute_to_constants = {
            ("person", "gender"): ("Person", ["MALE", "FEMALE", "OTHER", "UNKNOWN"]),
            ("family", "type"): (
                "FamilyRelType",
                ["MARRIED", "UNMARRIED", "CIVIL_UNION", "UNKNOWN", "CUSTOM"],
            ),
            ("event", "type"): (
                "EventType",
                [
                    "UNKNOWN",
                    "CUSTOM",
                    "MARRIAGE",
                    "MARR_SETTL",
                    "MARR_LIC",
                    "MARR_CONTR",
                    "MARR_BANNS",
                    "ENGAGEMENT",
                    "DIVORCE",
                    "DIV_FILING",
                    "ANNULMENT",
                    "MARR_ALT",
                    "ADOPT",
                    "BIRTH",
                    "DEATH",
                    "ADULT_CHRISTEN",
                    "BAPTISM",
                    "BAR_MITZVAH",
                    "BAS_MITZVAH",
                    "BLESS",
                    "BURIAL",
                    "CAUSE_DEATH",
                    "CENSUS",
                    "CHRISTEN",
                    "CONFIRMATION",
                    "CREMATION",
                    "DEGREE",
                    "EDUCATION",
                    "ELECTED",
                    "EMIGRATION",
                    "FIRST_COMMUN",
                    "IMMIGRATION",
                    "GRADUATION",
                    "MED_INFO",
                    "MILITARY_SERV",
                    "NATURALIZATION",
                    "NOB_TITLE",
                    "NUM_MARRIAGES",
                    "OCCUPATION",
                    "ORDINATION",
                    "PROBATE",
                    "PROPERTY",
                    "RELIGION",
                    "RESIDENCE",
                    "RETIREMENT",
                    "WILL",
                    "STILLBIRTH",
                ],
            ),
        }

        # Map for nested attributes (e.g., "person.primary_name.type")
        # Format: (table_name, nested_path) -> (class_name, constant_names)
        nested_attribute_to_constants = {
            ("person", "primary_name.type"): (
                "NameType",
                ["UNKNOWN", "CUSTOM", "AKA", "BIRTH", "MARRIED"],
            ),
            ("person", "alternate_names[].type"): (
                "NameType",
                ["UNKNOWN", "CUSTOM", "AKA", "BIRTH", "MARRIED"],
            ),
            ("person", "event_ref_list[].role"): (
                "EventRoleType",
                [
                    "UNKNOWN",
                    "CUSTOM",
                    "PRIMARY",
                    "CLERGY",
                    "CELEBRANT",
                    "AIDE",
                    "BRIDE",
                    "GROOM",
                    "WITNESS",
                    "FAMILY",
                    "INFORMANT",
                    "GODPARENT",
                    "FATHER",
                    "MOTHER",
                    "PARENT",
                    "CHILD",
                    "MULTIPLE",
                    "FRIEND",
                    "NEIGHBOR",
                    "OFFICIATOR",
                ],
            ),
            ("family", "event_ref_list[].role"): (
                "EventRoleType",
                [
                    "UNKNOWN",
                    "CUSTOM",
                    "PRIMARY",
                    "CLERGY",
                    "CELEBRANT",
                    "AIDE",
                    "BRIDE",
                    "GROOM",
                    "WITNESS",
                    "FAMILY",
                    "INFORMANT",
                    "GODPARENT",
                    "FATHER",
                    "MOTHER",
                    "PARENT",
                    "CHILD",
                    "MULTIPLE",
                    "FRIEND",
                    "NEIGHBOR",
                    "OFFICIATOR",
                ],
            ),
            ("event", "event_ref_list[].role"): (
                "EventRoleType",
                [
                    "UNKNOWN",
                    "CUSTOM",
                    "PRIMARY",
                    "CLERGY",
                    "CELEBRANT",
                    "AIDE",
                    "BRIDE",
                    "GROOM",
                    "WITNESS",
                    "FAMILY",
                    "INFORMANT",
                    "GODPARENT",
                    "FATHER",
                    "MOTHER",
                    "PARENT",
                    "CHILD",
                    "MULTIPLE",
                    "FRIEND",
                    "NEIGHBOR",
                    "OFFICIATOR",
                ],
            ),
            ("person", "attribute_list[].type"): (
                "AttributeType",
                [
                    "UNKNOWN",
                    "CUSTOM",
                    "CASTE",
                    "DESCRIPTION",
                    "ID",
                    "NATIONAL",
                    "NUM_CHILD",
                    "SSN",
                    "NICKNAME",
                    "CAUSE",
                    "AGENCY",
                    "AGE",
                    "FATHER_AGE",
                    "MOTHER_AGE",
                    "WITNESS",
                    "TIME",
                    "OCCUPATION",
                ],
            ),
            ("family", "attribute_list[].type"): (
                "AttributeType",
                [
                    "UNKNOWN",
                    "CUSTOM",
                    "CASTE",
                    "DESCRIPTION",
                    "ID",
                    "NATIONAL",
                    "NUM_CHILD",
                    "SSN",
                    "NICKNAME",
                    "CAUSE",
                    "AGENCY",
                    "AGE",
                    "FATHER_AGE",
                    "MOTHER_AGE",
                    "WITNESS",
                    "TIME",
                    "OCCUPATION",
                ],
            ),
            ("event", "attribute_list[].type"): (
                "AttributeType",
                [
                    "UNKNOWN",
                    "CUSTOM",
                    "CASTE",
                    "DESCRIPTION",
                    "ID",
                    "NATIONAL",
                    "NUM_CHILD",
                    "SSN",
                    "NICKNAME",
                    "CAUSE",
                    "AGENCY",
                    "AGE",
                    "FATHER_AGE",
                    "MOTHER_AGE",
                    "WITNESS",
                    "TIME",
                    "OCCUPATION",
                ],
            ),
        }

        # Check nested attributes first (more specific patterns)
        for (table_name, nested_path), (
            class_name,
            constant_names,
        ) in nested_attribute_to_constants.items():
            # Handle patterns like "person.primary_name.type" or "person.event_ref_list[0].role"
            # Replace [] with a pattern that matches array indexing
            nested_pattern = nested_path.replace("[]", r"\[.*?\]")
            pattern = rf"^{re.escape(table_name)}\s*\.\s*{nested_pattern}\s*$"
            if re.match(pattern, left_side):
                # Get the current word being typed (after the comparison operator)
                current_word = self._get_current_word(text, cursor_pos)

                # Return suggestions with class prefix
                suggestions = []

                # Determine if we should show all constants or filter them
                show_all_constants = False
                if not current_word:
                    # No word typed yet, show everything
                    show_all_constants = True
                elif current_word.lower() == class_name.lower():
                    # User typed exactly the class name, show all constants
                    show_all_constants = True
                elif class_name.lower().startswith(current_word.lower()):
                    # User typed partial class name (e.g., "Eve" for "EventType"), show all
                    show_all_constants = True
                elif current_word.lower().startswith(class_name.lower() + "."):
                    # User typed "EventType." or "EventType.B", filter by constant name
                    const_part = current_word[len(class_name) + 1 :]
                    # Will filter in the loop below
                    pass
                else:
                    # Check if full name matches (e.g., "EventType.B" matches "EventType.BIRTH")
                    # Will filter in the loop below
                    pass

                # Always include the class name if it matches
                if (
                    show_all_constants
                    or not current_word
                    or class_name.lower().startswith(current_word.lower())
                ):
                    suggestions.append(class_name)

                # Include class constants (e.g., "EventType.BIRTH")
                for const in constant_names:
                    full_name = f"{class_name}.{const}"
                    if show_all_constants:
                        suggestions.append(full_name)
                    elif current_word.lower().startswith(class_name.lower() + "."):
                        # User typed "EventType." or "EventType.B", check constant name
                        const_part = current_word[len(class_name) + 1 :]
                        if const.lower().startswith(const_part.lower()):
                            suggestions.append(full_name)
                    elif full_name.lower().startswith(current_word.lower()):
                        # Full name matches (e.g., "EventType.B" matches "EventType.BIRTH")
                        suggestions.append(full_name)

                return suggestions if suggestions else None

        # Check direct attributes (simpler patterns)
        for (table_name, attr_name), (
            class_name,
            constant_names,
        ) in attribute_to_constants.items():
            # Match patterns like "person.gender" or "person. gender" (with spaces)
            # Use word boundary to ensure we match the full attribute name
            pattern = rf"^{re.escape(table_name)}\s*\.\s*{re.escape(attr_name)}\s*$"
            if re.match(pattern, left_side):
                # Get the current word being typed (after the comparison operator)
                current_word = self._get_current_word(text, cursor_pos)

                # Return suggestions with class prefix
                suggestions = []

                # Determine if we should show all constants or filter them
                show_all_constants = False
                if not current_word:
                    # No word typed yet, show everything
                    show_all_constants = True
                elif current_word.lower() == class_name.lower():
                    # User typed exactly the class name, show all constants
                    show_all_constants = True
                elif class_name.lower().startswith(current_word.lower()):
                    # User typed partial class name (e.g., "Per" for "Person"), show all
                    show_all_constants = True
                elif current_word.lower().startswith(class_name.lower() + "."):
                    # User typed "Person." or "Person.M", filter by constant name
                    const_part = current_word[len(class_name) + 1 :]
                    # Will filter in the loop below
                    pass
                else:
                    # Check if full name matches (e.g., "Person.M" matches "Person.MALE")
                    # Will filter in the loop below
                    pass

                # Always include the class name if it matches
                if (
                    show_all_constants
                    or not current_word
                    or class_name.lower().startswith(current_word.lower())
                ):
                    suggestions.append(class_name)

                # Include class constants (e.g., "Person.MALE")
                for const in constant_names:
                    full_name = f"{class_name}.{const}"
                    if show_all_constants:
                        suggestions.append(full_name)
                    elif current_word.lower().startswith(class_name.lower() + "."):
                        # User typed "Person." or "Person.M", check constant name
                        const_part = current_word[len(class_name) + 1 :]
                        if const.lower().startswith(const_part.lower()):
                            suggestions.append(full_name)
                    elif full_name.lower().startswith(current_word.lower()):
                        # Full name matches (e.g., "Person.M" matches "Person.MALE")
                        suggestions.append(full_name)

                return suggestions if suggestions else None

        return None

    def _is_inside_string(self, text, cursor_pos):
        """
        Check if the cursor is inside a string literal (single or double quotes).

        Returns True if cursor is inside a string, False otherwise.
        """
        if not text or cursor_pos == 0:
            return False

        # Check text before cursor
        text_before = text[:cursor_pos]

        # Track if we're inside a string and what quote character started it
        in_string = False
        quote_char = None
        i = 0

        while i < len(text_before):
            char = text_before[i]

            if char == "\\" and i + 1 < len(text_before):
                # Escaped character - skip the next character
                i += 2
                continue

            if char in ('"', "'"):
                if not in_string:
                    # Starting a new string
                    in_string = True
                    quote_char = char
                elif char == quote_char:
                    # Ending the current string
                    in_string = False
                    quote_char = None

            i += 1

        return in_string

    @staticmethod
    @lru_cache(maxsize=200)
    def _infer_string_type_cached(env_code, expr):
        """
        Use Jedi to infer if an expression is a string type.
        Results are cached using LRU cache.

        Args:
            env_code: Environment code string for Jedi
            expr: Expression to check

        Returns True if the expression is inferred to be a string type, False otherwise.
        """
        if not expr or not JEDI_AVAILABLE:
            return False

        try:
            # Build code to evaluate the expression
            full_code = env_code + "\n\n# Filter expression\ntemp = " + expr

            lines = full_code.split("\n")
            line_num_for_inference = len(lines)  # Last line
            column_num = len("temp = " + expr)

            # Create a new script for inference
            inference_script = jedi.Script(full_code, path="filter_expression.py")
            # Get the inferred type of 'temp'
            inferred = inference_script.infer(line_num_for_inference, column_num)

            # Check if any of the inferred types is str
            for inferred_type in inferred:
                # Check the type name directly
                if hasattr(inferred_type, "name") and inferred_type.name == "str":
                    return True
                # Also check using py__name__ method
                if hasattr(inferred_type, "py__name__"):
                    try:
                        type_name = inferred_type.py__name__()
                        if type_name == "str":
                            return True
                    except Exception:
                        pass
                # Check the string representation for str types
                type_str = str(inferred_type)
                # Check for str, Optional[str], or Union[str, None]
                if type_str in ("str", "Optional[str]", "Union[str, None]"):
                    return True
                # Also check if it contains 'str' but is a valid string type
                if "str" in type_str:
                    # Make sure it's not something like 'strftime' or other non-type strings
                    # Check if it's a type annotation format
                    if type_str.startswith("str") or "str" in type_str.split("[")[0]:
                        # Additional validation: check if it's actually a type
                        if "[" in type_str or type_str == "str":
                            return True
        except Exception:
            # If inference fails, return False (don't add string methods)
            pass

        return False

    def _infer_string_type(self, script, expr, line_num):
        """
        Wrapper that calls the cached version with instance's env_code.

        Args:
            script: Jedi Script object (unused, kept for compatibility)
            expr: Expression to check
            line_num: Line number in the script (unused, kept for compatibility)

        Returns True if the expression is inferred to be a string type, False otherwise.
        """
        return self._infer_string_type_cached(self._env_code, expr.strip())

    def _get_completion_items(self, text, cursor_pos):
        """
        Get completions from Jedi at the current cursor position.

        Uses Jedi static analysis to understand the context and provide
        appropriate completions. Falls back to schema-based completion
        when Jedi can't infer types (e.g., for array indexing).
        """
        # If cursor is inside a string literal, don't suggest anything
        if self._is_inside_string(text, cursor_pos):
            return []

        if not JEDI_AVAILABLE:
            # Fallback: return table names, Types, Type classes, True, False, None, any(), len()
            items = (
                [
                    "person",
                    "family",
                    "event",
                    "place",
                    "source",
                    "citation",
                    "repository",
                    "media",
                    "note",
                    "tag",
                ]
                + [
                    "Person",
                    "Family",
                    "Event",
                    "Place",
                    "Source",
                    "Citation",
                    "Repository",
                    "Media",
                    "Note",
                    "Tag",
                ]
                + self._type_class_names
                + ["True", "False", "None", "any(", "len("]
            )
            return items

        if not text:
            # Show table names (lowercase), Types (uppercase), Type classes, True, False, None, any(), len()
            # No items starting with "_"
            items = (
                [
                    "person",
                    "family",
                    "event",
                    "place",
                    "source",
                    "citation",
                    "repository",
                    "media",
                    "note",
                    "tag",
                ]
                + [
                    "Person",
                    "Family",
                    "Event",
                    "Place",
                    "Source",
                    "Citation",
                    "Repository",
                    "Media",
                    "Note",
                    "Tag",
                ]
                + self._type_class_names
                + ["True", "False", "None", "any(", "len("]
            )
            return items

        # Check if we're in a comparison context (after ==, !=, >, <, >=, <=)
        # and suggest class constants if appropriate
        comparison_suggestions = self._get_comparison_suggestions(text, cursor_pos)
        if comparison_suggestions:
            return comparison_suggestions

        # Check if cursor is right after a dot
        # Jedi can't parse "person." when cursor is right after the dot
        # So we need to get completions by analyzing what's before the dot
        if cursor_pos > 0 and cursor_pos <= len(text) and text[cursor_pos - 1] == ".":
            # Get the expression before the dot
            expr_before_dot = text[: cursor_pos - 1].strip()
            if expr_before_dot:
                # Build code to get completions for what's before the dot
                full_code = (
                    self._env_code
                    + "\n\n# Filter expression\ntemp = "
                    + expr_before_dot
                    + "\nresult = temp."
                )

                lines = full_code.split("\n")
                line_num = len(lines)  # Last line
                column_num = len("result = temp.")

                try:
                    script = jedi.Script(full_code, path="filter_expression.py")
                    jedi_completions = script.complete(line_num, column_num)

                    # Extract completion names
                    # Check if expression starts with lowercase table name (instance, not class)
                    # If so, filter out uppercase properties (constants)
                    starts_with_lowercase = False
                    table_names = [
                        "person",
                        "family",
                        "event",
                        "place",
                        "source",
                        "citation",
                        "repository",
                        "media",
                        "note",
                        "tag",
                    ]
                    # Check if expr_before_dot starts with a lowercase table name
                    # Handle nested paths like "event.date" or "person.primary_name"
                    for table_name in table_names:
                        # Check if it starts with lowercase table name followed by dot or is just the table name
                        if (
                            expr_before_dot.startswith(table_name + ".")
                            or expr_before_dot == table_name
                            or expr_before_dot.split(".")[0] == table_name
                        ):
                            starts_with_lowercase = True
                            break

                    completion_names = []
                    # Track if the expression before the dot is a string type
                    # Use Jedi's inference to detect string types from type hints
                    is_string_type = self._infer_string_type(
                        script, expr_before_dot, line_num
                    )

                    for completion in jedi_completions:
                        name = completion.name
                        # Filter out methods (functions) - only show attributes
                        if completion.type == "function":
                            continue
                        # Filter out built-ins except any and len
                        if name in self._EXCLUDED_BUILTINS:
                            continue
                        # If using lowercase table name, filter out uppercase properties (constants)
                        if starts_with_lowercase and name and name[0].isupper():
                            continue
                        # Filter out private attributes and Python keywords
                        # Note: None is allowed, so we don't filter it out
                        # Filter out __class__ and other private attributes
                        if (not name.startswith("_")) and name not in [
                            "and",
                            "or",
                            "not",
                            "in",
                            "is",
                            "True",
                            "False",
                            "if",
                            "else",
                            "for",
                            "while",
                            "def",
                            "class",
                            "import",
                            "from",
                            "as",
                            "pass",
                            "return",
                            "break",
                            "continue",
                            "temp",
                        ]:
                            completion_names.append(name)

                    # If the expression before the dot is a string type, add string methods
                    if is_string_type:
                        # Add QueryBuilder string methods
                        string_methods = ["startswith(", "endswith("]
                        completion_names.extend(string_methods)

                    # If Jedi returned completions, sort and return them
                    if completion_names:
                        return sorted(completion_names)

                    # Fallback: If Jedi returned no completions, try to infer from expression
                    # Check if expression ends with [0] or [something] - might be array indexing
                    # Match patterns like "person.event_ref_list[0]" or "person.event_ref_list[index]"
                    match = re.match(r"(\w+)\.(\w+)\[.*?\]$", expr_before_dot)
                    if match:
                        list_name = match.group(2)

                        # Map list names to their item types
                        list_to_type = {
                            "event_ref_list": "EventRef",
                            "media_list": "MediaRef",
                            "address_list": "Address",
                            "attribute_list": "Attribute",
                            "urls": "Url",
                            "lds_ord_list": "LdsOrd",
                            "alternate_names": "Name",
                            "person_ref_list": "PersonRef",
                        }

                        if list_name in list_to_type:
                            type_name = list_to_type[list_name]
                            # Get schema for this type
                            try:
                                from gramps.gen.lib import (
                                    EventRef,
                                    MediaRef,
                                    Address,
                                    Attribute,
                                    Url,
                                    LdsOrd,
                                    Name,
                                    PersonRef,
                                )

                                type_map = {
                                    "EventRef": EventRef,
                                    "MediaRef": MediaRef,
                                    "Address": Address,
                                    "Attribute": Attribute,
                                    "Url": Url,
                                    "LdsOrd": LdsOrd,
                                    "Name": Name,
                                    "PersonRef": PersonRef,
                                }
                                if type_name in type_map:
                                    cls = type_map[type_name]
                                    schema = cls.get_schema()
                                    # Extract attribute names from schema
                                    props = schema.get("properties", {})
                                    attr_names = [
                                        name
                                        for name in props.keys()
                                        if name != "_class"
                                    ]
                                    return sorted(attr_names)
                            except Exception:
                                pass

                except Exception:
                    # Jedi might fail - that's okay, fall through to normal case
                    pass

        # Normal case: cursor is not right after a dot
        full_code = self._env_code + "\n\n# Filter expression\nresult = " + text

        # Calculate line and column
        lines = full_code.split("\n")
        line_num = len(lines)  # Last line
        column_num = cursor_pos + len("result = ")

        try:
            script = jedi.Script(full_code, path="filter_expression.py")
            jedi_completions = script.complete(line_num, column_num)

            # Extract completion names
            # Check if text starts with lowercase table name (instance, not class)
            starts_with_lowercase = False
            table_names = [
                "person",
                "family",
                "event",
                "place",
                "source",
                "citation",
                "repository",
                "media",
                "note",
                "tag",
            ]
            # Check if text starts with a lowercase table name
            # Handle nested paths like "event.date" or "person.primary_name"
            for table_name in table_names:
                # Check if it starts with lowercase table name followed by dot or is just the table name
                if (
                    text.startswith(table_name + ".")
                    or text == table_name
                    or text.split(".")[0] == table_name
                ):
                    starts_with_lowercase = True
                    break

            completion_names = []
            # Check if we're completing after a string attribute
            # Extract the expression before the current word (if any)
            current_word = self._get_current_word(text, cursor_pos)
            expr_before_word = text[
                : cursor_pos - len(current_word) if current_word else cursor_pos
            ].strip()

            # Use Jedi to infer if we're completing after a string type
            is_string_type = False
            if expr_before_word and expr_before_word.endswith("."):
                # Remove the trailing dot
                expr_before_dot = expr_before_word[:-1].strip()
                is_string_type = self._infer_string_type(
                    script, expr_before_dot, line_num
                )

            for completion in jedi_completions:
                name = completion.name
                # Filter out methods (functions) - only show attributes
                if completion.type == "function":
                    continue
                # Filter out built-ins except any and len
                if name in self._EXCLUDED_BUILTINS:
                    continue
                # If using lowercase table name, filter out uppercase properties (constants)
                if starts_with_lowercase and name and name[0].isupper():
                    continue
                # Filter out private attributes and Python keywords
                # Note: None is allowed, so we don't filter it out
                # Filter out __class__ and other private attributes
                if (not name.startswith("_")) and name not in [
                    "and",
                    "or",
                    "not",
                    "in",
                    "is",
                    "True",
                    "False",
                    "if",
                    "else",
                    "for",
                    "while",
                    "def",
                    "class",
                    "import",
                    "from",
                    "as",
                    "pass",
                    "return",
                    "break",
                    "continue",
                ]:
                    completion_names.append(name)

            # If we're completing after a string attribute, add string methods
            if is_string_type:
                # Add QueryBuilder string methods
                string_methods = ["startswith(", "endswith("]
                # Filter to only methods that match what user is typing
                if current_word:
                    string_methods = [
                        m
                        for m in string_methods
                        if m.lower().startswith(current_word.lower())
                    ]
                completion_names.extend(string_methods)

            return sorted(completion_names)
        except Exception:
            # Jedi might fail on incomplete code - that's okay
            return []

    def _match_func(self, completion, key, iter, user_data):
        """
        Custom matching function for Gtk.EntryCompletion.

        Matches only against the current word at cursor position.
        Shows all completions when cursor is right after a dot.
        """
        model = completion.get_model()
        completion_text = model[iter][0]

        # Get current text and cursor position
        text = self.get_text()
        cursor_pos = self.get_position()

        # Find the current word at cursor (this handles words after dots too)
        current_word = self._get_current_word(text, cursor_pos)

        # If cursor is right after a dot (no word yet), show all completions
        if (
            cursor_pos > 0
            and cursor_pos <= len(text)
            and text[cursor_pos - 1] == "."
            and not current_word
        ):
            return True  # Show all when cursor is right after dot with no word

        if not current_word:
            return True  # Show all if no current word

        # Case-sensitive prefix match
        return completion_text.startswith(current_word)

    def _get_current_word(self, text, cursor_pos):
        """
        Extract the current word at cursor position.

        Handles words inside brackets, after dots, etc.
        Returns empty string if cursor is right after a dot with no word.
        """
        if not text or cursor_pos == 0:
            return ""

        # Find start of current word (go back until we hit a non-word character)
        # But stop at dots, brackets, etc. - we want the word after the dot
        start = cursor_pos - 1
        while start >= 0 and (text[start].isalnum() or text[start] == "_"):
            start -= 1
        start += 1

        # If we stopped at a dot, that's fine - we want the word after the dot
        # If cursor is right after a dot with no characters yet, start will equal cursor_pos
        if start == cursor_pos:
            # No word yet - cursor is at start of potential word (maybe right after dot)
            return ""

        # Find end of current word
        end = cursor_pos
        while end < len(text) and (text[end].isalnum() or text[end] == "_"):
            end += 1

        return text[start:end]

    def _on_match_selected(self, completion, model, iter):
        """
        Handle completion selection.

        Replaces only the current word, not the entire text.
        """
        selected_text = model[iter][0]

        text = self.get_text()
        cursor_pos = self.get_position()

        # Find current word boundaries (same logic as _get_current_word)
        # Only look for alphanumeric and underscore - stop at dots, brackets, etc.
        start = cursor_pos - 1
        while start >= 0 and (text[start].isalnum() or text[start] == "_"):
            start -= 1
        start += 1

        # If we're right after a dot with no word yet, insert at cursor position
        if start == cursor_pos:
            # Insert the completion at cursor position
            new_text = text[:cursor_pos] + selected_text + text[cursor_pos:]
            new_cursor_pos = cursor_pos + len(selected_text)
        else:
            # Find end of current word
            end = cursor_pos
            while end < len(text) and (text[end].isalnum() or text[end] == "_"):
                end += 1

            # Replace only the current word
            new_text = text[:start] + selected_text + text[end:]
            new_cursor_pos = start + len(selected_text)

        self.set_text(new_text)
        self.set_position(new_cursor_pos)

        return True  # Prevent default behavior

    def _on_text_changed(self, entry):
        """Update completions when text changes."""
        text = self.get_text()
        cursor_pos = self.get_position()

        # Check if a dot was just typed
        if (
            len(text) > len(self._last_text)
            and cursor_pos > 0
            and text[cursor_pos - 1] == "."
        ):
            # Dot was just typed - update completions first, then trigger popup
            self._update_completions()
            # Trigger completion popup after model is updated
            # Use idle_add to ensure it happens after the text change is processed
            GLib.idle_add(self._trigger_completion)
        else:
            self._update_completions()

        self._last_text = text

    def _on_cursor_moved(self, entry, pspec):
        """Update completions when cursor moves."""
        self._update_completions()

    def _trigger_completion(self):
        """Trigger the completion popup to show."""
        # Ensure model is set and has items
        model = self._completion.get_model()
        if model and len(model) > 0:
            # Call complete() to trigger the popup
            # This should show the popup with all matching items
            self._completion.complete()
        return False  # Remove from idle queue

    def _update_completions(self):
        """Update the completion list based on current context."""
        text = self.get_text()
        cursor_pos = self.get_position()

        # Get completions from Jedi (with type hints, it understands everything!)
        completions = self._get_completion_items(text, cursor_pos)

        # Update the model
        model = Gtk.ListStore(str)
        for completion in completions:
            model.append([completion])

        self._completion.set_model(model)

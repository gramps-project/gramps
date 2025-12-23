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
    import jedi  # type: ignore[import-untyped]

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

    def _get_completion_items(self, text, cursor_pos):
        """
        Get completions from Jedi at the current cursor position.

        Uses Jedi static analysis to understand the context and provide
        appropriate completions. Falls back to schema-based completion
        when Jedi can't infer types (e.g., for array indexing).
        """
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

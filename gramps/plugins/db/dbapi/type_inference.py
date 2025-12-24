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
Type Inference System for Query Builder

Infers types from Python expressions using type hints from Gramps objects.
"""

import inspect
from typing import Any, Dict, List, Optional, Tuple, Type, get_args, get_origin

import gramps.gen.lib

from .query_model import (
    Expression,
    AttributeExpression,
    ArrayAccessExpression,
    ConstantExpression,
    BinaryOpExpression,
    CompareExpression,
    BoolOpExpression,
    CallExpression,
    IfExpression,
    ListComprehensionExpression,
    AnyExpression,
    TupleExpression,
)


# Table name to class mapping
TABLE_TO_CLASS: Dict[str, Type] = {
    "person": gramps.gen.lib.Person,
    "family": gramps.gen.lib.Family,
    "event": gramps.gen.lib.Event,
    "place": gramps.gen.lib.Place,
    "source": gramps.gen.lib.Source,
    "citation": gramps.gen.lib.Citation,
    "repository": gramps.gen.lib.Repository,
    "media": gramps.gen.lib.Media,
    "note": gramps.gen.lib.Note,
    "tag": gramps.gen.lib.Tag,
}


class TypeInferenceVisitor:
    """
    Visitor that infers types from expression trees using type hints.
    """

    def __init__(self, env: Optional[Dict[str, Any]] = None):
        """
        Initialize type inference visitor.

        Args:
            env: Environment dictionary with class constants (e.g., Person.MALE)
        """
        self.env = env or {}
        self._type_cache: Dict[str, Optional[Type]] = {}

    def infer_type(self, expr: Expression) -> Optional[Type]:
        """
        Infer the type of an expression.

        Args:
            expr: Expression to infer type for

        Returns:
            Inferred type, or None if type cannot be determined
        """
        return self.visit(expr)

    def visit(self, expr: Expression) -> Optional[Type]:
        """
        Visit an expression and infer its type.

        Args:
            expr: Expression to visit

        Returns:
            Inferred type, or None if type cannot be determined
        """
        method_name = f"visit_{type(expr).__name__}"
        method = getattr(self, method_name, self.generic_visit)
        return method(expr)

    def generic_visit(self, expr: Expression) -> Optional[Type]:
        """
        Default visitor method - returns None (unknown type).

        Args:
            expr: Expression to visit

        Returns:
            None (unknown type)
        """
        return None

    def visit_AttributeExpression(self, expr: AttributeExpression) -> Optional[Type]:
        """
        Infer type from attribute access like person.handle or person.primary_name.surname.

        Args:
            expr: Attribute expression

        Returns:
            Inferred type of the attribute, or None if cannot be determined
        """
        # If base is provided, infer type from base first
        if expr.base is not None:
            base_type = self.visit(expr.base)
            if base_type is None:
                return None
            return self._get_attribute_type(base_type, expr.attribute_path)

        # Get the class for the table
        table_class = TABLE_TO_CLASS.get(expr.table_name)
        if table_class is None:
            return None

        # Build full path
        if expr.attribute_path:
            return self._get_attribute_type(table_class, expr.attribute_path)
        else:
            # Just the table itself
            return table_class

    def visit_ArrayAccessExpression(
        self, expr: ArrayAccessExpression
    ) -> Optional[Type]:
        """
        Infer type from array access like person.event_ref_list[0].

        Args:
            expr: Array access expression

        Returns:
            Element type of the array, or None if cannot be determined
        """
        base_type = self.visit(expr.base)
        if base_type is None:
            return None

        # Check if base_type is a List type
        # First check if it's already a list type (not a generic)
        if base_type is list:
            # Can't determine element type from plain list
            return None

        origin = get_origin(base_type)
        if origin is list or origin is List:
            args = get_args(base_type)
            if args:
                element_type = args[0]
                # Resolve the element type if it's a forward reference
                return self._resolve_type(element_type)
        elif hasattr(base_type, "__args__"):
            # Try to get element type from __args__
            try:
                if base_type.__args__:
                    return self._resolve_type(base_type.__args__[0])
            except (AttributeError, IndexError, TypeError):
                pass

        return None

    def visit_ConstantExpression(self, expr: ConstantExpression) -> Optional[Type]:
        """
        Infer type from constant value.

        Args:
            expr: Constant expression

        Returns:
            Type of the constant value
        """
        if expr.value is None:
            return type(None)
        return type(expr.value)

    def visit_BinaryOpExpression(self, expr: BinaryOpExpression) -> Optional[Type]:
        """
        Infer type from binary operation.

        Args:
            expr: Binary operation expression

        Returns:
            Result type of the operation, or None if cannot be determined
        """
        left_type = self.visit(expr.left)
        right_type = self.visit(expr.right)

        # For most operations, result type depends on operator
        if expr.operator in ("+", "-", "*", "/", "//", "%", "**"):
            # Numeric operations
            if left_type in (int, float) and right_type in (int, float):
                # If both are int, result is int (except / which is float)
                if expr.operator == "/":
                    return float
                if left_type == int and right_type == int:
                    return int
                return float
            # String concatenation
            if expr.operator == "+" and left_type == str and right_type == str:
                return str
        elif expr.operator in ("and", "or"):
            # Boolean operations
            return bool

        return None

    def visit_CompareExpression(self, expr: CompareExpression) -> Optional[Type]:
        """
        Infer type from comparison operation.

        Args:
            expr: Comparison expression

        Returns:
            bool (comparisons always return bool)
        """
        return bool

    def visit_BoolOpExpression(self, expr: BoolOpExpression) -> Optional[Type]:
        """
        Infer type from boolean operation.

        Args:
            expr: Boolean operation expression

        Returns:
            bool (boolean operations return bool)
        """
        return bool

    def visit_CallExpression(self, expr: CallExpression) -> Optional[Type]:
        """
        Infer type from function call.

        Args:
            expr: Call expression

        Returns:
            Return type of the function, or None if cannot be determined
        """
        # Special handling for known functions
        if isinstance(expr.function, ConstantExpression):
            func_name = expr.function.value
            if func_name == "len":
                return int
            elif func_name == "any":
                return bool
            elif func_name == "str":
                return str
            elif func_name == "int":
                return int
            elif func_name == "float":
                return float

        # For method calls like .startswith(), .endswith()
        if isinstance(expr.function, AttributeExpression):
            attr_path = expr.function.attribute_path
            if attr_path.endswith(".startswith") or attr_path.endswith(".endswith"):
                return bool

        return None

    def visit_IfExpression(self, expr: IfExpression) -> Optional[Type]:
        """
        Infer type from ternary expression.

        Args:
            expr: If expression

        Returns:
            Type of body or orelse (they should be compatible)
        """
        body_type = self.visit(expr.body)
        orelse_type = self.visit(expr.orelse)
        # Return the first non-None type, or None if both are None
        return body_type if body_type is not None else orelse_type

    def visit_ListComprehensionExpression(
        self, expr: ListComprehensionExpression
    ) -> Optional[Type]:
        """
        Infer type from list comprehension.

        Args:
            expr: List comprehension expression

        Returns:
            List type containing the element type
        """
        element_type = self.visit(expr.expression)
        if element_type is not None:
            return (
                list  # Could be more specific with List[element_type] but list is fine
            )
        return list

    def visit_AnyExpression(self, expr: AnyExpression) -> Optional[Type]:
        """
        Infer type from any() expression.

        Args:
            expr: Any expression

        Returns:
            bool (any() returns bool)
        """
        return bool

    def visit_TupleExpression(self, expr: TupleExpression) -> Optional[Type]:
        """
        Infer type from tuple expression.

        Args:
            expr: Tuple expression

        Returns:
            tuple type
        """
        return tuple

    def _get_attribute_type(self, obj_type: Type, attr_path: str) -> Optional[Type]:
        """
        Get the type of an attribute from a class using type hints.

        Args:
            obj_type: Class type to get attribute from
            attr_path: Dot-separated attribute path (e.g., "primary_name.surname")

        Returns:
            Type of the attribute, or None if cannot be determined
        """
        if not attr_path:
            return obj_type

        # Check cache first
        cache_key = f"{obj_type.__name__}.{attr_path}"
        if cache_key in self._type_cache:
            return self._type_cache[cache_key]

        # Split path into parts
        parts = attr_path.split(".")
        current_type = obj_type

        for part in parts:
            # Get type hint for this attribute
            attr_type = self._get_attr_type_from_class(current_type, part)
            if attr_type is None:
                # Fallback: check if attribute exists at runtime
                # This handles cases where type hints aren't available
                if hasattr(current_type, part):
                    # Attribute exists but no type hint - can't determine type precisely
                    # But we know it exists, so for validation purposes we can continue
                    # Try to get a sample instance to check the type
                    try:
                        # For dataclasses or classes with __init__, we might be able to infer
                        # For now, return None to indicate unknown type
                        pass
                    except Exception:
                        pass
                self._type_cache[cache_key] = None
                return None
            current_type = attr_type

        self._type_cache[cache_key] = current_type
        return current_type

    def _get_attr_type_from_class(self, cls: Type, attr_name: str) -> Optional[Type]:
        """
        Get the type of an attribute from a class using type hints.

        Args:
            cls: Class to get attribute type from
            attr_name: Name of the attribute

        Returns:
            Type of the attribute, or None if cannot be determined
        """
        # Try to get from MRO (method resolution order) to check base classes
        # This includes cls itself, so we check all classes in the inheritance hierarchy
        for base in cls.__mro__:
            if hasattr(base, "__annotations__"):
                annotations = base.__annotations__
                if attr_name in annotations:
                    resolved = self._resolve_type(annotations[attr_name])
                    if resolved is not None:
                        return resolved

        # Fallback: check if attribute exists at runtime (for attributes without type hints)
        if hasattr(cls, attr_name):
            attr = getattr(cls, attr_name, None)
            if attr is not None:
                # If it's a class, return the class
                if inspect.isclass(attr):
                    return attr
                # If it's a property, return None so that validate_attribute_path
                # can handle it specially (properties need special handling for return types)
                if isinstance(attr, property):
                    return None
                # Otherwise, return the type of the attribute
                return type(attr)

        return None

    def _extract_list_item_type(self, list_type: Type) -> Optional[Type]:
        """
        Extract the item type from a List[ItemType] or list[ItemType] type hint.

        Args:
            list_type: The list type (may be List[ItemType], list[ItemType], or just list)

        Returns:
            The item type if it can be determined, None otherwise
        """
        from typing import get_args, get_origin

        # Handle typing.List[ItemType] or list[ItemType]
        origin = get_origin(list_type)
        if origin is not None:
            # It's a generic type like List[str]
            args = get_args(list_type)
            if args and len(args) > 0:
                item_type = args[0]
                # Resolve the type if it's a string or forward reference
                return self._resolve_type(item_type)

        # If it's just 'list' without type parameters, we can't determine item type
        if list_type is list:
            return None

        return None

    def _resolve_type(self, type_hint: Any) -> Optional[Type]:
        """
        Resolve a type hint to an actual type.

        Handles forward references and string annotations.

        Args:
            type_hint: Type hint (may be a string, type, or generic)

        Returns:
            Resolved type, or None if cannot be resolved
        """
        # If it's already a type, return it
        if isinstance(type_hint, type):
            return type_hint

        # If it's a string (forward reference or string annotation), try to resolve it
        if isinstance(type_hint, str):
            # Handle typing constructs like "Optional[str]", "List[str]", etc.
            if type_hint.startswith("Optional["):
                # Extract the inner type
                inner = type_hint[9:-1]  # Remove "Optional[" and "]"
                inner_type = self._resolve_type(inner)
                if inner_type is not None:
                    # Return Union[inner_type, None] or just the inner type
                    # For simplicity, return the inner type (caller can handle Optional)
                    return inner_type
            elif type_hint.startswith("List["):
                # Extract the inner type
                inner = type_hint[5:-1]  # Remove "List[" and "]"
                inner_type = self._resolve_type(inner)
                # Return list type (we'll handle element types separately)
                return list
            elif type_hint in ("str", "int", "float", "bool"):
                # Built-in types
                return {"str": str, "int": int, "float": float, "bool": bool}[type_hint]
            else:
                # Try to find in gramps.gen.lib
                if hasattr(gramps.gen.lib, type_hint):
                    return getattr(gramps.gen.lib, type_hint)

        # Handle generic types like List[T]
        origin = get_origin(type_hint)
        if origin is not None:
            # For List[T], return list (we'll handle element types separately)
            if origin is list or origin is List:
                return list

        # Try to get the type from typing module
        try:
            if hasattr(type_hint, "__origin__"):
                return type_hint.__origin__
        except (AttributeError, TypeError):
            pass

        return None

    def validate_attribute_path(
        self, obj_type: Type, attr_path: str, allow_json_fields: bool = False
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate that an attribute path exists on a type.

        Args:
            obj_type: Class type to validate against
            attr_path: Dot-separated attribute path (may include array access like "list[0].attr")
            allow_json_fields: If True, allow attributes that don't exist as Python attributes
                              but might be JSON fields

        Returns:
            Tuple of (is_valid, error_message)
            - is_valid: True if path is valid, False otherwise
            - error_message: Error message if invalid, None if valid
        """
        if not attr_path:
            return True, None

        # Handle array access in paths like "surname_list[0].surname"
        import re

        array_match = re.search(r"^([^[]+)\[.*?\](.*)$", attr_path)
        if array_match:
            list_attr = array_match.group(1)
            remainder = array_match.group(2).lstrip(".")

            # Validate the list attribute exists
            is_valid, error_msg = self.validate_attribute_path(
                obj_type, list_attr, allow_json_fields
            )
            if not is_valid:
                return False, error_msg

            # Infer the item type from the list
            list_type = self._get_attr_type_from_class(obj_type, list_attr)
            if list_type is None:
                # Can't determine list type - allow it
                return True, None

            # Extract item type from List[ItemType] or list[ItemType]
            item_type = self._extract_list_item_type(list_type)
            if item_type is None:
                # Can't determine item type - allow it
                return True, None

            # Validate remainder against item type
            if remainder:
                return self.validate_attribute_path(
                    item_type, remainder, allow_json_fields
                )
            else:
                # Just array access, no remainder - valid
                return True, None

        parts = attr_path.split(".")
        current_type = obj_type
        current_path = []

        for i, part in enumerate(parts):
            current_path.append(part)
            attr_type = self._get_attr_type_from_class(current_type, part)
            if attr_type is None:
                # Check if attribute exists at runtime as fallback
                # First check class attributes, then check if it might be an instance attribute
                # (instance attributes set in __init__ don't exist on the class)
                has_class_attr = hasattr(current_type, part)
                # For instance attributes, check if there's a getter method or if it's set in __init__
                has_getter = hasattr(current_type, f"get_{part}") or hasattr(
                    current_type, f"get_{part.replace('_', '')}"
                )
                if not has_class_attr and not has_getter:
                    # Check if it's a common pattern (like _handle attributes or type)
                    # These are typically instance attributes set in __init__
                    is_common_instance_attr = (
                        part.endswith("_handle")
                        or part
                        in [
                            "father_handle",
                            "mother_handle",
                            "child_ref_list",
                            "type",
                            "date",
                            "place",
                        ]
                        or part.endswith("_ref_list")
                    )
                    if is_common_instance_attr:
                        # Common instance attributes - allow them
                        # If there are more parts in the path, we can't validate them
                        # without knowing the attribute's type, so allow the entire path
                        if i < len(parts) - 1:
                            # There are more parts - we can't validate them without knowing the type
                            return True, None
                        # No more parts - attribute itself is valid
                        return True, None
                    else:
                        # Attribute doesn't exist - suggest similar attributes
                        suggestions = self._suggest_attributes(current_type, part)
                        full_path = ".".join(current_path)
                        error_msg = (
                            f"Attribute '{part}' not found on {current_type.__name__}"
                        )
                        if suggestions:
                            error_msg += (
                                f". Did you mean: {', '.join(suggestions[:3])}?"
                            )
                        return False, error_msg
                # Attribute exists at runtime but no type hint - use runtime type
                attr = getattr(current_type, part, None)
                if attr is not None:
                    if inspect.isclass(attr):
                        attr_type = attr
                    elif isinstance(attr, property):
                        # For properties, try to get the return type from annotations
                        if hasattr(attr, "fget") and attr.fget is not None:
                            if hasattr(attr.fget, "__annotations__"):
                                return_ann = attr.fget.__annotations__.get("return")
                                if return_ann is not None:
                                    attr_type = self._resolve_type(return_ann)
                                    if attr_type is not None:
                                        current_type = attr_type
                                        continue
                        # Properties in Gramps classes typically don't have return type annotations
                        # When we can't determine the return type and there are more parts in the path,
                        # we allow the entire remaining path to pass validation since we can't validate
                        # it statically without knowing the property's return type.
                        # This allows patterns like Event.type.value to work even without type hints.
                        if i < len(parts) - 1:
                            # There are more parts after this property - we can't validate them
                            # without knowing the property's return type, so allow the entire path
                            return True, None
                        # No more parts - property itself is valid
                        return True, None
                    else:
                        attr_type = type(attr)
                else:
                    # Attribute exists but is None - can't determine type
                    # Allow it but can't infer type
                    attr_type = type(None)
            current_type = attr_type

        return True, None

    def _suggest_attributes(
        self, cls: Type, attr_name: str, max_suggestions: int = 3
    ) -> list[str]:
        """
        Suggest similar attribute names for a typo.

        Args:
            cls: Class to search for attributes
            attr_name: The incorrect attribute name
            max_suggestions: Maximum number of suggestions to return

        Returns:
            List of suggested attribute names
        """
        suggestions = []
        available_attrs: set[str] = set()

        # Collect all available attributes from type hints
        for base in cls.__mro__:
            if hasattr(base, "__annotations__"):
                available_attrs.update(base.__annotations__.keys())

        # Simple string similarity (Levenshtein-like)
        for attr in available_attrs:
            if attr.startswith(attr_name[:2]) or attr_name[:2] in attr:
                suggestions.append(attr)
                if len(suggestions) >= max_suggestions:
                    break

        return suggestions[:max_suggestions]

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

import ast
import types
from typing import Dict, List, Optional, Tuple

from .query_model import (
    SelectQuery,
    SelectExpression,
    OrderBy,
    ArrayExpansion,
    Join,
    Expression,
    ListComprehensionExpression,
    AnyExpression,
    BoolOpExpression,
    CompareExpression,
    ConstantExpression,
    AttributeExpression,
    ArrayAccessExpression,
    BinaryOpExpression,
    UnaryOpExpression,
    CallExpression,
    IfExpression,
    TupleExpression,
    ArrayExpansionExpression,
)
from .query_parser import QueryParser
from .sql_generator import SQLGenerator
from .type_inference import TypeInferenceVisitor

# Database columns (not in JSON) that can be queried directly
# These are computed/stored fields that exist as actual database columns
DATABASE_COLUMNS: Dict[str, List[str]] = {
    "Person": [
        # "probably_alive_birth_start_sortval",
        # "probably_alive_death_stop_sortval",
        # "given_name",  # Derived from primary_name
        # "surname",  # Derived from primary_name
    ],
    # Add other tables' database columns here as needed
}


class ExpressionVisitor:
    """
    Base visitor class for traversing and transforming expression trees recursively.

    This provides a uniform way to traverse expression trees and perform operations
    like equality checking, condition removal, normalization, and validation.
    """

    def visit(self, expr: Expression) -> Optional[Expression]:
        """
        Visit an expression node and dispatch to the appropriate visitor method.

        Args:
            expr: Expression to visit

        Returns:
            Transformed expression (default: returns as-is), or None if expression should be removed
        """
        method_name = f"visit_{type(expr).__name__}"
        method = getattr(self, method_name, self.generic_visit)
        return method(expr)

    def generic_visit(self, expr: Expression) -> Optional[Expression]:
        """
        Default visitor method for expressions without specific handlers.

        Args:
            expr: Expression to visit

        Returns:
            Expression unchanged
        """
        return expr

    def visit_ConstantExpression(
        self, expr: ConstantExpression
    ) -> Optional[Expression]:
        """Visit a constant expression."""
        return self.generic_visit(expr)

    def visit_AttributeExpression(
        self, expr: AttributeExpression
    ) -> Optional[Expression]:
        """Visit an attribute expression, recursively visiting base if present."""
        if expr.base is not None:
            visited_base = self.visit(expr.base)
            if visited_base is None:
                return None
            expr.base = visited_base
        return self.generic_visit(expr)

    def visit_ArrayAccessExpression(
        self, expr: ArrayAccessExpression
    ) -> Optional[Expression]:
        """Visit an array access expression, recursively visiting base and index."""
        visited_base = self.visit(expr.base)
        if visited_base is None:
            return None
        expr.base = visited_base
        visited_index = self.visit(expr.index)
        if visited_index is None:
            return None
        expr.index = visited_index
        return self.generic_visit(expr)

    def visit_BinaryOpExpression(
        self, expr: BinaryOpExpression
    ) -> Optional[Expression]:
        """Visit a binary operation, recursively visiting left and right."""
        visited_left = self.visit(expr.left)
        if visited_left is None:
            return None
        expr.left = visited_left
        visited_right = self.visit(expr.right)
        if visited_right is None:
            return None
        expr.right = visited_right
        return self.generic_visit(expr)

    def visit_UnaryOpExpression(self, expr: UnaryOpExpression) -> Optional[Expression]:
        """Visit a unary operation, recursively visiting operand."""
        visited_operand = self.visit(expr.operand)
        if visited_operand is None:
            return None
        expr.operand = visited_operand
        return self.generic_visit(expr)

    def visit_CompareExpression(self, expr: CompareExpression) -> Optional[Expression]:
        """Visit a comparison, recursively visiting left and comparators."""
        visited_left = self.visit(expr.left)
        if visited_left is None:
            return None
        expr.left = visited_left
        visited_comparators: List[Expression] = []
        for comp in expr.comparators:
            visited_comp = self.visit(comp)
            if visited_comp is None:
                return None
            visited_comparators.append(visited_comp)
        expr.comparators = visited_comparators
        return self.generic_visit(expr)

    def visit_BoolOpExpression(self, expr: BoolOpExpression) -> Optional[Expression]:
        """Visit a boolean operation, recursively visiting all values."""
        visited_values: List[Expression] = []
        for val in expr.values:
            visited_val = self.visit(val)
            if visited_val is not None:
                visited_values.append(visited_val)
        if not visited_values:
            return None
        expr.values = visited_values
        return self.generic_visit(expr)

    def visit_CallExpression(self, expr: CallExpression) -> Optional[Expression]:
        """Visit a function call, recursively visiting function and arguments."""
        visited_function = self.visit(expr.function)
        if visited_function is None:
            return None
        expr.function = visited_function
        visited_arguments = []
        for arg in expr.arguments:
            visited_arg = self.visit(arg)
            if visited_arg is None:
                return None
            visited_arguments.append(visited_arg)
        expr.arguments = visited_arguments
        return self.generic_visit(expr)

    def visit_IfExpression(self, expr: IfExpression) -> Optional[Expression]:
        """Visit a ternary expression, recursively visiting test, body, and orelse."""
        visited_test = self.visit(expr.test)
        if visited_test is None:
            return None
        expr.test = visited_test
        visited_body = self.visit(expr.body)
        if visited_body is None:
            return None
        expr.body = visited_body
        visited_orelse = self.visit(expr.orelse)
        if visited_orelse is None:
            return None
        expr.orelse = visited_orelse
        return self.generic_visit(expr)

    def visit_ListComprehensionExpression(
        self, expr: ListComprehensionExpression
    ) -> Optional[Expression]:
        """Visit a list comprehension, recursively visiting expression and condition."""
        visited_expression = self.visit(expr.expression)
        if visited_expression is None:
            return None
        expr.expression = visited_expression
        if expr.condition is not None:
            visited_condition = self.visit(expr.condition)
            if visited_condition is None:
                return None
            expr.condition = visited_condition
        return self.generic_visit(expr)

    def visit_AnyExpression(self, expr: AnyExpression) -> Optional[Expression]:
        """Visit an any() expression, recursively visiting condition if present."""
        if expr.condition is not None:
            visited_condition = self.visit(expr.condition)
            if visited_condition is None:
                return None
            expr.condition = visited_condition
        return self.generic_visit(expr)

    def visit_ArrayExpansionExpression(
        self, expr: ArrayExpansionExpression
    ) -> Optional[Expression]:
        """Visit an array expansion, recursively visiting array expression."""
        visited_array = self.visit(expr.array_expression)
        if visited_array is None:
            return None
        expr.array_expression = visited_array
        return self.generic_visit(expr)

    def visit_TupleExpression(self, expr: TupleExpression) -> Optional[Expression]:
        """Visit a tuple, recursively visiting all elements."""
        visited_elements = []
        for elem in expr.elements:
            visited_elem = self.visit(elem)
            if visited_elem is None:
                return None
            visited_elements.append(visited_elem)
        expr.elements = visited_elements
        return self.generic_visit(expr)


class ExpressionEqualityVisitor:
    """
    Visitor to check if two expressions are equal.
    This doesn't inherit from ExpressionVisitor because it returns bool, not Expression.
    """

    def __init__(self, target: Expression):
        """
        Initialize with target expression to compare against.

        Args:
            target: Expression to compare with
        """
        self.target = target

    def visit(self, expr: Expression) -> bool:
        """
        Visit expression and check equality with target.

        Args:
            expr: Expression to check

        Returns:
            True if expressions are equal, False otherwise
        """
        # Type must match
        if type(expr) != type(self.target):
            return False

        method_name = f"visit_{type(expr).__name__}"
        method = getattr(self, method_name, self.generic_visit)
        return method(expr)

    def generic_visit(self, expr: Expression) -> bool:
        """Default equality check using string representation."""
        return str(expr) == str(self.target)

    def visit_CompareExpression(self, expr: CompareExpression) -> bool:
        """Check equality of comparison expressions."""
        if not isinstance(self.target, CompareExpression):
            return False
        target = self.target
        if (
            len(expr.operators) == len(target.operators)
            and len(expr.comparators) == len(target.comparators)
            and expr.operators == target.operators
        ):
            # Check if left sides match
            if not ExpressionEqualityVisitor(target.left).visit(expr.left):
                return False
            # Check if comparators match
            for c1, c2 in zip(expr.comparators, target.comparators):
                if not ExpressionEqualityVisitor(c2).visit(c1):
                    return False
            return True
        return False

    def visit_AttributeExpression(self, expr: AttributeExpression) -> bool:
        """Check equality of attribute expressions."""
        if not isinstance(self.target, AttributeExpression):
            return False
        target = self.target
        if (
            expr.table_name == target.table_name
            and expr.attribute_path == target.attribute_path
            and expr.is_database_column == target.is_database_column
        ):
            # Check base expressions if present
            if expr.base is None and target.base is None:
                return True
            if expr.base is not None and target.base is not None:
                return ExpressionEqualityVisitor(target.base).visit(expr.base)
            return False
        return False

    def visit_ConstantExpression(self, expr: ConstantExpression) -> bool:
        """Check equality of constant expressions."""
        if not isinstance(self.target, ConstantExpression):
            return False
        return expr.value == self.target.value

    def visit_UnaryOpExpression(self, expr: UnaryOpExpression) -> bool:
        """Check equality of unary operation expressions."""
        if not isinstance(self.target, UnaryOpExpression):
            return False
        target = self.target
        if expr.operator == target.operator:
            return ExpressionEqualityVisitor(target.operand).visit(expr.operand)
        return False

    def visit_BinaryOpExpression(self, expr: BinaryOpExpression) -> bool:
        """Check equality of binary operation expressions."""
        if not isinstance(self.target, BinaryOpExpression):
            return False
        target = self.target
        if expr.operator == target.operator:
            return ExpressionEqualityVisitor(target.left).visit(
                expr.left
            ) and ExpressionEqualityVisitor(target.right).visit(expr.right)
        return False

    def visit_BoolOpExpression(self, expr: BoolOpExpression) -> bool:
        """Check equality of boolean operation expressions."""
        if not isinstance(self.target, BoolOpExpression):
            return False
        target = self.target
        if expr.operator == target.operator and len(expr.values) == len(target.values):
            return all(
                ExpressionEqualityVisitor(target_val).visit(expr_val)
                for expr_val, target_val in zip(expr.values, target.values)
            )
        return False

    def visit_ArrayAccessExpression(self, expr: ArrayAccessExpression) -> bool:
        """Check equality of array access expressions."""
        if not isinstance(self.target, ArrayAccessExpression):
            return False
        target = self.target
        if expr.is_constant_index == target.is_constant_index:
            return ExpressionEqualityVisitor(target.base).visit(
                expr.base
            ) and ExpressionEqualityVisitor(target.index).visit(expr.index)
        return False

    def visit_CallExpression(self, expr: CallExpression) -> bool:
        """Check equality of function call expressions."""
        if not isinstance(self.target, CallExpression):
            return False
        target = self.target
        if len(expr.arguments) == len(target.arguments):
            return ExpressionEqualityVisitor(target.function).visit(
                expr.function
            ) and all(
                ExpressionEqualityVisitor(target_arg).visit(expr_arg)
                for expr_arg, target_arg in zip(expr.arguments, target.arguments)
            )
        return False


class ConditionRemovalVisitor(ExpressionVisitor):
    """
    Visitor to remove a specific condition from an expression tree.
    """

    def __init__(self, condition_to_remove: Expression, equality_checker):
        """
        Initialize with condition to remove and equality checker function.

        Args:
            condition_to_remove: Condition expression to remove
            equality_checker: Function to check expression equality
        """
        self.condition_to_remove = condition_to_remove
        self.equality_checker = equality_checker

    def visit(self, expr: Expression) -> Optional[Expression]:
        """
        Visit expression and remove matching condition.

        Args:
            expr: Expression to process

        Returns:
            Expression with condition removed, or None if entire expression was removed
        """
        # Check if this expression matches the condition to remove
        if self.equality_checker(expr, self.condition_to_remove):
            return None

        # Continue with normal visitor pattern
        return super().visit(expr)

    def visit_BoolOpExpression(self, expr: BoolOpExpression) -> Optional[Expression]:
        """Recursively remove condition from boolean operation."""
        filtered_values = []
        for value in expr.values:
            filtered = self.visit(value)
            if filtered is not None:
                filtered_values.append(filtered)

        if not filtered_values:
            # All conditions were removed
            return None
        elif len(filtered_values) == 1:
            # Only one condition left - return it directly
            return filtered_values[0]
        else:
            # Multiple conditions left - return BoolOp with filtered values
            return BoolOpExpression(
                operator=expr.operator,
                values=filtered_values,
            )


class ArrayExpansionRemovalVisitor(ExpressionVisitor):
    """
    Visitor to remove array expansion conditions from an expression tree.
    """

    def __init__(self, array_expansion: ArrayExpansion):
        """
        Initialize with array expansion to remove.

        Args:
            array_expansion: ArrayExpansion object identifying the condition to remove
        """
        self.array_expansion = array_expansion

    def visit(self, expr: Expression) -> Optional[Expression]:
        """
        Visit expression and remove array expansion condition.

        Args:
            expr: Expression to process

        Returns:
            Expression with array expansion removed, or None if entire expression was removed
        """
        # Check if this is an array expansion condition
        if isinstance(expr, CompareExpression):
            if len(expr.operators) == 1 and expr.operators[0] == "in":
                # Check if left is the item variable
                left_is_item = False
                if isinstance(expr.left, AttributeExpression):
                    left_is_item = (
                        expr.left.table_name == "json_each"
                        and expr.left.attribute_path == ""
                    )
                elif isinstance(expr.left, ConstantExpression):
                    left_is_item = expr.left.value == self.array_expansion.item_var

                # Check if right matches the array path
                if (
                    left_is_item
                    and len(expr.comparators) > 0
                    and isinstance(expr.comparators[0], AttributeExpression)
                    and expr.comparators[0].attribute_path
                    == self.array_expansion.array_path
                ):
                    # This is the array expansion condition - remove it
                    return None

        # Continue with normal visitor pattern
        return super().visit(expr)

    def visit_BoolOpExpression(self, expr: BoolOpExpression) -> Optional[Expression]:
        """Recursively remove array expansion from boolean operation."""
        filtered_values = []
        for value in expr.values:
            filtered = self.visit(value)
            if filtered is not None:
                filtered_values.append(filtered)

        if not filtered_values:
            # All conditions were array expansion - return None
            return None
        elif len(filtered_values) == 1:
            # Only one condition left - return it directly
            return filtered_values[0]
        else:
            # Multiple conditions left - return BoolOp with filtered values
            return BoolOpExpression(
                operator=expr.operator,
                values=filtered_values,
            )


class ExpressionNormalizationVisitor(ExpressionVisitor):
    """
    Visitor to normalize expression trees by flattening nested operations.
    """

    def visit_BoolOpExpression(self, expr: BoolOpExpression) -> Optional[Expression]:
        """Flatten nested boolean operations of the same type."""
        # First, recursively normalize all values
        normalized_values: List[Expression] = []
        for value in expr.values:
            normalized = self.visit(value)
            if normalized is None:
                continue
            # If normalized value is the same operator, flatten it
            if (
                isinstance(normalized, BoolOpExpression)
                and normalized.operator == expr.operator
            ):
                normalized_values.extend(normalized.values)
            else:
                normalized_values.append(normalized)

        # If no values remain, return None
        if not normalized_values:
            return None
        # If only one value remains, return it directly
        if len(normalized_values) == 1:
            return normalized_values[0]

        # Return normalized BoolOp with flattened values
        return BoolOpExpression(
            operator=expr.operator,
            values=normalized_values,
        )

    def visit_CompareExpression(self, expr: CompareExpression) -> Optional[Expression]:
        """Normalize comparison expressions."""
        # Recursively normalize left and comparators
        normalized_left = self.visit(expr.left)
        if normalized_left is None:
            return None
        normalized_comparators: List[Expression] = []
        for comp in expr.comparators:
            normalized_comp = self.visit(comp)
            if normalized_comp is None:
                return None
            normalized_comparators.append(normalized_comp)

        return CompareExpression(
            left=normalized_left,
            operators=expr.operators,
            comparators=normalized_comparators,
        )


class ExpressionValidationVisitor(ExpressionVisitor):
    """
    Visitor to validate expression trees are well-formed.
    """

    def visit_CompareExpression(self, expr: CompareExpression) -> Optional[Expression]:
        """Validate comparison expression has matching operators and comparators."""
        if len(expr.operators) != len(expr.comparators):
            raise ValueError(
                f"CompareExpression has {len(expr.operators)} operators "
                f"but {len(expr.comparators)} comparators"
            )
        if not expr.operators:
            raise ValueError("CompareExpression must have at least one operator")
        return super().visit_CompareExpression(expr)

    def visit_BoolOpExpression(self, expr: BoolOpExpression) -> Optional[Expression]:
        """Validate boolean operation has at least one value."""
        if not expr.values:
            raise ValueError("BoolOpExpression must have at least one value")
        if expr.operator not in ("and", "or"):
            raise ValueError(f"Invalid boolean operator: {expr.operator}")
        return super().visit_BoolOpExpression(expr)

    def visit_CallExpression(self, expr: CallExpression) -> Optional[Expression]:
        """Validate function call has valid function and arguments."""
        if expr.function is None:
            raise ValueError("CallExpression must have a function")
        return super().visit_CallExpression(expr)

    def visit_IfExpression(self, expr: IfExpression) -> Optional[Expression]:
        """Validate ternary expression has all required parts."""
        if expr.test is None or expr.body is None or expr.orelse is None:
            raise ValueError("IfExpression must have test, body, and orelse")
        return super().visit_IfExpression(expr)


class TypeValidationVisitor(ExpressionVisitor):
    """
    Visitor to validate expression types using type hints.
    """

    def __init__(self, type_inference: TypeInferenceVisitor):
        """
        Initialize type validation visitor.

        Args:
            type_inference: Type inference visitor to use for type checking
        """
        self.type_inference = type_inference

    def visit_AttributeExpression(
        self, expr: AttributeExpression
    ) -> Optional[Expression]:
        """Validate attribute path exists using type hints."""
        # Get the class for the table
        from .type_inference import TABLE_TO_CLASS

        table_class = TABLE_TO_CLASS.get(expr.table_name)
        if table_class is None:
            # Unknown table - skip validation
            return super().visit_AttributeExpression(expr)

        # If base is provided, validate from base type
        if expr.base is not None:
            base_type = self.type_inference.visit(expr.base)
            if base_type is not None:
                is_valid, error_msg = self.type_inference.validate_attribute_path(
                    base_type, expr.attribute_path
                )
                if not is_valid:
                    raise ValueError(error_msg)
        else:
            # Validate from table class
            is_valid, error_msg = self.type_inference.validate_attribute_path(
                table_class, expr.attribute_path
            )
            if not is_valid:
                raise ValueError(error_msg)

        return super().visit_AttributeExpression(expr)


class QueryBuilder:
    """
    SQL query builder using intermediate query model objects.
    Orchestrates parsing and SQL generation.
    """

    def __init__(
        self,
        table_name,
        json_extract=None,
        json_array_length=None,
        env=None,
        dialect="sqlite",
        enable_type_validation=False,
    ):
        """
        Initialize QueryBuilder with table configuration.

        Args:
            table_name: Base table name (e.g., "person")
            json_extract: JSON extract pattern (deprecated, kept for compatibility)
            json_array_length: JSON array length pattern (deprecated, kept for compatibility)
            env: Environment dictionary for expression evaluation
            dialect: SQL dialect ("sqlite" or "postgres"). Defaults to "sqlite"
            enable_type_validation: If True, validate attribute paths using type hints
        """
        self.table_name = table_name
        self.dialect = dialect.lower()
        self.env = env if env is not None else {}
        self.enable_type_validation = enable_type_validation
        database_columns = set(DATABASE_COLUMNS.get(table_name.capitalize(), []))

        # Create parser and generator
        # Type inference is always enabled to improve SQL generation
        self.parser = QueryParser(
            table_name=table_name,
            env=self.env,
            database_columns=database_columns,
            database_columns_dict=DATABASE_COLUMNS,
        )
        self.generator = SQLGenerator(dialect=self.dialect, type_inference=None)
        self.type_inference = TypeInferenceVisitor(env=self.env)
        # Pass type inference to generator for type-aware SQL generation
        self.generator.type_inference = self.type_inference

    def get_sql_query(self, what, where, order_by, page=None, page_size=None):
        """
        Generate complete SQL query from what, where, and order_by parameters.

        Args:
            what: What clause (None, str, or list of strings)
            where: Where clause (None or str)
            order_by: Order by clause (None, str, or list of strings)
            page: 1-based page number for pagination. Must be provided together with page_size.
            page_size: Number of items per page. Must be provided together with page.

        Returns:
            Complete SQL query string
        """
        # Validate pagination parameters
        if (page is not None) != (page_size is not None):
            raise ValueError(
                "Both page and page_size must be provided together, or neither"
            )

        if page is not None and page_size is not None:
            if page < 1:
                raise ValueError("page must be >= 1")
            if page_size < 1:
                raise ValueError("page_size must be >= 1")

        # Validate input types
        if callable(where) or isinstance(where, types.LambdaType):
            raise ValueError(
                "Callables (lambda functions) are not supported for SQL generation. Please use string expressions instead."
            )
        if callable(what) or isinstance(what, types.LambdaType):
            raise ValueError(
                "Callables (lambda functions) are not supported for SQL generation. Please use string expressions instead."
            )
        if isinstance(what, list):
            for w in what:
                if callable(w) or isinstance(w, types.LambdaType):
                    raise ValueError(
                        "Callables (lambda functions) are not supported for SQL generation. Please use string expressions instead."
                    )

        # Parse what clause
        select_expressions = self._parse_what(what)

        # Parse where clause
        where_condition = None
        if where:
            where_condition = self.parser.parse_expression(where)
            # Always validate types to catch errors early
            if self.enable_type_validation:
                validator = TypeValidationVisitor(self.type_inference)
                validator.visit(where_condition)

        # Parse order_by clause
        order_by_list = self._parse_order_by(order_by)

        # Extract array expansion from WHERE condition FIRST
        # This needs to happen before join detection so that item_var is set
        # Array expansion is now represented as ArrayExpansionExpression in the parsed tree
        array_expansion = None
        is_array_expansion_in_or = False
        if where_condition:
            array_expansion, is_array_expansion_in_or = (
                self._extract_array_expansion_from_condition(where_condition)
            )

            # If array expansion is found, update parser context for item_var
            # This allows "item.attr" in join detection and what clause to be parsed correctly
            if array_expansion:
                self.parser.item_var = array_expansion.item_var
                self.parser.array_path = array_expansion.array_path

                # Re-parse WHERE clause with item_var context so that item.ref is correctly
                # parsed as json_each.ref instead of person.ref
                where_condition = self.parser.parse_expression(where)

        # Detect table references and JOINs
        # Do this AFTER setting item_var so that item.attr can be recognized
        referenced_tables = set()
        if where:
            referenced_tables.update(self.parser.detect_table_references(where))
        if what:
            if isinstance(what, str):
                referenced_tables.update(self.parser.detect_table_references(what))
            elif isinstance(what, list):
                for w in what:
                    if isinstance(w, str):
                        referenced_tables.update(self.parser.detect_table_references(w))

        # Extract JOIN conditions
        joins = []
        if referenced_tables and where:
            joins = self.parser.detect_joins(where)
            # Deduplicate JOINs to the same table by combining conditions with OR
            joins = self._deduplicate_joins(joins)

            # Remove join conditions from WHERE clause (they're now in JOIN ON clauses)
            if joins and where_condition:
                for join in joins:
                    where_condition = self._remove_join_condition(
                        where_condition, join.condition
                    )
                    if where_condition is None:
                        # All conditions were join conditions - break
                        break

        # If array expansion was found, re-parse what clause with item_var context if needed
        if array_expansion:
            # Check if what clause references the item variable
            if what:
                if isinstance(what, str) and array_expansion.item_var in what:
                    # Re-parse with item_var context
                    select_expressions = self._parse_what(what)
                elif isinstance(what, list):
                    # Check if any item references the item variable
                    needs_reparse = any(
                        isinstance(w, str) and array_expansion.item_var in w
                        for w in what
                    )
                    if needs_reparse:
                        select_expressions = self._parse_what(what)

        # Handle UNION query for array expansion in OR expressions
        if is_array_expansion_in_or:
            return self._build_union_query(
                select_expressions,
                where_condition,
                order_by_list,
                array_expansion,
                joins,
                page,
                page_size,
            )

        # Build SelectQuery object
        query = SelectQuery(
            base_table=self.table_name,
            select_expressions=select_expressions,
            where_condition=where_condition,
            joins=joins,
            order_by=order_by_list,
            array_expansion=array_expansion,
            limit=page_size if page_size is not None else None,
            offset=(
                (page - 1) * page_size
                if page is not None and page_size is not None
                else None
            ),
        )

        # Handle list comprehensions in what clause
        query = self._handle_list_comprehensions(query, what)

        # Generate SQL
        return self.generator.generate(query)

    def _parse_what(self, what) -> List[SelectExpression]:
        """Parse what clause into SelectExpression objects."""
        if what is None:
            # Default: select json_data
            from .query_model import AttributeExpression

            attr_expr = AttributeExpression(
                table_name=self.table_name,
                attribute_path="",
                is_database_column=False,
            )
            return [SelectExpression(expression=attr_expr)]

        if isinstance(what, str):
            # Handle special cases
            if what in ["obj", "person"]:
                from .query_model import AttributeExpression

                attr_expr = AttributeExpression(
                    table_name=self.table_name,
                    attribute_path="",
                    is_database_column=False,
                )
                return [SelectExpression(expression=attr_expr)]

            # Parse as expression
            expr = self.parser.parse_expression(what)
            return [SelectExpression(expression=expr)]

        elif isinstance(what, list):
            select_exprs = []
            for w in what:
                if isinstance(w, str):
                    if w in ["obj", "person"]:
                        from .query_model import AttributeExpression

                        attr_expr = AttributeExpression(
                            table_name=self.table_name,
                            attribute_path="",
                            is_database_column=False,
                        )
                        select_exprs.append(SelectExpression(expression=attr_expr))
                    else:
                        expr = self.parser.parse_expression(w)
                        select_exprs.append(SelectExpression(expression=expr))
                else:
                    # Non-string - treat as expression (shouldn't happen normally)
                    expr = self.parser.parse_expression(str(w))
                    select_exprs.append(SelectExpression(expression=expr))
            return select_exprs

        else:
            # Fallback
            expr = self.parser.parse_expression(str(what))
            return [SelectExpression(expression=expr)]

    def _parse_order_by(self, order_by) -> List[OrderBy]:
        """Parse order_by clause into OrderBy objects."""
        if order_by is None:
            return []

        if isinstance(order_by, str):
            order_by = [order_by]

        order_by_list = []
        for expr in order_by:
            if isinstance(expr, types.LambdaType):
                raise ValueError(
                    "Lambda functions are not supported for SQL generation. Please use string expressions instead."
                )

            # Check for descending (starts with "-")
            if isinstance(expr, str) and expr.startswith("-"):
                direction = "DESC"
                expr_str = expr[1:]
            else:
                direction = "ASC"
                expr_str = str(expr)

            order_expr = self.parser.parse_expression(expr_str)
            order_by_list.append(OrderBy(expression=order_expr, direction=direction))

        return order_by_list

    def _extract_array_expansion_from_condition(
        self, condition: Expression
    ) -> Tuple[Optional[ArrayExpansion], bool]:
        """Extract array expansion from WHERE condition expression.

        This method traverses the expression tree to find ArrayExpansionExpression
        and determine if it's part of an OR expression (which requires UNION).

        Returns:
            Tuple of (ArrayExpansion object if found, whether it's in an OR expression)
        """
        from .query_model import (
            ArrayExpansionExpression,
            BoolOpExpression,
            ArrayExpansion,
        )

        array_expansion = None
        is_in_or = False

        def find_array_expansion(
            expr: Expression,
        ) -> Optional[ArrayExpansionExpression]:
            """Recursively find ArrayExpansionExpression in expression tree."""
            if isinstance(expr, ArrayExpansionExpression):
                return expr
            if isinstance(expr, BoolOpExpression):
                for value in expr.values:
                    found = find_array_expansion(value)
                    if found:
                        return found
            return None

        def check_if_in_or(expr: Expression, target: ArrayExpansionExpression) -> bool:
            """Check if target expression is part of an OR expression."""
            if isinstance(expr, BoolOpExpression):
                if expr.operator == "or":
                    # Check if target is in any of the OR values
                    for value in expr.values:
                        if find_array_expansion(value) == target:
                            return True
                # Recursively check nested expressions
                for value in expr.values:
                    if check_if_in_or(value, target):
                        return True
            return False

        # Find array expansion expression
        array_expansion_expr = find_array_expansion(condition)
        if array_expansion_expr:
            # Convert to ArrayExpansion object for use in query
            array_expansion = ArrayExpansion(
                item_var=array_expansion_expr.item_var,
                array_path=array_expansion_expr.array_path,
                array_expression=array_expansion_expr.array_expression,
            )

            # Check if it's in an OR expression
            is_in_or = check_if_in_or(condition, array_expansion_expr)

        return array_expansion, is_in_or

    def _deduplicate_joins(self, joins: List[Join]) -> List[Join]:
        """Deduplicate JOINs to the same table by combining conditions with OR.

        If multiple JOINs exist to the same table, combine their conditions
        into a single JOIN with an OR condition.
        """
        # Group joins by table name
        joins_by_table: Dict[str, List[Join]] = {}
        for join in joins:
            if join.table_name not in joins_by_table:
                joins_by_table[join.table_name] = []
            joins_by_table[join.table_name].append(join)

        # Combine joins to the same table
        deduplicated = []
        for table_name, table_joins in joins_by_table.items():
            if len(table_joins) == 1:
                # Single join - keep as-is
                deduplicated.append(table_joins[0])
            else:
                # Multiple joins to same table - combine conditions with OR
                # Use the first join as the base
                base_join = table_joins[0]
                conditions = [base_join.condition]
                for join in table_joins[1:]:
                    conditions.append(join.condition)

                # Combine all conditions with OR
                combined_condition = BoolOpExpression(
                    operator="or",
                    values=conditions,
                )

                # Create a single JOIN with combined condition
                deduplicated.append(
                    Join(
                        table_name=table_name,
                        join_type=base_join.join_type,
                        condition=combined_condition,
                    )
                )

        return deduplicated

    def _remove_array_expansion_condition(
        self, condition: Expression, array_expansion: ArrayExpansion
    ) -> Optional[Expression]:
        """Remove array expansion condition from WHERE clause expression.

        Returns the expression with array expansion conditions removed.
        Returns None if the entire expression was just the array expansion.
        """
        visitor = ArrayExpansionRemovalVisitor(array_expansion)
        result = visitor.visit(condition)
        return result

    def _remove_join_condition(
        self, condition: Expression, join_condition: Expression
    ) -> Optional[Expression]:
        """Remove join condition from WHERE clause expression.

        Returns the expression with join condition removed.
        Returns None if the entire expression was just the join condition.
        """
        visitor = ConditionRemovalVisitor(join_condition, self._expressions_equal)
        result = visitor.visit(condition)
        return result

    def _expressions_equal(self, expr1: Expression, expr2: Expression) -> bool:
        """Check if two expressions are equal (same structure and values)."""
        visitor = ExpressionEqualityVisitor(expr2)
        return visitor.visit(expr1)

    def _is_array_expansion_in_or(
        self, where_condition: Expression, array_expansion: ArrayExpansion
    ) -> bool:
        """Check if array expansion is part of an OR expression."""
        if not isinstance(where_condition, BoolOpExpression):
            return False

        if where_condition.operator != "or":
            return False

        # Check if any value contains the array expansion
        for value in where_condition.values:
            if self._contains_array_expansion(value, array_expansion):
                return True

        return False

    def _contains_array_expansion(
        self, expr: Expression, array_expansion: ArrayExpansion
    ) -> bool:
        """Check if expression contains array expansion."""
        from .query_model import ArrayExpansionExpression, BoolOpExpression

        if isinstance(expr, ArrayExpansionExpression):
            return (
                expr.item_var == array_expansion.item_var
                and expr.array_path == array_expansion.array_path
            )

        if isinstance(expr, BoolOpExpression):
            for value in expr.values:
                if self._contains_array_expansion(value, array_expansion):
                    return True

        return False

    def _build_union_query(
        self,
        select_expressions: List[SelectExpression],
        where_condition: Optional[Expression],
        order_by_list: List[OrderBy],
        array_expansion: ArrayExpansion,
        joins: List[Join],
        page: Optional[int],
        page_size: Optional[int],
    ) -> str:
        """Build UNION query for array expansion in OR expressions."""
        if not isinstance(where_condition, BoolOpExpression):
            # Shouldn't happen if we got here
            raise ValueError("Expected BoolOpExpression for UNION query")

        # Split OR expression into parts with and without array expansion
        left_parts = []
        right_parts = []

        for value in where_condition.values:
            if self._contains_array_expansion(value, array_expansion):
                right_parts.append(value)
            else:
                left_parts.append(value)

        if not left_parts or not right_parts:
            # Can't split - fall back to regular query
            query = SelectQuery(
                base_table=self.table_name,
                select_expressions=select_expressions,
                where_condition=where_condition,
                joins=joins,
                order_by=order_by_list,
                array_expansion=array_expansion,
                limit=page_size if page_size is not None else None,
                offset=(
                    (page - 1) * page_size
                    if page is not None and page_size is not None
                    else None
                ),
            )
            return self.generator.generate(query)

        # Build left query (no array expansion)
        if len(left_parts) == 1:
            left_where = left_parts[0]
        else:
            left_where = BoolOpExpression(operator="and", values=left_parts)

        left_query = SelectQuery(
            base_table=self.table_name,
            select_expressions=select_expressions,
            where_condition=left_where,
            joins=joins,
            order_by=order_by_list,
            array_expansion=None,
            limit=page_size if page_size is not None else None,
            offset=(
                (page - 1) * page_size
                if page is not None and page_size is not None
                else None
            ),
        )

        # Build right query (with array expansion)
        if len(right_parts) == 1:
            right_where = right_parts[0]
        else:
            right_where = BoolOpExpression(operator="and", values=right_parts)

        right_query = SelectQuery(
            base_table=self.table_name,
            select_expressions=select_expressions,
            where_condition=right_where,
            joins=joins,
            order_by=order_by_list,
            array_expansion=array_expansion,
            limit=page_size if page_size is not None else None,
            offset=(
                (page - 1) * page_size
                if page is not None and page_size is not None
                else None
            ),
        )

        # Generate SQL for both queries
        left_sql = self.generator._generate_select(left_query).rstrip(";")
        right_sql = self.generator._generate_select(right_query).rstrip(";")

        return f"{left_sql} UNION {right_sql};"

    def _handle_list_comprehensions(self, query: SelectQuery, what) -> SelectQuery:
        """Handle list comprehensions in what clause."""
        # Check if any select expression is a list comprehension with concatenated arrays
        for sel_expr in query.select_expressions:
            if isinstance(sel_expr.expression, ListComprehensionExpression):
                listcomp = sel_expr.expression
                if listcomp.array_info.get("type") == "concatenated":
                    # Need to generate UNION query for concatenated arrays
                    # This is handled in the generator, but we need to mark it
                    # For SQLite, we'll create union queries
                    if self.dialect == "sqlite":
                        # Create two separate queries and combine with UNION ALL
                        left_query, right_query = (
                            self._build_concatenated_array_queries(query, listcomp)
                        )
                        # Set union_queries on left_query, then return left_query
                        left_query.union_queries = [right_query]
                        return left_query
                    elif self.dialect == "postgres":
                        # For PostgreSQL, use LATERAL joins with UNION ALL in subquery
                        # This is handled in the SQL generator
                        # For now, use the same UNION approach as SQLite
                        left_query, right_query = (
                            self._build_concatenated_array_queries(query, listcomp)
                        )
                        left_query.union_queries = [right_query]
                        return left_query

        return query

    def _build_concatenated_array_queries(
        self, query: SelectQuery, listcomp: ListComprehensionExpression
    ) -> tuple:
        """Build left and right queries for concatenated arrays."""
        from .query_model import (
            AttributeExpression,
            ArrayExpansion,
            BinaryOpExpression,
            ConstantExpression,
            CallExpression,
        )

        # Left query: from [person.primary_name]
        # The left side needs to be wrapped in json_array() since it's a single item
        left_array_attr = AttributeExpression(
            table_name=self.table_name,
            attribute_path="primary_name",
            is_database_column=False,
        )
        # Create a special expression that represents json_array(left_array_attr)
        # This will be used in the FROM clause
        left_array_wrapped = CallExpression(
            function=ConstantExpression(value="json_array"),
            arguments=[left_array_attr],
        )
        left_array_expansion = ArrayExpansion(
            item_var=listcomp.item_var,
            array_path="primary_name",
            array_expression=left_array_wrapped,
        )

        left_select_expr = SelectExpression(expression=listcomp.expression)

        left_query = SelectQuery(
            base_table=self.table_name,
            select_expressions=[left_select_expr],
            where_condition=query.where_condition,
            joins=query.joins,
            order_by=query.order_by,
            array_expansion=left_array_expansion,
            limit=query.limit,
            offset=query.offset,
        )

        # Right query: from person.alternate_names
        right_path = listcomp.array_info["right_path"]
        right_array_attr = AttributeExpression(
            table_name=self.table_name,
            attribute_path=right_path,
            is_database_column=False,
        )
        right_array_expansion = ArrayExpansion(
            item_var=listcomp.item_var,
            array_path=right_path,
            array_expression=right_array_attr,
        )

        right_select_expr = SelectExpression(expression=listcomp.expression)

        right_query = SelectQuery(
            base_table=self.table_name,
            select_expressions=[right_select_expr],
            where_condition=query.where_condition,
            joins=query.joins,
            order_by=query.order_by,
            array_expansion=right_array_expansion,
            limit=query.limit,
            offset=query.offset,
        )

        return left_query, right_query

    def normalize_expression(self, expr: Expression) -> Optional[Expression]:
        """
        Normalize an expression tree by flattening nested AND/OR and optimizing comparisons.

        Args:
            expr: Expression to normalize

        Returns:
            Normalized expression, or None if expression becomes empty
        """
        visitor = ExpressionNormalizationVisitor()
        return visitor.visit(expr)

    def validate_expression(self, expr: Expression) -> bool:
        """
        Recursively validate that an expression tree is well-formed.

        Args:
            expr: Expression to validate

        Returns:
            True if expression is valid, False otherwise
        """
        visitor = ExpressionValidationVisitor()
        try:
            visitor.visit(expr)
            return True
        except ValueError:
            return False

    def validate_types(self, expr: Expression) -> Tuple[bool, Optional[str]]:
        """
        Validate expression types using type hints.

        Args:
            expr: Expression to validate

        Returns:
            Tuple of (is_valid, error_message)
            - is_valid: True if types are valid, False otherwise
            - error_message: Error message if invalid, None if valid
        """
        if not self.enable_type_validation or not self.type_inference:
            return True, None

        validator = TypeValidationVisitor(self.type_inference)
        try:
            validator.visit(expr)
            return True, None
        except ValueError as e:
            return False, str(e)

    # Compatibility methods (kept for backward compatibility)
    def format_json_extract(self, base_expr):
        """Format JSON extract expression based on dialect."""
        if self.dialect == "sqlite":
            return f"json_extract({base_expr}, '$.{{attr}}')"
        elif self.dialect == "postgres":
            return f"JSON_EXTRACT_PATH({base_expr}, '{{attr}}')"
        else:
            return f"json_extract({base_expr}, '$.{{attr}}')"

    def format_json_array_length(self, base_expr):
        """Format JSON array length expression based on dialect."""
        if self.dialect == "sqlite":
            return f"json_array_length(json_extract({base_expr}, '$.{{attr}}'))"
        elif self.dialect == "postgres":
            return f"JSON_ARRAY_LENGTH(JSON_EXTRACT_PATH({base_expr}, '{{attr}}'))"
        else:
            return f"json_array_length(json_extract({base_expr}, '$.{{attr}}'))"

    def format_json_each(self, array_expr, path="$"):
        """Format json_each expression based on dialect."""
        if self.dialect == "sqlite":
            return f"json_each({array_expr}, '{path}')"
        elif self.dialect == "postgres":
            return f"LATERAL json_array_elements({array_expr}) AS json_each(value)"
        else:
            return f"json_each({array_expr}, '{path}')"

    def format_json_array(self, *args):
        """Format json_array expression based on dialect."""
        if self.dialect == "sqlite":
            if len(args) == 0:
                return "json_array()"
            args_str = ", ".join(str(arg) for arg in args)
            return f"json_array({args_str})"
        elif self.dialect == "postgres":
            if len(args) == 0:
                return "json_build_array()"
            args_str = ", ".join(str(arg) for arg in args)
            return f"json_build_array({args_str})"
        else:
            if len(args) == 0:
                return "json_array()"
            args_str = ", ".join(str(arg) for arg in args)
            return f"json_array({args_str})"

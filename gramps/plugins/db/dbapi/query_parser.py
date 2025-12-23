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
Query Parser

Converts Python AST nodes to query model objects.
This provides a clean separation between parsing and SQL generation.
"""

import ast
from typing import Optional, List, Set, Dict, Tuple

import gramps.gen.lib

from .query_model import (
    Expression,
    ConstantExpression,
    AttributeExpression,
    ArrayAccessExpression,
    BinaryOpExpression,
    UnaryOpExpression,
    CompareExpression,
    BoolOpExpression,
    CallExpression,
    IfExpression,
    ListComprehensionExpression,
    AnyExpression,
    ArrayExpansionExpression,
    TupleExpression,
    Join,
    OrderBy,
    SelectExpression,
    ArrayExpansion,
    SelectQuery,
)

TABLE_NAMES = {
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
}


class QueryParser:
    """Converts AST nodes to query model objects."""

    def __init__(
        self,
        table_name: str,
        env: Optional[Dict] = None,
        item_var: Optional[str] = None,
        array_path: Optional[str] = None,
        database_columns: Optional[Set[str]] = None,
        database_columns_dict: Optional[Dict[str, List[str]]] = None,
    ):
        """
        Initialize the parser.

        Args:
            table_name: Base table name (e.g., "person")
            env: Environment dictionary for constants (e.g., Person.MALE)
            item_var: Variable name for array iteration (e.g., "item")
            array_path: Array path for array iteration (e.g., "event_ref_list")
            database_columns: Set of database column names for this table
            database_columns_dict: Dict mapping table names to their database columns
        """
        self.table_name = table_name
        self.env = {}
        # Add Gramps classes to environment
        for key in dir(gramps.gen.lib):
            if key[0].isupper():
                self.env[key] = getattr(gramps.gen.lib, key)
        if env:
            self.env.update(env)
        self.item_var = item_var
        self.array_path = array_path
        self.database_columns = database_columns or set()
        self.database_columns_dict = database_columns_dict or {}

    def parse_expression(self, expr_str: str) -> Expression:
        """
        Parse a Python expression string into an Expression object.

        Args:
            expr_str: Python expression as string

        Returns:
            Expression object
        """
        if not expr_str or not isinstance(expr_str, str):
            raise ValueError(f"Invalid expression: {expr_str}")

        try:
            tree = ast.parse(expr_str, mode="eval")
            return self._parse_node(tree.body)
        except SyntaxError as e:
            raise ValueError(f"Invalid expression syntax: {expr_str}") from e
        except AttributeError as e:
            raise ValueError(f"Invalid expression structure: {expr_str}") from e

    def _parse_node(self, node: ast.AST) -> Expression:
        """Recursively parse an AST node into an Expression."""
        if isinstance(node, ast.Constant):
            # Filter value to supported types (str, int, float, bool, None)
            value = node.value
            if isinstance(value, (str, int, float, bool)) or value is None:
                return ConstantExpression(value=value)
            # For unsupported types (bytes, complex, Ellipsis), convert or raise
            if isinstance(value, bytes):
                return ConstantExpression(value=value.decode("utf-8"))
            # For other types, convert to string representation
            return ConstantExpression(value=str(value))
        elif isinstance(node, ast.BinOp):
            return self._parse_binop(node)
        elif isinstance(node, ast.UnaryOp):
            return self._parse_unaryop(node)
        elif isinstance(node, ast.Compare):
            return self._parse_compare(node)
        elif isinstance(node, ast.BoolOp):
            return self._parse_boolop(node)
        elif isinstance(node, ast.Call):
            return self._parse_call(node)
        elif isinstance(node, ast.IfExp):
            return IfExpression(
                test=self._parse_node(node.test),
                body=self._parse_node(node.body),
                orelse=self._parse_node(node.orelse),
            )
        elif isinstance(node, ast.Attribute):
            return self._parse_attribute(node)
        elif isinstance(node, ast.Subscript):
            return self._parse_subscript(node)
        elif isinstance(node, ast.Name):
            return self._parse_name(node)
        elif isinstance(node, ast.List):
            return self._parse_list(node)
        elif isinstance(node, ast.Tuple):
            return TupleExpression(
                elements=[self._parse_node(elt) for elt in node.elts]
            )
        elif isinstance(node, ast.ListComp):
            return self._parse_listcomp(node)
        else:
            raise ValueError(f"Unsupported AST node type: {type(node)}")

    def _parse_binop(self, node: ast.BinOp) -> BinaryOpExpression:
        """Parse binary operation."""
        op_map = {
            ast.Add: "+",
            ast.Sub: "-",
            ast.Mult: "*",
            ast.Div: "/",
            ast.Mod: "%",
            ast.Pow: "**",
            ast.FloorDiv: "//",
        }
        operator = op_map.get(type(node.op))
        if not operator:
            raise ValueError(f"Unsupported binary operator: {type(node.op)}")
        return BinaryOpExpression(
            operator=operator,
            left=self._parse_node(node.left),
            right=self._parse_node(node.right),
        )

    def _parse_unaryop(self, node: ast.UnaryOp) -> UnaryOpExpression:
        """Parse unary operation."""
        op_map = {
            ast.USub: "-",
            ast.Not: "not",
        }
        operator = op_map.get(type(node.op))
        if not operator:
            raise ValueError(f"Unsupported unary operator: {type(node.op)}")
        return UnaryOpExpression(
            operator=operator, operand=self._parse_node(node.operand)
        )

    def _parse_compare(self, node: ast.Compare) -> Expression:
        """Parse comparison operation."""
        # Check if this is an array expansion pattern: item in person.array
        if len(node.ops) == 1 and isinstance(node.ops[0], ast.In):
            left = node.left
            right = node.comparators[0] if node.comparators else None

            # Check if left is a name (item variable)
            if isinstance(left, ast.Name):
                item_var = left.id

                # Check if right is an attribute path (person.array_path)
                if isinstance(right, ast.Attribute):
                    # Build the full path
                    path_parts: List[str] = []
                    current: ast.AST = right
                    while isinstance(current, ast.Attribute):
                        path_parts.insert(0, current.attr)
                        current = current.value

                    # Check if it starts with table name
                    if isinstance(current, ast.Name) and current.id in [
                        self.table_name,
                        "obj",
                        "person",
                    ]:
                        array_path = ".".join(path_parts)
                        # Parse the array expression
                        array_expr = self.parse_expression(
                            f"{self.table_name}.{array_path}"
                        )
                        # Return as ArrayExpansionExpression instead of CompareExpression
                        return ArrayExpansionExpression(
                            item_var=item_var,
                            array_path=array_path,
                            array_expression=array_expr,
                        )

        # Regular comparison
        op_map = {
            ast.Eq: "==",
            ast.NotEq: "!=",
            ast.Lt: "<",
            ast.Gt: ">",
            ast.LtE: "<=",
            ast.GtE: ">=",
            ast.Is: "is",
            ast.IsNot: "is not",
            ast.In: "in",
            ast.NotIn: "not in",
        }
        operators = [op_map.get(type(op), str(op)) for op in node.ops]
        comparators = [self._parse_node(comp) for comp in node.comparators]
        return CompareExpression(
            left=self._parse_node(node.left),
            operators=operators,
            comparators=comparators,
        )

    def _parse_boolop(self, node: ast.BoolOp) -> BoolOpExpression:
        """Parse boolean operation."""
        op_map = {ast.And: "and", ast.Or: "or"}
        operator = op_map.get(type(node.op))
        if not operator:
            raise ValueError(f"Unsupported boolean operator: {type(node.op)}")
        return BoolOpExpression(
            operator=operator,
            values=[self._parse_node(value) for value in node.values],
        )

    def _parse_call(self, node: ast.Call) -> Expression:
        """Parse function call."""
        func = self._parse_node(node.func)
        args = [self._parse_node(arg) for arg in node.args]

        # Check for special functions
        if isinstance(func, AttributeExpression):
            # Method call like attribute.startswith('x')
            if func.attribute_path.endswith(
                ".startswith"
            ) or func.attribute_path.endswith(".endswith"):
                return CallExpression(function=func, arguments=args)
        elif isinstance(func, ConstantExpression):
            # Built-in function like len(), any()
            func_name = func.value
            if func_name == "len" and len(args) == 1:
                # len() is handled specially - it becomes a call to get_length()
                # But we'll represent it as a CallExpression
                return CallExpression(
                    function=ConstantExpression(value="len"), arguments=args
                )
            elif func_name == "any" and len(args) == 1:
                # any() with list comprehension - check if arg is a list comprehension
                if isinstance(node.args[0], ast.ListComp):
                    # Parse the list comprehension
                    listcomp = self._parse_listcomp(node.args[0])
                    return AnyExpression(
                        item_var=listcomp.item_var,
                        array_path=listcomp.array_info.get("path", ""),
                        condition=listcomp.condition,
                    )

        return CallExpression(function=func, arguments=args)

    def _parse_attribute(self, node: ast.Attribute) -> Expression:
        """Parse attribute access."""
        # Build the full attribute path
        path_parts: List[str] = []
        current: ast.AST = node
        while isinstance(current, ast.Attribute):
            path_parts.insert(0, current.attr)
            current = current.value

        # Determine table name and attribute path
        if isinstance(current, ast.Name):
            name = current.id
            # Check if it's the item variable from array expansion FIRST
            if self.item_var and name == self.item_var:
                # This is item.attr - reference json_each.value
                attribute_path = ".".join(path_parts)
                return AttributeExpression(
                    table_name="json_each",
                    attribute_path=attribute_path,
                    is_database_column=False,
                )
            # Check if it's in environment (class constant) BEFORE checking table names
            # This is important because "Person" could match both a class and a table name
            elif name in self.env:
                # This is a class constant like Person.MALE or Person.UNKNOWN
                # Get the attribute value from the class
                if path_parts:
                    attr_value = getattr(self.env[name], path_parts[0])
                    return ConstantExpression(value=attr_value)
                else:
                    # Just the class name - return the class itself
                    return ConstantExpression(value=self.env[name])
            # Check if it's a table name
            elif name.lower() in TABLE_NAMES:
                table_name = name.lower()
                attribute_path = ".".join(path_parts)
                # Check if it's a database column
                is_db_column = self._is_database_column(table_name, attribute_path)
                return AttributeExpression(
                    table_name=table_name,
                    attribute_path=attribute_path,
                    is_database_column=is_db_column,
                )
            else:
                # Unknown name - treat as table reference if lowercase
                if name.islower() and name in TABLE_NAMES:
                    table_name = name
                    attribute_path = ".".join(path_parts)
                    is_db_column = self._is_database_column(table_name, attribute_path)
                    return AttributeExpression(
                        table_name=table_name,
                        attribute_path=attribute_path,
                        is_database_column=is_db_column,
                    )
        elif isinstance(current, ast.Subscript):
            # This is array[index].attr - parse the subscript first
            base = self._parse_subscript(current)
            # Then add the attribute to the path
            if isinstance(base, ArrayAccessExpression):
                # Add attribute to the base
                if isinstance(base.base, AttributeExpression):
                    # For constant indices, we can extend the path directly
                    if base.is_constant_index:
                        index_str = self._index_to_string(
                            base.index, base.is_constant_index
                        )
                        extended_path = f"{base.base.attribute_path}[{index_str}].{'.'.join(path_parts)}"
                        return AttributeExpression(
                            table_name=base.base.table_name,
                            attribute_path=extended_path,
                            is_database_column=base.base.is_database_column,
                        )
                    else:
                        # For variable indices, create an AttributeExpression with the array access as base
                        # This allows the SQL generator to handle it recursively
                        attr_path = ".".join(path_parts)
                        return AttributeExpression(
                            table_name=base.base.table_name,
                            attribute_path=attr_path,
                            is_database_column=base.base.is_database_column,
                            base=base,  # The array access expression becomes the base
                        )
            # If base is not an ArrayAccessExpression with AttributeExpression,
            # create an AttributeExpression with the base as the base expression
            if path_parts:
                attr_path = ".".join(path_parts)
                # Determine table_name from base if possible
                table_name = self.table_name
                if isinstance(base, AttributeExpression):
                    table_name = base.table_name
                return AttributeExpression(
                    table_name=table_name,
                    attribute_path=attr_path,
                    is_database_column=False,
                    base=base,
                )
            return base

        # Fallback: treat as attribute of the base table
        if path_parts:
            attribute_path = ".".join(path_parts)
            is_db_column = self._is_database_column(self.table_name, attribute_path)
            return AttributeExpression(
                table_name=self.table_name,
                attribute_path=attribute_path,
                is_database_column=is_db_column,
            )

        raise ValueError(f"Could not parse attribute: {node}")

    def _parse_subscript(self, node: ast.Subscript) -> Expression:
        """Parse subscript (array access)."""
        base = self._parse_node(node.value)

        # Get index - in Python 3.9+, slice is directly the value
        index_node = node.slice
        index = self._parse_node(index_node)
        is_constant = isinstance(index, ConstantExpression)

        return ArrayAccessExpression(
            base=base, index=index, is_constant_index=is_constant
        )

    def _index_to_string(self, index: Expression, is_constant: bool) -> str:
        """Convert index expression to string for use in JSON path."""
        if is_constant and isinstance(index, ConstantExpression):
            return str(index.value)
        else:
            # Variable index - this shouldn't be used in path strings
            # but we'll return a placeholder
            return "*"

    def _parse_name(self, node: ast.Name) -> Expression:
        """Parse name (variable, constant, table reference)."""
        name = node.id

        # Check if it's the item variable from array expansion
        if self.item_var and name == self.item_var:
            return AttributeExpression(
                table_name="json_each",
                attribute_path="",
                is_database_column=False,
            )

        # Check if it's in environment (class constant)
        if name in self.env:
            return ConstantExpression(value=self.env[name])

        # Check if it's a table name
        if name.lower() in TABLE_NAMES:
            return AttributeExpression(
                table_name=name.lower(),
                attribute_path="",
                is_database_column=False,
            )

        # Unknown name - return as string constant
        return ConstantExpression(value=name)

    def _parse_list(self, node: ast.List) -> Expression:
        """Parse list literal."""
        elements = [self._parse_node(elt) for elt in node.elts]
        if len(elements) == 1:
            # Single element list - might be used for concatenation
            return TupleExpression(elements=elements)
        return TupleExpression(elements=elements)

    def _parse_listcomp(self, node: ast.ListComp) -> ListComprehensionExpression:
        """Parse list comprehension."""
        if len(node.generators) != 1:
            raise ValueError("List comprehensions must have exactly one generator")

        gen = node.generators[0]
        if not isinstance(gen.target, ast.Name):
            raise ValueError("List comprehension target must be a name")

        item_var = gen.target.id
        iter_node = gen.iter

        # Extract array info
        array_info = self._extract_array_info(iter_node)

        # Extract expression with item_var context
        # Temporarily set item_var so that the expression can reference it
        old_item_var = self.item_var
        old_array_path = self.array_path
        self.item_var = item_var
        self.array_path = array_info.get("path", "")
        try:
            expression = self._parse_node(node.elt)
            # Extract condition with item_var context
            condition = None
            if gen.ifs:
                condition = self._parse_node(gen.ifs[0])
        finally:
            # Restore old values
            self.item_var = old_item_var
            self.array_path = old_array_path

        return ListComprehensionExpression(
            expression=expression,
            item_var=item_var,
            array_info=array_info,
            condition=condition,
        )

    def _extract_array_info(self, iter_node: ast.AST) -> dict:
        """Extract array information from iteration node."""
        # Check for concatenated arrays: [something] + array_path
        if isinstance(iter_node, ast.BinOp) and isinstance(iter_node.op, ast.Add):
            left = iter_node.left
            right = iter_node.right

            # Check if left is a list with one element
            if isinstance(left, ast.List) and len(left.elts) == 1:
                left_item = left.elts[0]
                if isinstance(left_item, ast.Attribute):
                    # Check if right is an attribute path
                    if isinstance(right, ast.Attribute):
                        # Build right path
                        path_parts: List[str] = []
                        current: ast.AST = right
                        while isinstance(current, ast.Attribute):
                            path_parts.insert(0, current.attr)
                            current = current.value

                        if isinstance(current, ast.Name) and current.id in [
                            self.table_name,
                            "obj",
                            "person",
                        ]:
                            right_path = ".".join(path_parts)
                            return {
                                "type": "concatenated",
                                "left": self._parse_node(left_item),
                                "right_path": right_path,
                            }

        # Check for simple array path
        if isinstance(iter_node, ast.Attribute):
            simple_path_parts: List[str] = []
            simple_current: ast.AST = iter_node
            while isinstance(simple_current, ast.Attribute):
                simple_path_parts.insert(0, simple_current.attr)
                simple_current = simple_current.value

            if isinstance(simple_current, ast.Name) and simple_current.id in [
                self.table_name,
                "obj",
                "person",
            ]:
                array_path = ".".join(simple_path_parts)
                return {"type": "single", "path": array_path}

        raise ValueError(f"Could not extract array info from: {iter_node}")

    def detect_array_expansion(self, expr_str: str) -> Optional[ArrayExpansion]:
        """Detect array expansion pattern in expression."""
        try:
            tree = ast.parse(expr_str, mode="eval")
            result = self._extract_array_expansion_from_node(tree.body)
            if result:
                item_var, array_path = result
                # Parse the array expression
                array_expr = self.parse_expression(f"{self.table_name}.{array_path}")
                return ArrayExpansion(
                    item_var=item_var,
                    array_path=array_path,
                    array_expression=array_expr,
                )
        except (SyntaxError, AttributeError, ValueError):
            pass
        return None

    def _extract_array_expansion_from_node(
        self, node: ast.AST
    ) -> Optional[Tuple[str, str]]:
        """Extract array expansion pattern from AST node."""
        # Look for Compare node with "in" operator
        if isinstance(node, ast.Compare):
            if len(node.ops) == 1 and isinstance(node.ops[0], ast.In):
                left = node.left
                right = node.comparators[0]

                # Left should be a Name (the item variable)
                if isinstance(left, ast.Name):
                    item_var = left.id

                    # Right should be an Attribute (e.g., person.event_ref_list)
                    if isinstance(right, ast.Attribute):
                        # Build the full path
                        path_parts: List[str] = []
                        current: ast.AST = right
                        while isinstance(current, ast.Attribute):
                            path_parts.insert(0, current.attr)
                            current = current.value

                        if isinstance(current, ast.Name) and current.id in [
                            self.table_name,
                            "obj",
                            "person",
                        ]:
                            array_path = ".".join(path_parts)
                            return item_var, array_path

        # Check inside BoolOp
        if isinstance(node, ast.BoolOp):
            for value in node.values:
                result = self._extract_array_expansion_from_node(value)
                if result:
                    return result

        return None

    def detect_table_references(self, expr_str: str) -> Set[str]:
        """Detect table references in expression."""
        referenced_tables: Set[str] = set()
        try:
            tree = ast.parse(expr_str, mode="eval")
            self._extract_table_references_from_node(tree.body, referenced_tables)
        except (SyntaxError, AttributeError):
            pass
        return referenced_tables

    def _extract_table_references_from_node(
        self, node: ast.AST, referenced_tables: Set[str]
    ) -> None:
        """Recursively extract table references from AST node."""
        if isinstance(node, ast.Attribute):
            obj = node.value
            if isinstance(obj, ast.Name):
                if obj.id.islower() and obj.id in TABLE_NAMES:
                    if obj.id != self.table_name:
                        referenced_tables.add(obj.id)
            if not (isinstance(obj, ast.Name) and obj.id[0].isupper()):
                self._extract_table_references_from_node(obj, referenced_tables)

        elif isinstance(node, ast.Compare):
            self._extract_table_references_from_node(node.left, referenced_tables)
            for comparator in node.comparators:
                self._extract_table_references_from_node(comparator, referenced_tables)

        elif isinstance(node, ast.BoolOp):
            for value in node.values:
                self._extract_table_references_from_node(value, referenced_tables)

        elif isinstance(node, ast.BinOp):
            self._extract_table_references_from_node(node.left, referenced_tables)
            self._extract_table_references_from_node(node.right, referenced_tables)

        elif isinstance(node, ast.UnaryOp):
            self._extract_table_references_from_node(node.operand, referenced_tables)

        elif isinstance(node, ast.Call):
            self._extract_table_references_from_node(node.func, referenced_tables)
            for arg in node.args:
                self._extract_table_references_from_node(arg, referenced_tables)

        elif isinstance(node, ast.ListComp):
            self._extract_table_references_from_node(node.elt, referenced_tables)
            for gen in node.generators:
                self._extract_table_references_from_node(gen.iter, referenced_tables)
                for if_expr in gen.ifs:
                    self._extract_table_references_from_node(if_expr, referenced_tables)

    def detect_joins(self, expr_str: str) -> List[Join]:
        """Detect JOIN conditions from expression."""
        joins: List[Join] = []
        try:
            tree = ast.parse(expr_str, mode="eval")
            self._extract_joins_from_node(tree.body, joins)
        except (SyntaxError, AttributeError):
            pass
        return joins

    def _extract_joins_from_node(self, node: ast.AST, joins: List[Join]) -> None:
        """Recursively extract JOIN conditions from AST node."""
        if isinstance(node, ast.Compare):
            # Check for equality comparisons between table attributes
            if len(node.ops) == 1 and isinstance(node.ops[0], ast.Eq):
                left = node.left
                right = node.comparators[0]

                # Try to extract table.attr from both sides
                left_table, left_attr = self._extract_table_attr(left)
                right_table, right_attr = self._extract_table_attr(right)

                # Check if one side is from array expansion (json_each) and the other is a table
                # This handles cases like item.ref == event.handle
                if (
                    left_table == "json_each"
                    and right_table
                    and right_table in TABLE_NAMES
                    and left_attr
                    and right_attr
                    and self._is_handle_field(left_attr)
                    and self._is_handle_field(right_attr)
                ):
                    # Found a join from array expansion item to a table
                    ref_table = right_table
                    if ref_table != self.table_name:
                        join_condition = self._parse_node(node)
                        joins.append(
                            Join(
                                table_name=ref_table,
                                join_type="INNER",
                                condition=join_condition,
                            )
                        )
                elif (
                    right_table == "json_each"
                    and left_table
                    and left_table in TABLE_NAMES
                    and left_attr
                    and right_attr
                    and self._is_handle_field(left_attr)
                    and self._is_handle_field(right_attr)
                ):
                    # Found a join from a table to array expansion item
                    ref_table = left_table
                    if ref_table != self.table_name:
                        join_condition = self._parse_node(node)
                        joins.append(
                            Join(
                                table_name=ref_table,
                                join_type="INNER",
                                condition=join_condition,
                            )
                        )
                elif (
                    left_table
                    and right_table
                    and left_attr
                    and right_attr
                    and self._is_handle_field(left_attr)
                    and self._is_handle_field(right_attr)
                ):
                    # Found a valid handle-based join condition between tables
                    if left_table in [self.table_name] or right_table in [
                        self.table_name
                    ]:
                        ref_table = (
                            right_table if left_table == self.table_name else left_table
                        )
                        if ref_table != self.table_name:
                            join_condition = self._parse_node(node)
                            joins.append(
                                Join(
                                    table_name=ref_table,
                                    join_type="INNER",
                                    condition=join_condition,
                                )
                            )

        elif isinstance(node, ast.BoolOp):
            for value in node.values:
                self._extract_joins_from_node(value, joins)

    def _extract_table_attr(self, node: ast.AST) -> Tuple[Optional[str], Optional[str]]:
        """Extract table name and attribute path from AST node."""
        # Handle attribute access after subscript (e.g., array[index].attr)
        if isinstance(node, ast.Attribute):
            # Check if the value is a subscript
            if isinstance(node.value, ast.Subscript):
                # Extract from subscript first
                table_name, base_expr = self._extract_table_attr(node.value)
                if table_name:
                    # Add the attribute to the path
                    attr_path = f"{base_expr}.{node.attr}"
                    return table_name, attr_path
            else:
                # Regular attribute chain
                path_parts: List[str] = []
                current: ast.AST = node
                while isinstance(current, ast.Attribute):
                    path_parts.insert(0, current.attr)
                    current = current.value

                if isinstance(current, ast.Name):
                    # Check if it's the item variable from array expansion
                    if self.item_var and current.id == self.item_var:
                        # This is item.attr from array expansion
                        # Return "json_each" as the table name to indicate it's from array expansion
                        attr_path = ".".join(path_parts)
                        return "json_each", attr_path

                    table_name = current.id.lower()
                    if table_name in TABLE_NAMES:
                        attr_path = ".".join(path_parts)
                        return table_name, attr_path

        elif isinstance(node, ast.Subscript):
            # Handle array indexing
            table_name, base_expr = self._extract_table_attr(node.value)
            if table_name:
                # Build full expression path
                # In Python 3.9+, slice is directly the value (no ast.Index wrapper)
                index_node = node.slice

                if isinstance(index_node, ast.Constant):
                    index_str = str(index_node.value)
                elif isinstance(index_node, ast.Attribute):
                    # Variable index
                    index_parts: List[str] = []
                    index_current: ast.AST = index_node
                    while isinstance(index_current, ast.Attribute):
                        index_parts.insert(0, index_current.attr)
                        index_current = index_current.value
                    if isinstance(index_current, ast.Name):
                        index_str = f"{index_current.id}.{'.'.join(index_parts)}"
                    else:
                        return None, None
                elif isinstance(index_node, ast.Name):
                    # Simple variable index
                    index_str = index_node.id
                else:
                    return None, None

                full_expr = f"{base_expr}[{index_str}]"
                return table_name, full_expr

        return None, None

    def _is_handle_field(self, attr_path: str) -> bool:
        """Check if attribute path is a handle field."""
        if not attr_path:
            return False
        return (
            attr_path == "handle"
            or attr_path == "ref"
            or attr_path.endswith("_handle")
            or attr_path.endswith(".ref")
        )

    def _is_database_column(self, table_name: str, attr_path: str) -> bool:
        """Check if attribute is a database column (not JSON field)."""
        # Check if this is the current table
        if table_name == self.table_name:
            # Get just the first part of the path (column name)
            column_name = attr_path.split(".")[0]
            return column_name in self.database_columns

        # For other tables (JOIN cases), check DATABASE_COLUMNS dict
        if self.database_columns_dict:
            class_name = table_name.capitalize()
            known_columns = self.database_columns_dict.get(class_name, [])
            column_name = attr_path.split(".")[0]
            return column_name in known_columns

        return False

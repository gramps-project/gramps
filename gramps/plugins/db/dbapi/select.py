#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2024 Douglas S. Blank <doug.blank@gmail.com>
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

import gramps.gen.lib
from gramps.gen.db.lambda_to_string import lambda_to_string

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


class AttributeNode:
    def __init__(self, json_extract, json_array_length, obj, attr):
        self.json_extract = json_extract
        self.json_array_length = json_array_length
        self.obj = obj
        self.attr = attr

    def __str__(self):
        return self.json_extract.format(
            attr=self.attr,
        )

    def remove_attribute(self):
        self.attr = self.attr.rsplit(".", 1)[0]

    def get_length(self):
        return self.json_array_length.format(
            attr=self.attr,
        )

    def __repr__(self):
        return "{obj}.{attr}".format(
            obj=self.obj,
            attr=self.attr,
        )


class ExpressionBuilder:
    """
    Python expression to SQL expression converter.
    """

    def __init__(
        self,
        table_name,
        json_extract,
        json_array_length,
        env,
        item_var=None,
        array_path=None,
    ):
        self.json_extract = json_extract
        self.json_array_length = json_array_length
        self.table_name = table_name
        self.env = {
            key: getattr(gramps.gen.lib, key)
            for key in [
                x for x in dir(gramps.gen.lib) if x[0] in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            ]
        }
        if env:
            self.env.update(env)
        self.item_var = (
            item_var  # Variable name for array iteration (e.g., "item", "event_ref")
        )
        self.array_path = (
            array_path  # Array path for json_each (e.g., "event_ref_list")
        )
        self.operators = {
            ast.Mod: "({leftOperand} % {rightOperand})",
            ast.Add: "({leftOperand} + {rightOperand})",
            ast.Sub: "({leftOperand} - {rightOperand})",
            ast.Mult: "({leftOperand} * {rightOperand})",
            ast.Div: "({leftOperand} / {rightOperand})",
            ast.Pow: "POW({leftOperand}, {rightOperand})",
            ast.Not: "not {operand}",
            ast.FloorDiv: "(CAST (({leftOperand} / {rightOperand}) AS INT))",
            ast.USub: "-{operand}",
        }

    @staticmethod
    def _ast_operator_to_string(op):
        """
        Convert an AST operator node to its string representation.

        Args:
            op: AST operator node (ast.And, ast.Or, etc.)

        Returns:
            String representation of the operator ("and" or "or")
        """
        if isinstance(op, ast.And):
            return "and"
        elif isinstance(op, ast.Or):
            return "or"
        else:
            # Unknown operator - raise error instead of silently defaulting
            raise ValueError(f"Unsupported boolean operator: {type(op).__name__}")

    def detect_table_references(self, expr_str, base_table=None):
        """
        Detect table references in an expression string.

        Looks for patterns like:
        - "family.handle"
        - "person.handle"
        - "event.handle"

        Args:
            expr_str: Expression string to analyze
            base_table: Base table name to exclude from results

        Returns:
            set: Set of table names referenced (excluding base_table)
        """
        if not expr_str or not isinstance(expr_str, str):
            return set()

        referenced_tables = set()

        try:
            tree = ast.parse(expr_str, mode="eval")
            self._extract_table_references_from_node(
                tree.body, referenced_tables, base_table
            )
        except SyntaxError as e:
            raise ValueError(
                f"Invalid expression syntax in table reference detection: {expr_str}"
            ) from e
        except AttributeError as e:
            raise ValueError(
                f"Invalid expression structure in table reference detection: {expr_str}"
            ) from e

        return referenced_tables

    def _extract_table_references_from_node(
        self, node, referenced_tables, base_table=None
    ):
        """
        Recursively extract table references from an AST node.

        Args:
            node: AST node to analyze
            referenced_tables: set to add table names to
            base_table: Base table name to skip (don't add to referenced_tables)
        """
        if isinstance(node, ast.Attribute):
            # Check if this is a table reference (e.g., "family.handle")
            # But skip if it's a class attribute access (e.g., "Person.MALE")
            obj = node.value
            if isinstance(obj, ast.Name):
                # Only treat as table reference if it's lowercase and matches table name
                # PascalCase names like "Person" are classes from env, not table references
                if obj.id.islower() and obj.id in TABLE_NAMES:
                    # Skip if it's the base table
                    if obj.id != base_table:
                        referenced_tables.add(obj.id)
            # Recursively check nested attributes (but skip class attribute chains)
            if isinstance(obj, ast.Name) and not (
                obj.id.islower() and obj.id in TABLE_NAMES
            ):
                # This is a class name, don't recurse into it
                pass
            else:
                self._extract_table_references_from_node(
                    obj, referenced_tables, base_table
                )

        elif isinstance(node, ast.Compare):
            # Check both left and right sides of comparisons
            self._extract_table_references_from_node(
                node.left, referenced_tables, base_table
            )
            for comparator in node.comparators:
                self._extract_table_references_from_node(
                    comparator, referenced_tables, base_table
                )

        elif isinstance(node, ast.BoolOp):
            # Check all values in boolean operations
            for value in node.values:
                self._extract_table_references_from_node(
                    value, referenced_tables, base_table
                )

        elif isinstance(node, ast.BinOp):
            # Check both operands
            self._extract_table_references_from_node(
                node.left, referenced_tables, base_table
            )
            self._extract_table_references_from_node(
                node.right, referenced_tables, base_table
            )

        elif isinstance(node, ast.UnaryOp):
            # Check operand
            self._extract_table_references_from_node(
                node.operand, referenced_tables, base_table
            )

        elif isinstance(node, ast.Call):
            # Check function and arguments
            self._extract_table_references_from_node(
                node.func, referenced_tables, base_table
            )
            for arg in node.args:
                self._extract_table_references_from_node(
                    arg, referenced_tables, base_table
                )

        elif isinstance(node, ast.ListComp):
            # Check list comprehension
            self._extract_table_references_from_node(
                node.elt, referenced_tables, base_table
            )
            for gen in node.generators:
                self._extract_table_references_from_node(
                    gen.iter, referenced_tables, base_table
                )
                for if_expr in gen.ifs:
                    self._extract_table_references_from_node(
                        if_expr, referenced_tables, base_table
                    )

    def determine_join_conditions(self, base_table, referenced_tables, where_str=None):
        """
        Determine JOIN conditions between tables based on explicit handle relationships.

        Only handle-based joins are allowed. Handle fields include:
        - 'handle' (the primary handle)
        - Any field ending in '_handle' (e.g., 'father_handle', 'mother_handle')

        Join conditions must be explicitly specified in the WHERE clause.
        Examples:
        - "person.handle == family.father_handle"
        - "family.mother_handle == person.handle"

        Args:
            base_table: The primary table name (e.g., "person")
            referenced_tables: Set of referenced table names (e.g., {"family"})
            where_str: WHERE clause string containing explicit join conditions

        Returns:
            dict: Mapping of table_name -> list of JOIN conditions
                 Each condition is a tuple: (left_table, left_attr, right_table, right_attr, join_type)
                 join_type is "INNER" by default
                 All attributes must be handle fields
                 Only includes tables with explicit join conditions found in where_str
        """
        join_conditions = {}

        # Try to extract explicit join conditions from WHERE clause first
        explicit_joins = {}
        if where_str:
            explicit_joins = self._extract_explicit_join_conditions(
                where_str, base_table, referenced_tables
            )

        # For each referenced table, determine join condition
        for ref_table in referenced_tables:
            if ref_table == base_table:
                continue  # Skip self-references

            # Only use explicit join conditions - require them to be specified in WHERE clause
            if ref_table in explicit_joins:
                join_conditions[ref_table] = explicit_joins[ref_table]
            # If no explicit join condition found, don't add a join condition
            # This means the query will fail if tables are referenced but not properly joined

        return join_conditions

    def _extract_explicit_join_conditions(
        self, where_str, base_table, referenced_tables
    ):
        """
        Extract explicit join conditions from WHERE clause.

        Only extracts join conditions where both sides are handle fields.
        Looks for patterns like:
        - "person.handle == family.father_handle"
        - "family.mother_handle == person.handle"

        Non-handle comparisons are ignored (e.g., "person.gender == family.type.value"
        will not be treated as a join condition).

        Returns:
            dict: Mapping of table_name -> list of JOIN conditions
        """
        explicit_joins = {}

        if not where_str:
            return explicit_joins

        try:
            tree = ast.parse(where_str, mode="eval")
            self._extract_joins_from_node(
                tree.body, base_table, referenced_tables, explicit_joins
            )
        except SyntaxError as e:
            raise ValueError(
                f"Invalid expression syntax in join condition extraction: {where_str}"
            ) from e
        except AttributeError as e:
            raise ValueError(
                f"Invalid expression structure in join condition extraction: {where_str}"
            ) from e

        return explicit_joins

    def _extract_joins_from_node(
        self, node, base_table, referenced_tables, explicit_joins
    ):
        """
        Recursively extract join conditions from AST node.

        Looks for equality comparisons between table attributes.
        Only accepts join conditions where both sides are handle fields.
        """
        if isinstance(node, ast.Compare):
            # Check for equality comparisons
            if len(node.ops) == 1 and isinstance(node.ops[0], ast.Eq):
                left = node.left
                right = node.comparators[0]

                # Try to extract table.attr from both sides
                left_table, left_attr = self._extract_table_attr(left)
                right_table, right_attr = self._extract_table_attr(right)

                if left_table and right_table and left_attr and right_attr:
                    # Only accept join conditions where both sides are handle fields
                    if not (
                        self._is_handle_field(left_attr)
                        and self._is_handle_field(right_attr)
                    ):
                        return  # Skip non-handle join conditions

                    # Found a valid handle-based join condition - determine which table is the referenced one
                    if left_table in referenced_tables and right_table == base_table:
                        if left_table not in explicit_joins:
                            explicit_joins[left_table] = []
                        explicit_joins[left_table].append(
                            (left_table, left_attr, right_table, right_attr, "INNER")
                        )
                    elif right_table in referenced_tables and left_table == base_table:
                        if right_table not in explicit_joins:
                            explicit_joins[right_table] = []
                        explicit_joins[right_table].append(
                            (left_table, left_attr, right_table, right_attr, "INNER")
                        )
                    elif (
                        left_table in referenced_tables
                        and right_table in referenced_tables
                    ):
                        # Both are referenced tables - store join condition under both
                        # to ensure it's found regardless of iteration order
                        # The tables_joined set in join processing prevents duplicates
                        join_cond = (
                            left_table,
                            left_attr,
                            right_table,
                            right_attr,
                            "INNER",
                        )
                        if left_table not in explicit_joins:
                            explicit_joins[left_table] = []
                        explicit_joins[left_table].append(join_cond)
                        if right_table not in explicit_joins:
                            explicit_joins[right_table] = []
                        explicit_joins[right_table].append(join_cond)

        # Recursively check boolean operations
        if isinstance(node, ast.BoolOp):
            for value in node.values:
                self._extract_joins_from_node(
                    value, base_table, referenced_tables, explicit_joins
                )

    def _extract_table_attr(self, node):
        """
        Extract table name and attribute from an AST node.

        Returns:
            tuple: (table_name, attr_path) or (None, None)
        """
        if isinstance(node, ast.Attribute):
            # Build attribute path
            attr_parts = []
            current = node
            while isinstance(current, ast.Attribute):
                attr_parts.insert(0, current.attr)
                current = current.value

            if isinstance(current, ast.Name):
                table_name = current.id.lower()
                attr_path = ".".join(attr_parts)
                return table_name, attr_path

        return None, None

    def _is_handle_field(self, attr_path):
        """
        Check if an attribute path represents a handle field.

        Handle fields are:
        - 'handle' (the primary handle)
        - 'ref' (reference handle, e.g., event_ref.ref, citation_ref.ref)
        - Any field ending in '_handle' (e.g., 'father_handle', 'mother_handle')

        Args:
            attr_path: Attribute path string (e.g., 'handle', 'ref', 'father_handle')

        Returns:
            bool: True if the attribute is a handle field
        """
        if not attr_path:
            return False
        # Check if it's exactly 'handle', 'ref', or ends with '_handle'
        return (
            attr_path == "handle" or attr_path == "ref" or attr_path.endswith("_handle")
        )

    def remove_join_conditions_from_where(self, where_str, join_conditions):
        """
        Remove join conditions from WHERE clause since they're in JOIN clauses.

        Args:
            where_str: WHERE clause string
            join_conditions: Dict of join conditions (from determine_join_conditions)

        Returns:
            Modified WHERE clause string with join conditions removed, or None if empty
        """
        if not where_str or not join_conditions:
            return where_str

        try:
            tree = ast.parse(where_str, mode="eval")
            result = self._remove_join_conditions_from_node(tree.body, join_conditions)
            if result is None:
                return None
            # Convert back to string by converting to SQL
            # We need to use a dummy evaluator to convert the remaining AST
            dummy_expression = ExpressionBuilder(
                self.table_name,
                self.json_extract,
                self.json_array_length,
                self.env,
            )
            sql_result = dummy_expression.convert_to_sql(result)
            result_str = (
                str(sql_result) if not isinstance(sql_result, str) else sql_result
            )
            return result_str if result_str and result_str.strip() else None
        except SyntaxError as e:
            raise ValueError(
                f"Invalid expression syntax when removing join conditions from WHERE clause: {where_str}"
            ) from e
        except AttributeError as e:
            raise ValueError(
                f"Invalid expression structure when removing join conditions from WHERE clause: {where_str}"
            ) from e

    def _remove_join_conditions_from_node(self, node, join_conditions):
        """
        Recursively remove join conditions from AST node.

        Returns:
            Modified AST node with join conditions removed, or None if node should be removed
        """
        if isinstance(node, ast.Compare):
            # Check if this is a join condition
            if len(node.ops) == 1 and isinstance(node.ops[0], ast.Eq):
                left = node.left
                right = node.comparators[0]

                left_table, left_attr = self._extract_table_attr(left)
                right_table, right_attr = self._extract_table_attr(right)

                if left_table and right_table and left_attr and right_attr:
                    # Check if this matches any join condition
                    for ref_table, conditions in join_conditions.items():
                        for cond in conditions:
                            (
                                cond_left_table,
                                cond_left_attr,
                                cond_right_table,
                                cond_right_attr,
                                _,
                            ) = cond
                            # Check if this comparison matches the join condition
                            if (
                                left_table == cond_left_table
                                and left_attr == cond_left_attr
                                and right_table == cond_right_table
                                and right_attr == cond_right_attr
                            ) or (
                                left_table == cond_right_table
                                and left_attr == cond_right_attr
                                and right_table == cond_left_table
                                and right_attr == cond_left_attr
                            ):
                                # This is a join condition - remove it
                                return None

        # Handle boolean operations
        if isinstance(node, ast.BoolOp):
            new_values = []
            for value in node.values:
                result = self._remove_join_conditions_from_node(value, join_conditions)
                if result is not None:
                    new_values.append(result)

            if not new_values:
                return None
            elif len(new_values) == 1:
                return new_values[0]
            else:
                # Create new BoolOp with remaining values
                return ast.BoolOp(op=node.op, values=new_values)

        # For other nodes, recursively process children
        if isinstance(node, ast.UnaryOp):
            result = self._remove_join_conditions_from_node(
                node.operand, join_conditions
            )
            if result is None:
                return None
            return ast.UnaryOp(op=node.op, operand=result)

        # For all other nodes, return as-is
        return node

    def detect_list_comprehension_in_what(self, what_expr):
        """
        Detect list comprehension pattern in what clause.

        Looks for patterns like:
        - "[event_ref.role.value for event_ref in person.event_ref_list if event_ref.role.value == 5]"

        Returns:
            tuple: (item_var, array_path, expression_node, condition_node) if pattern detected, (None, None, None, None) otherwise
            item_var: name of the iteration variable (e.g., "event_ref")
            array_path: path to the array attribute (e.g., "event_ref_list")
            expression_node: AST node for the expression to extract (e.g., event_ref.role.value)
            condition_node: AST node for the condition (e.g., event_ref.role.value == 5), or None if no condition
        """
        if not what_expr or not isinstance(what_expr, str):
            return None, None, None, None

        try:
            tree = ast.parse(what_expr, mode="eval")
            node = tree.body

            # Look for ListComp node (list comprehension)
            if isinstance(node, ast.ListComp):
                listcomp = node

                # List comprehension should have one generator
                if len(listcomp.generators) == 1:
                    gen = listcomp.generators[0]

                    # Extract iteration variable
                    if isinstance(gen.target, ast.Name):
                        item_var = gen.target.id
                    else:
                        return None, None, None, None

                    # Extract array path from iter
                    iter_node = gen.iter
                    array_path = None

                    if isinstance(iter_node, ast.Attribute):
                        # Build the full path
                        path_parts = []
                        current = iter_node
                        while isinstance(current, ast.Attribute):
                            path_parts.insert(0, current.attr)
                            current = current.value

                        if isinstance(current, ast.Name) and current.id in [
                            self.table_name,
                            "obj",
                            "person",
                        ]:
                            array_path = ".".join(path_parts)

                    # Extract expression (what to return)
                    expression = listcomp.elt

                    # Extract condition (if any)
                    condition = None
                    if gen.ifs:
                        # Take the first condition
                        condition = gen.ifs[0]

                    if item_var and array_path:
                        return item_var, array_path, expression, condition

        except SyntaxError as e:
            raise ValueError(
                f"Invalid expression syntax in list comprehension detection: {what_expr}"
            ) from e
        except AttributeError as e:
            raise ValueError(
                f"Invalid expression structure in list comprehension detection: {what_expr}"
            ) from e

        return None, None, None, None

    def detect_array_expansion(self, where_expr):
        """
        Detect array expansion pattern in where clause.

        Looks for patterns like:
        - "item in person.event_ref_list"
        - "event_ref in person.event_ref_list"
        - "item in person.event_ref_list and item.role.value == 1" (extracts the "item in array" part)

        Returns:
            tuple: (item_var, array_path) if pattern detected, (None, None) otherwise
            item_var: name of the iteration variable (e.g., "item", "event_ref")
            array_path: path to the array attribute (e.g., "event_ref_list")
        """
        if not where_expr or not isinstance(where_expr, str):
            return None, None

        try:
            tree = ast.parse(where_expr, mode="eval")
            node = tree.body

            # Check if it's a direct "item in array" pattern
            result = self._extract_array_expansion_from_node(node)
            if result[0] is not None:
                return result

            # Check if it's inside a BoolOp (and/or expressions)
            if isinstance(node, ast.BoolOp):
                for value in node.values:
                    result = self._extract_array_expansion_from_node(value)
                    if result[0] is not None:
                        return result

        except SyntaxError as e:
            raise ValueError(
                f"Invalid expression syntax in array expansion detection: {where_expr}"
            ) from e
        except AttributeError as e:
            raise ValueError(
                f"Invalid expression structure in array expansion detection: {where_expr}"
            ) from e

        return None, None

    def is_array_expansion_in_or(self, where_expr, item_var, array_path):
        """
        Check if array expansion is part of an OR expression.

        Returns True if the array expansion pattern is in an OR (not AND) expression.
        This is needed to determine if we should use UNION to handle both sides correctly.
        """
        if (
            not where_expr
            or not isinstance(where_expr, str)
            or not item_var
            or not array_path
        ):
            return False

        try:
            tree = ast.parse(where_expr, mode="eval")
            node = tree.body

            # Check if it's a BoolOp with OR
            if isinstance(node, ast.BoolOp) and isinstance(node.op, ast.Or):
                # Check if any value contains the array expansion
                for value in node.values:
                    result = self._extract_array_expansion_from_node(value)
                    if result[0] == item_var and result[1] == array_path:
                        return True

        except SyntaxError as e:
            raise ValueError(
                f"Invalid expression syntax in array expansion OR detection: {where_expr}"
            ) from e
        except AttributeError as e:
            raise ValueError(
                f"Invalid expression structure in array expansion OR detection: {where_expr}"
            ) from e

        return False

    def split_or_expression_with_array_expansion(
        self, where_expr, item_var, array_path
    ):
        """
        Split an OR expression into parts with and without array expansion.

        For an expression like "(A and B) or (item in person.array) or (C and D)",
        this splits it into:
        - left_parts: Parts without array expansion (e.g., ["(A and B)", "(C and D)"])
        - right_parts: Parts with array expansion (e.g., ["(item in person.array)"])

        Args:
            where_expr: Where clause as string
            item_var: Variable name for array expansion (e.g., "item")
            array_path: Array path for array expansion (e.g., "event_ref_list")

        Returns:
            tuple: (left_parts, right_parts, has_array_expansion)
            - left_parts: List of AST nodes without array expansion
            - right_parts: List of AST nodes with array expansion
            - has_array_expansion: Boolean indicating if any right parts exist
        """
        if (
            not where_expr
            or not isinstance(where_expr, str)
            or not item_var
            or not array_path
        ):
            return None, None, False

        try:
            tree = ast.parse(where_expr, mode="eval")
            node = tree.body

            # Check if it's a BoolOp with OR at the top level
            if isinstance(node, ast.BoolOp) and isinstance(node.op, ast.Or):
                left_parts = []
                right_parts = []

                # Split each value in the OR expression
                for value in node.values:
                    # Check if this part contains the array expansion
                    result = self._extract_array_expansion_from_node(value)
                    if result[0] == item_var and result[1] == array_path:
                        # This part has array expansion - goes to right
                        right_parts.append(value)
                    else:
                        # This part doesn't have array expansion - goes to left
                        left_parts.append(value)

                has_array_expansion = len(right_parts) > 0

                # If we have both left and right parts, return them
                if has_array_expansion and len(left_parts) > 0:
                    return left_parts, right_parts, True
                else:
                    # Not a valid split case (all parts on one side)
                    return None, None, False

        except SyntaxError as e:
            raise ValueError(
                f"Invalid expression syntax in OR expression splitting: {where_expr}"
            ) from e
        except AttributeError as e:
            raise ValueError(
                f"Invalid expression structure in OR expression splitting: {where_expr}"
            ) from e

        return None, None, False

    def _extract_any_from_node(self, node):
        """
        Helper method to extract any() pattern from an AST node.
        Handles Call nodes directly, or UnaryOp(Not) wrapping a Call.
        """
        # Handle UnaryOp(Not) wrapping any()
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            node = node.operand

        # Look for Call node with function name "any"
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id == "any":
                # Check if first argument is a list comprehension
                if node.args and isinstance(node.args[0], ast.ListComp):
                    listcomp = node.args[0]

                    # List comprehension should have one generator
                    if len(listcomp.generators) == 1:
                        gen = listcomp.generators[0]

                        # Extract iteration variable
                        if isinstance(gen.target, ast.Name):
                            item_var = gen.target.id
                        else:
                            return None, None, None

                        # Extract array path from iter
                        iter_node = gen.iter
                        array_path = None

                        if isinstance(iter_node, ast.Attribute):
                            # Build the full path
                            path_parts = []
                            current = iter_node
                            while isinstance(current, ast.Attribute):
                                path_parts.insert(0, current.attr)
                                current = current.value

                            if isinstance(current, ast.Name) and current.id in [
                                self.table_name,
                                "obj",
                                "person",
                            ]:
                                array_path = ".".join(path_parts)

                        # Extract condition (if any)
                        condition = None
                        if gen.ifs:
                            # Take the first condition
                            condition = gen.ifs[0]

                        if item_var and array_path:
                            return item_var, array_path, condition

        return None, None, None

    def _extract_array_expansion_from_node(self, node):
        """
        Helper method to extract array expansion pattern from an AST node.
        Looks for "item in person.array_path" pattern.
        """
        # Look for Compare node with "in" operator
        if isinstance(node, ast.Compare):
            ops = node.ops
            comparators = node.comparators

            # Check if it's an "in" operation
            if len(ops) == 1 and isinstance(ops[0], ast.In):
                left = node.left
                right = comparators[0]

                # Left should be a Name (the item variable)
                if isinstance(left, ast.Name):
                    item_var = left.id

                    # Right should be an Attribute (e.g., person.event_ref_list)
                    if isinstance(right, ast.Attribute):
                        # Check if it starts with table_name or "obj"
                        attr_obj = right.value
                        if isinstance(attr_obj, ast.Name) and attr_obj.id in [
                            self.table_name,
                            "obj",
                            "person",
                        ]:
                            array_path = right.attr
                            return item_var, array_path

                    # Or right could be a nested attribute path
                    # Try to extract the full path
                    if isinstance(right, ast.Attribute):
                        # Build the full path
                        path_parts = []
                        current = right
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

        return None, None

    def convert_to_sql(self, node):
        # ast.Constant handles Num, Str, NameConstant, Bytes, and Ellipsis (Python 3.8+)
        if isinstance(node, ast.Constant):
            if node.value is None:
                return "null"
            else:
                return repr(node.value)
        elif isinstance(node, ast.BinOp):
            template = self.operators[type(node.op)]
            args = {
                "leftOperand": self.convert_to_sql(node.left),
                "rightOperand": self.convert_to_sql(node.right),
            }
            return template.format(**args)
        elif isinstance(node, ast.UnaryOp):
            template = self.operators[type(node.op)]
            args = {
                "operand": self.convert_to_sql(node.operand),
            }
            return template.format(**args)
        elif isinstance(node, ast.IfExp):
            args = {
                "result_1": self.convert_to_sql(node.body),
                "test_1": self.convert_to_sql(node.test),
                "result_2": self.convert_to_sql(node.orelse),
            }
            return "(CASE WHEN {test_1} THEN {result_1} ELSE {result_2} END)".format(
                **args
            )
        elif isinstance(node, ast.Compare):
            comparators = [self.convert_to_sql(arg) for arg in node.comparators]
            ops = [self.convert_to_sql(arg) for arg in node.ops]
            left = self.convert_to_sql(node.left)

            if ops[0] in [" IN ", " NOT IN "]:
                # FIXME: this just checks the first
                # should pre-process, and leave for
                # zip below
                if (
                    isinstance(comparators[0], str)
                    and comparators[0][0] == "("
                    or comparators[0] == "null"
                ):
                    # item in (1, 2, 3)
                    if comparators[0] == "null":
                        comparators[0] = "()"
                    if ops[0] == " IN ":
                        return "%s IN %s" % (left, comparators[0])
                    elif ops[0] == " NOT IN ":
                        return "%s NOT IN %s" % (left, comparators[0])
                else:
                    # "<string> IN X":
                    if ops[0] == " IN ":
                        return "%s LIKE '%%%s%%'" % (comparators[0], left[1:-1])
                    elif ops[0] == " NOT IN ":
                        return "%s NOT LIKE '%%%s%%'" % (comparators[0], left[1:-1])

            retval = ""
            for op, right in zip(ops, comparators):
                if retval:
                    retval += " and "
                retval += "({left} {op} {right})".format(left=left, op=op, right=right)
                left = right
            return retval

        elif isinstance(node, ast.Lt):
            return "<"
        elif isinstance(node, ast.Gt):
            return ">"
        elif isinstance(node, ast.Eq):
            return "="
        elif isinstance(node, ast.Is):
            return "is"
        elif isinstance(node, ast.LtE):
            return "<="
        elif isinstance(node, ast.GtE):
            return ">="
        elif isinstance(node, ast.NotEq):
            return "!="
        elif isinstance(node, ast.IsNot):
            return "is not"
        elif isinstance(node, ast.And):
            return "and"
        elif isinstance(node, ast.Or):
            return "or"
        elif isinstance(node, ast.BoolOp):
            values = [self.convert_to_sql(value) for value in node.values]
            op = self.convert_to_sql(node.op)
            return "(" + (" %s " % op).join([str(value) for value in values]) + ")"
        elif isinstance(node, ast.Tuple):
            args = [self.convert_to_sql(arg) for arg in node.elts]
            return "(" + (", ".join([str(arg) for arg in args])) + ")"
        elif isinstance(node, ast.In):
            return " IN "
        elif isinstance(node, ast.NotIn):
            return " NOT IN "
        elif isinstance(node, ast.Index):
            return self.convert_to_sql(node.value)
        elif isinstance(node, ast.Subscript):
            obj = self.convert_to_sql(node.value)
            index = self.convert_to_sql(node.slice)
            if isinstance(obj, AttributeNode):
                obj.attr += "[%s]" % index
                return obj
            else:
                raise Exception("Attempt to take index of a non-attribute")
        elif isinstance(node, ast.Attribute):
            obj = self.convert_to_sql(node.value)
            attr = node.attr
            # Handle item variable from array expansion
            if isinstance(obj, AttributeNode) and obj.obj == "json_each":
                # This is item.attr or item.attr1.attr2 - build path from json_each.value
                if obj.attr == "":
                    obj.attr = attr
                else:
                    obj.attr += ".%s" % attr
                return obj
            elif obj in [self.table_name, "obj"]:
                # Base table reference (e.g., "person.handle" when table_name is "person")
                return AttributeNode(
                    self.json_extract, self.json_array_length, self.table_name, attr
                )
            elif isinstance(obj, AttributeNode):
                obj.attr += ".%s" % attr
                return obj
            elif isinstance(obj, str):
                # Check if obj is a table name (for JOIN support)
                # This handles cases like "family.handle" where obj="family"
                obj_lower = obj.lower()
                if obj_lower in TABLE_NAMES:
                    # This is a table reference (e.g., "family.handle")
                    # If it's the base table, use base table's json_extract pattern
                    if obj_lower == self.table_name:
                        return AttributeNode(
                            self.json_extract,
                            self.json_array_length,
                            self.table_name,
                            attr,
                        )
                    else:
                        # Referenced table - use table-prefixed json_extract
                        return AttributeNode(
                            f"json_extract({obj_lower}.json_data, '$.{{attr}}')",
                            f"json_array_length(json_extract({obj_lower}.json_data, '$.{{attr}}'))",
                            obj_lower,
                            attr,
                        )
                else:
                    # Not a table name, try to get attribute
                    try:
                        return getattr(obj, attr)
                    except AttributeError:
                        return f"{obj}.{attr}"
            else:
                # obj is from env (e.g., Person class) - get attribute value
                try:
                    attr_value = getattr(obj, attr)
                    # Return the actual value (e.g., Person.MALE = 1)
                    return attr_value
                except AttributeError:
                    return f"{obj}.{attr}"
        elif isinstance(node, ast.Name):
            value = node.id
            # If this is the item variable from array expansion, reference json_each.value
            if self.item_var and value == self.item_var:
                # Create an AttributeNode that will build paths from json_each.value
                return AttributeNode(
                    "json_extract(json_each.value, '$.{attr}')",
                    "json_array_length(json_extract(json_each.value, '$.{attr}'))",
                    "json_each",
                    "",
                )
            # Check env first (e.g., Person, Family classes)
            if value in self.env:
                return self.env[value]
            # Then check if this is a table name (for JOIN support)
            # Only if it's lowercase and not in env
            if value in TABLE_NAMES:
                # Return the table name as a string (will be used in JOIN clauses)
                return value
            else:
                return str(value)
        elif isinstance(node, ast.List):
            args = [self.convert_to_sql(arg) for arg in node.elts]
            if len(args) == 0:
                return "null"
            return "(" + (", ".join([str(arg) for arg in args])) + ")"
        elif isinstance(node, ast.Call):
            function_name = self.convert_to_sql(node.func)
            args = [self.convert_to_sql(arg) for arg in node.args]
            if function_name == "len":
                # Assumes taking len of a json_data field
                return args[0].get_length()
            elif function_name == "any":
                # Handle any() with list comprehension - should be handled at higher level
                # This shouldn't be reached if properly detected
                raise ValueError(
                    "any() with list comprehension should be handled by detect_any_list_comprehension"
                )
            elif isinstance(function_name, AttributeNode):
                if any(
                    [
                        function_name.attr.endswith(x)
                        for x in [
                            ".endswith",
                            ".startswith",
                        ]
                    ]
                ):
                    # check to make sure string
                    if (
                        len(args) != 1
                        or len(args[0]) < 2
                        or len(set([args[0][0], args[0][-1]])) != 1
                        or args[0][0] not in ["'", '"']
                    ):
                        raise Exception(
                            "%r function requires a string" % function_name.attr
                        )

                    if function_name.attr.endswith(".endswith"):
                        function_name.remove_attribute()
                        return "like('%s', %s)" % ("%" + args[0][1:-1], function_name)
                    elif function_name.attr.endswith(".startswith"):
                        function_name.remove_attribute()
                        return "like('%s', %s)" % (args[0][1:-1] + "%", function_name)
                    else:
                        raise Exception("unhandled function")

            else:
                raise ValueError("unknown function %r" % function_name)

        elif isinstance(node, ast.ListComp):
            # List comprehensions should be handled at higher level (detect_any_list_comprehension)
            raise ValueError(
                "List comprehensions should be handled by detect_any_list_comprehension"
            )

        raise TypeError(f"Unsupported AST node type: {type(node)}")

    def convert(self, python_expr):
        """
        Convert Python expression (string) to SQL expression.

        Args:
            python_expr: String expression.

        Returns:
            SQL expression string
        """
        # Parse and convert to SQL
        node = ast.parse(python_expr, mode="eval").body
        sql_expr = self.convert_to_sql(node)
        # Ensure we return a string, not an AttributeNode
        return str(sql_expr) if not isinstance(sql_expr, str) else sql_expr

    def convert_where_clause(
        self, where_str, exclude_array_expansion=False, item_var=None, array_path=None
    ):
        """
        Convert a where clause string to SQL, preserving full boolean structure.
        Recursively processes the AST, replacing any() patterns with their SQL equivalents.

        This method handles:
        - any() patterns → EXISTS subqueries
        - Array expansion patterns → excluded if exclude_array_expansion=True (handled via FROM clause)
        - Full boolean structure preservation (nested and/or)
        - All operators and nesting levels

        Args:
            where_str: Where clause as string
            exclude_array_expansion: If True, exclude "item in array" patterns from WHERE (they're in FROM)
            item_var: Variable name for array expansion (e.g., "item") - needed to process remaining conditions
            array_path: Array path for array expansion - needed to process remaining conditions

        Returns:
            SQL string for WHERE clause (without "WHERE" keyword), or None if where_str is None/empty
        """
        if where_str is None:
            return None

        try:
            # Parse to AST
            where_ast = ast.parse(where_str, mode="eval").body
        except SyntaxError as e:
            raise ValueError(
                f"Invalid expression syntax in WHERE clause: {where_str}"
            ) from e
        except AttributeError as e:
            raise ValueError(
                f"Invalid expression structure in WHERE clause: {where_str}"
            ) from e

        # If array expansion is excluded but we have item_var, create evaluator with item_var set
        # This is needed to process remaining conditions like "item.role.value == 1"
        if exclude_array_expansion and item_var and array_path:
            # Create evaluator with item_var set for processing remaining conditions
            condition_expression = ExpressionBuilder(
                self.table_name,
                "json_extract(json_each.value, '$.{attr}')",
                "json_array_length(json_extract(json_each.value, '$.{attr}'))",
                self.env,
                item_var=item_var,
                array_path=array_path,
            )
            # Use the condition evaluator for conversion
            result = condition_expression._convert_node_with_replacements(
                where_ast, exclude_array_expansion
            )
        else:
            # Recursively convert, replacing any() patterns and optionally excluding array expansion
            result = self._convert_node_with_replacements(
                where_ast, exclude_array_expansion
            )

        # Ensure result is a string (convert AttributeNode if needed)
        if result is None:
            return None
        result_str = str(result) if not isinstance(result, str) else result
        return result_str if result_str and result_str.strip() else None

    def _convert_node_with_replacements(self, node, exclude_array_expansion=False):
        """
        Recursively convert AST node to SQL, replacing any() patterns and optionally excluding array expansion.
        This preserves the full boolean structure.

        Args:
            node: AST node to convert
            exclude_array_expansion: If True, exclude "item in array" patterns (return None for them)

        Returns:
            SQL string, or None if node should be excluded
        """
        # Check for array expansion pattern (if we should exclude it)
        if exclude_array_expansion:
            array_result = self._extract_array_expansion_from_node(node)
            if array_result[0] is not None:
                # This is "item in array" - handled via FROM clause with json_each
                # In WHERE, we replace it with TRUE (1=1) so OR expressions work correctly
                # The presence of json_each in FROM means this condition is always true for array elements
                return "1=1"

        # Check for any() pattern (handles both direct and wrapped in Not)
        result = self._extract_any_from_node(node)
        if result[0] is not None:
            item_var, array_path, condition_node = result
            is_negated = isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not)

            # Generate SQL for this any() pattern
            array_sql = self.convert(f"{self.table_name}.{array_path}")
            json_each_expr = f"json_each({array_sql}, '$')"

            if condition_node is not None:
                condition_expression = ExpressionBuilder(
                    self.table_name,
                    "json_extract(json_each.value, '$.{attr}')",
                    "json_array_length(json_extract(json_each.value, '$.{attr}'))",
                    self.env,
                    item_var=item_var,
                    array_path=array_path,
                )
                condition_sql = condition_expression.convert_to_sql(condition_node)
                exists_expr = (
                    f"EXISTS (SELECT 1 FROM {json_each_expr} WHERE {condition_sql})"
                )
            else:
                exists_expr = f"EXISTS (SELECT 1 FROM {json_each_expr})"

            if is_negated:
                return f"NOT ({exists_expr})"
            else:
                return exists_expr

        # Handle UnaryOp(Not) - recursively convert operand
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            operand_sql = self._convert_node_with_replacements(
                node.operand, exclude_array_expansion
            )
            if operand_sql is None:
                return None  # If operand is excluded, exclude the whole Not
            return f"NOT ({operand_sql})"

        # Handle BoolOp - preserve structure by recursively converting all values
        # Filter out None values (excluded nodes) and adjust operators if needed
        if isinstance(node, ast.BoolOp):
            op_str = self._ast_operator_to_string(node.op).upper()
            converted_values = []
            for value in node.values:
                value_sql = self._convert_node_with_replacements(
                    value, exclude_array_expansion
                )
                if value_sql is not None:  # Only include non-excluded values
                    value_sql_str = str(value_sql)
                    # Check if this value is itself a BoolOp (nested boolean expression)
                    # If so, we need to ensure it's wrapped as a single unit
                    is_nested_boolop = isinstance(value, ast.BoolOp)

                    # Only wrap if not already wrapped in parentheses
                    # Check if it starts with ( and ends with ) and has balanced parentheses
                    if value_sql_str.startswith("(") and value_sql_str.endswith(")"):
                        # Check if parentheses are balanced (simple check)
                        if value_sql_str.count("(") == value_sql_str.count(")"):
                            # If it's a nested BoolOp, we may need to wrap it anyway
                            # to ensure proper precedence when combined with different operators
                            if is_nested_boolop:
                                # Check if the nested operator is different from current operator
                                # If different, we need to wrap to preserve precedence
                                nested_op = self._ast_operator_to_string(
                                    value.op
                                ).upper()
                                if nested_op != op_str:
                                    # Different operators - wrap to preserve precedence
                                    converted_values.append(f"({value_sql_str})")
                                else:
                                    # Same operator - no need to wrap
                                    converted_values.append(value_sql_str)
                            else:
                                converted_values.append(value_sql_str)
                        else:
                            converted_values.append(f"({value_sql_str})")
                    else:
                        # Not wrapped - always wrap
                        converted_values.append(f"({value_sql_str})")

            if not converted_values:
                return None  # All values were excluded
            elif len(converted_values) == 1:
                return converted_values[0]  # Single value, no need for operator
            else:
                return f" {op_str} ".join(converted_values)

        # For all other nodes, convert normally using evaluator
        sql_result = self.convert_to_sql(node)
        # Ensure we return a string, not an AttributeNode
        return str(sql_result) if not isinstance(sql_result, str) else sql_result

    def get_order_by(self, order_by, has_joins=False):
        order_by_exprs = []
        for expr in order_by:
            # Handle string with "-" prefix for descending
            if isinstance(expr, str) and expr.startswith("-"):
                converted = self.convert(expr[1:])
                # If JOINs are present and result is json_data without table prefix, add prefix
                if (
                    has_joins
                    and isinstance(converted, str)
                    and converted.startswith("json_extract(json_data")
                ):
                    # Replace json_data with table_name.json_data
                    converted = converted.replace(
                        "json_extract(json_data",
                        f"json_extract({self.table_name}.json_data",
                        1,
                    )
                order_by_exprs.append("%s %s" % (converted, "DESC"))
            else:
                # Handle string expression (lambdas should already be converted to strings)
                converted = self.convert(expr)
                # If JOINs are present and result is json_data without table prefix, add prefix
                if (
                    has_joins
                    and isinstance(converted, str)
                    and converted.startswith("json_extract(json_data")
                ):
                    # Replace json_data with table_name.json_data
                    converted = converted.replace(
                        "json_extract(json_data",
                        f"json_extract({self.table_name}.json_data",
                        1,
                    )
                order_by_exprs.append(str(converted))

        if order_by_exprs:
            order_expr = " ORDER BY %s" % (", ".join(order_by_exprs))
        else:
            order_expr = ""

        return order_expr


class QueryBuilder:
    """
    SQL query builder that uses a single ExpressionBuilder instance.
    Consolidates all SQL generation logic for select_from_table.
    """

    def __init__(self, table_name, json_extract, json_array_length, env):
        """
        Initialize QueryBuilder with table configuration.

        Args:
            table_name: Base table name (e.g., "person")
            json_extract: JSON extract pattern (e.g., "json_extract(json_data, '$.{attr}')")
            json_array_length: JSON array length pattern
            env: Environment dictionary for expression evaluation
        """
        self.table_name = table_name
        self.json_extract = json_extract
        self.json_array_length = json_array_length
        self.env = env if env is not None else {}
        # Create single ExpressionBuilder instance for primary conversions
        self.expression = ExpressionBuilder(
            table_name, json_extract, json_array_length, self.env
        )

    def _create_array_evaluator(self, item_var, array_path):
        """
        Create a specialized evaluator for array expansion contexts.

        Args:
            item_var: Variable name for array iteration (e.g., "item")
            array_path: Array path for json_each (e.g., "event_ref_list")

        Returns:
            ExpressionBuilder instance configured for array expansion
        """
        return ExpressionBuilder(
            self.table_name,
            "json_extract(json_each.value, '$.{attr}')",
            "json_array_length(json_extract(json_each.value, '$.{attr}'))",
            self.env,
            item_var=item_var,
            array_path=array_path,
        )

    def _create_join_evaluator(self, table_name):
        """
        Create a specialized evaluator for JOIN attribute conversion.

        Args:
            table_name: Table name for the evaluator

        Returns:
            ExpressionBuilder instance configured for the specified table
        """
        return ExpressionBuilder(
            table_name,
            f"json_extract({table_name}.json_data, '$.{{attr}}')",
            f"json_array_length(json_extract({table_name}.json_data, '$.{{attr}}'))",
            self.env,
        )

    def get_sql_query(self, what, where, order_by):
        """
        Generate complete SQL query from what, where, and order_by parameters.

        Handles all complex cases:
        - Lambda to string conversion
        - Table reference detection and JOINs
        - Array expansion in WHERE clause
        - Array expansion in OR expressions (UNION queries)
        - List comprehensions in WHAT clause
        - ORDER BY conversion

        Args:
            what: What clause (None, str, lambda, or list)
            where: Where clause (None, str, or lambda)
            order_by: Order by clause (None, str, lambda, or list)

        Returns:
            Complete SQL query string
        """
        # Convert where to string if needed
        where_str = where
        if isinstance(where, types.LambdaType):
            where_str = lambda_to_string(where)
        elif where is None:
            where_str = None

        # Detect table references for JOIN support
        referenced_tables = set()
        if where_str:
            referenced_tables.update(
                self.expression.detect_table_references(
                    where_str, base_table=self.table_name
                )
            )

        # Check what clause for table references
        if isinstance(what, types.LambdaType):
            what_str_for_join = lambda_to_string(what)
            if what_str_for_join:
                referenced_tables.update(
                    self.expression.detect_table_references(
                        what_str_for_join, base_table=self.table_name
                    )
                )
        elif isinstance(what, str):
            referenced_tables.update(
                self.expression.detect_table_references(
                    what, base_table=self.table_name
                )
            )
        elif isinstance(what, list):
            for w in what:
                if isinstance(w, types.LambdaType):
                    w = lambda_to_string(w)
                if isinstance(w, str):
                    referenced_tables.update(
                        self.expression.detect_table_references(
                            w, base_table=self.table_name
                        )
                    )

        # Determine JOIN conditions
        join_conditions = {}
        if referenced_tables:
            join_conditions = self.expression.determine_join_conditions(
                self.table_name, referenced_tables, where_str
            )

        # Check if we have JOINs
        has_joins = bool(referenced_tables and join_conditions)

        # Check for array expansion pattern
        item_var, array_path = self.expression.detect_array_expansion(where_str)
        is_array_expansion = item_var is not None and array_path is not None

        # Check if array expansion is in an OR expression (needs UNION handling)
        is_array_expansion_in_or = False
        if is_array_expansion:
            is_array_expansion_in_or = self.expression.is_array_expansion_in_or(
                where_str, item_var, array_path
            )

        # Handle UNION query for array expansion in OR expressions
        if is_array_expansion_in_or:
            return self._build_union_query(
                what,
                where_str,
                order_by,
                item_var,
                array_path,
                join_conditions,
                has_joins,
            )

        # Check for list comprehension in what clause
        what_str = what
        if isinstance(what, types.LambdaType):
            what_str = lambda_to_string(what)
        elif isinstance(what, list) and len(what) == 1 and isinstance(what[0], str):
            what_str = what[0]
        elif not isinstance(what, str):
            what_str = None

        what_item_var, what_array_path, what_expression_node, what_condition_node = (
            self.expression.detect_list_comprehension_in_what(what_str)
        )

        # Build what expression
        what_condition_sql = None
        if what_item_var and what_array_path:
            # List comprehension in what clause
            what_expression = self._create_array_evaluator(
                what_item_var, what_array_path
            )
            what_expr = str(what_expression.convert_to_sql(what_expression_node))
            array_sql_expression = ExpressionBuilder(
                self.table_name,
                "json_extract(json_data, '$.{attr}')",
                "json_array_length(json_extract(json_data, '$.{attr}'))",
                self.env,
            )
            array_sql = array_sql_expression.convert(
                f"{self.table_name}.{what_array_path}"
            )
            json_each_expr = f"json_each({array_sql}, '$')"
            from_clause = f"{self.table_name}, {json_each_expr}"
            if what_condition_node:
                what_condition_sql = what_expression.convert_to_sql(what_condition_node)
        elif what is None:
            what_expr = "json_data"
        elif isinstance(what, types.LambdaType):
            what_str = lambda_to_string(what)
            if what_str in ["obj", "person"]:
                what_str = "json_data"
            what_expr = str(self.expression.convert(what_str))
        elif isinstance(what, str):
            if what in ["obj", "person"]:
                what = "json_data"
            if (
                is_array_expansion
                and item_var
                and (what.startswith(f"{item_var}.") or what == item_var)
            ):
                array_expansion_expression = self._create_array_evaluator(
                    item_var, array_path
                )
                what_expr = str(array_expansion_expression.convert(what))
            else:
                if has_joins:
                    join_expression = self._create_join_evaluator(self.table_name)
                    what_expr = str(join_expression.convert(what))
                else:
                    what_expr = str(self.expression.convert(what))
        else:
            what_list = []
            join_expression = None
            if has_joins:
                join_expression = self._create_join_evaluator(self.table_name)
            for w in what:
                if isinstance(w, types.LambdaType):
                    w = lambda_to_string(w)
                if w in ["obj", "person"]:
                    w = "json_data"
                if (
                    is_array_expansion
                    and item_var
                    and (w.startswith(f"{item_var}.") or w == item_var)
                ):
                    array_expansion_expression = self._create_array_evaluator(
                        item_var, array_path
                    )
                    what_list.append(str(array_expansion_expression.convert(w)))
                else:
                    if join_expression:
                        what_list.append(str(join_expression.convert(w)))
                    else:
                        what_list.append(str(self.expression.convert(w)))
            what_expr = ", ".join(what_list)

        # Build WHERE clause
        if has_joins:
            where_expression = self._create_join_evaluator(self.table_name)
            where_sql = where_expression.convert_where_clause(
                where_str,
                exclude_array_expansion=is_array_expansion,
                item_var=item_var if is_array_expansion else None,
                array_path=array_path if is_array_expansion else None,
            )
        else:
            where_sql = self.expression.convert_where_clause(
                where_str,
                exclude_array_expansion=is_array_expansion,
                item_var=item_var if is_array_expansion else None,
                array_path=array_path if is_array_expansion else None,
            )

        # Combine with what condition if present
        if what_item_var and what_array_path and what_condition_sql:
            if where_sql:
                where_expr = f" WHERE ({where_sql}) AND ({what_condition_sql})"
            else:
                where_expr = f" WHERE {what_condition_sql}"
        elif where_sql:
            where_expr = f" WHERE {where_sql}"
        else:
            where_expr = ""

        # Handle array expansion in where clause
        if is_array_expansion:
            array_sql = self.expression.convert(f"{self.table_name}.{array_path}")
            json_each_expr = f"json_each({array_sql}, '$')"
            if not (what_item_var and what_array_path):
                from_clause = f"{self.table_name}, {json_each_expr}"

        # Set from_clause if not already set
        if what_item_var and what_array_path:
            pass  # Already set above
        elif is_array_expansion:
            pass  # Already set above
        else:
            from_clause = self.table_name

        # Add JOIN clauses if tables are referenced
        if has_joins:
            join_clauses = []
            tables_joined = set()
            for ref_table in sorted(referenced_tables):
                if ref_table in join_conditions and ref_table not in tables_joined:
                    join_cond = join_conditions[ref_table][0]
                    left_table, left_attr, right_table, right_attr, join_type = (
                        join_cond
                    )
                    left_expression = self._create_join_evaluator(left_table)
                    right_expression = self._create_join_evaluator(right_table)
                    left_sql = left_expression.convert(f"{left_table}.{left_attr}")
                    right_sql = right_expression.convert(f"{right_table}.{right_attr}")
                    join_clause = (
                        f"{join_type} JOIN {ref_table} ON {left_sql} = {right_sql}"
                    )
                    join_clauses.append(join_clause)
                    tables_joined.add(ref_table)
            if join_clauses:
                from_clause = f"{from_clause} " + " ".join(join_clauses)

        # Build ORDER BY
        if order_by is None:
            order_by_expr = ""
        else:
            if isinstance(order_by, types.LambdaType):
                order_by = [lambda_to_string(order_by)]
            elif callable(order_by) and not isinstance(order_by, type):
                order_by = [order_by]
            elif isinstance(order_by, str):
                order_by = [order_by]
            converted_order_by = []
            for expr in order_by:
                if isinstance(expr, types.LambdaType):
                    converted_order_by.append(lambda_to_string(expr))
                else:
                    converted_order_by.append(expr)
            if has_joins:
                order_by_expression = self._create_join_evaluator(self.table_name)
                order_by_expr = order_by_expression.get_order_by(
                    converted_order_by, has_joins=False
                )
            else:
                order_by_expr = self.expression.get_order_by(
                    converted_order_by, has_joins=False
                )

        return f"SELECT {what_expr} from {from_clause}{where_expr}{order_by_expr};"

    def _build_union_query(
        self,
        what,
        where_str,
        order_by,
        item_var,
        array_path,
        join_conditions,
        has_joins,
    ):
        """
        Build UNION query for array expansion in OR expressions.

        Args:
            what: What clause
            where_str: Where clause as string
            order_by: Order by clause
            item_var: Array iteration variable
            array_path: Array path
            join_conditions: JOIN conditions dict
            has_joins: Whether JOINs are present

        Returns:
            Complete UNION SQL query string
        """
        # Split the OR expression
        left_parts, right_parts, has_array_expansion = (
            self.expression.split_or_expression_with_array_expansion(
                where_str, item_var, array_path
            )
        )

        if not (has_array_expansion and left_parts and right_parts):
            # Split failed - this shouldn't happen, but handle gracefully
            # Return empty query or raise error - for now, return empty
            # In practice, this condition should never be true if we reach _build_union_query
            return ""

        # Prepare what clause
        what_str = what
        if isinstance(what, types.LambdaType):
            what_str = lambda_to_string(what)
        elif isinstance(what, list) and len(what) == 1 and isinstance(what[0], str):
            what_str = what[0]
        elif not isinstance(what, str):
            what_str = None

        (
            what_item_var,
            what_array_path,
            what_expression_node,
            what_condition_node,
        ) = self.expression.detect_list_comprehension_in_what(what_str)

        # Build what_expr (same for both queries)
        if what_item_var and what_array_path:
            what_expression = self._create_array_evaluator(
                what_item_var, what_array_path
            )
            what_expr = str(what_expression.convert_to_sql(what_expression_node))
            array_sql_expression = ExpressionBuilder(
                self.table_name,
                "json_extract(json_data, '$.{attr}')",
                "json_array_length(json_extract(json_data, '$.{attr}'))",
                self.env,
            )
            what_array_sql = array_sql_expression.convert(
                f"{self.table_name}.{what_array_path}"
            )
            what_json_each_expr = f"json_each({what_array_sql}, '$')"
        elif what is None:
            what_expr = "json_data"
        elif isinstance(what, types.LambdaType):
            what_str = lambda_to_string(what)
            if what_str in ["obj", "person"]:
                what_str = "json_data"
            what_expr = str(self.expression.convert(what_str))
        elif isinstance(what, str):
            if what in ["obj", "person"]:
                what = "json_data"
            if what.startswith(f"{item_var}.") or what == item_var:
                array_expansion_expression = self._create_array_evaluator(
                    item_var, array_path
                )
                what_expr = str(array_expansion_expression.convert(what))
            else:
                what_expr = str(self.expression.convert(what))
        else:
            what_list = []
            for w in what:
                if isinstance(w, types.LambdaType):
                    w = lambda_to_string(w)
                if w in ["obj", "person"]:
                    w = "json_data"
                if w.startswith(f"{item_var}.") or w == item_var:
                    array_expansion_expression = self._create_array_evaluator(
                        item_var, array_path
                    )
                    what_list.append(str(array_expansion_expression.convert(w)))
                else:
                    what_list.append(str(self.expression.convert(w)))
            what_expr = ", ".join(what_list)

        # Build left query (no array expansion)
        if len(left_parts) == 1:
            left_where_node = left_parts[0]
        else:
            left_where_node = ast.BoolOp(op=ast.And(), values=left_parts)

        left_where_sql = self.expression._convert_node_with_replacements(
            left_where_node, exclude_array_expansion=False
        )
        left_where_sql = (
            str(left_where_sql)
            if not isinstance(left_where_sql, str)
            else left_where_sql
        )

        if what_item_var and what_array_path and what_condition_node:
            what_condition_sql = what_expression.convert_to_sql(what_condition_node)
            if left_where_sql:
                left_where_expr = (
                    f" WHERE ({left_where_sql}) AND ({what_condition_sql})"
                )
            else:
                left_where_expr = f" WHERE {what_condition_sql}"
        elif left_where_sql:
            left_where_expr = f" WHERE {left_where_sql}"
        else:
            left_where_expr = ""

        if what_item_var and what_array_path:
            left_from_clause = f"{self.table_name}, {what_json_each_expr}"
        else:
            left_from_clause = self.table_name
        left_query = f"SELECT {what_expr} FROM {left_from_clause}{left_where_expr}"

        # Build right query (with array expansion)
        if len(right_parts) == 1:
            right_where_node = right_parts[0]
        else:
            right_where_node = ast.BoolOp(op=ast.And(), values=right_parts)

        right_expression = self._create_array_evaluator(item_var, array_path)
        right_where_sql = right_expression._convert_node_with_replacements(
            right_where_node, exclude_array_expansion=True
        )
        right_where_sql = (
            str(right_where_sql)
            if not isinstance(right_where_sql, str)
            else right_where_sql
        )

        if what_item_var and what_array_path and what_condition_node:
            what_condition_sql = what_expression.convert_to_sql(what_condition_node)
            if right_where_sql:
                right_where_expr = (
                    f" WHERE ({right_where_sql}) AND ({what_condition_sql})"
                )
            else:
                right_where_expr = f" WHERE {what_condition_sql}"
        elif right_where_sql:
            right_where_expr = f" WHERE {right_where_sql}"
        else:
            right_where_expr = ""

        array_sql = self.expression.convert(f"{self.table_name}.{array_path}")
        json_each_expr = f"json_each({array_sql}, '$')"

        if what_item_var and what_array_path:
            if what_array_path == array_path:
                right_from_clause = f"{self.table_name}, {json_each_expr}"
            else:
                right_from_clause = (
                    f"{self.table_name}, {what_json_each_expr}, {json_each_expr}"
                )
        else:
            right_from_clause = f"{self.table_name}, {json_each_expr}"

        right_query = f"SELECT {what_expr} FROM {right_from_clause}{right_where_expr}"

        # Handle ORDER BY after UNION
        if order_by is None:
            order_by_expr = ""
        else:
            if isinstance(order_by, types.LambdaType):
                order_by = [lambda_to_string(order_by)]
            elif callable(order_by) and not isinstance(order_by, type):
                order_by = [order_by]
            elif isinstance(order_by, str):
                order_by = [order_by]
            converted_order_by = []
            for expr in order_by:
                if isinstance(expr, types.LambdaType):
                    converted_order_by.append(lambda_to_string(expr))
                else:
                    converted_order_by.append(expr)
            order_by_expr = self.expression.get_order_by(converted_order_by)

        return f"{left_query} UNION {right_query}{order_by_expr};"

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
SQL Generator

Converts query model objects to SQL strings.
Handles dialect differences (SQLite vs PostgreSQL).
"""

from typing import List, Optional

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


class SQLGenerator:
    """Converts query model objects to SQL strings."""

    def __init__(self, dialect: str = "sqlite"):
        """
        Initialize the SQL generator.

        Args:
            dialect: SQL dialect ("sqlite" or "postgres")
        """
        self.dialect = dialect.lower()

    def generate(self, query: SelectQuery) -> str:
        """
        Generate SQL from a SelectQuery object.

        Args:
            query: SelectQuery object

        Returns:
            SQL query string
        """
        # Handle UNION queries
        if query.union_queries:
            return self._generate_union(query)

        # Generate standard SELECT query
        return self._generate_select(query)

    def _generate_select(self, query: SelectQuery) -> str:
        """Generate a SELECT statement."""
        # Store base table for use in expressions
        self.base_table = query.base_table

        # SELECT clause
        select_parts = []
        for sel_expr in query.select_expressions:
            # Handle list comprehensions specially
            if isinstance(sel_expr.expression, ListComprehensionExpression):
                # List comprehension needs special FROM clause handling
                # For now, generate placeholder
                expr_sql = self._generate_listcomp_in_select(sel_expr.expression, query)
            else:
                expr_sql = self.generate_expression(sel_expr.expression)
            if sel_expr.alias:
                select_parts.append(f"{expr_sql} AS {sel_expr.alias}")
            else:
                select_parts.append(expr_sql)
        select_clause = ", ".join(select_parts) if select_parts else "json_data"

        # FROM clause
        from_parts = [query.base_table]

        # Check for list comprehensions that need array expansion
        for sel_expr in query.select_expressions:
            if isinstance(sel_expr.expression, ListComprehensionExpression):
                listcomp = sel_expr.expression
                if listcomp.array_info.get("type") == "single":
                    # Single array - add json_each
                    array_path = listcomp.array_info["path"]
                    from .query_model import AttributeExpression

                    array_attr = AttributeExpression(
                        table_name=query.base_table,
                        attribute_path=array_path,
                        is_database_column=False,
                    )
                    array_sql = self.generate_expression(array_attr)
                    json_each_expr = self._format_json_each(array_sql)
                    from_parts.append(json_each_expr)
                    break  # Only add once

        # Add array expansion if present (for WHERE clause array expansion)
        if query.array_expansion:
            array_sql = self.generate_expression(query.array_expansion.array_expression)
            # If it's a CallExpression for json_array, we need to handle it specially
            if isinstance(query.array_expansion.array_expression, CallExpression):
                # For concatenated arrays, the left side is wrapped in json_array()
                # Generate the json_array call
                array_sql = self.generate_expression(
                    query.array_expansion.array_expression
                )
            json_each_expr = self._format_json_each(array_sql)
            if json_each_expr not in from_parts:
                from_parts.append(json_each_expr)

        # Add JOINs - JOINs should not be comma-separated
        # Build FROM clause: base_table, json_each (if any), then JOINs
        from_clause_parts = []
        # Add base table and json_each (comma-separated)
        from_clause_parts.append(", ".join(from_parts))
        # Add JOINs (space-separated, not comma-separated)
        for join in query.joins:
            join_sql = self._generate_join(join)
            from_clause_parts.append(join_sql)

        from_clause = " ".join(from_clause_parts)

        # WHERE clause
        # Collect all conditions: query WHERE condition + list comprehension conditions
        where_conditions = []

        # Add query-level WHERE condition (excluding ArrayExpansionExpression)
        if query.where_condition:
            where_sql = self._generate_where_condition(query.where_condition)
            if where_sql:
                where_conditions.append(where_sql)

        # Add list comprehension conditions from SELECT expressions
        # These need to be evaluated in the context of json_each
        for sel_expr in query.select_expressions:
            if isinstance(sel_expr.expression, ListComprehensionExpression):
                listcomp = sel_expr.expression
                if listcomp.condition:
                    # Generate the condition SQL with item_var context
                    # The condition references the item variable (e.g., eref.role.value)
                    condition_sql = self.generate_expression(listcomp.condition)
                    if condition_sql:
                        where_conditions.append(condition_sql)

        # Combine all conditions with AND
        where_clause = ""
        if where_conditions:
            combined_where = " AND ".join(f"({cond})" for cond in where_conditions)
            where_clause = f" WHERE {combined_where}"

        # ORDER BY clause
        order_by_clause = ""
        if query.order_by:
            order_parts = []
            for order in query.order_by:
                expr_sql = self.generate_expression(order.expression)
                order_parts.append(f"{expr_sql} {order.direction}")
            order_by_clause = f" ORDER BY {', '.join(order_parts)}"

        # LIMIT/OFFSET clause
        limit_clause = ""
        if query.limit is not None:
            limit_clause = f" LIMIT {query.limit}"
            if query.offset is not None:
                limit_clause += f" OFFSET {query.offset}"

        return f"SELECT {select_clause} FROM {from_clause}{where_clause}{order_by_clause}{limit_clause};"

    def _generate_where_condition(self, expr: Expression) -> str:
        """Generate SQL for WHERE condition, filtering out ArrayExpansionExpression."""
        from .query_model import ArrayExpansionExpression, BoolOpExpression

        # If it's an ArrayExpansionExpression, return empty (handled in FROM clause)
        if isinstance(expr, ArrayExpansionExpression):
            return ""

        # If it's a BoolOp, recursively process and filter out empty conditions
        if isinstance(expr, BoolOpExpression):
            condition_parts = []
            for value in expr.values:
                part = self._generate_where_condition(value)
                if part:
                    condition_parts.append(f"({part})")

            if not condition_parts:
                return ""
            elif len(condition_parts) == 1:
                return condition_parts[0]
            else:
                operator = " AND " if expr.operator == "and" else " OR "
                return operator.join(condition_parts)

        # For other expressions, generate normally
        return self.generate_expression(expr)

    def _generate_union(self, query: SelectQuery) -> str:
        """Generate a UNION query."""
        queries = [query] + query.union_queries
        query_strings = [self._generate_select(q) for q in queries]
        # Remove semicolons from individual queries
        query_strings = [q.rstrip(";") for q in query_strings]
        # Combine with UNION ALL for concatenated arrays
        union_sql = " UNION ALL ".join(query_strings)
        return union_sql + ";"

    def _generate_join(self, join: Join) -> str:
        """Generate a JOIN clause."""
        from .query_model import CompareExpression, BoolOpExpression

        # The condition can be a single equality or a BoolOp (OR) combining multiple conditions
        if (
            isinstance(join.condition, BoolOpExpression)
            and join.condition.operator == "or"
        ):
            # Multiple conditions combined with OR - generate each and combine
            condition_parts = []
            for condition in join.condition.values:
                if isinstance(condition, CompareExpression):
                    if len(condition.operators) == 1 and condition.operators[0] == "==":
                        left_sql = self.generate_expression(condition.left)
                        right_sql = self.generate_expression(condition.comparators[0])
                        condition_parts.append(f"{left_sql} = {right_sql}")
                    else:
                        condition_parts.append(self.generate_expression(condition))
                else:
                    condition_parts.append(self.generate_expression(condition))

            combined_condition = " OR ".join(f"({part})" for part in condition_parts)
            return f"{join.join_type} JOIN {join.table_name} ON {combined_condition}"

        # Single condition
        if isinstance(join.condition, CompareExpression):
            if (
                len(join.condition.operators) == 1
                and join.condition.operators[0] == "=="
            ):
                left_sql = self.generate_expression(join.condition.left)
                right_sql = self.generate_expression(join.condition.comparators[0])
                return f"{join.join_type} JOIN {join.table_name} ON {left_sql} = {right_sql}"

        # Fallback: use the condition as-is
        condition_sql = self.generate_expression(join.condition)
        return f"{join.join_type} JOIN {join.table_name} ON {condition_sql}"

    def generate_expression(self, expr: Expression) -> str:
        """
        Generate SQL from an Expression object.

        Args:
            expr: Expression object

        Returns:
            SQL expression string
        """
        if isinstance(expr, ConstantExpression):
            return self._generate_constant(expr)
        elif isinstance(expr, AttributeExpression):
            return self._generate_attribute(expr)
        elif isinstance(expr, ArrayAccessExpression):
            return self._generate_array_access(expr)
        elif isinstance(expr, BinaryOpExpression):
            return self._generate_binaryop(expr)
        elif isinstance(expr, UnaryOpExpression):
            return self._generate_unaryop(expr)
        elif isinstance(expr, CompareExpression):
            return self._generate_compare(expr)
        elif isinstance(expr, BoolOpExpression):
            return self._generate_boolop(expr)
        elif isinstance(expr, CallExpression):
            return self._generate_call(expr)
        elif isinstance(expr, IfExpression):
            return self._generate_if(expr)
        elif isinstance(expr, ListComprehensionExpression):
            return self._generate_listcomp(expr)
        elif isinstance(expr, AnyExpression):
            return self._generate_any(expr)
        elif isinstance(expr, ArrayExpansionExpression):
            # Array expansion is handled in FROM clause, not as a WHERE condition
            # Return empty string - will be filtered out in _generate_where_condition
            return ""
        elif isinstance(expr, TupleExpression):
            return self._generate_tuple(expr)
        else:
            raise ValueError(f"Unsupported expression type: {type(expr)}")

    def _generate_constant(self, expr: ConstantExpression) -> str:
        """Generate SQL for a constant."""
        if expr.value is None:
            return "null"
        elif isinstance(expr.value, str):
            return repr(expr.value)
        elif isinstance(expr.value, bool):
            return "1" if expr.value else "0"
        else:
            return str(expr.value)

    def _generate_attribute(self, expr: AttributeExpression) -> str:
        """Generate SQL for an attribute access."""
        if expr.is_database_column:
            # Direct database column reference
            return f"{expr.table_name}.{expr.attribute_path}"

        # If base is provided, this is attribute access on the result of another expression
        # Generate SQL for the base expression first, then extract the attribute
        if expr.base is not None:
            # Generate SQL for the base expression (e.g., array access subquery)
            base_sql = self.generate_expression(expr.base)

            # Now extract the attribute from the base result
            if expr.attribute_path:
                if self.dialect == "sqlite":
                    return f"json_extract({base_sql}, '$.{expr.attribute_path}')"
                elif self.dialect == "postgres":
                    return f"JSON_EXTRACT_PATH({base_sql}, '{expr.attribute_path}')"
                else:
                    return f"json_extract({base_sql}, '$.{expr.attribute_path}')"
            else:
                # No attribute path - just return the base
                return base_sql

        # JSON field - use json_extract
        if expr.table_name == "json_each":
            # Array expansion context
            base_expr = "json_each.value"
        else:
            # Regular table
            base_expr = f"{expr.table_name}.json_data"

        if not expr.attribute_path:
            # Just the base (e.g., person or json_each)
            if expr.table_name == "json_each":
                return "json_each.value"
            else:
                return f"{expr.table_name}.json_data"

        # Build JSON extract
        if self.dialect == "sqlite":
            return f"json_extract({base_expr}, '$.{expr.attribute_path}')"
        elif self.dialect == "postgres":
            return f"JSON_EXTRACT_PATH({base_expr}, '{expr.attribute_path}')"
        else:
            return f"json_extract({base_expr}, '$.{expr.attribute_path}')"

    def _generate_array_access(self, expr: ArrayAccessExpression) -> str:
        """Generate SQL for array access."""
        base_sql = self.generate_expression(expr.base)

        if expr.is_constant_index:
            # Constant index: add to JSON path
            index_sql = self.generate_expression(expr.index)
            # Remove quotes if it's a string constant
            if isinstance(expr.index, ConstantExpression) and isinstance(
                expr.index.value, str
            ):
                try:
                    index_val = int(expr.index.value)
                    index_sql = str(index_val)
                except ValueError:
                    pass

            # Check if base is an AttributeExpression
            if isinstance(expr.base, AttributeExpression):
                # Add index to attribute path
                new_path = f"{expr.base.attribute_path}[{index_sql}]"
                if expr.base.is_database_column:
                    return f"{expr.base.table_name}.{new_path}"
                base_expr = (
                    "json_each.value"
                    if expr.base.table_name == "json_each"
                    else f"{expr.base.table_name}.json_data"
                )
                if self.dialect == "sqlite":
                    return f"json_extract({base_expr}, '$.{new_path}')"
                elif self.dialect == "postgres":
                    return f"JSON_EXTRACT_PATH({base_expr}, '{new_path}')"
                else:
                    return f"json_extract({base_expr}, '$.{new_path}')"
            else:
                # Base is already a SQL expression - can't modify path
                # This shouldn't happen in normal cases
                return f"{base_sql}[{index_sql}]"
        else:
            # Variable index: use subquery with json_each
            index_sql = self.generate_expression(expr.index)

            # Extract array path from base
            if isinstance(expr.base, AttributeExpression):
                array_path = expr.base.attribute_path.split("[")[0]
                base_expr = (
                    "json_each.value"
                    if expr.base.table_name == "json_each"
                    else f"{expr.base.table_name}.json_data"
                )

                if self.dialect == "sqlite":
                    array_expr = f"json_extract({base_expr}, '$.{array_path}')"
                    json_each_expr = f"json_each({array_expr}, '$')"
                    return f"(SELECT json_each.value FROM {json_each_expr} WHERE CAST(json_each.key AS INTEGER) = CAST({index_sql} AS INTEGER) LIMIT 1)"
                elif self.dialect == "postgres":
                    array_expr = f"JSON_EXTRACT_PATH({base_expr}, '{array_path}')"
                    json_each_expr = f"LATERAL json_array_elements({array_expr}) WITH ORDINALITY AS json_each(value, ordinality)"
                    return f"(SELECT json_each.value FROM {json_each_expr} WHERE json_each.ordinality - 1 = CAST({index_sql} AS INTEGER) LIMIT 1)"
                else:
                    array_expr = f"json_extract({base_expr}, '$.{array_path}')"
                    json_each_expr = f"json_each({array_expr}, '$')"
                    return f"(SELECT json_each.value FROM {json_each_expr} WHERE CAST(json_each.key AS INTEGER) = CAST({index_sql} AS INTEGER) LIMIT 1)"
            else:
                # Can't handle variable index on non-attribute base
                raise ValueError(f"Cannot handle variable index on: {expr.base}")

    def _generate_binaryop(self, expr: BinaryOpExpression) -> str:
        """Generate SQL for binary operation."""
        left_sql = self.generate_expression(expr.left)
        right_sql = self.generate_expression(expr.right)

        op_map = {
            "+": "+",
            "-": "-",
            "*": "*",
            "/": "/",
            "%": "%",
            "**": "POW",
            "//": "CAST (({left} / {right}) AS INT)",
        }

        if expr.operator == "**":
            return f"POW({left_sql}, {right_sql})"
        elif expr.operator == "//":
            return f"(CAST (({left_sql} / {right_sql}) AS INT))"
        else:
            return f"({left_sql} {expr.operator} {right_sql})"

    def _generate_unaryop(self, expr: UnaryOpExpression) -> str:
        """Generate SQL for unary operation."""
        operand_sql = self.generate_expression(expr.operand)

        if expr.operator == "-":
            return f"-{operand_sql}"
        elif expr.operator == "not":
            # For JSON fields, "not field" should check for NULL, empty string, empty array, etc.
            # Check if operand is a JSON field (AttributeExpression that's not a database column)
            from .query_model import AttributeExpression

            if (
                isinstance(expr.operand, AttributeExpression)
                and not expr.operand.is_database_column
            ):
                # This is a JSON field - check for falsy values
                # In Python, "not value" means value is falsy
                # For JSON: NULL, empty string, empty array, empty object, 0, false
                empty_obj = "'{}'"
                if self.dialect == "sqlite":
                    return f"({operand_sql} IS NULL OR {operand_sql} = '' OR {operand_sql} = '[]' OR {operand_sql} = {empty_obj} OR {operand_sql} = 0 OR {operand_sql} = false)"
                elif self.dialect == "postgres":
                    return f"({operand_sql} IS NULL OR {operand_sql} = '' OR {operand_sql} = '[]' OR {operand_sql} = {empty_obj} OR {operand_sql} = 0 OR {operand_sql} = false)"
                else:
                    return f"({operand_sql} IS NULL OR {operand_sql} = '' OR {operand_sql} = '[]' OR {operand_sql} = {empty_obj} OR {operand_sql} = 0 OR {operand_sql} = false)"
            else:
                # For non-JSON fields or database columns, use standard NOT
                return f"NOT ({operand_sql})"
        else:
            return f"{expr.operator} {operand_sql}"

    def _generate_compare(self, expr: CompareExpression) -> str:
        """Generate SQL for comparison."""
        left_sql = self.generate_expression(expr.left)
        parts = []

        current_left = left_sql
        for op, right in zip(expr.operators, expr.comparators):
            right_sql = self.generate_expression(right)

            # Handle special cases for IN/NOT IN
            if op == "in":
                # Check if right is a tuple/list (normal IN) or string (LIKE pattern)
                if isinstance(right, TupleExpression) or (
                    isinstance(right, ConstantExpression)
                    and isinstance(right.value, str)
                    and right.value.startswith("(")
                ):
                    # Normal IN
                    parts.append(f"{current_left} IN {right_sql}")
                else:
                    # String IN pattern - convert to LIKE
                    # Extract string value from left
                    if isinstance(expr.left, ConstantExpression) and isinstance(
                        expr.left.value, str
                    ):
                        str_val = expr.left.value
                        parts.append(f"{right_sql} LIKE '%{str_val}%'")
                    else:
                        parts.append(f"{current_left} IN {right_sql}")
            elif op == "not in":
                if isinstance(right, TupleExpression) or (
                    isinstance(right, ConstantExpression)
                    and isinstance(right.value, str)
                    and right.value.startswith("(")
                ):
                    parts.append(f"{current_left} NOT IN {right_sql}")
                else:
                    if isinstance(expr.left, ConstantExpression) and isinstance(
                        expr.left.value, str
                    ):
                        str_val = expr.left.value
                        parts.append(f"{right_sql} NOT LIKE '%{str_val}%'")
                    else:
                        parts.append(f"{current_left} NOT IN {right_sql}")
            else:
                # Standard comparison operator
                op_map = {
                    "==": "=",
                    "!=": "!=",
                    "<": "<",
                    ">": ">",
                    "<=": "<=",
                    ">=": ">=",
                    "is": "IS",
                    "is not": "IS NOT",
                }
                sql_op = op_map.get(op, op)
                parts.append(f"({current_left} {sql_op} {right_sql})")

            current_left = right_sql

        if len(parts) == 1:
            return parts[0]
        else:
            return " AND ".join([f"({p})" for p in parts])

    def _generate_boolop(self, expr: BoolOpExpression) -> str:
        """Generate SQL for boolean operation."""
        value_sqls = [self.generate_expression(v) for v in expr.values]
        op = expr.operator.upper()
        return f"({f' {op} '.join([f'({v})' for v in value_sqls])})"

    def _generate_call(self, expr: CallExpression) -> str:
        """Generate SQL for function call."""
        func = expr.function
        args = [self.generate_expression(arg) for arg in expr.arguments]

        # Handle special functions
        if isinstance(func, ConstantExpression):
            func_name = func.value
            if func_name == "len" and len(args) == 1:
                # len() - get array length
                # The argument should be an AttributeExpression or ArrayAccessExpression
                arg = expr.arguments[0]
                if isinstance(arg, AttributeExpression):
                    base_expr = (
                        "json_each.value"
                        if arg.table_name == "json_each"
                        else f"{arg.table_name}.json_data"
                    )
                    if self.dialect == "sqlite":
                        return f"json_array_length(json_extract({base_expr}, '$.{arg.attribute_path}'))"
                    elif self.dialect == "postgres":
                        return f"JSON_ARRAY_LENGTH(JSON_EXTRACT_PATH({base_expr}, '{arg.attribute_path}'))"
                    else:
                        return f"json_array_length(json_extract({base_expr}, '$.{arg.attribute_path}'))"
                else:
                    # Fallback
                    return f"LENGTH({args[0]})"
            elif func_name == "json_array":
                # json_array() function call
                if self.dialect == "sqlite":
                    if len(args) == 0:
                        return "json_array()"
                    return f"json_array({', '.join(args)})"
                elif self.dialect == "postgres":
                    if len(args) == 0:
                        return "json_build_array()"
                    return f"json_build_array({', '.join(args)})"
                else:
                    if len(args) == 0:
                        return "json_array()"
                    return f"json_array({', '.join(args)})"

        # Handle method calls like .startswith() and .endswith()
        if isinstance(func, AttributeExpression):
            attr_path = func.attribute_path
            if attr_path.endswith(".startswith"):
                if len(args) != 1:
                    raise ValueError("startswith() requires exactly one argument")
                base_attr = AttributeExpression(
                    table_name=func.table_name,
                    attribute_path=attr_path.rsplit(".", 1)[0],
                    is_database_column=func.is_database_column,
                )
                base_sql = self.generate_expression(base_attr)
                pattern = args[0]
                # Remove quotes from pattern
                if pattern.startswith("'") and pattern.endswith("'"):
                    pattern = pattern[1:-1]
                elif pattern.startswith('"') and pattern.endswith('"'):
                    pattern = pattern[1:-1]
                return f"LIKE('{pattern}%', {base_sql})"
            elif attr_path.endswith(".endswith"):
                if len(args) != 1:
                    raise ValueError("endswith() requires exactly one argument")
                base_attr = AttributeExpression(
                    table_name=func.table_name,
                    attribute_path=attr_path.rsplit(".", 1)[0],
                    is_database_column=func.is_database_column,
                )
                base_sql = self.generate_expression(base_attr)
                pattern = args[0]
                if pattern.startswith("'") and pattern.endswith("'"):
                    pattern = pattern[1:-1]
                elif pattern.startswith('"') and pattern.endswith('"'):
                    pattern = pattern[1:-1]
                return f"LIKE('%{pattern}', {base_sql})"

        # Generic function call
        func_sql = self.generate_expression(func)
        return f"{func_sql}({', '.join(args)})"

    def _generate_if(self, expr: IfExpression) -> str:
        """Generate SQL for ternary expression."""
        test_sql = self.generate_expression(expr.test)
        body_sql = self.generate_expression(expr.body)
        orelse_sql = self.generate_expression(expr.orelse)
        return f"(CASE WHEN {test_sql} THEN {body_sql} ELSE {orelse_sql} END)"

    def _generate_listcomp(self, expr: ListComprehensionExpression) -> str:
        """Generate SQL for list comprehension."""
        # This is handled at the query level, not expression level
        # Return placeholder - actual generation happens in query builder
        return f"[{expr.item_var} for {expr.item_var} in {expr.array_info}]"

    def _generate_listcomp_in_select(
        self, expr: ListComprehensionExpression, query: SelectQuery
    ) -> str:
        """Generate SQL for list comprehension in SELECT clause."""
        # Create a parser with item_var context to properly resolve item.attr references
        # For now, we'll generate the expression - it should work if item_var is set in the query context
        # The expression was already parsed, so we just need to generate it
        expr_sql = self.generate_expression(expr.expression)

        # The FROM clause should already have json_each added
        # Return the expression SQL
        return expr_sql

    def _generate_any(self, expr: AnyExpression) -> str:
        """Generate SQL for any() pattern."""
        # Generate EXISTS subquery
        # Build array expression
        from .query_model import AttributeExpression

        array_attr = AttributeExpression(
            table_name=self.base_table,
            attribute_path=expr.array_path,
            is_database_column=False,
        )
        array_sql = self.generate_expression(array_attr)
        json_each_expr = self._format_json_each(array_sql)

        if expr.condition:
            # Parse condition with item_var context
            # For now, generate placeholder - condition needs special handling
            # The condition should reference the item variable
            condition_sql = "1=1"  # Placeholder
            return f"EXISTS (SELECT 1 FROM {json_each_expr} WHERE {condition_sql})"
        else:
            return f"EXISTS (SELECT 1 FROM {json_each_expr})"

    def _generate_array_expansion_expr(self, expr: ArrayExpansionExpression) -> str:
        """Generate SQL for array expansion expression."""
        # This is typically handled at the query level (FROM clause)
        # Return TRUE for now
        return "1=1"

    def _generate_tuple(self, expr: TupleExpression) -> str:
        """Generate SQL for tuple."""
        if len(expr.elements) == 0:
            return "()"
        element_sqls = [self.generate_expression(e) for e in expr.elements]
        return f"({', '.join(element_sqls)})"

    def _format_json_each(self, array_expr: str, path: str = "$") -> str:
        """Format json_each expression based on dialect."""
        if self.dialect == "sqlite":
            return f"json_each({array_expr}, '{path}')"
        elif self.dialect == "postgres":
            return f"LATERAL json_array_elements({array_expr}) AS json_each(value)"
        else:
            return f"json_each({array_expr}, '{path}')"

    def _get_base_table(self) -> str:
        """Get base table name - placeholder for now."""
        # This should be passed from the query context
        return getattr(self, "base_table", "person")

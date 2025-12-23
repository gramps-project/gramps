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
)
from .query_parser import QueryParser
from .sql_generator import SQLGenerator

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
    ):
        """
        Initialize QueryBuilder with table configuration.

        Args:
            table_name: Base table name (e.g., "person")
            json_extract: JSON extract pattern (deprecated, kept for compatibility)
            json_array_length: JSON array length pattern (deprecated, kept for compatibility)
            env: Environment dictionary for expression evaluation
            dialect: SQL dialect ("sqlite" or "postgres"). Defaults to "sqlite"
        """
        self.table_name = table_name
        self.dialect = dialect.lower()
        self.env = env if env is not None else {}
        database_columns = set(DATABASE_COLUMNS.get(table_name.capitalize(), []))

        # Create parser and generator
        self.parser = QueryParser(
            table_name=table_name,
            env=self.env,
            database_columns=database_columns,
            database_columns_dict=DATABASE_COLUMNS,
        )
        self.generator = SQLGenerator(dialect=self.dialect)

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

        # Parse order_by clause
        order_by_list = self._parse_order_by(order_by)

        # Detect table references and JOINs
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

        # Extract array expansion from WHERE condition if present
        # Array expansion is now represented as ArrayExpansionExpression in the parsed tree
        array_expansion = None
        is_array_expansion_in_or = False
        if where_condition:
            array_expansion, is_array_expansion_in_or = (
                self._extract_array_expansion_from_condition(where_condition)
            )

            # If array expansion is found, update parser context for item_var
            # This allows "item.attr" in what clause to be parsed correctly
            if array_expansion:
                self.parser.item_var = array_expansion.item_var
                self.parser.array_path = array_expansion.array_path

                # Re-parse what clause with item_var context if needed
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
        from .query_model import (
            CompareExpression,
            BoolOpExpression,
            AttributeExpression,
            ConstantExpression,
        )

        # Check if this is the array expansion condition itself
        # Pattern: item in person.array_path
        # Left side: item (parsed as AttributeExpression with table_name="json_each" when item_var is set,
        #            or as ConstantExpression with value="item" when not in array expansion context)
        # Right side: person.array_path (parsed as AttributeExpression)
        if isinstance(condition, CompareExpression):
            if len(condition.operators) == 1 and condition.operators[0] == "in":
                # Check if left is the item variable (could be AttributeExpression or ConstantExpression)
                left_is_item = False
                if isinstance(condition.left, AttributeExpression):
                    left_is_item = (
                        condition.left.table_name == "json_each"
                        and condition.left.attribute_path == ""
                    )
                elif isinstance(condition.left, ConstantExpression):
                    left_is_item = condition.left.value == array_expansion.item_var

                # Check if right matches the array path
                if (
                    left_is_item
                    and isinstance(condition.comparators[0], AttributeExpression)
                    and condition.comparators[0].attribute_path
                    == array_expansion.array_path
                ):
                    # This is the array expansion condition - remove it
                    return None

        # Check inside BoolOp expressions
        if isinstance(condition, BoolOpExpression):
            # Recursively remove from all values
            filtered_values = []
            for value in condition.values:
                filtered = self._remove_array_expansion_condition(
                    value, array_expansion
                )
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
                    operator=condition.operator,
                    values=filtered_values,
                )

        # Not an array expansion condition - return as-is
        return condition

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

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

from .expression_builder import ExpressionBuilder


class QueryBuilder:
    """
    SQL query builder that uses a single ExpressionBuilder instance.
    Consolidates all SQL generation logic for select_from_table.
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
            json_extract: JSON extract pattern (e.g., "json_extract(json_data, '$.{attr}')")
                          If None, will be set based on dialect
            json_array_length: JSON array length pattern
                              If None, will be set based on dialect
            env: Environment dictionary for expression evaluation
            dialect: SQL dialect ("sqlite" or "postgres"). Defaults to "sqlite"
        """
        self.table_name = table_name
        self.dialect = dialect.lower()
        self.env = env if env is not None else {}

        # Set json_extract and json_array_length based on dialect if not provided
        if json_extract is None:
            json_extract = self.format_json_extract("json_data")
        if json_array_length is None:
            json_array_length = self.format_json_array_length("json_data")

        self.json_extract = json_extract
        self.json_array_length = json_array_length

        # Create single ExpressionBuilder instance for primary conversions
        self.expression = ExpressionBuilder(
            table_name, json_extract, json_array_length, self.env
        )

    def _get_array_path_from_info(self, array_info):
        """
        Helper method to extract array path from array_info.
        Returns the path string for single arrays, or None for concatenated arrays.
        """
        if array_info and array_info.get("type") == "single":
            return array_info.get("path")
        return None

    def format_json_extract(self, base_expr):
        """
        Format JSON extract expression based on dialect.

        Args:
            base_expr: Base expression (e.g., "json_data", "json_each.value", "table.json_data")

        Returns:
            Formatted JSON extract pattern with {attr} placeholder
        """
        if self.dialect == "sqlite":
            # Use older json_extract() format for compatibility with older SQLite versions
            return f"json_extract({base_expr}, '$.{{attr}}')"
        elif self.dialect == "postgres":
            # PostgreSQL uses JSON_EXTRACT_PATH and removes $ prefix from path
            return f"JSON_EXTRACT_PATH({base_expr}, '{{attr}}')"
        else:
            # Default to SQLite format for backward compatibility
            return f"json_extract({base_expr}, '$.{{attr}}')"

    def format_json_array_length(self, base_expr):
        """
        Format JSON array length expression based on dialect.

        Args:
            base_expr: Base expression (e.g., "json_data", "json_each.value", "table.json_data")

        Returns:
            Formatted JSON array length pattern with {attr} placeholder
        """
        if self.dialect == "sqlite":
            # Use older json_extract() format for compatibility with older SQLite versions
            return f"json_array_length(json_extract({base_expr}, '$.{{attr}}'))"
        elif self.dialect == "postgres":
            # PostgreSQL uses JSON_EXTRACT_PATH and removes $ prefix from path
            return f"JSON_ARRAY_LENGTH(JSON_EXTRACT_PATH({base_expr}, '{{attr}}'))"
        else:
            # Default to SQLite format for backward compatibility
            return f"json_array_length(json_extract({base_expr}, '$.{{attr}}'))"

    def format_json_each(self, array_expr, path="$"):
        """
        Format json_each expression based on dialect.

        Args:
            array_expr: Array expression to iterate over
            path: JSON path (default '$' for SQLite, ignored for PostgreSQL)

        Returns:
            Formatted json_each expression that can be aliased and referenced as json_each.value
            For SQLite: returns "json_each(expr, '$')"
            For PostgreSQL: returns "LATERAL json_array_elements(expr) AS json_each(value)"
        """
        if self.dialect == "sqlite":
            return f"json_each({array_expr}, '{path}')"
        elif self.dialect == "postgres":
            # PostgreSQL uses json_array_elements with LATERAL join
            # LATERAL allows us to reference columns from the left side
            # AS json_each(value) creates table alias 'json_each' with column 'value'
            return f"LATERAL json_array_elements({array_expr}) AS json_each(value)"
        else:
            # Default to SQLite format for backward compatibility
            return f"json_each({array_expr}, '{path}')"

    def format_json_array(self, *args):
        """
        Format json_array expression based on dialect.

        Args:
            *args: Arguments to json_array function

        Returns:
            Formatted json_array expression
        """
        if self.dialect == "sqlite":
            if len(args) == 0:
                return "json_array()"
            args_str = ", ".join(str(arg) for arg in args)
            return f"json_array({args_str})"
        elif self.dialect == "postgres":
            # PostgreSQL uses json_build_array or jsonb_build_array
            # For now, use json_build_array
            if len(args) == 0:
                return "json_build_array()"
            args_str = ", ".join(str(arg) for arg in args)
            return f"json_build_array({args_str})"
        else:
            # Default to SQLite format for backward compatibility
            if len(args) == 0:
                return "json_array()"
            args_str = ", ".join(str(arg) for arg in args)
            return f"json_array({args_str})"

    def _create_array_expression(self, item_var, array_path):
        """
        Create a specialized expression for array expansion contexts.

        Args:
            item_var: Variable name for array iteration (e.g., "item")
            array_path: Array path for json_each (e.g., "event_ref_list")

        Returns:
            ExpressionBuilder instance configured for array expansion
        """
        json_extract_pattern = self.format_json_extract("json_each.value")
        json_array_length_pattern = self.format_json_array_length("json_each.value")

        return ExpressionBuilder(
            self.table_name,
            json_extract_pattern,
            json_array_length_pattern,
            self.env,
            item_var=item_var,
            array_path=array_path,
        )

    def _create_join_expression(self, table_name):
        """
        Create a specialized expression for JOIN attribute conversion.

        Args:
            table_name: Table name for the expression

        Returns:
            ExpressionBuilder instance configured for the specified table
        """
        json_extract_pattern = self.format_json_extract(f"{table_name}.json_data")
        json_array_length_pattern = self.format_json_array_length(
            f"{table_name}.json_data"
        )

        return ExpressionBuilder(
            table_name,
            json_extract_pattern,
            json_array_length_pattern,
            self.env,
        )

    def _convert_listcomp_expression(self, expression, expression_node):
        """
        Convert a list comprehension expression node to SQL.
        Handles tuples specially by converting each element to a separate column.

        Args:
            expression: ExpressionBuilder instance for conversion
            expression_node: AST node for the expression (can be Tuple, Attribute, etc.)

        Returns:
            String with SQL expression(s). For tuples, returns comma-separated columns.
        """
        if isinstance(expression_node, ast.Tuple):
            # Convert each element separately and join with commas (multiple columns)
            column_exprs = [
                str(expression.convert_to_sql(elt)) for elt in expression_node.elts
            ]
            return ", ".join(column_exprs)
        else:
            # Single expression - convert normally
            return str(expression.convert_to_sql(expression_node))

    def get_sql_query(self, what, where, order_by, page=None, page_size=None):
        """
        Generate complete SQL query from what, where, and order_by parameters.

        Handles all complex cases:
        - Table reference detection and JOINs
        - Array expansion in WHERE clause
        - Array expansion in OR expressions (UNION queries)
        - List comprehensions in WHAT clause
        - ORDER BY conversion
        - Pagination with LIMIT/OFFSET

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

        # Calculate offset if pagination is requested
        limit_offset = ""
        if page is not None and page_size is not None:
            if page < 1:
                raise ValueError("page must be >= 1")
            if page_size < 1:
                raise ValueError("page_size must be >= 1")
            offset = (page - 1) * page_size
            limit_offset = f" LIMIT {page_size} OFFSET {offset}"
        # Convert where to string if needed
        where_str = where
        if callable(where) or isinstance(where, types.LambdaType):
            raise ValueError(
                "Callables (lambda functions) are not supported for SQL generation. Please use string expressions instead."
            )
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
        if callable(what) or isinstance(what, types.LambdaType):
            raise ValueError(
                "Callables (lambda functions) are not supported for SQL generation. Please use string expressions instead."
            )
        elif isinstance(what, str):
            referenced_tables.update(
                self.expression.detect_table_references(
                    what, base_table=self.table_name
                )
            )
        elif isinstance(what, list):
            for w in what:
                if callable(w) or isinstance(w, types.LambdaType):
                    raise ValueError(
                        "Callables (lambda functions) are not supported for SQL generation. Please use string expressions instead."
                    )
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
                page=page,
                page_size=page_size,
            )

        # Check for list comprehension in what clause
        # Handle both string and list cases
        what_str = what
        what_is_list = isinstance(what, list) and len(what) > 0
        what_list_comprehension_idx = None
        what_other_fields = []

        if callable(what) or isinstance(what, types.LambdaType):
            raise ValueError(
                "Callables (lambda functions) are not supported for SQL generation. Please use string expressions instead."
            )
        elif what_is_list:
            # Check each element for list comprehension
            for idx, item in enumerate(what):
                if isinstance(item, str):
                    item_var, array_info, expr_node, cond_node = (
                        self.expression.detect_list_comprehension_in_what(item)
                    )
                    if item_var and array_info:
                        # Found list comprehension
                        what_list_comprehension_idx = idx
                        what_str = item
                        break
                    else:
                        what_other_fields.append(item)
                elif callable(item) or isinstance(item, types.LambdaType):
                    raise ValueError(
                        "Callables (lambda functions) are not supported for SQL generation. Please use string expressions instead."
                    )
                else:
                    what_other_fields.append(item)

            # If no list comprehension found, treat as single string if only one item
            if (
                what_list_comprehension_idx is None
                and len(what) == 1
                and isinstance(what[0], str)
            ):
                what_str = what[0]
            elif what_list_comprehension_idx is None:
                what_str = None
        elif not isinstance(what, str):
            what_str = None

        what_item_var, what_array_info, what_expression_node, what_condition_node = (
            self.expression.detect_list_comprehension_in_what(what_str)
        )

        # Build what expression
        what_condition_sql = None
        if what_item_var and what_array_info:
            # List comprehension in what clause
            # Handle both single array and concatenated arrays
            if what_array_info["type"] == "single":
                array_path = what_array_info["path"]
                what_expression = self._create_array_expression(
                    what_item_var, array_path
                )
                listcomp_expr = self._convert_listcomp_expression(
                    what_expression, what_expression_node
                )

                # Add other fields if what is a list
                if what_other_fields:
                    other_fields_sql = []
                    for field in what_other_fields:
                        if isinstance(field, str):
                            if field in ["obj", "person"]:
                                field = "json_data"
                            other_fields_sql.append(str(self.expression.convert(field)))
                        else:
                            other_fields_sql.append(str(self.expression.convert(field)))
                    what_expr = ", ".join(other_fields_sql + [listcomp_expr])
                else:
                    what_expr = listcomp_expr

                array_sql_expression = ExpressionBuilder(
                    self.table_name,
                    self.json_extract,
                    self.json_array_length,
                    self.env,
                )
                array_sql = array_sql_expression.convert(
                    f"{self.table_name}.{array_path}"
                )
                json_each_expr = self.format_json_each(array_sql)
                from_clause = f"{self.table_name}, {json_each_expr}"
                if what_condition_node:
                    what_condition_sql = what_expression.convert_to_sql(
                        what_condition_node
                    )
            elif what_array_info["type"] == "concatenated":
                # Handle concatenated arrays: [person.primary_name] + person.alternate_names
                # For SQLite, we need to use UNION query because subqueries can't see outer table
                # For PostgreSQL, we can use LATERAL joins
                left_node = what_array_info["left"]
                right_path = what_array_info["right_path"]

                # Create expression for the concatenated array
                what_expression = self._create_array_expression(
                    what_item_var, right_path  # Use right_path as base for expression
                )
                listcomp_expr = self._convert_listcomp_expression(
                    what_expression, what_expression_node
                )

                # Add other fields if what is a list
                if what_other_fields:
                    other_fields_sql = []
                    for field in what_other_fields:
                        if isinstance(field, str):
                            if field in ["obj", "person"]:
                                field = "json_data"
                            other_fields_sql.append(str(self.expression.convert(field)))
                        else:
                            other_fields_sql.append(str(self.expression.convert(field)))
                    what_expr = ", ".join(other_fields_sql + [listcomp_expr])
                else:
                    what_expr = listcomp_expr

                # Convert left side (person.primary_name) to SQL
                array_sql_expression = ExpressionBuilder(
                    self.table_name,
                    self.json_extract,
                    self.json_array_length,
                    self.env,
                )
                left_sql = str(array_sql_expression.convert_to_sql(left_node))
                # Wrap in json_array/json_build_array since it's a single item
                left_array_sql = self.format_json_array(left_sql)

                # Convert right side (person.alternate_names) to SQL
                right_sql = str(
                    array_sql_expression.convert(f"{self.table_name}.{right_path}")
                )

                if self.dialect == "postgres":
                    # PostgreSQL: use LATERAL joins which can reference outer table
                    left_json_each = f"LATERAL json_array_elements({left_array_sql}) AS left_each(value)"
                    right_json_each = (
                        f"LATERAL json_array_elements({right_sql}) AS right_each(value)"
                    )
                    json_each_expr = f"(SELECT value FROM {left_json_each} UNION ALL SELECT value FROM {right_json_each}) AS json_each"
                    from_clause = f"{self.table_name}, {json_each_expr}"
                else:
                    # SQLite: use UNION query - two separate SELECTs combined with UNION ALL
                    # This avoids subquery issues with table references
                    # json_each can reference outer table when used directly in FROM clause

                    # Convert condition if present
                    what_condition_sql = None
                    if what_condition_node:
                        what_condition_sql = what_expression.convert_to_sql(
                            what_condition_node
                        )

                    # Handle WHERE clause if present
                    where_sql = None
                    if where_str:
                        where_sql = self.expression.convert_where_clause(where_str)

                    # Build WHERE expressions for both queries
                    left_where_parts = []
                    right_where_parts = []
                    if where_sql:
                        left_where_parts.append(where_sql)
                        right_where_parts.append(where_sql)
                    if what_condition_sql:
                        left_where_parts.append(what_condition_sql)
                        right_where_parts.append(what_condition_sql)

                    left_where_expr = (
                        f" WHERE {' AND '.join(left_where_parts)}"
                        if left_where_parts
                        else ""
                    )
                    right_where_expr = (
                        f" WHERE {' AND '.join(right_where_parts)}"
                        if right_where_parts
                        else ""
                    )

                    # Build left query (from primary_name array)
                    left_from = (
                        f"{self.table_name}, {self.format_json_each(left_array_sql)}"
                    )
                    left_query = f"SELECT {what_expr} FROM {left_from}{left_where_expr}"

                    # Build right query (from alternate_names)
                    right_from = (
                        f"{self.table_name}, {self.format_json_each(right_sql)}"
                    )
                    right_query = (
                        f"SELECT {what_expr} FROM {right_from}{right_where_expr}"
                    )

                    # Handle ORDER BY
                    order_by_expr = ""
                    if order_by is not None:
                        if callable(order_by) or isinstance(order_by, types.LambdaType):
                            raise ValueError(
                                "Callables (lambda functions) are not supported for SQL generation. Please use string expressions instead."
                            )
                        elif callable(order_by) and not isinstance(order_by, type):
                            raise ValueError(
                                "Callables (lambda functions) are not supported for SQL generation. Please use string expressions instead."
                            )
                        elif isinstance(order_by, str):
                            order_by = [order_by]
                        converted_order_by = []
                        for expr in order_by:
                            if callable(expr) or isinstance(expr, types.LambdaType):
                                raise ValueError(
                                    "Callables (lambda functions) are not supported for SQL generation. Please use string expressions instead."
                                )
                            else:
                                converted_order_by.append(expr)
                        order_by_expr = self.expression.get_order_by(converted_order_by)

                    # Return the UNION query directly
                    return f"{left_query} UNION ALL {right_query}{order_by_expr}{limit_offset};"

                # For PostgreSQL, set what_condition_sql if needed
                if what_condition_node:
                    what_condition_sql = what_expression.convert_to_sql(
                        what_condition_node
                    )
        elif what is None:
            what_expr = "json_data"
        elif isinstance(what, types.LambdaType):
            raise ValueError(
                "Lambda functions are not supported for SQL generation. Please use string expressions instead."
            )
            what_expr = str(self.expression.convert(what_str))
        elif isinstance(what, str):
            if what in ["obj", "person"]:
                what = "json_data"
            if (
                is_array_expansion
                and item_var
                and (what.startswith(f"{item_var}.") or what == item_var)
            ):
                array_expansion_expression = self._create_array_expression(
                    item_var, array_path
                )
                what_expr = str(array_expansion_expression.convert(what))
            else:
                if has_joins:
                    join_expression = self._create_join_expression(self.table_name)
                    what_expr = str(join_expression.convert(what))
                else:
                    what_expr = str(self.expression.convert(what))
        else:
            what_list = []
            join_expression = None
            if has_joins:
                join_expression = self._create_join_expression(self.table_name)
            for w in what:
                if callable(w) or isinstance(w, types.LambdaType):
                    raise ValueError(
                        "Callables (lambda functions) are not supported for SQL generation. Please use string expressions instead."
                    )
                if w in ["obj", "person"]:
                    w = "json_data"
                if (
                    is_array_expansion
                    and item_var
                    and (w.startswith(f"{item_var}.") or w == item_var)
                ):
                    array_expansion_expression = self._create_array_expression(
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
            where_expression = self._create_join_expression(self.table_name)
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
        if what_item_var and what_array_info and what_condition_sql:
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
            json_each_expr = self.format_json_each(array_sql)
            if not (what_item_var and what_array_info):
                from_clause = f"{self.table_name}, {json_each_expr}"

        # Set from_clause if not already set
        if what_item_var and what_array_info:
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
                    left_expression = self._create_join_expression(left_table)
                    right_expression = self._create_join_expression(right_table)
                    # Build full expression paths - left_attr and right_attr may contain
                    # complex paths like "event_ref_list[person.birth_ref_index].ref"
                    # or simple paths like "handle"
                    left_expr = (
                        f"{left_table}.{left_attr}" if left_attr else f"{left_table}"
                    )
                    right_expr = (
                        f"{right_table}.{right_attr}"
                        if right_attr
                        else f"{right_table}"
                    )
                    left_sql = left_expression.convert(left_expr)
                    right_sql = right_expression.convert(right_expr)
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
            if callable(order_by) or isinstance(order_by, types.LambdaType):
                raise ValueError(
                    "Callables (lambda functions) are not supported for SQL generation. Please use string expressions instead."
                )
            elif callable(order_by) and not isinstance(order_by, type):
                raise ValueError(
                    "Callables (lambda functions) are not supported for SQL generation. Please use string expressions instead."
                )
            elif isinstance(order_by, str):
                order_by = [order_by]
            converted_order_by = []
            for expr in order_by:
                if isinstance(expr, types.LambdaType):
                    raise ValueError(
                        "Lambda functions are not supported for SQL generation. Please use string expressions instead."
                    )
                else:
                    converted_order_by.append(expr)
            if has_joins:
                order_by_expression = self._create_join_expression(self.table_name)
                order_by_expr = order_by_expression.get_order_by(
                    converted_order_by, has_joins=False
                )
            else:
                order_by_expr = self.expression.get_order_by(
                    converted_order_by, has_joins=False
                )

        return f"SELECT {what_expr} from {from_clause}{where_expr}{order_by_expr}{limit_offset};"

    def _build_union_query(
        self,
        what,
        where_str,
        order_by,
        item_var,
        array_path,
        join_conditions,
        has_joins,
        page=None,
        page_size=None,
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
            page: 1-based page number for pagination. Must be provided together with page_size.
            page_size: Number of items per page. Must be provided together with page.

        Returns:
            Complete UNION SQL query string
        """
        # Calculate offset if pagination is requested
        limit_offset = ""
        if page is not None and page_size is not None:
            if page < 1:
                raise ValueError("page must be >= 1")
            if page_size < 1:
                raise ValueError("page_size must be >= 1")
            offset = (page - 1) * page_size
            limit_offset = f" LIMIT {page_size} OFFSET {offset}"
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
        if callable(what) or isinstance(what, types.LambdaType):
            raise ValueError(
                "Callables (lambda functions) are not supported for SQL generation. Please use string expressions instead."
            )
        elif isinstance(what, list) and len(what) == 1 and isinstance(what[0], str):
            what_str = what[0]
        elif not isinstance(what, str):
            what_str = None

        (
            what_item_var,
            what_array_info,
            what_expression_node,
            what_condition_node,
        ) = self.expression.detect_list_comprehension_in_what(what_str)

        # Build what_expr (same for both queries)
        if what_item_var and what_array_info:
            what_array_path = self._get_array_path_from_info(what_array_info)
            if what_array_path:
                # Single array
                what_expression = self._create_array_expression(
                    what_item_var, what_array_path
                )
                what_expr = self._convert_listcomp_expression(
                    what_expression, what_expression_node
                )
                array_sql_expression = ExpressionBuilder(
                    self.table_name,
                    self.json_extract,
                    self.json_array_length,
                    self.env,
                )
                what_array_sql = array_sql_expression.convert(
                    f"{self.table_name}.{what_array_path}"
                )
                what_json_each_expr = self.format_json_each(what_array_sql)
            else:
                # Concatenated arrays - not supported in UNION queries yet
                # For now, raise an error or handle gracefully
                raise ValueError(
                    "Concatenated arrays in list comprehensions are not supported in UNION queries"
                )
        elif what is None:
            what_expr = "json_data"
        elif isinstance(what, types.LambdaType):
            raise ValueError(
                "Lambda functions are not supported for SQL generation. Please use string expressions instead."
            )
            what_expr = str(self.expression.convert(what_str))
        elif isinstance(what, str):
            if what in ["obj", "person"]:
                what = "json_data"
            if what.startswith(f"{item_var}.") or what == item_var:
                array_expansion_expression = self._create_array_expression(
                    item_var, array_path
                )
                what_expr = str(array_expansion_expression.convert(what))
            else:
                what_expr = str(self.expression.convert(what))
        else:
            what_list = []
            for w in what:
                if callable(w) or isinstance(w, types.LambdaType):
                    raise ValueError(
                        "Callables (lambda functions) are not supported for SQL generation. Please use string expressions instead."
                    )
                if w in ["obj", "person"]:
                    w = "json_data"
                if w.startswith(f"{item_var}.") or w == item_var:
                    array_expansion_expression = self._create_array_expression(
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

        if what_item_var and what_array_info and what_condition_node:
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

        if what_item_var and what_array_info:
            left_from_clause = f"{self.table_name}, {what_json_each_expr}"
        else:
            left_from_clause = self.table_name
        left_query = f"SELECT {what_expr} FROM {left_from_clause}{left_where_expr}"

        # Build right query (with array expansion)
        if len(right_parts) == 1:
            right_where_node = right_parts[0]
        else:
            right_where_node = ast.BoolOp(op=ast.And(), values=right_parts)

        right_expression = self._create_array_expression(item_var, array_path)
        right_where_sql = right_expression._convert_node_with_replacements(
            right_where_node, exclude_array_expansion=True
        )
        right_where_sql = (
            str(right_where_sql)
            if not isinstance(right_where_sql, str)
            else right_where_sql
        )

        if what_item_var and what_array_info and what_condition_node:
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
        json_each_expr = self.format_json_each(array_sql)

        if what_item_var and what_array_info:
            what_array_path = self._get_array_path_from_info(what_array_info)
            if what_array_path and what_array_path == array_path:
                right_from_clause = f"{self.table_name}, {json_each_expr}"
            elif what_array_path:
                right_from_clause = (
                    f"{self.table_name}, {what_json_each_expr}, {json_each_expr}"
                )
            else:
                # Concatenated arrays - not supported in UNION queries
                right_from_clause = f"{self.table_name}, {json_each_expr}"
        else:
            right_from_clause = f"{self.table_name}, {json_each_expr}"

        right_query = f"SELECT {what_expr} FROM {right_from_clause}{right_where_expr}"

        # Handle ORDER BY after UNION
        if order_by is None:
            order_by_expr = ""
        else:
            if callable(order_by) or isinstance(order_by, types.LambdaType):
                raise ValueError(
                    "Callables (lambda functions) are not supported for SQL generation. Please use string expressions instead."
                )
            elif callable(order_by) and not isinstance(order_by, type):
                raise ValueError(
                    "Callables (lambda functions) are not supported for SQL generation. Please use string expressions instead."
                )
            elif isinstance(order_by, str):
                order_by = [order_by]
            converted_order_by = []
            for expr in order_by:
                if isinstance(expr, types.LambdaType):
                    raise ValueError(
                        "Lambda functions are not supported for SQL generation. Please use string expressions instead."
                    )
                else:
                    converted_order_by.append(expr)
            order_by_expr = self.expression.get_order_by(converted_order_by)

        return f"{left_query} UNION {right_query}{order_by_expr}{limit_offset};"

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


class Evaluator:
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
        self.env = env
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
            # Default to "and" for unknown operators
            return "and"

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

        except (SyntaxError, AttributeError):
            # Not a valid expression or doesn't match pattern
            pass

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

        except (SyntaxError, AttributeError):
            # Not a valid expression or doesn't match pattern
            pass

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

        except (SyntaxError, AttributeError):
            pass

        return False

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
                return AttributeNode(
                    self.json_extract, self.json_array_length, self.table_name, attr
                )
            elif isinstance(obj, AttributeNode):
                obj.attr += ".%s" % attr
                return obj
            else:
                return getattr(obj, attr)
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
            if value in self.env:
                return self.env[value]
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
        except (SyntaxError, AttributeError):
            # If parsing fails, fall back to simple conversion
            return str(self.convert(where_str))

        # If array expansion is excluded but we have item_var, create evaluator with item_var set
        # This is needed to process remaining conditions like "item.role.value == 1"
        if exclude_array_expansion and item_var and array_path:
            # Create evaluator with item_var set for processing remaining conditions
            condition_evaluator = Evaluator(
                self.table_name,
                "json_extract(json_each.value, '$.{attr}')",
                "json_array_length(json_extract(json_each.value, '$.{attr}'))",
                self.env,
                item_var=item_var,
                array_path=array_path,
            )
            # Use the condition evaluator for conversion
            result = condition_evaluator._convert_node_with_replacements(
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
                condition_evaluator = Evaluator(
                    self.table_name,
                    "json_extract(json_each.value, '$.{attr}')",
                    "json_array_length(json_extract(json_each.value, '$.{attr}'))",
                    self.env,
                    item_var=item_var,
                    array_path=array_path,
                )
                condition_sql = condition_evaluator.convert_to_sql(condition_node)
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
                    converted_values.append(f"({value_sql})")

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

    def get_order_by(self, order_by):
        order_by_exprs = []
        for expr in order_by:
            # Handle string with "-" prefix for descending
            if isinstance(expr, str) and expr.startswith("-"):
                order_by_exprs.append("%s %s" % (self.convert(expr[1:]), "DESC"))
            else:
                # Handle string expression (lambdas should already be converted to strings)
                order_by_exprs.append(str(self.convert(expr)))

        if order_by_exprs:
            order_expr = " ORDER BY %s" % (", ".join(order_by_exprs))
        else:
            order_expr = ""

        return order_expr

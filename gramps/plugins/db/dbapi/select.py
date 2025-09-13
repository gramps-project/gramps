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

    def __init__(self, table_name, json_extract, json_array_length, env):
        self.json_extract = json_extract
        self.json_array_length = json_array_length
        self.table_name = table_name
        self.env = env
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

    def convert_to_sql(self, node):
        if isinstance(node, ast.Num):
            return str(node.n)
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
        elif isinstance(node, (ast.Constant, ast.NameConstant)):
            if node.value is None:
                return "null"
            else:
                return repr(node.value)
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
        elif isinstance(node, ast.Str):
            ## Python 3.7
            return repr(node.s)
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
            if obj in [self.table_name, "_"]:
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
            elif isinstance(function_name, AttributeNode):
                if any(
                    [
                        function_name.attr.endswith(x)
                        for x in [
                            ".contains",
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

                    if function_name.attr.endswith(".contains"):
                        function_name.remove_attribute()
                        return "like('%s', %s)" % (
                            "%" + args[0][1:-1] + "%",
                            function_name,
                        )
                    elif function_name.attr.endswith(".endswith"):
                        function_name.remove_attribute()
                        return "like('%s', %s)" % ("%" + args[0][1:-1], function_name)
                        pass
                    elif function_name.attr.endswith(".startswith"):
                        function_name.remove_attribute()
                        return "like('%s', %s)" % (args[0][1:-1] + "%", function_name)
                    else:
                        raise Exception("unhandled function")

            else:
                raise ValueError("unknown function %r" % function_name)

        raise TypeError(node)

    def convert(self, python_expr):
        node = ast.parse(python_expr, mode="eval").body
        sql_expr = self.convert_to_sql(node)
        return sql_expr

    def get_order_by(self, order_by):
        order_by_exprs = []
        for expr in order_by:
            if expr.startswith("-"):
                order_by_exprs.append("%s %s" % (self.convert(expr[1:]), "DESC"))
            else:
                order_by_exprs.append(str(self.convert(expr)))

        if order_by_exprs:
            order_expr = " ORDER BY %s" % (", ".join(order_by_exprs))
        else:
            order_expr = ""

        return order_expr

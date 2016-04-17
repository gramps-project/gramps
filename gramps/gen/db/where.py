#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2016       Gramps Development Team
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
#

from meta.asttools import Visitor
from meta.decompiler import _ast, decompile_func

import copy

class ParseFilter(Visitor):
    def visitName(self, node):
        return node.id
    
    def visitNum(self, node):
        return node.n
        
    def visitlong(self, node):
        return node

    def process_expression(self, expr):
        if isinstance(expr, str):
            # boolean
            return [self.process_field(expr), "==", True]
        elif len(expr) == 3:
            # (field, op, value)
            return [self.process_field(expr[0]), 
                    expr[1], 
                    self.process_value(expr[2])]
        else:
            # list of exprs
            return [self.process_expression(exp) for
                    exp in expr]

    def process_value(self, value):
        try:
            return eval(value, self.env)
        except:
            return value

    def process_field(self, field):
        field = field.replace("[", ".").replace("]", "")
        if field.startswith(self.parameter + "."):
            return field[len(self.parameter) + 1:]
        else:
            return field

    def visitCall(self, node):
        """
        Handle LIKE()
        """
        return [self.process_field(self.visit(node.args[0])), 
                self.visit(node.func),
                self.process_value(self.visit(node.args[1]))]

    def visitStr(self, node):
        return node.s

    def visitlist(self, list):
        return [self.visit(node) for node in list]

    def visitCompare(self, node):
        return [self.process_field(self.visit(node.left)), 
                " ".join(self.visit(node.ops)), 
                self.process_value(self.visit(node.comparators[0]))]

    def visitAttribute(self, node):
        return "%s.%s" % (self.visit(node.value), node.attr)

    def get_boolean_op(self, node):
        if isinstance(node, _ast.And):
            return "AND"
        elif isinstance(node, _ast.Or):
            return "OR"
        else:
            raise Exception("invalid boolean")

    def visitNotEq(self, node):
        return "!="

    def visitLtE(self, node):
        return "<="

    def visitGtE(self, node):
        return ">="

    def visitEq(self, node):
        return "=="

    def visitBoolOp(self, node):
        """
        BoolOp: boolean operator
        """
        op = self.get_boolean_op(node.op)
        values = list(node.values)
        return [op, self.process_expression(
            [self.visit(value) for value in values])]

    def visitLambda(self, node):
        self.parameter = self.visit(node.args)[0]
        return self.visit(node.body)

    def visitarguments(self, node):
        return [self.visit(arg) for arg in node.args]

    def visitarg(self, node):
        return node.arg

    def visitSubscript(self, node):
        return "%s[%s]" % (self.visit(node.value), 
                          self.visit(node.slice))

    def visitIndex(self, node):
        return self.visit(node.value)

def make_env(closure):
    """
    Create an environment from the closure.
    """
    env = copy.copy(closure.__globals__)
    if closure.__closure__:
        for i in range(len(closure.__closure__)):
            env[closure.__code__.co_freevars[i]] = closure.__closure__[i].cell_contents
    return env

def eval_where(closure):
    """
    Given a closure, parse and evaluate it.
    Return a WHERE expression.
    """
    parser = ParseFilter()
    parser.env = make_env(closure)
    ast_top = decompile_func(closure)
    result = parser.visit(ast_top)
    return result


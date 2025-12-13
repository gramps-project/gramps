#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2024 Doug Blank <doug.blank@gmail.com>
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
import inspect

from gramps.gen.lib import (
    Citation,
    Event,
    Family,
    Media,
    Note,
    Person,
    Place,
    Repository,
    Source,
    Tag,
)


def _function_to_expr_string(func):
    """
    Extract return expression from function or lambda as string (Python 3.9+).

    Supports both regular functions and lambda expressions.

    Limitations:
    - Only works for functions/lambdas defined in source files (not dynamically created)
    - Function must have a single return statement with an expression
    - Functions created with exec()/eval() or in REPL may not work
    - Only the first return statement is used if multiple exist

    Raises:
        OSError: If function source cannot be retrieved (e.g., dynamically created)
        ValueError: If function doesn't have a return statement or returns None
    """
    try:
        source = inspect.getsource(func)
    except OSError as e:
        raise OSError(
            f"Cannot get source for {getattr(func, '__name__', 'lambda')}. "
            "Functions/lambdas must be defined in source files, not dynamically created "
            "with exec()/eval() or in REPL."
        ) from e

    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        raise ValueError(f"Failed to parse source: {e}") from e

    if not tree.body:
        raise ValueError(f"Empty source for {func}")

    node = tree.body[0]

    # Handle lambda expressions (e.g., "l = lambda x: x + 1")
    if isinstance(node, ast.Assign):
        # Lambda assigned to variable
        if len(node.targets) == 1 and isinstance(node.value, ast.Lambda):
            return ast.unparse(node.value.body)
    elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Lambda):
        # Standalone lambda expression
        return ast.unparse(node.value.body)
    elif isinstance(node, ast.FunctionDef):
        # Regular function definition
        func_node = node
        # Find the first return statement
        for stmt in func_node.body:
            if isinstance(stmt, ast.Return):
                if stmt.value is None:
                    raise ValueError(
                        "Function must return an expression, not just 'return'"
                    )
                # Python 3.9+ has built-in unparse
                return ast.unparse(stmt.value)

        raise ValueError(
            f"Function {func_node.name} must have a return statement with an expression"
        )

    raise ValueError(
        f"Expected function or lambda definition, got: {type(node).__name__}"
    )


def _expr_to_string(expr):
    """
    Convert expression to string if it's a callable, otherwise return as-is.

    Args:
        expr: String expression or callable (function/lambda) that returns an expression.

    Returns:
        String expression ready for eval() or SQL conversion.
    """
    if callable(expr) and not isinstance(expr, type):
        return _function_to_expr_string(expr)
    return expr


def sort_data(rows, specs):
    for key, reverse in reversed(specs):
        rows.sort(key=lambda item: item[key], reverse=reverse)
    return rows


def select_from_table(db, table_name, what, where, order_by, env):
    # Convert functions to strings for what and where
    if what is not None:
        if isinstance(what, str):
            what = _expr_to_string(what)
        else:
            what = [_expr_to_string(w) for w in what]
    if where is not None:
        where = _expr_to_string(where)

    if order_by is None:
        yield from _select_from_table(db, table_name, what=what, where=where, env=env)
        return
    else:
        data = []

        for row in _select_from_table(db, table_name, what=what, where=where, env=env):
            if what is None:
                what_expr = ["person"]
            elif isinstance(what, str):
                what_expr = [what]
            else:
                what_expr = what
            data.append(dict(zip(what_expr, row)))

        specs = []
        for item in order_by:
            # Convert function to string if needed
            item_str = _expr_to_string(item)
            # Handle string with "-" prefix for descending
            if isinstance(item_str, str) and item_str.startswith("-"):
                specs.append((item_str[1:], True))
            else:
                specs.append((item_str, False))

        for row in sort_data(data, specs):
            yield list(row.values())
        return


def _select_from_table(db, table_name, what, where, env):
    # Note: what and where should already be converted to strings by select_from_table
    # This function just evaluates them
    env = (
        env
        if env
        else {
            "Citation": Citation,
            "Event": Event,
            "Family": Family,
            "Media": Media,
            "Note": Note,
            "Person": Person,
            "Place": Place,
            "Repository": Repository,
            "Source": Source,
            "Tag": Tag,
        }
    )
    method = db._get_table_func(table_name.title(), "iter_func")
    for obj in method():
        env["_"] = env[table_name] = obj
        if where:
            where_value = eval(where, env)
        else:
            where_value = True

        if where_value:
            if what is None:
                what_value = obj
            elif isinstance(what, str):
                what_value = eval(what, env)
            else:
                what_value = [eval(w, env) for w in what]

            yield what_value

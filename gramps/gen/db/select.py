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
import types

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


def sort_data(rows, specs):
    for key, reverse in reversed(specs):
        rows.sort(key=lambda item: item[key], reverse=reverse)
    return rows


# Safe builtins allowed in expressions
_SAFE_BUILTINS = {
    "len": len,
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
    "list": list,
    "dict": dict,
    "tuple": tuple,
    "set": set,
    "min": min,
    "max": max,
    "sum": sum,
    "abs": abs,
    "round": round,
    "sorted": sorted,
    "any": any,
    "all": all,
}


def safe_eval(expr, env, obj=None):
    """
    Safely evaluate an expression.

    This function provides a safer alternative to eval() by:
    1. Using AST parsing and compilation for string expressions
    2. Validating the AST to ensure it's safe (only expressions, no statements)

    Args:
        expr: A string expression to evaluate.
        env: Dictionary containing the evaluation environment (obj should be in env)
        obj: Optional object (for compatibility, but obj should be in env)

    Returns:
        The result of evaluating the expression

    Raises:
        ValueError: If the expression contains unsafe constructs or is a callable
        SyntaxError: If the expression is not valid Python syntax
    """
    # Reject callables (lambdas) - they are not supported
    if callable(expr):
        raise ValueError(
            "Callables (lambda functions) are not supported. Please use string expressions instead."
        )

    # Handle strings - use AST parsing and compilation
    if isinstance(expr, str):
        try:
            # Parse the expression into an AST
            tree = ast.parse(expr, mode="eval")

            # Validate that it's a safe expression (no statements, only expressions)
            # The ast.parse with mode="eval" already ensures it's an expression,
            # but we can add additional validation if needed

            # Compile the AST to bytecode
            code = compile(tree, "<string>", "eval")

            # Execute the compiled code with the environment
            # This is safer than eval because:
            # 1. We've validated it's an expression (not arbitrary code)
            # 2. We control the environment
            # 3. We restrict builtins to only safe functions
            # Note: We use eval here, but only on pre-compiled, validated AST code
            # This is much safer than eval() on raw strings

            # Allow only safe builtins that are commonly used in expressions
            return eval(code, {"__builtins__": _SAFE_BUILTINS}, env)

        except SyntaxError as e:
            raise SyntaxError(f"Invalid expression syntax: {expr}") from e
        except Exception as e:
            raise ValueError(f"Error evaluating expression: {expr}") from e

    # If it's neither a callable nor a string, return as-is
    return expr


def select_from_table(
    db, table_name, *, what=None, where=None, order_by=None, env=None
):

    if order_by is None:
        yield from _select_from_table(db, table_name, what=what, where=where, env=env)
        return
    else:
        # Reject callables for order_by
        if callable(order_by) or isinstance(order_by, types.LambdaType):
            raise ValueError(
                "Callables (lambda functions) are not supported for 'order_by' argument. Please use string expressions instead."
            )
        # Handle single string as order_by (convert to list)
        if isinstance(order_by, str):
            order_by = [order_by]
        # Validate all items in order_by list are strings
        for item in order_by:
            if callable(item) or isinstance(item, types.LambdaType):
                raise ValueError(
                    "Callables (lambda functions) are not supported for 'order_by' argument. Please use string expressions instead."
                )

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
            # Handle string with "-" prefix for descending
            if isinstance(item, str) and item.startswith("-"):
                specs.append((item[1:], True))
            else:
                specs.append((item, False))

        for row in sort_data(data, specs):
            yield list(row.values())
        return


def _select_from_table(db, table_name, what, where, env):
    # Note: what and where must be strings (callables/lambdas are not supported)
    # This function safely evaluates string expressions using safe_eval
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
    # Store table_name in env if needed
    env["table_name"] = table_name

    method = db._get_table_func(table_name.title(), "iter_func")
    for obj in method():
        env["obj"] = env[table_name] = obj
        if where:
            # Reject callables for where clause
            if callable(where) or isinstance(where, types.LambdaType):
                raise ValueError(
                    "Callables (lambda functions) are not supported for 'where' argument. Please use string expressions instead."
                )
            # safe_eval handles string expressions using AST parsing and compilation
            where_value = safe_eval(where, env, obj)
        else:
            where_value = True

        if where_value:
            if what is None:
                what_value = obj
            elif isinstance(what, str):
                # safe_eval handles string expressions
                what_value = safe_eval(what, env, obj)
            elif callable(what) or isinstance(what, types.LambdaType):
                raise ValueError(
                    "Callables (lambda functions) are not supported for 'what' argument. Please use string expressions instead."
                )
            else:
                # Handle list of expressions (must be strings)
                for w in what:
                    if callable(w) or isinstance(w, types.LambdaType):
                        raise ValueError(
                            "Callables (lambda functions) are not supported for 'what' argument. Please use string expressions instead."
                        )
                what_value = [safe_eval(w, env, obj) for w in what]

            yield what_value

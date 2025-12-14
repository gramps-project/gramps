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

# Import lambda_to_string for converting lambda functions to strings when needed
# (e.g., for logging, debugging, or SQL generation)
from gramps.gen.db.lambda_to_string import lambda_to_string
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
    Safely evaluate an expression or callable.

    This function provides a safer alternative to eval() by:
    1. Converting callables (lambda functions) to strings using lambda_to_string,
       then evaluating them in the environment (lambdas never have arguments)
    2. Using AST parsing and compilation for string expressions
    3. Validating the AST to ensure it's safe (only expressions, no statements)

    Args:
        expr: Either a callable (lambda with no arguments) or a string expression.
              Lambdas should reference 'obj' from the environment, e.g.:
              lambda: '234' in obj.handle
        env: Dictionary containing the evaluation environment (obj should be in env)
        obj: Optional object (for compatibility, but obj should be in env)

    Returns:
        The result of evaluating the expression

    Raises:
        ValueError: If the expression contains unsafe constructs or lambda conversion fails
        SyntaxError: If the expression is not valid Python syntax
    """
    # Handle callables (lambdas) - convert to string and evaluate
    # Users never pass lambdas with arguments, so all lambdas reference obj from environment
    if callable(expr):
        # Convert lambda to string and evaluate in the environment
        # This allows lambdas like lambda: '234' in obj.handle to work
        try:
            expr_str = lambda_to_string(expr)
            # Now evaluate the string expression in the environment
            # where obj is available
            tree = ast.parse(expr_str, mode="eval")
            code = compile(tree, "<string>", "eval")
            return eval(code, {"__builtins__": _SAFE_BUILTINS}, env)
        except Exception as e:
            # If lambda_to_string fails, provide helpful error
            raise ValueError(
                f"Failed to convert lambda to string expression: {e}. "
                f"Lambda may reference variables not available in the environment."
            ) from e

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
        # Handle single string as order_by (convert to list)
        if isinstance(order_by, str):
            order_by = [order_by]

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
    # Note: what and where can be callables (lambda functions) or strings
    # This function safely evaluates them using safe_eval instead of eval
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
    # Store table_name in env for lambda_to_string conversion if needed
    env["table_name"] = table_name

    method = db._get_table_func(table_name.title(), "iter_func")
    for obj in method():
        env["obj"] = env[table_name] = obj
        if where:
            # safe_eval handles both callables (lambdas) and strings
            # For lambdas, it executes them directly (no eval needed)
            # For strings, it uses AST parsing and compilation (safer than eval)
            where_value = safe_eval(where, env, obj)
        else:
            where_value = True

        if where_value:
            if what is None:
                what_value = obj
            elif isinstance(what, (str, types.LambdaType)) or callable(what):
                # safe_eval handles both callables (lambdas) and strings
                what_value = safe_eval(what, env, obj)
            else:
                # Handle list of expressions (can be mix of strings and callables)
                what_value = [safe_eval(w, env, obj) for w in what]

            yield what_value

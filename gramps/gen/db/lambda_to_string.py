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
import dis
import marshal
import types


def ast_to_string(node):
    """
    Convert an AST node to its string representation.

    This function recursively converts AST nodes to their Python source
    code string representation. It handles lambda expressions, expressions,
    statements, and various Python constructs.

    Args:
        node: An AST node (e.g., ast.Lambda, ast.Expression, etc.)

    Returns:
        String representation of the AST node

    Examples:
        # Convert a lambda AST node to string
        lambda_ast = ast.parse("lambda x: x + 1", mode="eval").body
        result = ast_to_string(lambda_ast)
        # Returns: "lambda x: x + 1"

        # Convert an expression AST node to string
        expr_ast = ast.parse("person.handle == 'A6E74B3D65D23F'", mode="eval").body
        result = ast_to_string(expr_ast)
        # Returns: "person.handle == 'A6E74B3D65D23F'"

    Limitations (Python 3.10+):
        - Comprehensions (list, set, dict comprehensions): Not supported
        - Match/case statements: Not supported (not relevant for lambda expressions)
        - Type annotations with union syntax (X | Y): Not fully supported
          (type hints are preserved but union syntax may not roundtrip perfectly)
        - Walrus operator (:=): Not supported
        - Parenthesized context managers: Not relevant for expressions
        - String quote normalization: Python's repr() may use single or double
          quotes, so the output may differ from input in quote style only
        - Operator precedence: Parentheses are added conservatively to preserve
          meaning, which may differ from minimal parenthesization
        - Comments and formatting: All comments and original formatting are lost
          (AST doesn't preserve these)
    """
    if isinstance(node, ast.Lambda):
        args_str = _args_to_string(node.args)
        body_str = ast_to_string(node.body)
        # No space before colon if no arguments
        if args_str:
            return f"lambda {args_str}: {body_str}"
        else:
            return f"lambda: {body_str}"

    elif isinstance(node, ast.Expression):
        return ast_to_string(node.body)

    elif isinstance(node, ast.Constant):
        return repr(node.value)

    elif isinstance(node, ast.Name):
        return node.id

    elif isinstance(node, ast.Attribute):
        value_str = ast_to_string(node.value)
        return f"{value_str}.{node.attr}"

    elif isinstance(node, ast.BinOp):
        left_str = ast_to_string(node.left)
        right_str = ast_to_string(node.right)
        op_str = _operator_to_string(node.op)
        # Add parentheses for clarity in complex expressions
        return f"({left_str} {op_str} {right_str})"

    elif isinstance(node, ast.UnaryOp):
        operand_str = ast_to_string(node.operand)
        op_str = _operator_to_string(node.op)
        # Add space after "not" operator
        if isinstance(node.op, ast.Not):
            return f"{op_str} {operand_str}"
        else:
            return f"{op_str}{operand_str}"

    elif isinstance(node, ast.Compare):
        left_str = ast_to_string(node.left)
        parts = [left_str]
        for op, comparator in zip(node.ops, node.comparators):
            op_str = _operator_to_string(op)
            comp_str = ast_to_string(comparator)
            parts.append(f"{op_str} {comp_str}")
        return " ".join(parts)

    elif isinstance(node, ast.BoolOp):
        values_str = [ast_to_string(v) for v in node.values]
        op_str = _operator_to_string(node.op)
        return f"({f' {op_str} '.join(values_str)})"

    elif isinstance(node, ast.IfExp):
        test_str = ast_to_string(node.test)
        body_str = ast_to_string(node.body)
        orelse_str = ast_to_string(node.orelse)
        return f"{body_str} if {test_str} else {orelse_str}"

    elif isinstance(node, ast.Call):
        func_str = ast_to_string(node.func)
        args_str = ", ".join(ast_to_string(arg) for arg in node.args)
        if node.keywords:
            keywords_str = ", ".join(
                (
                    f"{kw.arg}={ast_to_string(kw.value)}"
                    if kw.arg
                    else f"**{ast_to_string(kw.value)}"
                )
                for kw in node.keywords
            )
            if args_str:
                args_str = f"{args_str}, {keywords_str}"
            else:
                args_str = keywords_str
        return f"{func_str}({args_str})"

    elif isinstance(node, ast.Subscript):
        value_str = ast_to_string(node.value)
        slice_str = _slice_to_string(node.slice)
        return f"{value_str}[{slice_str}]"

    elif isinstance(node, ast.List):
        elts_str = ", ".join(ast_to_string(elt) for elt in node.elts)
        return f"[{elts_str}]"

    elif isinstance(node, ast.Tuple):
        elts_str = ", ".join(ast_to_string(elt) for elt in node.elts)
        if len(node.elts) == 1:
            return f"({elts_str},)"
        return f"({elts_str})"

    else:
        # For unhandled node types, try to get a basic representation
        return f"<{type(node).__name__}>"


def _args_to_string(args_node):
    """Convert ast.arguments to string representation."""
    args = []

    # Positional arguments
    for arg in args_node.args:
        arg_str = arg.arg
        if arg.annotation:
            arg_str += f": {ast_to_string(arg.annotation)}"
        args.append(arg_str)

    # *args
    if args_node.vararg:
        vararg_str = args_node.vararg.arg
        if args_node.vararg.annotation:
            vararg_str += f": {ast_to_string(args_node.vararg.annotation)}"
        args.append(f"*{vararg_str}")

    # Keyword-only arguments
    for kwarg in args_node.kwonlyargs:
        kwarg_str = kwarg.arg
        if kwarg.annotation:
            kwarg_str += f": {ast_to_string(kwarg.annotation)}"
        default = None
        if args_node.kw_defaults:
            idx = args_node.kwonlyargs.index(kwarg)
            if idx < len(args_node.kw_defaults):
                default = args_node.kw_defaults[idx]
        if default is not None:
            kwarg_str += f"={ast_to_string(default)}"
        args.append(kwarg_str)

    # **kwargs
    if args_node.kwarg:
        kwarg_str = args_node.kwarg.arg
        if args_node.kwarg.annotation:
            kwarg_str += f": {ast_to_string(args_node.kwarg.annotation)}"
        args.append(f"**{kwarg_str}")

    # Default values for positional args
    if args_node.defaults:
        num_defaults = len(args_node.defaults)
        num_args = len(args_node.args)
        for i, default in enumerate(args_node.defaults):
            arg_idx = num_args - num_defaults + i
            if arg_idx >= 0:
                args[arg_idx] += f"={ast_to_string(default)}"

    return ", ".join(args)


def _operator_to_string(op):
    """Convert an operator AST node to its string representation."""
    op_map = {
        ast.Add: "+",
        ast.Sub: "-",
        ast.Mult: "*",
        ast.Div: "/",
        ast.Mod: "%",
        ast.Pow: "**",
        ast.LShift: "<<",
        ast.RShift: ">>",
        ast.BitOr: "|",
        ast.BitXor: "^",
        ast.BitAnd: "&",
        ast.FloorDiv: "//",
        ast.And: "and",
        ast.Or: "or",
        ast.Eq: "==",
        ast.NotEq: "!=",
        ast.Lt: "<",
        ast.LtE: "<=",
        ast.Gt: ">",
        ast.GtE: ">=",
        ast.Is: "is",
        ast.IsNot: "is not",
        ast.In: "in",
        ast.NotIn: "not in",
        ast.Not: "not",
        ast.USub: "-",
        ast.UAdd: "+",
        ast.Invert: "~",
    }
    return op_map.get(type(op), f"<{type(op).__name__}>")


def _slice_to_string(slice_node):
    """Convert a slice AST node to string representation."""
    if isinstance(slice_node, ast.Slice):
        lower = ast_to_string(slice_node.lower) if slice_node.lower else ""
        upper = ast_to_string(slice_node.upper) if slice_node.upper else ""
        step = ast_to_string(slice_node.step) if slice_node.step else ""
        if step:
            return f"{lower}:{upper}:{step}"
        elif upper:
            return f"{lower}:{upper}"
        elif lower:
            return f"{lower}:"
        else:
            return ":"
    elif isinstance(slice_node, ast.ExtSlice):
        dims = ", ".join(_slice_to_string(dim) for dim in slice_node.dims)
        return dims
    else:
        return ast_to_string(slice_node)


def lambda_to_string(lambda_func):
    """
    Convert a lambda function object to its string representation using bytecode decompilation.

    This function decompiles a lambda function from its bytecode and reconstructs
    the source code. Works reliably for Python 3.10+ with simple expressions:
    - Comparisons (==, !=, <, <=, >, >=, in, not in, is, is not)
    - Logical operations (and, or, not)
    - Attribute access
    - Function calls
    - Subscripts
    - Nested operations

    Args:
        lambda_func: A lambda function object (must have no arguments)

    Returns:
        String representation of the lambda body (without "lambda: " prefix)

    Examples:
        my_lambda = lambda: "ABC" in person.handle
        result = lambda_to_string(my_lambda)
        # Returns: '"ABC" in person.handle'

        my_lambda = lambda: person.handle == 'A6E74B3D65D23F'
        result = lambda_to_string(my_lambda)
        # Returns: "person.handle == 'A6E74B3D65D23F'"

    Note:
        This function only handles simple expressions needed for database select
        operations. Complex constructs like comprehensions, generators, dict/set
        literals, and control flow are not supported.
    """
    if not isinstance(lambda_func, types.LambdaType):
        raise TypeError(f"Expected lambda function, got {type(lambda_func)}")

    full_result = _decompile_lambda(lambda_func)
    # Remove "lambda: " prefix to return only the body
    if full_result.startswith("lambda: "):
        return full_result[8:]  # Remove "lambda: " (8 characters)
    elif full_result.startswith("lambda "):
        # Handle case with arguments (shouldn't happen, but be safe)
        idx = full_result.find(": ")
        if idx != -1:
            return full_result[idx + 2 :]  # Remove "lambda ...: " prefix
    return full_result


def _decompile_lambda(lambda_func):
    """
    Decompile a lambda function object to source code using bytecode analysis.

    This function uses the dis module to analyze bytecode and reconstruct
    the lambda expression. Works reliably for Python 3.10+.

    Args:
        lambda_func: A lambda function object

    Returns:
        String representation of the lambda
    """
    if not isinstance(lambda_func, types.LambdaType):
        raise TypeError(f"Expected lambda function, got {type(lambda_func)}")

    code = lambda_func.__code__

    # Get the code object's bytecode
    instructions = list(dis.get_instructions(code))

    # Reconstruct the lambda expression from bytecode
    # This is a simplified approach - for full decompilation, you'd need
    # a more sophisticated bytecode analyzer

    # For Python 3.10+, we can use marshal to get the code object
    # and then use dis to analyze it

    # Extract argument names
    arg_names = code.co_varnames[: code.co_argcount]
    args_str = ", ".join(arg_names)

    # Try to reconstruct the body from bytecode
    # This is complex - we'll use a bytecode-to-AST approach
    body_str = _bytecode_to_expression(instructions, code)

    if args_str:
        return f"lambda {args_str}: {body_str}"
    else:
        return f"lambda: {body_str}"


def _bytecode_to_expression(instructions, code):
    """
    Convert bytecode instructions to a Python expression string.

    Handles simple expressions: comparisons, logical operations, attribute access,
    function calls, subscripts, and nested operations. Works for Python 3.10+.
    Uses a recursive approach to handle control flow for logical operations.
    """
    # Filter out RESUME instruction (Python 3.11+)
    instructions = [instr for instr in instructions if instr.opname != "RESUME"]

    # Build offset map for jumps
    offset_map = {instr.offset: i for i, instr in enumerate(instructions)}

    # Process recursively starting from the beginning
    result, _ = _process_instructions(
        instructions, 0, len(instructions), offset_map, code
    )
    return result


def _process_instructions(instructions, start_idx, end_idx, offset_map, code):
    """
    Recursively process bytecode instructions to build an expression.

    Returns:
        (expression_string, next_index) - the expression and the index after processing
    """
    stack = []
    locals_map = {i: name for i, name in enumerate(code.co_varnames)}
    constants = code.co_consts
    names = code.co_names

    i = start_idx
    while i < end_idx:
        instr = instructions[i]
        opname = instr.opname
        arg = instr.arg

        if opname == "LOAD_CONST":
            stack.append(repr(constants[arg]))
        elif opname == "LOAD_FAST":
            stack.append(locals_map[arg])
        elif opname == "LOAD_GLOBAL":
            if hasattr(instr, "argval") and instr.argval is not None:
                stack.append(str(instr.argval))
            elif arg < len(names):
                stack.append(names[arg])
            else:
                stack.append(f"<global{arg}>")
        elif opname == "LOAD_ATTR":
            obj = stack.pop()
            if hasattr(instr, "argval") and instr.argval is not None:
                attr_name = str(instr.argval)
            elif arg < len(names):
                attr_name = names[arg]
            else:
                attr_name = f"<attr{arg}>"
            stack.append(f"{obj}.{attr_name}")
        elif opname == "LOAD_METHOD":
            obj = stack.pop()
            if hasattr(instr, "argval") and instr.argval is not None:
                method_name = str(instr.argval)
            elif arg < len(names):
                method_name = names[arg]
            else:
                method_name = f"<method{arg}>"
            stack.append(f"{obj}.{method_name}")
        elif opname == "COMPARE_OP":
            right = stack.pop()
            left = stack.pop()
            if hasattr(instr, "argval") and instr.argval is not None:
                op = str(instr.argval)
            else:
                compare_ops = {
                    0: "<",
                    1: "<=",
                    2: "==",
                    3: "!=",
                    4: ">",
                    5: ">=",
                    6: "in",
                    7: "not in",
                    8: "is",
                    9: "is not",
                    10: "exception match",
                    11: "BAD",
                }
                op = compare_ops.get(arg, "?")
            stack.append(f"{left} {op} {right}")
        elif opname == "CONTAINS_OP":
            right = stack.pop()
            left = stack.pop()
            if arg == 0:
                stack.append(f"{left} in {right}")
            elif arg == 1:
                stack.append(f"{left} not in {right}")
            else:
                stack.append(f"{left} in {right}")
        elif opname == "IS_OP":
            right = stack.pop()
            left = stack.pop()
            if arg == 0:
                stack.append(f"{left} is {right}")
            elif arg == 1:
                stack.append(f"{left} is not {right}")
            else:
                stack.append(f"{left} is {right}")
        elif opname == "BINARY_OP":
            right = stack.pop()
            left = stack.pop()
            # For Python 3.10+, argval is a number representing the operation
            # Use argval if available, otherwise use arg
            op_code = (
                instr.argval
                if hasattr(instr, "argval") and instr.argval is not None
                else arg
            )
            binary_ops = {
                0: "+",
                1: "-",
                2: "//",
                3: "/",
                4: "%",
                5: "*",
                6: "%",
                7: ">>",
                8: "**",
                9: "^",
                10: "-",
                11: "/",
                12: "@",
                13: "<<",
                14: "&",
                15: "|",
            }
            op = binary_ops.get(op_code, "?")
            stack.append(f"({left} {op} {right})")
        elif opname == "COPY":
            # Duplicate top of stack (used before POP_JUMP for logical ops)
            if stack:
                stack.append(stack[-1])
        elif opname == "POP_JUMP_IF_FALSE":
            # Pattern for 'and': COPY, POP_JUMP_IF_FALSE <target>, POP_TOP, <right>
            # The left side is already on the stack (duplicated by COPY)
            left = stack.pop()  # Remove duplicate
            jump_target = instr.argval if hasattr(instr, "argval") else arg
            target_idx = offset_map.get(jump_target, end_idx)

            # Skip POP_TOP
            if i + 1 < len(instructions) and instructions[i + 1].opname == "POP_TOP":
                i += 1

            # Recursively process the right side (from next instruction to jump target)
            right, _ = _process_instructions(
                instructions, i + 1, target_idx, offset_map, code
            )
            stack.append(f"({left} and {right})")

            # Skip to the target (right side has been processed)
            i = target_idx - 1  # Will be incremented at end of loop
        elif opname == "POP_JUMP_IF_TRUE":
            # Pattern for 'or': COPY, POP_JUMP_IF_TRUE <target>, POP_TOP, <right>
            left = stack.pop()  # Remove duplicate
            jump_target = instr.argval if hasattr(instr, "argval") else arg
            target_idx = offset_map.get(jump_target, end_idx)

            # Skip POP_TOP
            if i + 1 < len(instructions) and instructions[i + 1].opname == "POP_TOP":
                i += 1

            # Recursively process the right side
            right, _ = _process_instructions(
                instructions, i + 1, target_idx, offset_map, code
            )
            stack.append(f"({left} or {right})")

            # Skip to the target
            i = target_idx - 1
        elif opname == "POP_TOP":
            # Discard top of stack
            if stack:
                stack.pop()
        elif opname == "UNARY_NOT":
            stack.append(f"not {stack.pop()}")
        elif opname == "UNARY_NEGATIVE":
            stack.append(f"-{stack.pop()}")
        elif opname == "UNARY_POSITIVE":
            stack.append(f"+{stack.pop()}")
        elif opname == "CALL":
            nargs = arg
            args = []
            for _ in range(nargs):
                args.insert(0, stack.pop())
            func = stack.pop()
            stack.append(f"{func}({', '.join(args)})")
        elif opname == "BINARY_SUBSCR":
            index = stack.pop()
            obj = stack.pop()
            stack.append(f"{obj}[{index}]")
        elif opname == "RETURN_CONST":
            # Python 3.11+ uses RETURN_CONST for simple constants
            if hasattr(instr, "argval") and instr.argval is not None:
                stack.append(repr(instr.argval))
            else:
                stack.append(repr(constants[arg]))
            # This is the end
            break
        elif opname == "RETURN_VALUE":
            # End of expression
            break
        elif opname == "EXTENDED_ARG":
            # Extended argument - just continue
            pass
        else:
            # Unknown instruction - skip it
            pass

        i += 1

    # Return the expression on the stack and the next index
    if stack:
        return stack[-1], i
    else:
        raise NotImplementedError(
            f"Could not decompile bytecode. Stack empty at index {i}."
        )

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
import sys
import types

# Python version detection for bytecode differences
# TODO: Remove version-specific code as minimum Python version increases
# - Python 3.10: Uses JUMP_IF_FALSE_OR_POP, JUMP_IF_TRUE_OR_POP, specific binary ops
# - Python 3.11: Uses POP_JUMP_FORWARD_IF_FALSE, BINARY_OP, CALL
# - Python 3.12+: Uses COPY + POP_JUMP_IF_FALSE + POP_TOP pattern
# - Python 3.13+: Adds TO_BOOL instruction
PYTHON_VERSION = sys.version_info[:2]  # (major, minor)
PYTHON_310 = PYTHON_VERSION == (3, 10)
PYTHON_311 = PYTHON_VERSION == (3, 11)
PYTHON_312_PLUS = PYTHON_VERSION >= (3, 12)


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


def _resolve_jump_target(instr_or_target, instructions, offset_map):
    """
    Resolve a jump target to an instruction index.

    Args:
        instr_or_target: Either a jump instruction object, or a jump target offset (int)
        instructions: List of all instructions
        offset_map: Map from instruction offsets to indices

    Returns:
        The index of the target instruction, or len(instructions) if not found
    """
    # Get jump target - handle both instruction objects and direct offsets
    if isinstance(instr_or_target, int):
        jump_target = instr_or_target
    elif hasattr(instr_or_target, "argval") and instr_or_target.argval is not None:
        jump_target = instr_or_target.argval
    else:
        # For relative jumps, calculate absolute offset
        jump_target = instr_or_target.offset + instr_or_target.arg

    # Look up the target in the offset map
    target_idx = offset_map.get(jump_target)
    if target_idx is not None:
        return target_idx

    # If not found in offset_map, search for the instruction with that offset
    for j, check_instr in enumerate(instructions):
        if check_instr.offset == jump_target:
            return j

    # Still not found - try to find the closest instruction with offset >= jump_target
    for j, check_instr in enumerate(instructions):
        if check_instr.offset >= jump_target:
            return j

    # Last resort: use end of instructions
    return len(instructions)


def _check_python_312_copy_pattern(instructions, i):
    """
    Check if the instruction at index i is part of a Python 3.12+ COPY pattern.

    Pattern: COPY, [TO_BOOL], POP_JUMP_IF_FALSE/POP_JUMP_IF_TRUE, POP_TOP

    Args:
        instructions: List of all instructions
        i: Index of the POP_JUMP instruction

    Returns:
        True if this is a Python 3.12+ COPY pattern, False otherwise
    """
    if not PYTHON_312_PLUS:
        return False

    # Check if previous instruction was COPY or TO_BOOL
    if i > 0 and instructions[i - 1].opname in ("COPY", "TO_BOOL"):
        # Look further back for COPY
        check_idx = i - 1
        if instructions[check_idx].opname == "TO_BOOL" and check_idx > 0:
            check_idx = check_idx - 1
        if check_idx >= 0 and instructions[check_idx].opname == "COPY":
            return True

    return False


def _find_and_end_idx(instructions, start_idx, end_idx):
    """
    Find where an 'and' operation ends when there's an 'or' operation after it.

    Args:
        instructions: List of all instructions
        start_idx: Start index to search from
        end_idx: End index to search up to

    Returns:
        The index where the 'and' ends (where 'or' starts), or end_idx if no 'or' found
    """
    # In Python 3.12+, 'or' starts with COPY followed by [TO_BOOL] and POP_JUMP_IF_TRUE
    # In Python 3.10/3.11, 'or' uses JUMP_IF_TRUE_OR_POP or POP_JUMP_IF_TRUE
    for j in range(start_idx, min(end_idx, len(instructions))):
        opname = instructions[j].opname
        if opname in ("JUMP_IF_TRUE_OR_POP", "POP_JUMP_IF_TRUE"):
            return j  # The 'and' ends here
        # In Python 3.12+, look for COPY followed by [TO_BOOL] and POP_JUMP_IF_TRUE
        if PYTHON_312_PLUS and opname == "COPY":
            check_idx = j + 1
            # Skip TO_BOOL if present (Python 3.13+)
            if (
                check_idx < len(instructions)
                and instructions[check_idx].opname == "TO_BOOL"
            ):
                check_idx += 1
            # Check if next instruction is POP_JUMP_IF_TRUE
            if (
                check_idx < len(instructions)
                and instructions[check_idx].opname == "POP_JUMP_IF_TRUE"
            ):
                return j  # The 'and' ends at the COPY (start of 'or')
    return end_idx


def _handle_binary_operation(stack, opname, op_symbol):
    """
    Handle a binary operation by popping two operands and pushing the result.

    Args:
        stack: The evaluation stack
        opname: Name of the operation (for error messages)
        op_symbol: Symbol to use in the expression (e.g., "+", "-")
    """
    right = stack.pop()
    left = stack.pop()
    stack.append(f"({left} {op_symbol} {right})")


def _find_return_value(instructions, start_idx):
    """
    Find the RETURN_VALUE instruction after start_idx.

    Args:
        instructions: List of all instructions
        start_idx: Start index to search from

    Returns:
        The index of RETURN_VALUE, or len(instructions) if not found
    """
    for j in range(start_idx, len(instructions)):
        if instructions[j].opname == "RETURN_VALUE":
            return j
    return len(instructions)


def _handle_pop_jump_if_false_python_312_plus(instructions, i, stack, offset_map, code):
    """
    Handle POP_JUMP_IF_FALSE for Python 3.12+ with COPY pattern.

    Pattern: COPY, [TO_BOOL], POP_JUMP_IF_FALSE, POP_TOP, <right side>, RETURN_VALUE

    Returns:
        (new_i, should_continue) - new instruction index and whether to continue loop
    """
    instr = instructions[i]
    next_idx = i + 1

    # Pop left operand (COPY duplicated it, so we have [x, x])
    if len(stack) >= 2:
        left = stack.pop()  # Pop the duplicate for left side
    else:
        left = stack.pop()

    # Resolve jump target
    target_idx = _resolve_jump_target(instr, instructions, offset_map)

    # Skip TO_BOOL and POP_TOP if present
    if next_idx < len(instructions) and instructions[next_idx].opname == "TO_BOOL":
        next_idx += 1
    if next_idx < len(instructions) and instructions[next_idx].opname == "POP_TOP":
        next_idx += 1

    # Check if target_idx itself is a COPY that starts an 'or' operation (Python 3.12+)
    # In 'x and y or z', the 'and' jumps to the COPY that starts the 'or'
    # In 'A and (B or C)', the 'and' jumps to RETURN_VALUE, and 'or' is nested before that
    is_or_at_target = False
    or_jump_target = None
    and_end_idx = None
    if target_idx < len(instructions) and instructions[target_idx].opname == "COPY":
        # Check if this COPY starts an 'or' operation
        check_idx = target_idx + 1
        if (
            check_idx < len(instructions)
            and instructions[check_idx].opname == "TO_BOOL"
        ):
            check_idx += 1
        if (
            check_idx < len(instructions)
            and instructions[check_idx].opname == "POP_JUMP_IF_TRUE"
        ):
            is_or_at_target = True
            and_end_idx = target_idx
            # Get the 'or' operation's jump target
            or_instr = instructions[check_idx]
            or_jump_target = _resolve_jump_target(or_instr, instructions, offset_map)

    if not is_or_at_target:
        # Check if there's an 'or' operation after the 'and' (not at target)
        and_end_idx = _find_and_end_idx(instructions, next_idx, target_idx + 1)
        if and_end_idx < target_idx and and_end_idx + 1 < len(instructions):
            # Get the 'or' operation's jump target
            or_instr = instructions[and_end_idx]
            if or_instr.opname == "COPY" and and_end_idx + 1 < len(instructions):
                # Skip TO_BOOL if present
                check_or_idx = and_end_idx + 1
                if (
                    check_or_idx < len(instructions)
                    and instructions[check_or_idx].opname == "TO_BOOL"
                ):
                    check_or_idx += 1
                if check_or_idx < len(instructions):
                    or_instr = instructions[check_or_idx]
            if or_instr.opname in ("POP_JUMP_IF_TRUE", "JUMP_IF_TRUE_OR_POP"):
                or_jump_target = _resolve_jump_target(
                    or_instr, instructions, offset_map
                )

    # Determine if 'or' is nested or sequential:
    # - In 'A and (B or C)': 'and' jumps to RETURN_VALUE, 'or' jumps to RETURN_VALUE -> nested
    # - In 'A and B or C': 'and' jumps to COPY (start of 'or'), 'or' jumps to RETURN_VALUE -> sequential
    return_value_idx = _find_return_value(instructions, target_idx)

    # Check if 'or' is nested: both 'and' and 'or' must jump to the same RETURN_VALUE
    is_nested = False
    if or_jump_target is not None:
        # If both jump to RETURN_VALUE, it's nested; otherwise sequential
        is_nested = (
            target_idx == return_value_idx and or_jump_target == return_value_idx
        )

    if is_nested:
        # 'or' is nested - process it as part of 'and' right side
        actual_end = _find_return_value(instructions, next_idx)
        if actual_end <= next_idx:
            actual_end = _find_return_value(instructions, next_idx + 1)
            if actual_end <= next_idx:
                actual_end = min(next_idx + 1, len(instructions))
        if next_idx < actual_end:
            right, _ = _process_instructions(
                instructions, next_idx, actual_end, offset_map, code
            )
            stack.append(f"({left} and {right})")
            return (actual_end - 1, True)
    elif is_or_at_target or (and_end_idx is not None and and_end_idx < target_idx):
        # There's an 'or' operation after the 'and' (not nested)
        right, _ = _process_instructions(
            instructions, next_idx, and_end_idx, offset_map, code
        )
        stack.append(f"({left} and {right})")
        return (and_end_idx - 1, True)  # Will process 'or' next

    # No 'or' operation - process up to RETURN_VALUE
    actual_end = _find_return_value(instructions, next_idx)

    # Ensure we process at least one instruction
    if actual_end <= next_idx:
        # Search from next_idx + 1
        actual_end = _find_return_value(instructions, next_idx + 1)
        if actual_end <= next_idx:
            actual_end = min(next_idx + 1, len(instructions))

    # Process the right side
    if next_idx < actual_end:
        right, _ = _process_instructions(
            instructions, next_idx, actual_end, offset_map, code
        )
        stack.append(f"({left} and {right})")
        return (actual_end - 1, True)
    else:
        # Edge case: process one instruction manually
        if next_idx < len(instructions):
            right, _ = _process_instructions(
                instructions, next_idx, next_idx + 1, offset_map, code
            )
            stack.append(f"({left} and {right})")
            return (next_idx, True)
        else:
            stack.append(left)
            return (target_idx - 1, True)


def _handle_pop_jump_if_false_python_310_311(instructions, i, stack, offset_map, code):
    """
    Handle POP_JUMP_IF_FALSE for Python 3.10/3.11.

    Returns:
        (new_i, should_continue) - new instruction index and whether to continue loop
    """
    instr = instructions[i]
    next_idx = i + 1

    # Pop left operand
    left = stack.pop()

    # Resolve jump target
    target_idx = _resolve_jump_target(instr, instructions, offset_map)

    # Check if there's an 'or' operation after the 'and'
    and_end_idx = _find_and_end_idx(instructions, next_idx, target_idx)

    if and_end_idx < target_idx:
        # There's an 'or' operation after the 'and'
        right, _ = _process_instructions(
            instructions, next_idx, and_end_idx, offset_map, code
        )
        stack.append(f"({left} and {right})")
        return (and_end_idx - 1, True)  # Will process 'or' next
    elif next_idx < target_idx:
        # Normal case: process up to target_idx
        right, _ = _process_instructions(
            instructions, next_idx, target_idx, offset_map, code
        )
        stack.append(f"({left} and {right})")
        return (target_idx - 1, True)
    else:
        # Edge case: next_idx >= target_idx
        if next_idx < len(instructions):
            right, _ = _process_instructions(
                instructions, next_idx, len(instructions), offset_map, code
            )
            stack.append(f"({left} and {right})")
            return (len(instructions) - 1, True)
        else:
            stack.append(left)
            return (target_idx - 1, True)


def _bytecode_to_expression(instructions, code):
    """
    Convert bytecode instructions to a Python expression string.

    Handles simple expressions: comparisons, logical operations, attribute access,
    function calls, subscripts, and nested operations. Works for Python 3.10+.
    Uses a recursive approach to handle control flow for logical operations.
    """
    # Filter out RESUME instruction (Python 3.11+)
    instructions = [instr for instr in instructions if instr.opname != "RESUME"]

    # Build offset map for jumps - map instruction offsets to their indices
    # This is used to resolve jump targets
    offset_map = {instr.offset: i for i, instr in enumerate(instructions)}

    # Also build a reverse map for debugging (index to offset)
    # This helps ensure we can always find targets

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
    # Process instructions up to (but not including) end_idx
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
            # Python 3.11+ uses BINARY_OP with opcode
            right = stack.pop()
            left = stack.pop()
            op_code = (
                instr.argval
                if hasattr(instr, "argval") and instr.argval is not None
                else arg
            )
            # Only arithmetic operations, not bitwise
            # Opcode mapping from Python 3.11+ dis module
            binary_ops = {
                0: "+",  # Addition
                2: "//",  # Floor division
                5: "*",  # Multiplication
                6: "%",  # Modulo
                8: "**",  # Exponentiation
                10: "-",  # Subtraction
                11: "/",  # True division
            }
            op = binary_ops.get(op_code, "?")
            stack.append(f"({left} {op} {right})")
        elif opname == "BINARY_ADD":
            _handle_binary_operation(stack, opname, "+")
        elif opname == "BINARY_SUBTRACT":
            _handle_binary_operation(stack, opname, "-")
        elif opname == "BINARY_MULTIPLY":
            _handle_binary_operation(stack, opname, "*")
        elif opname == "BINARY_DIVIDE":
            _handle_binary_operation(stack, opname, "/")
        elif opname == "BINARY_FLOOR_DIVIDE":
            _handle_binary_operation(stack, opname, "//")
        elif opname == "BINARY_TRUE_DIVIDE":
            _handle_binary_operation(stack, opname, "/")
        elif opname == "BINARY_MODULO":
            _handle_binary_operation(stack, opname, "%")
        elif opname == "BINARY_POWER":
            _handle_binary_operation(stack, opname, "**")
        elif opname == "COPY":
            # Duplicate top of stack (used before POP_JUMP for logical ops)
            # Python 3.12+: COPY, POP_JUMP_IF_FALSE, POP_TOP
            # Python 3.13+: COPY, TO_BOOL, POP_JUMP_IF_FALSE, POP_TOP
            if stack:
                stack.append(stack[-1])
        elif opname == "TO_BOOL":
            # Python 3.13+: Convert value to boolean (used in logical operations)
            # This doesn't change the stack structure for our purposes
            # Just continue - the value remains on the stack
            pass
        elif opname == "POP_JUMP_IF_FALSE":
            # Pattern for 'and': POP_JUMP_IF_FALSE <target>
            # Python 3.10: Pops the value, if false jumps to target, else continues
            # Python 3.12+: COPY, POP_JUMP_IF_FALSE, POP_TOP pattern
            # Python 3.13+: COPY, TO_BOOL, POP_JUMP_IF_FALSE, POP_TOP pattern
            is_python_312_plus_copy = _check_python_312_copy_pattern(instructions, i)

            if is_python_312_plus_copy:
                i, _ = _handle_pop_jump_if_false_python_312_plus(
                    instructions, i, stack, offset_map, code
                )
            else:
                i, _ = _handle_pop_jump_if_false_python_310_311(
                    instructions, i, stack, offset_map, code
                )
        elif opname == "POP_JUMP_IF_TRUE":
            # Pattern for 'or': POP_JUMP_IF_TRUE <target>
            # Python 3.12+: COPY, POP_JUMP_IF_TRUE, POP_TOP pattern
            # Check if previous instruction was COPY (Python 3.12+ pattern)
            if i > 0 and instructions[i - 1].opname == "COPY":
                # Python 3.12+ pattern: COPY duplicated the value, now we pop the duplicate
                left = stack.pop()  # Remove duplicate, keep original
            else:
                # Shouldn't happen in Python 3.12+, but handle it
                left = stack.pop()

            target_idx = _resolve_jump_target(instr, instructions, offset_map)

            # Skip POP_TOP if present (Python 3.12+)
            next_idx = i + 1
            if (
                next_idx < len(instructions)
                and instructions[next_idx].opname == "POP_TOP"
            ):
                next_idx += 1

            # Recursively process the right side
            right, _ = _process_instructions(
                instructions, next_idx, target_idx, offset_map, code
            )
            stack.append(f"({left} or {right})")

            # Skip to the target
            i = target_idx - 1
        elif opname == "POP_JUMP_FORWARD_IF_FALSE":
            # Python 3.11 pattern for 'and': POP_JUMP_FORWARD_IF_FALSE <delta>
            # Jumps forward by delta if false, otherwise continues
            left = stack.pop()
            # Calculate target offset (current offset + delta)
            current_offset = instr.offset
            jump_delta = (
                instr.argval
                if (hasattr(instr, "argval") and instr.argval is not None)
                else arg
            )
            target_offset = current_offset + jump_delta
            target_idx = _resolve_jump_target(target_offset, instructions, offset_map)

            next_idx = i + 1

            # Check if there's a JUMP_IF_TRUE_OR_POP in the range (part of an 'or' operation)
            and_end_idx = _find_and_end_idx(instructions, next_idx, target_idx)

            if and_end_idx < target_idx:
                # There's an 'or' operation after the 'and'
                right, _ = _process_instructions(
                    instructions, next_idx, and_end_idx, offset_map, code
                )
                stack.append(f"({left} and {right})")
                i = and_end_idx - 1  # Will process 'or' next
            else:
                # Normal case: process the right side up to the jump target
                right, _ = _process_instructions(
                    instructions, next_idx, target_idx, offset_map, code
                )
                stack.append(f"({left} and {right})")
                i = target_idx - 1
        elif opname == "JUMP_IF_FALSE_OR_POP":
            # Python 3.10 pattern for 'and': JUMP_IF_FALSE_OR_POP <target>
            # If false, jump to target (short-circuit), otherwise pop and continue
            left = stack.pop()
            jump_target = (
                instr.argval
                if (hasattr(instr, "argval") and instr.argval is not None)
                else instr.offset + instr.arg
            )
            target_idx = _resolve_jump_target(jump_target, instructions, offset_map)

            # Process the right side (from next instruction to jump target)
            right, _ = _process_instructions(
                instructions, i + 1, target_idx, offset_map, code
            )
            stack.append(f"({left} and {right})")

            # Skip to the target (right side has been processed)
            i = target_idx - 1
        elif opname == "JUMP_IF_TRUE_OR_POP":
            # Python 3.10 pattern for 'or': JUMP_IF_TRUE_OR_POP <target>
            # If true, jump to target (short-circuit), otherwise pop and continue
            left = stack.pop()
            jump_target = (
                instr.argval
                if (hasattr(instr, "argval") and instr.argval is not None)
                else instr.offset + instr.arg
            )
            target_idx = _resolve_jump_target(jump_target, instructions, offset_map)

            # Process the right side (from next instruction to target)
            next_idx = i + 1
            right, _ = _process_instructions(
                instructions, next_idx, target_idx, offset_map, code
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
            # Python 3.11+ uses CALL
            nargs = arg
            args = []
            for _ in range(nargs):
                args.insert(0, stack.pop())
            func = stack.pop()
            stack.append(f"{func}({', '.join(args)})")
        elif opname == "CALL_FUNCTION":
            # Python 3.10 uses CALL_FUNCTION
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

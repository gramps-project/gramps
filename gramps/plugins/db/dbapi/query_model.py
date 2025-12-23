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

"""
Query Model Classes

Intermediate representation of SQL queries as objects, similar to an ORM.
This separates parsing from SQL generation, eliminating edge cases.
"""

from typing import List, Optional, Union
from dataclasses import dataclass, field


# ============================================================================
# Expression Base Classes
# ============================================================================


class Expression:
    """Base class for all expressions in the query model."""

    pass


@dataclass
class ConstantExpression(Expression):
    """Represents a constant value (string, number, None, etc.)."""

    value: Union[str, int, float, bool, None]

    def __repr__(self):
        return f"Constant({self.value!r})"


@dataclass
class AttributeExpression(Expression):
    """Represents attribute access like person.handle or person.primary_name.surname.

    Can represent:
    - Direct attribute: table_name="person", attribute_path="handle", base=None
    - Nested attribute: base=ArrayAccessExpression(...), attribute_path="role.value"
    """

    table_name: str  # Base table name (e.g., "person") - used when base is None
    attribute_path: str  # Dot-separated path (e.g., "handle" or "primary_name.surname")
    is_database_column: bool = False  # True if this is a DB column, not JSON field
    base: Optional[Expression] = (
        None  # Optional base expression (e.g., ArrayAccessExpression)
    )
    # When base is provided, table_name is used for context but base expression is evaluated first

    def __repr__(self):
        if self.base:
            return f"Attribute({self.base}.{self.attribute_path})"
        return f"Attribute({self.table_name}.{self.attribute_path})"


@dataclass
class ArrayAccessExpression(Expression):
    """Represents array access like person.event_ref_list[0] or person.array[index]."""

    base: Expression  # The array expression
    index: Expression  # Index expression (can be constant or variable)
    is_constant_index: bool  # True if index is a constant

    def __repr__(self):
        return f"ArrayAccess({self.base}[{self.index}])"


@dataclass
class BinaryOpExpression(Expression):
    """Represents binary operations like +, -, *, /, %, etc."""

    operator: str  # "+", "-", "*", "/", "%", "**", "//"
    left: Expression
    right: Expression

    def __repr__(self):
        return f"BinaryOp({self.left} {self.operator} {self.right})"


@dataclass
class UnaryOpExpression(Expression):
    """Represents unary operations like -x or not x."""

    operator: str  # "-", "not"
    operand: Expression

    def __repr__(self):
        return f"UnaryOp({self.operator} {self.operand})"


@dataclass
class CompareExpression(Expression):
    """Represents comparison operations like ==, !=, <, >, <=, >=, in, not in, is, is not."""

    left: Expression
    operators: List[str]  # Can have multiple (e.g., "a < b < c")
    comparators: List[Expression]

    def __repr__(self):
        ops_str = " ".join(self.operators)
        return f"Compare({self.left} {ops_str} {self.comparators})"


@dataclass
class BoolOpExpression(Expression):
    """Represents boolean operations like and, or."""

    operator: str  # "and" or "or"
    values: List[Expression]

    def __repr__(self):
        return f"BoolOp({self.operator}, {len(self.values)} values)"


@dataclass
class CallExpression(Expression):
    """Represents function calls like len(array) or attribute.startswith('x')."""

    function: Expression  # Can be AttributeExpression for methods
    arguments: List[Expression]

    def __repr__(self):
        return f"Call({self.function}({len(self.arguments)} args))"


@dataclass
class IfExpression(Expression):
    """Represents ternary expressions like x if condition else y."""

    test: Expression
    body: Expression
    orelse: Expression

    def __repr__(self):
        return f"If({self.test} ? {self.body} : {self.orelse})"


@dataclass
class ListComprehensionExpression(Expression):
    """Represents list comprehensions like [x.field for x in array if condition]."""

    expression: Expression  # What to extract
    item_var: str  # Iteration variable name
    array_info: dict  # {'type': 'single'/'concatenated', 'path': str, etc.}
    condition: Optional[Expression] = None  # Optional filter condition

    def __repr__(self):
        return f"ListComp({self.item_var} in {self.array_info})"


@dataclass
class AnyExpression(Expression):
    """Represents any() patterns like any([x.field for x in array if condition])."""

    item_var: str
    array_path: str
    array_info: Optional[dict] = None  # Full array info for concatenated arrays
    condition: Optional[Expression] = None

    def __repr__(self):
        return f"Any({self.item_var} in {self.array_path})"


@dataclass
class ArrayExpansionExpression(Expression):
    """Represents array expansion patterns like 'item in person.array'."""

    item_var: str
    array_path: str
    array_expression: Expression  # The array being iterated

    def __repr__(self):
        return f"ArrayExpansion({self.item_var} in {self.array_path})"


@dataclass
class TupleExpression(Expression):
    """Represents tuples like (x, y, z)."""

    elements: List[Expression]

    def __repr__(self):
        return f"Tuple({len(self.elements)} elements)"


# ============================================================================
# Query Structure Classes
# ============================================================================


@dataclass
class SelectExpression:
    """Represents a single SELECT expression."""

    expression: Expression
    alias: Optional[str] = None

    def __repr__(self):
        if self.alias:
            return f"Select({self.expression} AS {self.alias})"
        return f"Select({self.expression})"


@dataclass
class Join:
    """Represents a JOIN clause."""

    table_name: str
    join_type: str  # "INNER", "LEFT", "RIGHT", etc.
    condition: Expression  # Equality expression between handles

    def __repr__(self):
        return f"Join({self.join_type} {self.table_name} ON {self.condition})"


@dataclass
class OrderBy:
    """Represents an ORDER BY clause."""

    expression: Expression
    direction: str  # "ASC" or "DESC"

    def __repr__(self):
        return f"OrderBy({self.expression} {self.direction})"


@dataclass
class ArrayExpansion:
    """Represents array expansion context for FROM clause."""

    item_var: str
    array_path: str
    array_expression: Expression

    def __repr__(self):
        return f"ArrayExpansion({self.item_var} in {self.array_path})"


@dataclass
class SelectQuery:
    """Main query container representing a SELECT statement."""

    base_table: str
    select_expressions: List[SelectExpression] = field(default_factory=list)
    where_condition: Optional[Expression] = None
    joins: List[Join] = field(default_factory=list)
    order_by: List[OrderBy] = field(default_factory=list)
    limit: Optional[int] = None
    offset: Optional[int] = None
    array_expansion: Optional[ArrayExpansion] = None  # For array expansion in WHERE
    union_queries: List["SelectQuery"] = field(
        default_factory=list
    )  # For UNION queries

    def __repr__(self):
        parts = [f"SELECT {len(self.select_expressions)} expressions"]
        parts.append(f"FROM {self.base_table}")
        if self.joins:
            parts.append(f"{len(self.joins)} joins")
        if self.where_condition:
            parts.append("WHERE ...")
        if self.order_by:
            parts.append(f"ORDER BY {len(self.order_by)}")
        if self.union_queries:
            parts.append(f"UNION {len(self.union_queries)} queries")
        return " ".join(parts)

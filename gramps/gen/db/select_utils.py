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

"""
Support functions for Generic DB select functionality
"""

import re
import jsonpath_ng

PARSE_CACHE = {}


def select(db, table, selections, where, sort_by, page, page_size):
    """
    Top-level function for select functions.

    Args:
        db: database instance
        table: the table name
        selections: list of jsonpaths
        where: a where expression
        sort_by: list of jsonpaths to sort by
    """
    selections = selections if selections else ["$"]
    if page_size is None:
        limit = float("+inf")
        offset = 0
    else:
        offset = page * page_size
        limit = page_size

    if sort_by is None:
        for count, row in enumerate(select_items(db, table, selections, where)):
            if count < offset:
                continue
            if count > (offset + limit):
                break
            yield row
    else:
        results = list(select_items(db, table, ["$"], where))
        for count, row in enumerate(
            sorted(results, key=lambda item: sort_function(item, sort_by))
        ):
            if count < offset:
                continue
            if count > (offset + limit):
                break
            yield get_items(row, selections)


def select_items(db, table, selections, where):
    """
    Select items with optional where expr.

    Note that we apply the where, then select the items.
    """
    for row in select_where(db, table, where):
        results = get_items(row, selections)
        yield results


def select_where(db, table, where):
    """
    Select items in the table where an expression
    is True.

    We don't always want to scan the entire database
    if we don't have to. So we chech for all exact
    matches on what we can select on directly using
    handle and gramps_id lookup methods.
    """
    if where:
        indexed_expressions = []
        get_indexed_fields(where, indexed_expressions)
        if indexed_expressions:
            handles_returned = []
            for indexed in indexed_expressions:
                index_field, compare, index_value = indexed
                if index_field == "$.gramps_id":
                    func_name = "raw_id_func"
                elif index_field == "$.handle":
                    func_name = "raw_func"
                else:
                    raise Exception("index must be handle or gramps_id")

                row = db._get_table_func(table.title(), func_name)(index_value)
                if match_where(row, where):
                    # Don't return the same row more than once:
                    if row["handle"] not in handles_returned:
                        handles_returned.append(row["handle"])
                        yield row
            return

    # Otherwise, we have to scan the whole table:
    iter_func = db._get_table_func(table.title(), "cursor_func")
    for row in iter_func():
        if where:
            if match_where(row[1], where):
                yield row[1]
        else:
            yield row[1]


def sort_function(item, sort_by):
    """
    Given a list of jsonpaths, return a
    tuple of associated values for sorting.
    """
    results = get_items(item, sort_by)
    return tuple(results.values())


def get_items(row, selections):
    """
    Given a list of jsonpaths, get the
    items from the row.
    """
    results = {}
    for json_path in selections:
        if json_path == "$":
            results = row
        else:
            match = match_json_path(json_path, row)
            if match:
                # Remove jsonpath syntax:
                results[json_path[2:]] = match[0].value
    return results


def match_json_path(json_path, row):
    """
    Return the matching json_path item if the given
    json_path matches.
    """
    if json_path not in PARSE_CACHE:
        PARSE_CACHE[json_path] = jsonpath_ng.parse(json_path)
    jsonpath_expr = PARSE_CACHE[json_path]
    match = jsonpath_expr.find(row)
    return match


def eval_expr(expr, data):
    """
    Evaluate the expr. If the expr is a jsonpath,
    then get the matching value, else all
    other values are assumed to be self-evaluating.
    """
    if isinstance(expr, str) and expr.startswith("$"):
        match = match_json_path(expr, data)
        if match:
            return match[0].value
        else:
            return None

    return expr


def match_where(data, where):
    """
    Assumes all comparisons are using jsonpath
    ("$.gender", "=", value)
    """
    if len(where) == 3:
        lhs = eval_expr(where[0], data)
        op = where[1].lower()
        rhs = eval_expr(where[2], data)
        return compare_where(lhs, op, rhs)
    elif where[0].lower() == "and":
        for expr in where[1]:
            result = match_where(data, expr)
            if not result:
                return False
        return True
    elif where[0].lower() == "or":
        for expr in where[1]:
            result = match_where(data, expr)
            if result:
                return True
        return False
    else:
        raise Exception("Malformed where expression: %r" % where)


def compare_where(lhs, op, rhs):
    """
    Evaluate the where expression.
    """
    if op == "=":
        return lhs == rhs
    elif op == "!=":
        return lhs != rhs
    elif op == "<":
        return lhs < rhs
    elif op == "<=":
        return lhs <= rhs
    elif op == ">":
        return lhs > rhs
    elif op == ">=":
        return lhs >= rhs
    elif op == "in":
        return lhs in rhs
    elif op == "not in":
        return lhs not in rhs
    elif op == "like":
        pattern = rhs.replace("%", ".*").replace("_", ".")
        return re.match("^" + pattern + "$", lhs) is not None
    else:
        raise Exception("Operator %r is not supported" % op)


def get_indexed_fields(where, indexes):
    """
    Recursive function that accumpulates matches
    in the mutable `indexes` list.

    A match is an expression that compares "$.handle"
    or "$.gramps_id" equal to a value.

    where - a tuple expression, "or" or "and"
    indexes - pass in a list

    Example where clauses:

    There are 4 cases to consider:
    ```
    ("$.gramps_id", "=", "I0043")
    ("$.handle", "=", "abc23652")
    ("and", (...))
    ("or", (...))
    ```
    """
    if len(where) == 3:
        # A comparison expression
        if where[0] in ["$.gramps_id", "$.handle"] and where[1] == "=":
            indexes += [where]
    else:
        # Must be ("and", exprs) or ("or", exprs)
        # Recurse on all expressions
        for expr in where[1]:
            get_indexed_fields(expr, indexes)

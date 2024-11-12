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
OPERATORS = ("=", "!=", "<", "<=", ">", ">=", "in", "not in", "like")


def select(db, table, selections, where, sort_by, page, page_size):
    """This is a DB-API implementation of the DbGeneric.select()
    method.

    :param table: Name of table
    :type table: str
    :param selections: List of json-paths
    :type selections: List[str] or tuple(str)
    :param where: A single where-expression (see below)
    :type where: tuple or list
    :param sort_by: A list of expressions to sort on
    :type where: tuple or list
    :param page: The page number to return (zero-based)
    :type page: int
    :param page_size: The size of a page in rows; None means ignore
    :type page: int or None
    :returns: Returns selected items from select rows, from iterator
    :rtype: dict

    Examples:

    Get the gender and surname of all males, sort by gramps_id:
    ```
    db.select(
        "person",
        ["$.gender", "$.primary_name.surname_list[0].surname"],
        where=["$.gender", "=", Person.MALE],
        sort_by=["$.gramps_id"],
    )
    ```
    Notes:

    Although the SQL engine may support more variations than
    Python (or other implementations) you should not use them to
    ensure that your code will run with all backends.

    The where expressions only support the following operators:
        "=", "!=", "<", "<=", ">", ">=", "in", "not in", "like"

    The `like` operator supports "%" (zero or more characters)
    and "_" (one character) regular expression matches.
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
        # Check for a simple optimization:
        # is where composed of indexable expressions?
        indexed_expressions = []
        non_indexed_expressions = []
        connectors = []
        get_indexed_fields(
            where, indexed_expressions, non_indexed_expressions, connectors
        )
        # Has to have some indexed, and either no non-indexed
        # or only non-indexed combined with "and"
        if indexed_expressions and (
            (not non_indexed_expressions) or ("or" not in connectors)
        ):
            handles_returned = []
            for indexed in indexed_expressions:
                index_field, compare, index_value = indexed
                if isinstance(index_value, str) and index_value.startswith("$"):
                    index_value, compare, index_field = (
                        index_field,
                        compare,
                        index_value,
                    )
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
        if where[1].lower() == "and":
            for expr in [where[0], where[2]]:
                result = match_where(data, expr)
                if not result:
                    return False
            return True
        elif where[1].lower() == "or":
            for expr in [where[0], where[2]]:
                result = match_where(data, expr)
                if result:
                    return True
            return False
        elif where[1].lower() in OPERATORS:
            lhs = eval_expr(where[0], data)
            op = where[1].lower()
            rhs = eval_expr(where[2], data)
            return compare_where(lhs, op, rhs)
        else:
            raise Exception("Operator %r is not supported" % where[1])
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


def get_indexed_fields(where, indexes, non_indexes, connectors):
    """
    Recursive function that accumpulates data
    in the mutable lists.

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
    if where[1] in OPERATORS:
        # A comparison expression
        if (
            (where[0] in ["$.gramps_id", "$.handle"])
            or (where[2] in ["$.gramps_id", "$.handle"])
        ) and where[1] == "=":
            indexes += [where]
        else:
            non_indexes += [where]
    else:
        # Must be (lhs, "and", rhs) or (lhs, "or", rhs)
        # Recurse on all expressions
        connectors += [where[1]]
        for expr in [where[0], where[2]]:
            get_indexed_fields(expr, indexes, non_indexes, connectors)

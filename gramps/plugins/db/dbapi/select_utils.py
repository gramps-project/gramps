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

import orjson

from gramps.gen.lib.json_utils import DataDict


def parse_query_result_value(value):
    """
    Parse a query result value that may be a JSON string.

    This function handles values returned from SQL queries that may be JSON strings
    (starting with '{' or '[') but might not be valid JSON. If the value is a string
    that looks like JSON but fails to parse, it returns the original string.

    Args:
        value: The value from the query result (may be str, bytes, or other types)

    Returns:
        Parsed JSON data (DataDict, list, or original value if not JSON)
    """
    # Only attempt to parse strings that look like JSON
    if isinstance(value, str) and (value.startswith("{") or value.startswith("[")):
        try:
            raw_data = orjson.loads(value)

            if isinstance(raw_data, dict):
                return DataDict(raw_data)
            elif isinstance(raw_data, list):
                # Recursively process list items
                result = []
                for item in raw_data:
                    if isinstance(item, str):
                        # Recursively parse JSON strings (e.g., from json_group_array)
                        result.append(parse_query_result_value(item))
                    elif isinstance(item, dict) and "_class" in item:
                        # Convert dicts with _class to DataDict
                        result.append(DataDict(item))
                    else:
                        result.append(item)
                return result
            else:
                return raw_data
        except (orjson.JSONDecodeError, ValueError, TypeError):
            # If the string is not valid JSON, return it as-is
            # This can happen when a value looks like JSON (starts with { or [)
            # but is actually just a regular string
            return value

    # For non-string values or strings that don't look like JSON, return as-is
    return value

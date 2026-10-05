#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026       Doug Blank <doug.blank@gmail.com>
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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

"""
Helper for freezing the JSON Schema dicts returned by ``get_schema()``.
"""


class FrozenDict(dict):
    """
    A ``dict`` that raises on any attempt to mutate it in place.

    Subclassing ``dict`` (rather than using ``types.MappingProxyType``)
    keeps ``isinstance(x, dict)`` true, which third-party consumers such as
    the ``jsonschema`` library rely on to recognize a JSON Schema "object".
    """

    def _read_only(self, *args, **kwargs):
        raise TypeError(f"{type(self).__name__} is read-only")

    __setitem__ = _read_only
    __delitem__ = _read_only
    clear = _read_only
    pop = _read_only
    popitem = _read_only
    setdefault = _read_only
    update = _read_only


class FrozenList(list):
    """
    A ``list`` that raises on any attempt to mutate it in place.

    Subclassing ``list`` (rather than using ``tuple``) keeps
    ``isinstance(x, list)`` true, for the same reason as :class:`FrozenDict`.
    """

    def _read_only(self, *args, **kwargs):
        raise TypeError(f"{type(self).__name__} is read-only")

    __setitem__ = _read_only
    __delitem__ = _read_only
    __iadd__ = _read_only
    __imul__ = _read_only
    append = _read_only
    clear = _read_only
    extend = _read_only
    insert = _read_only
    pop = _read_only
    remove = _read_only
    reverse = _read_only
    sort = _read_only


def freeze_schema(schema):
    """
    Recursively convert a JSON-schema-shaped value into a read-only
    structure: dicts become :class:`FrozenDict` and lists become
    :class:`FrozenList`.

    ``get_schema()`` classmethods are cached (``functools.cache``) and
    their return value is shared by every caller and by every composing
    parent schema. Freezing it turns any accidental in-place mutation by
    a caller into an immediate ``TypeError`` instead of silently
    corrupting the cached schema for every other caller.

    :param schema: A dict/list/scalar value, as returned by a
                   ``get_schema()`` classmethod.
    :returns: The same structure with all dicts and lists made read-only.
    """
    if isinstance(schema, dict):
        return FrozenDict((key, freeze_schema(value)) for key, value in schema.items())
    if isinstance(schema, list):
        return FrozenList(freeze_schema(item) for item in schema)
    return schema

#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2006  Donald N. Allingham
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
Package providing filtering framework for Gramps.
"""

CustomFilters = None

from ..const import CUSTOM_FILTERS
from ._filterlist import FilterList
from ._genericfilter import (
    GenericFilter,
    GenericFilterFactory,
    DeferredFilter,
    DeferredFamilyFilter,
)
from ._paramfilter import ParamFilter
from ._searchfilter import SearchFilter, ExactSearchFilter


def reload_custom_filters():
    global CustomFilters
    CustomFilters = FilterList(CUSTOM_FILTERS)
    CustomFilters.load()


def set_custom_filters(filter_list):
    global CustomFilters
    CustomFilters = filter_list


def get_filter_by_name(namespace: str, filter_name: str):
    """
    Get a filter_name from a namespace.

    Assumes filters have been loaded.
    """
    if CustomFilters is None:
        return None
    filters_dict = CustomFilters.get_filters_dict(namespace)
    return filters_dict.get(filter_name)


def get_rule_names(namespace: str, filter_name: str):
    """
    Get all of rule names recursively that a filter references
    """
    filt = get_filter_by_name(namespace, filter_name)

    return _get_rule_names_recursively(filt)


def _get_rule_names_recursively(filt, seen: set[str] | None = None):
    """
    Walk a gramps filter object looking for rules.

    Returns a set of rulenames.
    """
    from gramps.gen.filters.rules._matchesfilterbase import MatchesFilterBase

    if seen is None:
        seen = set()
    if filt.name in seen:
        return []
    seen.add(filt.name)

    names = []
    for rule in filt.get_rules():
        names.append(type(rule).__name__)
        if isinstance(rule, MatchesFilterBase):
            nested = rule.find_filter()
            if nested:
                names += _get_rule_names_recursively(nested, seen)
    return names


# if not CustomFilters:  # moved to viewmanager
# reload_custom_filters()

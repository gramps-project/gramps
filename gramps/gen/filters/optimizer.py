#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2024  Doug Blank <doug.blank@gmail.com>
# Copyright (C) 2025  Steve Youngs <steve@youngs.cc>
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

import logging

LOG = logging.getLogger(".filter.optimizer")


def intersection(sets):
    # sort the sets by length, shortest first.
    # with interrsection, the shortest of the starting sets determines the
    # maximum size of the result
    sorted_sets = sorted(sets, key=lambda s: len(s))
    return set.intersection(*sorted_sets)


def union(sets):
    return set.union(*sets)


class Optimizer:
    """
    Optimizer uses the filter's pre-selected selected_handles
    for each rule to reduce the search space.
    selected_handles is a superset of the final result of the rule.
    the selected_handles of each rule in each filter of the filter list
    are combined to create `possible_handles`, the superset of the result
    of the filter list.
    """

    def __init__(self, all_handles, filter):
        """
        Compute possible_handles for the filter list.
        """
        self.all_handles = all_handles
        self.possible_handles = self.compute_potential_handles_for_filter(filter)

    def compute_potential_handles_for_filter(self, filter):
        """
        Compute the superset of handles which are the result of the supplied filter
        In the worst case, this is self.all_handles
        """
        if len(filter.flist) == 0:
            return self.all_handles
        handlesets = [
            self.compute_potential_handles_for_rule(rule) for rule in filter.flist
        ]

        if filter.logical_op == "and":
            # the result of filter is contained within the intersection of the sets in handlesets
            handles = intersection(handlesets)
        elif filter.logical_op in ("or", "one"):
            # the result of filter is contained within the union of the sets in handlesets
            handles = union(handlesets)

        if filter.invert:
            handles = self.all_handles.difference(handles)

        return handles

    def compute_potential_handles_for_rule(self, rule):
        """
        Compute the superset of handles which are the result of the supplied rule
        In the worst case, this is self.all_handles
        """
        if hasattr(rule, "selected_handles"):
            # this rule has provided a superset of handles that
            # contain the result of the rule
            return rule.selected_handles
        if hasattr(rule, "find_filter"):
            filter = rule.find_filter()
            if filter:
                return self.compute_potential_handles_for_filter(filter)
        return (
            self.all_handles
        )  # no optimization ispossible so assume all handles could match the rule

    def get_possible_handles(self):
        """
        Returns possible_handles

        `possible_handles` is a superset of the handles that will match the filter.
        """
        LOG.debug("optimizer possible_handles: %s", len(self.possible_handles))
        return self.possible_handles

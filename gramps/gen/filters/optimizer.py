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
    if sets:
        result = sets[0]
        for s in sets[1:]:
            result = result.intersection(s)
        return result
    else:
        return set()


def union(sets):
    if sets:
        result = sets[0]
        for s in sets[1:]:
            result = result.union(s)
        return result
    else:
        return set()


class Optimizer:
    """
    Optimizer to use the filter's pre-selected selected_handles
    to include or exclude.
    """

    def __init__(self, all_handles, filter):
        """
        Initialize the collection of selected_handles in the filter list.
        """
        self.all_handles = all_handles
        self.handles_in = self.compute_potential_handles_for_filter(filter)
        self.handles_out = set()

    def compute_potential_handles_for_filter(self, filter):
        """
        Compute the superset of handles which are the result of the supplied filter
        """
        if len(filter.flist) == 0:
            return self.all_handles
        handlesets = [
            self.compute_potential_handles_for_rule(rule) for rule in filter.flist
        ]

        if filter.logical_op == "and":
            handles = intersection(handlesets)
        elif filter.logical_op in ("or", "one"):
            handles = union(handlesets)

        if filter.invert:
            handles = self.all_handles.difference(handles)

        return handles

    def compute_potential_handles_for_rule(self, rule):
        """
        Compute the superset of handles which are the result of the supplied rule
        """
        if hasattr(rule, "selected_handles"):
            return rule.selected_handles  # this rule can be optimised
        if hasattr(rule, "find_filter"):
            filter = rule.find_filter()
            if filter:
                return self.compute_potential_handles_for_filter(filter)
        return (
            self.all_handles
        )  # no optimization possible so assume all handles could match the rule

    def get_handles(self):
        """
        Returns handles_in, and handles_out.

        `handles_in` is a set of handles to include.
        Then those in the set are a superset of the items that will match.

        `handles_out` is a set. If any handle is in the set, it will
        not be included in the final results.
        """
        LOG.debug(
            "optimizer handles_in: %s, handles_out: %s",
            len(self.handles_in),
            len(self.handles_out),
        )
        return self.handles_in, self.handles_out

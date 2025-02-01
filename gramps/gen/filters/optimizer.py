#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2024  Doug Blank <doug.blank@gmail.com>
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

    def __init__(self, filter):
        """
        Initialize the collection of selected_handles in the filter list.
        """
        self.all_selected_handles = []
        self.walk_filters(filter, False, self.all_selected_handles)

    def walk_filters(self, filter, parent_invert, result):
        """
        Recursively walk all of the filters/rules and get
        rules with selected_handles
        """
        current_invert = parent_invert if not filter.invert else not parent_invert
        LOG.debug(
            "walking, filter: %s, invert=%s, parent_invert=%s",
            filter,
            filter.invert,
            parent_invert,
        )
        rules_with_selected_handles = []
        for item in filter.flist:
            if hasattr(item, "find_filter"):
                rule_filter = item.find_filter()
                if rule_filter is not None:
                    self.walk_filters(
                        rule_filter,
                        current_invert,
                        result,
                    )
            elif hasattr(item, "selected_handles"):
                rules_with_selected_handles.append(set(item.selected_handles))
        if rules_with_selected_handles:
            LOG.debug(
                "filter %s: parent_invert=%s, invert=%s, op=%s, number of rules with selected_handles=%s",
                filter,
                parent_invert,
                filter.invert,
                filter.logical_op,
                len(rules_with_selected_handles),
            )
            result.append(
                (
                    current_invert,
                    filter.logical_op,
                    rules_with_selected_handles,
                )
            )

    def get_handles(self):
        """
        Returns handles_in, and handles_out.

        `handles_in` is either None, or a set of handles to include.
        if it is None, then there is no evidence to only include
        particular handles. If it is a set, then those in the set
        are a superset of the items that will match.

        `handles_out` is a set. If any handle is in the set, it will
        not be included in the final results.

        The handles_in are selected if all of the rules are connected with
        "and" and not inverted. The handles_out are selected if all of the
        rules are connected with "and" and inverted.
        """
        handles_in = None
        handles_out = set()
        # Get all positive non-inverted selected_handles
        for inverted, logical_op, selected_handles in self.all_selected_handles:
            if logical_op == "and" and not inverted:
                LOG.debug("optimizer positive match!")
                if handles_in is None:
                    handles_in = intersection(selected_handles)
                else:
                    handles_in = intersection([handles_in] + selected_handles)

        # Get all inverted selected_handles:
        for inverted, logical_op, selected_handles in self.all_selected_handles:
            if logical_op == "and" and inverted:
                LOG.debug("optimizer inverted match!")
                handles_out = union([handles_out] + selected_handles)

        if handles_in is not None:
            handles_in = handles_in - handles_out

        LOG.debug("optimizer handles_in: %s", len(handles_in) if handles_in else 0)
        return handles_in, handles_out

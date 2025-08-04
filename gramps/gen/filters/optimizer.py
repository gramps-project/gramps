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
# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
from __future__ import annotations
import logging

# -------------------------------------------------------------------------
#
# Typing modules
#
# -------------------------------------------------------------------------
from typing import List, Set, TYPE_CHECKING, Tuple
from .rules import Rule

if TYPE_CHECKING:
    from ._genericfilter import GenericFilter
from ..types import PrimaryObjectHandle

LOG = logging.getLogger(".filter.optimizer")


class Optimizer:
    def __init__(self, top_level_filter):
        self.top_level_filter = top_level_filter

    def compute_potential_handles_for_filter(
        self, filter: GenericFilter
    ) -> Tuple[Set[PrimaryObjectHandle] | None, Set[PrimaryObjectHandle] | None]:
        if len(filter.flist) == 0:
            return (None, None)

        handles_in = None
        handles_out = None
        for rule in filter.flist:
            if filter.logical_op == "and" or len(filter.flist) == 1:
                rule_in, rule_out = self.compute_potential_handles_for_rule(rule)
                if rule_in is not None:
                    if handles_in is None:
                        handles_in = rule_in
                    else:
                        handles_in = handles_in.intersection(rule_in)
                if rule_out is not None:
                    if handles_out is None:
                        handles_out = rule_out
                    else:
                        handles_out = handles_out.union(rule_out)

        if filter.invert:
            handles_in, handles_out = handles_out, handles_in

        return handles_in, handles_out

    def compute_potential_handles_for_rule(
        self,
        rule: Rule,
    ) -> Tuple[Set[PrimaryObjectHandle] | None, Set[PrimaryObjectHandle] | None]:
        """
        Find the the handles for a particular rule.
        """
        # Has to be of the appropriate type
        if hasattr(rule, "selected_handles"):
            return (rule.selected_handles, None)
        if hasattr(rule, "find_filter"):
            filter = rule.find_filter()
            if filter and self.is_same_namespace(filter):
                return self.compute_potential_handles_for_filter(filter)
        return (None, None)

    def is_same_namespace(self, filter):
        """
        Determine if the given filter is in the 'same namespace' as the top-level filter.

        In this context, 'same namespace' means that both filters are instances of the same class,
        as determined by comparing their class names.

        Parameters:
            filter: The filter object to compare against the top-level filter.

        Returns:
            True if both filters have the object type, False otherwise.
        """
        return type(self.top_level_filter.make_obj()) == type(filter.make_obj())

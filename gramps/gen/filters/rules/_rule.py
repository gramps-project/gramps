# -*- coding: utf-8 -*-
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
Base class for filter rules.
"""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
from __future__ import annotations
import re

from ...errors import FilterError
from ...const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext

# -------------------------------------------------------------------------
#
# enable logging for error handling
#
# -------------------------------------------------------------------------
import logging

LOG = logging.getLogger(".rules")


# -------------------------------------------------------------------------
#
# Typing modules
#
# -------------------------------------------------------------------------
from typing import Any, List
from ...db import Database


# -------------------------------------------------------------------------
#
# Rule
#
# -------------------------------------------------------------------------
class Rule:
    """Base rule class."""

    labels: list[str] = []
    name = ""
    category = _("Miscellaneous filters")
    description = _("No description")
    allow_regex = False

    def __init__(self, arg, use_regex=False, use_case=False):
        self.list = []
        self.regex = []
        self.match_substring = self.__match_substring
        self.set_list(arg)
        self.use_regex = use_regex
        self.use_case = use_case
        self.nrprepare = 0

    def is_empty(self):
        return False

    def requestprepare(self, db: Database, user):
        """
        Request that the prepare method of the rule is executed if needed

        Special: Custom Filters have fixed values, so only one instance needs to
        exists during a search. It is stored in a FilterStore, and initialized
        once.
        As filters are can be grouped in a group
        filter, we request a prepare. Only the first time prepare will be
        called
        """
        if self.nrprepare == 0:
            if self.use_regex:
                self.regex = [None] * len(self.labels)
                for index, label in enumerate(self.labels):
                    if self.list[index]:
                        try:
                            if self.use_case:
                                self.regex[index] = re.compile(self.list[index])
                            else:
                                self.regex[index] = re.compile(self.list[index], re.I)
                        except re.error:
                            self.regex[index] = re.compile("")
                self.match_substring = self.match_regex
            self._checked_prepare(db, user)
        self.nrprepare += 1
        if self.nrprepare > 20:  # more references to a filter than expected
            raise FilterError(
                _("The filter definition contains a loop."),
                _(
                    "One rule references another which eventually"
                    " references the first."
                ),
            )

    def prepare(self, db: Database, user):
        """prepare so the rule can be executed efficiently"""
        pass

    def _checked_prepare(self, db: Database, user):
        """
        Call prepare, routing through a DB override when one is registered.

        This method is called by requestprepare and is never overridden by
        rule subclasses, so the lookup works regardless of inheritance depth.
        """
        cls = type(self)
        parts = cls.__module__.split(".")
        try:
            key = (parts[parts.index("rules") + 1], cls.__name__)
        except (ValueError, IndexError):
            key = (None, cls.__name__)
        entry = (
            getattr(db, "_override_registry", {}).get("rule", {}).get(key)
            if db is not None and not db.is_proxy()
            else None
        )
        if entry is not None and entry.get("prepare") is not None:
            LOG.debug("%s using optimized prepare", cls.__name__)
            return entry["prepare"](self, cls.prepare, db, user)
        LOG.debug("%s using non-optimized prepare", cls.__name__)
        return self.prepare(db, user)

    def _checked_apply_to_one(self, db: Database, obj) -> bool:
        """
        Call apply_to_one, routing through a DB override when one is registered.

        Filters call this method instead of apply_to_one directly so that
        overrides fire for rules that inherit apply_to_one from a base class
        (e.g. HasTag inheriting from HasTagBase) without any wrapping magic.
        Internal super().apply_to_one() calls inside rule implementations
        bypass this method and go straight to the original, so there is no
        risk of double dispatch.
        """
        cls = type(self)
        parts = cls.__module__.split(".")
        try:
            key = (parts[parts.index("rules") + 1], cls.__name__)
        except (ValueError, IndexError):
            key = (None, cls.__name__)
        entry = (
            getattr(db, "_override_registry", {}).get("rule", {}).get(key)
            if db is not None and not db.is_proxy()
            else None
        )
        if entry is not None and entry.get("apply_to_one") is not None:
            LOG.debug("%s using optimized apply_to_one", type(self).__name__)
            return entry["apply_to_one"](self, type(self).apply_to_one, db, obj)
        LOG.debug("%s using non-optimized apply_to_one", type(self).__name__)
        return self.apply_to_one(db, obj)

    def requestreset(self):
        """
        Request that the reset method of the rule is executed if possible

        Special: Custom Filters have fixed values, so only one instance needs to
        exists during a search. It is stored in a FilterStore, and initialized
        once.
        As filters are can be grouped in a group
        filter, we request a reset. Only the last time reset will be
        called
        """
        self.nrprepare -= 1
        if self.nrprepare == 0:
            self.reset()

    def reset(self):
        """remove no longer needed memory"""
        pass

    def set_list(self, arg):
        """Store the values of this rule."""
        assert isinstance(arg, list) or arg is None, "Argument is not a list"
        if len(arg) != len(self.labels):
            LOG.warning(
                (
                    "Number of arguments does not match number of "
                    + "labels.\n   list:   %s\n   labels: %s"
                )
                % (arg, self.labels)
            )
        self.list = arg

    def values(self):
        """Return the values used by this rule."""
        return self.list

    def check(self):
        """Verify the number of rule values versus the number of rule labels."""
        return len(self.list) == len(self.labels)

    def apply_to_one(self, dummy_db: Database, dummy_object: Any) -> bool:
        """Apply the rule to some database entry; must be overwritten."""
        return True

    def display_values(self):
        """Return the labels and values of this rule."""
        l_v = (
            '%s="%s"'
            % (
                _(
                    self.labels[index][0]
                    if isinstance(self.labels[index], tuple)
                    else self.labels[index]
                ),
                item,
            )
            for index, item in enumerate(self.list)
            if item
        )

        return ";".join(l_v)

    def __match_substring(self, param_index, str_var):
        """
        Return boolean indicating if database element represented by str_var
        matches filter element indicated by param_index using case insensitive
        string matching.
        """
        # make str_var unicode so that search for ü works
        # see issue 3188
        str_var = str(str_var)
        if self.list[param_index] and (
            str_var.upper().find(self.list[param_index].upper()) == -1
        ):
            return False
        else:
            return True

    def match_regex(self, param_index, str_var):
        """
        Return boolean indicating if database element represented by str_var
        matches filter element indicated by param_index using a regular
        expression search.
        """
        str_var = str(str_var)
        if self.list[param_index] and self.regex[param_index].search(str_var) is None:
            return False
        else:
            return True

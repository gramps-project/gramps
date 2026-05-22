#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2010    Nick Hall
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
Rule that checks for an object with a particular tag.
"""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
from typing import Set

from ...const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from . import Rule

# -------------------------------------------------------------------------
#
# Typing modules
#
# -------------------------------------------------------------------------
from ...lib.primaryobj import PrimaryObject
from ...db import Database
from ...types import PrimaryObjectHandle


# -------------------------------------------------------------------------
#
# HasTag
#
# -------------------------------------------------------------------------
class HasTagBase(Rule):
    """
    Rule that checks for an object with a particular tag.
    """

    labels = ["Tag:"]
    name = "Objects with the <tag>"
    description = "Matches objects with the given tag"
    category = _("General filters")
    namespace = ""

    def prepare(self, db: Database, user) -> None:
        """
        Build the set of matching object handles once before filtering begins.
        """
        self.selected_handles: Set[PrimaryObjectHandle] = set()
        tag = db.get_tag_from_name(self.list[0])
        if tag is not None:
            for _classname, handle in db.find_backlink_handles(
                tag.handle, include_classes=[self.namespace]
            ):
                self.selected_handles.add(handle)

    def apply_to_one(self, db: Database, obj: PrimaryObject) -> bool:
        """
        Return True if this object's handle is in the pre-built match set.
        """
        return obj.handle in self.selected_handles

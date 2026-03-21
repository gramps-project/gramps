#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2006  Donald N. Allingham
# Copyright (C) 2016       Nick Hall
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
Rule that checks for a family that is a descendant of a specified family.
"""

# -------------------------------------------------------------------------
#
# Standard python modules
#
# -------------------------------------------------------------------------

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from .. import Rule
from ....utils.graph import find_descendants
from ....const import GRAMPS_LOCALE as glocale

# -------------------------------------------------------------------------
#
# Typing modules
#
# -------------------------------------------------------------------------
from ....lib import Family
from ....db import Database
from ....types import FamilyHandle
from ....user import UserBase

_ = glocale.translation.gettext


# -------------------------------------------------------------------------
#
# IsDescendantOf
#
# -------------------------------------------------------------------------
class IsDescendantOf(Rule):
    """
    Rule that checks for a family that is a descendant of a specified family.
    """

    labels = [_("ID:"), _("Inclusive:")]
    name = _("Descendant families of <family>")
    category = _("General filters")
    description = _("Matches descendant families of the specified family")

    def prepare(self, db: Database, user: UserBase) -> None:
        self.selected_handles: set[FamilyHandle] = set()
        try:
            inclusive = bool(int(self.list[1]))
        except IndexError:
            inclusive = False
        root_family = db.get_family_from_gramps_id(self.list[0])
        if root_family is not None:
            # The inclusive flag controls only whether the root family itself
            # is included — not whether children are included in traversal.
            if inclusive:
                self.selected_handles.add(root_family.handle)

            # Start from children of the root family (inclusive so children
            # themselves are in the set and their families are found).
            children = [cr.ref for cr in root_family.child_ref_list if cr.ref]
            if children:
                descendants = find_descendants(db, children, inclusive=True)
                for person_handle in descendants:
                    person = db.get_person_from_handle(person_handle)
                    if person:
                        for family_handle in person.family_list:
                            self.selected_handles.add(family_handle)

    def reset(self) -> None:
        self.selected_handles.clear()

    def apply_to_one(self, db: Database, family: Family) -> bool:
        return family.handle in self.selected_handles

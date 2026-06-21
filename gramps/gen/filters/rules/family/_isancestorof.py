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
Rule that checks for a family that is an ancestor of a specified family.
"""

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from .. import Rule
from ....utils.graph import find_ancestors
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
# IsAncestorOf
#
# -------------------------------------------------------------------------
class IsAncestorOf(Rule):
    """
    Rule that checks for a family that is an ancestor of a specified family.
    """

    labels = [_("ID:"), _("Inclusive:")]
    name = _("Ancestor families of <family>")
    category = _("General filters")
    description = _("Matches ancestor families of the specified family")

    def prepare(self, db: Database, user: UserBase) -> None:
        self.selected_handles: set[FamilyHandle] = set()
        try:
            inclusive = bool(int(self.list[1]))
        except IndexError:
            inclusive = False
        root_family = db.get_family_from_gramps_id(self.list[0])
        if root_family is not None:
            if inclusive:
                self.selected_handles.add(root_family.handle)
            parents = [
                h
                for h in [root_family.father_handle, root_family.mother_handle]
                if h is not None
            ]
            if parents:
                ancestors = find_ancestors(db, parents, inclusive=True)
                for person_handle in ancestors:
                    person = db.get_raw_person_data(person_handle)
                    if person is not None and person.parent_family_list:
                        self.selected_handles.add(person.parent_family_list[0])

    def reset(self) -> None:
        self.selected_handles.clear()

    def apply_to_one(self, db: Database, family: Family) -> bool:
        return family.handle in self.selected_handles

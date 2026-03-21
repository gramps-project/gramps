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

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
from ....const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext
try:
    set()
except NameError:
    from sets import Set as set

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from .. import Rule
from ....utils.graph import find_descendants

# -------------------------------------------------------------------------
#
# Typing modules
#
# -------------------------------------------------------------------------
from ....lib import Person
from ....db import Database
from ....types import PersonHandle


# -------------------------------------------------------------------------
#
# IsDescendantFamilyOf
#
# -------------------------------------------------------------------------
class IsDescendantFamilyOf(Rule):
    """Rule that checks for a person that is a descendant or the spouse
    of a descendant of a specified person"""

    labels = [_("ID:"), _("Inclusive:")]
    name = _("Descendant family members of <person>")
    category = _("Descendant filters")
    description = _(
        "Matches people that are descendants or the spouse "
        "of a descendant of a specified person"
    )

    def prepare(self, db: Database, user):
        self.db = db
        self.selected_handles: set[PersonHandle] = set()
        self.root_person = db.get_person_from_gramps_id(self.list[0])
        try:
            if int(self.list[1]):
                inclusive = True
            else:
                inclusive = False
        except IndexError:
            inclusive = True

        if self.root_person is not None:
            # Use the find_descendants function to get descendants
            descendants = find_descendants(
                db, [self.root_person.handle], inclusive=inclusive
            )
            self.selected_handles.update(descendants)

            # Add spouses of descendants
            self.add_spouses_of_descendants(descendants)

    def reset(self):
        self.selected_handles.clear()

    def apply_to_one(self, db: Database, person: Person) -> bool:
        return person.handle in self.selected_handles

    def add_spouses_of_descendants(self, descendants: set[PersonHandle]):
        """Add spouses of all descendants to the selected handles."""
        for person_handle in descendants:
            person = self.db.get_raw_person_data(person_handle)
            if person is not None:
                for family_handle in person.family_list:
                    family = self.db.get_raw_family_data(family_handle)
                    if family is not None:
                        # Add spouse
                        if person_handle == family.father_handle:
                            spouse_handle = family.mother_handle
                        else:
                            spouse_handle = family.father_handle
                        if spouse_handle is not None:
                            self.selected_handles.add(spouse_handle)

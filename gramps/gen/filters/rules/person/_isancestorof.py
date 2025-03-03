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
from ....const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from .. import Rule


# -------------------------------------------------------------------------
#
# Typing modules
#
# -------------------------------------------------------------------------
from typing import Set
from ....lib import Person
from ....db import Database


# -------------------------------------------------------------------------
#
# IsAncestorOf
#
# -------------------------------------------------------------------------
class IsAncestorOf(Rule):
    """Rule that checks for a person that is an ancestor of a specified person"""

    labels = [_("ID:"), _("Inclusive:")]
    name = _("Ancestors of <person>")
    category = _("Ancestral filters")
    description = _("Matches people that are ancestors of a specified person")

    def prepare(self, db: Database, user):
        """Assume that if 'Inclusive' not defined, assume inclusive"""
        self.db = db
        self.selected_handles: Set[str] = set()
        try:
            first = False if int(self.list[1]) else True
        except IndexError:
            first = True
        try:
            root_person = db.get_person_from_gramps_id(self.list[0])
            self.init_ancestor_list(db, root_person, first)
        except:
            pass

    def reset(self):
        self.selected_handles.clear()

    def apply_to_one(self, db: Database, person: Person) -> bool:
        return person.handle in self.selected_handles

    def init_ancestor_list(
        self, db: Database, person: Person | None, first: bool
    ) -> None:
        if not person:
            return
        if person.handle in self.selected_handles:
            return
        if not first:
            self.selected_handles.add(person.handle)
        fam_id = (
            person.parent_family_list[0] if len(person.parent_family_list) > 0 else None
        )
        if fam_id:
            fam = db.get_family_from_handle(fam_id)
            if fam:
                f_id = fam.father_handle
                m_id = fam.mother_handle

                if f_id:
                    self.init_ancestor_list(db, db.get_person_from_handle(f_id), False)
                if m_id:
                    self.init_ancestor_list(db, db.get_person_from_handle(m_id), False)

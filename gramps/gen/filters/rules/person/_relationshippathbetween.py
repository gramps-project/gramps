#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2007  Donald N. Allingham
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
from typing import List, Set, Dict
from ....lib import Person
from ....db import Database
from ....types import PersonHandle


# -------------------------------------------------------------------------
#
# RelationshipPathBetween
#
# -------------------------------------------------------------------------
class RelationshipPathBetween(Rule):
    """Rule that checks for a person that is a descendant of a specified person
    not more than N generations away"""

    labels = [_("ID:"), _("ID:")]
    name = _("Relationship path between <persons>")
    category = _("Relationship filters")
    description = _(
        "Matches the ancestors of two persons back "
        "to a common ancestor, producing the relationship "
        "path between two persons."
    )

    def prepare(self, db: Database, user):
        self.db = db
        self.selected_handles: Set[PersonHandle] = set()
        root1 = db.get_person_from_gramps_id(self.list[0])
        root2 = db.get_person_from_gramps_id(self.list[1])
        if root1 and root2:
            self.init_list(root1.handle, root2.handle)

    def reset(self):
        self.selected_handles.clear()

    def desc_list(self, handle: PersonHandle, map, first: bool):
        if not first:
            map.add(handle)

        p = self.db.get_person_from_handle(handle)
        for fam_id in p.family_list:
            fam = self.db.get_family_from_handle(fam_id)
            if fam:
                for child_ref in fam.child_ref_list:
                    if child_ref.ref:
                        self.desc_list(child_ref.ref, map, False)

    def apply_filter(
        self,
        rank: int,
        handle: PersonHandle,
        plist: Set[PersonHandle],
        pmap: Dict[PersonHandle, int],
    ):
        if not handle:
            return
        person = self.db.get_person_from_handle(handle)
        if person is None:
            return
        plist.add(handle)
        pmap[person.handle] = rank

        fam_id = (
            person.parent_family_list[0] if len(person.parent_family_list) > 0 else None
        )
        if not fam_id:
            return
        family = self.db.get_family_from_handle(fam_id)
        if family is not None:
            self.apply_filter(rank + 1, family.father_handle, plist, pmap)
            self.apply_filter(rank + 1, family.mother_handle, plist, pmap)

    def apply_to_one(self, db: Database, person: Person) -> bool:
        return person.handle in self.selected_handles

    def init_list(self, p1_handle: PersonHandle, p2_handle: PersonHandle):
        firstMap: Dict[PersonHandle, int] = {}
        firstList: Set[PersonHandle] = set()
        secondMap: Dict[PersonHandle, int] = {}
        secondList: Set[PersonHandle] = set()
        common: List[PersonHandle] = []
        rank = 9999999

        self.apply_filter(0, p1_handle, firstList, firstMap)
        self.apply_filter(0, p2_handle, secondList, secondMap)

        for person_handle in firstList and secondList:
            new_rank = firstMap[person_handle]
            if new_rank < rank:
                rank = new_rank
                common = [person_handle]
            elif new_rank == rank:
                common.append(person_handle)

        path1 = set([p1_handle])
        path2 = set([p2_handle])

        for person_handle in common:
            new_map: Set[PersonHandle] = set()
            self.desc_list(person_handle, new_map, True)
            path1.update(new_map.intersection(firstMap))
            path2.update(new_map.intersection(secondMap))
        self.selected_handles.update(path1, path2, common)

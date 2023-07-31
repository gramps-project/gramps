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

    def prepare(self, db, user):
        self.db = db
        self.map = set()
        try:
            root1_handle = db.get_person_from_gramps_id(self.list[0]).get_handle()
            root2_handle = db.get_person_from_gramps_id(self.list[1]).get_handle()
            self.init_list(root1_handle, root2_handle)
        except:
            pass

    def reset(self):
        self.map = ()

    def desc_list(self, handle, map, first):
        if not first:
            map.add(handle)

        p = self.db.get_person_from_handle(handle)
        for fam_id in p.get_family_handle_list():
            fam = self.db.get_family_from_handle(fam_id)
            if fam:
                for child_ref in fam.get_child_ref_list():
                    if child_ref.ref:
                        self.desc_list(child_ref.ref, map, 0)

    def apply_filter(self, rank, handle, plist, pmap):
        if not handle:
            return
        person = self.db.get_person_from_handle(handle)
        if person is None:
            return
        plist.add(handle)
        pmap[person.get_handle()] = rank

        fam_id = person.get_main_parents_family_handle()
        if not fam_id:
            return
        family = self.db.get_family_from_handle(fam_id)
        if family is not None:
            self.apply_filter(rank + 1, family.get_father_handle(), plist, pmap)
            self.apply_filter(rank + 1, family.get_mother_handle(), plist, pmap)

    def apply(self, db, person):
        return person.handle in self.map

    def init_list(self, p1_handle, p2_handle):
        firstMap = {}
        firstList = set()
        secondMap = {}
        secondList = set()
        common = []
        rank = 9999999

        self.apply_filter(0, p1_handle, firstList, firstMap)
        self.apply_filter(0, p2_handle, secondList, secondMap)

        for person_handle in firstList & secondList:
            new_rank = firstMap[person_handle]
            if new_rank < rank:
                rank = new_rank
                common = [person_handle]
            elif new_rank == rank:
                common.append(person_handle)

        path1 = set([p1_handle])
        path2 = set([p2_handle])

        for person_handle in common:
            new_map = set()
            self.desc_list(person_handle, new_map, 1)
            path1.update(new_map.intersection(firstMap))
            path2.update(new_map.intersection(secondMap))
        self.map.update(path1, path2, common)

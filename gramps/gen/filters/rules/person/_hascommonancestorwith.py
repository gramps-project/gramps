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
from ....const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ....utils.db import for_each_ancestor
from .. import Rule


# -------------------------------------------------------------------------
#
# HasCommonAncestorWith
#
# -------------------------------------------------------------------------
class HasCommonAncestorWith(Rule):
    """Rule that checks for a person that has a common ancestor with a specified person"""

    labels = [_("ID:")]
    name = _("People with a common ancestor with <person>")
    category = _("Ancestral filters")
    description = _(
        "Matches people that have a common ancestor " "with a specified person"
    )

    def prepare(self, db, user):
        self.db = db
        # For each(!) person we keep track of who their ancestors
        # are, in a set(). So we only have to compute a person's
        # ancestor list once.
        # Start with filling the cache for root person (gramps_id in self.list[0])
        self.ancestor_cache = {}
        root_person = db.get_person_from_gramps_id(self.list[0])
        if root_person:
            self.add_ancs(db, root_person)
            self.with_people = [root_person.handle]
        else:
            self.with_people = []

    def add_ancs(self, db, person):
        if person and person.handle not in self.ancestor_cache:
            self.ancestor_cache[person.handle] = set()
            # We are going to compare ancestors of one person with that of
            # another person; if that other person is an ancestor and itself
            # has no ancestors is must be included, this is achieved by the
            # little trick of making a person his own ancestor.
            self.ancestor_cache[person.handle].add(person.handle)
        else:
            return

        for fam_handle in person.get_parent_family_handle_list():
            parentless_fam = True
            fam = db.get_family_from_handle(fam_handle)
            if fam:
                for par_handle in (fam.get_father_handle(), fam.get_mother_handle()):
                    if par_handle:
                        parentless_fam = False
                        par = db.get_person_from_handle(par_handle)
                        if par and par.handle not in self.ancestor_cache:
                            self.add_ancs(db, par)
                        if par:
                            self.ancestor_cache[person.handle] |= self.ancestor_cache[
                                par.handle
                            ]
                if parentless_fam:
                    self.ancestor_cache[person.handle].add(fam_handle)

    def reset(self):
        self.ancestor_cache = {}

    def has_common_ancestor(self, other):
        for handle in self.with_people:
            if (handle in self.ancestor_cache and self.ancestor_cache[handle]) & (
                other
                and other.handle in self.ancestor_cache
                and self.ancestor_cache[other.handle]
            ):
                return True
        return False

    def apply(self, db, person):
        if person and person.handle not in self.ancestor_cache:
            self.add_ancs(db, person)

        return self.has_common_ancestor(person)

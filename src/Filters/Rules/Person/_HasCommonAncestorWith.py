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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id:_HasCommonAncestorWith.py 9912 2008-01-22 09:17:46Z acraphae $

#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
from gen.ggettext import gettext as _

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from Utils import for_each_ancestor
from Filters.Rules._Rule import Rule

#-------------------------------------------------------------------------
#
# HasCommonAncestorWith
#
#-------------------------------------------------------------------------
class HasCommonAncestorWith(Rule):
    """Rule that checks for a person that has a common ancestor with a specified person"""

    labels      = [ _('ID:') ]
    name        = _('People with a common ancestor with <person>')
    category    = _("Ancestral filters")
    description = _("Matches people that have a common ancestor "
                    "with a specified person")

    def prepare(self, db):
        self.db = db
        # For each(!) person we keep track of who their ancestors
        # are, in a set(). So we only have to compute a person's
        # ancestor list once.
        # Start with filling the cache for root person (gramps_id in self.list[0])
        self.ancestor_cache = {}
        root_person = db.get_person_from_gramps_id(self.list[0])
        self.add_ancs(db, root_person)
        self.with_people = [root_person.handle]

    def add_ancs(self, db, person):
        if person.handle not in self.ancestor_cache:
            self.ancestor_cache[person.handle] = set()
        else:
            return

        for fam_handle in person.get_parent_family_handle_list():
            fam = db.get_family_from_handle(fam_handle)
            for par_handle in (fam.get_father_handle(), fam.get_mother_handle()):
                if par_handle:
                    par = db.get_person_from_handle(par_handle)
                    if par and par.handle not in self.ancestor_cache:
                        self.add_ancs(db, par)
                    if par:
                        self.ancestor_cache[person.handle].add(par)
                        self.ancestor_cache[person.handle] |= self.ancestor_cache[par.handle]

    def reset(self):
        self.ancestor_cache = {}

    def has_common_ancestor(self, other):
        for handle in self.with_people:
            if self.ancestor_cache[handle] & \
                    self.ancestor_cache[other.handle]:
                return True
        return False

    def apply(self, db, person):
        if person.handle not in self.ancestor_cache:
            self.add_ancs(db, person)

        return self.has_common_ancestor(person)

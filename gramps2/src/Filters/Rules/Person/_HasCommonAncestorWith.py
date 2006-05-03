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

# $Id$

#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _

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

    def prepare(self,db):
        self.db = db
        # Keys in `ancestor_cache' are ancestors of list[0].
        # We delay the computation of ancestor_cache until the
        # first use, because it's not uncommon to instantiate
        # this class and not use it.
        self.ancestor_cache = {}

    def reset(self):
        self.ancestor_cache = {}

    def init_ancestor_cache(self,db):
        # list[0] is an Id, but we need to pass a Person to for_each_ancestor.
        try:
            handle = db.get_person_from_gramps_id(self.list[0]).get_handle()
            if handle:
                def init(self,handle): self.ancestor_cache[handle] = 1
                for_each_ancestor(db,[handle],init,self)
        except:
            pass

    def apply(self,db,person):
        # On the first call, we build the ancestor cache for the
        # reference person.   Then, for each person to test,
        # we browse his ancestors until we found one in the cache.
        if len(self.ancestor_cache) == 0:
            self.init_ancestor_cache(db)
        handle = person.handle
        return for_each_ancestor(
            db,[handle],
            lambda self,handle: self.ancestor_cache.has_key(handle),
            self);

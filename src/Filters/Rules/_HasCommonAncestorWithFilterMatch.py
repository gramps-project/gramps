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
from _HasCommonAncestorWith import HasCommonAncestorWith
from _MatchesFilter import MatchesFilter

#-------------------------------------------------------------------------
#
# HasCommonAncestorWithFilterMatch
#
#-------------------------------------------------------------------------
class HasCommonAncestorWithFilterMatch(HasCommonAncestorWith):
    """Rule that checks for a person that has a common ancestor with
    someone matching a filter"""

    labels      = [ _('Filter name:') ]
    name        = _('People with a common ancestor with <filter> match')
    description = _("Matches people that have a common ancestor "
                    "with anybody matched by a filter")
    category    = _("Ancestral filters")

    def __init__(self,list):
        HasCommonAncestorWith.__init__(self,list)
        self.ancestor_cache = {}

    def init_ancestor_cache(self,db):
        filt = MatchesFilter(self.list)
        filt.prepare(db)
        def init(self,h): self.ancestor_cache[h] = 1
        for handle in db.get_person_handles(sort_handles=False):
            if (not self.ancestor_cache.has_key (handle)
                and filt.apply (db, db.get_person_from_handle(handle))):
                for_each_ancestor(db,[handle],init,self)
        filt.reset()

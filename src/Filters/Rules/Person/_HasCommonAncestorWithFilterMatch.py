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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id:_HasCommonAncestorWithFilterMatch.py 9912 2008-01-22 09:17:46Z acraphae $

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
from _HasCommonAncestorWith import HasCommonAncestorWith
from _MatchesFilter import MatchesFilter

#-------------------------------------------------------------------------
#
# HasCommonAncestorWithFilterMatch
#
#-------------------------------------------------------------------------
class HasCommonAncestorWithFilterMatch(HasCommonAncestorWith,MatchesFilter):
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

    def prepare(self, db):
        self.db = db
        # For each(!) person we keep track of who their ancestors
        # are, in a set(). So we only have to compute a person's
        # ancestor list once.
        # Start with filling the cache for root person (gramps_id in self.list[0])
        self.ancestor_cache = {}
        self.with_people = []
        filt = MatchesFilter(self.list)
        filt.prepare(db)
        for handle in db.iter_person_handles():
            person = db.get_person_from_handle(handle)
            if filt.apply (db, person):
                #store all people in the filter so as to compare later
                self.with_people.append(person.handle)
                #fill list of ancestor of person if not present yet
                if handle not in self.ancestor_cache:
                    self.add_ancs(db, person)
        filt.reset()

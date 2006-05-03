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
from _IsAncestorOf import IsAncestorOf
from _MatchesFilter import MatchesFilter

#-------------------------------------------------------------------------
#
# IsAncestorOfFilterMatch
#
#-------------------------------------------------------------------------
class IsAncestorOfFilterMatch(IsAncestorOf):
    """Rule that checks for a person that is an ancestor of
    someone matched by a filter"""

    labels      = [ _('Filter name:') ]
    name        = _('Ancestors of <filter> match')
    category    =  _("Ancestral filters")
    description = _("Matches people that are ancestors "
                    "of anybody matched by a filter")


    def __init__(self,list):
        IsAncestorOf.__init__(self,list)
    
    def prepare(self,db):
        self.db = db
        self.map = {}
        try:
            if int(self.list[1]):
                first = 0
            else:
                first = 1
        except IndexError:
            first = 1
            
        filt = MatchesFilter(self.list[0:1])
        filt.prepare(db)
        for person_handle in db.get_person_handles(sort_handles=False):
            person = db.get_person_from_handle( person_handle)
            if filt.apply (db, person):
                self.init_ancestor_list (db,person,first)
        filt.reset()

    def reset(self):
        self.map = {}

    def apply(self,db,person):
        return self.map.has_key(person.handle)

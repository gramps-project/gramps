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
from Filters.Rules._Rule import Rule
from _MatchesFilter import MatchesFilter

#-------------------------------------------------------------------------
#
# IsParentOfFilterMatch
#
#-------------------------------------------------------------------------
class IsParentOfFilterMatch(Rule):
    """Rule that checks for a person that is a parent
    of someone matched by a filter"""

    labels      = [ _('Filter name:') ]
    name        = _('Parents of <filter> match')
    category    = _('Family filters')
    description = _("Matches parents of anybody matched by a filter")

    def prepare(self,db):
        self.db = db
        self.map = {}
        filt = MatchesFilter(self.list)
        filt.prepare(db)
        for person_handle in db.get_person_handles(sort_handles=False):
            person = db.get_person_from_handle(person_handle)
            if filt.apply (db, person):
                self.init_list (person)
        filt.reset()

    def reset(self):
        self.map = {}

    def apply(self,db,person):
        return self.map.has_key(person.handle)

    def init_list(self,person):
        for fam_id,frel,mrel in person.get_parent_family_handle_list():
            fam = self.db.get_family_from_handle(fam_id)
            for parent_id in [fam.get_father_handle (), fam.get_mother_handle ()]:
                if parent_id:
                    self.map[parent_id] = 1

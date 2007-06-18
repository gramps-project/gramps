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
from _MatchesFilter import MatchesFilter

#-------------------------------------------------------------------------
#
# IsSiblingOfFilterMatch
#
#-------------------------------------------------------------------------
class IsSiblingOfFilterMatch(MatchesFilter):
    """Rule that checks for siblings of someone matched by a filter"""

    labels      = [ _('Filter name:') ]
    name        = _('Siblings of <filter> match')
    category    = _('Family filters')
    description = _("Matches siblings of anybody matched by a filter")

    def prepare(self,db):
        self.db = db
        self.map = {}
        filt = MatchesFilter(self.list)
        filt.prepare(db)
        for person_handle in db.get_person_handles(sort_handles=False):
            person = db.get_person_from_handle( person_handle)
            if filt.apply (db, person):
                self.init_list (person)
        filt.reset()

    def reset(self):
        self.map = {}

    def apply(self,db,person):
        return self.map.has_key(person.handle)

    def init_list(self,person):
        if not person:
            return
        fam_id = person.get_main_parents_family_handle()
        fam = self.db.get_family_from_handle(fam_id)
        if fam:
            for child_ref in fam.get_child_ref_list():
                if child_ref.ref != person.handle:
                    self.map[child_ref.ref] = 1

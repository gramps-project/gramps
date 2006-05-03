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
from _Rule import Rule

#-------------------------------------------------------------------------
#
# IsDescendantFamilyOf
#
#-------------------------------------------------------------------------
class IsDescendantFamilyOf(Rule):
    """Rule that checks for a person that is a descendant or the spouse
    of a descendant of a specified person"""

    labels      = [ _('ID:') ]
    name        = _('Descendant family members of <person>')
    category    = _('Descendant filters')
    description = _("Matches people that are descendants or the spouse "
                    "of a descendant of a specified person")
    
    def apply(self,db,person):
        self.map = {}
        self.orig_handle = person.handle
        self.db = db
        return self.search(person.handle,1)

    def search(self,handle,val):
        try:
            if handle == self.db.get_person_from_gramps_id(self.list[0]).get_handle():
                self.map[handle] = 1
                return True
        except:
            return False
        
        p = self.db.get_person_from_handle(handle)
        for (f,r1,r2) in p.get_parent_family_handle_list():
            family = self.db.get_family_from_handle(f)
            for person_handle in [family.get_mother_handle(),family.get_father_handle()]:
                if person_handle:
                    if self.search(person_handle,0):
                        return True
        if val:
            for family_handle in p.get_family_handle_list():
                family = self.db.get_family_from_handle(family_handle)
                if handle == family.get_father_handle():
                    spouse_id = family.get_mother_handle()
                else:
                    spouse_id = family.get_father_handle()
                if spouse_id:
                    if self.search(spouse_id,0):
                        return True
        return False

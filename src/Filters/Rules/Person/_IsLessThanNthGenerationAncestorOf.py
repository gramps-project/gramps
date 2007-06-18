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

#-------------------------------------------------------------------------
#
# IsLessThanNthGenerationAncestorOf
#
#-------------------------------------------------------------------------
class IsLessThanNthGenerationAncestorOf(Rule):
    """Rule that checks for a person that is an ancestor of a specified person
    not more than N generations away"""

    labels      = [ _('ID:'), _('Number of generations:') ]
    name        = _('Ancestors of <person> not more than <N> generations away')
    category    = _("Ancestral filters")
    description = _("Matches people that are ancestors "
                    "of a specified person not more than N generations away")

    def prepare(self,db):
        self.db = db
        self.map = {}
        try:
            root_handle = db.get_person_from_gramps_id(self.list[0]).get_handle()
            self.init_ancestor_list(root_handle,0)
        except:
            pass

    def reset(self):
        self.map = {}
    
    def apply(self,db,person):
        return self.map.has_key(person.handle)

    def init_ancestor_list(self,handle,gen):
#        if self.map.has_key(p.get_handle()) == 1:
#            loop_error(self.orig,p)
        if not handle:
            return
        if gen:
            self.map[handle] = 1
            if gen >= int(self.list[1]):
                return
        
        p = self.db.get_person_from_handle(handle)
        fam_id = p.get_main_parents_family_handle()
        fam = self.db.get_family_from_handle(fam_id)
        if fam:
            f_id = fam.get_father_handle()
            m_id = fam.get_mother_handle()
        
            if f_id:
                self.init_ancestor_list(f_id,gen+1)
            if m_id:
                self.init_ancestor_list(m_id,gen+1)

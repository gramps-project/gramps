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
# IsAncestorOf
#
#-------------------------------------------------------------------------
class IsAncestorOf(Rule):
    """Rule that checks for a person that is an ancestor of a specified person"""

    labels      = [ _('ID:'), _('Inclusive:') ]
    name        = _('Ancestors of <person>')
    category    = _("Ancestral filters")
    description = _("Matches people that are ancestors of a specified person")

    def prepare(self,db):
        """Assume that if 'Inclusive' not defined, assume inclusive"""
        self.db = db
        self.map = {}
        try:
            if int(self.list[1]):
                first = 0
            else:
                first = 1
        except IndexError:
            first = 1
        try:
            root_person = db.get_person_from_gramps_id(self.list[0])
            self.init_ancestor_list(db,root_person,first)
        except:
            pass

    def reset(self):
        self.map = {}

    def apply(self,db,person):
        return self.map.has_key(person.handle)

    def init_ancestor_list(self,db,person,first):
        if not person:
            return
        if not first:
            self.map[person.handle] = 1
        
        fam_id = person.get_main_parents_family_handle()
        fam = db.get_family_from_handle(fam_id)
        if fam:
            f_id = fam.get_father_handle()
            m_id = fam.get_mother_handle()
        
            if f_id:
                self.init_ancestor_list(db,db.get_person_from_handle(f_id),0)
            if m_id:
                self.init_ancestor_list(db,db.get_person_from_handle(m_id),0)

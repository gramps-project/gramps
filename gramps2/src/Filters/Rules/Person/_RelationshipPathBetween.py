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
# RelationshipPathBetween
#
#-------------------------------------------------------------------------
class RelationshipPathBetween(Rule):
    """Rule that checks for a person that is a descendant of a specified person
    not more than N generations away"""

    labels      = [ _('ID:'), _('ID:') ]
    name        = _("Relationship path between <persons>")
    category    = _('Relationship filters')
    description = _("Matches the ancestors of two persons back "
                    "to a common ancestor, producing the relationship "
                    "path between two persons.")

    def prepare(self,db):
        self.db = db
        self.map = {}
        try:
            root1_handle = db.get_person_from_gramps_id(self.list[0]).get_handle()
            root2_handle = db.get_person_from_gramps_id(self.list[1]).get_handle()
            self.init_list(root1_handle,root2_handle)
        except:
            pass

    def reset(self):
        self.map = {}

    def desc_list(self, handle, map, first):
        if not first:
            map[handle] = 1
        
        p = self.db.get_person_from_handle(handle)
        for fam_id in p.get_family_handle_list():
            fam = self.db.get_family_from_handle(fam_id)
            if fam:
                for child_handle in fam.get_child_handle_list():
                    if child_handle:
                        self.desc_list(child_handle,map,0)
    
    def apply_filter(self,rank,handle,plist,pmap):
        person = self.db.get_person_from_handle(handle)
        if person == None:
            return
        plist.append(person)
        pmap[person.get_handle()] = rank
        
        fam_id = person.get_main_parents_family_handle()
        family = self.db.get_family_from_handle(fam_id)
        if family != None:
            self.apply_filter(rank+1,family.get_father_handle(),plist,pmap)
            self.apply_filter(rank+1,family.get_mother_handle(),plist,pmap)

    def apply(self,db,person):
        return self.map.has_key(person.handle)

    def init_list(self,p1_handle,p2_handle):
        firstMap = {}
        firstList = []
        secondMap = {}
        secondList = []
        common = []
        rank = 9999999

        self.apply_filter(0,p1_handle,firstList,firstMap)
        self.apply_filter(0,p2_handle,secondList,secondMap)
        
        for person_handle in firstList:
            if person_handle in secondList:
                new_rank = firstMap[person_handle]
                if new_rank < rank:
                    rank = new_rank
                    common = [ person_handle ]
                elif new_rank == rank:
                    common.append(person_handle)

        path1 = { p1_handle : 1}
        path2 = { p2_handle : 1}

        for person_handle in common:
            new_map = {}
            self.desc_list(person_handle,new_map,1)
            self.get_intersection(path1,firstMap,new_map)
            self.get_intersection(path2,secondMap,new_map)

        for e in path1:
            self.map[e] = 1
        for e in path2:
            self.map[e] = 1
        for e in common:
            self.map[e] = 1

    def get_intersection(self,target, map1, map2):
        for e in map1.keys():
            if map2.has_key(e):
                target[e] = map2[e]

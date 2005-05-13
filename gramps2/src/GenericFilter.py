#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2005  Donald N. Allingham
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

"""Generic Filtering Routines"""

__author__ = "Don Allingham"

#-------------------------------------------------------------------------
#
# Try to abstract SAX1 from SAX2
#
#-------------------------------------------------------------------------
from xml.sax import make_parser,handler,SAXParseException

#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
import os
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# gtk
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import const
import RelLib
import Date
import DateHandler
import NameDisplay
from TransTable import TransTable
from Utils import for_each_ancestor,probably_alive,get_source_referents

#-------------------------------------------------------------------------
#
# date_cmp
#
#-------------------------------------------------------------------------
def date_cmp(rule,value):
    sd = rule.get_start_date()
    s = rule.get_modifier()
    od = value.get_start_date()
    cmp_rule = (sd[2],sd[1],sd[0])
    cmp_value = (od[2],od[1],od[0])
    if s == Date.MOD_BEFORE:
        return  cmp_rule > cmp_value
    elif s == Date.MOD_AFTER:
        return cmp_rule < cmp_value
    else:
        return cmp_rule == cmp_value

#-------------------------------------------------------------------------
#
# Rule
#
#-------------------------------------------------------------------------
class Rule:
    """Base rule class"""

    labels = []
    
    def __init__(self,list):
        self.set_list(list)
    
    def prepare(self,db):
        pass

    def reset(self):
        pass

    def set_list(self,list):
        assert type(list) == type([]) or list == None, "Argument is not a list"
        self.list = list

    def values(self):
        return self.list

    def trans_name(self):
        return _(self.name())
    
    def name(self): 
        return 'None'

    def category(self): 
        return _('Miscellaneous filters')
    
    def description(self):
        return _('No description')

    def check(self):
        return len(self.list) == len(self.labels)

    def apply(self,db,p):
        return 1

    def display_values(self):
        v = []
        for i in range(0,len(self.list)):
            if self.list[i]:
                v.append('%s="%s"' % (_(self.labels[i]),_(self.list[i])))
        return ';'.join(v)

#-------------------------------------------------------------------------
#
# Everyone
#
#-------------------------------------------------------------------------
class Everyone(Rule):
    """Matches Everyone"""

    labels = []
    
    def name(self):
        return 'Everyone'

    def category(self): 
        return _('General filters')
    
    def description(self):
        return _('Matches everyone in the database')

    def apply(self,db,p_id):
        return 1

#-------------------------------------------------------------------------
#
# Disconnected
#
#-------------------------------------------------------------------------
class Disconnected(Rule):
    """Matches disconnected individuals"""

    labels = []
    
    def name(self):
        return 'Disconnected individuals'

    def category(self): 
        return _('General filters')
    
    def description(self):
        return _('Matches individuals that have no relationships')

    def apply(self,db,p_id):
        person = db.get_person_from_handle(p_id)
        return (not person.get_main_parents_family_handle() and
                not len(person.get_family_handle_list()))

#-------------------------------------------------------------------------
#
# RelationshipPathBetween
#
#-------------------------------------------------------------------------
class RelationshipPathBetween(Rule):
    """Rule that checks for a person that is a descendant of a specified person
    not more than N generations away"""

    labels = [ _('ID:'), _('ID:') ]
    
    def prepare(self,db):
        self.db = db
        self.map = {}
        root1 = self.list[0]
        root2 = self.list[1]
        self.init_list(root1,root2)

    def reset(self):
        self.map = {}

    def name(self):
        return "Relationship path between two people"

    def category(self): 
        return _('Relationship filters')

    def description(self):
        return _("Matches the ancestors of two people back to a common ancestor, producing "
                 "the relationship path between two people.")

    def desc_list(self, p_id, map, first):
        if not first:
            map[p_id] = 1
        
        p = self.db.get_person_from_handle(p_id)
        for fam_id in p.get_family_handle_list():
            fam = self.db.get_family_from_handle(fam_id)
            if fam:
                for child_handle in fam.get_child_handle_list():
                    if child_handle:
                        self.desc_list(child_handle,map,0)
    
    def apply_filter(self,rank,p_id,plist,pmap):
        person = self.db.get_person_from_handle(p_id)
        if person == None:
            return
        plist.append(person)
        pmap[person.get_handle()] = rank
        
        fam_id = person.get_main_parents_family_handle()
        family = self.db.get_family_from_handle(fam_id)
        if family != None:
            self.apply_filter(rank+1,family.get_father_handle(),plist,pmap)
            self.apply_filter(rank+1,family.get_mother_handle(),plist,pmap)

    def apply(self,db,p_id):
        return self.map.has_key(p_id)

    def init_list(self,p1_id,p2_id):
        firstMap = {}
        firstList = []
        secondMap = {}
        secondList = []
        common = []
        rank = 9999999

        self.apply_filter(0,p1_id,firstList,firstMap)
        self.apply_filter(0,p2_id,secondList,secondMap)
        
        for person_handle in firstList:
            if person_handle in secondList:
                new_rank = firstMap[person_handle]
                if new_rank < rank:
                    rank = new_rank
                    common = [ person_handle ]
                elif new_rank == rank:
                    common.append(person_handle)

        path1 = { p1_id : 1}
        path2 = { p2_id : 1}

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
        
#-------------------------------------------------------------------------
#
# HasIdOf
#
#-------------------------------------------------------------------------
class HasIdOf(Rule):
    """Rule that checks for a person with a specific GRAMPS ID"""

    labels = [ _('ID:') ]
    
    def name(self):
        return 'Has the Id'

    def description(self):
        return _("Matches the person with a specified GRAMPS ID")

    def category(self):
        return _('General filters')

    def apply(self,db,p_id):
        return p_id == self.list[0]

#-------------------------------------------------------------------------
#
# HasIdOf
#
#-------------------------------------------------------------------------
class IsDefaultPerson(Rule):
    """Rule that checks for a default person in the database"""

    labels = []
    
    def name(self):
        return 'Is default person'

    def description(self):
        return _("Matches the default person")

    def category(self):
        return _('General filters')

    def apply(self,db,p_id):
        person = db.get_default_person()
        if person:
            return p_id == person.get_handle()
        return 0

#-------------------------------------------------------------------------
#
# IsBookmarked
#
#-------------------------------------------------------------------------
class IsBookmarked(Rule):
    """Rule that checks for the bookmark list in the database"""

    labels = []
    
    def name(self):
        return 'Is bookmarked person'

    def description(self):
        return _("Matches the people on the bookmark list")

    def category(self):
        return _('General filters')

    def apply(self,db,p_id):
        if p_id in db.get_bookmarks():
           return 1
        return 0

#-------------------------------------------------------------------------
#
# HasCompleteRecord
#
#-------------------------------------------------------------------------
class HasCompleteRecord(Rule):
    """Rule that checks for a person whose record is complete"""

    labels = []
    
    def name(self):
        return 'Has complete record'

    def category(self): 
        return _('General filters')
    
    def description(self):
        return _('Matches all people whose records are complete')

    def apply(self,db,p_id):
        return db.get_person_from_handle(p_id).get_complete_flag() == 1

#-------------------------------------------------------------------------
#
# IsFemale
#
#-------------------------------------------------------------------------
class IsFemale(Rule):
    """Rule that checks for a person that is a female"""

    labels = []
    
    def name(self):
        return 'Is a female'

    def category(self): 
        return _('General filters')
    
    def description(self):
        return _('Matches all females')

    def apply(self,db,p_id):
        return db.get_person_from_handle(p_id).get_gender() == RelLib.Person.FEMALE

#-------------------------------------------------------------------------
#
# IsDescendantOf
#
#-------------------------------------------------------------------------
class IsDescendantOf(Rule):
    """Rule that checks for a person that is a descendant
    of a specified person"""

    labels = [ _('ID:'), _('Inclusive:') ]
    
    def prepare(self,db):
        self.db = db
        self.map = {}
        self.db = db
        try:
            if int(self.list[1]):
                first = 0
            else:
                first = 1
        except IndexError:
            first = 1

        root_id = self.list[0]
        self.init_list(root_id,first)

    def reset(self):
        self.map = {}

    def name(self):
        return 'Is a descendant of'

    def category(self): 
        return _('Descendant filters')
    
    def description(self):
        return _('Matches all descendants for the specified person')

    def apply(self,db,p_id):
        return self.map.has_key(p_id)

    def init_list(self,p_id,first):
        if not p_id:
            return
        if not first:
            self.map[p_id] = 1
        
        p = self.db.get_person_from_handle(p_id)
        for fam_id in p.get_family_handle_list():
            fam = self.db.get_family_from_handle(fam_id)
            if fam:
                for child_handle in fam.get_child_handle_list():
                    self.init_list(child_handle,0)

#-------------------------------------------------------------------------
#
# IsDescendantOfFilterMatch
#
#-------------------------------------------------------------------------
class IsDescendantOfFilterMatch(IsDescendantOf):
    """Rule that checks for a person that is a descendant
    of someone matched by a filter"""

    labels = [ _('Filter name:'), _('Inclusive:') ]

    def __init__(self,list):
        IsDescendantOf.__init__(self,list)

    def name(self):
        return 'Is a descendant of filter match'

    def category(self): 
        return _('Descendant filters')

    def description(self):
        return _("Matches people that are descendants of someone matched by a filter")
    
    def apply(self,db,p_id):
        return self.map.has_key(p_id)

#-------------------------------------------------------------------------
#
# IsLessThanNthGenerationDescendantOf
#
#-------------------------------------------------------------------------
class IsLessThanNthGenerationDescendantOf(Rule):
    """Rule that checks for a person that is a descendant of a specified person
    not more than N generations away"""

    labels = [ _('ID:'), _('Number of generations:') ]
    
    def prepare(self,db):
        self.db = db
        self.map = {}
        root_id = self.list[0]
        self.init_list(root_id,0)

    def reset(self):
        self.map = {}

    def name(self):
        return 'Is a descendant of person not more than N generations away'

    def category(self): 
        return _('Descendant filters')

    def description(self):
        return _("Matches people that are descendants of a specified person "
                 "not more than N generations away")
    
    def apply(self,db,p_id):
        return self.map.has_key(p_id)

    def init_list(self,p_id,gen):
        if not p_id:
            return
        if gen:
            self.map[p_id] = 1
            if gen >= int(self.list[1]):
                return

        p = self.db.get_person_from_handle(p_id)
        for fam_id in p.get_family_handle_list():
            fam = self.db.get_family_from_handle(fam_id)
            for child_handle in fam.get_child_handle_list():
                self.init_list(child_handle,gen+1)

#-------------------------------------------------------------------------
#
# IsMoreThanNthGenerationDescendantOf
#
#-------------------------------------------------------------------------
class IsMoreThanNthGenerationDescendantOf(Rule):
    """Rule that checks for a person that is a descendant of a specified person
    at least N generations away"""

    labels = [ _('ID:'), _('Number of generations:') ]
    
    def prepare(self,db):
        self.db = db
        self.map = {}
        root_id = self.list[0]
        self.init_list(root_id,0)

    def reset(self):
        self.map = {}

    def name(self):
        return 'Is a descendant of person at least N generations away'

    def description(self):
        return _("Matches people that are descendants of a specified "
                 "person at least N generations away")
    
    def category(self):
        return _("Descendant filters")

    def apply(self,db,p_id):
        return self.map.has_key(p_id)

    def init_list(self,p_id,gen):
        if not p_id:
            return
        if gen >= int(self.list[1]):
            self.map[p_id] = 1

        p = self.db.get_person_from_handle(p_id)
        for fam_id in p.get_family_handle_list():
            fam = self.db.get_family_from_handle(fam_id)
            for child_handle in fam.get_child_handle_list():
                self.init_list(child_handle,gen+1)

#-------------------------------------------------------------------------
#
# IsChildOfFilterMatch
#
#-------------------------------------------------------------------------
class IsChildOfFilterMatch(Rule):
    """Rule that checks for a person that is a child
    of someone matched by a filter"""

    labels = [ _('Filter name:') ]

    def prepare(self,db):
        self.db = db
        self.map = {}
        filt = MatchesFilter(self.list)
        filt.prepare(db)
        for person_handle in db.get_person_handles(sort_handles=False):
            if filt.apply (db, person_handle):
                self.init_list (person_handle)
        filt.reset()

    def reset(self):
        self.map = {}

    def name(self):
        return 'Is a child of filter match'

    def description(self):
        return _("Matches the person that is a child of someone matched by a filter")

    def category(self):
        return _('Family filters')

    def apply(self,db,p_id):
        return self.map.has_key(p_id)

    def init_list(self,p_id):
        if not p_id:
            return
        p = self.db.get_person_from_handle(p_id)
        for fam_id in p.get_family_handle_list():
            fam = self.db.get_family_from_handle(fam_id)
            for child_handle in fam.get_child_handle_list():
                self.map[child_handle] = 1

#-------------------------------------------------------------------------
#
# IsSiblingOfFilterMatch
#
#-------------------------------------------------------------------------
class IsSiblingOfFilterMatch(Rule):
    """Rule that checks for a person that is a sibling
    of someone matched by a filter"""

    labels = [ _('Filter name:') ]

    def prepare(self,db):
        self.db = db
        self.map = {}
        filt = MatchesFilter(self.list)
        filt.prepare(db)
        for person_handle in db.get_person_handles(sort_handles=False):
            if filt.apply (db, person_handle):
                self.init_list (person_handle)
        filt.reset()

    def reset(self):
        self.map = {}

    def name(self):
        return 'Is a sibling of filter match'

    def description(self):
        return _("Matches the person that is a sibling of someone matched by a filter")

    def category(self):
        return _('Family filters')

    def apply(self,db,p_id):
        return self.map.has_key(p_id)

    def init_list(self,p_id):
        if not p_id:
            return
        p = self.db.get_person_from_handle(p_id)
        fam_id = p.get_main_parents_family_handle()
        fam = self.db.get_family_from_handle(fam_id)
        if fam:
            for child_handle in fam.get_child_handle_list():
                self.map[child_handle] = 1

#-------------------------------------------------------------------------
#
# IsDescendantFamilyOf
#
#-------------------------------------------------------------------------
class IsDescendantFamilyOf(Rule):
    """Rule that checks for a person that is a descendant or the spouse
    of a descendant of a specified person"""

    labels = [ _('ID:') ]
    
    def name(self):
        return "Is a descendant family member of"

    def category(self): 
        return _('Descendant filters')

    def description(self):
        return _("Matches people that are descendants or the spouse "
                 "of a descendant of a specified person")
    
    def apply(self,db,p_id):
        self.map = {}
        self.orig_id = p_id
        self.db = db
        return self.search(p_id,1)

    def search(self,p_id,val):
        if p_id == self.list[0]:
            self.map[p_id] = 1
            return 1
        
        p = self.db.get_person_from_handle(p_id)
        for (f,r1,r2) in p.get_parent_family_handle_list():
            family = self.db.get_family_from_handle(f)
            for person_handle in [family.get_mother_handle(),family.get_father_handle()]:
                if person_handle:
                    if self.search(person_handle,0):
                        return 1
        if val:
            for family_handle in p.get_family_handle_list():
                family = self.db.get_family_from_handle(family_handle)
                if p_id == family.get_father_handle():
                    spouse_id = family.get_mother_handle()
                else:
                    spouse_id = family.get_father_handle()
                if spouse_id:
                    if self.search(spouse_id,0):
                        return 1
        return 0

#-------------------------------------------------------------------------
#
# IsAncestorOf
#
#-------------------------------------------------------------------------
class IsAncestorOf(Rule):
    """Rule that checks for a person that is an ancestor of a specified person"""

    labels = [ _('ID:'), _('Inclusive:') ]

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
        root_id = self.list[0]
        self.init_ancestor_list(db,root_id,first)

    def reset(self):
        self.map = {}
    
    def name(self):
        return 'Is an ancestor of'

    def description(self):
        return _("Matches people that are ancestors of a specified person")
    
    def category(self):
        return _("Ancestral filters")

    def apply(self,db,p_id):
        return self.map.has_key(p_id)

    def init_ancestor_list(self,db,p_id,first):
        if not p_id:
            return
        if not first:
            self.map[p_id] = 1
        
        p = db.get_person_from_handle(p_id)
        fam_id = p.get_main_parents_family_handle()
        fam = db.get_family_from_handle(fam_id)
        if fam:
            f_id = fam.get_father_handle()
            m_id = fam.get_mother_handle()
        
            if f_id:
                self.init_ancestor_list(db,f_id,0)
            if m_id:
                self.init_ancestor_list(db,m_id,0)

#-------------------------------------------------------------------------
#
# IsAncestorOfFilterMatch
#
#-------------------------------------------------------------------------
class IsAncestorOfFilterMatch(IsAncestorOf):
    """Rule that checks for a person that is an ancestor of
    someone matched by a filter"""

    labels = [ _('Filter name:'), _('Inclusive:') ]

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
            
        filt = MatchesFilter(self.list)
        filt.prepare(db)
        for person_handle in db.get_person_handles(sort_handles=False):
            if filt.apply (db, person_handle):
                self.init_ancestor_list (db,person_handle,first)
        filt.reset()

    def reset(self):
        self.map = {}

    def name(self):
        return 'Is an ancestor of filter match'

    def description(self):
        return _("Matches people that are ancestors "
            "of someone matched by a filter")
    
    def category(self):
        return _("Ancestral filters")

    def apply(self,db,p_id):
        return self.map.has_key(p_id)

#-------------------------------------------------------------------------
#
# IsLessThanNthGenerationAncestorOf
#
#-------------------------------------------------------------------------
class IsLessThanNthGenerationAncestorOf(Rule):
    """Rule that checks for a person that is an ancestor of a specified person
    not more than N generations away"""

    labels = [ _('ID:'), _('Number of generations:') ]

    def prepare(self,db):
        self.db = db
        self.map = {}
        root_id = self.list[0]
        self.init_ancestor_list(root_id,0)

    def reset(self):
        self.map = {}
    
    def name(self):
        return 'Is an ancestor of person not more than N generations away'

    def description(self):
        return _("Matches people that are ancestors "
            "of a specified person not more than N generations away")
    
    def category(self):
        return _("Ancestral filters")

    def apply(self,db,p_id):
        return self.map.has_key(p_id)

    def init_ancestor_list(self,p_id,gen):
#        if self.map.has_key(p.get_handle()) == 1:
#            loop_error(self.orig,p)
        if not p_id:
            return
        if gen:
            self.map[p_id] = 1
            if gen >= int(self.list[1]):
                return
        
        p = self.db.get_person_from_handle(p_id)
        fam_id = p.get_main_parents_family_handle()
        fam = self.db.get_family_from_handle(fam_id)
        if fam:
            f_id = fam.get_father_handle()
            m_id = fam.get_mother_handle()
        
            if f_id:
                self.init_ancestor_list(f_id,gen+1)
            if m_id:
                self.init_ancestor_list(m_id,gen+1)

#-------------------------------------------------------------------------
#
# IsMoreThanNthGenerationAncestorOf
#
#-------------------------------------------------------------------------
class IsMoreThanNthGenerationAncestorOf(Rule):
    """Rule that checks for a person that is an ancestor of a specified person
    at least N generations away"""

    labels = [ _('ID:'), _('Number of generations:') ]

    def prepare(self,db):
        self.db = db
        self.map = {}
        root_id = self.list[0]
        self.init_ancestor_list(root_id,0)

    def reset(self):
        self.map = []
    
    def name(self):
        return 'Is an ancestor of person at least N generations away'

    def description(self):
        return _("Matches people that are ancestors "
            "of a specified person at least N generations away")
    
    def category(self):
        return _("Ancestral filters")

    def apply(self,db,p_id):
        return self.map.has_key(p_id)

    def init_ancestor_list(self,p_id,gen):
#        if self.map.has_key(p.get_handle()) == 1:
#            loop_error(self.orig,p)
        if not p_id:
            return
        if gen >= int(self.list[1]):
            self.map[p_id] = 1
        
        p = self.db.get_person_from_handle(p_id)
        fam_id = p.get_main_parents_family_handle()
        fam = self.db.get_family_from_handle(fam_id)
        if fam:
            f_id = fam.get_father_handle()
            m_id = fam.get_mother_handle()
        
            if f_id:
                self.init_ancestor_list(f_id,gen+1)
            if m_id:
                self.init_ancestor_list(m_id,gen+1)

#-------------------------------------------------------------------------
#
# IsParentOfFilterMatch
#
#-------------------------------------------------------------------------
class IsParentOfFilterMatch(Rule):
    """Rule that checks for a person that is a parent
    of someone matched by a filter"""

    labels = [ _('Filter name:') ]

    def prepare(self,db):
        self.db = db
        self.map = {}
        filt = MatchesFilter(self.list)
        filt.prepare(db)
        for person_handle in db.get_person_handles(sort_handles=False):
            if filt.apply (db, person_handle):
                self.init_list (person_handle)
        filt.reset()

    def reset(self):
        self.map = {}

    def name(self):
        return 'Is a parent of filter match'

    def description(self):
        return _("Matches the person that is a parent of someone matched by a filter")

    def category(self):
        return _('Family filters')

    def apply(self,db,p_id):
        return self.map.has_key(p_id)

    def init_list(self,p_id):
        p = self.db.get_person_from_handle(p_id)
        for fam_id,frel,mrel in p.get_parent_family_handle_list():
            fam = self.db.get_family_from_handle(fam_id)
            for parent_id in [fam.get_father_handle (), fam.get_mother_handle ()]:
                if parent_id:
                    self.map[parent_id] = 1

#-------------------------------------------------------------------------
#
# HasCommonAncestorWith
#
#-------------------------------------------------------------------------
class HasCommonAncestorWith(Rule):
    """Rule that checks for a person that has a common ancestor with a specified person"""

    labels = [ _('ID:') ]

    def name(self):
        return 'Has a common ancestor with'

    def description(self):
        return _("Matches people that have a common ancestor "
            "with a specified person")
    
    def category(self):
        return _("Ancestral filters")

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
        p_id = self.list[0]
        if p_id:
            def init(self,pid): self.ancestor_cache[pid] = 1
            for_each_ancestor(db,[p_id],init,self)

    def apply(self,db,p_id):
        # On the first call, we build the ancestor cache for the
        # reference person.   Then, for each person to test,
        # we browse his ancestors until we found one in the cache.
        if len(self.ancestor_cache) == 0:
            self.init_ancestor_cache(db)
        return for_each_ancestor(db,[p_id],
                                 lambda self,p_id: self.ancestor_cache.has_key(p_id),
                                 self);

#-------------------------------------------------------------------------
#
# HasCommonAncestorWithFilterMatch
#
#-------------------------------------------------------------------------
class HasCommonAncestorWithFilterMatch(HasCommonAncestorWith):
    """Rule that checks for a person that has a common ancestor with
    someone matching a filter"""

    labels = [ _('Filter name:') ]

    def name(self):
        return 'Has a common ancestor with filter match'

    def description(self):
        return _("Matches people that have a common ancestor "
            "with someone matched by a filter")
    
    def category(self):
        return _("Ancestral filters")

    def __init__(self,list):
        HasCommonAncestorWith.__init__(self,list)

    def init_ancestor_cache(self,db):
        filt = MatchesFilter(self.list)
        filt.prepare(db)
        def init(self,pid): self.ancestor_cache[pid] = 1
        for p_id in db.get_person_handles(sort_handles=False):
            if (not self.ancestor_cache.has_key (p_id)
                and filt.apply (db, p_id)):
                for_each_ancestor(db,[p_id],init,self)
        filt.reset()

#-------------------------------------------------------------------------
#
# IsMale
#
#-------------------------------------------------------------------------
class IsMale(Rule):
    """Rule that checks for a person that is a male"""

    labels = []
    
    def name(self):
        return 'Is a male'

    def category(self): 
        return _('General filters')
    
    def description(self):
        return _('Matches all males')

    def apply(self,db,p_id):
        return db.get_person_from_handle(p_id).get_gender() == RelLib.Person.MALE

#-------------------------------------------------------------------------
#
# HasEvent
#
#-------------------------------------------------------------------------
class HasEvent(Rule):
    """Rule that checks for a person with a particular value"""

    labels = [ _('Personal event:'), _('Date:'), _('Place:'), _('Description:') ]
    
    def __init__(self,list):
        Rule.__init__(self,list)
        if self.list and self.list[1]:
            self.date = DateHandler.parser.parse(self.list[1])
        else:
            self.date = None

    def name(self):
        return 'Has the personal event'

    def description(self):
        return _("Matches the person with a personal event of a particular value")

    def category(self):
        return _('Event filters')

    def apply(self,db,p_id):
        p = db.get_person_from_handle(p_id)
        for event_handle in p.get_event_list():
            if not event_handle:
                continue
            event = db.get_event_from_handle(event_handle)
            val = 1
            if self.list[0] and event.get_name() != self.list[0]:
                val = 0
            if self.list[3] and event.get_description().upper().find(
                                            self.list[3].upper())==-1:
                val = 0
            if self.date:
                if date_cmp(self.date,event.get_date_object()):
                    val = 0
            if self.list[2]:
                pl_id = event.get_place_handle()
                if pl_id:
                    pl = db.get_place_from_handle(pl_id)
                    pn = pl.get_title()
                    if pn.upper().find(self.list[2].upper()) == -1:
                        val = 0
            if val == 1:
                return 1
        return 0

#-------------------------------------------------------------------------
#
# HasFamilyEvent
#
#-------------------------------------------------------------------------
class HasFamilyEvent(Rule):
    """Rule that checks for a person who has a relationship event
    with a particular value"""

    labels = [ _('Family event:'), _('Date:'), _('Place:'), _('Description:') ]
    
    def __init__(self,list):
        Rule.__init__(self,list)
        if self.list and self.list[1]:
            self.date = DateHandler.parser.parse(self.list[1])
        else:
            self.date = None

    def name(self):
        return 'Has the family event'

    def description(self):
        return _("Matches the person with a family event of a particular value")

    def category(self):
        return _('Event filters')

    def apply(self,db,p_id):
        p = db.get_person_from_handle(p_id)
        for f_id in p.get_family_handle_list():
            f = db.get_family_from_handle(f_id)
            for event_handle in f.get_event_list():
                if not event_handle:
                    continue
                event = db.get_event_from_handle(event_handle)
                val = 1
                if self.list[0] and event.get_name() != self.list[0]:
                    val = 0
                v = self.list[3]
                if v and event.get_description().upper().find(v.upper())==-1:
                    val = 0
                if self.date:
                    if date_cmp(self.date,event.get_date_object()):
                        val = 0
                pl_id = event.get_place_handle()
                if pl_id:
                    pl = db.get_place_from_handle(pl_id)
                    pn = pl.get_title()
                    if self.list[2] and pn.find(self.list[2].upper()) == -1:
                        val = 0
                if val == 1:
                    return 1
        return 0

#-------------------------------------------------------------------------
#
# HasRelationship
#
#-------------------------------------------------------------------------
class HasRelationship(Rule):
    """Rule that checks for a person who has a particular relationship"""

    labels = [ _('Number of relationships:'),
               _('Relationship type:'),
               _('Number of children:') ]

    def name(self):
        return 'Has the relationships'

    def description(self):
        return _("Matches the person who has a particular relationship")

    def category(self):
        return _('Family filters')

    def apply(self,db,p_id):
        rel_type = 0
        cnt = 0
        p = db.get_person_from_handle(p_id)
        num_rel = len(p.get_family_handle_list())

        # count children and look for a relationship type match
        for f_id in p.get_family_handle_list():
            f = db.get_family_from_handle(f_id)
            cnt = cnt + len(f.get_child_handle_list())
            if self.list[1]  and int(self.list[1]) == f.get_relationship():
                rel_type = 1

        # if number of relations specified
        if self.list[0]:
            try:
                v = int(self.list[0])
            except:
                return 0
            if v != num_rel:
                return 0

        # number of childred
        if self.list[2]:
            try:
                v = int(self.list[2])
            except:
                return 0
            if v != cnt:
                return 0

        # relation
        if self.list[1]:
            return rel_type == 1
        else:
            return 1

#-------------------------------------------------------------------------
#
# HasBirth
#
#-------------------------------------------------------------------------
class HasBirth(Rule):
    """Rule that checks for a person with a birth of a particular value"""

    labels = [ _('Date:'), _('Place:'), _('Description:') ]
    
    def __init__(self,list):
        Rule.__init__(self,list)
        if self.list and self.list[0]:
            self.date = DateHandler.parser.parse(self.list[0])
        else:
            self.date = None
        
    def name(self):
        return 'Has the birth'

    def description(self):
        return _("Matches the person with a birth of a particular value")

    def category(self):
        return _('Event filters')

    def apply(self,db,p_id):
        p = db.get_person_from_handle(p_id)
        event_handle = p.get_birth_handle()
        if not event_handle:
            return False
        event = db.get_event_from_handle(event_handle)
        ed = event.get_description().upper()
        if len(self.list) > 2 and ed.find(self.list[2].upper())==-1:
            return False
        if self.date:
            if date_cmp(self.date,event.get_date_object()) == 0:
                return False
        pl_id = event.get_place_handle()
        if pl_id:
            pl = db.get_place_from_handle(pl_id)
            pn = pl.get_title()
            if len(self.list) > 1 and pn.find(self.list[1].upper()) == -1:
                return False
        return True

#-------------------------------------------------------------------------
#
# HasDeath
#
#-------------------------------------------------------------------------
class HasDeath(Rule):
    """Rule that checks for a person with a death of a particular value"""

    labels = [ _('Date:'), _('Place:'), _('Description:') ]
    
    def __init__(self,list):
        Rule.__init__(self,list)
        if self.list and self.list[0]:
            self.date = DateHandler.parser.parse(self.list[0])
        else:
            self.date = None

    def name(self):
        return 'Has the death'

    def description(self):
        return _("Matches the person with a death of a particular value")

    def category(self):
        return _('Event filters')

    def apply(self,db,p_id):
        p = db.get_person_from_handle(p_id)
        event_handle = p.get_death_handle()
        if not event_handle:
            return 0
        event = db.get_event_from_handle(event_handle)
        ed = event.get_description().upper()
        if self.list[2] and ed.find(self.list[2].upper())==-1:
            return 0
        if self.date:
            if date_cmp(self.date,event.get_date_object()) == 0:
                return 0
        pl_id = event.get_place_handle()
        if pl_id:
            pl = db.get_place_from_handle(pl_id)
            pn = pl.get_title()
            if self.list[1] and pn.find(self.list[1].upper()) == -1:
                return 0
        return 1

#-------------------------------------------------------------------------
#
# HasAttribute
#
#-------------------------------------------------------------------------
class HasAttribute(Rule):
    """Rule that checks for a person with a particular personal attribute"""

    labels = [ _('Personal attribute:'), _('Value:') ]
    
    def name(self):
        return 'Has the personal attribute'

    def apply(self,db,p_id):
        if not self.list[0]:
            return 0
        p = db.get_person_from_handle(p_id)
        for attr in p.get_attribute_list():
            name_match = self.list[0] == attr.get_type()
            value_match = \
                    attr.get_value().upper().find(self.list[1].upper()) != -1
            if name_match and value_match:
                return 1
        return 0

#-------------------------------------------------------------------------
#
# HasFamilyAttribute
#
#-------------------------------------------------------------------------
class HasFamilyAttribute(Rule):
    """Rule that checks for a person with a particular family attribute"""

    labels = [ _('Family attribute:'), _('Value:') ]
    
    def name(self):
        return 'Has the family attribute'

    def apply(self,db,p_id):
        if not self.list[0]:
            return 0
        p = db.get_person_from_handle(p_id)
        for f_id in p.get_family_handle_list():
            f = db.get_family_from_handle(f_id)
            for attr in f.get_attribute_list():
                name_match = self.list[0] == attr.get_type()
                value_match = \
                        attr.get_value().upper().find(self.list[1].upper()) != -1
                if name_match and value_match:
                    return 1
        return 0

#-------------------------------------------------------------------------
#
# HasNameOf
#
#-------------------------------------------------------------------------
class HasNameOf(Rule):
    """Rule that checks for full or partial name matches"""

    labels = [_('Given name:'),_('Family name:'),_('Suffix:'),_('Title:')]
    
    def name(self):
        return 'Has a name'
    
    def description(self):
        return _("Matches the person with a specified (partial) name")

    def category(self):
        return _('General filters')

    def apply(self,db,p_id):
        self.f = self.list[0]
        self.l = self.list[1]
        self.s = self.list[2]
        self.t = self.list[3]
        p = db.get_person_from_handle(p_id)
        for name in [p.get_primary_name()] + p.get_alternate_names():
            val = 1
            if self.f and name.get_first_name().upper().find(self.f.upper()) == -1:
                val = 0
            if self.l and name.get_surname().upper().find(self.l.upper()) == -1:
                val = 0
            if self.s and name.get_suffix().upper().find(self.s.upper()) == -1:
                val = 0
            if self.t and name.get_title().upper().find(self.t.upper()) == -1:
                val = 0
            if val == 1:
                return 1
        return 0

#-------------------------------------------------------------------------
#
# HasNameOf
#
#-------------------------------------------------------------------------
class SearchName(Rule):
    """Rule that checks for full or partial name matches"""

    labels = [_('Substring:')]
    
    def name(self):
        return 'Matches name'
    
    def description(self):
        return _("Matches the person with a specified (partial) name")

    def category(self):
        return _('General filters')

    def apply(self,db,p_id):
        self.f = self.list[0]
        p = db.get_person_from_handle(p_id)
        n = NameDisplay.displayer.display(p)
        return self.f and n.upper().find(self.f.upper()) != -1
    
#-------------------------------------------------------------------------
#
# IncompleteNames
#
#-------------------------------------------------------------------------
class IncompleteNames(Rule):
    """People with incomplete names"""

    labels = []
    
    def name(self):
        return 'People with incomplete names'
    
    def description(self):
        return _("Matches people with firstname or lastname missing")

    def category(self):
        return _('General filters')

    def apply(self,db,p_id):
        p = db.get_person_from_handle(p_id)
        for name in [p.get_primary_name()] + p.get_alternate_names():
            if name.get_first_name() == "":
                return 1
            if name.get_surname() == "":
                return 1
        return 0

#-------------------------------------------------------------------------
#
# MatchesFilter
#
#-------------------------------------------------------------------------
class MatchesFilter(Rule):
    """Rule that checks against another filter"""

    labels = [_('Filter name:')]

    def prepare(self,db):
        for filt in SystemFilters.get_filters():
            if filt.get_name() == self.list[0]:
                for rule in filt.flist:
                    rule.prepare(db)
        for filt in CustomFilters.get_filters():
            if filt.get_name() == self.list[0]:
                for rule in filt.flist:
                    rule.prepare(db)

    def reset(self):
        for filt in SystemFilters.get_filters():
            if filt.get_name() == self.list[0]:
                for rule in filt.flist:
                    rule.reset()
        for filt in CustomFilters.get_filters():
            if filt.get_name() == self.list[0]:
                for rule in filt.flist:
                    rule.reset()

    def name(self):
        return 'Matches the filter named'

    def apply(self,db,p_id):
        for filt in SystemFilters.get_filters():
            if filt.get_name() == self.list[0]:
                return filt.check(p_id)
        for filt in CustomFilters.get_filters():
            if filt.get_name() == self.list[0]:
                return filt.check(db,p_id)
        return 0

#-------------------------------------------------------------------------
#
# IsSpouseOfFilterMatch
#
#-------------------------------------------------------------------------
class IsSpouseOfFilterMatch(Rule):
    """Rule that checks for a person married to someone matching
    a filter"""

    labels = [_('Filter name:')]

    def name(self):
        return 'Is spouse of filter match'

    def description(self):
        return _("Matches the person married to someone matching a filter")

    def category(self):
        return _('Family filters')

    def apply(self,db,p_id):
        filt = MatchesFilter (self.list)
        p = db.get_person_from_handle(p_id)
        for family_handle in p.get_family_handle_list ():
            family = db.get_family_from_handle(family_handle)
            for spouse_id in [family.get_father_handle (), family.get_mother_handle ()]:
                if not spouse_id:
                    continue
                if spouse_id == p_id:
                    continue
                if filt.apply (db, spouse_id):
                    return 1
        return 0

#-------------------------------------------------------------------------
# "People who were adopted"
#-------------------------------------------------------------------------


class HaveAltFamilies(Rule):
    """People who were adopted"""

    labels = []

    def name(self):
        return 'People who were adopted'

    def description(self):
        return _("Matches person who were adopted")

    def category(self):
        return _('Family filters')


    def apply(self,db,p_id):
        p = db.get_person_from_handle(p_id)
        for (fam,rel1,rel2) in p.get_parent_family_handle_list():
            if rel1 == RelLib.Person.CHILD_REL_ADOPT or rel2 == RelLib.Person.CHILD_REL_ADOPT:
                return 1
        return 0


#-------------------------------------------------------------------------
# "People who have images"
#-------------------------------------------------------------------------


class HavePhotos(Rule):
    """People who have images"""

    labels = []

    def name(self):
        return 'People who have images'

    def description(self):
        return _("Matches person who have images in the gallery")

    def category(self):
        return _('General filters')


    def apply(self,db,p_id):
        p = db.get_person_from_handle(p_id)
        return len( p.get_media_list()) > 0

#-------------------------------------------------------------------------
# "People with children"
#-------------------------------------------------------------------------


class HaveChildren(Rule):
    """People with children"""

    labels = []

    def name(self):
        return 'People with children'

    def description(self):
        return _("Matches persons who have children")

    def category(self):
        return _('Family filters')


    def apply(self,db,p_id):
        p = db.get_person_from_handle(p_id)
        for family_handle in p.get_family_handle_list():
            family = db.get_family_from_handle(family_handle)
            return len(family.get_child_handle_list()) > 0

#-------------------------------------------------------------------------
# "People with no marriage records"
#-------------------------------------------------------------------------


class NeverMarried(Rule):
    """People with no marriage records"""

    labels = []

    def name(self):
        return 'People with no marriage records'

    def description(self):
        return _("Matches persons who have have no spouse")

    def category(self):
        return _('Family filters')


    def apply(self,db,p_id):
        p = db.get_person_from_handle(p_id)
        return len(p.get_family_handle_list()) == 0

#-------------------------------------------------------------------------
# "People with multiple marriage records"
#-------------------------------------------------------------------------


class MultipleMarriages(Rule):
    """People with multiple marriage records"""

    labels = []

    def name(self):
        return 'People with multiple marriage records'

    def description(self):
        return _("Matches persons who have more than one spouse")

    def category(self):
        return _('Family filters')


    def apply(self,db,p_id):
        p = db.get_person_from_handle(p_id)
        return len(p.get_family_handle_list()) > 1

#-------------------------------------------------------------------------
# "People without a birth date"
#-------------------------------------------------------------------------


class NoBirthdate(Rule):
    """People without a birth date"""

    labels = []

    def name(self):
        return 'People without a birth date'

    def description(self):
        return _("Matches persons without a birthdate")

    def category(self):
        return _('General filters')


    def apply(self,db,p_id):
        p = db.get_person_from_handle(p_id)
        birth_handle = p.get_birth_handle()
        if not birth_handle:
            return 1
        birth = db.get_event_from_handle(birth_handle)
        if not birth.get_date_object():
            return 1
        return 0

#-------------------------------------------------------------------------
# "People with incomplete events"
#-------------------------------------------------------------------------


class PersonWithIncompleteEvent(Rule):
    """People with incomplete events"""

    labels = []

    def name(self):
        return 'People with incomplete events'

    def description(self):
        return _("Matches persons with missing date or place in an event")

    def category(self):
        return _('Event filters')


    def apply(self,db,p_id):
        p = db.get_person_from_handle(p_id)
        for event_handle in p.get_event_list() + [p.get_birth_handle(), p.get_death_handle()]:
            event = db.get_event_from_handle(event_handle)
            if event:
                if not event.get_place_handle():
                    return 1
                if not event.get_date_object():
                    return 1
        return 0

#-------------------------------------------------------------------------
# "Families with incomplete events"
#-------------------------------------------------------------------------


class FamilyWithIncompleteEvent(Rule):
    """Families with incomplete events"""

    labels = []

    def name(self):
        return 'Families with incomplete events'

    def description(self):
        return _("Matches persons with missing date or place in an event of the family")

    def category(self):
        return _('Event filters')


    def apply(self,db,p_id):
        p = db.get_person_from_handle(p_id)
        for family_handle in p.get_family_handle_list():
            family = db.get_family_from_handle(family_handle)
            for event_handle in family.get_event_list():
                event = db.get_event_from_handle(event_handle)
                if event:
                    if not event.get_place_handle():
                        return 1
                    if not event.get_date_object():
                        return 1
        return 0


#-------------------------------------------------------------------------
# "People probably alive"
#-------------------------------------------------------------------------


class ProbablyAlive(Rule):
    """People probably alive"""

    labels = [_("On year:")]

    def prepare(self,db):
        try:
            self.current_year = int(self.list[0])
        except:
            self.current_year = None

    def name(self):
        return 'People probably alive'

    def description(self):
        return _("Matches persons without indications of death that are not too old")

    def category(self):
        return _('General filters')


    def apply(self,db,p_id):
        p = db.get_person_from_handle(p_id)
        return probably_alive(p,db,self.current_year)

#-------------------------------------------------------------------------
# "People marked private"
#-------------------------------------------------------------------------


class PeoplePrivate(Rule):
    """People marked private"""

    labels = []

    def name(self):
        return 'People marked private'

    def description(self):
        return _("Matches persons that are indicated as private")

    def category(self):
        return _('General filters')


    def apply(self,db,p_id):
        p = db.get_person_from_handle(p_id)
        return p.get_privacy()

#-------------------------------------------------------------------------
# "Witnesses"
#-------------------------------------------------------------------------


class IsWitness(Rule):
    """Witnesses"""

    labels = [_('Personal event:'), _('Family event:')]

    def prepare(self,db):
        self.db = db
        self.map = []
        self.build_witness_list()

    def reset(self):
        self.map = []
        
    def name(self):
        return 'Witnesses'

    def description(self):
        return _("Matches persons who are witnesses in an event")

    def category(self):
        return _('Event filters')

    def apply(self,db,p_id):
        return p_id in self.map

    def build_witness_list(self):
        event_type = None
        if self.list and self.list[0]:
            event_type = self.list[0]
        if not self.list or event_type:
            for person_handle in self.db.get_person_handles():
                p = self.db.get_person_from_handle(person_handle)
                self.get_witness_of_events( event_type,
                    p.get_event_list()+[p.get_birth_handle(), p.get_death_handle()])
        event_type = None
        if self.list and self.list[1]:
            event_type = self.list[1]
        if not self.list or event_type:
            for family_handle in self.db.get_family_handles():
                f = self.db.get_family_from_handle(family_handle)
                self.get_witness_of_events(event_type, f.get_event_list())

    def get_witness_of_events(self, event_type, event_list):
        if not event_list:
            return
        for event_handle in event_list:
            event = self.db.get_event_from_handle(event_handle)
            if event:
                if event_type and not event.get_name() == event_type:
                    continue
                wlist = event.get_witness_list()
                if wlist:
                    for w in wlist:
                        if w.get_type() == RelLib.Event.ID:
                            self.map.append(w.get_value())


#-------------------------------------------------------------------------
# "HasTextMatchingSubstringOf"
#-------------------------------------------------------------------------

class HasTextMatchingSubstringOf(Rule):
    """Rule that checks for string matches in any textual information"""

    labels = [_('Substring:'), _('Case sensitive:'), _('Regular-Expression matching:')]

    def prepare(self,db):
        self.db = db
        self.person_map = {}
        self.event_map = {}
        self.source_map = {}
        self.family_map = {}
        self.place_map = {}
        try:
            if int(self.list[1]):
                self.case_sensitive = True
            else:
                self.case_sensitive = False
        except IndexError:
            self.case_sensitive = False
        try:
            if int(self.list[2]):
                self.regexp_match = True
            else:
                self.regexp_match = False
        except IndexError:
            self.regexp_match = False
        self.cache_sources()

    def reset(self):
        self.person_map = {}
        self.event_map = {}
        self.source_map = {}
        self.family_map = {}
        self.place_map = {}

    def name(self):
        return 'Has text matching substring of'
    
    def description(self):
        return _("Matches persons whose records contain text matching a substring")

    def category(self):
        return _('General filters')

    def apply(self,db,p_id):
        if p_id in self.person_map:	# Cached by matching Source?
            return self.person_map[p_id]
        p = db.get_person_from_handle(p_id)
        if self.match_object(p):	# first match the person itself
            return 1
        for event_handle in p.get_event_list()+[p.get_birth_handle(), p.get_death_handle()]:
            if self.search_event(event_handle):	# match referenced events
                return 1
        for family_handle in p.get_family_handle_list(): # match families
            if self.search_family(family_handle):
                return 1
        return 0
    
    def search_family(self,family_handle):
        if not family_handle:
            return 0
        # search inside the family and cache the result to not search a family twice
        if not family_handle in self.family_map:
            match = 0
            family = self.db.get_family_from_handle(family_handle)
            if self.match_object(family):
                match = 1
            else:
                for event_handle in family.get_event_list():
                    if self.search_event(event_handle):
                        match = 1
                        break
            self.family_map[family_handle] = match
        return self.family_map[family_handle]

    def search_event(self,event_handle):
        if not event_handle:
            return 0
        # search inside the event and cache the result (event sharing)
        if not event_handle in self.event_map:
            match = 0
            event = self.db.get_event_from_handle(event_handle)
            if self.match_object(event):
                match = 1
            elif event:
                place_handle = event.get_place_handle()
                if place_handle:
                    if self.search_place(place_handle):
                        match = 1
            self.event_map[event_handle] = match
        return self.event_map[event_handle]

    def search_place(self,place_handle):
        if not place_handle:
            return 0
        # search inside the place and cache the result
        if not place_handle in self.place_map:
            place = self.db.get_place_from_handle(place_handle)
            self.place_map[place_handle] = self.match_object(place)
        return self.place_map[place_handle]

    def cache_sources(self):
        # search all sources and match all referents of a matching source
        for source_handle in self.db.get_source_handles():
            source = self.db.get_source_from_handle(source_handle)
            if self.match_object(source):
                (person_list,family_list,event_list,
                    place_list,source_list,media_list
                    ) = get_source_referents(source_handle,self.db)
                for handle in person_list:
                    self.person_map[handle] = 1
                for handle in family_list:
                    self.family_map[handle] = 1
                for handle in event_list:
                    self.event_map[handle] = 1
                for handle in place_list:
                    self.place_map[handle] = 1

    def match_object(self,obj):
        if not obj:
            return 0
        if self.regexp_match:
            return obj.matches_regexp(self.list[0],self.case_sensitive)
        return obj.matches_string(self.list[0],self.case_sensitive)

#-------------------------------------------------------------------------
# "HasTextMatchingRegexOf"
#-------------------------------------------------------------------------
class HasTextMatchingRegexpOf(HasTextMatchingSubstringOf):
    """This is wrapping HasTextMatchingSubstringOf to enable the regex_match parameter"""
    def __init__(self,list):
        HasTextMatchingSubstringOf.__init__(self,list)

    def prepare(self,db):
        self.db = db
        self.person_map = {}
        self.event_map = {}
        self.source_map = {}
        self.family_map = {}
        self.place_map = {}
        self.case_sensitive = False
        self.regexp_match = True
        self.cache_sources()


#-------------------------------------------------------------------------
#
# HasSourceOf
#
#-------------------------------------------------------------------------
class HasSourceOf(Rule):
    """Rule that checks people that have a particular source."""

    labels = [ _('Source ID:') ]
    
    def prepare(self,db):
        self.source_handle = db.get_source_from_gramps_id(self.list[0]).get_handle()

    def name(self):
        return 'Has source of'

    def category(self): 
        return _('Event filters')
    
    def description(self):
        return _('Matches people who have a particular source')

    def apply(self,db,p_id):
        p = db.get_person_from_handle(p_id)

        return p.has_source_reference( self.source_handle)


#-------------------------------------------------------------------------
#
# GenericFilter
#
#-------------------------------------------------------------------------
class GenericFilter:
    """Filter class that consists of several rules"""
    
    logical_functions = ['or', 'and', 'xor', 'one']

    def __init__(self,source=None):
        if source:
            self.need_param = source.need_param
            self.flist = source.flist[:]
            self.name = source.name
            self.comment = source.comment
            self.logical_op = source.logical_op
            self.invert = source.invert
        else:
            self.need_param = 0
            self.flist = []
            self.name = ''
            self.comment = ''
            self.logical_op = 'and'
            self.invert = 0

    def set_logical_op(self,val):
        if val in GenericFilter.logical_functions:
            self.logical_op = val
        else:
            self.logical_op = 'and'

    def get_logical_op(self):
        return self.logical_op

    def set_invert(self, val):
        self.invert = not not val

    def get_invert(self):
        return self.invert
    
    def get_name(self):
        return self.name
    
    def set_name(self,name):
        self.name = name

    def set_comment(self,comment):
        self.comment = comment

    def get_comment(self):
        return self.comment
    
    def add_rule(self,rule):
        self.flist.append(rule)

    def delete_rule(self,rule):
        self.flist.remove(rule)

    def set_rules(self,rules):
        self.flist = rules

    def get_rules(self):
        return self.flist

    def check_or(self,db,p_id):
        test = 0
        for rule in self.flist:
            test = test or rule.apply(db,p_id)
            if test:
                break
        if self.invert:
            return not test
        else:
            return test

    def check_xor(self,db,p_id):
        test = 0
        for rule in self.flist:
            temp = rule.apply(db,p_id)
            test = ((not test) and temp) or (test and (not temp))
        if self.invert:
            return not test
        else:
            return test

    def check_one(self,db,p_id):
        count = 0
        for rule in self.flist:
            if rule.apply(db,p_id):
                count = count + 1
                if count > 1:
                    break
        if self.invert:
            return count != 1
        else:
            return count == 1

    def check_and(self,db,p_id):
        test = 1
        for rule in self.flist:
            test = test and rule.apply(db,p_id)
            if not test:
                break
        if self.invert:
            return not test
        else:
            return test
    
    def get_check_func(self):
        try:
            m = getattr(self, 'check_' + self.logical_op)
        except AttributeError:
            m = self.check_and
        return m

    def check(self,db,p_id):
        return self.get_check_func()(db,p_id)

    def apply(self,db,id_list):
        m = self.get_check_func()
        res = []
        for rule in self.flist:
            rule.prepare(db)
        for p_id in id_list:
            if m(db,p_id):
                res.append(p_id)
        for rule in self.flist:
            rule.reset()
        return res


#-------------------------------------------------------------------------
#
# Name to class mappings
#
#-------------------------------------------------------------------------
tasks = {
    unicode(_("Everyone"))                             : Everyone,
    unicode(_("Is default person"))                    : IsDefaultPerson,
    unicode(_("Is bookmarked person"))                 : IsBookmarked,
    unicode(_("Has the Id"))                           : HasIdOf,
    unicode(_("Has a name"))                           : HasNameOf,
    unicode(_("Has the relationships"))                : HasRelationship,
    unicode(_("Has the death"))                        : HasDeath,
    unicode(_("Has the birth"))                        : HasBirth,
    unicode(_("Is a descendant of"))                   : IsDescendantOf,
    unicode(_("Is a descendant family member of"))     : IsDescendantFamilyOf,
    unicode(_("Is a descendant of filter match"))      : IsDescendantOfFilterMatch,
    unicode(_("Is a descendant of person not more than N generations away"))
                                                       : IsLessThanNthGenerationDescendantOf,
    unicode(_("Is a descendant of person at least N generations away"))
                                                       : IsMoreThanNthGenerationDescendantOf,
    unicode(_("Is a child of filter match"))           : IsChildOfFilterMatch,
    unicode(_("Is an ancestor of"))                    : IsAncestorOf,
    unicode(_("Is an ancestor of filter match"))       : IsAncestorOfFilterMatch,
    unicode(_("Is an ancestor of person not more than N generations away"))
                                                       : IsLessThanNthGenerationAncestorOf,
    unicode(_("Is an ancestor of person at least N generations away"))
                                                       : IsMoreThanNthGenerationAncestorOf,
    unicode(_("Is a parent of filter match"))          : IsParentOfFilterMatch,
    unicode(_("Has a common ancestor with"))           : HasCommonAncestorWith,
    unicode(_("Has a common ancestor with filter match"))
                                                       : HasCommonAncestorWithFilterMatch,
    unicode(_("Is a female"))                          : IsFemale,
    unicode(_("Is a male"))                            : IsMale,
    unicode(_("Has complete record"))                  : HasCompleteRecord,
    unicode(_("Has the personal event"))               : HasEvent,
    unicode(_("Has the family event"))                 : HasFamilyEvent,
    unicode(_("Has the personal attribute"))           : HasAttribute,
    unicode(_("Has the family attribute"))             : HasFamilyAttribute,
    unicode(_("Has source of"))                        : HasSourceOf,
    unicode(_("Matches the filter named"))             : MatchesFilter,
    unicode(_("Is spouse of filter match"))            : IsSpouseOfFilterMatch,
    unicode(_("Is a sibling of filter match"))         : IsSiblingOfFilterMatch,
    unicode(_("Relationship path between two people")) : RelationshipPathBetween,

    unicode(_("People who were adopted"))              : HaveAltFamilies,
    unicode(_("People who have images"))               : HavePhotos,
    unicode(_("People with children"))                 : HaveChildren,
    unicode(_("People with incomplete names"))         : IncompleteNames,
    unicode(_("People with no marriage records"))      : NeverMarried,
    unicode(_("People with multiple marriage records")): MultipleMarriages,
    unicode(_("People without a birth date"))          : NoBirthdate,
    unicode(_("People with incomplete events"))        : PersonWithIncompleteEvent,
    unicode(_("Families with incomplete events"))      : FamilyWithIncompleteEvent,
    unicode(_("People probably alive"))                : ProbablyAlive,
    unicode(_("People marked private"))                : PeoplePrivate,
    unicode(_("Witnesses"))                            : IsWitness,

    unicode(_("Has text matching substring of"))       : HasTextMatchingSubstringOf,
}

#-------------------------------------------------------------------------
#
# GenericFilterList
#
#-------------------------------------------------------------------------
class GenericFilterList:
    """Container class for the generic filters. Stores, saves, and
    loads the filters."""
    
    def __init__(self,file):
        self.filter_list = []
        self.file = os.path.expanduser(file)

    def get_filters(self):
        return self.filter_list
    
    def add(self,filt):
        self.filter_list.append(filt)
        
    def load(self):
       try:
           parser = make_parser()
           parser.setContentHandler(FilterParser(self))
           if self.file[0:7] != "file://":
               parser.parse("file://" + self.file)
           else:
               parser.parse(self.file)
       except (IOError,OSError):
           pass
       except SAXParseException:
           print "Parser error"

    def fix(self,line):
        l = line.strip()
        l = l.replace('&','&amp;')
        l = l.replace('>','&gt;')
        l = l.replace('<','&lt;')
        return l.replace('"','&quot;')

    def save(self):
        f = open(self.file.encode('utf-8'),'w')
        
        f.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
        f.write('<filters>\n')
        for i in self.filter_list:
            f.write('  <filter name="%s"' % self.fix(i.get_name()))
            if i.get_invert():
                f.write(' invert="1"')
            f.write(' function="%s"' % i.get_logical_op())
            comment = i.get_comment()
            if comment:
                f.write(' comment="%s"' % self.fix(comment))
            f.write('>\n')
            for rule in i.get_rules():
                f.write('    <rule class="%s">\n' % self.fix(rule.name()))
                for v in rule.values():
                    f.write('      <arg value="%s"/>\n' % self.fix(v))
                f.write('    </rule>\n')
            f.write('  </filter>\n')
        f.write('</filters>\n')
        f.close()

#-------------------------------------------------------------------------
#
# FilterParser
#
#-------------------------------------------------------------------------
class FilterParser(handler.ContentHandler):
    """Parses the XML file and builds the list of filters"""
    
    def __init__(self,gfilter_list):
        handler.ContentHandler.__init__(self)
        self.gfilter_list = gfilter_list
        self.f = None
        self.r = None
        self.a = []
        self.cname = None
        
    def setDocumentLocator(self,locator):
        self.locator = locator

    def startElement(self,tag,attrs):
        if tag == "filter":
            self.f = GenericFilter()
            self.f.set_name(attrs['name'])
            if attrs.has_key('function'):
                try:
                    if int(attrs['function']):
                        op = 'or'
                    else:
                        op = 'and'
                except ValueError:
                    op = attrs['function']
                self.f.set_logical_op(op)
            if attrs.has_key('comment'):
                self.f.set_comment(attrs['comment'])
            if attrs.has_key('invert'):
                try:
                    self.f.set_invert(int(attrs['invert']))
                except ValueError:
                    pass
            self.gfilter_list.add(self.f)
        elif tag == "rule":
            cname = attrs['class']
            name = unicode(_(cname))
            self.a = []
            if name in tasks:
                self.cname = tasks[name]
            else:
                print "ERROR: Filter rule '%s' in filter '%s' not found!" % (name,self.f.get_name())
        elif tag == "arg":
            self.a.append(attrs['value'])

    def endElement(self,tag):
        if tag == "rule":
            rule = self.cname(self.a)
            self.f.add_rule(rule)
            
    def characters(self, data):
        pass

class ParamFilter(GenericFilter):

    def __init__(self,source=None):
        GenericFilter.__init__(self,source)
        self.need_param = 1
        self.param_list = []

    def set_parameter(self,param):
        self.param_list = [param]

    def apply(self,db,id_list):
        for rule in self.flist:
            rule.set_list(self.param_list)
        for rule in self.flist:
            rule.prepare(db)
        result = GenericFilter.apply(self,db,id_list)
        for rule in self.flist:
            rule.reset()
        return result

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
SystemFilters = None
CustomFilters = None

def reload_system_filters():
    global SystemFilters
    SystemFilters = GenericFilterList(const.system_filters)
    SystemFilters.load()
    
def reload_custom_filters():
    global CustomFilters
    CustomFilters = GenericFilterList(const.custom_filters)
    CustomFilters.load()
    
if not SystemFilters:
    reload_system_filters()

if not CustomFilters:
    reload_custom_filters()


class GrampsFilterComboBox(gtk.ComboBox):

    def set(self,local_filters,default=""):
        self.store = gtk.ListStore(str)
        self.set_model(self.store)
        cell = gtk.CellRendererText()
        self.pack_start(cell,True)
        self.add_attribute(cell,'text',0)

        self.map = {}
        
        active = 0
        cnt = 0
        for filt in local_filters:
            self.store.append(row=[filt.get_name()])
            self.map[filt.get_name()] = filt
            if default != "" and default == filt.get_name():
                active = cnt
            cnt += 1
        
        for filt in SystemFilters.get_filters():
            self.store.append(row=[_(filt.get_name())])
            self.map[filt.get_name()] = filt
            if default != "" and default == filt.get_name():
                active = cnt
            cnt += 1

        for filt in CustomFilters.get_filters():
            self.store.append(row=[_(filt.get_name())])
            self.map[filt.get_name()] = filt
            if default != "" and default == filt.get_name():
                active = cnt
            cnt += 1

        if active:
            self.set_active(active)
        elif len(local_filters):
            self.set_active(2)
        elif len(SystemFilters.get_filters()):
            self.set_active(4 + len(local_filters))
        elif len(CustomFilters.get_filters()):
            self.set_active(6 + len(local_filters) + len(SystemFilters.get_filters()))
        else:
            self.set_active(0)

    def get_value(self):
        active = self.get_active()
        if active < 0:
            return None
        key = self.store[active][0]
        return self.map[key]


class FilterStore(gtk.ListStore):

    def __init__(self,local_filters=[], default=""):
        gtk.ListStore.__init__(self,str)
        self.list_map = []
        self.def_index = 0

        cnt = 0
        for filt in local_filters:
            name = filt.get_name()
            self.append(row=[name])
            self.list_map.append(filt)
            if default != "" and default == name:
                self.def_index = cnt
            cnt += 1

        for filt in SystemFilters.get_filters() + CustomFilters.get_filters():
            name = _(filt.get_name())
            self.append(row=[name])
            self.list_map.append(filt)
            if default != "" and default == name:
                self.def_index = cnt
            cnt += 1

    def default_index(self):
        return self.def_index

    def get_filter(self,index):
        return self.list_map[index]
    
            
def build_filter_menu(local_filters = [], default=""):
    menu = gtk.Menu()

    active = 0
    cnt = 0
    for filt in local_filters:
        menuitem = gtk.MenuItem(filt.get_name())
        menuitem.show()
        menu.append(menuitem)
        menuitem.set_data("filter", filt)
        if default != "" and default == filt.get_name():
            active = cnt
        cnt += 1
        
    for filt in SystemFilters.get_filters():
        menuitem = gtk.MenuItem(_(filt.get_name()))
        menuitem.show()
        menu.append(menuitem)
        menuitem.set_data("filter", filt)
        if default != "" and default == filt.get_name():
            active = cnt
        cnt += 1

    for filt in CustomFilters.get_filters():
        menuitem = gtk.MenuItem(_(filt.get_name()))
        menuitem.show()
        menu.append(menuitem)
        menuitem.set_data("filter", filt)
        if default != "" and default == filt.get_name():
            active = cnt
        cnt += 1

    if active:
        menu.set_active(active)
    elif len(local_filters):
        menu.set_active(2)
    elif len(SystemFilters.get_filters()):
        menu.set_active(4 + len(local_filters))
    elif len(CustomFilters.get_filters()):
        menu.set_active(6 + len(local_filters) + len(SystemFilters.get_filters()))
    else:
        menu.set_active(0)
        
    return menu

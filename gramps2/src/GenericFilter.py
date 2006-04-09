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
import sets
from TransUtils import sgettext as _

#-------------------------------------------------------------------------
#
# set up logging
#
#-------------------------------------------------------------------------
import logging
log = logging.getLogger(".GenericFilter")

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
import DateHandler
import NameDisplay
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
    if s == RelLib.Date.MOD_BEFORE:
        return  cmp_rule > cmp_value
    elif s == RelLib.Date.MOD_AFTER:
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

    labels      = []
    name        = ''
    category    = _('Miscellaneous filters')
    description = _('No description')

    def __init__(self,list):
        self.set_list(list)

    def is_empty(self):
        return False
    
    def prepare(self,db):
        pass

    def reset(self):
        pass

    def set_list(self,list):
        assert type(list) == type([]) or list == None, "Argument is not a list"
        assert len(list) == len(self.labels), \
               "Number of arguments does not match number of labels.\n"\
               "list: %s\nlabels: %s" % (list,self.labels)
        self.list = list

    def values(self):
        return self.list
    
    def check(self):
        return len(self.list) == len(self.labels)

    def apply(self,db,person):
        return True

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

    name        = _('Everyone')
    category    = _('General filters')
    description = _('Matches everyone in the database')

    def is_empty(self):
        return True

    def apply(self,db,person):
        return True

#-------------------------------------------------------------------------
#
# Disconnected
#
#-------------------------------------------------------------------------
class Disconnected(Rule):
    """Matches disconnected people"""

    name        = _('Disconnected people')
    category    = _('General filters')
    description = _('Matches people that have no family relationships '
                    'to any other person in the database')

    def apply(self,db,person):
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

    labels      = [ _('ID:'), _('ID:') ]
    name        = _("Relationship path between <persons>")
    category    = _('Relationship filters')
    description = _("Matches the ancestors of two persons back to a common ancestor, "
                    "producing the relationship path between two persons.")    

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
        
#-------------------------------------------------------------------------
#
# HasIdOf
#
#-------------------------------------------------------------------------
class HasIdOf(Rule):
    """Rule that checks for a person with a specific GRAMPS ID"""

    labels      = [ _('ID:') ]
    name        = _('People with <Id>')
    description = _("Matches people with a specified GRAMPS ID")
    category    = _('General filters')

    def apply(self,db,person):
        return person.gramps_id == self.list[0]

#-------------------------------------------------------------------------
#
# IsDefaultPerson
#
#-------------------------------------------------------------------------
class IsDefaultPerson(Rule):
    """Rule that checks for a default person in the database"""

    name        = _('Default person')
    category    = _('General filters')
    description = _("Matches the default person")

    def prepare(self,db):
        p = db.get_default_person()
        if p:
            self.def_handle = p.get_handle()
            self.apply = self.apply_real
        else:
            self.apply = lambda db,p: False

    def apply_real(self,db,person):
        return person.handle == self.def_handle

#-------------------------------------------------------------------------
#
# IsBookmarked
#
#-------------------------------------------------------------------------
class IsBookmarked(Rule):
    """Rule that checks for the bookmark list in the database"""

    name        = _('Bookmarked people')
    category    = _('General filters')
    description = _("Matches the people on the bookmark list")

    def prepare(self,db):
        bookmarks = db.get_bookmarks()
        if len(bookmarks) == 0:
            self.apply = lambda db,p : False
        else:
            self.bookmarks = sets.Set(bookmarks)
            self.apply = self.apply_real

    def apply_real(self,db,person):
        return person.handle in self.bookmarks

#-------------------------------------------------------------------------
#
# HasCompleteRecord
#
#-------------------------------------------------------------------------
class HasCompleteRecord(Rule):
    """Rule that checks for a person whose record is complete"""

    name        = _('People with complete records')
    category    = _('General filters')
    description = _('Matches all people whose records are complete')

    def apply(self,db,person):
        return person.get_complete_flag() == 1

#-------------------------------------------------------------------------
#
# IsFemale
#
#-------------------------------------------------------------------------
class IsFemale(Rule):
    """Rule that checks for a person that is a female"""

    name        = _('Females')
    category    = _('General filters')
    description = _('Matches all females')

    def apply(self,db,person):
        return person.gender == RelLib.Person.FEMALE

#-------------------------------------------------------------------------
#
# HasUnknownGender
#
#-------------------------------------------------------------------------
class HasUnknownGender(Rule):
    """Rule that checks for a person that has unknown gender"""

    name        = _('People with unknown gender')
    category    = _('General filters')
    description = _('Matches all people with unknown gender')

    def apply(self,db,person):
        return person.gender == RelLib.Person.UNKNOWN

#-------------------------------------------------------------------------
#
# IsDescendantOf
#
#-------------------------------------------------------------------------
class IsDescendantOf(Rule):
    """Rule that checks for a person that is a descendant
    of a specified person"""

    labels      = [ _('ID:'), _('Inclusive:') ]
    name        = _('Descendants of <person>')
    category    = _('Descendant filters')
    description = _('Matches all descendants for the specified person')

    def prepare(self,db):
        self.db = db
        self.map = {}
        try:
            if int(self.list[1]):
                first = False
            else:
                first = True
        except IndexError:
            first = True
        try:
            root_person = db.get_person_from_gramps_id(self.list[0])
            self.init_list(root_person,first)
        except:
            pass

    def reset(self):
        self.map = {}

    def apply(self,db,person):
        return self.map.has_key(person.handle)

    def init_list(self,person,first):
        if not person:
            return
        if not first:
            self.map[person.handle] = 1
        
        for fam_id in person.get_family_handle_list():
            fam = self.db.get_family_from_handle(fam_id)
            if fam:
                for child_handle in fam.get_child_handle_list():
                    self.init_list(self.db.get_person_from_handle(child_handle),0)

#-------------------------------------------------------------------------
#
# IsDescendantOfFilterMatch
#
#-------------------------------------------------------------------------
class IsDescendantOfFilterMatch(IsDescendantOf):
    """Rule that checks for a person that is a descendant
    of someone matched by a filter"""

    labels      = [ _('Filter name:') ]
    name        = _('Descendants of <filter> match')
    category    = _('Descendant filters')
    description = _("Matches people that are descendants of anybody matched by a filter")
    

#    def __init__(self,list):
#        IsDescendantOf.__init__(self,list)

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
                self.init_list (person,first)
        filt.reset()

    def reset(self):
        self.map = {}

    def apply(self,db,person):
        return self.map.has_key(person.handle)

#-------------------------------------------------------------------------
#
# IsLessThanNthGenerationDescendantOf
#
#-------------------------------------------------------------------------
class IsLessThanNthGenerationDescendantOf(Rule):
    """Rule that checks for a person that is a descendant of a specified person
    not more than N generations away"""

    labels      = [ _('ID:'), _('Number of generations:') ]
    name        = _('Descendants of <person> not more than <N> generations away')
    category    = _('Descendant filters')
    description = _("Matches people that are descendants of a specified person "
                 "not more than N generations away")

    def prepare(self,db):
        self.db = db
        self.map = {}
        try:
            root_person = db.get_person_from_gramps_id(self.list[0])
            self.init_list(root_person,0)
        except:
            pass

    def reset(self):
        self.map = {}

    def apply(self,db,person):
        return self.map.has_key(person.handle)

    def init_list(self,person,gen):
        if not person:
            return
        if gen:
            self.map[person.handle] = 1
            if gen >= int(self.list[1]):
                return

        for fam_id in person.get_family_handle_list():
            fam = self.db.get_family_from_handle(fam_id)
            for child_handle in fam.get_child_handle_list():
                self.init_list(self.db.get_person_from_handle(child_handle),gen+1)

#-------------------------------------------------------------------------
#
# IsMoreThanNthGenerationDescendantOf
#
#-------------------------------------------------------------------------
class IsMoreThanNthGenerationDescendantOf(Rule):
    """Rule that checks for a person that is a descendant of a specified person
    at least N generations away"""

    labels      = [ _('ID:'), _('Number of generations:') ]
    name        = _('Descendants of <person> at least <N> generations away')
    category    = _("Descendant filters")
    description = _("Matches people that are descendants of a specified "
                 "person at least N generations away")
    
    
    def prepare(self,db):
        self.db = db
        self.map = {}
        try:
            root_person = db.get_person_from_gramps_id(self.list[0])
            self.init_list(root_person,0)
        except:
            pass

    def reset(self):
        self.map = {}

    def apply(self,db,person):
        return self.map.has_key(person.handle)

    def init_list(self,person,gen):
        if not person:
            return
        if gen >= int(self.list[1]):
            self.map[person.handle] = 1

        for fam_id in person.get_family_handle_list():
            fam = self.db.get_family_from_handle(fam_id)
            for child_handle in fam.get_child_handle_list():
                self.init_list(self.db.get_person_from_handle(child_handle),gen+1)

#-------------------------------------------------------------------------
#
# IsChildOfFilterMatch
#
#-------------------------------------------------------------------------
class IsChildOfFilterMatch(Rule):
    """Rule that checks for a person that is a child
    of someone matched by a filter"""

    labels      = [ _('Filter name:') ]
    name        = _('Children of <filter> match')
    category    = _('Family filters')
    description = _("Matches children of anybody matched by a filter")

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
        for fam_id in person.get_family_handle_list():
            fam = self.db.get_family_from_handle(fam_id)
            for child_handle in fam.get_child_handle_list():
                self.map[child_handle] = 1

#-------------------------------------------------------------------------
#
# IsSiblingOfFilterMatch
#
#-------------------------------------------------------------------------
class IsSiblingOfFilterMatch(Rule):
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
            for child_handle in fam.get_child_handle_list():
                if child_handle != person.handle:
                    self.map[child_handle] = 1

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

#-------------------------------------------------------------------------
#
# IsMoreThanNthGenerationAncestorOf
#
#-------------------------------------------------------------------------
class IsMoreThanNthGenerationAncestorOf(Rule):
    """Rule that checks for a person that is an ancestor of a specified person
    at least N generations away"""

    labels      = [ _('ID:'), _('Number of generations:') ]
    name        = _('Ancestors of <person> at least <N> generations away')
    category    = _("Ancestral filters")
    description = _("Matches people that are ancestors "
                    "of a specified person at least N generations away")

    def prepare(self,db):
        self.db = db
        self.map = {}
        try:
            root_handle = db.get_person_from_gramps_id(self.list[0]).get_handle()
            self.init_ancestor_list(root_handle,0)
        except:
            pass

    def reset(self):
        self.map = []
    
    def apply(self,db,person):
        return self.map.has_key(person.handle)

    def init_ancestor_list(self,handle,gen):
#        if self.map.has_key(p.get_handle()) == 1:
#            loop_error(self.orig,p)
        if not handle:
            return
        if gen >= int(self.list[1]):
            self.map[handle] = 1
        
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

#-------------------------------------------------------------------------
#
# HasCommonAncestorWith
#
#-------------------------------------------------------------------------
class HasCommonAncestorWith(Rule):
    """Rule that checks for a person that has a common ancestor with a specified person"""

    labels      = [ _('ID:') ]
    name        = _('People with a common ancestor with <person>')
    category    = _("Ancestral filters")
    description = _("Matches people that have a common ancestor "
                    "with a specified person")

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
        try:
            handle = db.get_person_from_gramps_id(self.list[0]).get_handle()
            if handle:
                def init(self,handle): self.ancestor_cache[handle] = 1
                for_each_ancestor(db,[handle],init,self)
        except:
            pass

    def apply(self,db,person):
        # On the first call, we build the ancestor cache for the
        # reference person.   Then, for each person to test,
        # we browse his ancestors until we found one in the cache.
        if len(self.ancestor_cache) == 0:
            self.init_ancestor_cache(db)
        handle = person.handle
        return for_each_ancestor(db,[handle],
                                 lambda self,handle: self.ancestor_cache.has_key(handle),
                                 self);

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

#-------------------------------------------------------------------------
#
# IsMale
#
#-------------------------------------------------------------------------
class IsMale(Rule):
    """Rule that checks for a person that is a male"""

    name        =  _('Males')
    category    = _('General filters')
    description = _('Matches all males')

    def apply(self,db,person):
        return person.gender == RelLib.Person.MALE

#-------------------------------------------------------------------------
#
# HasEvent
#
#-------------------------------------------------------------------------
class HasEvent(Rule):
    """Rule that checks for a person with a particular value"""

    labels      = [ _('Personal event:'), 
                    _('Date:'), 
                    _('Place:'), 
                    _('Description:') ]
    name        =  _('People with the personal <event>')
    description = _("Matches people with a personal event of a particular value")
    category    = _('Event filters')
    
    def prepare(self,db):
        self.date = None
        try:
            if self.list[1]:
                self.date = DateHandler.parser.parse(self.list[1])
        except: pass

    def apply(self,db,person):
        for event_handle in person.get_event_list():
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
                return True
        return False

#-------------------------------------------------------------------------
#
# HasFamilyEvent
#
#-------------------------------------------------------------------------
class HasFamilyEvent(Rule):
    """Rule that checks for a person who has a relationship event
    with a particular value"""

    labels      = [ _('Family event:'), 
                    _('Date:'), 
                    _('Place:'), 
                    _('Description:') ]
    name        =  _('People with the family <event>')
    description = _("Matches people with a family event of a particular value")
    category    = _('Event filters')
    
    def prepare(self,db):
        self.date = None
        try:
            if self.list[1]:
                self.date = DateHandler.parser.parse(self.list[1])
        except:
            pass

    def apply(self,db,person):
        for f_id in person.get_family_handle_list():
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
                if self.list[2]:
                    pl_id = event.get_place_handle()
                    if pl_id:
                        pl = db.get_place_from_handle(pl_id)
                        pn = pl.get_title().upper()
                        if pn.find(self.list[2].upper()) == -1:
                            val = 0
                    else:
                        val = 0
                            
                if val == 1:
                    return True
        return False

#-------------------------------------------------------------------------
#
# HasRelationship
#
#-------------------------------------------------------------------------
class HasRelationship(Rule):
    """Rule that checks for a person who has a particular relationship"""

    labels      = [ _('Number of relationships:'),
                    _('Relationship type:'),
                    _('Number of children:') ]
    name        = _('People with the <relationships>')
    description = _("Matches people with a particular relationship")
    category    = _('Family filters')

    def apply(self,db,person):
        rel_type = 0
        cnt = 0
        num_rel = len(person.get_family_handle_list())

        # count children and look for a relationship type match
        for f_id in person.get_family_handle_list():
            f = db.get_family_from_handle(f_id)
            cnt = cnt + len(f.get_child_handle_list())
            if self.list[1] and int(self.list[1]) == f.get_relationship():
                rel_type = 1

        # if number of relations specified
        if self.list[0]:
            try:
                v = int(self.list[0])
            except:
                return False
            if v != num_rel:
                return False

        # number of childred
        if self.list[2]:
            try:
                v = int(self.list[2])
            except:
                return False
            if v != cnt:
                return False

        # relation
        if self.list[1]:
            return rel_type == 1
        else:
            return True

#-------------------------------------------------------------------------
#
# HasBirth
#
#-------------------------------------------------------------------------
class HasBirth(Rule):
    """Rule that checks for a person with a birth of a particular value"""

    labels      = [ _('Date:'), _('Place:'), _('Description:') ]
    name        = _('People with the <birth data>')
    description = _("Matches people with birth data of a particular value")
    category    = _('Event filters')
    
    def __init__(self,list):
        Rule.__init__(self,list)
        if self.list[0]:
            self.date = DateHandler.parser.parse(self.list[0])
        else:
            self.date = None
        
    def apply(self,db,person):
        event_ref = person.get_birth_ref()
        if not event_ref:
            return False
        event = db.get_event_from_handle(event_ref.ref)
        ed = event.get_description().upper()
        if self.list[2] \
               and ed.find(self.list[2].upper())==-1:
            return False
        if self.date:
            if date_cmp(self.date,event.get_date_object()) == 0:
                return False
        if self.list[1]:
            pl_id = event.get_place_handle()
            if pl_id:
                pl = db.get_place_from_handle(pl_id)
                pn = pl.get_title().upper()
                if pn.find(self.list[1].upper()) == -1:
                    return False
            else:
                return False
        return True

#-------------------------------------------------------------------------
#
# HasDeath
#
#-------------------------------------------------------------------------
class HasDeath(Rule):
    """Rule that checks for a person with a death of a particular value"""

    labels      = [ _('Date:'), _('Place:'), _('Description:') ]
    name        = _('People with the <death data>')
    description = _("Matches people with death data of a particular value")
    category    = _('Event filters')
    
    def __init__(self,list):
        Rule.__init__(self,list)
        if self.list[0]:
            self.date = DateHandler.parser.parse(self.list[0])
        else:
            self.date = None

    def apply(self,db,person):
        event_handle = person.get_death_handle()
        if not event_handle:
            return False
        event = db.get_event_from_handle(event_handle)
        ed = event.get_description().upper()
        if self.list[2] \
               and ed.find(self.list[2].upper())==-1:
            return False
        if self.date:
            if date_cmp(self.date,event.get_date_object()) == 0:
                return False
        if self.list[1]:
            pl_id = event.get_place_handle()
            if pl_id:
                pl = db.get_place_from_handle(pl_id)
                pn = pl.get_title().upper()
                if self.list[1] and pn.find(self.list[1].upper()) == -1:
                    return False
            else:
                return False
        return True

#-------------------------------------------------------------------------
#
# HasAttribute
#
#-------------------------------------------------------------------------
class HasAttribute(Rule):
    """Rule that checks for a person with a particular personal attribute"""

    labels      = [ _('Personal attribute:'), _('Value:') ]
    name        = _('People with the personal <attribute>')
    description = _("Matches people with the personal attribute of a particular value")
    category    = _('General filters')

    def apply(self,db,person):
        if not self.list[0]:
            return False
        for attr in person.get_attribute_list():
            name_match = self.list[0] == attr.get_type()
            value_match = \
                    attr.get_value().upper().find(self.list[1].upper()) != -1
            if name_match and value_match:
                return True
        return False

#-------------------------------------------------------------------------
#
# HasFamilyAttribute
#
#-------------------------------------------------------------------------
class HasFamilyAttribute(Rule):
    """Rule that checks for a person with a particular family attribute"""

    labels      = [ _('Family attribute:'), _('Value:') ]
    name        = _('People with the family <attribute>')
    description = _("Matches people with the family attribute of a particular value")
    category    = _('General filters')
    
    def apply(self,db,person):
        if not self.list[0]:
            return False
        for f_id in person.get_family_handle_list():
            f = db.get_family_from_handle(f_id)
            for attr in f.get_attribute_list():
                name_match = self.list[0] == attr.get_type()
                value_match = \
                        attr.get_value().upper().find(self.list[1].upper()) != -1
                if name_match and value_match:
                    return True
        return False

#-------------------------------------------------------------------------
#
# HasNameOf
#
#-------------------------------------------------------------------------
class HasNameOf(Rule):
    """Rule that checks for full or partial name matches"""

    labels      = [ _('Given name:'),
                    _('Family name:'),
                    _('Suffix:'),
                    _('person|Title:')]
    name        = _('People with the <name>')
    description = _("Matches people with a specified (partial) name")
    category    = _('General filters')

    def apply(self,db,person):
        self.f = self.list[0]
        self.l = self.list[1]
        self.s = self.list[2]
        self.t = self.list[3]
        for name in [person.get_primary_name()] + person.get_alternate_names():
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
                return True
        return False

#-------------------------------------------------------------------------
#
# HasNameOf
#
#-------------------------------------------------------------------------
class SearchName(Rule):
    """Rule that checks for full or partial name matches"""

    labels      = [_('Substring:')]
    name        = _('People matching the <name>')
    description = _("Matches people with a specified (partial) name")
    category    = _('General filters')

    def apply(self,db,person):
        self.f = self.list[0]
        n = NameDisplay.displayer.display(person)
        return self.f and n.upper().find(self.f.upper()) != -1
    
#-------------------------------------------------------------------------
#
# IncompleteNames
#
#-------------------------------------------------------------------------
class IncompleteNames(Rule):
    """People with incomplete names"""

    name        = _('People with incomplete names')
    description = _("Matches people with firstname or lastname missing")
    category    = _('General filters')

    def apply(self,db,person):
        for name in [person.get_primary_name()] + person.get_alternate_names():
            if name.get_first_name() == "":
                return True
            if name.get_surname() == "":
                return True
        return False

#-------------------------------------------------------------------------
#
# MatchesFilter
#
#-------------------------------------------------------------------------
class MatchesFilter(Rule):
    """Rule that checks against another filter"""

    labels      = [_('Filter name:')]
    name        = _('People matching the <filter>')
    description = _("Matches people macthed by the specified filter name")
    category    = _('General filters')

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

    def apply(self,db,person):
        for filt in SystemFilters.get_filters():
            if filt.get_name() == self.list[0]:
                return filt.check(db,person.handle)
        for filt in CustomFilters.get_filters():
            if filt.get_name() == self.list[0]:
                return filt.check(db,person.handle)
        return False

#-------------------------------------------------------------------------
#
# IsSpouseOfFilterMatch
#
#-------------------------------------------------------------------------
class IsSpouseOfFilterMatch(Rule):
    """Rule that checks for a person married to someone matching
    a filter"""

    labels      = [_('Filter name:')]
    name        = _('Spouses of <filter> match')
    description = _("Matches people married to anybody matching a filter")
    category    = _('Family filters')

    def prepare(self,db):
        self.filt = MatchesFilter (self.list)
        self.filt.prepare(db)
        
    def apply(self,db,person):
        for family_handle in person.get_family_handle_list ():
            family = db.get_family_from_handle(family_handle)
            for spouse_id in [family.get_father_handle (), family.get_mother_handle ()]:
                if not spouse_id:
                    continue
                if spouse_id == person.handle:
                    continue
                if self.filt.apply (db, db.get_person_from_handle( spouse_id)):
                    return True
        return False

#-------------------------------------------------------------------------
# "People who were adopted"
#-------------------------------------------------------------------------
class HaveAltFamilies(Rule):
    """People who were adopted"""

    name        = _('Adopted people')
    description = _("Matches people who were adopted")
    category    = _('Family filters')

    def apply(self,db,person):
        for (fam,rel1,rel2) in person.get_parent_family_handle_list():
            if rel1 == RelLib.Person.CHILD_ADOPTED \
                   or rel2 == RelLib.Person.CHILD_ADOPTED:
                return True
        return False


#-------------------------------------------------------------------------
# "People who have images"
#-------------------------------------------------------------------------
class HavePhotos(Rule):
    """People who have images"""

    name        = _('People with images')
    description = _("Matches people with images in the gallery")
    category    = _('General filters')

    def apply(self,db,person):
        return len( person.get_media_list()) > 0

#-------------------------------------------------------------------------
# "People with children"
#-------------------------------------------------------------------------
class HaveChildren(Rule):
    """People with children"""

    name        = _('People with children')
    description = _("Matches people who have children")
    category    = _('Family filters')

    def apply(self,db,person):
        for family_handle in person.get_family_handle_list():
            family = db.get_family_from_handle(family_handle)
            return len(family.get_child_handle_list()) > 0

#-------------------------------------------------------------------------
# "People with no marriage records"
#-------------------------------------------------------------------------
class NeverMarried(Rule):
    """People with no marriage records"""

    name        = _('People with no marriage records')
    description = _("Matches people who have no spouse")
    category    = _('Family filters')

    def apply(self,db,person):
        return len(person.get_family_handle_list()) == 0

#-------------------------------------------------------------------------
# "People with multiple marriage records"
#-------------------------------------------------------------------------
class MultipleMarriages(Rule):
    """People with multiple marriage records"""

    name        = _('People with multiple marriage records')
    description = _("Matches people who have more than one spouse")
    category    = _('Family filters')

    def apply(self,db,person):
        return len(person.get_family_handle_list()) > 1

#-------------------------------------------------------------------------
# "People without a birth date"
#-------------------------------------------------------------------------
class NoBirthdate(Rule):
    """People without a birth date"""

    name        = _('People without a known birth date')
    description = _("Matches people without a known birthdate")
    category    = _('General filters')

    def apply(self,db,person):
        birth_ref = person.get_birth_ref()
        if not birth_ref:
            return True
        birth = db.get_event_from_handle(birth_ref.ref)
        if not birth.get_date_object():
            return True
        return False

#-------------------------------------------------------------------------
# "People with incomplete events"
#-------------------------------------------------------------------------
class PersonWithIncompleteEvent(Rule):
    """People with incomplete events"""

    name        = _('People with incomplete events')
    description = _("Matches people with missing date or place in an event")
    category    = _('Event filters')

    def apply(self,db,person):
        for event_ref in person.get_event_ref_list() + \
                [person.get_birth_ref(), person.get_death_ref()]:
            if event_ref:
                event = db.get_event_from_handle(event_ref.ref)
                if not event.get_place_handle():
                    return True
                if not event.get_date_object():
                    return True
        return False

#-------------------------------------------------------------------------
# "Families with incomplete events"
#-------------------------------------------------------------------------
class FamilyWithIncompleteEvent(Rule):
    """Families with incomplete events"""

    name        = _('Families with incomplete events')
    description = _("Matches people with missing date or place in an event of the family")
    category    = _('Event filters')

    def apply(self,db,person):
        for family_handle in person.get_family_handle_list():
            family = db.get_family_from_handle(family_handle)
            for event_handle in family.get_event_list():
                event = db.get_event_from_handle(event_handle)
                if event:
                    if not event.get_place_handle():
                        return True
                    if not event.get_date_object():
                        return True
        return False

#-------------------------------------------------------------------------
# "People probably alive"
#-------------------------------------------------------------------------
class ProbablyAlive(Rule):
    """People probably alive"""

    labels      = [_("On year:")]
    name        =  _('People probably alive')
    description = _("Matches people without indications of death that are not too old")
    category    = _('General filters')

    def prepare(self,db):
        try:
            self.current_year = int(self.list[0])
        except:
            self.current_year = None

    def apply(self,db,person):
        return probably_alive(person,db,self.current_year)

#-------------------------------------------------------------------------
# "People marked private"
#-------------------------------------------------------------------------
class PeoplePrivate(Rule):
    """People marked private"""

    name        = _('People marked private')
    description = _("Matches people that are indicated as private")
    category    = _('General filters')

    def apply(self,db,person):
        return person.get_privacy()

#-------------------------------------------------------------------------
# "Witnesses"
#-------------------------------------------------------------------------
class IsWitness(Rule):
    """Witnesses"""

    labels      = [_('Personal event:'), _('Family event:')]
    name        = _('Witnesses')
    description = _("Matches people who are witnesses in any event")
    category    = _('Event filters')

    def prepare(self,db):
        self.db = db
        self.map = []
        self.build_witness_list()

    def reset(self):
        self.map = []
        
    def apply(self,db,person):
        return person.handle in self.map

    def build_witness_list(self):
        for person_handle in self.db.get_person_handles():
            p = self.db.get_person_from_handle(person_handle)
            self.get_witness_of_events(self.list[0],
                                       p.get_event_ref_list()+
                                       [p.get_birth_ref(),
                                        p.get_death_ref()]
                                       )

        for family_handle in self.db.get_family_handles():
            f = self.db.get_family_from_handle(family_handle)
            self.get_witness_of_events(self.list[1],f.get_event_ref_list())

    def get_witness_of_events(self, event_type, event_list):
        if not event_list:
            return
        for event_ref in event_list:
            if event_reg:
                event = self.db.get_event_from_handle(event_ref.ref)
                if event_type and not event.get_name() == event_type:
                    continue
                wlist = event.get_witness_list()
                if wlist:
                    for w in wlist:
                        if w.get_type()[0] == RelLib.Event.ID:
                            self.map.append(w.get_value())


#-------------------------------------------------------------------------
# "HasTextMatchingSubstringOf"
#-------------------------------------------------------------------------
class HasTextMatchingSubstringOf(Rule):
    """Rule that checks for string matches in any textual information"""

    labels      = [ _('Substring:'),
                    _('Case sensitive:'), 
                    _('Regular-Expression matching:')]
    name        = _('People with records containing <substring>')
    description = _("Matches people whose records contain text matching a substring")
    category    = _('General filters')

    def prepare(self,db):
        self.db = db
        self.person_map = {}
        self.event_map = {}
        self.source_map = {}
        self.repo_map = {}
        self.family_map = {}
        self.place_map = {}
        self.media_map = {}
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
        self.cache_repos()
        self.cache_sources()

    def reset(self):
        self.person_map = {}
        self.event_map = {}
        self.source_map = {}
        self.repo_map = {}
        self.family_map = {}
        self.place_map = {}
        self.media_map = {}

    def apply(self,db,person):
        if person.handle in self.person_map:   # Cached by matching Source?
            return self.person_map[person.handle]
        if self.match_object(person):        # first match the person itself
            return True
        for event_ref in person.get_event_ref_list()+[person.get_birth_ref(), person.get_death_ref()]:
            if self.search_event(event_ref.ref): # match referenced events
                return True
        for family_handle in person.get_family_handle_list(): # match families
            if self.search_family(family_handle):
                return True
        for media_ref in person.get_media_list(): # match Media object
            if self.search_media(media_ref.get_reference_handle()):
                return True
        return False
    
    def search_family(self,family_handle):
        if not family_handle:
            return False
        # search inside the family and cache the result to not search a family twice
        if not family_handle in self.family_map:
            match = 0
            family = self.db.get_family_from_handle(family_handle)
            if self.match_object(family):
                match = 1
            else:
                for event_ref in family.get_event_ref_list():
                    if self.search_event(event_ref.ref):
                        match = 1
                        break
                for media_ref in family.get_media_list(): # match Media object
                    if self.search_media(media_ref.get_reference_handle()):
                        return True
            self.family_map[family_handle] = match
        return self.family_map[family_handle]

    def search_event(self,event_handle):
        if not event_handle:
            return False
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
                for media_ref in event.get_media_list(): # match Media object
                    if self.search_media(media_ref.get_reference_handle()):
                        return True
            self.event_map[event_handle] = match
        return self.event_map[event_handle]

    def search_place(self,place_handle):
        if not place_handle:
            return False
        # search inside the place and cache the result
        if not place_handle in self.place_map:
            place = self.db.get_place_from_handle(place_handle)
            self.place_map[place_handle] = self.match_object(place)
        return self.place_map[place_handle]

    def search_media(self,media_handle):
        if not media_handle:
            return False
        # search inside the place and cache the result
        if not media_handle in self.media_map:
            media = self.db.get_object_from_handle(media_handle)
            self.media_map[media_handle] = self.match_object(media)
        return self.media_map[media_handle]

    def cache_repos(self):
        # search all matching repositories
        for repo_handle in self.db.get_repository_handles():
            repo = self.db.get_repository_from_handle(repo_handle)
            if( self.match_object(repo)):
                self.repo_map[repo_handle] = 1
    
    def cache_sources(self):
        # search all sources and match all referents of a matching source
        for source_handle in self.db.get_source_handles():
            source = self.db.get_source_from_handle(source_handle)
            match = self.match_object(source)
            if not match:
                for reporef in source.get_reporef_list():
                    if reporef.get_reference_handle() in self.repo_map:
                        match = 1
            if match:
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
                for handle in media_list:
                    self.media_map[handle] = 1

    def match_object(self,obj):
        if not obj:
            return False
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
        self.repo_map = {}
        self.family_map = {}
        self.place_map = {}
        self.media_map = {}
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

    labels      = [ _('Source ID:') ]
    name        = _('People with the <source>')
    category    = _('General filters')
    description = _('Matches people who have a particular source')
    
    def prepare(self,db):
        try:
            self.source_handle = db.get_source_from_gramps_id(self.list[0]).get_handle()
        except:
            self.source_handle = None

    def apply(self,db,person):
        if not self.source_handle:
            return False
        return person.has_source_reference( self.source_handle)

#-------------------------------------------------------------------------
# "People having notes"
#-------------------------------------------------------------------------
class HasNote(Rule):
    """People having notes"""

    name        = _('People having notes')
    description = _("Matches people that have a note")
    category    = _('General filters')

    def apply(self,db,person):
        return bool(person.get_note())

#-------------------------------------------------------------------------
# "People having notes that contain a substring"
#-------------------------------------------------------------------------
class HasNoteMatchingSubstringOf(Rule):
    """People having notes containing <subtring>"""

    labels      = [ _('Substring:')]
    name        = _('People having notes containing <subtring>')
    description = _("Matches people whose notes contain text matching a substring")
    category    = _('General filters')

    def apply(self,db,person):
        n = person.get_note()
        if n:
            return n.upper().find(self.list[0].upper()) != -1
        return False

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
            self.invert = False

    def match(self,handle):
        return True

    def is_empty(self):
        return len(self.flist) == 1 and self.flist[0].is_empty()

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

    def check_func(self,db,id_list,task):
        final_list = []
        
        if id_list == None:
            cursor = db.get_person_cursor()
            data = cursor.next()
            while data:
                person = RelLib.Person()
                person.unserialize(data[1])
                if self.invert ^ task(db,person):
                    final_list.append(data[0])
                data = cursor.next()
        else:
            for handle in id_list:
                person = db.get_person_from_handle(handle)
                if self.invert ^ task(db,person):
                    final_list.append(handle)
        return final_list

    def check_or(self,db,id_list):
        return self.check_func(db,id_list,self.or_test)

    def check_and(self,db,id_list):
        final_list = []
        flist = self.flist
        invert = self.invert
        if id_list == None:
            cursor = db.get_person_cursor()
            data = cursor.next()
            p = RelLib.Person
            while data:
                person = p(data[1])
                val = True
                for rule in flist:
                    if not rule.apply(db,person):
                        val = False
                        break
                if invert ^ val:
                    final_list.append(data[0])
                data = cursor.next()
        else:
            for handle in id_list:
                person = db.get_person_from_handle(handle)
                val = True
                for rule in flist:
                    if not rule.apply(db,person):
                        val = False
                if invert ^ val:
                    final_list.append(handle)
        return final_list

    def check_one(self,db,id_list):
        return self.check_func(db,id_list,self.one_test)

    def check_xor(self,db,id_list):
        return self.check_func(db,id_list,self.xor_test)

    def xor_test(self,db,person):
        test = False
        for rule in self.flist:
            test = test ^ rule.apply(db,person)
        return test

    def one_test(self,db,person):
        count = 0
        for rule in self.flist:
            if rule.apply(db,person):
                if count:
                    return False
                count += 1
        return count == 1

    def or_test(self,db,person):
        for rule in self.flist:
            if rule.apply(db,person):
                return True
        return False
    
    def get_check_func(self):
        try:
            m = getattr(self, 'check_' + self.logical_op)
        except AttributeError:
            m = self.check_and
        return m

    def check(self,db,handle):
        return self.get_check_func()(db,[handle])

    def apply(self,db,id_list=None):
        m = self.get_check_func()
        for rule in self.flist:
            rule.prepare(db)
        res = m(db,id_list)
        for rule in self.flist:
            rule.reset()
        return res

#-------------------------------------------------------------------------
#
# IsLessThanNthGenerationAncestorOfBookmarked
#
#-------------------------------------------------------------------------
class IsLessThanNthGenerationAncestorOfBookmarked(Rule):
    # Submitted by Wayne Bergeron
    """Rule that checks for a person that is an ancestor of bookmarked persons
    not more than N generations away"""

    labels      = [ _('Number of generations:') ]
    name        = _('Ancestors of bookmarked people not more '
                    'than <N> generations away')
    category    = _('Ancestral filters')
    description = _("Matches ancestors of the people on the bookmark list "
                    "not more than N generations away")

    def prepare(self,db):
	self.db = db
        bookmarks = self.db.get_bookmarks()
        if len(bookmarks) == 0:
            self.apply = lambda db,p : False
        else:
            self.map = {}
            self.bookmarks = sets.Set(bookmarks)
            self.apply = self.apply_real
            for self.bookmarkhandle in self.bookmarks:
		self.init_ancestor_list(self.bookmarkhandle, 1)


    def init_ancestor_list(self,handle,gen):
#        if self.map.has_key(p.get_handle()) == 1:
#            loop_error(self.orig,p)
        if not handle:
            return
        if gen:
            self.map[handle] = 1
            if gen >= int(self.list[0]):
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

    def apply_real(self,db,person):
        return person.handle in self.map

    def reset(self):
        self.map = {}

#-------------------------------------------------------------------------
#
# IsLessThanNthGenerationAncestorOfDefaultPerson
#
#-------------------------------------------------------------------------
class IsLessThanNthGenerationAncestorOfDefaultPerson(Rule):
    # Submitted by Wayne Bergeron
    """Rule that checks for a person that is an ancestor of the default person
    not more than N generations away"""

    labels      = [ _('Number of generations:') ]
    name        = _('Ancestors of the default person '
                    'not more than <N> generations away')
    category    = _('Ancestral filters')
    description = _("Matches ancestors of the default person "
                    "not more than N generations away")

    def prepare(self,db):
	self.db = db
	p = db.get_default_person()
        if p == 0:
            self.apply = lambda db,p: False
        else:
            self.def_handle = p.get_handle()
            self.apply = self.apply_real
            self.map = {}
            self.init_ancestor_list(self.def_handle, 1)


    def init_ancestor_list(self,handle,gen):
#        if self.map.has_key(p.get_handle()) == 1:
#            loop_error(self.orig,p)
        if not handle:
            return
        if gen:
            self.map[handle] = 1
            if gen >= int(self.list[0]):
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

    def apply_real(self,db,person):
        return person.handle in self.map

    def reset(self):
        self.map = {}

#-------------------------------------------------------------------------
#
# Name to class mappings
#
#-------------------------------------------------------------------------
# This dict is mapping from old names to new names, so that the existing
# custom_filters.xml will continue working
old_names_2_class = {
    "Everyone"                      : Everyone,
    "Is default person"             : IsDefaultPerson,
    "Is bookmarked person"          : IsBookmarked,
    "Has the Id"                    : HasIdOf,
    "Has a name"                    : HasNameOf,
    "Has the relationships"         : HasRelationship,
    "Has the death"                 : HasDeath,
    "Has the birth"                 : HasBirth,
    "Is a descendant of"            : IsDescendantOf,
    "Is a descendant family member of" : IsDescendantFamilyOf,
    "Is a descendant of filter match": IsDescendantOfFilterMatch,
    "Is a descendant of person not more than N generations away":
                                IsLessThanNthGenerationDescendantOf,
    "Is a descendant of person at least N generations away":
                                IsMoreThanNthGenerationDescendantOf,
    "Is an descendant of person at least N generations away" :
                                IsMoreThanNthGenerationDescendantOf,
    "Is a child of filter match"    : IsChildOfFilterMatch,
    "Is an ancestor of"             : IsAncestorOf,
    "Is an ancestor of filter match": IsAncestorOfFilterMatch,
    "Is an ancestor of person not more than N generations away" : 
                                IsLessThanNthGenerationAncestorOf,
    "Is an ancestor of person at least N generations away":
                                IsMoreThanNthGenerationAncestorOf,
    "Is a parent of filter match"   : IsParentOfFilterMatch,
    "Has a common ancestor with"    : HasCommonAncestorWith,
    "Has a common ancestor with filter match" :HasCommonAncestorWithFilterMatch,
    "Is a female"                   : IsFemale,
    "Is a male"                     : IsMale,
    "Has complete record"           : HasCompleteRecord,
    "Has the personal event"        : HasEvent,
    "Has the family event"          : HasFamilyEvent,
    "Has the personal attribute"    : HasAttribute,
    "Has the family attribute"      : HasFamilyAttribute,
    "Has source of"                 : HasSourceOf,
    "Matches the filter named"      : HasSourceOf,
    "Is spouse of filter match"     : IsSpouseOfFilterMatch,
    "Is a sibling of filter match"  : IsSiblingOfFilterMatch,
    "Relationship path between two people" : RelationshipPathBetween,
    "People who were adopted"       : HaveAltFamilies,
    "People who have images"        : HavePhotos,
    "People with children"          : HaveChildren,
    "People with incomplete names"  : IncompleteNames,
    "People with no marriage records" : NeverMarried,
    "People with multiple marriage records": MultipleMarriages,
    "People without a birth date"   : NoBirthdate,
    "People with incomplete events" : PersonWithIncompleteEvent,
    "Families with incomplete events" :FamilyWithIncompleteEvent,
    "People probably alive"         : ProbablyAlive,
    "People marked private"         : PeoplePrivate,
    "Witnesses"                     : IsWitness,
    "Has text matching substring of":HasTextMatchingSubstringOf,
}

editor_rule_list = [
    Everyone,
    IsFemale,
    HasUnknownGender,
    IsMale,
    IsDefaultPerson,
    IsBookmarked,
    HasIdOf,
    HasNameOf,
    HasRelationship,
    HasDeath,
    HasBirth,
    HasCompleteRecord,
    HasEvent,
    HasFamilyEvent,
    HasAttribute,
    HasFamilyAttribute,
    HasSourceOf,
    HaveAltFamilies,
    HavePhotos,
    HaveChildren,
    IncompleteNames,
    NeverMarried,
    MultipleMarriages,
    NoBirthdate,
    PersonWithIncompleteEvent,
    FamilyWithIncompleteEvent,
    ProbablyAlive,
    PeoplePrivate,
    IsWitness,
    IsDescendantOf,
    IsDescendantFamilyOf,
    IsLessThanNthGenerationAncestorOfDefaultPerson,
    IsDescendantOfFilterMatch,
    IsLessThanNthGenerationDescendantOf,
    IsMoreThanNthGenerationDescendantOf,
    IsAncestorOf,
    IsAncestorOfFilterMatch,
    IsLessThanNthGenerationAncestorOf,
    IsLessThanNthGenerationAncestorOfBookmarked,
    IsMoreThanNthGenerationAncestorOf,
    HasCommonAncestorWith,
    HasCommonAncestorWithFilterMatch,
    MatchesFilter,
    IsChildOfFilterMatch,
    IsParentOfFilterMatch,
    IsSpouseOfFilterMatch,
    IsSiblingOfFilterMatch,
    RelationshipPathBetween,
    HasTextMatchingSubstringOf,
    HasNote,
    HasNoteMatchingSubstringOf
]

#-------------------------------------------------------------------------
#
# GenericFilterList
#
#-------------------------------------------------------------------------
class GenericFilterList:
    """Container class for the generic filters. Stores, saves, and
    loads the filters."""
    
    def __init__(self,file):
        self.filter_list = {}
        self.file = os.path.expanduser(file)

    def get_filters(self,namespace='generic'):
        try:
            return self.filter_list[namespace]
        except KeyError:
            return []
    
    def add(self,namespace,filt):
        if namespace not in self.filter_list:
            self.filter_list[namespace] = []
        self.filter_list[namespace].append(filt)
        
    def load(self):
       try:
           if os.path.isfile(self.file):
               parser = make_parser()
               parser.setContentHandler(FilterParser(self))
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
        for namespace in self.filter_list:
            f.write('<object "%s">\n' % "person")
            print namespace
            for i in namespace:
                f.write('  <filter name="%s"' % self.fix(i.get_name()))
                if i.get_invert():
                    f.write(' invert="1"')
                f.write(' function="%s"' % i.get_logical_op())
                comment = i.get_comment()
                if comment:
                    f.write(' comment="%s"' % self.fix(comment))
                f.write('>\n')
                for rule in i.get_rules():
                    rule_module_name = rule.__module__
                    rule_class_name = rule.__class__.__name__
                    rule_save_name = "%s.%s" % (rule_module_name,rule_class_name)
                    f.write('    <rule class="%s">\n' % rule_save_name)
                    for v in rule.values():
                        f.write('      <arg value="%s"/>\n' % self.fix(v))
                    f.write('    </rule>\n')
                f.write('  </filter>\n')
            f.write('</object>\n')
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
        self.namespace = "person"
        
    def setDocumentLocator(self,locator):
        self.locator = locator

    def startElement(self,tag,attrs):
        if tag == "object":
            if attrs.has_key('type'):
                self.namespace = attrs['type']
            else:
                self.namespace = "generic"
        elif tag == "filter":
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
            self.gfilter_list.add(self.namespace,self.f)
        elif tag == "rule":
            save_name = attrs['class']
            if save_name in old_names_2_class.keys():
                self.r = old_names_2_class[save_name]
            else:
                mc_match = save_name.split('.')
                if len(mc_match) != 2:
                    # rule has an old style name, that is not in old_names_2_class
                    # or is not in the format "module.class"
                    print "ERROR: Filter rule '%s' in filter '%s' not found!" % (
                            save_name,self.f.get_name())
                    self.r = None
                    return
                module_name,class_name = mc_match
                try:
                    if module_name == self.__module__:
                        exec 'self.r = %s' % class_name
                    else:
                        exec 'import %s' % module_name
                        exec 'self.r = %s.%s' % (module_name,class_name)
                except (ImportError,NameError):
                    print "ERROR: Filter rule '%s' in filter '%s' not found!" % (
                            save_name,self.f.get_name())
                    self.r = None
                    return
            self.a = []
        elif tag == "arg":
            self.a.append(attrs['value'])

    def endElement(self,tag):
        if tag == "rule" and self.r != None:
            if len(self.r.labels) < len(self.a):
                print "WARNING: Invalid number of arguments in filter '%s'!" %\
                      self.f.get_name()
                nargs = len(self.r.labels)
                rule = self.r(self.a[0:nargs])
                self.f.add_rule(rule)
            elif len(self.r.labels) > len(self.a):
                print "ERROR: Invalid number of arguments in filter '%s'!" %\
                            self.f.get_name()
            else:
                rule = self.r(self.a)
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

    def apply(self,db,id_list=None):
        for rule in self.flist:
            #rule.set_list(self.param_list)
            #
            # The above breaks filters with more than one param
            # Need to change existing params one by one to keep
            # the correct number of arguments
            new_list = rule.list[:]
            for ix in range(len(self.param_list)):
                new_list[ix] = self.param_list[ix]
            rule.set_list(new_list)
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
            self.store.append(row=[filt.get_name()])
            self.map[filt.get_name()] = filt
            if default != "" and default == filt.get_name():
                active = cnt
            cnt += 1

        for filt in CustomFilters.get_filters():
            self.store.append(row=[filt.get_name()])
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
        key = unicode(self.store[active][0])
        return self.map[key]


class FilterStore(gtk.ListStore):

    def __init__(self,local_filters=[], namespace="generic",default=""):
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

        for filt in SystemFilters.get_filters(namespace) + CustomFilters.get_filters(namespace):
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
    
class FilterWidget:
    def __init__( self, uistate, on_apply, apply_done = None):
        self.on_apply_callback = on_apply
        self.apply_done_callback = apply_done
        self.uistate = uistate
        
    def build( self):
        self.filterbar = gtk.HBox()
        self.filterbar.set_spacing(4)
        self.filter_text = gtk.Entry()
        self.filter_label = gtk.Label('Label:')
        self.filter_list = gtk.ComboBox()
        self.filter_invert = gtk.CheckButton('Invert')
        self.filter_button = gtk.Button('Apply')
        self.filter_button.connect( 'clicked',self.apply_filter_clicked)
        self.filterbar.pack_start(self.filter_list,False)
        self.filterbar.pack_start(self.filter_label,False)
        self.filterbar.pack_start(self.filter_text,True)
        self.filterbar.pack_start(self.filter_invert,False)
        self.filterbar.pack_end(self.filter_button,False)

        self.filter_text.set_sensitive(False)

        return self.filterbar
        
    def setup_filter( self, default_filters, namespace="generic"):
        cell = gtk.CellRendererText()
        self.filter_list.clear()
        self.filter_list.pack_start(cell,True)
        self.filter_list.add_attribute(cell,'text',0)

        filter_list = []
        
        for f in default_filters:
            all = GenericFilter()
            rule = f[0](f[1])
            #print rule
            all.set_name( rule.name)
            all.add_rule( rule)
            filter_list.append(all)

        self.filter_model = FilterStore(filter_list, namespace)
        self.filter_list.set_model(self.filter_model)
        self.filter_list.set_active(self.filter_model.default_index())
        self.filter_list.connect('changed',self.on_filter_name_changed)
        self.filter_text.set_sensitive(False)
        self.DataFilter = filter_list[self.filter_model.default_index()]
        
    def apply_filter_clicked(self,ev=None):
        print "apply_filter_clicked"
        index = self.filter_list.get_active()
        self.DataFilter = self.filter_model.get_filter(index)
        if self.DataFilter.need_param:
            qual = unicode(self.filter_text.get_text())
            self.DataFilter.set_parameter(qual)
        self.apply_filter()
        if self.apply_done_callback:
            self.apply_done_callback()

    def on_filter_name_changed(self,obj):
        print "on_filter_name_changed"
        index = self.filter_list.get_active()
        mime_filter = self.filter_model.get_filter(index)
        qual = mime_filter.need_param
        if qual:
            self.filter_text.show()
            self.filter_text.set_sensitive(True)
            self.filter_label.show()
            self.filter_label.set_text(mime_filter.get_rules()[0].labels[0])
        else:
            self.filter_text.hide()
            self.filter_text.set_sensitive(False)
            self.filter_label.hide()

    def apply_filter(self,current_model=None):
        self.uistate.status_text(_('Updating display...'))
        self.on_apply_callback()
        self.uistate.modify_statusbar()

    def get_filter( self):
        print "get_filter"
        #print self.DataFilter.flist[0]
        return self.DataFilter
        
    def inverted( self):
        return self.filter_invert.get_active()

    def show( self):
        self.filterbar.show()

    def hide( self):
        self.filterbar.hide()
    
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

#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2003  Donald N. Allingham
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
try:
    from xml.sax import make_parser,handler,SAXParseException
except:
    from _xmlplus.sax import make_parser,handler,SAXParseException

#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
import os
from string import find,join

import gtk

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import const
import RelLib
import Date
import Calendar
from gettext import gettext as _
from Utils import for_each_ancestor

#-------------------------------------------------------------------------
#
# date_cmp
#
#-------------------------------------------------------------------------
def date_cmp(rule,value):
    sd = rule.get_start_date()
    s = sd.mode
    if s == Calendar.BEFORE:
        return Date.compare_dates(rule,value) == 1
    elif s == Calendar.AFTER:
        return Date.compare_dates(rule,value) == -1
    elif sd.month == Date.UNDEF and sd.year != Date.UNDEF:
        return sd.year == value.get_start_date().year
    else:
        return Date.compare_dates(rule,value) == 0

#-------------------------------------------------------------------------
#
# Rule
#
#-------------------------------------------------------------------------
class Rule:
    """Base rule class"""

    labels = []
    
    def __init__(self,list):
        assert type(list) == type([]), "Argument is not a list"
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
                v.append('%s="%s"' % (_(self.labels[i]),self.list[i]))
        return join(v,'; ')

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

    def apply(self,db,p):
        return 1

#-------------------------------------------------------------------------
#
# RelationshipPathBetween
#
#-------------------------------------------------------------------------
class RelationshipPathBetween(Rule):
    """Rule that checks for a person that is a descendant of a specified person
    not more than N generations away"""

    labels = [ _('ID:'), _('ID:') ]
    
    def __init__(self,list):
        Rule.__init__(self,list)
        self.init = 0
        self.map = {}

    def name(self):
        return "Relationship path between two people"

    def category(self): 
        return _('Relationship filters')

    def description(self):
        return _("Matches the ancestors of two people back to a common ancestor, producing "
                 "the relationship path between two people.")

    def desc_list(self, p, map, first):
        if not first:
            map[p.getId()] = 1
        
        for fam in p.getFamilyList():
            for child in fam.getChildList():
                self.desc_list(child,map,0)
    
    def apply_filter(self,rank,person,plist,pmap):
        if person == None:
            return
        plist.append(person)
        pmap[person.getId()] = rank
        
        family = person.getMainParents()
        if family != None:
            self.apply_filter(rank+1,family.getFather(),plist,pmap)
            self.apply_filter(rank+1,family.getMother(),plist,pmap)

    def apply(self,db,p):
        if not self.init:
            self.init = 1
            root1 = db.getPerson(self.list[0])
            root2 = db.getPerson(self.list[1])
            self.init_list(root1,root2)
        return self.map.has_key(p.getId())

    def init_list(self,p1,p2):

        firstMap = {}
        firstList = []
        secondMap = {}
        secondList = []
        common = []
        rank = 9999999

        self.apply_filter(0,p1,firstList,firstMap)
        self.apply_filter(0,p2,secondList,secondMap)
        
        for person in firstList:
            if person in secondList:
                new_rank = firstMap[person.getId()]
                if new_rank < rank:
                    rank = new_rank
                    common = [ person ]
                elif new_rank == rank:
                    common.append(person)

        path1 = { p1.getId() : 1}
        path2 = { p2.getId() : 1}

        print common[0].getId()
        print common[1].getId()
        
        for person in common:
            new_map = {}
            self.desc_list(person,new_map,1)
            self.get_intersection(path1,firstMap,new_map)
            self.get_intersection(path2,secondMap,new_map)

        print "Common Ancestor desc"
        print new_map
        print "p1 ancestors"
        print path1
        print "p2 ancestors"
        print path2
        
        for e in path1:
            self.map[e] = 1
        for e in path2:
            self.map[e] = 1
        for e in common:
            self.map[e.getId()] = 1

        print path1
        print path2
        print self.map

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

    def apply(self,db,p):
        return p.getId() == self.list[0]

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

    def apply(self,db,p):
        return p.getComplete() == 1


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

    def apply(self,db,p):
        return p.getGender() == RelLib.Person.female

#-------------------------------------------------------------------------
#
# IsDescendantOf
#
#-------------------------------------------------------------------------
class IsDescendantOf(Rule):
    """Rule that checks for a person that is a descendant
    of a specified person"""

    labels = [ _('ID:'), _('Inclusive:') ]
    
    def __init__(self,list):
        Rule.__init__(self,list)
        self.init = 0
        self.map = {}

    def name(self):
        return 'Is a descendant of'

    def category(self): 
        return _('Descendant filters')
    
    def description(self):
        return _('Matches all descendants for the specified person')

    def apply(self,db,p):
        self.orig = p
        try:
            if int(self.list[1]):
                first = 0
            else:
                first = 1
        except IndexError:
            first = 1

        if not self.init:
            self.init = 1
            root = db.getPerson(self.list[0])
            self.init_list(root,first)
        return self.map.has_key(p.getId())

    def init_list(self,p,first):
        if not first:
            self.map[p.getId()] = 1
        
        for fam in p.getFamilyList():
            for child in fam.getChildList():
                self.init_list(child,0)

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
    
    def apply(self,db,p):
        self.orig = p
        try:
            if int(self.list[1]):
                first = 0
            else:
                first = 1
        except IndexError:
            first = 1

        if not self.init:
            self.init = 1
            filter = MatchesFilter(self.list)
            for person in db.getPersonMap ().values ():
                if filter.apply (db, person):
                    self.init_list (person, first)
        return self.map.has_key(p.getId())

#-------------------------------------------------------------------------
#
# IsLessThanNthGenerationDescendantOf
#
#-------------------------------------------------------------------------
class IsLessThanNthGenerationDescendantOf(Rule):
    """Rule that checks for a person that is a descendant of a specified person
    not more than N generations away"""

    labels = [ _('ID:'), _('Number of generations:') ]
    
    def __init__(self,list):
        Rule.__init__(self,list)
        self.init = 0
        self.map = {}

    def name(self):
        return 'Is a descendant of person not more than N generations away'

    def category(self): 
        return _('Descendant filters')

    def description(self):
        return _("Matches people that are descendants of a specified person "
                 "not more than N generations away")
    
    def apply(self,db,p):
        self.orig = p

        if not self.init:
            self.init = 1
            root = db.getPerson(self.list[0])
            self.init_list(root,0)
        return self.map.has_key(p.getId())

    def init_list(self,p,gen):
        if gen:
            self.map[p.getId()] = 1
            if gen >= int(self.list[1]):
                return

        for fam in p.getFamilyList():
            for child in fam.getChildList():
                self.init_list(child,gen+1)

#-------------------------------------------------------------------------
#
# IsMoreThanNthGenerationDescendantOf
#
#-------------------------------------------------------------------------
class IsMoreThanNthGenerationDescendantOf(Rule):
    """Rule that checks for a person that is a descendant of a specified person
    at least N generations away"""

    labels = [ _('ID:'), _('Number of generations:') ]
    
    def __init__(self,list):
        Rule.__init__(self,list)
        self.init = 0
        self.map = {}

    def name(self):
        return 'Is a descendant of person at least N generations away'

    def description(self):
        return _("Matches people that are descendants of a specified "
                 "person at least N generations away")
    
    def category(self):
        return _("Descendant filters")

    def apply(self,db,p):
        self.orig = p

        if not self.init:
            self.init = 1
            root = db.getPerson(self.list[0])
            self.init_list(root,0)
        return self.map.has_key(p.getId())

    def init_list(self,p,gen):
        if gen >= int(self.list[1]):
            self.map[p.getId()] = 1

        for fam in p.getFamilyList():
            for child in fam.getChildList():
                self.init_list(child,gen+1)

#-------------------------------------------------------------------------
#
# IsChildOfFilterMatch
#
#-------------------------------------------------------------------------
class IsChildOfFilterMatch(Rule):
    """Rule that checks for a person that is a child
    of someone matched by a filter"""

    labels = [ _('Filter name:') ]

    def __init__(self,list):
        Rule.__init__(self,list)
        self.init = 0
        self.map = {}

    def name(self):
        return 'Is a child of filter match'

    def description(self):
        return _("Matches the person that is a child of someone matched by a filter")

    def category(self):
        return _('Family filters')

    def apply(self,db,p):
        self.orig = p

        if not self.init:
            self.init = 1
            filter = MatchesFilter(self.list)
            for person in db.getPersonMap ().values ():
                if filter.apply (db, person):
                    self.init_list (person)
        return self.map.has_key(p.getId())

    def init_list(self,p):
        for fam in p.getFamilyList():
            for child in fam.getChildList():
                self.map[child.getId()] = 1

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
    
    def apply(self,db,p):
        self.map = {}
        self.orig = p
        return self.search(p,1)

    def search(self,p,val):
        if p.getId() == self.list[0]:
            self.map[p.getId()] = 1
            return 1
        for (f,r1,r2) in p.getParentList():
            for p1 in [f.getMother(),f.getFather()]:
                if p1:
                    if self.search(p1,0):
                        return 1
        if val:
            for fm in p.getFamilyList():
                if p == fm.getFather():
                    s = fm.getMother()
                else:
                    s = fm.getFather()
                if s:
                    if self.search(s,0):
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

    def __init__(self,list):
        Rule.__init__(self,list)
        self.init = 0
        self.map = {}
    
    def name(self):
        return 'Is an ancestor of'

    def description(self):
        return _("Matches people that are ancestors of a specified person")
    
    def category(self):
        return _("Ancestral filters")

    def apply(self,db,p):
        """Assume that if 'Inclusive' not defined, assume inclusive"""
        self.orig = p
        try:
            if int(self.list[1]):
                first = 0
            else:
                first = 1
        except IndexError:
            first = 1
            
        if not self.init:
            self.init = 1
            root = db.getPerson(self.list[0])
            self.init_ancestor_list(root,first)
        return self.map.has_key(p.getId())

    def init_ancestor_list(self,p,first):
        if not first:
            self.map[p.getId()] = 1
        
        fam = p.getMainParents()
        if fam:
            f = fam.getFather()
            m = fam.getMother()
        
            if f:
                self.init_ancestor_list(f,0)
            if m:
                self.init_ancestor_list(m,0)

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
    
    def name(self):
        return 'Is an ancestor of filter match'

    def description(self):
        return _("Matches people that are ancestors "
            "of someone matched by a filter")
    
    def category(self):
        return _("Ancestral filters")

    def apply(self,db,p):
        self.orig = p
        try:
            if int(self.list[1]):
                first = 0
            else:
                first = 1
        except IndexError:
            first = 1
            
        if not self.init:
            self.init = 1
            filter = MatchesFilter(self.list[0])
            for person in db.getPersonMap ().values ():
                if filter.apply (db, person):
                    self.init_ancestor_list (person,first)
        return self.map.has_key(p.getId())

#-------------------------------------------------------------------------
#
# IsLessThanNthGenerationAncestorOf
#
#-------------------------------------------------------------------------
class IsLessThanNthGenerationAncestorOf(Rule):
    """Rule that checks for a person that is an ancestor of a specified person
    not more than N generations away"""

    labels = [ _('ID:'), _('Number of generations:') ]

    def __init__(self,list):
        Rule.__init__(self,list)
        self.init = 0
        self.map = {}
    
    def name(self):
        return 'Is an ancestor of person not more than N generations away'

    def description(self):
        return _("Matches people that are ancestors "
            "of a specified person not more than N generations away")
    
    def category(self):
        return _("Ancestral filters")

    def apply(self,db,p):
        self.orig = p
        if not self.init:
            self.init = 1
            root = db.getPerson(self.list[0])
            self.init_ancestor_list(root,0)
        return self.map.has_key(p.getId())

    def init_ancestor_list(self,p,gen):
#        if self.map.has_key(p.getId()) == 1:
#            loop_error(self.orig,p)
        if gen:
            self.map[p.getId()] = 1
            if gen >= int(self.list[1]):
                return
        
        fam = p.getMainParents()
        if fam:
            f = fam.getFather()
            m = fam.getMother()
        
            if f:
                self.init_ancestor_list(f,gen+1)
            if m:
                self.init_ancestor_list(m,gen+1)

#-------------------------------------------------------------------------
#
# IsMoreThanNthGenerationAncestorOf
#
#-------------------------------------------------------------------------
class IsMoreThanNthGenerationAncestorOf(Rule):
    """Rule that checks for a person that is an ancestor of a specified person
    at least N generations away"""

    labels = [ _('ID:'), _('Number of generations:') ]

    def __init__(self,list):
        Rule.__init__(self,list)
        self.init = 0
        self.map = {}
    
    def name(self):
        return 'Is an ancestor of person at least N generations away'

    def description(self):
        return _("Matches people that are ancestors "
            "of a specified person at least N generations away")
    
    def category(self):
        return _("Ancestral filters")

    def apply(self,db,p):
        self.orig = p
        if not self.init:
            self.init = 1
            root = db.getPerson(self.list[0])
            self.init_ancestor_list(root,0)
        return self.map.has_key(p.getId())

    def init_ancestor_list(self,p,gen):
#        if self.map.has_key(p.getId()) == 1:
#            loop_error(self.orig,p)
        if gen >= int(self.list[1]):
            self.map[p.getId()] = 1
        
        fam = p.getMainParents()
        if fam:
            f = fam.getFather()
            m = fam.getMother()
        
            if f:
                self.init_ancestor_list(f,gen+1)
            if m:
                self.init_ancestor_list(m,gen+1)

#-------------------------------------------------------------------------
#
# IsParentOfFilterMatch
#
#-------------------------------------------------------------------------
class IsParentOfFilterMatch(Rule):
    """Rule that checks for a person that is a parent
    of someone matched by a filter"""

    labels = [ _('Filter name:') ]

    def __init__(self,list):
        Rule.__init__(self,list)
        self.init = 0
        self.map = {}

    def name(self):
        return 'Is a parent of filter match'

    def description(self):
        return _("Matches the person that is a parent of someone matched by a filter")

    def category(self):
        return _('Family filters')

    def apply(self,db,p):
        self.orig = p

        if not self.init:
            self.init = 1
            filter = MatchesFilter(self.list)
            for person in db.getPersonMap ().values ():
                if filter.apply (db, person):
                    self.init_list (person)
        return self.map.has_key(p.getId())

    def init_list(self,p):
        for fam in p.getMainParents():
            for parent in [fam.getFather (), fam.getMother ()]:
                if parent:
                    self.map[parent.getId()] = 1

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

    def __init__(self,list):
        Rule.__init__(self,list)
        # Keys in `ancestor_cache' are ancestors of list[0].
        # We delay the computation of ancestor_cache until the
        # first use, because it's not uncommon to instantiate
        # this class and not use it.
        self.ancestor_cache = {}

    def init_ancestor_cache(self,db):
        # list[0] is an Id, but we need to pass a Person to for_each_ancestor.
        p = db.getPerson(self.list[0])
        if p:
            def init(self,pid): self.ancestor_cache[pid] = 1
            for_each_ancestor([p],init,self)

    def apply(self,db,p):
        # On the first call, we build the ancestor cache for the
        # reference person.   Then, for each person to test,
        # we browse his ancestors until we found one in the cache.
        if len(self.ancestor_cache) == 0:
            self.init_ancestor_cache(db)
        return for_each_ancestor([p],
                                 lambda self,p: self.ancestor_cache.has_key(p),
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
        filter = MatchesFilter(self.list)
        def init(self,pid): self.ancestor_cache[pid] = 1
        for p in db.getPersonMap ().values ():
            if (not self.ancestor_cache.has_key (p.getId ())
                and filter.apply (db, p)):
                for_each_ancestor([p],init,self)

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

    def apply(self,db,p):
        return p.getGender() == RelLib.Person.male

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
        if self.list[0]:
            self.date = Date.Date()
            self.date.set(self.list[0])
        else:
            self.date = None

    def name(self):
        return 'Has the personal event'

    def description(self):
        return _("Matches the person with a personal event of a particular value")

    def category(self):
        return _('Event filters')

    def apply(self,db,p):
        for event in p.getEventList():
            val = 1
            if self.list[0] and event.getName() != self.list[0]:
                val = 0
            if self.list[3] and find(event.getDescription().upper(),
                                     self.list[3].upper())==-1:
                val = 0
            if self.date:
                if date_cmp(self.date,event.getDateObj()):
                    val = 0
            if self.list[2]:
                pn = event.getPlaceName()
                if find(pn.upper(),self.list[2].upper()) == -1:
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
        if self.list[0]:
            self.date = Date.Date()
            self.date.set(self.list[0])
        else:
            self.date = None

    def name(self):
        return 'Has the family event'

    def description(self):
        return _("Matches the person with a family event of a particular value")

    def category(self):
        return _('Event filters')

    def apply(self,db,p):
        for f in p.getFamilyList():
            for event in f.getEventList():
                val = 1
                if self.list[0] and event.getName() != self.list[0]:
                    val = 0
                v = self.list[3]
                if v and find(event.getDescription().upper(),v.upper())==-1:
                    val = 0
                if self.date:
                    if date_cmp(self.date,event.getDateObj()):
                        val = 0
                pn = event.getPlaceName().upper()
                if self.list[2] and find(pn,self.list[2].upper()) == -1:
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

    def apply(self,db,p):
        rel_type = 0
        cnt = 0
        num_rel = len(p.getFamilyList())

        # count children and look for a relationship type match
        for f in p.getFamilyList():
            cnt = cnt + len(f.getChildList())
            if self.list[1] and f.getRelationship() == self.list[1]:
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
        if self.list[0]:
            self.date = Date.Date()
            self.date.set(self.list[0])
        else:
            self.date = None
        
    def name(self):
        return 'Has the birth'

    def description(self):
        return _("Matches the person with a birth of a particular value")

    def category(self):
        return _('Event filters')

    def apply(self,db,p):
        event = p.getBirth()
        ed = event.getDescription().upper()
        if len(self.list) > 2 and find(ed,self.list[2].upper())==-1:
            return 0
        if self.date:
            if date_cmp(self.date,event.getDateObj()) == 0:
                return 0
        pn = event.getPlaceName().upper()
        if len(self.list) > 1 and find(pn,self.list[1].upper()) == -1:
            return 0
        return 1

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
        if self.list[0]:
            self.date = Date.Date()
            self.date.set(self.list[0])
        else:
            self.date = None

    def name(self):
        return 'Has the death'

    def description(self):
        return _("Matches the person with a death of a particular value")

    def category(self):
        return _('Event filters')

    def apply(self,db,p):
        event = p.getDeath()
        ed = event.getDescription().upper()
        if self.list[2] and find(ed,self.list[2].upper())==-1:
            return 0
        if self.date:
            if date_cmp(self.date,event.getDateObj()) == 0:
                return 0
        pn = p.getPlaceName().upper()
        if self.list[1] and find(pn,self.list[1].upper()) == -1:
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

    def apply(self,db,p):
        for event in p.getAttributes():
            if self.list[0] and event.getType() != self.list[0]:
                return 0
            ev = event.getValue().upper()
            if self.list[1] and find(ev,self.list[1].upper())==-1:
                return 0
        return 1

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

    def apply(self,db,p):
        for f in p.getFamilyList():
            for event in f.getAttributes():
                val = 1
                if self.list[0] and event.getType() != self.list[0]:
                    val = 0
                ev = event.getValue().upper()
                if self.list[1] and find(ev,self.list[1].upper())==-1:
                    val = 0
                if val == 1:
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

    def apply(self,db,p):
        self.f = self.list[0]
        self.l = self.list[1]
        self.s = self.list[2]
        self.t = self.list[3]
        for name in [p.getPrimaryName()] + p.getAlternateNames():
            val = 1
            if self.f and find(name.getFirstName().upper(),self.f.upper()) == -1:
                val = 0
            if self.l and find(name.getSurname().upper(),self.l.upper()) == -1:
                val = 0
            if self.s and find(name.getSuffix().upper(),self.s.upper()) == -1:
                val = 0
            if self.t and find(name.getTitle().upper(),self.t.upper()) == -1:
                val = 0
            if val == 1:
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

    def name(self):
        return 'Matches the filter named'

    def apply(self,db,p):
        for filter in SystemFilters.get_filters():
            if filter.get_name() == self.list[0]:
                return filter.check(p)
        for filter in CustomFilters.get_filters():
            if filter.get_name() == self.list[0]:
                return filter.check(db,p)
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

    def apply(self,db,p):
        filter = MatchesFilter (self.list)
        for family in p.getFamilyList ():
            for spouse in [family.getFather (), family.getMother ()]:
                if not spouse:
                    continue
                if spouse == p:
                    continue
                if filter.apply (db, spouse):
                    return 1
        return 0

#-------------------------------------------------------------------------
#
# GenericFilter
#
#-------------------------------------------------------------------------
class GenericFilter:
    """Filter class that consists of several rules"""
    
    def __init__(self,source=None):
        if source:
            self.flist = source.flist[:]
            self.name = source.name
            self.comment = source.comment
            self.logical_op = source.logical_op
            self.invert = source.invert
        else:
            self.flist = []
            self.name = ''
            self.comment = ''
            self.logical_op = 'and'
            self.invert = 0

    def set_logical_op(self,val):
        if val in const.logical_functions:
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

    def check_or(self,db,p):
        test = 0
        for rule in self.flist:
            test = test or rule.apply(db,p)
            if test:
                break
        if self.invert:
            return not test
        else:
            return test

    def check_xor(self,db,p):
        test = 0
        for rule in self.flist:
            temp = rule.apply(db,p)
            test = ((not test) and temp) or (test and (not temp))
        if self.invert:
            return not test
        else:
            return test

    def check_one(self,db,p):
        count = 0
        for rule in self.flist:
            if rule.apply(db,p):
                count = count + 1
                if count > 1:
                    break
        if self.invert:
            return count != 1
        else:
            return count == 1

    def check_and(self,db,p):
        test = 1
        for rule in self.flist:
            test = test and rule.apply(db,p)
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

    def check(self,db,p):
        return self.get_check_func()(db,p)

    def apply(self,db,list):
        m = self.get_check_func()
        res = []
        for p in list:
            if m(db,p):
                res.append(p)
        return res


#-------------------------------------------------------------------------
#
# Name to class mappings
#
#-------------------------------------------------------------------------
tasks = {
    _("Everyone")                             : Everyone,
    _("Has the Id")                           : HasIdOf,
    _("Has a name")                           : HasNameOf,
    _("Has the relationships")                : HasRelationship,
    _("Has the death")                        : HasDeath,
    _("Has the birth")                        : HasBirth,
    _("Is a descendant of")                   : IsDescendantOf,
    _("Is a descendant family member of")     : IsDescendantFamilyOf,
    _("Is a descendant of filter match")      : IsDescendantOfFilterMatch,
    _("Is a descendant of person not more than N generations away")
                                              : IsLessThanNthGenerationDescendantOf,
    _("Is a descendant of person at least N generations away")
                                              : IsMoreThanNthGenerationDescendantOf,
    _("Is a child of filter match")           : IsChildOfFilterMatch,
    _("Is an ancestor of")                    : IsAncestorOf,
    _("Is an ancestor of filter match")       : IsAncestorOfFilterMatch,
    _("Is an ancestor of person not more than N generations away")
                                              : IsLessThanNthGenerationAncestorOf,
    _("Is an ancestor of person at least N generations away")
                                              : IsMoreThanNthGenerationAncestorOf,
    _("Is a parent of filter match")          : IsParentOfFilterMatch,
    _("Has a common ancestor with")           : HasCommonAncestorWith,
    _("Has a common ancestor with filter match")
                                              : HasCommonAncestorWithFilterMatch,
    _("Is a female")                          : IsFemale,
    _("Is a male")                            : IsMale,
    _("Has complete record")                  : HasCompleteRecord,
    _("Has the personal event")               : HasEvent,
    _("Has the family event")                 : HasFamilyEvent,
    _("Has the personal attribute")           : HasAttribute,
    _("Has the family attribute")             : HasFamilyAttribute,
    _("Matches the filter named")             : MatchesFilter,
    _("Is spouse of filter match")            : IsSpouseOfFilterMatch,
    _("Relationship path between two people") : RelationshipPathBetween,
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
    
    def add(self,filter):
        self.filter_list.append(filter)
        
    def load(self):
        try:
            parser = make_parser()
            parser.setContentHandler(FilterParser(self))
            if self.file[0:7] != "file://":
                parser.parse("file://" + self.file)
            else:
                parser.parse(self.file)
        except (IOError,OSError,SAXParseException):
            pass

    def fix(self,line):
        l = line.strip()
        l = l.replace('&','&amp;')
        l = l.replace('>','&gt;')
        l = l.replace('<','&lt;')
        return l.replace('"','&quot;')

    def save(self):
#        try:
#            f = open(self.file,'w')
#        except:
#            return

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
            name = _(cname)
            self.a = []
            self.cname = tasks[name]
        elif tag == "arg":
            self.a.append(attrs['value'])

    def endElement(self,tag):
        if tag == "rule":
            rule = self.cname(self.a)
            self.f.add_rule(rule)
            
    def characters(self, data):
        pass

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

def build_filter_menu(local_filters = [], default=""):
    menu = gtk.Menu()

    active = 0
    cnt = 0
    for filter in local_filters:
        menuitem = gtk.MenuItem(filter.get_name())
        menuitem.show()
        menu.append(menuitem)
        menuitem.set_data("filter", filter)
        if default != "" and default == filter.get_name():
            active = cnt
        cnt += 1
        
    for filter in SystemFilters.get_filters():
        menuitem = gtk.MenuItem(_(filter.get_name()))
        menuitem.show()
        menu.append(menuitem)
        menuitem.set_data("filter", filter)
        if default != "" and default == filter.get_name():
            active = cnt
        cnt += 1

    for filter in CustomFilters.get_filters():
        menuitem = gtk.MenuItem(_(filter.get_name()))
        menuitem.show()
        menu.append(menuitem)
        menuitem.set_data("filter", filter)
        if default != "" and default == filter.get_name():
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

#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002  Donald N. Allingham
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
import types
import os
from string import find,join

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from RelLib import *
from Date import Date

#-------------------------------------------------------------------------
#
# Rule
#
#-------------------------------------------------------------------------
class Rule:
    """Base rule class"""

    labels = []
    
    def __init__(self,list):
        assert(type(list) == type([]),"Argument is not a list")
        self.list = list

    def values(self):
        return self.list
    
    def name(self): 
        return 'None'
    
    def check(self):
        return len(self.list) == len(self.labels)

    def apply(self,p):
        return 1

    def display_values(self):
        v = []
        for i in range(0,len(self.list)):
            if self.list[i]:
                v.append('%s="%s"' % (self.labels[i],self.list[i]))
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

    def apply(self,p):
        return 1

#-------------------------------------------------------------------------
#
# HasIdOf
#
#-------------------------------------------------------------------------
class HasIdOf(Rule):
    """Rule that checks for a person with a specific GID"""

    labels = [ 'ID' ]
    
    def name(self):
        return 'Has the Id'

    def apply(self,p):
        return p.getId() == self.list[0]

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

    def apply(self,p):
        return p.getGender() == Person.female

#-------------------------------------------------------------------------
#
# IsDescendantOf
#
#-------------------------------------------------------------------------
class IsDescendantOf(Rule):
    """Rule that checks for a person that is a descendant of a specified person"""

    labels = ['ID']
    
    def name(self):
        return 'Is a descendant of'

    def apply(self,p):
        return self.search(p)

    def search(self,p):
        if p.getId() == self.list[0]:
            return 1

        for (f,r1,r2) in p.getParentList():
            for p1 in [f.getMother(),f.getFather()]:
                if p1:
                    if self.search(p1):
                        return 1
        return 0

#-------------------------------------------------------------------------
#
# IsAncestorOf
#
#-------------------------------------------------------------------------
class IsAncestorOf(Rule):
    """Rule that checks for a person that is an ancestor of a specified person"""

    labels = ['ID']
    
    def name(self):
        return 'Is an ancestor of'

    def apply(self,p):
        return self.search(p)

    def search(self,p):
        if p.getId() == self.list[0]:
            return 1

        for f in p.getFamilyList():
            for p1 in f.getChildList():
                if p1:
                    if self.search(p1):
                        return 1
        return 0

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

    def apply(self,p):
        return p.getGender() == Person.male

#-------------------------------------------------------------------------
#
# HasEvent
#
#-------------------------------------------------------------------------
class HasEvent(Rule):
    """Rule that checks for a person with a particular value"""

    labels = [ 'Event', 'Date', 'Place', 'Description' ]
    
    def name(self):
        return 'Has the event'

    def apply(self,p):
        for event in [p.getBirth(),p.getDeath()] + p.getEventList():
            if self.list[0] and event.getName() != self.list[0]:
                return 0
            if self.list[3] and find(event.getDescription(),self.list[3])==-1:
                return 0
            if self.list[1]:
                try:
                    d = Date.Date(self.list[1])
                except:
                    return 0
                if Date.compare_dates(d,event.getDateObj()):
                    return 0
            if self.list[2] and find(p.getPlaceName(),self.list[2]) == -1:
                return 0
        return 1

#-------------------------------------------------------------------------
#
# HasAttribute
#
#-------------------------------------------------------------------------
class HasAttribute(Rule):
    """Rule that checks for a person with a particular attribute"""

    labels = [ 'Attribute', 'Value' ]
    
    def name(self):
        return 'Has the attribute'

    def apply(self,p):
        for event in p.getAttributes():
            if self.list[0] and event.getType() != self.list[0]:
                return 0
            if self.list[1] and find(event.getValue(),self.list[1])==-1:
                return 0
        return 1

#-------------------------------------------------------------------------
#
# HasNameOf
#
#-------------------------------------------------------------------------
class HasNameOf(Rule):
    """Rule that checks for full or partial name matches"""

    labels = ['Given Name','Surname','Suffix','Title']
    
    def name(self):
        return 'Has a name'
    
    def apply(self,p):
        self.f = self.list[0]
        self.l = self.list[1]
        self.s = self.list[2]
        self.t = self.list[3]
        for name in [p.getPrimaryName()] + p.getAlternateNames():
            if self.f and find(name.getFirstName(),self.f) == -1:
                return 0
            if self.l and find(name.getSurname(),self.l) == -1:
                return 0
            if self.s and find(name.getSuffix(),self.s) == -1:
                return 0
            if self.t and find(name.getTitle(),self.t) == -1:
                return 0
        return 1
    
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
        else:
            self.flist = []
            self.name = 'NoName'
            self.comment = ''

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

    def set_rules(self,rules):
        self.flist = rules

    def get_rules(self):
        return self.flist
    
    def apply(self,list):
        result = []
        for p in list:
            for rule in self.flist:
                if rule.apply(p) == 0:
                    break
            else:
                result.append(p)
        return result

#-------------------------------------------------------------------------
#
# Name to class mappings
#
#-------------------------------------------------------------------------
tasks = {
    "Everyone"             : Everyone,
    "Has the Id"           : HasIdOf,
    "Has a name"           : HasNameOf,
    "Is the descendant of" : IsDescendantOf,
    "Is an ancestor of"    : IsAncestorOf,
    "Is a female"          : IsFemale,
    "Is a male"            : IsMale,
    "Has the event"        : HasEvent,
    "Has the attribute"    : HasAttribute,
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
            parser.parse(self.file)
        except (IOError,OSError,SAXParseException):
            pass

    def save(self):
        f = open(self.file,'w')
        f.write("<?xml version=\"1.0\" encoding=\"iso-8859-1\"?>\n")
        f.write('<filters>\n')
        for i in self.filter_list:
            f.write('  <filter name="%s"' % i.get_name())
            comment = i.get_comment()
            if comment:
                f.write(' comment="%s"' % comment)
            f.write('>\n')
            for rule in i.get_rules():
                f.write('    <rule class="%s">\n' % rule.name())
                for v in rule.values():
                    f.write('      <arg value="%s"/>\n' % v)
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
            if attrs.has_key('comment'):
                self.f.set_comment(attrs['comment'])
            self.gfilter_list.add(self.f)
        elif tag == "rule":
            name = attrs['class']
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

if __name__ == '__main__':

    g = GenericFilter()
    g.set_name("Everyone")
    rule = Everyone([])
    g.add_rule(rule)

    l = GenericFilterList('/home/dona/.gramps/custom_filters.xml')
    l.load()
    l.add(g)
    l.save()


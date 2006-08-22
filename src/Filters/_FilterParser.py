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
from xml.sax import handler

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from _GenericFilter import GenericFilterFactory
import Rules

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
        self.namespace = "Person"
        
    def setDocumentLocator(self,locator):
        self.locator = locator

    def startElement(self,tag,attrs):
        if tag == "object":
            if attrs.has_key('type'):
                self.namespace = attrs['type']
                if self.namespace == 'Media':
                    self.namespace = 'MediaObject'
            else:
                self.namespace = "generic"
        elif tag == "filter":
            self.f = GenericFilterFactory(self.namespace)()
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
            if attrs.has_key('invert'):
                self.f.set_invert(attrs['invert'])
            if attrs.has_key('comment'):
                self.f.set_comment(attrs['comment'])
            self.gfilter_list.add(self.namespace,self.f)
        elif tag == "rule":
            save_name = attrs['class']
            if save_name in old_names_2_class.keys():
                self.r = old_names_2_class[save_name]
            else:
                try:
                    # First try to use fully qualified name
                    exec 'self.r = %s' % save_name
                except (ImportError, NameError, AttributeError ):
                    # Now try to use name from Rules.Namespace
                    mc_match = save_name.split('.')
                    try:
                        exec 'self.r = Rules.%s.%s' % (
                            self.namespace,mc_match[-1])
                    except (ImportError, NameError ):
                        print "ERROR: Filter rule '%s' in "\
                              "filter '%s' not found!"\
                              % (save_name,self.f.get_name())
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

#-------------------------------------------------------------------------
#
# Name to class mappings
#
#-------------------------------------------------------------------------
# This dict is mapping from old names to new names, so that the existing
# custom_filters.xml will continue working
old_names_2_class = {
    "Everyone"                      : Rules.Person.Everyone,
    "Is default person"             : Rules.Person.IsDefaultPerson,
    "Is bookmarked person"          : Rules.Person.IsBookmarked,
    "Has the Id"                    : Rules.Person.HasIdOf,
    "Has a name"                    : Rules.Person.HasNameOf,
    "Has the relationships"         : Rules.Person.HasRelationship,
    "Has the death"                 : Rules.Person.HasDeath,
    "Has the birth"                 : Rules.Person.HasBirth,
    "Is a descendant of"            : Rules.Person.IsDescendantOf,
    "Is a descendant family member of" : Rules.Person.IsDescendantFamilyOf,
    "Is a descendant of filter match": Rules.Person.IsDescendantOfFilterMatch,
    "Is a descendant of person not more than N generations away":
        Rules.Person.IsLessThanNthGenerationDescendantOf,
    "Is a descendant of person at least N generations away":
        Rules.Person.IsMoreThanNthGenerationDescendantOf,
    "Is an descendant of person at least N generations away" :
        Rules.Person.IsMoreThanNthGenerationDescendantOf,
    "Is a child of filter match"    : Rules.Person.IsChildOfFilterMatch,
    "Is an ancestor of"             : Rules.Person.IsAncestorOf,
    "Is an ancestor of filter match": Rules.Person.IsAncestorOfFilterMatch,
    "Is an ancestor of person not more than N generations away" : 
        Rules.Person.IsLessThanNthGenerationAncestorOf,
    "Is an ancestor of person at least N generations away":
        Rules.Person.IsMoreThanNthGenerationAncestorOf,
    "Is a parent of filter match"   : Rules.Person.IsParentOfFilterMatch,
    "Has a common ancestor with"    : Rules.Person.HasCommonAncestorWith,
    "Has a common ancestor with filter match" :
        Rules.Person.HasCommonAncestorWithFilterMatch,
    "Is a female"                   : Rules.Person.IsFemale,
    "Is a male"                     : Rules.Person.IsMale,
    "Has complete record"           : Rules.Person.HasCompleteRecord,
    "Has the personal event"        : Rules.Person.HasEvent,
    "Has the family event"          : Rules.Person.HasFamilyEvent,
    "Has the personal attribute"    : Rules.Person.HasAttribute,
    "Has the family attribute"      : Rules.Person.HasFamilyAttribute,
    "Has source of"                 : Rules.Person.HasSourceOf,
    "Matches the filter named"      : Rules.Person.HasSourceOf,
    "Is spouse of filter match"     : Rules.Person.IsSpouseOfFilterMatch,
    "Is a sibling of filter match"  : Rules.Person.IsSiblingOfFilterMatch,
    "Relationship path between two people" :
        Rules.Person.RelationshipPathBetween,
    "People who were adopted"       : Rules.Person.HaveAltFamilies,
    "People who have images"        : Rules.Person.HavePhotos,
    "People with children"          : Rules.Person.HaveChildren,
    "People with incomplete names"  : Rules.Person.IncompleteNames,
    "People with no marriage records" : Rules.Person.NeverMarried,
    "People with multiple marriage records": Rules.Person.MultipleMarriages,
    "People without a birth date"   : Rules.Person.NoBirthdate,
    "People with incomplete events" : Rules.Person.PersonWithIncompleteEvent,
    "Families with incomplete events" :Rules.Person.FamilyWithIncompleteEvent,
    "People probably alive"         : Rules.Person.ProbablyAlive,
    "People marked private"         : Rules.Person.PeoplePrivate,
    "Witnesses"                     : Rules.Person.IsWitness,
    "Has text matching substring of": Rules.Person.HasTextMatchingSubstringOf,
}

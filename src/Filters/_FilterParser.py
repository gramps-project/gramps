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
from _GenericFilter import GenericFilter
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
            self.gfilter_list.add(self.namespace,self.f)
        elif tag == "rule":
            save_name = attrs['class']
            if save_name in old_names_2_class.keys():
                self.r = old_names_2_class[save_name]
            else:
                try:
                    # First try to use fully qualified name
                    exec 'self.r = %s' % save_name
                except (ImportError,NameError,AttributeError):
                    # Now try to use name from Rules
                    mc_match = save_name.split('.')
                    try:
                        exec 'self.r = Rules.%s' % mc_match[-1]
                    except (ImportError,NameError):
                        print "ERROR: Filter rule '%s' in filter '%s' not found!"\
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
    "Everyone"                      : Rules.Everyone,
    "Is default person"             : Rules.IsDefaultPerson,
    "Is bookmarked person"          : Rules.IsBookmarked,
    "Has the Id"                    : Rules.HasIdOf,
    "Has a name"                    : Rules.HasNameOf,
    "Has the relationships"         : Rules.HasRelationship,
    "Has the death"                 : Rules.HasDeath,
    "Has the birth"                 : Rules.HasBirth,
    "Is a descendant of"            : Rules.IsDescendantOf,
    "Is a descendant family member of" : Rules.IsDescendantFamilyOf,
    "Is a descendant of filter match": Rules.IsDescendantOfFilterMatch,
    "Is a descendant of person not more than N generations away":
                                Rules.IsLessThanNthGenerationDescendantOf,
    "Is a descendant of person at least N generations away":
                                Rules.IsMoreThanNthGenerationDescendantOf,
    "Is an descendant of person at least N generations away" :
                                Rules.IsMoreThanNthGenerationDescendantOf,
    "Is a child of filter match"    : Rules.IsChildOfFilterMatch,
    "Is an ancestor of"             : Rules.IsAncestorOf,
    "Is an ancestor of filter match": Rules.IsAncestorOfFilterMatch,
    "Is an ancestor of person not more than N generations away" : 
                                Rules.IsLessThanNthGenerationAncestorOf,
    "Is an ancestor of person at least N generations away":
                                Rules.IsMoreThanNthGenerationAncestorOf,
    "Is a parent of filter match"   : Rules.IsParentOfFilterMatch,
    "Has a common ancestor with"    : Rules.HasCommonAncestorWith,
    "Has a common ancestor with filter match" :Rules.HasCommonAncestorWithFilterMatch,
    "Is a female"                   : Rules.IsFemale,
    "Is a male"                     : Rules.IsMale,
    "Has complete record"           : Rules.HasCompleteRecord,
    "Has the personal event"        : Rules.HasEvent,
    "Has the family event"          : Rules.HasFamilyEvent,
    "Has the personal attribute"    : Rules.HasAttribute,
    "Has the family attribute"      : Rules.HasFamilyAttribute,
    "Has source of"                 : Rules.HasSourceOf,
    "Matches the filter named"      : Rules.HasSourceOf,
    "Is spouse of filter match"     : Rules.IsSpouseOfFilterMatch,
    "Is a sibling of filter match"  : Rules.IsSiblingOfFilterMatch,
    "Relationship path between two people" : Rules.RelationshipPathBetween,
    "People who were adopted"       : Rules.HaveAltFamilies,
    "People who have images"        : Rules.HavePhotos,
    "People with children"          : Rules.HaveChildren,
    "People with incomplete names"  : Rules.IncompleteNames,
    "People with no marriage records" : Rules.NeverMarried,
    "People with multiple marriage records": Rules.MultipleMarriages,
    "People without a birth date"   : Rules.NoBirthdate,
    "People with incomplete events" : Rules.PersonWithIncompleteEvent,
    "Families with incomplete events" :Rules.FamilyWithIncompleteEvent,
    "People probably alive"         : Rules.ProbablyAlive,
    "People marked private"         : Rules.PeoplePrivate,
    "Witnesses"                     : Rules.IsWitness,
    "Has text matching substring of": Rules.HasTextMatchingSubstringOf,
}

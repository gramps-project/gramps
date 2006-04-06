# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2006  Donald N. Allingham
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

# Written by Alex Roitman, largely based on Relationship.py by Don Allingham
# and on valuable input from Jens Arvidsson

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------

import RelLib
import Relationship
import types
from gettext import gettext as _
from PluginUtils import register_relcalc

#-------------------------------------------------------------------------
#
# Swedish-specific definitions of relationships
#
#-------------------------------------------------------------------------

_cousin_level = [ "", "kusin", 
"tremänning", "fyrmänning", "femmänning", 
"sexmänning", "sjumänning", "åttamänning",
"niomänning", "tiomänning", "elvammänning", 
"tolvmänning", "trettonmänning", "fjortonmänning",
"femtonmänning", "sextonmänning", "sjuttonmänning",
"artonmänning", "nittonmänning", "tjugomänning" ] 

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class RelationshipCalculator(Relationship.RelationshipCalculator):

    def __init__(self,db):
        Relationship.RelationshipCalculator.__init__(self,db)

    def get_parents(self,level):
        if level == 1:
            return "föräldrar"
        else:
            return "anor i generation %d" % (level)

    def get_cousin(self,level):
        if level>len(_cousin_level)-1:
            return "distant relative"
        else:
            return _cousin_level[level]

    def pair_up(self,rel_list):
        result = []
        item = ""
        for word in rel_list[:]:
            if not word:
                continue
            if word in _cousin_level:
                if item:
                    result.append(item)
                    item = ""
                result.append(word)
                continue
	    if item:
                if word == 'syster':
                    item = item[0:-1]
                    word = 'ster'
                elif word == 'dotter' and item == 'bror':
                    item = 'brors'
                result.append(item + word)
                item = ""
            else:
                item = word
        if item:
            result.append(item)
        gen_result = [ item + 's' for item in result[0:-1] ]
        return ' '.join(gen_result+result[-1:])

    def get_direct_ancestor(self,person,rel_string):
        result = []
        for ix in range(len(rel_string)):
            if rel_string[ix] == 'f':
                result.append('far')
            else:
                result.append('mor')
        return self.pair_up(result)

    def get_direct_descendant(self,person,rel_string):
        result = []
        for ix in range(len(rel_string)-2,-1,-1):
            if rel_string[ix] == 'f':
                result.append('son')
            else:
                result.append('dotter')
        if person.get_gender() == RelLib.Person.MALE:
            result.append('son')
        else:
            result.append('dotter')
        return self.pair_up(result)

    def get_ancestors_cousin(self,rel_string_long,rel_string_short):
        result = []
        removed = len(rel_string_long)-len(rel_string_short)
        level = len(rel_string_short)-1
        for ix in range(removed):
            if rel_string_long[ix] == 'f':
                result.append('far')
            else:
                result.append('mor')
        result.append(self.get_cousin(level))
        return self.pair_up(result)

    def get_cousins_descendant(self,person,rel_string_long,rel_string_short):
        result = []
        removed = len(rel_string_long)-len(rel_string_short)-1
        level = len(rel_string_short)-1
        if level:
    	    result.append(self.get_cousin(level))
        elif rel_string_long[removed] == 'f':
        	result.append('bror')
        else:
        	result.append('syster')
        for ix in range(removed-1,-1,-1):
            if rel_string_long[ix] == 'f':
                result.append('son')
            else:
                result.append('dotter')
        if person.get_gender() == RelLib.Person.MALE:
            result.append('son')
        else:
            result.append('dotter')
        return self.pair_up(result)

    def get_ancestors_brother(self,rel_string):
        result = []
        for ix in range(len(rel_string)-1):
            if rel_string[ix] == 'f':
                result.append('far')
            else:
                result.append('mor')
        result.append('bror')
        return self.pair_up(result)

    def get_ancestors_sister(self,rel_string):
        result = []
        for ix in range(len(rel_string)-1):
            if rel_string[ix] == 'f':
                result.append('far')
            else:
                result.append('mor')
        result.append('syster')
        return self.pair_up(result)

    def get_relationship(self,orig_person,other_person):
        """
        Returns a string representing the relationshp between the two people,
        along with a list of common ancestors (typically father,mother) 
        
        Special cases: relation strings "", "undefined" and "spouse".
        """

        if orig_person == None:
            return ("undefined",[])
    
        if orig_person.get_handle() == other_person.get_handle():
            return ('', [])

        is_spouse = self.is_spouse(orig_person,other_person)
        if is_spouse:
            return (is_spouse,[])

        (firstRel,secondRel,common) = self.get_relationship_distance(orig_person,other_person)

        if type(common) == types.StringType or type(common) == types.UnicodeType:
            return (common,[])
        elif common:
            person_handle = common[0]
        else:
            return ("",[])

        if not firstRel:
            if not secondRel:
                return ('',common)
            else:
                return (self.get_direct_ancestor(other_person,secondRel),common)
        elif not secondRel:
            return (self.get_direct_descendant(other_person,firstRel),common)
        elif len(firstRel) == 1:
            if other_person.get_gender() == RelLib.Person.MALE:
                return (self.get_ancestors_brother(secondRel),common)
            else:
                return (self.get_ancestors_sister(secondRel),common)
        elif len(secondRel) >= len(firstRel):
            return (self.get_ancestors_cousin(secondRel,firstRel),common)
        else:
            return (self.get_cousins_descendant(other_person,firstRel,secondRel),common)

#-------------------------------------------------------------------------
#
# Register this class with the Plugins system 
#
#-------------------------------------------------------------------------
register_relcalc(RelationshipCalculator,
    ["sv","SV","sv_SE","swedish","Swedish","sv_SE.UTF8","sv_SE@euro","sv_SE.UTF8@euro",
            "svenska","Svenska", "sv_SE.UTF-8", "sv_SE.utf-8", "sv_SE.utf8"])

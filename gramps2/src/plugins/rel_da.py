# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2005  Donald N. Allingham
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
# and on valuable input from Lars Kr. Lundin

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------

import RelLib
import Relationship
import types
from TransUtils import sgettext as _
from PluginUtils import register_relcalc

#-------------------------------------------------------------------------
#
# Danish-specific definitions of relationships
#
#-------------------------------------------------------------------------

_parents_level = [ "forældre", "bedsteforældre", "oldeforældre",
"tipoldeforældre", "tiptipoldeforældre" , "tiptiptipoldeforældre" ]

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class RelationshipCalculator(Relationship.RelationshipCalculator):

    def __init__(self,db):
        Relationship.RelationshipCalculator.__init__(self,db)

    def get_parents(self,level):
        if level>len(_parents_level)-1:
            #return "fjern forfader"
            #Instead of "remote ancestors" using "tip (level) oldeforældre" here.
            return "tip (%d) oldeforældre" % level
        else:
            return _parents_level[level]

    def pair_up(self,rel_list):
        result = []
        item = ""
        for word in rel_list[:]:
            if not word:
                continue
            if item:
                if word == 'søster':
                    item = item[0:-1]
                    word = 'ster'
                elif word == 'sønne':
                    word = 'søn'
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
                result.append('sønne')
            else:
                result.append('datter')
        if person.get_gender() == RelLib.Person.MALE:
            result.append('søn')
        else:
            result.append('datter')
        return self.pair_up(result)

    def get_two_way_rel(self,person,first_rel_string,second_rel_string):
        result = []
        for ix in range(len(second_rel_string)-1):
            if second_rel_string[ix] == 'f':
                result.append('far')
            else:
                result.append('mor')
        if len(first_rel_string)>1:
            if first_rel_string[-2] == 'f':
                result.append('bror')
            else:
                result.append('søster')
            for ix in range(len(first_rel_string)-3,-1,-1):
                if first_rel_string[ix] == 'f':
                    result.append('sønne')
                else:
                    result.append('datter')
            if person.get_gender() == RelLib.Person.MALE:
                result.append('søn')
            else:
                result.append('datter')
        else:
            if person.get_gender() == RelLib.Person.MALE:
                result.append('bror')
            else:
                result.append('søster')
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
        else:
            return (self.get_two_way_rel(other_person,firstRel,secondRel),common)

#-------------------------------------------------------------------------
#
# Register this class with the Plugins system 
#
#-------------------------------------------------------------------------
register_relcalc(RelationshipCalculator,
    [ "da", "DA", "da_DK", "danish", "Danish", "da_DK.UTF8",
      "da_DK@euro", "da_DK.UTF8@euro", "dansk", "Dansk",
      "da_DK.UTF-8", "da_DK.utf-8", "da_DK.utf8"])

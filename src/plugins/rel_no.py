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
# and on valuable input from Frode Jemtland

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
# Norwegian-specific definitions of relationships
#
#-------------------------------------------------------------------------

_cousin_level = [ "", "", #brother/sister, fetter/kusine -- these are taken care of separately
"tremenning", "firemenning", "femmenning", 
"seksmenning", "sjumenning", "åttemenning",
"nimenning", "timenning", "elvemenning", 
"tolvmenning", "tretenmenning", "fjortenmenning",
"femtenmenning", "sekstenmenning", "syttenmenning",
"attenmenning", "nittenmenning", "tyvemenning" ] 

_cousin_terms = _cousin_level + ["fetter","kusine"]
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class RelationshipCalculator(Relationship.RelationshipCalculator):

    def __init__(self,db):
        Relationship.RelationshipCalculator.__init__(self,db)

    def get_parents(self,level):
        if level == 0:
            return "forelder"
        else:
            return "ane i %d-te generationen" % (level+1)

    def get_cousin(self,level):
        if level>len(_cousin_level)-1:
            # FIXME: use Norwegian term term here, 
            # UPDATED by Frode: unsure about the expretion "en fjern slektning", should it be just "fjern slektning".
            # Need to see it used in the program to get the understanding.
            return "en fjern slektning"
        else:
            return _cousin_level[level]

    def pair_up(self,rel_list):
        result = []
        item = ""
        for word in rel_list[:]:
            if not word:
                continue
            if word in _cousin_terms:
                if item:
                    result.append(item)
                    item = ""
                result.append(word)
                continue
            if item:
                if word == 'sønne':
                    word = 'sønn'
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
            result.append('sønn')
        else:
            result.append('datter')
        return self.pair_up(result)

    def get_ancestors_cousin(self,person,rel_string_long,rel_string_short):
        result = []
        removed = len(rel_string_long)-len(rel_string_short)
        level = len(rel_string_short)-1
        for ix in range(removed):
            if rel_string_long[ix] == 'f':
                result.append('far')
            else:
                result.append('mor')
        if level > 1:
            result.append(self.get_cousin(level))
        elif person.get_gender() == RelLib.Person.MALE:
            result.append('fetter')
        else:
            result.append('kusine')
        main_string = self.get_two_way_rel(person,rel_string_short,rel_string_long)
        aux_string = self.pair_up(result)
        return "%s (%s)" % (main_string,aux_string)

    def get_cousins_descendant(self,person,rel_string_long,rel_string_short):
        result = []
        aux_string = ""
        removed = len(rel_string_long)-len(rel_string_short)-1
        level = len(rel_string_short)-1
        if level > 1:       # Cousin terms without gender
            result.append(self.get_cousin(level))
        elif level == 1:    # gender-dependent fetter/kusine
            if rel_string_long[removed] == 'f':
                result.append('fetter')
            else:
                result.append('kusine')
        elif rel_string_long[removed] == 'f':
            result.append('bror')
        else:
            result.append('søster')
        for ix in range(removed-1,-1,-1):
            if rel_string_long[ix] == 'f':
                result.append('sønn')
            else:
                result.append('datter')
        if person.get_gender() == RelLib.Person.MALE:
            result.append('sønn')
        else:
            result.append('datter')
        main_string = self.get_two_way_rel(person,rel_string_long,rel_string_short)
        if level:
            aux_string = " (%s)" % self.pair_up(result)
        return "%s%s" % (main_string,aux_string)

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
        result.append('søster')
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
                result.append('sønn')
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
        elif len(firstRel) == 1:
            if other_person.get_gender() == RelLib.Person.MALE:
                return (self.get_ancestors_brother(secondRel),common)
            else:
                return (self.get_ancestors_sister(secondRel),common)
        elif len(secondRel) >= len(firstRel):
            return (self.get_ancestors_cousin(other_person,secondRel,firstRel),common)
        else:
            return (self.get_cousins_descendant(other_person,firstRel,secondRel),common)

#-------------------------------------------------------------------------
#
# Register this class with the Plugins system 
#
#-------------------------------------------------------------------------
register_relcalc(RelationshipCalculator,
    ["nb","nn","no", "nb_NO","nn_NO","no_NO","nb_NO.UTF8","nn_NO.UTF8","no_NO.UTF8",
    "nb_NO.UTF-8","nn_NO.UTF-8","no_NO.UTF-8", 
    "nb_NO.utf-8","nn_NO.utf-8","no_NO.utf-8", 
    "nb_NO.iso88591","nn_NO.iso88591","no_NO.iso88591", 
    "nynorsk","Nynorsk"])

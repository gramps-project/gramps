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
# and on valuable input from Eero Tamminen

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
# Finnish-specific definitions of relationships
#
#-------------------------------------------------------------------------

_parents_level = [ "", "vanhemmat", "isovanhemmat", "isoisovanhemmat",
"isoisoisovanhemmat", "isoisoisoisovanhemmat" ]

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class RelationshipCalculator(Relationship.RelationshipCalculator):

    def __init__(self,db):
        Relationship.RelationshipCalculator.__init__(self,db)

    def get_cousin(self,level):
        if level == 0:
            return ""
        elif level == 1:
            return "serkku"
        elif level == 2:
            return "pikkuserkku"
        elif level > 2:
            return "%d. serkku" % level

    def get_cousin_genitive(self,level):
        if level == 0:
            return ""
        elif level == 1:
            return "serkun"
        elif level == 2:
            return "pikkuserkun"
        elif level > 2:
            return "%d. serkun" % level

    def get_parents(self,level):
        if level>len(_parents_level)-1:
            return "kaukaiset esivanhemmat"
        else:
            return _parents_level[level]

    def get_direct_ancestor(self,person,rel_string):
        result = []
        for ix in range(len(rel_string)-1):
            if rel_string[ix] == 'f':
                result.append('isän')
            else:
                result.append('äidin')
        if person.get_gender() == RelLib.Person.MALE:
            result.append('isä')
        else:
            result.append('äiti')
        return ' '.join(result)

    def get_direct_descendant(self,person,rel_string):
        result = []
        for ix in range(len(rel_string)-2,-1,-1):
            if rel_string[ix] == 'f':
                result.append('pojan')
            elif rel_string[ix] == 'm':
                result.append('tyttären')
            else:
                result.append('lapsen')
        if person.get_gender() == RelLib.Person.MALE:
            result.append('poika')
        elif person.get_gender() == RelLib.Person.FEMALE:
            result.append('tytär')
        else:
            result.append('lapsi')
        return ' '.join(result)

    def get_ancestors_cousin(self,rel_string_long,rel_string_short):
        result = []
        removed = len(rel_string_long)-len(rel_string_short)
        level = len(rel_string_short)-1
        for ix in range(removed):
            if rel_string_long[ix] == 'f':
                result.append('isän')
            else:
                result.append('äidin')
        result.append(self.get_cousin(level))
        return ' '.join(result)

    def get_cousins_descendant(self,person,rel_string_long,rel_string_short):
        result = []
        removed = len(rel_string_long)-len(rel_string_short)-1
        level = len(rel_string_short)-1
        if level:
            result.append(self.get_cousin_genitive(level))
        elif rel_string_long[removed] == 'f':
            result.append('veljen')
        else:
            result.append('sisaren')
        for ix in range(removed-1,-1,-1):
            if rel_string_long[ix] == 'f':
                result.append('pojan')
            elif rel_string_long[ix] == 'm':
                result.append('tyttären')
            else:
                result.append('lapsen')
        if person.get_gender() == RelLib.Person.MALE:
            result.append('poika')
        elif person.get_gender() == RelLib.Person.FEMALE:
            result.append('tytär')
        else:
            result.append('lapsi')
        return ' '.join(result)

    def get_ancestors_brother(self,rel_string):
        result = []
        for ix in range(len(rel_string)-1):
            if rel_string[ix] == 'f':
                result.append('isän')
            else:
                result.append('äidin')
        result.append('veli')
        return ' '.join(result)

    def get_ancestors_sister(self,rel_string):
        result = []
        for ix in range(len(rel_string)-1):
            if rel_string[ix] == 'f':
                result.append('isän')
            else:
                result.append('äidin')
        result.append('sisar')
        return ' '.join(result)


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
    ["fi","FI","fi_FI","finnish","Finnish","fi_FI.UTF8","fi_FI@euro","fi_FI.UTF8@euro",
            "suomi","Suomi", "fi_FI.UTF-8", "fi_FI.utf-8", "fi_FI.utf8"])

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

#
# Written by Lorenzo Cappelletti <lorenzo.cappelletti@email.it>, 2003
#

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------

import RelLib
import Relationship
import types
from PluginUtils import register_relcalc

#-------------------------------------------------------------------------
#
# Shared constants
#
#-------------------------------------------------------------------------

_level =\
    ["", "prim", "second", "terz", "quart", "quint", "sest",
     "settim", "ottav", "non", "decim", "undicesim", "dodicesim",
     "tredicesim", "quattordicesim", "quindicesim", "sedicesim",
     "diciasettesim", "diciottesim", "diciannovesim", "ventesim"]


#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class RelationshipCalculator(Relationship.RelationshipCalculator):

    def __init__(self,db):
        Relationship.RelationshipCalculator.__init__(self,db)

    #-------------------------------------------------------------------------
    #
    # Specific relationship functions
    #
    # To be honest, I doubt that this relationship naming method is widely
    # spread... If you know of a rigorous, italian naming convention,
    # please, drop me an email.
    #
    #-------------------------------------------------------------------------
    def get_parents (self,level):
        if level>len(_level)-1:
            return "remote ancestors"
        else:
            return "%si genitori" % _level[level]

    def get_father (self,level, gender="o"):
        if level>len(_level)-1:
            return "remote ancestor"
        elif level == 0: return ""
        elif level == 1: return "padre"
        elif level == 2: return "nonn%s" % gender
        elif level == 3: return "bisnonn%s" % gender
        else           : return "%s%s nonn%s" % (_level[level], gender, gender)

    def get_mother (self,level):
        if   level == 1: return "madre"
        else           : return self.get_father(level, "a")

    def get_son (self, level, gender="o"):
        if level>len(_level)-1:
            return "remote descendant"
        elif   level == 0: return ""
        elif level == 1: return "figli%s" % gender
        elif level == 2: return "nipote"
        elif level == 3: return "pronipote"
        else           : return "%s%s nipote" % (_level[level], gender)

    def get_daughter (self, level):
        return self.get_son(level, "a")

    def get_uncle (self, level, gender="o"):
        if level>len(_level)-1:
            return "remote ancestor"
        elif level == 0: return ""
        elif level == 1: return "fratello"
        elif level == 2: return "zi%s" % gender
        elif level == 3: return "prozi%s" % gender
        else           : return "%s%s zi%s" % (_level[level], gender, gender)

    def get_aunt (self,level):
        if   level == 1: return "sorella"
        else           : return self.get_uncle(level, "a")

    def get_nephew (self,level, gender="o"):
        if level>len(_level)-1:
            return "remote descendant"
        elif level == 0: return ""
        elif level == 1: return "nipote"
        elif level == 2: return "pronipote"
        else           : return "%s%s nipote" % (_level[level], gender)

    def get_niece(self,level):
        return self.get_nephew(level, "a")

    def get_male_cousin (self,levelA, levelB, gender="o"):
        if levelA+levelB>len(_level):
            return "remote relative"
        else:
            return "cugin%s di %so grado (%i-%i)" \
                   % (gender, _level[levelA+levelB-1], levelA, levelB)

    def get_female_cousin (self,levelA, levelB):
        return self.get_male_cousin(levelA, levelB, "a")

    #-------------------------------------------------------------------------
    #
    # get_relationship
    #
    #-------------------------------------------------------------------------

    def get_relationship(self,orig_person,other_person):
        """
        returns a string representing the relationshp between the two people,
        along with a list of common ancestors (typically father,mother)
        """

        if orig_person == None:
            return ("non definito",[])

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

        firstRel = len(firstRel)
        secondRel = len(secondRel)

        if firstRel == 0:
            if secondRel == 0:
                return ('',common)
            elif other_person.get_gender() == RelLib.Person.MALE:
                return (self.get_father(secondRel),common)
            else:
                return (self.get_mother(secondRel),common)
        elif secondRel == 0:
            if other_person.get_gender() == RelLib.Person.MALE:
                return (self.get_son(firstRel),common)
            else:
                return (self.get_daughter(firstRel),common)
        elif firstRel == 1:
            if other_person.get_gender() == RelLib.Person.MALE:
                return (self.get_uncle(secondRel),common)
            else:
                return (self.get_aunt(secondRel),common)
        elif secondRel == 1:
            if other_person.get_gender() == RelLib.Person.MALE:
                return (self.get_nephew(firstRel-1),common)
            else:
                return (self.get_niece(firstRel-1),common)
        else:
            if other_person.get_gender() == RelLib.Person.MALE:
                return (self.get_male_cousin(firstRel-1, secondRel-1), common)
            else:
                return (self.get_female_cousin(firstRel-1, secondRel-1), common)


#-------------------------------------------------------------------------
#
# Function registration
#
#-------------------------------------------------------------------------
register_relcalc(RelationshipCalculator,
    ["it", "IT", "it_IT", "it_IT@euro", "it_IT.utf8"])

# Local variables:
# buffer-file-coding-system: utf-8
# End:

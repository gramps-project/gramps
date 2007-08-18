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

# $Id: rel_nl.py 6775 2006-12-16 05:52:17Z erikderichter $

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
#
#
#-------------------------------------------------------------------------

_level_name = [ "",
                "eerste",
                "tweede",
                "derde",
                "vierde",
                "vijfde",
                "zesde",
                "zevende",
                "achtste",
                "negende",
                "tiende",
                "elfde",
                "twaalfde",
                "dertiende",
                "veertiende", 
                "vijftiende",
                "zestiende",
                "zeventiende",
                "acttiende",
                "negentiende",
                "twintigste",
                "eenentwintigste",
                "tweeëntwintigste", 
                "drieëntwingste",
                "vierentwingste",
                "vijfentwintigste",
                "zesentwintigste",
                "zevenentwintigste",
                "achtentwintigste",
                "negenentwintigste",
                "dertigste" ]

_parents_level = [ "",
                   "ouders",
                   "grootouders",
                   "overgrootouders",
                   "betovergrootouders", ]

_father_level = [ "",
                  "vader",
                  "grootvader",
                  "overgrootvader",
                  "betovergrootvader", ]

_mother_level = [ "",
                  "moeder",
                  "grootmoeder",
                  "overgrootmoeder",
                  "betovergrootmoeder", ]

_son_level = [ "",
               "zoon",
               "kleinzoon",
               "achterkleinzoon", ]

_daughter_level = [ "",
                    "dochter",
                    "kleindochter",
                    "achterkleindochter", ]

_sister_level = [ "",
                  "zuster",
                  "tante",
                  "groottante", ]

_brother_level = [ "",
                   "broer",
                   "oom",
                   "grootoom", ]

_nephew_level = [ "",
                  "neef",
                  "achterneef", ]

_niece_level = [ "",
                 "nicht",
                 "achternicht", ]

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class RelationshipCalculator(Relationship.RelationshipCalculator):

    def __init__(self):
        Relationship.RelationshipCalculator.__init__(self)

    def get_male_cousin(self,level):
        if level>len(_level_name)-1:
            return "le parent lointain"
        else:
            return "neef in de %s graad" % (_level_name[level])

    def get_female_cousin(self,level):
        if level>len(_level_name)-1:
            return "la parente lointaine"
        else:
            return "nicht in de %s graad" % (_level_name[level])

    def get_parents(self,level):
        if level>len(_parents_level)-1:
            return "verre voorouders"
        else:
            return _parents_level[level]

    def get_father(self,level):
        if level>len(_father_level)-1:
            return "verre voorouder"
        else:
            return _father_level[level]

    def get_son(self,level):
        if level>len(_son_level)-1:
            return "verre afstammeling"
        else:
            return _son_level[level]

    def get_mother(self,level):
        if level>len(_mother_level)-1:
            return "verre voorouder"
        else:
            return _mother_level[level]

    def get_daughter(self,level):
        if level>len(_daughter_level)-1:
            return "verre afstammelinge"
        else:
            return _daughter_level[level]

    def get_aunt(self,level):
        if level>len(_sister_level)-1:
            return "verre voorouder"
        else:
            return _sister_level[level]

    def get_uncle(self,level):
        if level>len(_brother_level)-1:
            return "verre voorouder"
        else:
            return _brother_level[level]

    def get_nephew(self,level):
        if level>len(_nephew_level)-1:
            return "verre afstammelling"
        else:
            return _nephew_level[level]

    def get_niece(self,level):
        if level>len(_niece_level)-1:
            return "verre afstammelinge"
        else:
            return _niece_level[level]

    def get_relationship(self,db,orig_person,other_person):
        """
        Returns a string representing the relationshp between the two people,
        along with a list of common ancestors (typically father,mother) 
        
        Special cases: relation strings "", "undefined" and "spouse".
        """

        if orig_person == None:
            return ("niet bepaalde",[])

        if orig_person.get_handle() == other_person.get_handle():
            return ('', [])

        is_spouse = self.is_spouse(db,orig_person,other_person)
        if is_spouse:
            return (is_spouse,[])

        (firstRel,secondRel,common) = \
                     self.get_relationship_distance(db,orig_person,other_person)

        if type(common) == types.StringType or \
           type(common) == types.UnicodeType:
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
        elif firstRel == 2 and secondRel == 2:
            if other_person.get_gender() == RelLib.Person.MALE:
                return ('le cousin germain',common)
            else:
                return ('la cousine germaine',common)
        elif firstRel == 3 and secondRel == 2:
            if other_person.get_gender() == RelLib.Person.MALE:
                return ('le neveu à la mode de Bretagne',common)
            else:
                return ('la nièce à la mode de Bretagne',common)
        elif firstRel == 2 and secondRel == 3:
            if other_person.get_gender() == RelLib.Person.MALE:
                return ('l\'oncle à la mode de Bretagne',common)
            else:
                return ('la tante à la mode de Bretagne',common)
        else:
            if other_person.get_gender() == RelLib.Person.MALE:
                if firstRel+secondRel>len(_level_name)-1:
                    return (self.get_male_cousin(firstRel+secondRel),common)
                else:
                    return ('verre neef',common)
            else:
                if firstRel+secondRel>len(_level_name)-1:
                    return (self.get_female_cousin(firstRel+secondRel),common)
                else:
                    return ('verre nicht',common)

#-------------------------------------------------------------------------
#
# Register this class with the Plugins system 
#
#-------------------------------------------------------------------------
register_relcalc(RelationshipCalculator,
    ["nl", "NL", "nl_NL", "nl_BE", "nederlands", "Nederlands", "nl_NL.UTF8", "nl_BE.UTF8","nl_NL@euro", "nl_NL.UTF8@euro","nl_BE@euro",
     "dutch","Dutch", "nl_NL.UTF-8", "nl_BE.UTF-8","nl_NL.utf-8", "nl_BE.utf-8","nl_NL.utf8", "nl_BE.UTF-8", "nl_BE.UTF8@euro"])

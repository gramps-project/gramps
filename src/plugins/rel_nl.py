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

_removed_level = [ " ",
                " eerste graad",
                " tweede graad",
                " derde graad",
                " vierde graad",
                " vijfde graad",
                " zesde graad",
                " zevende graad",
                " achtste",
                " negende",
                " tiende",
                " elfde",
                " twaalfde",
                " dertiende",
                " veertiende", 
                " vijftiende",
                " zestiende",
                " zeventiende",
                " achttiende",
                " negentiende",
                " twintigste",
                " eenentwintigste",
                " tweeëntwintigste", 
                " drieëntwingste",
                " vierentwingste",
                " vijfentwintigste",
                " zesentwintigste",
                " zevenentwintigste",
                " achtentwintigste",
                " negenentwintigste",
                " dertigste" ]

_parents_level = [ "",
                   "ouders",
                   "grootouders",
                   "overgrootouders",
                   "betovergrootouders",
                   "oudouders",
                   "oudgrootouders",
                   "oudovergrootouders",
                   "oudbetovergrootouders",
                   "stamouders",
                   "stamgrootouders",
                   "stamovergrootouders",
                   "stambetovergrootouders",
                   "stamoudouders",
                   "stamoudgrootouders",
                   "stamoudovergrootouders",
                   "stamoudbetovergrootouders",
                   "edelouders",
                   "edelgrootoders",
                   "edelovergrootoudouders",
                   "edelbetovergrootouders",
                   "edeloudouders",
                   "edeloudgrootouders",
                   "edeloudvergrootouders",
                   "edeloudbetovergrootouders",
                   "edelstamouders",
                   "edelstamgrootouders",
                   "edelstamovergrootouders",
                   "edelstambetovergrootouders",
                   "edelstamoudouders" ]

_father_level = [ "",
                  "vader (graad 1)",
                  "grootvader (graad 2)",
                  "overgrootvader (graad 3)",
                  "betovergrootvader (graad 4)",
                  "oudvader (graad 5)",
                  "oudgrootvader (graad 6)",
                  "oudovergrootvader(graad 7)",
                  "oudbetovergrootvader (graad 8)",
                  "stamvader graad 9)",
                  "stamgrootvader",
                  "stamovergrootvader",
                  "stambetovergrootvader",
                  "stamoudvader",
                  "stamoudgrootvader",
                  "stamoudovergrootvader",
                  "stamoudbetovergrootvader",
                  "edelvader",
                  "edelgrootvader",
                  "edelovergrootoudvader",
                  "edelbetovergrootvader",
                  "edeloudvader",
                  "edeloudgrootvader",
                  "edeloudvergrootvader",
                  "edeloudbetovergrootvader",
                  "edelstamvader",
                  "edelstamgrootvader",
                  "edelstamovergrootvader",
                  "edelstambetovergrootvader",
                  "edelstamoudvader" ]

_mother_level = [ "",
                  "moeder (graad 1)",
                  "grootmoeder (graad 2)",
                  "overgrootmoeder (graad 3)",
                  "betovergrootmoeder (graad 4)",
                  "oudmoeder",
                  "oudgrootmoeder",
                  "oudovergrootmoeder",
                  "oudbetovergrootmoeder",
                  "stammoeder",
                  "stamgrootmoeder",
                  "stamovergrootmoeder",
                  "stambetovergrootmoeder",
                  "stamoudmoeder",
                  "stamoudgrootmoeder",
                  "stamoudovergrootmoeder",
                  "stamoudbetovergrootmoeder",
                  "edelmoeder",
                  "edelgrootmoeder",
                  "edelovergrootoudmoeder",
                  "edelbetovergrootmoeder",
                  "edeloudmoeder",
                  "edeloudgrootmoeder",
                  "edeloudvergrootmoeder",
                  "edeloudbetovergrootmoeder",
                  "edelstammoeder",
                  "edelstamgrootmoeder",
                  "edelstamovergrootmoeder",
                  "edelstambetovergrootmoeder",
                  "edelstamoudmoeder" ]

_son_level = [ "",
               "zoon",
               "kleinzoon",
               "achterkleinzoon", 
               "achterachterkleinzoon",
               "achterachterachterkleinzoon"]

_daughter_level = [ "",
                    "dochter",
                    "kleindochter",
                    "achterkleindochter",
                    "achterachterkleindochter",
                    "achterachterachterkleindochter"]

##_sister_level = [ "",
##                  "zuster",
##                  "tante",
##                  "groottante",
##                  "overgroottante" ,
##                  "betovergroottante",
##                  "oudtante"]

##_brother_level = [ "",
##                   "broer",
##                   "oom",
##                   "grootoom",
##                   "overgrootoom",
##                   "betovergrootoom",
##                   "oudoom" ]

_nephew_level = [ "",
                  "neef",
                  "achterneef",
                  "achterachterneef" ]

_niece_level = [ "",
                 "nicht",
                 "achternicht", 
                 "achterachtenicht"]
_aunt_level = [ "",  
                "tante", 
                "groottante",
                "overgroottante",
                "betovergroottante",
                "oudtante"]

_uncle_level = [ "",  
                 "oom",
                 "grootoom",
                 "overgrootoom",
                 "betovergrootoom"]
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class RelationshipCalculator(Relationship.RelationshipCalculator):

    def __init__(self,db):
        Relationship.RelationshipCalculator.__init__(self,db)

    def get_parents(self, level):
        if level>len(_parents_level)-1:
            return "verre voorouders"
        else:
            return _parents_level[level]    
    def get_father(self, level):
        if level>len(_father_level)-1:
            return "verre voorouder"
        else:
            return _father_level[level]

    def get_son(self, level):
        if level>len(_son_level)-1:
            return "verre afstammeling"
        else:
            return _son_level[level]  

    def get_mother(self,level):
        if level>len(_mother_level)-1:
            return "verre voorouder"
        else:
            return _mother_level[level]

    def get_daughter(self, level):
        if level>len(_daughter_level)-1:
            return "verre afstammelinge"
        else:
            return _daughter_level[level]

    def get_aunt(self, level, removed):
        if level>len(_aunt_level)-1 or removed > len(_removed_level) -1:
            return "verre voorouder"
        else:
            return _aunt_level[level] + _removed_level[removed]    
    def get_uncle(self, level, removed):
        if level>len(_uncle_level)-1 or removed > len(_removed_level) -1:
            return "verre voorouder"
        else:
            return _uncle_level[level] + _removed_level[removed]   

    def get_nephew(self,level, removed):
        if level>len(_nephew_level)-1 or removed > len(_removed_level) -1:
            return "verre voorouder"
        else:
            return _nephew_level[level] + _removed_level[removed]   

    def get_niece(self,level, removed):
        if level>len(_niece_level)-1 or removed > len(_removed_level) -1:
            return "verre afstammelinge"
        else:
            return _niece_level[level] + _removed_level[removed]  

    def get_male_cousin(self,removed):
        if removed>len(_removed_level)-1:
            return "verre afstammeling"
        elif removed == 0:
            return "broer"
        else:
            return "neef "+_removed_level[removed]

    def get_female_cousin(self,removed):
        if removed>len(_removed_level)-1:
            return "verre afstammelinge"
        elif  removed == 0:
            return " zus"
        else:
            return "nicht "+ _removed_level[removed]

    def get_relationship(self,orig_person,other_person):
        """
        Returns a string representing the relationshp between the two peopl
e,
        along with a list of common ancestors (typically father,mother) 

        Special cases: relation strings "", "undefined" and "spouse".
        """
        if orig_person == None:
            return ("niet bepaald",[])

        if orig_person.get_handle() == other_person.get_handle():
            return ('', [])

        is_spouse = self.is_spouse(orig_person,other_person)
        if is_spouse:
            return (is_spouse,[])

        (firstRel,secondRel,common) = self.get_relationship_distance(orig
_person,other_person)

        if type(common) == types.StringType or type(common) == type
s.UnicodeType:
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
                return (self.get_father(secondRel), common)
            else:
                return (self.get_mother(secondRel), common)
        elif secondRel == 0:
            if other_person.get_gender() == RelLib.Person.MALE:
                return (self.get_son(firstRel), common)
            else:
                return (self.get_daughter(firstRel), common)
        elif secondRel > firstRel:
            if other_person.get_gender() == RelLib.Person.MALE:
                return (self.get_uncle(secondRel - firstRel,firstRel), comm
on)
            else:
                return (self.get_aunt(secondRel - firstRel, firstRel), comm
on)
        elif secondRel < firstRel:
            if other_person.get_gender() == RelLib.Person.MALE:
                return (self.get_nephew(firstRel - secondRel, secondRel), c
ommon)
            else:
                return (self.get_niece(firstRel - secondRel, secondRel), co
mmon)
        else:
                if other_person.get_gender() == RelLib.Person.MALE:
                    return (self.get_male_cousin(firstRel -1), common)
                else:
                    return (self.get_female_cousin(firstRel -1), common)
##        elif firstRel == 2 and secondRel == 2:
##            if other_person.get_gender() == RelLib.Person.MALE:
##                return ('de neef',common)
##            else:
##                return ('de nicht',common)
##        elif firstRel == 3 and secondRel == 2:
##            if other_person.get_gender() == RelLib.Person.MALE:
##                return ('neef',common)
##            else:
##                return ('nicht',common)
##        elif firstRel == 2 and secondRel == 3:
##            if other_person.get_gender() == RelLib.Person.MALE:
##                return ('de oom',common)
##            else:
##                return ('de tante',common)
##        else:
##            if other_person.get_gender() == RelLib.Person.MALE:
##                if firstRel+secondRel>len(_level_name)-1:
##                    return (self.get_male_cousin(firstRel+secondRel),comm
on)
##                else:
##                    return ('verre neef',common)
##            else:
##                if firstRel+secondRel>len(_level_name)-1:
##                    return (self.get_female_cousin(firstRel+secondRel),co
mmon)
##                else:
##                    return ('verre nicht',common)

#-------------------------------------------------------------------------
#
# Register this class with the Plugins system 
#
#-------------------------------------------------------------------------
register_relcalc(RelationshipCalculator,
    ["nl", "NL", "nl_NL", "nl_BE", "nederlands", "Nederlands", "nl_NL.UTF8"
,
     "nl_BE.UTF8","nl_NL@euro", "nl_NL.UTF8@euro","nl_BE@euro",
     "dutch","Dutch", "nl_NL.UTF-8", "nl_BE.UTF-8","nl_NL.utf-8",
     "nl_BE.utf-8","nl_NL.utf8", "nl_BE.UTF-8", "nl_BE.UTF8@euro"])

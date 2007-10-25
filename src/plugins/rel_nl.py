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
                " eerste",
                " tweede",
                " derde",
                " vierde",
                " vijfde",
                " zesde",
                " zevende",
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
                   "stamgrootouders",        # gen 10
                   "stamovergrootouders",
                   "stambetovergrootouders",
                   "stamoudouders",
                   "stamoudgrootouders",
                   "stamoudovergrootouders",
                   "stamoudbetovergrootouders",
                   "edelouders",
                   "edelgrootoders",
                   "edelovergrootoudouders",
                   "edelbetovergrootouders", # gen 20
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
                  "vader",
                  "grootvader",
                  "overgrootvader",
                  "betovergrootvader",
                  "oudvader (generatie 5)",
                  "oudgrootvader  (generatie 6)",
                  "oudovergrootvader  (generatie 7)",
                  "oudbetovergrootvader  (generatie 8)",
                  "stamvader  (generatie 9)",
                  "stamgrootvader  (generatie 10)",
                  "stamovergrootvader  (generatie 11)",
                  "stambetovergrootvader (generatie 12)",
                  "stamoudvader (generatie 13)",
                  "stamoudgrootvader (generatie 14)",
                  "stamoudovergrootvader (generatie 15)",
                  "stamoudbetovergrootvader (generatie 16)",
                  "edelvader (generatie 17)",
                  "edelgrootvader (generatie 18)",
                  "edelovergrootoudvader (generatie 19)",
                  "edelbetovergrootvader  (generatie 20)",
                  "edeloudvader (generatie 21)",
                  "edeloudgrootvader (generatie 22)",
                  "edeloudvergrootvader (generatie 23)",
                  "edeloudbetovergrootvader (generatie 24)",
                  "edelstamvader (generatie 25)",
                  "edelstamgrootvader (generatie 26)",
                  "edelstamovergrootvader (generatie 27)",
                  "edelstambetovergrootvader (generatie 28)",
                  "edelstamoudvader (generatie 29)" ]

_mother_level = [ "",
                  "moeder ",
                  "grootmoeder",
                  "overgrootmoeder",
                  "betovergrootmoeder",
                  "oudmoeder (generatie 5)",
                  "oudgrootmoeder (generatie 6)",
                  "oudovergrootmoeder (generatie 7)",
                  "oudbetovergrootmoeder (generatie 8)",
                  "stammoeder (generatie 9)",
                  "stamgrootmoeder (generatie 10)",
                  "stamovergrootmoeder  (generatie 11)",
                  "stambetovergrootmoeder (generatie 12)",
                  "stamoudmoeder (generatie 13)",
                  "stamoudgrootmoeder (generatie 14)",
                  "stamoudovergrootmoeder (generatie 15)",
                  "stamoudbetovergrootmoeder (generatie 16)",
                  "edelmoeder (generatie 17)",
                  "edelgrootmoeder (generatie 18)",
                  "edelovergrootoudmoeder (generatie 19)",
                  "edelbetovergrootmoeder (generatie 20)",
                  "edeloudmoeder (generatie 21)",
                  "edeloudgrootmoeder (generatie 22)",
                  "edeloudvergrootmoeder (generatie 23)",
                  "edeloudbetovergrootmoeder (generatie 24)",
                  "edelstammoeder (generatie 25)",
                  "edelstamgrootmoeder (generatie 26)",
                  "edelstamovergrootmoeder (generatie 27)",
                  "edelstambetovergrootmoeder (generatie 28)",
                  "edelstamoudmoeder (generatie 29)" ]

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

_nephew_level = [ "",
                  "neef",
                  "achterneef",
                  "achterachterneef" ]

_niece_level = [ "",
                 "nicht",
                 "achternicht", 
                 "achterachternicht"]
_aunt_level = [ "",  
                "tante", 
                "groottante",
                "overgroottante",
                "betovergroottante",
                "oudtante (generatie 5)"]

_uncle_level = [ "",  
                 "oom",
                 "grootoom",
                 "overgrootoom",
                 "betovergrootoom",
                 "oudoom (generatie 5)"]
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class RelationshipCalculator(Relationship.RelationshipCalculator):

    def __init__(self,db):
        Relationship.RelationshipCalculator.__init__(self,db)

    def get_parents(self, level):
        if level > len(_parents_level)-1:
            return "verre voorouders (%d generaties)" % level
        else:
            return _parents_level[level]    
    def get_father(self, level):
        if level > len(_father_level)-1:
            return "verre voorvader (%d generaties)" % level
        else:
            return _father_level[level]

    def get_son(self, level):
        if level < len(_son_level):
            return _son_level[level] 
        else:
            return "verre achterkleinzoon (%d generaties)" % level

    def get_mother(self,level):
        if level > len(_mother_level)-1:
            return "verre voormoeder (%d generaties)" % level
        else:
            return _mother_level[level]

    def get_daughter(self, level):
        if level > len(_daughter_level)-1:
            return "verre achterkleindochter (%d generaties)" % level
        else:
            return _daughter_level[level]

    def get_aunt(self, level, removed):
        if removed == 1 and level < len(_aunt_level):
            return _aunt_level[level]
        elif level > len(_aunt_level)-1 or removed > len(_removed_level) -1:
            return "verre tante (%d generaties, %d graden)" % (level, removed)
        elif level > len(_aunt_level)-1:
            return "verre tante van de%s graad (%d generaties)" \
                                            % (_removed_level[removed], level)
        else:
            return _aunt_level[level] + _removed_level[removed] + " graad"    
        
    def get_uncle(self, level, removed):
        if removed == 1 and level < len(_uncle_level):
            return _uncle_level[level]
        elif level > len(_uncle_level)-1 or removed > len(_removed_level) -1:
            return "verre oom (%d generaties, %d graden)" % (level, removed)
        elif level > len(_uncle_level)-1:
            return "verre oom van de%s graad (%d generaties)" \
                                            % (_removed_level[removed], level)
        else:
            return _uncle_level[level] + _removed_level[removed] + " graad"

    def get_nephew(self, level, removed=1):
        if removed == 1 and level < len(_nephew_level):
            return _nephew_level[level]
        elif level > len(_nephew_level)-1 or removed > len(_removed_level) -1:
            return "verre neef (%d generaties, %d graden)" % (level, removed)
        elif level > len(_nephew_level)-1:
            return "verre neef van de%s graad (%d generaties)" \
                                            % (_removed_level[removed], level)
        else:
            return _nephew_level[level] + _removed_level[removed] + " graad"

    def get_niece(self, level, removed=1):
        if removed == 1 and level < len(_niece_level):
            return _niece_level[level]
        if level > len(_niece_level)-1 or removed > len(_removed_level) -1:
            return "verre nicht (%d generaties, %d graden)" % (level, removed)
        elif level > len(_niece_level)-1:
            return "verre nicht van de%s graad (%d generaties)" \
                                            % (_removed_level[removed], level)
        else:
            return _niece_level[level] + _removed_level[removed] + " graad"

    def get_male_cousin(self,removed):
        """Specific Dutch thing, the nieces/nephews on same level are called
            going sideways in a branch as the nieces/newphews going downward
            from your brother/sisters. This used to be called "kozijn"
        """
        removed = removed - 1
        if removed > len(_removed_level)-1:
            return "verre neef (kozijn, %d graden)" % removed
        elif removed == 0:
            return "broer"
        else:
            return "neef (kozijn)"+_removed_level[removed] + " graad"

    def get_female_cousin(self,removed):
        """Specific Dutch thing, the nieces/nephews on same level are called
            going sideways in a branch as the nieces/newphews going downward
            from your brother/sisters.  This used to be called "kozijn"
        """
        removed = removed - 1
        if removed > len(_removed_level)-1:
            return "verre nicht (kozijn, %d graden)" % removed
        elif removed == 0:
            return "zus"
        else:
            return "nicht (kozijn)"+ _removed_level[removed] + " graad"

    def get_relationship(self,orig_person,other_person):
        """
        Returns a string representing the relationshp between the two people,
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
            #other person is ancestor
            if secondRel == 0:
                return ('',common)
            elif other_person.get_gender() == RelLib.Person.MALE:
                return (self.get_father(secondRel), common)
            else:
                return (self.get_mother(secondRel), common)
        elif secondRel == 0:
            #other person is descendant
            if other_person.get_gender() == RelLib.Person.MALE:
                return (self.get_son(firstRel), common)
            else:
                return (self.get_daughter(firstRel), common)
        elif secondRel > firstRel:
            #other person is higher in the branch, in english uncle/aunt or 
            #cousin up, in dutch always 'oom/tante'
            if other_person.get_gender() == RelLib.Person.MALE:
                return (self.get_uncle(secondRel - firstRel,firstRel), common)
            else:
                return (self.get_aunt(secondRel - firstRel, firstRel), common)
        elif secondRel < firstRel:
            #other person is lower in the branch, in english niece/nephew or 
            #cousin down, in dutch always 'neef/nicht'
            if other_person.get_gender() == RelLib.Person.MALE:
                return (self.get_nephew(firstRel - secondRel, secondRel), common)
            else:
                return (self.get_niece(firstRel - secondRel, secondRel), common)
        else:
            # people on the same level secondRel == firstRel
            if other_person.get_gender() == RelLib.Person.MALE:
                return (self.get_male_cousin(firstRel), common)
            else:
                return (self.get_female_cousin(firstRel), common)

#-------------------------------------------------------------------------
#
# Register this class with the Plugins system 
#
#-------------------------------------------------------------------------
register_relcalc(RelationshipCalculator,
    ["nl", "NL", "nl_NL", "nl_BE", "nederlands", "Nederlands", "nl_NL.UTF8",
     "nl_BE.UTF8","nl_NL@euro", "nl_NL.UTF8@euro","nl_BE@euro",
     "dutch","Dutch", "nl_NL.UTF-8", "nl_BE.UTF-8","nl_NL.utf-8",
     "nl_BE.utf-8","nl_NL.utf8", "nl_BE.UTF-8", "nl_BE.UTF8@euro"])

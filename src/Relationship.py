#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2004  Donald N. Allingham
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
# GRAMPS modules
#
#-------------------------------------------------------------------------

import RelLib
import types
from gettext import gettext as _

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------

_level_name = [ "", "first", "second", "third", "fourth", "fifth", "sixth",
                "seventh", "eighth", "ninth", "tenth", "eleventh", "twelfth",
                "thirteenth", "fourteenth", "fifteenth", "sixteenth",
                "seventeenth", "eighteenth", "nineteenth", "twentieth" ]

_removed_level = [ "", " once removed", " twice removed", " three times removed",
                   " four times removed", " five times removed", " six times removed",
                   " sevent times removed", " eight times removed", " nine times removed",
                   " ten times removed", " eleven times removed", " twelve times removed",
                   " thirteen times removed", " fourteen times removed", " fifteen times removed",
                   " sixteen times removed", " seventeen times removed", " eighteen times removed",
                   " nineteen times removed", " twenty times removed" ]

_parents_level = [ "", "parents", "grandparents", "great grandparents", "second great grandparents",
                  "third great grandparents",  "fourth great grandparents",
                  "fifth great grandparents",  "sixth great grandparents",
                  "seventh great grandparents", "eighth great grandparents",
                  "ninth great grandparents", "tenth great grandparents",
                  "eleventh great grandparents",  "twelfth great grandparents",
                  "thirteenth great grandparents", "fourteenth great grandparents",
                  "fifteenth great grandparents", "sixteenth great grandparents",
                  "seventeenth great grandparents", "eighteenth great grandparents",
                  "nineteenth great grandparents", "twentieth great grandparents", ]

_father_level = [ "", "father", "grandfather", "great grandfather", "second great grandfather",
                  "third great grandfather",  "fourth great grandfather",
                  "fifth great grandfather",  "sixth great grandfather",
                  "seventh great grandfather", "eighth great grandfather",
                  "ninth great grandfather", "tenth great grandfather",
                  "eleventh great grandfather",  "twelfth great grandfather",
                  "thirteenth great grandfather", "fourteenth great grandfather",
                  "fifteenth great grandfather", "sixteenth great grandfather",
                  "seventeenth great grandfather", "eighteenth great grandfather",
                  "nineteenth great grandfather", "twentieth great grandfather", ]

_mother_level = [ "", "mother", "grandmother", "great grandmother", "second great grandmother",
                  "third great grandmother",  "fourth great grandmother",
                  "fifth great grandmother",  "sixth great grandmother",
                  "seventh great grandmother", "eighth great grandmother",
                  "ninth great grandmother", "tenth great grandmother",
                  "eleventh great grandmother",  "twelfth great grandmother",
                  "thirteenth great grandmother", "fourteenth great grandmother",
                  "fifteenth great grandmother", "sixteenth great grandmother",
                  "seventeenth great grandmother", "eighteenth great grandmother",
                  "nineteenth great grandmother", "twentieth great grandmother", ]

_son_level = [ "", "son", "grandson", "great grandson", "second great grandson",
               "third great grandson",  "fourth great grandson",
               "fifth great grandson",  "sixth great grandson",
               "seventh great grandson", "eighth great grandson",
               "ninth great grandson", "tenth great grandson",
               "eleventh great grandson",  "twelfth great grandson",
               "thirteenth great grandson", "fourteenth great grandson",
               "fifteenth great grandson", "sixteenth great grandson",
               "seventeenth great grandson", "eighteenth great grandson",
               "nineteenth great grandson", "twentieth great grandson", ]

_daughter_level = [ "", "daughter", "granddaughter", "great granddaughter",
                    "second great granddaughter",
                    "third great granddaughter",  "fourth great granddaughter",
                    "fifth great granddaughter",  "sixth great granddaughter",
                    "seventh great granddaughter", "eighth great granddaughter",
                    "ninth great granddaughter", "tenth great granddaughter",
                    "eleventh great granddaughter",  "twelfth great granddaughter",
                    "thirteenth great granddaughter", "fourteenth great granddaughter",
                    "fifteenth great granddaughter", "sixteenth great granddaughter",
                    "seventeenth great granddaughter", "eighteenth great granddaughter",
                    "nineteenth great granddaughter", "twentieth great granddaughter", ]

_sister_level = [ "", "sister", "aunt", "grandaunt", "great grandaunt", "second great grandaunt",
                  "third great grandaunt",  "fourth great grandaunt",
                  "fifth great grandaunt",  "sixth great grandaunt",
                  "seventh great grandaunt", "eighth great grandaunt",
                  "ninth great grandaunt", "tenth great grandaunt",
                  "eleventh great grandaunt",  "twelfth great grandaunt",
                  "thirteenth great grandaunt", "fourteenth great grandaunt",
                  "fifteenth great grandaunt", "sixteenth great grandaunt",
                  "seventeenth great grandaunt", "eighteenth great grandaunt",
                  "nineteenth great grandaunt", "twentieth great grandaunt", ]

_brother_level = [ "", "brother", "uncle", "granduncle", "great granduncle", "second great granduncle",
                   "third great granduncle",  "fourth great granduncle",
                   "fifth great granduncle",  "sixth great granduncle",
                   "seventh great granduncle", "eighth great granduncle",
                   "ninth great granduncle", "tenth great granduncle",
                   "eleventh great granduncle",  "twelfth great granduncle",
                   "thirteenth great granduncle", "fourteenth great granduncle",
                   "fifteenth great granduncle", "sixteenth great granduncle",
                   "seventeenth great granduncle", "eighteenth great granduncle",
                   "nineteenth great granduncle", "twentieth great granduncle", ]

_nephew_level = [ "", "nephew", "grandnephew", "great grandnephew", "second great grandnephew",
                  "third great grandnephew",  "fourth great grandnephew",
                  "fifth great grandnephew",  "sixth great grandnephew",
                  "seventh great grandnephew", "eighth great grandnephew",
                  "ninth great grandnephew", "tenth great grandnephew",
                  "eleventh great grandnephew",  "twelfth great grandnephew",
                  "thirteenth great grandnephew", "fourteenth great grandnephew",
                  "fifteenth great grandnephew", "sixteenth great grandnephew",
                  "seventeenth great grandnephew", "eighteenth great grandnephew",
                  "nineteenth great grandnephew", "twentieth great grandnephew", ]

_niece_level = [ "", "niece", "grandniece", "great grandniece", "second great grandniece",
                 "third great grandniece",  "fourth great grandniece",
                 "fifth great grandniece",  "sixth great grandniece",
                 "seventh great grandniece", "eighth great grandniece",
                 "ninth great grandniece", "tenth great grandniece",
                 "eleventh great grandniece",  "twelfth great grandniece",
                 "thirteenth great grandniece", "fourteenth great grandniece",
                 "fifteenth great grandniece", "sixteenth great grandniece",
                 "seventeenth great grandniece", "eighteenth great grandniece",
                 "nineteenth great grandniece", "twentieth great grandniece", ]

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------

class RelationshipCalculator:

    def __init__(self,db):
        self.db = db

    def set_db(self,db):
        self.db = db

    def apply_filter(self,person,index,plist,pmap):
        if person == None:
            return
        plist.append(person.get_id())
        pmap[person.get_id()] = index

        family_id = person.get_main_parents_family_id()
        family = self.db.find_family_from_id(family_id)
        if family != None:
            father = self.db.try_to_find_person_from_id(family.get_father_id())
            mother = self.db.try_to_find_person_from_id(family.get_mother_id())
            self.apply_filter(father,index+1,plist,pmap)
            self.apply_filter(mother,index+1,plist,pmap)

    def get_cousin(self,level,removed):
        if removed > len(_removed_level)-1 or level>len(_level_name)-1:
            return "distant relative"
        else:
            return "%s cousin%s" % (_level_name[level],_removed_level[removed])

    def get_parents(self,level):
        if level>len(_parents_level)-1:
            return "distant ancestors"
        else:
            return _parents_level[level]

    def get_father(self,level):
        if level>len(_father_level)-1:
            return "distant ancestor"
        else:
            return _father_level[level]

    def get_son(self,level):
        if level>len(_son_level)-1:
            return "distant descendant"
        else:
            return _son_level[level]

    def get_mother(self,level):
        if level>len(_mother_level)-1:
            return "distant ancestor"
        else:
            return _mother_level[level]

    def get_daughter(self,level):
        if level>len(_daughter_level)-1:
            return "distant descendant"
        else:
            return _daughter_level[level]

    def get_aunt(self,level):
        if level>len(_sister_level)-1:
            return "distant ancestor"
        else:
            return _sister_level[level]

    def get_uncle(self,level):
        if level>len(_brother_level)-1:
            return "distant ancestor"
        else:
            return _brother_level[level]

    def get_nephew(self,level):
        if level>len(_nephew_level)-1:
            return "distant descendant"
        else:
            return _nephew_level[level]

    def get_niece(self,level):
        if level>len(_niece_level)-1:
            return "distant descendant"
        else:
            return _niece_level[level]
        
    def is_spouse(self,orig,other):
        for f in orig.get_family_id_list():
            family = self.db.find_family_from_id(f)
            if family:
                if other == family.get_father_id() or other == family.get_mother_id():
                    return 1
            else:
                return 0
        return 0

    def get_relationship_distance(self,orig_person,other_person):
        """
        Returns a tuple (firstRel,secondRel,common):
        
        firstRel    Number of generations from the orig_person to their
                    closest common ancestor
        secondRel   Number of generations from the other_person to their
                    closest common ancestor
        common      list of their common ancestors, the closest is the first
        
        is returned
        """
        
        firstRel = -1
        secondRel = -1
        common = []

        firstMap = {}
        firstList = []
        secondMap = {}
        secondList = []
        rank = 9999999

        try:
            self.apply_filter(orig_person,0,firstList,firstMap)
            self.apply_filter(other_person,0,secondList,secondMap)
        except RuntimeError,msg:
            return (firstRel,secondRel,_("Relationship loop detected"))

        for person_id in firstList:
            if person_id in secondList:
                new_rank = firstMap[person_id]
                if new_rank < rank:
                    rank = new_rank
                    common = [ person_id ]
                elif new_rank == rank:
                    common.append(person_id)

        if common:
            person_id = common[0]
            secondRel = firstMap[person_id]
            firstRel = secondMap[person_id]

        return (firstRel,secondRel,common)

    def get_relationship(self,orig_person,other_person):
        """
        returns a string representping the relationshp between the two people,
        along with a list of common ancestors (typically father,mother) 
        """

        if orig_person == None:
            return ("undefined",[])

        if orig_person == other_person:
            return ('', [])

        if self.is_spouse(orig_person,other_person):
            return ("spouse",[])

        (firstRel,secondRel,common) = self.get_relationship_distance(orig_person,other_person)
        
        if type(common) == types.StringType or type(common) == types.UnicodeType:
            return (common,[])
        elif common:
            person_id = common[0]
        else:
            return ("",[])

        if firstRel == 0:
            if secondRel == 0:
                return ('',common)
            elif other_person.get_gender() == RelLib.Person.male:
                return (self.get_father(secondRel),common)
            else:
                return (self.get_mother(secondRel),common)
        elif secondRel == 0:
            if other_person.get_gender() == RelLib.Person.male:
                return (self.get_son(firstRel),common)
            else:
                return (self.get_daughter(firstRel),common)
        elif firstRel == 1:
            if other_person.get_gender() == RelLib.Person.male:
                return (self.get_uncle(secondRel),common)
            else:
                return (self.get_aunt(secondRel),common)
        elif secondRel == 1:
            if other_person.get_gender() == RelLib.Person.male:
                return (self.get_nephew(firstRel-1),common)
            else:
                return (self.get_niece(firstRel-1),common)
        else:
            if secondRel > firstRel:
                return (self.get_cousin(firstRel-1,secondRel-firstRel),common)
            else:
                return (self.get_cousin(secondRel-1,firstRel-secondRel),common)


    def get_grandparents_string(self,orig_person,other_person):
        """
        returns a string representing the relationshp between the two people,
        along with a list of common ancestors (typically father,mother) 
        """
        if orig_person == None:
            return ("undefined",[])

        if orig_person == other_person:
            return ('', [])
        
        (firstRel,secondRel,common) = self.get_relationship_distance(orig_person,other_person)
        
        if type(common) == types.StringType or type(common) == types.UnicodeType:
            return (common,[])
        elif common:
            person_id = common[0]
        else:
            return ("",[])

        if firstRel == 0:
            if secondRel == 0:
                return ('',common)
            else:
                return (self.get_parents(secondRel),common)
        else:
            return None

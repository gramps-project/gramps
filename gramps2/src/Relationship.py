#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003  Donald N. Allingham
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

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------

import RelLib
import GrampsCfg
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
def apply_filter(person,index,plist,pmap):
    if person == None:
        return
    plist.append(person)
    pmap[person.getId()] = index
    
    family = person.getMainParents()
    if family != None:
        apply_filter(family.getFather(),index+1,plist,pmap)
        apply_filter(family.getMother(),index+1,plist,pmap)

def get_cousin(level,removed):
    return "%s cousin%s" % (_level_name[level],_removed_level[removed])

def get_parents(level):
    return _parents_level[level]

def get_father(level):
    return _father_level[level]

def get_son(level):
    return _son_level[level]

def get_mother(level):
    return _mother_level[level]

def get_daughter(level):
    return _daughter_level[level]

def get_aunt(level):
    return _sister_level[level]

def get_uncle(level):
    return _brother_level[level]

def get_nephew(level):
    return _nephew_level[level]

def get_niece(level):
    return _niece_level[level]

def is_spouse(orig,other):
    for f in orig.getFamilyList():
        if other == f.getFather() or other == f.getMother():
            return 1
    return 0

def get_relationship(orig_person,other_person):
    """
    returns a string representing the relationshp between the two people,
    along with a list of common ancestors (typically father,mother) 
    """
    firstMap = {}
    firstList = []
    secondMap = {}
    secondList = []
    common = []
    rank = 9999999

    if orig_person == None:
        return ("undefined",[])

    if orig_person == other_person:
        return ('', [])
    if is_spouse(orig_person,other_person):
        return ("spouse",[])

    try:
        apply_filter(orig_person,0,firstList,firstMap)
        apply_filter(other_person,0,secondList,secondMap)
    except RuntimeError,msg:
        return (_("Relationship loop detected"),None)
    
    for person in firstList:
        if person in secondList:
            new_rank = firstMap[person.getId()]
            if new_rank < rank:
                rank = new_rank
                common = [ person ]
            elif new_rank == rank:
                common.append(person)

    firstRel = -1
    secondRel = -1

    length = len(common)
    
    if length == 1:
        person = common[0]
        secondRel = firstMap[person.getId()]
        firstRel = secondMap[person.getId()]
    elif length == 2:
        p1 = common[0]
        secondRel = firstMap[p1.getId()]
        firstRel = secondMap[p1.getId()]
    elif length > 2:
        person = common[0]
        secondRel = firstMap[person.getId()]
        firstRel = secondMap[person.getId()]

    if firstRel == -1:
        return ("",[])
    elif firstRel == 0:
        if secondRel == 0:
            return ('',common)
        elif other_person.getGender() == RelLib.Person.male:
            return (get_father(secondRel),common)
        else:
            return (get_mother(secondRel),common)
    elif secondRel == 0:
        if other_person.getGender() == RelLib.Person.male:
            return (get_son(firstRel),common)
        else:
            return (get_daughter(firstRel),common)
    elif firstRel == 1:
        if other_person.getGender() == RelLib.Person.male:
            return (get_uncle(secondRel),common)
        else:
            return (get_aunt(secondRel),common)
    elif secondRel == 1:
        if other_person.getGender() == RelLib.Person.male:
            return (get_nephew(firstRel-1),common)
        else:
            return (get_niece(firstRel-1),common)
    else:
        if secondRel > firstRel:
            return (get_cousin(firstRel-1,secondRel-firstRel),common)
        else:
            return (get_cousin(secondRel-1,firstRel-secondRel),common)

def get_grandparents_string(orig_person,other_person):
    """
    returns a string representing the relationshp between the two people,
    along with a list of common ancestors (typically father,mother) 
    """
    firstMap = {}
    firstList = []
    secondMap = {}
    secondList = []
    common = []
    rank = 9999999

    if orig_person == None:
        return ("undefined",[])

    if orig_person == other_person:
        return ('', [])

    apply_filter(orig_person,0,firstList,firstMap)
    apply_filter(other_person,0,secondList,secondMap)
    
    for person in firstList:
        if person in secondList:
            new_rank = firstMap[person.getId()]
            if new_rank < rank:
                rank = new_rank
                common = [ person ]
            elif new_rank == rank:
                common.append(person)

    firstRel = -1
    secondRel = -1

    length = len(common)
    
    if length == 1:
        person = common[0]
        secondRel = firstMap[person.getId()]
        firstRel = secondMap[person.getId()]
    elif length == 2:
        p1 = common[0]
        secondRel = firstMap[p1.getId()]
        firstRel = secondMap[p1.getId()]
    elif length > 2:
        person = common[0]
        secondRel = firstMap[person.getId()]
        firstRel = secondMap[person.getId()]

    if firstRel == 0:
        if secondRel == 0:
            return ('',common)
        else:
            return (get_parents(secondRel),common)
    else:
        return None

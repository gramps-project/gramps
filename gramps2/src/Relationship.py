#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000  Donald N. Allingham
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

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------

level_name = [ "", "First", "Second", "Third", "Fourth", "Fifth", "Sixth",
               "Seventh", "Eighth", "Ninth", "Tenth", "Eleventh", "Twelfth",
               "Thirteenth", "Fourteenth", "Fifteenth", "Sixteenth",
               "Seventeenth", "Eigthteenth", "Nineteenth", "Twentieth" ]

removed_level = [ "", " once removed", " twice removed", " three times removed",
                  " four times removed", " five times removed", " six times removed",
                  " sevent times removed", " eight times removed", " nine times removed",
                  " ten times removed", " eleven times removed", " twelve times removed",
                  " thirteen times removed", " fourteen times removed", " fifteen times removed",
                  " sixteen times removed", " seventeen times removed", " eighteen times removed",
                  " nineteen times removed", " twenty times removed" ]

father_level = [ "", "Father", "Grandfather", "Great Grandfather", "Second Great Grandfather",
                 "Third Great Grandfather",  "Fourth Great Grandfather",
                 "Fifth Great Grandfather",  "Sixth Great Grandfather",
                 "Seventh Great Grandfather", "Eighth Great Grandfather",
                 "Ninth Great Grandfather", "Tenth Great Grandfather",
                 "Eleventh Great Grandfather",  "Twelefth Great Grandfather",
                 "Thirteenth Great Grandfather", "Fourteenth Great Grandfather",
                 "Fifteenth Great Grandfather", "Sixteenth Great Grandfather",
                 "Seventeenth Great Grandfather", "Eightteenth Great Grandfather",
                 "Ninetheen Great Grandfather", "Twentieth Great Grandfather", ]

mother_level = [ "", "Mother", "Grandmother", "Great Grandmother", "Second Great Grandmother",
                 "Third Great Grandmother",  "Fourth Great Grandmother",
                 "Fifth Great Grandmother",  "Sixth Great Grandmother",
                 "Seventh Great Grandmother", "Eighth Great Grandmother",
                 "Ninth Great Grandmother", "Tenth Great Grandmother",
                 "Eleventh Great Grandmother",  "Twelefth Great Grandmother",
                 "Thirteenth Great Grandmother", "Fourteenth Great Grandmother",
                 "Fifteenth Great Grandmother", "Sixteenth Great Grandmother",
                 "Seventeenth Great Grandmother", "Eightteenth Great Grandmother",
                 "Ninetheen Great Grandmother", "Twentieth Great Grandmother", ]

son_level = [ "", "Son", "Grandson", "Great Grandson", "Second Great Grandson",
              "Third Great Grandson",  "Fourth Great Grandson",
              "Fifth Great Grandson",  "Sixth Great Grandson",
              "Seventh Great Grandson", "Eighth Great Grandson",
              "Ninth Great Grandson", "Tenth Great Grandson",
              "Eleventh Great Grandson",  "Twelefth Great Grandson",
              "Thirteenth Great Grandson", "Fourteenth Great Grandson",
              "Fifteenth Great Grandson", "Sixteenth Great Grandson",
              "Seventeenth Great Grandson", "Eightteenth Great Grandson",
              "Ninetheen Great Grandson", "Twentieth Great Grandson", ]

daughter_level = [ "", "Daughter", "Granddaughter", "Great Granddaughter", "Second Great Granddaughter",
              "Third Great Granddaughter",  "Fourth Great Granddaughter",
              "Fifth Great Granddaughter",  "Sixth Great Granddaughter",
              "Seventh Great Granddaughter", "Eighth Great Granddaughter",
              "Ninth Great Granddaughter", "Tenth Great Granddaughter",
              "Eleventh Great Granddaughter",  "Twelefth Great Granddaughter",
              "Thirteenth Great Granddaughter", "Fourteenth Great Granddaughter",
              "Fifteenth Great Granddaughter", "Sixteenth Great Granddaughter",
              "Seventeenth Great Granddaughter", "Eightteenth Great Granddaughter",
              "Ninetheen Great Granddaughter", "Twentieth Great Granddaughter", ]

sister_level = [ "", "Sister", "Aunt", "Grandaunt", "Great Grandaunt", "Second Great Grandaunt",
                 "Third Great Grandaunt",  "Fourth Great Grandaunt",
                 "Fifth Great Grandaunt",  "Sixth Great Grandaunt",
                 "Seventh Great Grandaunt", "Eighth Great Grandaunt",
                 "Ninth Great Grandaunt", "Tenth Great Grandaunt",
                 "Eleventh Great Grandaunt",  "Twelefth Great Grandaunt",
                 "Thirteenth Great Grandaunt", "Fourteenth Great Grandaunt",
                 "Fifteenth Great Grandaunt", "Sixteenth Great Grandaunt",
                 "Seventeenth Great Grandaunt", "Eightteenth Great Grandaunt",
                 "Ninetheen Great Grandaunt", "Twentieth Great Grandaunt", ]

brother_level = [ "", "Brother", "Uncle", "Granduncle", "Great Granduncle", "Second Great Granduncle",
                 "Third Great Granduncle",  "Fourth Great Granduncle",
                 "Fifth Great Granduncle",  "Sixth Great Granduncle",
                 "Seventh Great Granduncle", "Eighth Great Granduncle",
                 "Ninth Great Granduncle", "Tenth Great Granduncle",
                 "Eleventh Great Granduncle",  "Twelefth Great Granduncle",
                 "Thirteenth Great Granduncle", "Fourteenth Great Granduncle",
                 "Fifteenth Great Granduncle", "Sixteenth Great Granduncle",
                 "Seventeenth Great Granduncle", "Eightteenth Great Granduncle",
                 "Ninetheen Great Granduncle", "Twentieth Great Granduncle", ]

nephew_level = [ "", "Nephew", "Grandnephew", "Great Grandnephew", "Second Great Grandnephew",
                 "Third Great Grandnephew",  "Fourth Great Grandnephew",
                 "Fifth Great Grandnephew",  "Sixth Great Grandnephew",
                 "Seventh Great Grandnephew", "Eighth Great Grandnephew",
                 "Ninth Great Grandnephew", "Tenth Great Grandnephew",
                 "Eleventh Great Grandnephew",  "Twelefth Great Grandnephew",
                 "Thirteenth Great Grandnephew", "Fourteenth Great Grandnephew",
                 "Fifteenth Great Grandnephew", "Sixteenth Great Grandnephew",
                 "Seventeenth Great Grandnephew", "Eightteenth Great Grandnephew",
                 "Ninetheen Great Grandnephew", "Twentieth Great Grandnephew", ]
niece_level = [ "", "Niece", "Grandniece", "Great Grandniece", "Second Great Grandniece",
                 "Third Great Grandniece",  "Fourth Great Grandniece",
                 "Fifth Great Grandniece",  "Sixth Great Grandniece",
                 "Seventh Great Grandniece", "Eighth Great Grandniece",
                 "Ninth Great Grandniece", "Tenth Great Grandniece",
                 "Eleventh Great Grandniece",  "Twelefth Great Grandniece",
                 "Thirteenth Great Grandniece", "Fourteenth Great Grandniece",
                 "Fifteenth Great Grandniece", "Sixteenth Great Grandniece",
                 "Seventeenth Great Grandniece", "Eightteenth Great Grandniece",
                 "Ninetheen Great Grandniece", "Twentieth Great Grandniece", ]

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def filter(person,index,list,map):
    if person == None:
        return
    list.append(person)
    map[person.getId()] = index
    
    family = person.getMainParents()
    if family != None:
        filter(family.getFather(),index+1,list,map)
        filter(family.getMother(),index+1,list,map)

def get_cousin(f,s,level,removed):
    return "%s cousin%s of %s" % (level_name[level],removed_level[removed],f)

def get_father(f,s,level):
    return "%s of %s" % (father_level[level],f)

def get_son(f,s,level):
    return "%s of %s" % (son_level[level],f)

def get_mother(f,s,level):
    return "%s of %s" % (mother_level[level],f)

def get_daughter(f,s,level):
    return "%s of %s" % (daughter_level[level],f)

def get_aunt(f,s,level):
    return "%s of %s" % (sister_level[level],f)

def get_uncle(f,s,level):
    return "%s of %s" % (brother_level[level],f)

def get_nephew(f,s,level):
    return "%s of %s" % (nephew_level[level],f)

def get_niece(f,s,level):
    return "%s of %s" % (niece_level[level],f)

def get_relationship(orig_person,other_person):
    firstMap = {}
    firstList = []
    secondMap = {}
    secondList = []
    common = []
    rank = 9999999

    filter(orig_person,0,firstList,firstMap)
    filter(other_person,0,secondList,secondMap)
    
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

    firstName = orig_person.getPrimaryName().getRegularName()
    secondName = other_person.getPrimaryName().getRegularName()

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
        return "No relationship to %s" % firstName
    elif firstRel == 0:
        if secondRel == 0:
            return firstName
        elif other_person.getGender() == RelLib.Person.male:
            return get_father(firstName,secondName,secondRel)
        else:
            return get_mother(firstName,secondName,secondRel)
    elif secondRel == 0:
        if other_person.getGender() == RelLib.Person.male:
            return get_son(firstName,secondName,firstRel)
        else:
            return get_daughter(firstName,secondName,firstRel)
    elif firstRel == 1:
        if other_person.getGender() == RelLib.Person.male:
            return get_uncle(firstName,secondName,secondRel)
        else:
            return get_aunt(firstName,secondName,secondRel)
    elif secondRel == 1:
        if other_person.getGender() == RelLib.Person.male:
            return get_nephew(firstName,secondName,firstRel-1)
        else:
            return get_niece(firstName,secondName,firstRel-1)
    else:
        if secondRel > firstRel:
            return get_cousin(firstName,secondName,firstRel-1,secondRel-firstRel)
        else:
            return get_cousin(firstName,secondName,secondRel-1,firstRel-secondRel)


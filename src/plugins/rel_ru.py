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

#
# Written by Alex Roitman, largely based on Relationship.py by Don Allingham.
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

_male_cousin_level = [ "двоюродный", "троюродный", "четвероюродный", ]

_female_cousin_level = [ "двоюродная", "троюродная", "четвероюродная", ]

_junior_male_removed_level = [ "брат", "племянник", "внучатый племянник", 
                             "правнучатый племянник", "праправнучатый племянник", ]

_junior_female_removed_level = [ "сестра", "племянница", "внучатая племянница",
                             "правнучатая племянница", "праправнучатая племянница", ]

_senior_male_removed_level = [ "дядя", "дед", "прадед", "прапрадед", ]

_senior_female_removed_level = [ "тетка", "бабка", "прабабка", "прапрабабка", ]

_father_level = [ "", "отец", "дед", "прадед", "прапрадед", 
                 "пра-пра-прадед", "пра-пра-пра-прадед", ]

_mother_level = [ "", "мать", "бабка", "прабабка", "прапрабабка", 
                  "пра-пра-прабабка",  "пра-пра-пра-прабабка", ]

_son_level = [ "", "сын", "внук", "правнук", "праправнук", 
             "пра-пра-правнук", "пра-пра-пра-правнук", ]

_daughter_level = [ "", "дочь", "внучка", "правнучка", "праправнучка", 
                  "пра-пра-правнучка",  "пра-пра-пра-правнучка", ]

_sister_level = [ "", "сестра", "тетка", "двоюродная бабка", 
                "двоюродная прабабка", "двоюродная прапрабабка", ]

_brother_level = [ "", "брат", "дядя", "двоюродный дед", 
                 "двоюродный прадед", "двоюродный прапрадед", ]

_nephew_level = [ "", "племянник", "внучатый племянник", 
                "правнучатый племянник", "праправнучатый племянник", ]

_niece_level = [ "", "племянница", "внучатая племянница", 
               "правнучатая племянница", "праправнучатая племянница", ]

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def getallancestors(person,index,ancestorlist,ancestormap):
    if person == None:
        return
    ancestorlist.append(person)
    ancestormap[person.getId()] = index
    
    family = person.getMainParents()
    if family != None:
        getallancestors(family.getFather(),index+1,ancestorlist,ancestormap)
        getallancestors(family.getMother(),index+1,ancestorlist,ancestormap)

def get_junior_male_cousin(level,removed):
    return "%s %s" % (_male_cousin_level[level],_junior_male_removed_level[removed])

def get_senior_male_cousin(level,removed):
    return "%s %s" % (_male_cousin_level[level],_senior_male_removed_level[removed])

def get_junior_female_cousin(level,removed):
    return "%s %s" % (_female_cousin_level[level],_junior_female_removed_level[removed])

def get_senior_female_cousin(level,removed):
    return "%s %s" % (_female_cousin_level[level],_senior_female_removed_level[removed])

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
    Returns a string representing the relationshp between the two people,
    along with a list of common ancestors (typically father,mother) 
    
    Special cases: relation strings "undefined" and "spouse".
    """

    firstMap = {}
    firstList = []
    secondMap = {}
    secondList = []
    common = []
    rank = 9999999
    
    if orig_person == None:
        return ("undefined",[])
    
    firstName = orig_person.getPrimaryName().getRegularName()
    secondName = other_person.getPrimaryName().getRegularName()
    
    if orig_person == other_person:
        return ('', [])
    if is_spouse(orig_person,other_person):
        return ("spouse",[])

    getallancestors(orig_person,0,firstList,firstMap)
    getallancestors(other_person,0,secondList,secondMap)
    
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
            if other_person.getGender() == RelLib.Person.male:
                return (get_senior_male_cousin(firstRel-1,secondRel-firstRel),common)
            else:
                return (get_senior_female_cousin(firstRel-1,secondRel-firstRel),common)
        else:
            if other_person.getGender() == RelLib.Person.male:
                return (get_junior_male_cousin(secondRel-1,firstRel-secondRel),common)
            else:
                return (get_junior_female_cousin(firstRel-1,secondRel-firstRel),common)
    

#-------------------------------------------------------------------------
#
# Register this function with the Plugins system 
#
#-------------------------------------------------------------------------
from Plugins import register_relcalc

register_relcalc(get_relationship,
    ["ru","RU","ru_RU","koi8r","ru_koi8r","russian","Russian","ru_RU.koi8r"])

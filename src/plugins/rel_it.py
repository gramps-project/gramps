# -*- coding: utf-8 -*-
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
# Written by Lorenzo Cappelletti <lorenzo.cappelletti@email.it>, 2003
#

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------

import RelLib

from Relationship import apply_filter, is_spouse
from Plugins import register_relcalc


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
# Specific relationship functions
#
# To be honest, I doubt that this relationship naming method is widely
# spread... If you know of a rigorous, italian naming convention,
# please, drop me an email.
#
#-------------------------------------------------------------------------

def get_parents (level):
    return "%si genitori" % _level[level]

def get_father (level, gender="o"):
    if   level == 0: return ""
    elif level == 1: return "padre"
    elif level == 2: return "nonn%s" % gender
    elif level == 3: return "bisnonn%s" % gender
    else           : return "%s%s nonn%s" % (_level[level], gender, gender)

def get_mother (level):
    if   level == 1: return "madre"
    else           : return get_father(level, "a")

def get_son (level, gender="o"):
    if   level == 0: return ""
    elif level == 1: return "figli%s" % gender
    elif level == 2: return "nipote"
    elif level == 3: return "pronipote"
    else           : return "%s%s nipote" % (_level[level], gender)

def get_daughter (level):
    return get_son(level, "a")

def get_uncle (level, gender="o"):
    if   level == 0: return ""
    elif level == 1: return "fratello"
    elif level == 2: return "zi%s" % gender
    elif level == 3: return "prozi%s" % gender
    else           : return "%s%s zi%s" % (_level[level], gender, gender)

def get_aunt (level):
    if   level == 1: return "sorella"
    else           : return get_uncle(level, "a")

def get_nephew (level, gender="o"):
    if   level == 0: return ""
    elif level == 1: return "nipote"
    elif level == 2: return "pronipote"
    else           : return "%s%s nipote" % (_level[level], gender)

def get_niece(level):
    return get_nephew(level, "a")

def get_male_cousin (levelA, levelB, gender="o"):
    return "cugin%s di %so grado (%i-%i)" \
           % (gender, _level[levelA+levelB-1], levelA, levelB)

def get_female_cousin (levelA, levelB):
    return get_male_cousin(levelA, levelB, "a")


#-------------------------------------------------------------------------
#
# get_relationship
#
#-------------------------------------------------------------------------

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
        return ("non definito",[])

    if orig_person == other_person:
        return ('', [])
    if is_spouse(orig_person,other_person):
        return ("coniuge",[])

    apply_filter(orig_person,0,firstList,firstMap)
    apply_filter(other_person,0,secondList,secondMap)

    for person in firstList:
        if person in secondList:
            new_rank = firstMap[person.get_id()]
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
        secondRel = firstMap[person.get_id()]
        firstRel = secondMap[person.get_id()]
    elif length == 2:
        p1 = common[0]
        secondRel = firstMap[p1.get_id()]
        firstRel = secondMap[p1.get_id()]
    elif length > 2:
        person = common[0]
        secondRel = firstMap[person.get_id()]
        firstRel = secondMap[person.get_id()]

    if firstRel == -1:
        return ("",[])
    elif firstRel == 0:
        if secondRel == 0:
            return ('',common)
        elif other_person.get_gender() == RelLib.Person.male:
            return (get_father(secondRel),common)
        else:
            return (get_mother(secondRel),common)
    elif secondRel == 0:
        if other_person.get_gender() == RelLib.Person.male:
            return (get_son(firstRel),common)
        else:
            return (get_daughter(firstRel),common)
    elif firstRel == 1:
        if other_person.get_gender() == RelLib.Person.male:
            return (get_uncle(secondRel),common)
        else:
            return (get_aunt(secondRel),common)
    elif secondRel == 1:
        if other_person.get_gender() == RelLib.Person.male:
            return (get_nephew(firstRel-1),common)
        else:
            return (get_niece(firstRel-1),common)
    else:
        if other_person.get_gender() == RelLib.Person.male:
            return (get_male_cousin(firstRel-1, secondRel-1), common)
        else:
            return (get_female_cousin(firstRel-1, secondRel-1), common)


#-------------------------------------------------------------------------
#
# Function registration
#
#-------------------------------------------------------------------------

register_relcalc(get_relationship,
    ["it", "IT", "it_IT", "it_IT@euro", "it_IT.utf8"])

# Local variables:
# buffer-file-coding-system: utf-8
# End:

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
# Written by Egyeki Gergely <egeri@elte.hu>, 2004
#
#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------

import RelLib
import Date

from Relationship import apply_filter, is_spouse
from Plugins import register_relcalc


#-------------------------------------------------------------------------
#
# Shared constants
#
#-------------------------------------------------------------------------

_level =\
    ["", "", "másod", "harmad", "negyed", "ötöd", "hatod",
     "heted", "nyolcad", "kilenced", "tized", "tizenegyed", "tizenketted",
     "tizenharmad", "tizennegyed", "tizenötöd", "tizenhatod",
     "tizenheted", "tizennyolcad", "tizenkilenced", "huszad","huszonegyed"]


#-------------------------------------------------------------------------
#
# Specific relationship functions
#
#-------------------------------------------------------------------------

def get_parents (level):
    if   level == 0: return ""
    elif level == 1: return "szülei"
    elif level == 2: return "nagyszülei"
    elif level == 3: return "dédszülei"
    elif level == 4: return "ükszülei"
    else           : return "%s szülei" % _level[level]



def get_father (level):
    if   level == 0: return ""
    elif level == 1: return "apja"
    elif level == 2: return "nagyapja"
    elif level == 3: return "dédapja"
    elif level == 4: return "ükapja"
    else           : return "%s ükapja" % (_level[level])

def get_mother (level):
    if   level == 0: return ""
    elif level == 1: return "anyja"
    elif level == 2: return "nagyanyja"
    elif level == 3: return "dédanyja"
    elif level == 4: return "ükanyja"
    else           : return "%s ükanyja" % (_level[level])



def get_son (level):
    if   level == 0: return ""
    elif level == 1: return "fia"
    elif level == 2: return "unokája"
    elif level == 3: return "dédunokája"
    elif level == 4: return "ükunokája"
    else           : return "%s unokája" % (_level[level])


def get_daughter (level):
    if   level == 0: return ""
    elif level == 1: return "lánya"
    else           : return get_son(level)





def get_uncle (level):
    if   level == 0: return ""
    elif level == 1: return "testvére"
    elif level == 2: return "nagybátyja"
    else           : return "%s nagybátyja" % (_level[level])


def get_aunt (level):
    if   level == 0: return ""
    elif level == 1: return "testvére"
    elif level == 2: return "nagynénje"
    else           : return "%s nagynénje" % (_level[level])




def get_nephew (level):
    if   level == 0: return ""
    elif level == 1: return "unokája"
    else           : return "%s unokája" % (_level[level])

def get_niece(level):
    return get_nephew(level)




def get_male_cousin (level):
    if   level == 0: return ""
    elif level == 1: return "unokatestvére"
    else           : return "%s unokatestvére" % (_level[level])

def get_female_cousin (level):
    return get_male_cousin(level)

#----------------------------------------------
#
# brother and sister age differences
#
#----------------------------------------------

def get_age_comp(orig_person,other_person):
    # 0=nothing, -1=other is younger 1=other is older
    orig_birth_event = orig_person.get_birth()
    orig_birth_date = orig_birth_event.get_date_object()
    other_birth_event = other_person.get_birth()
    other_birth_date = other_birth_event.get_date_object()
    if (orig_birth_date == "")or(other_birth_date == "") :return 0
    else  :return Date.compare_dates(orig_birth_date,other_birth_date)
          

def get_age_brother (level):
    if   level == 0  : return "testvére"
    elif level == 1  : return "öccse"
    else             : return "bátyja"

def get_age_sister (level):
    if   level == 0  : return "testvére"
    elif level == 1  : return "húga"
    else             : return "nővére"

#---------------------------------------------
#
# en: father-in-law, mother-in-law, son-in-law, daughter-in-law  
# hu: após, anyós, vő, meny
#
#---------------------------------------------

def is_fathermother_in_law(orig,other):
    for f in other.getFamilyList():
	if other == f.getFather(): sp = f.getMother()
	elif other == f.getMother() : sp = f.getFather()
        for g in orig.getFamilyList():
           if sp in g.getChildList(): return 1
    return 0

def get_fathermother_in_law_common(orig,other):
    for f in other.getFamilyList():
	if other == f.getFather(): sp = f.getMother()
	elif other == f.getMother() : sp = f.getFather()
        for g in orig.getFamilyList():
            if sp in g.getChildList(): return [sp]
    return []

#------------------------------------------------------------------------
#
# hu: sógor, sógornő
# en: brother-in-law, sister-in-law
#
#------------------------------------------------------------------------

def is_brothersister_in_law(orig,other):
    for f in orig.getFamilyList():
	if orig == f.getFather(): sp = f.getMother()
	elif orig == f.getMother() : sp = f.getFather()
	p = other.getMainParents()
	if (p != None): 
            c= p.getChildList()
	    if (other in c)and(sp in c): return 1
    return 0

def get_brothersister_in_law_common(orig,other):
    for f in orig.getFamilyList():
	if orig == f.getFather(): sp = f.getMother()
	elif orig == f.getMother() : sp = f.getFather()
	p = other.getMainParents()
	if (p != None): 
            c= p.getChildList()
	    if (other in c)and(sp in c): return [sp]
    return []

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
        return ("nem meghatározható",[])

    if orig_person == other_person:
        return ('', [])

    if is_spouse(orig_person,other_person):
        return ("házastársa",[])


    if is_fathermother_in_law(other_person,orig_person):
	if other_person.getGender() == RelLib.Person.male:
	   return ("apósa",get_fathermother_in_law_common(other_person,orig_person))
	elif other_person.getGender() == RelLib.Person.female:
	   return ("anyósa",get_fathermother_in_law_common(other_person,orig_person))
	elif other_person.getGender() == 2 :
	   return ("apósa vagy anyósa",get_fathermother_in_law_common(other_person,orig_person))

    if is_fathermother_in_law(orig_person,other_person):
	if orig_person.getGender() == RelLib.Person.male:
	   return ("veje",get_fathermother_in_law_common(orig_person,other_person))
	elif orig_person.getGender() == RelLib.Person.female:
 	   return ("menye",get_fathermother_in_law_common(orig_person,other_person))
	elif orig_person.getGender() == 2 :
 	   return ("veje vagy menye",get_fathermother_in_law_common(orig_person,other_person))

    if is_brothersister_in_law(orig_person,other_person):
       if other_person.getGender() == RelLib.Person.male:
	 return ("sógora",get_brothersister_in_law_common(orig_person,other_person))
       elif other_person.getGender() == RelLib.Person.female:
	 return ("sógornője",get_brothersister_in_law_common(orig_person,other_person))
       elif other_person.getGender() == 2 :
	 return ("sógora vagy sógornője",get_brothersister_in_law_common(orig_person,other_person))


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
            if secondRel == 1:
               return (get_age_brother(get_age_comp(orig_person,other_person)),common)
            else :return (get_uncle(secondRel),common)
        else:
            if secondRel == 1:
               return (get_age_sister(get_age_comp(orig_person,other_person)),common)
            else :return (get_aunt(secondRel),common)

    elif secondRel == 1:
        if other_person.get_gender() == RelLib.Person.male:
            return (get_nephew(firstRel-1),common)
        else:
            return (get_niece(firstRel-1),common)

    else:
        if other_person.get_gender() == RelLib.Person.male:
            return (get_male_cousin(firstRel-1), common)
        else:
            return (get_female_cousin(firstRel-1), common)


#-------------------------------------------------------------------------
#
# Function registration
#
#-------------------------------------------------------------------------

register_relcalc(get_relationship,
    ["hu", "HU", "hu_HU", "hu_HU.utf8", "hu_HU.UTF8"])

# Local variables:
# buffer-file-coding-system: utf-8
# End:

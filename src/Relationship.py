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

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------

import RelLib
import types
from TransUtils import sgettext as _

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

_children_level = [ "",
    "children",                        "grandchildren", 
    "great grandchildren",             "second great grandchildren",
    "third great grandchildren",       "fourth great grandchildren",
    "fifth great grandchildren",       "sixth great grandchildren",
    "seventh great grandchildren",     "eighth great grandchildren",
    "ninth great grandchildren",       "tenth great grandchildren",
    "eleventh great grandchildren",    "twelfth great grandchildren",
    "thirteenth great grandchildren",  "fourteenth great grandchildren",
    "fifteenth great grandchildren",   "sixteenth great grandchildren",
    "seventeenth great grandchildren", "eighteenth great grandchildren",
     "nineteenth great grandchildren", "twentieth great grandchildren", ]

_siblings_level = [ "",
    "siblings",                           "uncles/aunts", 
    "granduncles/aunts",                  "great granduncles/aunts", 
    "second great granduncles/aunts",     "third great granduncles/aunts",  
    "fourth great granduncles/aunts",     "fifth great granduncles/aunts",  
    "sixth great granduncles/aunts",      "seventh great granduncles/aunts", 
    "eighth great granduncles/aunts",     "ninth great granduncles/aunts", 
    "tenth great granduncles/aunts",      "eleventh great granduncles/aunts",  
    "twelfth great granduncles/aunts",    "thirteenth great granduncles/aunts", 
    "fourteenth great granduncles/aunts", "fifteenth great granduncles/aunts", 
    "sixteenth great granduncles/aunts",  "seventeenth great granduncles/aunts", 
    "eighteenth great granduncles/aunts", "nineteenth great granduncles/aunts", 
    "twentieth great granduncles/aunts", ]

_nephews_nieces_level = [   "", 
                            "siblings",
                            "nephews/nieces",
                            "grandnephews/nieces", 
                            "great grandnephews/nieces",
                            "second great grandnephews/nieces",
                            "third great grandnephews/nieces",
                            "fourth great grandnephews/nieces",
                            "fifth great grandnephews/nieces",
                            "sixth great grandnephews/nieces",
                            "seventh great grandnephews/nieces",
                            "eighth great grandnephews/nieces",
                            "ninth great grandnephews/nieces",
                            "tenth great grandnephews/nieces",
                            "eleventh great grandnephews/nieces",
                            "twelfth great grandnephews/nieces",
                            "thirteenth great grandnephews/nieces",
                            "fourteenth great grandnephews/nieces",
                            "fifteenth great grandnephews/nieces",
                            "sixteenth great grandnephews/nieces",
                            "seventeenth great grandnephews/nieces",
                            "eighteenth great grandnephews/nieces",
                            "nineteenth great grandnephews/nieces",
                            "twentieth great grandnephews/nieces",    ]


#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------

MAX_DEPTH = 15

class RelationshipCalculator:

    def __init__(self):
        pass

    def __apply_filter(self,db,person,rel_str,plist,pmap,gen=1):
        if person == None or gen > MAX_DEPTH:
            return
        gen += 1
        plist.append(person.handle)
        pmap[person.handle] = rel_str

        family_handle = person.get_main_parents_family_handle()
        try:
            if family_handle:
                family = db.get_family_from_handle(family_handle)
                fhandle = family.father_handle
                if fhandle:
                    father = db.get_person_from_handle(fhandle)
                    self.__apply_filter(db,father,rel_str+'f',plist,pmap,gen)
                mhandle = family.mother_handle
                if mhandle:
                    mother = db.get_person_from_handle(mhandle)
                    self.__apply_filter(db,mother,rel_str+'m',plist,pmap,gen)
        except:
            return

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
        
    def is_spouse(self,db,orig,other):
        for f in orig.get_family_handle_list():
            family = db.get_family_from_handle(f)
            if family and other.get_handle() in [family.get_father_handle(),
                                                 family.get_mother_handle()]:
                family_rel = family.get_relationship()
                # Determine person's gender
                if other.get_gender() == RelLib.Person.MALE:
                    gender = RelLib.Person.MALE
                elif other.get_gender() == RelLib.Person.FEMALE:
                    gender = RelLib.Person.FEMALE
                # Person's gender is unknown, try guessing from spouse's
                elif orig.get_gender() == RelLib.Person.MALE:
                    if family_rel == RelLib.FamilyRelType.CIVIL_UNION:
                        gender = RelLib.Person.MALE
                    else:
                        gender = RelLib.Person.FEMALE
                elif orig.get_gender() == RelLib.Person.FEMALE:
                    if family_rel == RelLib.FamilyRelType.CIVIL_UNION:
                        gender = RelLib.Person.FEMALE
                    else:
                        gender = RelLib.Person.MALE
                else:
                    gender = RelLib.Person.UNKNOWN

                if family_rel == RelLib.FamilyRelType.MARRIED:
                    if gender == RelLib.Person.MALE:
                        return _("husband")
                    elif gender == RelLib.Person.FEMALE:
                        return _("wife")
                    else:
                        return _("gender unknown|spouse")
                elif family_rel == RelLib.FamilyRelType.UNMARRIED:
                    if gender == RelLib.Person.MALE:
                        return _("unmarried|husband")
                    elif gender == RelLib.Person.FEMALE:
                        return _("unmarried|wife")
                    else:
                        return _("gender unknown,unmarried|spouse")
                elif family_rel == RelLib.FamilyRelType.CIVIL_UNION:
                    if gender == RelLib.Person.MALE:
                        return _("male,civil union|partner")
                    elif gender == RelLib.Person.FEMALE:
                        return _("female,civil union|partner")
                    else:
                        return _("gender unknown,civil union|partner")
                else:
                    if gender == RelLib.Person.MALE:
                        return _("male,unknown relation|partner")
                    elif gender == RelLib.Person.FEMALE:
                        return _("female,unknown relation|partner")
                    else:
                        return _("gender unknown,unknown relation|partner")
            else:
                return None
        return None

    def get_relationship_distance(self,db,orig_person,other_person):
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
            self.__apply_filter(db,orig_person,'',firstList,firstMap)
            self.__apply_filter(db,other_person,'',secondList,secondMap)
        except RuntimeError:
            return (firstRel,secondRel,_("Relationship loop detected"))

        for person_handle in firstList:
            if person_handle in secondList:
                new_rank = len(firstMap[person_handle])
                if new_rank < rank:
                    rank = new_rank
                    common = [ person_handle ]
                elif new_rank == rank:
                    common.append(person_handle)

        if common:
            person_handle = common[0]
            secondRel = firstMap[person_handle]
            firstRel = secondMap[person_handle]

        return (firstRel,secondRel,common)

    def get_relationship(self,db,orig_person,other_person):
        """
        returns a string representping the relationshp between the two people,
        along with a list of common ancestors (typically father,mother) 
        """

        if orig_person == None:
            return ("undefined",[])

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
        else:
            if secondRel > firstRel:
                return (self.get_cousin(firstRel-1,secondRel-firstRel),common)
            else:
                return (self.get_cousin(secondRel-1,firstRel-secondRel),common)


    def get_grandparents_string(self,db,orig_person,other_person):
        """
        returns a string representing the relationshp between the two people,
        along with a list of common ancestors (typically father,mother) 
        """
        if orig_person == None:
            return ("undefined",[])

        if orig_person == other_person:
            return ('', [])
        
        (firstRel,secondRel,common) = \
                     self.get_relationship_distance(db,orig_person,other_person)
        
        if type(common) == types.StringType or \
           type(common) == types.UnicodeType:
            return (common,[])
        elif common:
            person_handle = common[0]
        else:
            return ("",[])

        if len(firstRel) == 0:
            if len(secondRel) == 0:
                return ('',common)
            else:
                return (self.get_parents(len(secondRel)),common)
        else:
            return None
        
    def get_plural_relationship_string(self,Ga,Gb):
        """
        Provides a string that describes the relationsip between a person, and
        a group of people with the same relationship. E.g. "grandparents" or
        "children".
        
        Ga and Gb can be used to mathematically calculate the relationship.
        See the Wikipedia entry for more information:
            http://en.wikipedia.org/wiki/Cousin#Mathematical_definitions
        
        @param Ga: The number of generations between the main person and the 
        common ancestor.
        @type Ga: int
        @param Gb: The number of generations between the group of people and the
        common ancestor
        @type Gb: int
        @returns: A string describing the relationship between the person and
        the group.
        @rtype: str
        """
        rel_str = "distant relatives"
        if Ga == 0:
            # These are descendants
            if Gb < len(_children_level):
                rel_str = _children_level[Gb]
            else:
                rel_str = "distant descendants"
        elif Gb == 0:
            # These are parents/grand parents
            if Ga < len(_parents_level):
                rel_str = _parents_level[Ga]
            else:
                rel_str = "distant ancestors"
        elif Gb == 1:
            # These are siblings/aunts/uncles
            if Ga < len(_siblings_level):
                rel_str = _siblings_level[Ga]
            else:
                rel_str = "distant uncles/aunts"
        elif Ga == 1:
            # These are nieces/nephews
            if Ga < len(_nephews_nieces_level):
                rel_str = _nephews_nieces_level[Gb]
            else:
                rel_str = "distant nephews/nieces"
        elif Ga > 1 and Ga == Gb:
            # These are cousins in the same generation
            if Ga <= len(_level_name):
                rel_str = "%s cousins" % _level_name[Ga-1]
            else:
                rel_str = "distant cousins"
        elif Ga > 1 and Ga > Gb:
            # These are cousins in different generations with the second person 
            # being in a higher generation from the common ancestor than the 
            # first person.
            if Gb <= len(_level_name) and (Ga-Gb) < len(_removed_level):
                rel_str = "%s cousins%s (up)" % ( _level_name[Gb-1], 
                                                  _removed_level[Ga-Gb] )
            else:
                rel_str =  "distant cousins"
        elif Gb > 1 and Gb > Ga:
            # These are cousins in different generations with the second person 
            # being in a lower generation from the common ancestor than the 
            # first person.
            if Ga <= len(_level_name) and (Gb-Ga) < len(_removed_level):
                rel_str = "%s cousins%s (down)" % ( _level_name[Ga-1], 
                                                    _removed_level[Gb-Ga] )
            else:
                rel_str =  "distant cousins"
        return rel_str

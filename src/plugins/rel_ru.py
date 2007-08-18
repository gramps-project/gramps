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

# $Id$

# Written by Alex Roitman, largely based on Relationship.py by Don Allingham.

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------

import RelLib
import Relationship
import types
from PluginUtils import register_relcalc

#-------------------------------------------------------------------------
#
# Russian-specific definitions of relationships
#
#-------------------------------------------------------------------------

_parents_level = [ "", "родители", 
"дедушки/бабушки", "прадедушки/прабабушки", "прапрадедушки/прапрабабушки",
]

_male_cousin_level = [ 
  "", "двоюродный", "троюродный", "четвероюродный",
  "пятиюродный", "шестиюродный", "семиюродный", "восьмиюродный",
  "девятиюродный", "десятиюродный", "одиннацатиюродный", "двенадцатиюродный", 
  "тринадцатиюродный", "четырнадцатиюродный", "пятнадцатиюродный", "шестнадцатиюродный", 
  "семнадцатиюродный", "восемнадцатиюродный", "девятнадцатиюродный","двадцатиюродный" ]

_female_cousin_level = [ 
  "", "двоюродная", "троюродная", "четвероюродная",
  "пятиюродная", "шестиюродная", "семиюродная", "восьмиюродная",
  "девятиюродная", "десятиюродная", "одиннацатиюродная", "двенадцатиюродная", 
  "тринадцатиюродная", "четырнадцатиюродная", "пятнадцатиюродная", "шестнадцатиюродная", 
  "семнадцатиюродная", "восемнадцатиюродная", "девятнадцатиюродная","двадцатиюродная" ]

_junior_male_removed_level = [ 
  "брат", "племянник", "внучатый племянник", "правнучатый племянник", 
  "праправнучатый племянник", "прапраправнучатый племянник", 
  "прапрапраправнучатый племянник" ]

_junior_female_removed_level = [ 
  "сестра", "племянница", "внучатая племянница", "правнучатая племянница", 
  "праправнучатая племянница", "прапраправнучатая племянница", 
  "прапрапраправнучатая племянница" ]

_senior_male_removed_level = [ 
  "", "дядя", "дед", "прадед", "прапрадед", "прапрапрадед","прапрапрапрадед" ]

_senior_female_removed_level = [ 
  "", "тетка", "бабка", "прабабка", "прапрабабка", "прапрапрабабка","прапрапрапрабабка" ]

_father_level = [ 
  "", "отец", "дед", "прадед", "прапрадед", "прапрапрадед", "прапрапрапрадед" ]

_mother_level = [ 
   "", "мать", "бабка", "прабабка", "прапрабабка", "прапрапрабабка", "прапрапрапрабабка" ]

_son_level = [ 
  "", "сын", "внук", "правнук", "праправнук", "прапраправнук", "прапрапраправнук" ]

_daughter_level = [ 
  "", "дочь", "внучка", "правнучка", "праправнучка", "прапраправнучка",
  "прапрапраправнучка" ]

_sister_level = [ 
  "", "сестра", "тетка", "двоюродная бабка", "двоюродная прабабка", 
  "двоюродная прапрабабка", "двоюродная прапрапрабабка", "двоюродная прапрапрапрабабка" ]

_brother_level = [ 
  "", "брат", "дядя", "двоюродный дед", "двоюродный прадед", 
  "двоюродный прапрадед", "двоюродный прапрапрадед", "двоюродный прапрапрапрадед" ]

_nephew_level = [ 
  "", "племянник", "внучатый племянник", "правнучатый племянник", 
  "праправнучатый племянник", "прапраправнучатый племянник", 
  "прапрапраправнучатый племянник" ]

_niece_level = [ 
  "", "племянница", "внучатая племянница", "правнучатая племянница", 
  "праправнучатая племянница", "прапраправнучатая племянница", 
  "прапрапраправнучатая племянница" ]

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class RelationshipCalculator(Relationship.RelationshipCalculator):

    def __init__(self):
        Relationship.RelationshipCalculator.__init__(self)

    def get_parents(self,level):
        if level>len(_parents_level)-1:
            return "дальние родственники"
        else:
            return _parents_level[level]

    def get_junior_male_cousin(self,level,removed):
        if removed > len(_junior_male_removed_level)-1 or level>len(_male_cousin_level)-1:
            return "дальний родственник"
        else:
            return "%s %s" % (_male_cousin_level[level],_junior_male_removed_level[removed])

    def get_senior_male_cousin(self,level,removed):
        if removed > len(_senior_male_removed_level)-1 or level>len(_male_cousin_level)-1:
            return "дальний родственник"
        else:
            return "%s %s" % (_male_cousin_level[level],_senior_male_removed_level[removed])

    def get_junior_female_cousin(self,level,removed):
        if removed > len(_junior_female_removed_level)-1 or level>len(_male_cousin_level)-1:
            return "дальняя родственница"
        else:
            return "%s %s" % (_female_cousin_level[level],_junior_female_removed_level[removed])

    def get_senior_female_cousin(self,level,removed):
        if removed > len(_senior_female_removed_level)-1 or level>len(_male_cousin_level)-1:
            return "дальняя родственница"
        else:
            return "%s %s" % (_female_cousin_level[level],_senior_female_removed_level[removed])

    def get_father(self,level):
        if level>len(_father_level)-1:
            return "дальний предок"
        else:
            return _father_level[level]

    def get_son(self,level):
        if level>len(_son_level)-1:
            return "дальний потомок"
        else:
            return _son_level[level]

    def get_mother(self,level):
        if level>len(_mother_level)-1:
            return "дальний предок"
        else:
            return _mother_level[level]

    def get_daughter(self,level):
        if level>len(_daughter_level)-1:
            return "дальний потомок"
        else:
            return _daughter_level[level]

    def get_aunt(self,level):
        if level>len(_sister_level)-1:
            return "дальний предок"
        else:
            return _sister_level[level]

    def get_uncle(self,level):
        if level>len(_brother_level)-1:
            return "дальний предок"
        else:
            return _brother_level[level]

    def get_nephew(self,level):
        if level>len(_nephew_level)-1:
            return "дальний потомок"
        else:
            return _nephew_level[level]

    def get_niece(self,level):
        if level>len(_niece_level)-1:
            return "дальний потомок"
        else:
            return _niece_level[level]

    def get_relationship(self,db,orig_person,other_person):
        """
        Returns a string representing the relationshp between the two people,
        along with a list of common ancestors (typically father,mother) 
        
        Special cases: relation strings "", "undefined" and "spouse".
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
        elif secondRel > firstRel:
            if other_person.get_gender() == RelLib.Person.MALE:
                return (self.get_senior_male_cousin(firstRel-1,secondRel-firstRel),common)
            else:
                return (self.get_senior_female_cousin(firstRel-1,secondRel-firstRel),common)
        else:
            if other_person.get_gender() == RelLib.Person.MALE:
                return (self.get_junior_male_cousin(secondRel-1,firstRel-secondRel),common)
            else:
                return (self.get_junior_female_cousin(secondRel-1,firstRel-secondRel),common)
    
#-------------------------------------------------------------------------
#
# Register this class with the Plugins system 
#
#-------------------------------------------------------------------------
register_relcalc(RelationshipCalculator,
    ["ru","RU","ru_RU","koi8r","ru_koi8r","russian","Russian","ru_RU.koi8r","ru_RU.KOI8-R","ru_RU.utf8","ru_RU.UTF8", "ru_RU.utf-8","ru_RU.UTF-8","ru_RU.iso88595","ru_RU.iso8859-5","ru_RU.iso-8859-5"])

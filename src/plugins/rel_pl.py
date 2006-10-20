# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2006  Donald N. Allingham
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

# Written by Piotr Czubaszek, largely based on rel_de.py by Alex Roitman.

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
# Polish-specific definitions of relationships
#
#-------------------------------------------------------------------------

_cousin_level = [ "", "kuzyn", 
  "drugi kuzyn", "trzeci kuzyn", "czwarty kuzyn", "piąty kuzyn", "szóśty kuzyn","siódmy kuzyn", "ósmy kuzyn", "dziewiąty kuzyn", "dziesiąty kuzyn", "jedenasty kuzyn", "dwunasty kuzyn", "trzynasty kuzyn", "czternasty kuzyn", "piętnasty kuzyn", "szesnasty kuzyn", "siedemnasty kuzyn","osiemnasty kuzyn"
  ]

_removed_level = [ "", "pierwszego", "drugiego", "trzeciego", "czwartego", "piątego",
  "szóstego", "siódmego", "ósmego", "dziewiątego", "dziesiątego", "jedenastego", "dwunastego", "trzynastego", "czternastego", "piętnastego", "szesnastego", "siedemnasego", "osiemnastego", "dziewiętnastego", "dwudziestego" ]

_father_level = [ "", "ojciec", 
  "dziadek", 
  "pradziadek", 
  "prapradziadek", 
  "praprapradziadek", 
  "praprapraprapradziadek",
  "prapraprapraprapradziadek",
  "praprapraprapraprapradziadek",
  "prapraprapraprapraprapradziadek",
  "praprapraprapraprapraprapradziadek",
  "prapraprapraprapraprapraprapradziadek",
  "praprapraprapraprapraprapraprapradziadek",
  "prapraprapraprapraprapraprapraprapradziadek",
  "praprapraprapraprapraprapraprapraprapradziadek",
  "prapraprapraprapraprapraprapraprapraprapradziadek",
  "praprapraprapraprapraprapraprapraprapraprapradziadek",
  "prapraprapraprapraprapraprapraprapraprapraprapradziadek",
  "praprapraprapraprapraprapraprapraprapraprapraprapradziadek",
  "prapraprapraprapraprapraprapraprapraprapraprapraprapradziadek",
  "praprapraprapraprapraprapraprapraprapraprapraprapraprapradziadek",
  "prapraprapraprapraprapraprapraprapraprapraprapraprapraprapradziadek",
  "praprapraprapraprapraprapraprapraprapraprapraprapraprapraprapradziadek",
]

_mother_level = [ "", "matka", 
  "babcia", 
  "prababcia", 
  "praprababcia", 
  "prapraprababcia", 
  "prapraprapraprababcia",
  "praprapraprapraprababcia",
  "prapraprapraprapraprababcia",
  "praprapraprapraprapraprababcia",
  "prapraprapraprapraprapraprababcia",
  "praprapraprapraprapraprapraprababcia",
  "prapraprapraprapraprapraprapraprababcia",
  "praprapraprapraprapraprapraprapraprababcia",
  "prapraprapraprapraprapraprapraprapraprababcia",
  "praprapraprapraprapraprapraprapraprapraprababcia",
  "prapraprapraprapraprapraprapraprapraprapraprababcia",
  "praprapraprapraprapraprapraprapraprapraprapraprababcia",
  "prapraprapraprapraprapraprapraprapraprapraprapraprababcia",
  "praprapraprapraprapraprapraprapraprapraprapraprapraprababcia",
  "prapraprapraprapraprapraprapraprapraprapraprapraprapraprababcia",
  "praprapraprapraprapraprapraprapraprapraprapraprapraprapraprababcia",
  "prapraprapraprapraprapraprapraprapraprapraprapraprapraprapraprababcia",
]

_son_level = [ "", "syn", 
  "wnuk", 
  "prawnuk", 
  "praprawnuk", 
  "prapraprauwnuk", 
  "prapraprapraprawnuk",
  "praprapraprapraprawnuk",
  "prapraprapraprapraprawnuk",
  "praprapraprapraprapraprawnuk",
  "prapraprapraprapraprapraprawnuk",
  "praprapraprapraprapraprapraprawnuk",
  "prapraprapraprapraprapraprapraprawnuk",
  "praprapraprapraprapraprapraprapraprawnuk",
  "prapraprapraprapraprapraprapraprapraprawnuk",
  "praprapraprapraprapraprapraprapraprapraprawnuk",
  "prapraprapraprapraprapraprapraprapraprapraprawnuk",
  "praprapraprapraprapraprapraprapraprapraprapraprawnuk",
  "prapraprapraprapraprapraprapraprapraprapraprapraprawnuk",
  "praprapraprapraprapraprapraprapraprapraprapraprapraprawnuk",
  "prapraprapraprapraprapraprapraprapraprapraprapraprapraprawnuk",
  "praprapraprapraprapraprapraprapraprapraprapraprapraprapraprawnuk",
  "prapraprapraprapraprapraprapraprapraprapraprapraprapraprapraprawnuk",
]

_daughter_level = [ "", "córka", 
  "wnuczka", 
  "prawnuczka", 
  "praprawnuczka", 
  "prapraprauwnuczka", 
  "prapraprapraprawnuczka", 
  "praprapraprapraprawnuczka", 
  "prapraprapraprapraprawnuczka", 
  "praprapraprapraprapraprawnuczka", 
  "prapraprapraprapraprapraprawnuczka", 
  "praprapraprapraprapraprapraprawnuczka", 
  "prapraprapraprapraprapraprapraprawnuczka", 
  "praprapraprapraprapraprapraprapraprawnuczka", 
  "prapraprapraprapraprapraprapraprapraprawnuczka", 
  "praprapraprapraprapraprapraprapraprapraprawnuczka", 
  "prapraprapraprapraprapraprapraprapraprapraprawnuczka", 
  "praprapraprapraprapraprapraprapraprapraprapraprawnuczka", 
  "prapraprapraprapraprapraprapraprapraprapraprapraprawnuczka", 
  "praprapraprapraprapraprapraprapraprapraprapraprapraprawnuczka", 
  "prapraprapraprapraprapraprapraprapraprapraprapraprapraprawnuczka", 
  "praprapraprapraprapraprapraprapraprapraprapraprapraprapraprawnuczka", 
  "prapraprapraprapraprapraprapraprapraprapraprapraprapraprapraprawnuczka", 
]

_sister_level = [ "", "siostra", "ciotka", 
  "babcia stryjeczna/cioteczna", 
  "prababcia stryjeczna/cioteczna", 
  "praprababcia stryjeczna/cioteczna", 
  "prapraprababcia stryjeczna/cioteczna", 
  "praprapraprababcia stryjeczna/cioteczna", 
  "prapraprapraprababcia stryjeczna/cioteczna", 
  "praprapraprapraprababcia stryjeczna/cioteczna", 
  "prapraprapraprapraprababcia stryjeczna/cioteczna", 
  "praprapraprapraprapraprababcia stryjeczna/cioteczna", 
  "prapraprapraprapraprapraprababcia stryjeczna/cioteczna", 
  "praprapraprapraprapraprapraprababcia stryjeczna/cioteczna", 
  "prapraprapraprapraprapraprapraprababcia stryjeczna/cioteczna", 
  "praprapraprapraprapraprapraprapraprababcia stryjeczna/cioteczna", 
  "prapraprapraprapraprapraprapraprapraprababcia stryjeczna/cioteczna", 
  "praprapraprapraprapraprapraprapraprapraprababcia stryjeczna/cioteczna", 
  "prapraprapraprapraprapraprapraprapraprapraprababcia stryjeczna/cioteczna", 
  "praprapraprapraprapraprapraprapraprapraprapraprababcia stryjeczna/cioteczna", 
  "prapraprapraprapraprapraprapraprapraprapraprapraprababcia stryjeczna/cioteczna", 
  "praprapraprapraprapraprapraprapraprapraprapraprapraprababcia stryjeczna/cioteczna", 
  "prapraprapraprapraprapraprapraprapraprapraprapraprapraprababcia stryjeczna/cioteczna", 
  "praprapraprapraprapraprapraprapraprapraprapraprapraprapraprababcia stryjeczna/cioteczna", 
]

_brother_level = [ "", "brat", "wuj/stryj", 
  "dziadek stryjeczny/cioteczny", 
  "pradziadek stryjeczny/cioteczny", 
  "prapradziadek stryjeczny/cioteczny",
  "praprapradziadek stryjeczny/cioteczny", 
  "prapraprapradziadek stryjeczny/cioteczny", 
  "praprapraprapradziadek stryjeczny/cioteczny", 
  "prapraprapraprapradziadek stryjeczny/cioteczny", 
  "praprapraprapraprapradziadek stryjeczny/cioteczny", 
  "prapraprapraprapraprapradziadek stryjeczny/cioteczny", 
  "praprapraprapraprapraprapradziadek stryjeczny/cioteczny", 
  "prapraprapraprapraprapraprapradziadek stryjeczny/cioteczny", 
  "praprapraprapraprapraprapraprapradziadek stryjeczny/cioteczny", 
  "prapraprapraprapraprapraprapraprapradziadek stryjeczny/cioteczny", 
  "praprapraprapraprapraprapraprapraprapradziadek stryjeczny/cioteczny", 
  "prapraprapraprapraprapraprapraprapraprapradziadek stryjeczny/cioteczny", 
  "praprapraprapraprapraprapraprapraprapraprapradziadek stryjeczny/cioteczny", 
  "prapraprapraprapraprapraprapraprapraprapraprapradziadek stryjeczny/cioteczny", 
  "praprapraprapraprapraprapraprapraprapraprapraprapradziadek stryjeczny/cioteczny", 
  "prapraprapraprapraprapraprapraprapraprapraprapraprapradziadek stryjeczny/cioteczny", 
  "praprapraprapraprapraprapraprapraprapraprapraprapraprapradziadek stryjeczny/cioteczny", 
  "prapraprapraprapraprapraprapraprapraprapraprapraprapraprapradziadek stryjeczny/cioteczny", 
]

_nephew_level = [ "", "bratanek/siostrzeniec", 
  "syn bratanka/siostrzeńca", 
  "wnuk bratanka/siostrzeńca", 
  "prawnuk bratanka/siostrzeńca", 
  "prawnuk bratanka/siostrzeńca", 
  "praprawnuk bratanka/siostrzeńca", 
  "prapraprawnuk bratanka/siostrzeńca", 
  "praprapraprawnuk bratanka/siostrzeńca", 
  "prapraprapraprawnuk bratanka/siostrzeńca", 
  "praprapraprapraprawnuk bratanka/siostrzeńca", 
  "prapraprapraprapraprawnuk bratanka/siostrzeńca", 
  "praprapraprapraprapraprawnuk bratanka/siostrzeńca", 
  "prapraprapraprapraprapraprawnuk bratanka/siostrzeńca", 
  "praprapraprapraprapraprapraprawnuk bratanka/siostrzeńca", 
  "prapraprapraprapraprapraprapraprawnuk bratanka/siostrzeńca", 
  "praprapraprapraprapraprapraprapraprawnuk bratanka/siostrzeńca", 
  "prapraprapraprapraprapraprapraprapraprawnuk bratanka/siostrzeńca", 
  "praprapraprapraprapraprapraprapraprapraprawnuk bratanka/siostrzeńca", 
  "prapraprapraprapraprapraprapraprapraprapraprawnuk bratanka/siostrzeńca", 
  "praprapraprapraprapraprapraprapraprapraprapraprawnuk bratanka/siostrzeńca", 
  "prapraprapraprapraprapraprapraprapraprapraprapraprawnuk bratanka/siostrzeńca", 
  "praprapraprapraprapraprapraprapraprapraprapraprapraprawnuk bratanka/siostrzeńca", 
]

_niece_level = [ "", "bratanica/siostrzenica", 
  "córka bratanka/siostrzeńca", 
  "wnuczka bratanka/siostrzeńca", 
  "prawnuczka bratanka/siostrzeńca", 
  "prawnuczka bratanka/siostrzeńca", 
  "praprawnuczka bratanka/siostrzeńca", 
  "prapraprawnuczka bratanka/siostrzeńca", 
  "praprapraprawnuczka bratanka/siostrzeńca", 
  "prapraprapraprawnuczka bratanka/siostrzeńca", 
  "praprapraprapraprawnuczka bratanka/siostrzeńca", 
  "prapraprapraprapraprawnuczka bratanka/siostrzeńca", 
  "praprapraprapraprapraprawnuczka bratanka/siostrzeńca", 
  "prapraprapraprapraprapraprawnuczka bratanka/siostrzeńca", 
  "praprapraprapraprapraprapraprawnuczka bratanka/siostrzeńca", 
  "prapraprapraprapraprapraprapraprawnuczka bratanka/siostrzeńca", 
  "praprapraprapraprapraprapraprapraprawnuczka bratanka/siostrzeńca", 
  "prapraprapraprapraprapraprapraprapraprawnuczka bratanka/siostrzeńca", 
  "praprapraprapraprapraprapraprapraprapraprawnuczka bratanka/siostrzeńca", 
  "prapraprapraprapraprapraprapraprapraprapraprawnuczka bratanka/siostrzeńca", 
  "praprapraprapraprapraprapraprapraprapraprapraprawnuczka bratanka/siostrzeńca", 
  "prapraprapraprapraprapraprapraprapraprapraprapraprawnuczka bratanka/siostrzeńca", 
]

_parents_level = [ "", "rodzice", 
  "dziadkowie", 
  "pradziadkowie", 
  "prapradziadkowie", 
  "praprapraudziadkowie", 
  "praprapraprapradziadkowie",
  "prapraprapraprapradziadkowie",
  "praprapraprapraprapradziadkowie",
  "prapraprapraprapraprapradziadkowie",
  "praprapraprapraprapraprapradziadkowie",
  "prapraprapraprapraprapraprapradziadkowie",
  "praprapraprapraprapraprapraprapradziadkowie",
  "prapraprapraprapraprapraprapraprapradziadkowie",
  "praprapraprapraprapraprapraprapraprapradziadkowie",
  "prapraprapraprapraprapraprapraprapraprapradziadkowie",
  "praprapraprapraprapraprapraprapraprapraprapradziadkowie",
  "prapraprapraprapraprapraprapraprapraprapraprapradziadkowie",
  "praprapraprapraprapraprapraprapraprapraprapraprapradziadkowie",
  "prapraprapraprapraprapraprapraprapraprapraprapraprapradziadkowie",
  "praprapraprapraprapraprapraprapraprapraprapraprapraprapradziadkowie",
  "prapraprapraprapraprapraprapraprapraprapraprapraprapraprapradziadkowie",
  "praprapraprapraprapraprapraprapraprapraprapraprapraprapraprapradziadkowie",
]

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class RelationshipCalculator(Relationship.RelationshipCalculator):

    def __init__(self,db):
        Relationship.RelationshipCalculator.__init__(self,db)

    def get_parents(self,level):
        if level>len(_parents_level)-1:
            return "dalecy przodkowie"
        else:
            return _parents_level[level]

    def get_junior_male_cousin(self,level,removed):
        if removed > len(_removed_level)-1 or level>len(_cousin_level)-1:
            return "daleki krewny"
        else:
            return "%s %s stopnia" % (_cousin_level[level],_removed_level[removed])

    def get_senior_male_cousin(self,level,removed):
        if removed > len(_removed_level)-1 or level>len(_brother_level)-1:
            return "daleki krewny"
        else:
            return "%s %s stopnia" % (_brother_level[level],_removed_level[removed])

    def get_junior_female_cousin(self,level,removed):
        if removed > len(_removed_level)-1 or level>len(_cousin_level)-1:
            return "daleka krewna"
        else:
            return "%ska %s stopnia" % (_cousin_level[level],_removed_level[removed])

    def get_senior_female_cousin(self,level,removed):
        if removed > len(_removed_level)-1 or level>len(_sister_level)-1:
            return "daleka krewna"
        else:
            return "%s %s stopnia" % (_sister_level[level],_removed_level[removed])

    def get_father(self,level):
        if level>len(_father_level)-1:
            return "daleki przodek"
        else:
            return _father_level[level]

    def get_son(self,level):
        if level>len(_son_level)-1:
            return "daleki potomek"
        else:
            return _son_level[level]

    def get_mother(self,level):
        if level>len(_mother_level)-1:
            return "daleki przodek"
        else:
            return _mother_level[level]

    def get_daughter(self,level):
        if level>len(_daughter_level)-1:
            return "daleki potomek"
        else:
            return _daughter_level[level]

    def get_aunt(self,level):
        if level>len(_sister_level)-1:
            return "daleki przodek"
        else:
            return _sister_level[level]

    def get_uncle(self,level):
        if level>len(_brother_level)-1:
            return "daleki przodek"
        else:
            return _brother_level[level]

    def get_nephew(self,level):
        if level>len(_nephew_level)-1:
            return "daleki potomek"
        else:
            return _nephew_level[level]

    def get_niece(self,level):
        if level>len(_niece_level)-1:
            return "daleki potomek"
        else:
            return _niece_level[level]

    def get_relationship(self,orig_person,other_person):
        """
        Returns a string representing the relationshp between the two people,
        along with a list of common ancestors (typically father,mother) 
        
        Special cases: relation strings "", "undefined" and "spouse".
        """

        if orig_person == None:
            return ("undefined",[])
    
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
                return (self.get_senior_male_cousin(secondRel-firstRel+1,secondRel-1),common)
            else:
                return (self.get_senior_female_cousin(secondRel-firstRel+1,secondRel-1),common)
        else:
            if other_person.get_gender() == RelLib.Person.MALE:
                return (self.get_junior_male_cousin(secondRel-1,firstRel-1),common)
            else:
                return (self.get_junior_female_cousin(secondRel-1,firstRel-1),common)
    
#-------------------------------------------------------------------------
#
# Register this class with the Plugins system 
#
#-------------------------------------------------------------------------
register_relcalc(RelationshipCalculator,
    ["pl","PL","pl_PL","polski","Polski","pl_PL.UTF-8", "pl_PL.utf-8", "pl_PL.utf8", "pl_PL.iso-8859-2", "pl_PL.iso8859-2", "pl_PL.cp1250", "pl_PL.cp-1250"])

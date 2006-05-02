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

# $Id: rel_sk.py,v 1.1.2.1 2006/03/16 16:22:27 rshura Exp $
# Slovak terms added by Lubo Vasko

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
#Slovak-specific definitions of relationships 
#
#-------------------------------------------------------------------------

_level_name = [ "", "prvého", "druhého", "tretieho", "štvrtého", "piateho", "šiesteho",
                "siedmeho", "ôsmeho", "deviateho", "desiateho", "jedenásteho", "dvanásteho",
                "trinásteho", "štrnásteho", "pätnásteho", "šestnásteho",
                "sedemnásteho", "osemnásteho", "devätnásteho", "dvadsiateho", "dvadsiatehoprvého", "dvadsiatehodruhého",
                "dvadsiatehotretieho", "dvadsiatehoštvrtého","dvadsiatehopiateho","dvadsiatehošiesteho","dvadsiatehosiedmeho",
                "dvadsiatehoôsmeho","dvadsiatehodeviateho","tridsiateho" ]

_parents_level = [ "", "rodičia", "starí rodičia", "prarodičia",
                   "vzdialení príbuzní", ]

_father_level = [ "", "otec", "starý otec", "prastarý otec", "prapredok", ]

_mother_level = [ "", "matka", "stará matka", "prastará matka", "prapredok", ]

_son_level = [ "", "syn", "vnuk", "pravnuk", ]

_daughter_level = [ "", "dcéra", "vnučka", "pravnučka", ]

_sister_level = [ "", "sestra", "teta", "prateta", "praprateta", ]

_brother_level = [ "", "brat", "strýko", "prastrýko", "praprastrýko", ]

_nephew_level = [ "", "synovec", "prasynovec", "praprasynovec", ]

_niece_level = [ "", "neter", "praneter", "prapraneter", ]

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class RelationshipCalculator(Relationship.RelationshipCalculator):

    def __init__(self,db):
        Relationship.RelationshipCalculator.__init__(self,db)

    def get_male_cousin(self,level):
        if level>len(_level_name)-1:
            return "vzdialený príbuzný"
        else:
            return "bratranec %s stupňa" % (_level_name[level])

    def get_female_cousin(self,level):
        if level>len(_level_name)-1:
            return "vzdialená príbuzná"
        else:
            return "sesternica %s stupňa" % (_level_name[level])

    def get_parents(self,level):
        if level>len(_parents_level)-1:
            return "vzdialení príbuzní"
        else:
            return _parents_level[level]

    def get_father(self,level):
        if level>len(_father_level)-1:
            return "vzdialený príbuzný"
        else:
            return _father_level[level]

    def get_son(self,level):
        if level>len(_son_level)-1:
            return "vzdialený potomok"
        else:
            return _son_level[level]

    def get_mother(self,level):
        if level>len(_mother_level)-1:
            return "vzdialený predok"
        else:
            return _mother_level[level]

    def get_daughter(self,level):
        if level>len(_daughter_level)-1:
            return "vzdialený potomok"
        else:
            return _daughter_level[level]

    def get_aunt(self,level):
        if level>len(_sister_level)-1:
            return "vzdialený predok"
        else:
            return _sister_level[level]

    def get_uncle(self,level):
        if level>len(_brother_level)-1:
            return "vzdialený predok"
        else:
            return _brother_level[level]

    def get_nephew(self,level):
        if level>len(_nephew_level)-1:
            return "vzdialený potomok"
        else:
            return _nephew_level[level]

    def get_niece(self,level):
        if level>len(_niece_level)-1:
            return "vzdialený potomok"
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
        elif firstRel == 2 and secondRel == 2:
            if other_person.get_gender() == RelLib.Person.MALE:
                return ('vlastný bratranec',common)
            else:
                return ('vlastná sesternica',common)
        elif firstRel == 3 and secondRel == 2:
            if other_person.get_gender() == RelLib.Person.MALE:
                return ('bratranec druhého stupňa',common)
            else:
                return ('sesternica druhého stupňa',common)
        elif firstRel == 2 and secondRel == 3:
            if other_person.get_gender() == RelLib.Person.MALE:
                return ('bratranec druhého stupňa',common)
            else:
                return ('sesternica druhého stupňa',common)
        else:
            if other_person.get_gender() == RelLib.Person.MALE:
                if firstRel+secondRel>len(_level_name)-1:
                    return (self.get_male_cousin(firstRel+secondRel),common)
                else:
                    return ('vzdialený bratranec',common)
            else:
                if firstRel+secondRel>len(_level_name)-1:
                    return (self.get_female_cousin(firstRel+secondRel),common)
                else:
                    return ('vzdialená sesternica',common)

#-------------------------------------------------------------------------
#
# Register this class with the Plugins system 
#
#-------------------------------------------------------------------------
register_relcalc(RelationshipCalculator,
    ["sk", "SK", "sk_SK", "slovensky", "slovak", "Slovak", "sk_SK.UTF8", "sk_SK.UTF-8", "sk_SK.utf-8", "sk_SK.utf8"])

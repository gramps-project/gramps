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

# Czech terms added by Zdeněk Hataš. Based on rel_sk.py by  Lubo Vasko

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------

import RelLib
import Relationship
from PluginUtils import register_relcalc

#-------------------------------------------------------------------------
#
# Czech-specific definitions of relationships 
#
#-------------------------------------------------------------------------

_level_name = [ "", "prvního", "druhého", "třetího", "čtvrtého", "pátého", "šestého",
                "sedmého", "osmého", "devátého", "desátého", "jedenáctého", "dvanáctého",
                "třináctého", "čtrnáctého", "patnáctého", "šestnáctého",
                "sedemnáctého", "osmnáctého", "devatenáctého", "dvacátého", "dvacátého prvního", "dvacátého druhého",
                "dvacátého třetího", "dvacátého čtvrtého","dvacátého pátého","dvacátého šestého","dvacátého sedmého",
                "dvacátého osmého","dvacátého devátého","třicátého" ]

_parents_level = [ "", "rodiče", "prarodiče", "praprarodiče",
                   "vzdálení příbuzní", ]

_father_level = [ "", "otec", "děd", "praděd", "prapředek", ]

_mother_level = [ "", "matka", "babička", "prababička", "prapředek", ]

_son_level = [ "", "syn", "vnuk", "pravnuk", ]

_daughter_level = [ "", "dcera", "vnučka", "pravnučka", ]

_sister_level = [ "", "sestra", "teta", "prateta", "praprateta", ]

_brother_level = [ "", "bratr", "strýc", "prastrýc", "praprastrýc", ]

_nephew_level = [ "", "synovec", "prasynovec", "praprasynovec", ]

_niece_level = [ "", "neteř", "praneteř", "prapraneteř", ]

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
            return "vzdálený příbuzný"
        else:
            return "bratranec %s stupně" % (_level_name[level])

    def get_female_cousin(self,level):
        if level>len(_level_name)-1:
            return "vzdálená příbuzná"
        else:
            return "sestřenice %s stupně" % (_level_name[level])

    def get_parents(self,level):
        if level>len(_parents_level)-1:
            return "vzdáleení příbuzní"
        else:
            return _parents_level[level]

    def get_father(self,level):
        if level>len(_father_level)-1:
            return "vzdálený příbuzný"
        else:
            return _father_level[level]

    def get_son(self,level):
        if level>len(_son_level)-1:
            return "vzdálený potomek"
        else:
            return _son_level[level]

    def get_mother(self,level):
        if level>len(_mother_level)-1:
            return "vzdálený předek"
        else:
            return _mother_level[level]

    def get_daughter(self,level):
        if level>len(_daughter_level)-1:
            return "vzdálený potomek"
        else:
            return _daughter_level[level]

    def get_aunt(self,level):
        if level>len(_sister_level)-1:
            return "vzdálený předek"
        else:
            return _sister_level[level]

    def get_uncle(self,level):
        if level>len(_brother_level)-1:
            return "vzdálený předek"
        else:
            return _brother_level[level]

    def get_nephew(self,level):
        if level>len(_nephew_level)-1:
            return "vzdálený potomek"
        else:
            return _nephew_level[level]

    def get_niece(self,level):
        if level>len(_niece_level)-1:
            return "vzdálený potomek"
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

        if type(common) in (str,unicode):
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
                return ('vlastní bratranec',common)
            else:
                return ('vlastní sestřenice',common)
        elif firstRel == 3 and secondRel == 2:
            if other_person.get_gender() == RelLib.Person.MALE:
                return ('bratranec druhého stupně',common)
            else:
                return ('sestřenice druhého stupně',common)
        elif firstRel == 2 and secondRel == 3:
            if other_person.get_gender() == RelLib.Person.MALE:
                return ('bratranec druhého stupně',common)
            else:
                return ('sestřenice druhého stupně',common)
        else:
            if other_person.get_gender() == RelLib.Person.MALE:
                if firstRel+secondRel>len(_level_name)-1:
                    return (self.get_male_cousin(firstRel+secondRel),common)
                else:
                    return ('vzdálený bratranec',common)
            else:
                if firstRel+secondRel>len(_level_name)-1:
                    return (self.get_female_cousin(firstRel+secondRel),common)
                else:
                    return ('vzdálená sestřenice',common)

#-------------------------------------------------------------------------
#
# Register this class with the Plugins system 
#
#-------------------------------------------------------------------------
register_relcalc(RelationshipCalculator,
    ["cs", "CZ", "cs_CZ", "česky", "czech", "Czech", "cs_CZ.UTF8", "cs_CZ.UTF-8", "cs_CZ.utf-8", "cs_CZ.utf8"])

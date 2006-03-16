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

# Written by Julio Sanchez <julio.sanchez@gmail.com>

# $Id$

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------

import RelLib
import Relationship
import types
from TransUtils import sgettext as _
from PluginUtils import register_relcalc

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------

_level_name_male = [ "", "primero", "segundo", "tercero", "cuarto", "quinto",
                "sexto", "séptimo", "octavo", "noveno", "décimo", "undécimo",
                "duodécimo", "decimotercero", "decimocuarto", "decimoquinto",
                "decimosexto", "decimoséptimo", "decimoctavo", "decimonono",
                "vigésimo", ]

# Short forms (in apocope) used before names
_level_name_male_a = [ "", "primer", "segundo", "tercer", "cuarto", "quinto",
                "sexto", "séptimo", "octavo", "noveno", "décimo", "undécimo",
                "duodécimo", "decimotercer", "decimocuarto", "decimoquinto",
                "decimosexto", "decimoséptimo", "decimoctavo", "decimonono",
                "vigésimo"]

_level_name_female = [ "", "primera", "segunda", "tercera", "cuarta", "quinta",
                "sexta", "séptima", "octava", "novena", "décima", "undécima",
                "duodécima", "decimotercera", "decimocuarta", "decimoquinta",
                "decimosexta", "decimoséptima", "decimoctava", "decimonona",
                "vigésima"]

_level_name_plural = [ "", "primeros", "segundos", "terceros", "cuartos",
                "quintos", "sextos", "séptimos", "octavos", "novenos",
                "décimos", "undécimos", "duodécimos", "decimoterceros",
                "decimocuartos", "decimoquintos", "decimosextos",
                "decimoséptimos", "decimoctavos", "decimononos",
                "vigésimos", ]

# This plugin tries to be flexible and expect little from the following
# tables.  Ancestors are named from the list for the first generations.
# When this list is not enough, ordinals are used based on the same idea,
# i.e. bisabuelo is 'segundo abuelo' and so on, that has been the
# traditional way in Spanish.  When we run out of ordinals we resort to
# N-ésimo notation, that is sort of understandable if in context.
_parents_level = [ "", "padres", "abuelos", "bisabuelos", "tatarabuelos",
                   "trastatarabuelos"]

_father_level = [ "", "padre", "abuelo", "bisabuelo", "tatarabuelo",
                  "trastatarabuelo"]

_mother_level = [ "", "madre", "abuela", "bisabuela", "tatarabuela",
                  "trastatarabuela"]

# Higher-order terms (after trastatarabuelo) on this list are not standard,
# but then there is no standard naming scheme at all for this in Spanish.
# Check http://www.genealogia-es.com/guia3.html that echoes a proposed
# scheme that has got some reception in the Spanish-language genealogy
# community. Uncomment these names if you want to use them.
#_parents_level = [ "", "padres", "abuelos", "bisabuelos", "tatarabuelos",
#                   "trastatarabuelos", "pentabuelos", "hexabuelos",
#                   "heptabuelos", "octabuelos", "eneabuelos", "decabuelos"]
#_father_level = [ "", "padre", "abuelo", "bisabuelo", "tatarabuelo",
#                  "trastatarabuelo", "pentabuelo", "hexabuelo",
#                  "heptabuelo", "octabuelo", "eneabuelo", "decabuelo"]
#_mother_level = [ "", "madre", "abuela", "bisabuela", "tatarabuela",
#                  "trastatarabuela", "pentabuela", "hexabuela",
#                  "heptabuela", "octabuela", "eneabuela", "decabuela"]

_son_level = [ "", "hijo", "nieto", "bisnieto",
               "tataranieto", "trastataranieto", ]

_daughter_level = [ "", "hija", "nieta", "bisnieta",
                    "tataranieta", "trastataranieta", ]

_sister_level = [ "", "hermana", "tía", "tía abuela",
                  "tía bisabuela", ]

_brother_level = [ "", "hermano", "tío", "tío abuelo",
                   "tío bisabuelo", ]

_nephew_level = [ "", "sobrino", "sobrino nieto", "sobrino bisnieto", ]

_niece_level = [ "", "sobrina", "sobrina nieta", "sobrina bisnieta", ]

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class RelationshipCalculator(Relationship.RelationshipCalculator):

    def __init__(self,db):
        Relationship.RelationshipCalculator.__init__(self,db)

    def get_male_cousin(self,level):
        if level<len(_level_name_male):
            return "primo %s" % (_level_name_male[level]) 
        else:
            return "primo %d-ésimo" % level 

    def get_female_cousin(self,level):
        if level<len(_level_name_female):
            return "prima %s" % (_level_name_female[level]) 
        else:
            return "prima %d-ésima" % level 

    def get_distant_uncle(self,level):
        if level<len(_level_name_male):
            return "tío %s" % (_level_name_male[level]) 
        else:
            return "tío %d-ésimo" % level 

    def get_distant_aunt(self,level):
        if level<len(_level_name_female):
            return "tía %s" % (_level_name_female[level]) 
        else:
            return "tía %d-ésima" % level 

    def get_distant_nephew(self,level):
        if level<len(_level_name_male):
            return "sobrino %s" % (_level_name_male[level]) 
        else:
            return "sobrino %d-ésimo" % level 

    def get_distant_nieve(self,level):
        if level<len(_level_name_female):
            return "sobrina %s" % (_level_name_female[level]) 
        else:
            return "sobrina %d-ésima" % level 

    def get_male_relative(self,level1,level2):
        if level1<len(_level_name_male_a):
            level1_str = _level_name_male_a[level1]
        else:
            level1_str = "%d-ésimo" % level1
        if level2<len(_level_name_male_a):
            level2_str = _level_name_male_a[level2]
        else:
            level2_str = "%d-ésimo" % level2
        level = level1 + level2
        if level<len(_level_name_male_a):
            level_str = _level_name_male_a[level]
        else:
            level_str = "%d-ésimo" % level
        return "pariente en %s grado (%s con %s)" % (level_str,level1_str,level2_str)

    def get_female_relative(self,level1,level2):
        return self.get_male_relative(level1,level2)

    def get_parents(self,level):
        if level<len(_parents_level):
            return _parents_level[level]
        elif (level-1)<len(_level_name_plural):
            return "%s abuelos" % (_level_name_plural[level-1])
        else:
            return "%d-ésimos abuelos" % (level-1)

    def get_father(self,level):
        if level<len(_father_level):
            return _father_level[level]
        elif (level-1)<len(_level_name_male_a):
            return "%s abuelo" % (_level_name_male_a[level-1])
        else:
            return "%d-ésimo abuelo" % (level-1)

    def get_son(self,level):
        if level<len(_son_level):
            return _son_level[level]
        elif (level-1)<len(_level_name_male_a):
            return "%s nieto" % (_level_name_male_a[level-1])
        else:
            return "%d-ésimo nieto" % (level-1)

    def get_mother(self,level):
        if level<len(_mother_level):
            return _mother_level[level]
        elif (level-1)<len(_level_name_female):
            return "%s abuela" % (_level_name_female[level-1])
        else:
            return "%d-ésima abuela" % (level-1)

    def get_daughter(self,level):
        if level<len(_daughter_level):
            return _daughter_level[level]
        elif (level-1)<len(_level_name_female):
            return "%s nieta" % (_level_name_female[level-1])
        else:
            return "%d-ésima nieta" % (level-1)

    def get_aunt(self,level):
        if level<len(_sister_level):
            return _sister_level[level]
        elif (level-2)<len(_level_name_female):
            return "%s tía abuela" % (_level_name_female[level-2])
        else:
            return "%d-ésima tía abuela" % (level-2)

    def get_uncle(self,level):
        if level<len(_brother_level):
            return _brother_level[level]
        elif (level-2)<len(_level_name_male_a):
            return "%s tío abuelo" % (_level_name_male_a[level-2])
        else:
            return "%d-ésimo tío abuelo" % (level-2)

    def get_nephew(self,level):
        if level<len(_nephew_level):
            return _nephew_level[level]
        elif (level-1)<len(_level_name_male_a):
            return "%s sobrino nieto" % (_level_name_male_a[level-1])
        else:
            return "%d-ésimo sobrino nieto" % (level-1)

    def get_niece(self,level):
        if level<len(_niece_level):
            return _niece_level[level]
        elif (level-1)<len(_level_name_female):
            return "%s sobrina nieta" % (_level_name_female[level-1])
        else:
            return "%d-ésima sobrina nieta" % (level-1)

    def get_relationship(self,orig_person,other_person):
        """
        returns a string representing the relationshp between the two people,
        along with a list of common ancestors (typically father,mother) 
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
                return ('primo hermano',common)
            else:
                return ('prima hermana',common)
        elif firstRel == secondRel:
            if other_person.get_gender() == RelLib.Person.MALE:
                return (self.get_male_cousin(firstRel-1),common)
            else:
                return (self.get_female_cousin(firstRel-1),common)
        elif firstRel == secondRel+1:
            if other_person.get_gender() == RelLib.Person.MALE:
                return (self.get_distant_nephew(secondRel),common)
            else:
                return (self.get_distant_niece(secondRel),common)
        elif firstRel+1 == secondRel:
            if other_person.get_gender() == RelLib.Person.MALE:
                return (self.get_distant_uncle(firstRel),common)
            else:
                return (self.get_distant_aunt(firstRel),common)
        else:
            if other_person.get_gender() == RelLib.Person.MALE:
                return (self.get_male_relative(firstRel,secondRel),common)
            else:
                return (self.get_female_relative(firstRel,secondRel),common)

#-------------------------------------------------------------------------
#
# Register this function with the Plugins system 
#
#-------------------------------------------------------------------------
register_relcalc(RelationshipCalculator,
    ["es","ES","es_ES","espanol","Espanol","es_ES.UTF8","es_ES@euro","es_ES.UTF8@euro",
            "spanish","Spanish", "es_ES.UTF-8", "es_ES.utf-8", "es_ES.utf8"])

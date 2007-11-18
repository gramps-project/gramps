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

# Portuguese version by Duarte Loreto <happyguy_pt@hotmail.com>, 2007.
# Based on the Spanish version by Julio Sanchez <julio.sanchez@gmail.com>

# $Id$

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------

import gen.lib
import Relationship
import types
from gettext import gettext as _
from PluginUtils import register_relcalc

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------

_level_name_male = [ "", "primeiro", "segundo", "terceiro", "quarto", "quinto",
                "sexto", "sétimo", "oitavo", "nono", "décimo", "décimo-primeiro",
                "décimo-segundo", "décimo-terceiro", "décimo-quarto", "décimo-quinto",
                "décimo-sexto", "décimo-sétimo", "décimo-oitavo", "décimo-nono",
                "vigésimo", ]

# Short forms (in apocope) used before names
_level_name_male_a = [ "", "primeiro", "segundo", "terceiro", "quarto", "quinto",
                "sexto", "sétimo", "oitavo", "nono", "décimo", "décimo-primeiro",
                "décimo-segundo", "décimo-terceiro", "décimo-quarto", "décimo-quinto",
                "décimo-sexto", "décimo-sétimo", "décimo-oitavo", "décimo-nono",
                "vigésimo"]

_level_name_female = [ "", "primeira", "segunda", "terceira", "quarta", "quinta",
                "sexta", "sétima", "oitava", "nona", "décima", "décima-primeira",
                "décima-segunda", "décima-terceira", "décima-quarta", "décima-quinta",
                "décima-sexta", "décima-sétima", "décima-oitava", "décima-nona",
                "vigésima"]

_level_name_plural = [ "", "primeiros", "segundos", "terceiros", "quartos",
                "quintos", "sextos", "sétimos", "oitavos", "nonos",
                "décimos", "décimos-primeiros", "décimos-segundos", "décimos-terceiros",
                "décimos-quartos", "décimos-quintos", "décimos-sextos",
                "décimos-sétimos", "décimos-oitavos", "décimos-nonos",
                "vigésimos", ]

# This plugin tries to be flexible and expect little from the following
# tables.  Ancestors are named from the list for the first generations.
# When this list is not enough, ordinals are used based on the same idea,
# i.e. bisavô is 'segundo avô' and so on, that has been the
# traditional way in Portuguese.  When we run out of ordinals we resort to
# Nº notation, that is sort of understandable if in context.
# There is a specificity for pt_BR where they can use "tataravô" instead 
# of "tetravô", being both forms correct for pt_BR but just "tetravô" 
# correct for pt. Translation keeps "tetravô".
_parents_level = [ "", "pais", "avós", "bisavós", "trisavós",
                   "tetravós"]

_father_level = [ "", "pai", "avô", "bisavô", "trisavô",
                  "tetravô"]

_mother_level = [ "", "mãe", "avó", "bisavó", "trisavó",
                  "tetravó"]

# Higher-order terms (after "tetravô") are not standard in Portuguese.
# Check http://www.geneall.net/P/forum_msg.php?id=136774 that states
# that although some people may use other greek-prefixed forms for
# higher levels, both pt and pt_BR correct form is to use, after
# "tetravô", the "quinto avô", "sexto avô", etc.

_son_level = [ "", "filho", "neto", "bisneto",
               "trisneto", ]

_daughter_level = [ "", "filha", "neta", "bisneta",
                    "trisneta", ]

_sister_level = [ "", "irmã", "tia", "tia avó", ]

_brother_level = [ "", "irmão", "tio", "tio avô", ]

_nephew_level = [ "", "sobrinho", "sobrinho neto", "sobrinho bisneto", ]

_niece_level = [ "", "sobrinha", "sobrinha neta", "sobrinha bisneta", ]

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
            return "%s primo" % (_level_name_male[level]) 
        else:
            return "%dº primo" % level 

    def get_female_cousin(self,level):
        if level<len(_level_name_female):
            return "%s prima" % (_level_name_female[level]) 
        else:
            return "%dª prima" % level 

    def get_distant_uncle(self,level):
        if level<len(_level_name_male):
            return "%s tio" % (_level_name_male[level]) 
        else:
            return "%dº tio" % level 

    def get_distant_aunt(self,level):
        if level<len(_level_name_female):
            return "%s tia" % (_level_name_female[level]) 
        else:
            return "%dª tia" % level 

    def get_distant_nephew(self,level):
        if level<len(_level_name_male):
            return "%s sobrinho" % (_level_name_male[level]) 
        else:
            return "%dº sobrinho" % level 

    def get_distant_nieve(self,level):
        if level<len(_level_name_female):
            return "%s sobrinha" % (_level_name_female[level]) 
        else:
            return "%dª sobrinha" % level 

    def get_male_relative(self,level1,level2):
        if level1<len(_level_name_male_a):
            level1_str = _level_name_male_a[level1]
        else:
            level1_str = "%dº" % level1
        if level2<len(_level_name_male_a):
            level2_str = _level_name_male_a[level2]
        else:
            level2_str = "%dº" % level2
        level = level1 + level2
        if level<len(_level_name_male_a):
            level_str = _level_name_male_a[level]
        else:
            level_str = "%dº" % level
        return "parente em %s grau (%s com %s)" % (level_str,level1_str,level2_str)

    def get_female_relative(self,level1,level2):
        return self.get_male_relative(level1,level2)

    def get_parents(self,level):
        if level<len(_parents_level):
            return _parents_level[level]
        elif (level-1)<len(_level_name_plural):
            return "%s avós" % (_level_name_plural[level-1])
        else:
            return "%dº avós" % (level-1)

    def get_father(self,level):
        if level<len(_father_level):
            return _father_level[level]
        elif (level-1)<len(_level_name_male_a):
            return "%s avô" % (_level_name_male_a[level-1])
        else:
            return "%dº avô" % (level-1)

    def get_son(self,level):
        if level<len(_son_level):
            return _son_level[level]
        elif (level-1)<len(_level_name_male_a):
            return "%s neto" % (_level_name_male_a[level-1])
        else:
            return "%dº neto" % (level-1)

    def get_mother(self,level):
        if level<len(_mother_level):
            return _mother_level[level]
        elif (level-1)<len(_level_name_female):
            return "%s avó" % (_level_name_female[level-1])
        else:
            return "%dª avó" % (level-1)

    def get_daughter(self,level):
        if level<len(_daughter_level):
            return _daughter_level[level]
        elif (level-1)<len(_level_name_female):
            return "%s neta" % (_level_name_female[level-1])
        else:
            return "%dª neta" % (level-1)

    def get_aunt(self,level):
        if level<len(_sister_level):
            return _sister_level[level]
        elif (level-2)<len(_level_name_female):
            return "%s tia avó" % (_level_name_female[level-2])
        else:
            return "%dª tia avó" % (level-2)

    def get_uncle(self,level):
        if level<len(_brother_level):
            return _brother_level[level]
        elif (level-2)<len(_level_name_male_a):
            return "%s tio avô" % (_level_name_male_a[level-2])
        else:
            return "%dº tio avô" % (level-2)

    def get_nephew(self,level):
        if level<len(_nephew_level):
            return _nephew_level[level]
        elif (level-1)<len(_level_name_male_a):
            return "%s sobrinho neto" % (_level_name_male_a[level-1])
        else:
            return "%dº sobrinho neto" % (level-1)

    def get_niece(self,level):
        if level<len(_niece_level):
            return _niece_level[level]
        elif (level-1)<len(_level_name_female):
            return "%s sobrinha neta" % (_level_name_female[level-1])
        else:
            return "%dª sobrinha neta" % (level-1)

    def get_relationship(self,orig_person,other_person):
        """
        returns a string representing the relationshp between the two people,
        along with a list of common ancestors (typically father,mother) 
        """

        if orig_person == None:
            return ("indefinido",[])

        if orig_person.get_handle() == other_person.get_handle():
            return ('', [])

        is_spouse = self.is_spouse(orig_person,other_person)
        if is_spouse:
            return (is_spouse,[])

        #get_relationship_distance changed, first data is relation to 
        #orig person, apperently secondRel in this function
        (secondRel,firstRel,common) = self.get_relationship_distance(orig_person,other_person)

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
                return ('primo irmão',common)
            else:
                return ('prima irmã',common)
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
    ["pt","PT","pt_PT","pt_BR","portugues","Portugues","pt_PT.UTF8","pt_BR.UTF8",
            "pt_PT@euro","pt_PT.UTF8@euro","pt_PT.UTF-8","pt_BR.UTF-8",
            "pt_PT.utf-8","pt_BR.utf-8","pt_PT.utf8","pt_BR.utf8"])

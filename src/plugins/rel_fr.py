# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2007  Donald N. Allingham
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

# level est utilisé pour trouver/afficher le niveau de la génération : à la %sème génération

_level_name = [ "première", "deuxième", "troisième", "quatrième", "cinquième", "sixième", "septième", "huitième", "neuvième", "dixième", "onzième", "douzième", "treizième", "quatorzième", "quinzième", "seizième", "dix-septième", "dix-huitième", "dix-neuvième", "vingtième", "vingt-et-unième", "vingt-deuxième", "vingt-deuxième", "vingt-troisième", "vingt-quatrième", "vingt-sixième", "vingt-septième", "vingt-huitième", "vingt-neuvième", "trentième", ]

# pour le degrè (canon et civil), limitation 20+20 ainsi que pour LE [premier] cousin 

_removed_level = [ "premier", "deuxième", "troisième", "quatrième", "cinquième", "sixième", "septième", "huitième", "neuvième", "dixième", "onzième", "douzième", "treizième", "quatorzième", "quinzième", "seizième", "dix-septième", "dix-huitième", "dix-neuvième", "vingtième", "vingt-et-unième", "vingt-deuxième", "vingt-deuxième", "vingt-troisième","vingt-quatrième","vingt-sixième","vingt-septième", "vingt-huitième","vingt-neuvième","trentième", "trente-et-unième", "trente-deuxième", "trente-troisième", "trente-quatrième", "trente-cinquième", "trente-sixième", "trente-septième", "trente-huitième", "trente-neuvième", "quarantième", "quanrante-et-unième", ]

# listes volontairement limitées | small lists, use generation level if > [5]

_father_level = [ "", "le père", "le grand-père", "l'arrière-grand-père", "le trisaïeul", ]

_mother_level = [ "", "la mère", "la grand-mère", "l'arrière-grand-mère", "la trisaïeule", ]

_son_level = [ "", "le fils", "le petit-fils", "l'arrière-petit-fils", ]

_daughter_level = [ "", "la fille", "la petite-fille", "l'arrière-petite-fille", ]

_sister_level = [ "", "la soeur", "la tante", "la grand-tante", "l'arrière-grand-tante", ]

_brother_level = [ "", "le frère", "l'oncle", "le grand-oncle", "l'arrière-grand-oncle", ]

_nephew_level = [ "", "le neveu", "le petit-neveu", "l'arrière-petit-neveu", ]

_niece_level = [ "", "la nièce", "la petite-nièce", "l'arrière-petite-nièce", ]

# kinship report

_parents_level = [ "", "les parents", "les grands-parents", "les arrières-grands-parents", "les trisaïeux", ]

_children_level = [ "", "les enfants", "les petits-enfants", "les arrières-petits-enfants", "les arrières-arrières-petits-enfants", ]

_siblings_level = [ "", "les frères et les soeurs", "les oncles et les tantes", "les grands-oncles et les grands-tantes", "les arrières-grands-oncles et les arrières-grands-tantes", ]

_nephews_nieces_level = [   "", "les neveux et les nièces", "les petits-neveux et les petites-nièces", "les arrière-petits-neveux et les arrières-petites-nièces", ]

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------

MAX_DEPTH = 15

class RelationshipCalculator(Relationship.RelationshipCalculator):


    REL_MOTHER           = 'm'      # going up to mother
    REL_FATHER           = 'f'      # going up to father
    REL_MOTHER_NOTBIRTH  = 'M'      # going up to mother, not birth relation
    REL_FATHER_NOTBIRTH  = 'F'      # going up to father, not birth relation
    REL_SIBLING          = 's'      # going sideways to sibling (no parents)
    REL_FAM_BIRTH        = 'a'      # going up to family (mother and father)
    REL_FAM_NONBIRTH     = 'A'      # going up to family, not birth relation
    REL_FAM_BIRTH_MOTH_ONLY = 'b'   # going up to fam, only birth rel to mother
    REL_FAM_BIRTH_FATH_ONLY = 'c'   # going up to fam, only birth rel to father
    
    REL_FAM_INLAW_PREFIX = 'L'      # going to the partner.

    def __init__(self):
        Relationship.RelationshipCalculator.__init__(self)

# de la personne active à l'ascendant commun Ga=[level] pour le calculateur de relations

    def get_cousin(self, level, removed):
        if (removed/level) == 1 and ((level*3)-3)/(level-1) == 3:
            return "le %s cousin" % (_level_name[level/2])
        elif (removed/level) == 1 and ((level*3)-3)/(level-1) == 2:
            return "le %s cousin" % (_level_name[(level+1)/2])
        elif (level) < (removed):
            return "le grand-oncle éloigné, relié à la %s génération" % (_level_name[level+3])
        else:
            return "le cousin éloigné, relié à la %s génération" % (_level_name[removed])

    def get_cousine(self, level, removed):
        if (removed/level) == 1 and ((level*3)-3)/(level-1) == 3:
            return "la %s cousine" % (_level_name[level/2])
        elif (removed/level) == 1 and ((level*3)-3)/(level-1) == 2:
            return "la %s cousine" % (_level_name[(level+1)/2])
        elif (level) < (removed):
            return "la grand-tante éloignée, reliée à la %s génération" % (_level_name[level+3])
        else:
            return "la cousine éloignée, reliée à la %s génération" % (_level_name[removed])

    def get_parents(self, level):
        if level > len(_parents_level)-1:
            return "les ascendants éloignés, à la %s génération" % (_level_name[level])
        else:
            return _parents_level[level]

    def get_father(self, level):
        if level > len(_father_level)-1:
            return "l'ascendant éloigné, à la %s génération" % (_level_name[level])
        else:
            return _father_level[level]

    def get_son(self, level):
        if level > len(_son_level)-1:
            return "le descendant éloigné, à la %s génération" % (_level_name[level+1])
        else:
            return _son_level[level]

    def get_mother(self, level):
        if level > len(_mother_level)-1:
            return "l'ascendante éloignée, à la %s génération" % (_level_name[level])
        else:
            return _mother_level[level]

    def get_daughter(self, level):
        if level > len(_daughter_level)-1:
            return "la descendante éloignée, à la %s génération" % (_level_name[level+1])
        else:
            return _daughter_level[level]

    def get_aunt(self, level):
        if level > len(_sister_level)-1:
            return "la tante éloignée, reliée à la %s génération" % (_level_name[level])
        else:
            return _sister_level[level]

    def get_uncle(self, level):
        if level > len(_brother_level)-1:
            return "l'oncle éloigné, relié à la %s génération" % (_level_name[level])
        else:
            return _brother_level[level]

    def get_nephew(self, level):
        if level > len(_nephew_level)-1:
            return "le neveu éloigné, relié à la %s génération" % (_level_name[level+1])
        else:
            return _nephew_level[level]

    def get_niece(self, level):
        if level > len(_niece_level)-1:
            return "la nièce éloignée, reliée à la %s génération" % (_level_name[level+1])
        else:
            return _niece_level[level]


# kinship report

    def get_plural_relationship_string(self, Ga, Gb):
        """
        voir Relationship.py
        """
        rel_str = "des parents éloignés"
        if Ga == 0:
            # These are descendants
            if Gb < len(_children_level):
                rel_str = _children_level[Gb]
            else:
                rel_str = "les descendants à la %sème génération" % (Gb+1)
        elif Gb == 0:
            # These are parents/grand parents
            if Ga < len(_parents_level):
                rel_str = _parents_level[Ga]
            else:
                rel_str = "les ascendants à la %sème génération" % (Ga+1) 
        elif Gb == 1:
            # These are siblings/aunts/uncles
            if Ga < len(_siblings_level):
                rel_str = _siblings_level[Ga]
            else:
                rel_str = "Les enfants d'un ascendant à la %sème génération (frères et soeurs d'un ascendant à la %sème génération)" % (Ga+1, Ga)
        elif Ga == 1:
            # These are nieces/nephews
            if Gb < len(_nephews_nieces_level):
                rel_str = _nephews_nieces_level[Gb]
            else:
                rel_str = "les neveux et les nièces à la %sème génération" % (Gb)
        elif Ga > 1 and Ga == Gb:
            # These are cousins in the same generation
            # use custom level for latin words
            if Ga == 2:
                rel_str = "les cousins germains et cousines germaines" 
            elif ((Ga*3)-3)/(Ga-1) == 2:
                rel_str = "le %s cousin et cousine" % (_removed_level[(Gb-1)/2])
            elif ((Ga*3)-3)/(Ga-1) != 2:
                rel_str = "le %s cousin et cousine" % (_removed_level[Gb/2])
            # security    
            else:
                rel_str = "les cousins et cousines"
        elif Ga > 1 and Ga > Gb:
            # These are cousins in different generations with the second person 
            # being in a higher generation from the common ancestor than the 
            # first person.
            # use custom level for latin words and specific relation
            if Ga == 3 and Gb == 2:
                rel_str = "les oncles et tantes à la mode de Bretagne (cousins germains d'un parent)" 
            elif Gb <= len(_level_name) and (Ga-Gb) < len(_removed_level) and (Ga+Gb) < len(_removed_level):
                rel_str = "les oncles et tantes du %s au %s degré (canon) et au %s degré (civil)" % (_removed_level[Gb], _removed_level[Ga], _removed_level[Ga+Gb] )
            elif Ga < len(_level_name):
                rel_str = "les grands-oncles et grands-tantes par la %sème génération" % (Ga)
            else:
                return rel_str
        elif Gb > 1 and Gb > Ga:
            # These are cousins in different generations with the second person 
            # being in a lower generation from the common ancestor than the 
            # first person.
            # use custom level for latin words and specific relation
            if Ga == 2 and Gb == 3:
                rel_str = "les neveux et nièces à la mode de Bretagne (cousins issus d'un germain)"
            elif Ga <= len(_level_name) and (Gb-Ga) < len(_removed_level) and (Ga+Gb) < len(_removed_level):
                rel_str = "le cousin ou cousine du %s au %s degré (canon) et au %s degré (civil)" % (_removed_level[Ga], _removed_level[Gb], _removed_level[Ga+Gb] )
            elif Ga < len(_level_name):
                rel_str =  "les cousins et cousines par la %sème génération" % (Ga)
            else:
                return rel_str
        return rel_str

# quick report /RelCalc tool

    def get_single_relationship_string(self, Ga, Gb, gender_a, gender_b,
                                       reltocommon_a, reltocommon_b,
                                       only_birth=True, 
                                       in_law_a=False, in_law_b=False):
        """
       voir Relationship.py
        """
       ## print 'Ga, Gb :', Ga, Gb

        if only_birth:
            step = 'germain'
        elif REL_FAM_BIRTH_MOTH_ONLY:
            step = 'utérin'
        elif REL_FAM_BIRTH_FATH_ONLY:
            step = 'consanguin'
        else:
            step = ''

        if in_law_a and gender_a == gen.lib.Person.MALE :
            inlaw = 'beau-'
        elif in_law_a and gender_a == gen.lib.Person.FEMALE:
            inlaw = 'belle-'
        else:
            inlaw = ''

        rel_str = "un parent éloigné"
        if Ga == 0:
            # b is descendant of a
            if Gb == 0 :
                rel_str = 'le même individu'
            elif gender_b == gen.lib.Person.MALE and Gb < len(_son_level):
                rel_str = _son_level[Gb]
            elif gender_b == gen.lib.Person.FEMALE and Gb < len(_daughter_level):
                rel_str = _daughter_level[Gb]
            elif Gb < len(_level_name) and gender_b == gen.lib.Person.MALE:
                rel_str = "le descendant éloigné (%dème génération)" % (Gb+1)
            elif Gb < len(_level_name) and gender_b == gen.lib.Person.FEMALE:
                rel_str = "la descendante éloignée (%dème génération)" % (Gb+1)
            else:
                return rel_str
        elif Gb == 0:
            # b is parents/grand parent of a
            if gender_b == gen.lib.Person.MALE and Ga < len(_father_level):
                rel_str = _father_level[Ga]
            elif gender_b == gen.lib.Person.FEMALE and Ga < len(_mother_level):
                rel_str = _mother_level[Ga]
            elif Ga < len(_level_name) and gender_b == gen.lib.Person.MALE:
                rel_str = "l'ascendant éloigné (%dème génération)" % Ga
            elif Ga < len(_level_name) and gender_b == gen.lib.Person.FEMALE:
                rel_str = "l'ascendante éloignée (%dème génération)" % Ga
            else:
                return rel_str
        elif Gb == 1:
            # b is sibling/aunt/uncle of a
            if gender_b == gen.lib.Person.MALE and Ga < len(_brother_level):
                rel_str = _brother_level[Ga]
            elif gender_b == gen.lib.Person.FEMALE and Ga < len(_sister_level):
                rel_str = _sister_level[Ga]
            else:
                if gender_b == gen.lib.Person.MALE:
                    rel_str = "l'oncle éloigné (par la %dème génération)" % (Ga+1)
                elif gender_b == gen.lib.Person.FEMALE:
                    rel_str = "la tante éloignée (par la %dème génération)" % (Ga+1)
                else:
                    return rel_str
        elif Ga == 1:
            # b is niece/nephew of a
            if gender_b == gen.lib.Person.MALE and Gb < len(_nephew_level):
                rel_str = _nephew_level[Gb]
            elif gender_b == gen.lib.Person.FEMALE and Gb < len(_niece_level):
                rel_str = _niece_level[Gb]
            else:
                if gender_b == gen.lib.Person.MALE: 
                    rel_str = "le neveu éloigné (par la %dème génération)" % (Gb+1)
                elif gender_b == gen.lib.Person.FEMALE:
                    rel_str = "la nièce éloignée (par la %dème génération)" % (Gb+1)
                else:
                    return rel_str   
        elif Ga > 1 and Ga == Gb:
            # a and b cousins in the same generation
            if ((Ga*3)-3)/(Ga-1) == 2 and gender_b == gen.lib.Person.MALE:
                rel_str = "le %s cousin" % (_removed_level[(Gb-1)/2])
            elif ((Ga*3)-3)/(Ga-1) != 2 and gender_b == gen.lib.Person.MALE:
                rel_str = "le %s cousin" % (_removed_level[Gb/2])
            elif ((Ga*3)-3)/(Ga-1) == 2 and gender_b == gen.lib.Person.FEMALE:
                rel_str = "la %s cousine" % (_removed_level[(Gb-1)/2])
            elif ((Ga*3)-3)/(Ga-1) != 2 and gender_b == gen.lib.Person.FEMALE:
                rel_str = "la %s cousine" % (_removed_level[Gb/2])
            else:
                if gender_b == gen.lib.Person.MALE:
                    rel_str = "le cousin éloigné"
                elif gender_b == gen.lib.Person.FEMALE:
                    rel_str = "la cousine éloignée"
                else:
                    return rel_str
        elif Ga > 1 and Ga > Gb:
            # These are cousins in different generations with the second person 
            # being in a higher generation from the common ancestor than the 
            # first person.
            if Ga == 3 and Gb == 2:
                if gender_b == gen.lib.Person.MALE:
                    rel_str = "l'oncle à la mode de Bretagne (cousin germain d'un parent)"
                elif gender_b == gen.lib.Person.FEMALE: 
                    rel_str = "la tante à la mode de Bretagne (cousin germain d'un parent)"
                else:
                    return rel_str
            elif Gb <= len(_level_name) and (Ga-Gb) < len(_removed_level) and (Ga+Gb) < len(_removed_level):
                if gender_b == gen.lib.Person.MALE:
                    rel_str = "l'oncle du %s au %s degré (canon) et au %s degré (civil)" % (_removed_level[Gb], _removed_level[Ga], _removed_level[Ga+Gb] )
                elif gender_b == gen.lib.Person.FEMALE:
                    rel_str = "la tante du %s au %s degré (canon) et au %s degré (civil)" % (_removed_level[Gb], _removed_level[Ga], _removed_level[Ga+Gb] )
                else:
                    return rel_str
            else:
                if gender_b == gen.lib.Person.MALE:   
                    rel_str = "le grand-oncle par la %sème génération" % (Ga+1)
                elif gender_b == gen.lib.Person.FEMALE:
                    rel_str = "la grand-tante par la %sème génération" % (Ga+1)
                else:
                    return rel_str 
        elif Gb > 1 and Gb > Ga:
            # These are cousins in different generations with the second person 
            # being in a lower generation from the common ancestor than the 
            # first person.
            if Ga == 2 and Gb == 3:
                if gender_b == gen.lib.Person.MALE:   
                    rel_str = "le neveu à la mode de Bretagne (cousin issu d'un germain)"
                elif gender_b == gen.lib.Person.FEMALE:
                    rel_str = "la nièce à la mode de Bretagne (cousine issue d'un germain)"
                else:
                    return rel_str
            elif Ga <= len(_level_name) and (Gb-Ga) < len(_removed_level) and (Ga+Gb) < len(_removed_level):
                if gender_b == gen.lib.Person.MALE:
                    rel_str = "le cousin du %s au %s degré (canon) et au %s degré (civil)" % (_removed_level[Ga], _removed_level[Gb], _removed_level[Ga+Gb] )
                if gender_b == gen.lib.Person.FEMALE:
                    rel_str = "la cousine du %s au %s degré (canon) et au %s degré (civil)" % (_removed_level[Ga], _removed_level[Gb], _removed_level[Ga+Gb] )
                else:
                    return rel_str
            elif Ga > len(_level_name):
                return rel_str
            else:
                if gender_b == gen.lib.Person.MALE:
                    rel_str = "le cousin par la %sème génération" % (Ga+1)
                elif gender_b ==gen.lib.Person.FEMALE:
                    rel_str = "la cousine par la %sème génération" % (Ga+1)
                else:
                    return rel_str 
        return rel_str

#-------------------------------------------------------------------------
#
# Register this class with the Plugins system 
#
#-------------------------------------------------------------------------
register_relcalc(RelationshipCalculator,
    ["fr", "FR", "fr_FR", "fr_CA", "francais", "Francais", "fr_FR.UTF8", "fr_FR@euro", "fr_FR.UTF8@euro",
            "french","French", "fr_FR.UTF-8", "fr_FR.utf-8", "fr_FR.utf8", "fr_CA.UTF-8"])

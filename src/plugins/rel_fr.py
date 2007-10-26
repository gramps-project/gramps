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

_level_name = [ "première", "deuxième", "troisième", "quatrième", "cinquième", "sixième", "septième", "huitième", "neuvième", "dixième", "onzième", "douzième", "treizième", "quatorzième", "quinzième", "seizième", "dix-septième", "dix-huitième", "dix-neuvième", "vingtième", "vingt-et-unième", "vingt-deuxième", "vingt-deuxième", "vingt-troisième","vingt-quatrième","vingt-sixième","vingt-septième", "vingt-huitième","vingt-neuvième","trentième", ]

# pour le degrè (canon et civil), limitation 20+20 ainsi que pour LE [premier] cousin 

_removed_level = [ "premier", "deuxième", "troisième", "quatrième", "cinquième", "sixième", "septième", "huitième", "neuvième", "dixième", "onzième", "douzième", "treizième", "quatorzième", "quinzième", "seizième", "dix-septième", "dix-huitième", "dix-neuvième", "vingtième", "vingt-et-unième", "vingt-deuxième", "vingt-deuxième", "vingt-troisième","vingt-quatrième","vingt-sixième","vingt-septième", "vingt-huitième","vingt-neuvième","trentième", "trente-et-unième", "trente-deuxième", "trente-troisième", "trente-quatrième", "trente-cinquième", "trente-sixième", "trente-septième", "trente-huitième", "trente-neuvième", "quarantième", "quanrante-et-unième", ]

# listes volontairement limitées | small lists, use generation level if > [4]

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


    def get_relationship(self, db, orig_person, other_person):
        """
        Returns a string representing the relationshp between the two people,
        along with a list of common ancestors (typically father,mother) 
        
        Special cases: relation strings "", "undefined" and "spouse".
        """

        if orig_person == None:
            return (_("undefined"), [])

        if orig_person.get_handle() == other_person.get_handle():
            return ('', [])

        is_spouse = self.is_spouse(db, orig_person, other_person)

        (secondRel, firstRel, common) = \
                self.get_relationship_distance(db, orig_person, other_person)
        
        if type(common) == types.StringType or \
           type(common) == types.UnicodeType:
            if is_spouse:
                return (is_spouse, [])
            else:
                return (common, [])
        elif common:
            person_handle = common[0]
        else:
            if is_spouse:
                return (is_spouse, [])
            else:
                return ("", [])

        #distance from common ancestor to the people
        dist_orig = len(firstRel)
        dist_other = len(secondRel)
        rel_str = self.get_single_relationship_string(dist_orig,
                                                      dist_other,
                                                    orig_person.get_gender(),
                                                    other_person.get_gender(),
                                                    firstRel, secondRel
                                                    )
        if is_spouse:
            return (_('%(spouse_relation)s et %(other_relation)s') % {
                        'spouse_relation': is_spouse, 
                        'other_relation': rel_str} , common )

        if dist_orig == 0:
            if dist_other == 0:
                return ('', common)
            elif other_person.get_gender() == gen.lib.Person.MALE:
                return (self.get_father(dist_other), common)
            else:
                return (self.get_mother(dist_other), common)
        elif dist_other == 0:
            if other_person.get_gender() == gen.lib.Person.MALE:
                return (self.get_son(dist_orig), common)
            else:
                return (self.get_daughter(dist_orig), common)
        elif dist_orig == 1:
            if other_person.get_gender() == gen.lib.Person.MALE:
                return (self.get_uncle(dist_other), common)
            else:
                return (self.get_aunt(dist_other), common)
        elif dist_other == 1:
            if other_person.get_gender() == gen.lib.Person.MALE:
                return (self.get_nephew(dist_orig-1), common)
            else:
                return (self.get_niece(dist_orig-1), common)
        elif dist_orig == 2 and dist_other == 2:
            if other_person.get_gender() == gen.lib.Person.MALE:
                return ('le cousin germain', common)
            else:
                return ('la cousine germaine', common)
        elif dist_orig == 3 and dist_other == 2:
            if other_person.get_gender() == gen.lib.Person.MALE:
                return ('le neveu à la mode de Bretagne', common)
            else:
                return ('la nièce à la mode de Bretagne', common)
        elif dist_orig == 2 and dist_other == 3:
            if other_person.get_gender() == gen.lib.Person.MALE:
                return ('l\'oncle à la mode de Bretagne', common)
            else:
                return ('la tante à la mode de Bretagne', common)     
        else:
            if other_person.get_gender() == gen.lib.Person.MALE:
                return (self.get_cousin(dist_orig, dist_other), common)
            else:
                return (self.get_cousine(dist_orig, dist_other), common)

# kinship report

    def get_plural_relationship_string(self, Ga, Gb):
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

# quick report

    def get_single_relationship_string(self, Ga, Gb, gender_a, gender_b,
                                       reltocommon_a, reltocommon_b,
                                       only_birth=True, 
                                       in_law_a=False, in_law_b=False):
        """
        Provides a string that describes the relationsip between a person, and
        another person. E.g. "grandparent" or "child".
        To be used as: 'person a is the grandparent of b', this will 
            be in translation string :
                            'person a is the %(relation)s of b'
            Note that languages with gender should add 'the' inside the 
            translation, so eg in french:
                            'person a est %(relation)s de b'
            where relation will be here: le grandparent
        
        Ga and Gb can be used to mathematically calculate the relationship.
        See the Wikipedia entry for more information:
            http://en.wikipedia.org/wiki/Cousin#Mathematical_definitions
        
        Some languages need to know the specific path to the common ancestor.
        Those languages should use reltocommon_a and reltocommon_b which is 
        a string like 'mfmf'. The possible string codes are:
            REL_MOTHER             # going up to mother
            REL_FATHER             # going up to father
            REL_MOTHER_NOTBIRTH    # going up to mother, not birth relation
            REL_FATHER_NOTBIRTH    # going up to father, not birth relation
            REL_SIBLING            # going sideways to sibling (no parents)
            REL_FAM_BIRTH          # going up to family (mother and father)
            REL_FAM_NONBIRTH       # going up to family, not birth relation
            REL_FAM_BIRTH_MOTH_ONLY # going up to fam, only birth rel to mother
            REL_FAM_BIRTH_FATH_ONLY # going up to fam, only birth rel to father
        Prefix codes are stripped, so REL_FAM_INLAW_PREFIX is not present. 
        If the relation starts with the inlaw of the person a, then 'in_law_a'
        is True, if it starts with the inlaw of person b, then 'in_law_b' is
        True.
        Note that only_birth=False, means that in the reltocommon one of the
        NOTBIRTH specifiers is present.
        The REL_FAM identifiers mean that the relation is not via a common 
        ancestor, but via a common family (note that that is not possible for 
        direct descendants or direct ancestors!). If the relation to one of the
        parents in that common family is by birth, then 'only_birth' is not
        set to False.
            
        @param Ga: The number of generations between the main person and the 
                   common ancestor.
        @type Ga: int
        @param Gb: The number of generations between the other person and the
                   common ancestor
        @type Gb: int
        @param gender_a : gender of person a
        @type gender_a: int gender
        @param gender_b : gender of person b
        @type gender_b: int gender
        @param reltocommon_a : relation path to common ancestor or common
                            Family for person a. 
                            Note that length = Ga
        @type reltocommon_a: str 
        @param reltocommon_b : relation path to common ancestor or common
                            Family for person b. 
                            Note that length = Gb
        @type reltocommon_b: str 
        @param in_law_a : True if path to common ancestors is via the partner
                          of person a
        @type in_law_a: bool
        @param in_law_b : True if path to common ancestors is via the partner
                          of person b
        @type in_law_b: bool
        @param only_birth : True if relation between a and b is by birth only
                            False otherwise
        @type only_birth: bool
        @returns: A string describing the relationship between the two people
        @rtype: str
        """
        print 'Ga, Gb :', Ga, Gb
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
                rel_str = "le descendant éloigné (%dème génération)" % Gb
            elif Gb < len(_level_name) and gender_b == gen.lib.Person.FEMALE:
                rel_str = "la descendante éloignée (%dème génération)" % Gb
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
                    rel_str = "l'oncle éloigné (par la %dème génération)" % Ga
                elif gender_b == gen.lib.Person.FEMALE:
                    rel_str = "la tante éloignée (par la %dème génération)" % Ga
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
                    rel_str = "le neveu éloigné (par la %dème génération)" % Gb
                elif gender_b == gen.lib.Person.FEMALE:
                    rel_str = "la nièce éloignée (par la %dème génération)" % Gb
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
                    rel_str = "le grand-oncle par la %sème génération" % (Ga)
                elif gender_b == gen.lib.Person.FEMALE:
                    rel_str = "la grand-tante par la %sème génération" % (Ga)
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
                    rel_str = "le cousin par la %sème génération" % (Ga)
                elif gender_b ==gen.lib.Person.FEMALE:
                    rel_str = "la cousine par la %sème génération" % (Ga)
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

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
#
#
#-------------------------------------------------------------------------

# level est utilisé pour trouver/afficher le niveau de la génération : à la %sème génération

_level_name = [ "première", "deuxième", "troisième", "quatrième", "cinquième", "sixième", "septième", "huitième", "neuvième", "dixième", "onzième", "douzième", "treizième", "quatorzième", "quinzième", "seizième", "dix-septième", "dix-huitième", "dix-neuvième", "vingtième", "vingt-et-unième", "vingt-deuxième", "vingt-deuxième", "vingt-troisième","vingt-quatrième","vingt-sixième","vingt-septième", "vingt-huitième","vingt-neuvième","trentième", ]

# pour le degrè (canon et civil) ainsi que pour LE [premier] cousin 

_removed_level = [ "premier", "deuxième", "troisième", "quatrième", "cinquième", "sixième", "septième", "huitième", "neuvième", "dixième", "onzième", "douzième", "treizième", "quatorzième", "quinzième", "seizième", "dix-septième", "dix-huitième", "dix-neuvième", "vingtième", "vingt-et-unième", "vingt-deuxième", "vingt-deuxième", "vingt-troisième","vingt-quatrième","vingt-sixième","vingt-septième", "vingt-huitième","vingt-neuvième","trentième", ]

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
class RelationshipCalculator(Relationship.RelationshipCalculator):

    def __init__(self):
        Relationship.RelationshipCalculator.__init__(self)

# génération de la personne active à l'ancêtre commun Ga=[level] pour le calculateur de relations
    

    def get_cousin(self,level,removed):
        if removed > len(_removed_level)-1 or level>len(_level_name)-1:
# _level_name[removed] pour avoir un adjectif au masculin ...
# not certain we need this on rel_fr
            return "le %s cousin au %s degré" % (_level_name[removed],_removed_level[removed])
        else:
# TODO working with junior cousin [Gb] > 4
            return "le cousin éloigné, à la %s génération" % (_level_name[level])

    def get_cousine(self,level,removed):
        if removed > len(_removed_level)-1 or level>len(_level_name)-1:
# not certain we need this on rel_fr
            return "la %s cousine au %s degré" % (_level_name[level],_removed_level[removed])
        else:
# TODO working with junior cousine [Gb] > 4
            return "la cousine éloignée, à la %s génération" % (_level_name[level])

    def get_parents(self,level):
        if level>len(_parents_level)-1:
            return "les ancêtres éloignés, à la %s génération" % (_level_name[level])
        else:
            return _parents_level[level]

    def get_father(self,level):
        if level>len(_father_level)-1:
            return "l'ancêtre éloigné, à la %s génération" % (_level_name[level])
        else:
            return _father_level[level]

    def get_son(self,level):
        if level>len(_son_level)-1:
            return "le descendant éloigné, à la %s génération" % (_level_name[level])
        else:
            return _son_level[level]

    def get_mother(self,level):
        if level>len(_mother_level)-1:
            return "l'ancêtre éloignée, à la %s génération" % (_level_name[level])
        else:
            return _mother_level[level]

    def get_daughter(self,level):
        if level>len(_daughter_level)-1:
            return "la descendante éloignée, à la %s génération" % (_level_name[level])
        else:
            return _daughter_level[level]

    def get_aunt(self,level):
        if level>len(_sister_level)-1:
            return "la tante éloignée, à la %s génération" % (_level_name[level+1])
        else:
            return _sister_level[level]

    def get_uncle(self,level):
        if level>len(_brother_level)-1:
            return "l'oncle éloigné, à la %s génération" % (_level_name[level+1])
        else:
            return _brother_level[level]

    def get_nephew(self,level):
        if level>len(_nephew_level)-1:
            return "le neveu éloigné, à la %s génération" % (_level_name[level+1])
        else:
            return _nephew_level[level]

    def get_niece(self,level):
        if level>len(_niece_level)-1:
            return "la nièce éloignée, à la %s génération" % (_level_name[level+1])
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
                        return _("le mari")
                    elif gender == RelLib.Person.FEMALE:
                        return _("la femme")
                    else:
                        return _("le conjoint")
                elif family_rel == RelLib.FamilyRelType.UNMARRIED:
                    if gender == RelLib.Person.MALE:
                        return _("le conjoint")
                    elif gender == RelLib.Person.FEMALE:
                        return _("la conjointe")
                    else:
                        return _("le conjoint")
                elif family_rel == RelLib.FamilyRelType.CIVIL_UNION:
                    if gender == RelLib.Person.MALE:
                        return _("le conjoint")
                    elif gender == RelLib.Person.FEMALE:
                        return _("la conjointe")
                    else:
                        return _("le conjoint")
                else:
                    if gender == RelLib.Person.MALE:
                        return _("le conjoint")
                    elif gender == RelLib.Person.FEMALE:
                        return _("la conjointe")
                    else:
                        return _("le conjoint")
            else:
                return None
        return None

    def get_relationship(self,db,orig_person,other_person):
        """
        Returns a string representing the relationshp between the two people,
        along with a list of common ancestors (typically father,mother) 
        
        Special cases: relation strings "", "undefined" and "spouse".
        """

        if orig_person == None:
            return ("non défini",[])

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
        elif firstRel == 2 and secondRel == 2:
            if other_person.get_gender() == RelLib.Person.MALE:
                return ('le cousin germain',common)
            else:
                return ('la cousine germaine',common)
        elif firstRel == 3 and secondRel == 2:
            if other_person.get_gender() == RelLib.Person.MALE:
                return ('le neveu à la mode de Bretagne',common)
            else:
                return ('la nièce à la mode de Bretagne',common)
        elif firstRel == 2 and secondRel == 3:
            if other_person.get_gender() == RelLib.Person.MALE:
                return ('l\'oncle à la mode de Bretagne',common)
            else:
                return ('la tante à la mode de Bretagne',common)
        else:
            if other_person.get_gender() == RelLib.Person.MALE:
                return (self.get_cousin(firstRel,secondRel),common)
            else:
                return (self.get_cousine(firstRel,secondRel),common)

    def get_grandparents_string(self,db,orig_person,other_person):
        """
        returns a string representing the relationshp between the two people,
        along with a list of common ancestors (typically father,mother) 
        """
        if orig_person == None:
            return ("non défini",[])

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

# kinship report

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
        rel_str = "un parent éloigné"
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
                rel_str = "les ancêtres à la %sème génération" % (Ga+1) 
        elif Gb == 1:
            # These are siblings/aunts/uncles
            if Ga < len(_siblings_level):
                rel_str = _siblings_level[Ga]
            else:
                rel_str = "les oncles et les tantes à la %sème génération" % (Ga+Gb)
        elif Ga == 1:
            # These are nieces/nephews
            if Gb < len(_nephews_nieces_level):
                rel_str = _nephews_nieces_level[Gb]
            else:
                rel_str = "les neveux et les nièces à la %sème génération" % (Gb)
        elif Ga > 1 and Ga == Gb:
            # These are cousins in the same generation
            # use custom level for latin words
            if Ga <= len(_level_name):
                rel_str = "le %s cousin et cousine" % _removed_level[Ga-2]
            else:
                rel_str = "les cousins et cousines"
        elif Ga > 1 and Ga > Gb:
            # These are cousins in different generations with the second person 
            # being in a higher generation from the common ancestor than the 
            # first person.
            # use custom level for latin words
            if Gb <= len(_level_name) and (Ga-Gb) < len(_removed_level):
                rel_str = "le %s parent au %s degré (canon) et %s degré (civil)" % ( _removed_level[Gb], 
                                                  _removed_level[Ga], _removed_level[Ga+Gb] )
            else:
                rel_str =  "les parents par la %sème génération" % (Ga)
        elif Gb > 1 and Gb > Ga:
            # These are cousins in different generations with the second person 
            # being in a lower generation from the common ancestor than the 
            # first person.
            # use custom level for latin words
            if Ga <= len(_level_name) and (Gb-Ga) < len(_removed_level):
                rel_str = "le %s cousin ou cousine au %s degré (canon) et %s degré (civil)" % ( _removed_level[Ga], 
                                                    _removed_level[Gb], _removed_level[Ga+Gb] )
            else:
                rel_str =  "les cousins et cousines par la %sème génération" % (Ga)
        return rel_str

#-------------------------------------------------------------------------
#
# Register this class with the Plugins system 
#
#-------------------------------------------------------------------------
register_relcalc(RelationshipCalculator,
    ["fr", "FR", "fr_FR", "fr_CA", "francais", "Francais", "fr_FR.UTF8", "fr_FR@euro", "fr_FR.UTF8@euro",
            "french","French", "fr_FR.UTF-8", "fr_FR.utf-8", "fr_FR.utf8", "fr_CA.UTF-8"])

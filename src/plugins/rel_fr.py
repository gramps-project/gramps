# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2007  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
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
from PluginUtils import PluginManager

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------

# level est utilisé pour trouver/afficher le niveau de la génération : 
# à la %sème génération

_level_name = [ "première", "deuxième", "troisième", "quatrième", 
                "cinquième", "sixième", "septième", "huitième", 
                "neuvième", "dixième", "onzième", "douzième", 
                "treizième", "quatorzième", "quinzième", 
                "seizième", "dix-septième", "dix-huitième",
                "dix-neuvième", "vingtième", "vingt-et-unième",
                "vingt-deuxième", "vingt-troisième", 
                "vingt-quatrième", "vingt-cinquième",
                "vingt-sixième", "vingt-septième", 
                "vingt-huitième", "vingt-neuvième",
                "trentième", ]

# pour le degrè (canon et civil), limitation 20+20 ainsi que pour 
# LE [premier] cousin 

_removed_level = [ "premier", "deuxième", "troisième", "quatrième", 
                   "cinquième", "sixième", "septième", "huitième", 
                   "neuvième", "dixième", "onzième", "douzième", 
                   "treizième", "quatorzième", "quinzième", 
                   "seizième", "dix-septième", "dix-huitième",
                   "dix-neuvième", "vingtième", "vingt-et-unième",
                   "vingt-deuxième", "vingt-troisième", 
                   "vingt-quatrième", "vingt-cinquième",
                   "vingt-sixième", "vingt-septième", 
                   "vingt-huitième", "vingt-neuvième",
                   "trentième", "trente-et-unième", 
                   "trente-deuxième", "trente-troisième", 
                   "trente-quatrième", "trente-cinquième", 
                   "trente-sixième", "trente-septième", 
                   "trente-huitième", "trente-neuvième", 
                   "quarantième", "quanrante-et-unième", ]

# listes volontairement limitées | small lists, use generation level if > [5]

_father_level = [ "", "le père%s", "le grand-père%s", 
                  "l'arrière-grand-père%s", "le trisaïeul%s", ]

_mother_level = [ "", "la mère%s", "la grand-mère%s", 
                  "l'arrière-grand-mère%s", "la trisaïeule%s", ]

_son_level = [ "", "le fils%s", "le petit-fils%s", "l'arrière-petit-fils%s", ]

_daughter_level = [ "", "la fille%s", "la petite-fille%s", 
                    "l'arrière-petite-fille%s", ]

_sister_level = [ "", "la sœur%s", "la tante%s", "la grand-tante%s", 
                    "l'arrière-grand-tante%s", ]

_brother_level = [ "", "le frère%s", "l'oncle%s", "le grand-oncle%s", 
                    "l'arrière-grand-oncle%s", ]

_nephew_level = [ "", "le neveu%s", "le petit-neveu%s", 
                  "l'arrière-petit-neveu%s", ]

_niece_level = [ "", "la nièce%s", "la petite-nièce%s", 
                 "l'arrière-petite-nièce%s", ]

# kinship report

_parents_level = [ "", "les parents", "les grands-parents", 
                    "les arrières-grands-parents", "les trisaïeux", ]

_children_level = [ "", "les enfants", "les petits-enfants", 
                    "les arrières-petits-enfants", 
                    "les arrières-arrières-petits-enfants", ]

_siblings_level = [ "", "les frères et les sœurs", 
                    "les oncles et les tantes", 
                    "les grands-oncles et les grands-tantes", 
                    "les arrières-grands-oncles et les arrières-grands-tantes", 
                    ]

_nephews_nieces_level = [ "", "les neveux et les nièces", 
                          "les petits-neveux et les petites-nièces", 
                          "les arrière-petits-neveux et les arrières-petites-nièces",
                        ]

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------

class RelationshipCalculator(Relationship.RelationshipCalculator):
   
    INLAW = ' (par alliance)'


    def __init__(self):
        Relationship.RelationshipCalculator.__init__(self)

# de la personne active à l'ascendant commun Ga=[level] pour 
# le calculateur de relations

    def get_cousin(self, level, removed, dir = '', inlaw=''):
        if removed == 0 and level < len(_level_name):
            return "le %s cousin%s" % (_removed_level[level-1],
                                        inlaw)
        elif (level) < (removed):
            rel_str = self.get_uncle(level-1, inlaw)
        else:
            # limitation gen = 29
            return "le cousin lointain, relié à la %s génération" % (
                        _level_name[removed])

    def get_cousine(self, level, removed, dir = '', inlaw=''):
        if removed == 0 and level < len(_level_name):
            return "la %s cousine%s" % (_level_name[level-1],
                                        inlaw)
        elif (level) < (removed):
            rel_str = self.get_aunt(level-1, inlaw)
        else:
            return "la cousine lointaine, reliée à la %s génération" % (
                        _level_name[removed])

    def get_parents(self, level):
        if level > len(_parents_level)-1:
            return "les ascendants lointains, à la %s génération" % (
                        _level_name[level])
        else:
            return _parents_level[level]

    def get_father(self, level, inlaw=''):
        if level > len(_father_level)-1:
            return "l'ascendant lointain, à la %s génération" % (
                        _level_name[level])
        else:
            return _father_level[level] % inlaw

    def get_mother(self, level, inlaw=''):
        if level > len(_mother_level)-1:
            return "l'ascendante lointaine, à la %s génération" % (
                        _level_name[level])
        else:
            return _mother_level[level] % inlaw

    def get_parent_unknown(self, level, inlaw=''):
        if level > len(_level_name)-1:
            return "l'ascendant lointain, à la %s génération" % (
                        _level_name[level])
        else:
            return "un parent lointain%s" % (inlaw)

    def get_son(self, level, inlaw=''):
        if level > len(_son_level)-1:
            return "le descendant lointain, à la %s génération" % (
                        _level_name[level+1])
        else:
            return _son_level[level] % (inlaw)

    def get_daughter(self, level, inlaw=''):
        if level > len(_daughter_level)-1:
            return "la descendante lointaine, à la %s génération" % (
                        _level_name[level+1])
        else:
            return _daughter_level[level] % (inlaw)

    def get_child_unknown(self, level, inlaw=''):
        if level > len(_level_name)-1:
            return "le descendant lointain, à la %s génération" % (
                        _level_name[level+1])
        else:
            return "un descendant lointain%s" % (inlaw)

    def get_sibling_unknown(self, level, inlaw=''):
        return "un parent lointain%s" % (inlaw)

    def get_uncle(self, level, inlaw=''):
        if level > len(_brother_level)-1:
            return "l'oncle lointain, relié à la %s génération" % (
                        _level_name[level])
        else:
            return _brother_level[level] % (inlaw)

    def get_aunt(self, level, inlaw=''):
        if level > len(_sister_level)-1:
            return "la tante lointaine, reliée à la %s génération" % (
                        _level_name[level])
        else:
            return _sister_level[level] % (inlaw)

    def get_nephew(self, level, inlaw=''):
        if level > len(_nephew_level)-1:
            return "le neveu lointain, à la %s génération" % (
                        _level_name[level])
        else:
            return _nephew_level[level] % (inlaw)

    def get_niece(self, level, inlaw=''):
        if level > len(_niece_level)-1:
            return "la nièce lointaine, à la %s génération" % (
                        _level_name[level])
        else:
            return _niece_level[level] % (inlaw)


# kinship report

    def get_plural_relationship_string(self, Ga, Gb):
        """
        voir Relationship.py
        """
        rel_str = "des parents lointains"
        gen = " à la %sème génération"
        bygen = " par la %sème génération"
        cmt = " (frères ou sœurs d'un ascendant" + gen % (
                       Ga) + ")"
        if Ga == 0:
            # These are descendants
            if Gb < len(_children_level):
                rel_str = _children_level[Gb]
            else:
                rel_str = "les descendants" + gen % (
                               Gb+1)
        elif Gb == 0:
            # These are parents/grand parents
            if Ga < len(_parents_level):
                rel_str = _parents_level[Ga]
            else:
                rel_str = "les ascendants" + gen % (
                               Ga+1) 
        elif Gb == 1:
            # These are siblings/aunts/uncles
            if Ga < len(_siblings_level):
                rel_str = _siblings_level[Ga]
            else:
                rel_str = "Les enfants d'un ascendant" + gen % (
                               Ga+1) + cmt 
        elif Ga == 1:
            # These are nieces/nephews
            if Gb < len(_nephews_nieces_level):
                rel_str = _nephews_nieces_level[Gb-1]
            else:
                rel_str = "les neveux et les nièces" + gen % (
                               Gb)
        elif Ga > 1 and Ga == Gb:
            # These are cousins in the same generation
            # use custom level for latin words
            if Ga == 2:
                rel_str = "les cousins germains et cousines germaines" 
            elif Ga <= len(_level_name):
                # %ss for plural
                rel_str = "les %ss cousins et cousines" % _level_name[Ga-2]
            # security    
            else:
                rel_str = "les cousins et cousines"
        elif Ga > 1 and Ga > Gb:
            # These are cousins in different generations with the second person 
            # being in a higher generation from the common ancestor than the 
            # first person.
            # use custom level for latin words and specific relation
            if Ga == 3 and Gb == 2:
                desc = " (cousins germains d'un parent)"
                rel_str = "les oncles et tantes à la mode de Bretagne" + desc
            elif Gb <= len(_level_name) and (Ga-Gb) < len(_removed_level) and (Ga+Gb+1) < len(_removed_level):
                can = " du %s au %s degré (canon)"  % (
                           _removed_level[Gb], _removed_level[Ga] )
                civ = " et au %s degré (civil)" % ( _removed_level[Ga+Gb+1] )
                rel_str = "les oncles et tantes" + can + civ
            elif Ga < len(_level_name):
                rel_str = "les grands-oncles et grands-tantes" + bygen % (
                               Ga+1)
            else:
                return rel_str
        elif Gb > 1 and Gb > Ga:
            # These are cousins in different generations with the second person 
            # being in a lower generation from the common ancestor than the 
            # first person.
            # use custom level for latin words and specific relation
            if Ga == 2 and Gb == 3:
                info = " (cousins issus d'un germain)"
                rel_str = "les neveux et nièces à la mode de Bretagne" + info
            elif Ga <= len(_level_name) and (Gb-Ga) < len(_removed_level) and (Ga+Gb+1) < len(_removed_level):
                can = " du %s au %s degré (canon)"  % (
                           _removed_level[Gb], _removed_level[Ga] )
                civ = " et au %s degré (civil)" % ( _removed_level[Ga+Gb+1] )
                rel_str = "les neveux et nièces" + can + civ
            elif Ga < len(_level_name):
                rel_str =  "les neveux et nièces" + bygen % (
                                Gb)
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
        if only_birth:
            step = ''
        else:
            step = self.STEP

        if in_law_a or in_law_b :
            inlaw = self.INLAW
        else:
            inlaw = ''
        
        
        rel_str = "un parent lointains%s" % (inlaw)
        bygen = " par la %sème génération"
        if Ga == 0:
            # b is descendant of a
            if Gb == 0 :
                rel_str = 'le même individu'
            elif gender_b == gen.lib.Person.MALE and Gb < len(_son_level):
                if inlaw and Gb == 1 and not step:
                    rel_str = "le gendre"
                else:
                    rel_str = self.get_son(Gb)
            elif gender_b == gen.lib.Person.FEMALE and Gb < len(_daughter_level):
                if inlaw and Gb == 1 and not step:
                    rel_str = "la bru"
                else:
                    rel_str = self.get_daughter(Gb)
            # don't display inlaw
            elif Gb < len(_level_name) and gender_b == gen.lib.Person.MALE:
                rel_str = "le descendant lointain (%dème génération)" % (
                               Gb+1)
            elif Gb < len(_level_name) and gender_b == gen.lib.Person.FEMALE:
                rel_str = "la descendante lointaine (%dème génération)" % (
                               Gb+1)
            else:
                return self.get_child_unknown(Gb)
        elif Gb == 0:
            # b is parents/grand parent of a
            if gender_b == gen.lib.Person.MALE and Ga < len(_father_level):
                if inlaw and Ga == 1 and not step:
                    rel_str = "le père du conjoint"
                elif step and Ga == 1 and not inlaw:
                    rel_str = "le beau-père"
                else:
                    rel_str = self.get_father(Ga, inlaw)
            elif gender_b == gen.lib.Person.FEMALE and Ga < len(_mother_level):
                if inlaw and Ga == 1 and not step:
                    rel_str = "la mère du conjoint"
                elif step and Ga == 1 and not inlaw:
                    rel_str = "la belle-mère"
                else:
                    rel_str = self.get_mother(Ga, inlaw)
            elif Ga < len(_level_name) and gender_b == gen.lib.Person.MALE:
                rel_str = "l'ascendant lointain%s (%dème génération)" % (
                               inlaw, Ga+1)
            elif Ga < len(_level_name) and gender_b == gen.lib.Person.FEMALE:
                rel_str = "l'ascendante lointaine%s (%dème génération)" % (
                               inlaw, Ga+1)
            else:
                return self.get_parent_unknown(Ga, inlaw)
        elif Gb == 1:
            # b is sibling/aunt/uncle of a
            if gender_b == gen.lib.Person.MALE and Ga < len(_brother_level):
                rel_str = self.get_uncle(Ga, inlaw)
            elif gender_b == gen.lib.Person.FEMALE and Ga < len(_sister_level):
                rel_str = self.get_aunt(Ga, inlaw)
            else:
                # don't display inlaw
                if gender_b == gen.lib.Person.MALE:
                    rel_str = "l'oncle lointain" + bygen % (
                                   Ga+1)
                elif gender_b == gen.lib.Person.FEMALE:
                    rel_str = "la tante lointaine" + bygen % (
                                   Ga+1)
                elif gender_b == gen.lib.Person.UNKNOWN:
                    rel_str = self.get_sibling_unknown(Ga, inlaw)
                else:
                    return rel_str
        elif Ga == 1:
            # b is niece/nephew of a
            if gender_b == gen.lib.Person.MALE and Gb < len(_nephew_level):
                rel_str = self.get_nephew(Gb-1, inlaw)
            elif gender_b == gen.lib.Person.FEMALE and Gb < len(_niece_level):
                rel_str = self.get_niece(Gb-1, inlaw)
            else:
                if gender_b == gen.lib.Person.MALE: 
                    rel_str = "le neveu lointain%s (%dème génération)" %  (
                                   inlaw, Gb)
                elif gender_b == gen.lib.Person.FEMALE:
                    rel_str = "la nièce lointaine%s (%dème génération)" %  (
                                   inlaw, Gb)
                elif gender_b == gen.lib.Person.UNKNOWN:
                    rel_str = self.get_sibling_unknown(Ga, inlaw)
                else:
                    return rel_str
        elif Ga == Gb:
            # a and b cousins in the same generation
            if gender_b == gen.lib.Person.MALE:
                rel_str = self.get_cousin(Ga-1, 0, dir = '', 
                                     inlaw=inlaw)
            elif gender_b == gen.lib.Person.FEMALE:
                rel_str = self.get_cousine(Ga-1, 0, dir = '', 
                                     inlaw=inlaw)
            elif gender_b == gen.lib.Person.UNKNOWN:
                rel_str = self.get_sibling_unknown(Ga-1, inlaw)
            else:
                return rel_str
        elif Ga > 1 and Ga > Gb:
            # These are cousins in different generations with the second person 
            # being in a higher generation from the common ancestor than the 
            # first person.
            if Ga == 3 and Gb == 2:
                if gender_b == gen.lib.Person.MALE:
                    desc = " (cousin germain d'un parent)"
                    rel_str = "l'oncle à la mode de Bretagne" + desc
                elif gender_b == gen.lib.Person.FEMALE: 
                    desc = " (cousine germaine d'un parent)"
                    rel_str = "la tante à la mode de Bretagne" + desc
                elif gender_b == gen.lib.Person.UNKNOWN: 
                    return self.get_sibling_unknown(Ga, inlaw)
                else:
                    return rel_str
            elif Gb <= len(_level_name) and (Ga-Gb) < len(_removed_level) and (Ga+Gb+1) < len(_removed_level):
                can = " du %s au %s degré (canon)"  % (
                           _removed_level[Gb], _removed_level[Ga] )
                civ = " et au %s degré (civil)" % ( _removed_level[Ga+Gb+1] )
                if gender_b == gen.lib.Person.MALE:
                    rel_str = "l'oncle" + can + civ
                elif gender_b == gen.lib.Person.FEMALE:
                    rel_str = "la tante" + can + civ
                elif gender_b == gen.lib.Person.UNKNOWN:
                    rel_str = self.get_sibling_unknown(Ga, inlaw)
                else:
                    return rel_str
            else:
                if gender_b == gen.lib.Person.MALE:   
                    rel_str = self.get_uncle(Ga, inlaw)
                elif gender_b == gen.lib.Person.FEMALE:
                    rel_str = self.get_aunt(Ga, inlaw)
                elif gender_b == gen.lib.Person.UNKNOWN:
                    rel_str = self.get_sibling_unknown(Ga, inlaw)
                else:
                    return rel_str 
        elif Gb > 1 and Gb > Ga:
            # These are cousins in different generations with the second person 
            # being in a lower generation from the common ancestor than the 
            # first person.
            if Ga == 2 and Gb == 3:
                info = " (cousins issus d'un germain)"
                if gender_b == gen.lib.Person.MALE:   
                    rel_str = "le neveu à la mode de Bretagne" + info
                elif gender_b == gen.lib.Person.FEMALE:
                    rel_str = "la nièce à la mode de Bretagne" + info
                elif gender_b == gen.lib.Person.UNKNOWN:
                    rel_str = self.get_sibling_unknown(Ga, inlaw)
                else:
                    return rel_str  
            elif Ga <= len(_level_name) and (Gb-Ga) < len(_removed_level) and (Ga+Gb+1) < len(_removed_level):
                can = " du %s au %s degré (canon)"  % (
                           _removed_level[Gb], _removed_level[Ga] )
                civ = " et au %s degré (civil)" % ( _removed_level[Ga+Gb+1] )
                if gender_b == gen.lib.Person.MALE:
                    rel_str = "le neveu" + can + civ
                if gender_b == gen.lib.Person.FEMALE:
                    rel_str = "la nièce" + can + civ
                elif gender_b == gen.lib.Person.UNKNOWN:
                    rel_str = self.get_sibling_unknown(Ga, inlaw)
                else:
                    return rel_str
            elif Ga > len(_level_name):
                return rel_str
            else:
                if gender_b == gen.lib.Person.MALE:
                    rel_str = self.get_nephew(Ga, inlaw)
                elif gender_b ==gen.lib.Person.FEMALE:
                    rel_str = self.get_niece(Ga, inlaw)
                elif gender_b == gen.lib.Person.UNKNOWN:
                    rel_str = self.get_sibling_unknown(Ga, inlaw)
                else:
                    return rel_str
        return rel_str

    def get_sibling_relationship_string(self, sib_type, gender_a, gender_b, 
                                        in_law_a=False, in_law_b=False):

        if in_law_a or in_law_b :
            inlaw = self.INLAW
        else:
            inlaw = ''
        
        if sib_type == self.NORM_SIB:
            if not inlaw:
                if gender_b == gen.lib.Person.MALE:
                    rel_str = 'le frère (germain)'
                elif gender_b == gen.lib.Person.FEMALE:
                    rel_str = 'la sœur (germaine)'
                else:
                    rel_str = 'le frère ou la sœur (germain)'
            else:
                if gender_b == gen.lib.Person.MALE:
                    rel_str = "le beau-frère"
                elif gender_b == gen.lib.Person.FEMALE:
                    rel_str = "la belle-sœur"
                else:
                    rel_str = "le beau-frère ou la belle-sœur"
        elif sib_type == self.UNKNOWN_SIB:
            if not inlaw:
                if gender_b == gen.lib.Person.MALE:
                    rel_str = 'le frère'
                elif gender_b == gen.lib.Person.FEMALE:
                    rel_str = 'la sœur'
                else:
                    rel_str = 'le frère ou la sœur'
            else:
                if gender_b == gen.lib.Person.MALE:
                    rel_str = "le beau-frère"
                elif gender_b == gen.lib.Person.FEMALE:
                    rel_str = "la belle-sœur"
                else:
                    rel_str = "le beau-frère ou la belle-sœur"
        elif sib_type == self.HALF_SIB_FATHER:
                if gender_b == gen.lib.Person.MALE:
                    rel_str = "le demi-frère consanguin"
                elif gender_b == gen.lib.Person.FEMALE:
                    rel_str = "la demi-sœur consanguine"
                else:
                    rel_str = "le demi-frère ou la demi-sœur consanguin(e)"
        elif sib_type == self.HALF_SIB_MOTHER:
                if gender_b == gen.lib.Person.MALE:
                    rel_str = "le demi-frère utérin"
                elif gender_b == gen.lib.Person.FEMALE:
                    rel_str = "la demi-sœur utérine"
                else:
                    rel_str = "le demi-frère ou la demi-sœur utérin(e)"
        elif sib_type == self.STEP_SIB:
                if gender_b == gen.lib.Person.MALE:
                    rel_str = "le demi-frère"
                elif gender_b == gen.lib.Person.FEMALE:
                    rel_str = "la demi-sœur"
                else:
                    rel_str = "le demi-frère ou la demi-sœur"
        return rel_str


#-------------------------------------------------------------------------
#
# Register this class with the Plugins system 
#
#-------------------------------------------------------------------------

pmgr = PluginManager.get_instance()
pmgr.register_relcalc(RelationshipCalculator,
    ["fr", "FR", "fr_FR", "fr_CA", "francais", "Francais", "fr_FR.UTF8", 
            "fr_FR@euro", "fr_FR.UTF8@euro",
            "french","French", "fr_FR.UTF-8", "fr_FR.utf-8", "fr_FR.utf8", 
            "fr_CA.UTF-8"])

if __name__ == "__main__":
    # Test function. Call it as follows from the command line (so as to find
    #        imported modules):
    #    export PYTHONPATH=/path/to/gramps/src 
    # python src/plugins/rel_fr.py 
    # (Above not needed here)
    
    """TRANSLATORS, copy this if statement at the bottom of your 
        rel_xx.py module, and test your work with:
        python src/plugins/rel_xx.py
    """
    from Relationship import test
    rc = RelationshipCalculator()
    test(rc, True)

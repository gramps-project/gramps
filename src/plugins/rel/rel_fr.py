#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2007  Donald N. Allingham
# Copyright (C) 2008-2009  Brian G. Matherly
# Copyright (C) 2007-2009  Jerome Rapinat
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
"""
French-specific classes for relationships.
"""
#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------

import gen.lib
import Relationship
from gen.plug import PluginManager

#-------------------------------------------------------------------------

# level is used for generation level:
# at %th generation

_LEVEL_NAME = [
    "première",
    "deuxième",
    "troisième",
    "quatrième",
    "cinquième",
    "sixième",
    "septième",
    "huitième",
    "neuvième",
    "dixième",
    "onzième",
    "douzième",
    "treizième",
    "quatorzième",
    "quinzième",
    "seizième",
    "dix-septième",
    "dix-huitième",
    "dix-neuvième",
    "vingtième",
    "vingt-et-unième",
    "vingt-deuxième",
    "vingt-troisième",
    "vingt-quatrième",
    "vingt-cinquième",
    "vingt-sixième",
    "vingt-septième",
    "vingt-huitième",
    "vingt-neuvième",
    "trentième",
    ]

# for degree (canon et civil), limitation 20+20 also used for
# the first [premier] cousin

_REMOVED_LEVEL = [
    "premier",
    "deuxième",
    "troisième",
    "quatrième",
    "cinquième",
    "sixième",
    "septième",
    "huitième",
    "neuvième",
    "dixième",
    "onzième",
    "douzième",
    "treizième",
    "quatorzième",
    "quinzième",
    "seizième",
    "dix-septième",
    "dix-huitième",
    "dix-neuvième",
    "vingtième",
    "vingt-et-unième",
    "vingt-deuxième",
    "vingt-troisième",
    "vingt-quatrième",
    "vingt-cinquième",
    "vingt-sixième",
    "vingt-septième",
    "vingt-huitième",
    "vingt-neuvième",
    "trentième",
    "trente-et-unième",
    "trente-deuxième",
    "trente-troisième",
    "trente-quatrième",
    "trente-cinquième",
    "trente-sixième",
    "trente-septième",
    "trente-huitième",
    "trente-neuvième",
    "quarantième",
    "quanrante-et-unième",
    ]

# small lists, use generation level if > [5]

_FATHER_LEVEL = ["", "le père%s", "le grand-père%s",
                 "l'arrière-grand-père%s", "le trisaïeul%s"]

_MOTHER_LEVEL = ["", "la mère%s", "la grand-mère%s",
                 "l'arrière-grand-mère%s", "la trisaïeule%s"]

_SON_LEVEL = ["", "le fils%s", "le petit-fils%s",
              "l'arrière-petit-fils%s"]

_DAUGHTER_LEVEL = ["", "la fille%s", "la petite-fille%s",
                   "l'arrière-petite-fille%s"]

_SISTER_LEVEL = ["", "la sœur%s", "la tante%s", "la grand-tante%s",
                 "l'arrière-grand-tante%s"]

_BROTHER_LEVEL = ["", "le frère%s", "l'oncle%s", "le grand-oncle%s",
                  "l'arrière-grand-oncle%s"]

_NEPHEW_LEVEL = ["", "le neveu%s", "le petit-neveu%s",
                 "l'arrière-petit-neveu%s"]

_NIECE_LEVEL = ["", "la nièce%s", "la petite-nièce%s",
                "l'arrière-petite-nièce%s"]

# kinship report

_PARENTS_LEVEL = ["", "les parents", "les grands-parents",
                  "les arrières-grands-parents", "les trisaïeux"]

_CHILDREN_LEVEL = ["", "les enfants", "les petits-enfants",
                   "les arrières-petits-enfants",
                   "les arrières-arrières-petits-enfants"]

_SIBLINGS_LEVEL = ["", "les frères et les sœurs",
                   "les oncles et les tantes",
                   "les grands-oncles et les grands-tantes",
                   "les arrières-grands-oncles et les arrières-grands-tantes"]

_NEPHEWS_NIECES_LEVEL = ["", "les neveux et les nièces",
                         "les petits-neveux et les petites-nièces",
                         "les arrière-petits-neveux et les arrières-petites-nièces"]

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------


class RelationshipCalculator(Relationship.RelationshipCalculator):
    """
    RelationshipCalculator Class
    """

    # RelCalc tool - Status Bar

    INLAW = ' (par alliance)'

    def __init__(self):
        Relationship.RelationshipCalculator.__init__(self)

    # from active person to common ancestor Ga=[level]

    def get_cousin(self, level, removed, inlaw=""):
        """
        cousins = same level, gender = male
        """
        if removed == 0 and level < len(_LEVEL_NAME):
            return "le %s cousin%s" % (_REMOVED_LEVEL[level - 1], inlaw)
        elif level < removed:
            self.get_uncle(level - 1, inlaw)
        else:

            # limitation gen = 29

            return "le cousin lointain, relié à la %s génération" % \
                _LEVEL_NAME[removed]

    def get_cousine(self, level, removed, inlaw=""):
        """
        cousines = same level, gender = female
        """
        if removed == 0 and level < len(_LEVEL_NAME):
            return "la %s cousine%s" % (_LEVEL_NAME[level - 1], inlaw)
        elif level < removed:
            self.get_aunt(level - 1, inlaw)
        else:
            return "la cousine lointaine, reliée à la %s génération" % \
                _LEVEL_NAME[removed]

    def get_parents(self, level):
        """
        ancestors
        """
        if level > len(_PARENTS_LEVEL) - 1:
            return "les ascendants lointains, à la %s génération" % \
                _LEVEL_NAME[level]
        else:
            return _PARENTS_LEVEL[level]

    def get_father(self, level, inlaw=""):
        """
        ancestor, gender = male
        """
        if level > len(_FATHER_LEVEL) - 1:
            return "l'ascendant lointain, à la %s génération" % \
                _LEVEL_NAME[level]
        else:
            return _FATHER_LEVEL[level] % inlaw

    def get_mother(self, level, inlaw=""):
        """
        ancestor, gender = female
        """
        if level > len(_MOTHER_LEVEL) - 1:
            return "l'ascendante lointaine, à la %s génération" % \
                _LEVEL_NAME[level]
        else:
            return _MOTHER_LEVEL[level] % inlaw

    def get_parent_unknown(self, level, inlaw=""):
        """
        unknown parent
        """
        if level > len(_LEVEL_NAME) - 1:
            return "l'ascendant lointain, à la %s génération" % \
                _LEVEL_NAME[level]
        elif level == 1:
            return "un parent%s" % inlaw
        else:
            return "un parent lointain%s" % inlaw

    def get_son(self, level, inlaw=""):
        """
        descendant, gender = male
        """
        if level > len(_SON_LEVEL) - 1:
            return "le descendant lointain, à la %s génération" % \
                _LEVEL_NAME[level + 1]
        else:
            return _SON_LEVEL[level] % inlaw

    def get_daughter(self, level, inlaw=""):
        """
        descendant, gender = female
        """
        if level > len(_DAUGHTER_LEVEL) - 1:
            return "la descendante lointaine, à la %s génération" % \
                _LEVEL_NAME[level + 1]
        else:
            return _DAUGHTER_LEVEL[level] % inlaw

    def get_child_unknown(self, level, inlaw=""):
        """
        descendant, gender = unknown
        """
        if level > len(_LEVEL_NAME) - 1:
            return "le descendant lointain, à la %s génération" % \
                _LEVEL_NAME[level + 1]
        elif level == 1:
            return "un enfant%s" % inlaw
        else:
            return "un descendant lointain%s" % inlaw

    def get_sibling_unknown(self, inlaw=""):
        """
        sibling of an ancestor, gender = unknown
        """
        return "un parent lointain%s" % inlaw

    def get_uncle(self, level, inlaw=""):
        """
        sibling of an ancestor, gender = male
        """
        if level > len(_BROTHER_LEVEL) - 1:
            return "l'oncle lointain, relié à la %s génération" % \
                _LEVEL_NAME[level]
        else:
            return _BROTHER_LEVEL[level] % inlaw

    def get_aunt(self, level, inlaw=""):
        """
        sibling of an ancestor, gender = female
        """
        if level > len(_SISTER_LEVEL) - 1:
            return "la tante lointaine, reliée à la %s génération" % \
                _LEVEL_NAME[level]
        else:
            return _SISTER_LEVEL[level] % inlaw

    def get_nephew(self, level, inlaw=""):
        """
        cousin of a descendant, gender = male
        """
        if level > len(_NEPHEW_LEVEL) - 1:
            return "le neveu lointain, à la %s génération" % _LEVEL_NAME[level]
        else:
            return _NEPHEW_LEVEL[level] % inlaw

    def get_niece(self, level, inlaw=""):
        """
        cousin of a descendant, gender = female
        """
        if level > len(_NIECE_LEVEL) - 1:
            return "la nièce lointaine, à la %s génération" % \
                _LEVEL_NAME[level]
        else:
            return _NIECE_LEVEL[level] % inlaw

# kinship report

    def get_plural_relationship_string(self, Ga, Gb):
        """
        voir Relationship.py
        """

        rel_str = "des parents lointains"
        atgen = " à la %sème génération"
        bygen = " par la %sème génération"
        cmt = " (frères ou sœurs d'un ascendant" + atgen % Ga + ")"
        if Ga == 0:

            # These are descendants

            if Gb < len(_CHILDREN_LEVEL):
                rel_str = _CHILDREN_LEVEL[Gb]
            else:
                rel_str = "les descendants" + atgen % (Gb + 1)
        elif Gb == 0:

            # These are parents/grand parents

            if Ga < len(_PARENTS_LEVEL):
                rel_str = _PARENTS_LEVEL[Ga]
            else:
                rel_str = "les ascendants" + atgen % (Ga + 1)
        elif Gb == 1:

            # These are siblings/aunts/uncles

            if Ga < len(_SIBLINGS_LEVEL):
                rel_str = _SIBLINGS_LEVEL[Ga]
            else:
                rel_str = "Les enfants d'un ascendant" + atgen % (Ga + 1) + \
                    cmt
        elif Ga == 1:

            # These are nieces/nephews

            if Gb < len(_NEPHEWS_NIECES_LEVEL):
                rel_str = _NEPHEWS_NIECES_LEVEL[Gb - 1]
            else:
                rel_str = "les neveux et les nièces" + atgen % Gb
        elif Ga > 1 and Ga == Gb:

            # These are cousins in the same generation
            # use custom level for latin words

            if Ga == 2:
                rel_str = "les cousins germains et cousines germaines"
            elif Ga <= len(_LEVEL_NAME):

                # %ss for plural

                rel_str = "les %ss cousins et cousines" % _LEVEL_NAME[Ga -
                        2]
            else:

            # security

                rel_str = "les cousins et cousines"
        elif Ga > 1 and Ga > Gb:

            # These are cousins in different generations with the second person
            # being in a higher generation from the common ancestor than the
            # first person.
            # use custom level for latin words and specific relation

            if Ga == 3 and Gb == 2:
                desc = " (cousins germains d'un parent)"
                rel_str = "les oncles et tantes à la mode de Bretagne" + \
                    desc
            elif Gb <= len(_LEVEL_NAME) and Ga - Gb < len(_REMOVED_LEVEL) and \
                Ga + Gb + 1 < len(_REMOVED_LEVEL):
                can = " du %s au %s degré (canon)" % (_REMOVED_LEVEL[Gb],
                        _REMOVED_LEVEL[Ga])
                civ = " et au %s degré (civil)" % _REMOVED_LEVEL[Ga + Gb +
                        1]
                rel_str = "les oncles et tantes" + can + civ
            elif Ga < len(_LEVEL_NAME):
                rel_str = "les grands-oncles et grands-tantes" + bygen % \
                    (Ga + 1)
            else:
                return rel_str
        elif Gb > 1 and Gb > Ga:

            # These are cousins in different generations with the second person
            # being in a lower generation from the common ancestor than the
            # first person.
            # use custom level for latin words and specific relation

            if Ga == 2 and Gb == 3:
                info = " (cousins issus d'un germain)"
                rel_str = "les neveux et nièces à la mode de Bretagne" + \
                    info
            elif Ga <= len(_LEVEL_NAME) and Gb - Ga < len(_REMOVED_LEVEL) and \
                Ga + Gb + 1 < len(_REMOVED_LEVEL):
                can = " du %s au %s degré (canon)" % (_REMOVED_LEVEL[Gb],
                        _REMOVED_LEVEL[Ga])
                civ = " et au %s degré (civil)" % _REMOVED_LEVEL[Ga + Gb +
                        1]
                rel_str = "les neveux et nièces" + can + civ
            elif Ga < len(_LEVEL_NAME):
                rel_str = "les neveux et nièces" + bygen % Gb
            else:
                return rel_str
        return rel_str

# quick report (missing on RelCalc tool - Status Bar)

    def get_single_relationship_string(
        self,
        Ga,
        Gb,
        gender_a,
        gender_b,
        reltocommon_a,
        reltocommon_b,
        only_birth=True,
        in_law_a=False,
        in_law_b=False,
        ):
        """
       voir Relationship.py
        """

        if only_birth:
            step = ""
        else:
            step = self.STEP

        if in_law_a or in_law_b:
            inlaw = self.INLAW
        else:
            inlaw = ""

        rel_str = "un parent lointains%s" % inlaw
        bygen = " par la %sème génération"
        if Ga == 0:

            # b is descendant of a

            if Gb == 0:
                rel_str = 'le même individu'
            elif gender_b == gen.lib.Person.MALE and Gb < len(_SON_LEVEL):

                # spouse of daughter

                if inlaw and Gb == 1 and not step:
                    rel_str = "le gendre"
                else:
                    rel_str = self.get_son(Gb)
            elif gender_b == gen.lib.Person.FEMALE and Gb < len(_DAUGHTER_LEVEL):

                # spouse of son

                if inlaw and Gb == 1 and not step:
                    rel_str = "la bru"
                else:
                    rel_str = self.get_daughter(Gb)
            elif Gb < len(_LEVEL_NAME) and gender_b == gen.lib.Person.MALE:

            # don't display inlaw

                rel_str = "le descendant lointain (%dème génération)" % \
                    (Gb + 1)
            elif Gb < len(_LEVEL_NAME) and gender_b == gen.lib.Person.FEMALE:
                rel_str = "la descendante lointaine (%dème génération)" % \
                    (Gb + 1)
            else:
                return self.get_child_unknown(Gb)
        elif Gb == 0:

            # b is parents/grand parent of a

            if gender_b == gen.lib.Person.MALE and Ga < len(_FATHER_LEVEL):

                # other spouse of father (new parent)

                if Ga == 1 and inlaw and self.STEP_SIB:
                    rel_str = "le beau-père"
                elif Ga == 1 and inlaw:

                # father of spouse (family of spouse)

                    rel_str = "le père du conjoint"
                else:
                    rel_str = self.get_father(Ga, inlaw)
            elif gender_b == gen.lib.Person.FEMALE and Ga < len(_MOTHER_LEVEL):

                # other spouse of mother (new parent)

                if Ga == 1 and inlaw and self.STEP_SIB:
                    rel_str = "la belle-mère"
                elif Ga == 1 and inlaw:

                # mother of spouse (family of spouse)

                    rel_str = "la mère du conjoint"
                else:
                    rel_str = self.get_mother(Ga, inlaw)
            elif Ga < len(_LEVEL_NAME) and gender_b == gen.lib.Person.MALE:
                rel_str = "l'ascendant lointain%s (%dème génération)" % \
                    (inlaw, Ga + 1)
            elif Ga < len(_LEVEL_NAME) and gender_b == gen.lib.Person.FEMALE:
                rel_str = "l'ascendante lointaine%s (%dème génération)" % \
                    (inlaw, Ga + 1)
            else:
                return self.get_parent_unknown(Ga, inlaw)
        elif Gb == 1:

            # b is sibling/aunt/uncle of a

            if gender_b == gen.lib.Person.MALE and Ga < len(_BROTHER_LEVEL):
                rel_str = self.get_uncle(Ga, inlaw)
            elif gender_b == gen.lib.Person.FEMALE and Ga < len(_SISTER_LEVEL):
                rel_str = self.get_aunt(Ga, inlaw)
            else:

                # don't display inlaw

                if gender_b == gen.lib.Person.MALE:
                    rel_str = "l'oncle lointain" + bygen % (Ga + 1)
                elif gender_b == gen.lib.Person.FEMALE:
                    rel_str = "la tante lointaine" + bygen % (Ga + 1)
                elif gender_b == gen.lib.Person.UNKNOWN:
                    rel_str = self.get_sibling_unknown(inlaw)
                else:
                    return rel_str
        elif Ga == 1:

            # b is niece/nephew of a

            if gender_b == gen.lib.Person.MALE and Gb < len(_NEPHEW_LEVEL):
                rel_str = self.get_nephew(Gb - 1, inlaw)
            elif gender_b == gen.lib.Person.FEMALE and Gb < len(_NIECE_LEVEL):
                rel_str = self.get_niece(Gb - 1, inlaw)
            else:
                if gender_b == gen.lib.Person.MALE:
                    rel_str = "le neveu lointain%s (%dème génération)" % \
                        (inlaw, Gb)
                elif gender_b == gen.lib.Person.FEMALE:
                    rel_str = "la nièce lointaine%s (%dème génération)" % \
                        (inlaw, Gb)
                elif gender_b == gen.lib.Person.UNKNOWN:
                    rel_str = self.get_sibling_unknown(inlaw)
                else:
                    return rel_str
        elif Ga == Gb:

            # a and b cousins in the same generation

            if gender_b == gen.lib.Person.MALE:
                rel_str = self.get_cousin(Ga - 1, 0, inlaw=inlaw)
            elif gender_b == gen.lib.Person.FEMALE:
                rel_str = self.get_cousine(Ga - 1, 0, inlaw=
                        inlaw)
            elif gender_b == gen.lib.Person.UNKNOWN:
                rel_str = self.get_sibling_unknown(inlaw)
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
            elif Gb <= len(_LEVEL_NAME) and Ga - Gb < len(_REMOVED_LEVEL) and \
                Ga + Gb + 1 < len(_REMOVED_LEVEL):
                can = " du %s au %s degré (canon)" % (_REMOVED_LEVEL[Gb],
                        _REMOVED_LEVEL[Ga])
                civ = " et au %s degré (civil)" % _REMOVED_LEVEL[Ga + Gb +
                        1]
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
            elif Ga <= len(_LEVEL_NAME) and Gb - Ga < len(_REMOVED_LEVEL) and \
                Ga + Gb + 1 < len(_REMOVED_LEVEL):
                can = " du %s au %s degré (canon)" % (_REMOVED_LEVEL[Gb],
                        _REMOVED_LEVEL[Ga])
                civ = " et au %s degré (civil)" % _REMOVED_LEVEL[Ga + Gb +
                        1]
                if gender_b == gen.lib.Person.MALE:
                    rel_str = "le neveu" + can + civ
                if gender_b == gen.lib.Person.FEMALE:
                    rel_str = "la nièce" + can + civ
                elif gender_b == gen.lib.Person.UNKNOWN:
                    rel_str = self.get_sibling_unknown(Ga, inlaw)
                else:
                    return rel_str
            elif Ga > len(_LEVEL_NAME):
                return rel_str
            else:
                if gender_b == gen.lib.Person.MALE:
                    rel_str = self.get_nephew(Ga, inlaw)
                elif gender_b == gen.lib.Person.FEMALE:
                    rel_str = self.get_niece(Ga, inlaw)
                elif gender_b == gen.lib.Person.UNKNOWN:
                    rel_str = self.get_sibling_unknown(Ga, inlaw)
                else:
                    return rel_str
        return rel_str

# RelCalc tool - Status Bar

    def get_sibling_relationship_string(self, sib_type, gender_a,
            gender_b, in_law_a=False, in_law_b=False):
        """
        voir Relationship.py
        """

        if in_law_a or in_law_b:
            inlaw = self.INLAW
        else:
            inlaw = ""

        if sib_type == self.NORM_SIB:
            if not inlaw:
                if gender_b == gen.lib.Person.MALE:
                    rel_str = 'le frère (germain)'
                elif gender_b == gen.lib.Person.FEMALE:
                    rel_str = 'la sœur (germaine)'
                else:
                    rel_str = 'le frère ou la sœur germain(e)'
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
        elif sib_type == self.HALF_SIB_MOTHER:

        # for descendants the "half" logic is reversed !

            if gender_b == gen.lib.Person.MALE:
                rel_str = "le demi-frère consanguin"
            elif gender_b == gen.lib.Person.FEMALE:
                rel_str = "la demi-sœur consanguine"
            else:
                rel_str = "le demi-frère ou la demi-sœur consanguin(e)"
        elif sib_type == self.HALF_SIB_FATHER:

        # for descendants the "half" logic is reversed !

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

PMGR = PluginManager.get_instance()
PMGR.register_relcalc(RelationshipCalculator, [
    "fr",
    "FR",
    "fr_FR",
    "fr_CA",
    "francais",
    "Francais",
    "fr_FR.UTF8",
    "fr_FR@euro",
    "fr_FR.UTF8@euro",
    "french",
    "French",
    "fr_FR.UTF-8",
    "fr_FR.utf-8",
    "fr_FR.utf8",
    "fr_CA.UTF-8",
    ])

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
    RC = RelationshipCalculator()
    test(RC, True)

# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2007  Donald N. Allingham
# Copyright (C) 2008-2010  Brian G. Matherly
# Copyright (C) 2007-2010  Jerome Rapinat
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

#-------------------------------------------------------------------------

# level is used for generation level:
# at %th generation

_LEVEL_NAME = [
    u"première",
    u"deuxième",
    u"troisième",
    u"quatrième",
    u"cinquième",
    u"sixième",
    u"septième",
    u"huitième",
    u"neuvième",
    u"dixième",
    u"onzième",
    u"douzième",
    u"treizième",
    u"quatorzième",
    u"quinzième",
    u"seizième",
    u"dix-septième",
    u"dix-huitième",
    u"dix-neuvième",
    u"vingtième",
    u"vingt-et-unième",
    u"vingt-deuxième",
    u"vingt-troisième",
    u"vingt-quatrième",
    u"vingt-cinquième",
    u"vingt-sixième",
    u"vingt-septième",
    u"vingt-huitième",
    u"vingt-neuvième",
    u"trentième",
    ]

# for degree (canon et civil), limitation 20+20 also used for
# the first [premier] cousin

_REMOVED_LEVEL = [
    u"premier",
    u"deuxième",
    u"troisième",
    u"quatrième",
    u"cinquième",
    u"sixième",
    u"septième",
    u"huitième",
    u"neuvième",
    u"dixième",
    u"onzième",
    u"douzième",
    u"treizième",
    u"quatorzième",
    u"quinzième",
    u"seizième",
    u"dix-septième",
    u"dix-huitième",
    u"dix-neuvième",
    u"vingtième",
    u"vingt-et-unième",
    u"vingt-deuxième",
    u"vingt-troisième",
    u"vingt-quatrième",
    u"vingt-cinquième",
    u"vingt-sixième",
    u"vingt-septième",
    u"vingt-huitième",
    u"vingt-neuvième",
    u"trentième",
    u"trente-et-unième",
    u"trente-deuxième",
    u"trente-troisième",
    u"trente-quatrième",
    u"trente-cinquième",
    u"trente-sixième",
    u"trente-septième",
    u"trente-huitième",
    u"trente-neuvième",
    u"quarantième",
    u"quanrante-et-unième",
    ]

# small lists, use generation level if > [5]

_FATHER_LEVEL = [u"", u"le père%s", u"le grand-père%s",
                 u"l'arrière-grand-père%s", u"le trisaïeul%s"]

_MOTHER_LEVEL = [u"", u"la mère%s", u"la grand-mère%s",
                 u"l'arrière-grand-mère%s", u"la trisaïeule%s"]

_SON_LEVEL = [u"", u"le fils%s", u"le petit-fils%s",
              u"l'arrière-petit-fils%s"]

_DAUGHTER_LEVEL = [u"", u"la fille%s", u"la petite-fille%s",
                   u"l'arrière-petite-fille%s"]

_SISTER_LEVEL = [u"", u"la sœur%s", u"la tante%s", u"la grand-tante%s",
                 u"l'arrière-grand-tante%s"]

_BROTHER_LEVEL = [u"", u"le frère%s", u"l'oncle%s", u"le grand-oncle%s",
                  u"l'arrière-grand-oncle%s"]

_NEPHEW_LEVEL = [u"", u"le neveu%s", u"le petit-neveu%s",
                 u"l'arrière-petit-neveu%s"]

_NIECE_LEVEL = [u"", u"la nièce%s", u"la petite-nièce%s",
                u"l'arrière-petite-nièce%s"]

# kinship report

_PARENTS_LEVEL = [u"", u"les parents", u"les grands-parents",
                  u"les arrières-grands-parents", u"les trisaïeux"]

_CHILDREN_LEVEL = [u"", u"les enfants", u"les petits-enfants",
                   u"les arrières-petits-enfants",
                   u"les arrières-arrières-petits-enfants"]

_SIBLINGS_LEVEL = [u"", u"les frères et les sœurs",
                   u"les oncles et les tantes",
                   u"les grands-oncles et les grands-tantes",
                   u"les arrières-grands-oncles et les arrières-grands-tantes"]

_NEPHEWS_NIECES_LEVEL = [u"", u"les neveux et les nièces",
                         u"les petits-neveux et les petites-nièces",
                         u"les arrière-petits-neveux et les arrières-petites-nièces"]

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

    INLAW = u' (par alliance)'

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
        elif level < 30:

            # limitation gen = 30

            return u"le cousin lointain, relié à la %s génération" % \
                _LEVEL_NAME[removed]
        else:

            # use numerical generation

            return u"le cousin lointain, relié à la %dème génération" % \
                (level + 1)

    def get_cousine(self, level, removed, inlaw=""):
        """
        cousines = same level, gender = female
        """
        if removed == 0 and level < len(_LEVEL_NAME):
            return "la %s cousine%s" % (_LEVEL_NAME[level - 1], inlaw)
        elif level < removed:
            self.get_aunt(level - 1, inlaw)
        elif level < 30:

            # limitation gen = 30

            return u"la cousine lointaine, reliée à la %s génération" % \
                _LEVEL_NAME[removed]
        else:

            # use numerical generation

            return u"la cousine lointaine, reliée à la %dème génération" % \
                (level + 1)

    def get_parents(self, level):
        """
        ancestors
        """
        if level > len(_PARENTS_LEVEL) - 1 and level < 30:

            # limitation gen = 30

            return u"les ascendants lointains, à la %s génération" % \
                _LEVEL_NAME[level]
        elif level > len(_PARENTS_LEVEL) - 1:

            # use numerical generation

            return u"les ascendants lointains, à la %dème génération" % level
        else:
            return _PARENTS_LEVEL[level]

    def get_father(self, level, inlaw=""):
        """
        ancestor, gender = male
        """
        if level > len(_FATHER_LEVEL) - 1 and level < 30:

            # limitation gen = 30

            return u"l'ascendant lointain, à la %s génération" % \
                _LEVEL_NAME[level]
        elif level > len(_FATHER_LEVEL) - 1:

            # use numerical generation

            return u"l'ascendant lointain, à la %dème génération" % level
        else:
            return _FATHER_LEVEL[level] % inlaw

    def get_mother(self, level, inlaw=""):
        """
        ancestor, gender = female
        """
        if level > len(_MOTHER_LEVEL) - 1 and level < 30:

            # limitation gen = 30

            return u"l'ascendante lointaine, à la %s génération" % \
                _LEVEL_NAME[level]
        elif level > len(_MOTHER_LEVEL) - 1:

            # use numerical generation

            return u"l'ascendante lointaine, à la %dème génération" % level
        else:
            return _MOTHER_LEVEL[level] % inlaw

    def get_parent_unknown(self, level, inlaw=""):
        """
        unknown parent
        """
        if level > len(_LEVEL_NAME) - 1 and level < 30:

            # limitation gen = 30

            return u"l'ascendant lointain, à la %s génération" % \
                _LEVEL_NAME[level]
        elif level == 1:
            return u"un parent%s" % inlaw
        else:
            return u"un parent lointain%s" % inlaw

    def get_son(self, level, inlaw=""):
        """
        descendant, gender = male
        """
        if level > len(_SON_LEVEL) - 1 and level < 30:

            # limitation gen = 30

            return u"le descendant lointain, à la %s génération" % \
                _LEVEL_NAME[level + 1]
        elif level > len(_SON_LEVEL) - 1:

            # use numerical generation

            return u"le descendant lointain, à la %dème génération" % level
        else:
            return _SON_LEVEL[level] % inlaw

    def get_daughter(self, level, inlaw=""):
        """
        descendant, gender = female
        """
        if level > len(_DAUGHTER_LEVEL) - 1 and level < 30:

            # limitation gen = 30

            return u"la descendante lointaine, à la %s génération" % \
                _LEVEL_NAME[level + 1]
        elif level > len(_DAUGHTER_LEVEL) - 1:

            # use numerical generation

            return u"la descendante lointaine, à la %dème génération" % level
        else:
            return _DAUGHTER_LEVEL[level] % inlaw

    def get_child_unknown(self, level, inlaw=""):
        """
        descendant, gender = unknown
        """
        if level > len(_LEVEL_NAME) - 1 and level < 30:

            # limitation gen = 30

            return u"le descendant lointain, à la %s génération" % \
                _LEVEL_NAME[level + 1]
        elif level == 1:
            return u"un enfant%s" % inlaw
        else:
            return u"un descendant lointain%s" % inlaw

    def get_sibling_unknown(self, inlaw=""):
        """
        sibling of an ancestor, gender = unknown
        """
        return u"un parent lointain%s" % inlaw

    def get_uncle(self, level, inlaw=""):
        """
        sibling of an ancestor, gender = male
        """
        if level > len(_BROTHER_LEVEL) - 1 and level < 30:

            # limitation gen = 30

            return u"l'oncle lointain, relié à la %s génération" % \
                _LEVEL_NAME[level]
        elif level > len(_BROTHER_LEVEL) - 1:

            # use numerical generation

            return u"l'oncle lointain, relié à la %dème génération" % \
                (level + 1)
        else:
            return _BROTHER_LEVEL[level] % inlaw

    def get_aunt(self, level, inlaw=""):
        """
        sibling of an ancestor, gender = female
        """
        if level > len(_SISTER_LEVEL) - 1 and level < 30:

            # limitation gen = 30

            return u"la tante lointaine, reliée à la %s génération" % \
                _LEVEL_NAME[level]
        elif level > len(_SISTER_LEVEL) -1:

            # use numerical generation

            return u"la tante lointaine, reliée à la %dème génération" % \
                (level + 1)
        else:
            return _SISTER_LEVEL[level] % inlaw

    def get_nephew(self, level, inlaw=""):
        """
        cousin of a descendant, gender = male
        """
        if level > len(_NEPHEW_LEVEL) - 1 and level < 30:

            # limitation gen = 30

            return u"le neveu lointain, à la %s génération" % _LEVEL_NAME[level]
        elif level > len(_NEPHEW_LEVEL) - 1:

            # use numerical generation

            return u"le neveu lointain, à la %dème génération" % (level + 1)
        else:
            return _NEPHEW_LEVEL[level] % inlaw

    def get_niece(self, level, inlaw=""):
        """
        cousin of a descendant, gender = female
        """
        if level > len(_NIECE_LEVEL) - 1 and level < 30:

            # limitation gen = 30

            return u"la nièce lointaine, à la %s génération" % \
                _LEVEL_NAME[level]
        elif level > len(_NIECE_LEVEL) - 1:

            # use numerical generation

            return u"la nièce lointaine, à la %dème génération" % (level + 1)
        else:
            return _NIECE_LEVEL[level] % inlaw

# kinship report

    def get_plural_relationship_string(self, Ga, Gb,
                                       reltocommon_a='', reltocommon_b='',
                                       only_birth=True,
                                       in_law_a=False, in_law_b=False):
        """
        voir Relationship.py
        """

        rel_str = u"des parents lointains"
        atgen = u" à la %sème génération"
        bygen = u" par la %sème génération"
        cmt = u" (frères ou sœurs d'un ascendant" + atgen % Ga + ")"
        if Ga == 0:

            # These are descendants

            if Gb < len(_CHILDREN_LEVEL):
                rel_str = _CHILDREN_LEVEL[Gb]
            else:
                rel_str = u"les descendants" + atgen % (Gb + 1)
        elif Gb == 0:

            # These are parents/grand parents

            if Ga < len(_PARENTS_LEVEL):
                rel_str = _PARENTS_LEVEL[Ga]
            else:
                rel_str = u"les ascendants" + atgen % (Ga + 1)
        elif Gb == 1:

            # These are siblings/aunts/uncles

            if Ga < len(_SIBLINGS_LEVEL):
                rel_str = _SIBLINGS_LEVEL[Ga]
            else:
                rel_str = u"les enfants d'un ascendant" + atgen % (Ga + 1) + \
                    cmt
        elif Ga == 1:

            # These are nieces/nephews

            if Gb < len(_NEPHEWS_NIECES_LEVEL):
                rel_str = _NEPHEWS_NIECES_LEVEL[Gb - 1]
            else:
                rel_str = u"les neveux et les nièces" + atgen % Gb
        elif Ga > 1 and Ga == Gb:

            # These are cousins in the same generation
            # use custom level for latin words

            if Ga == 2:
                rel_str = u"les cousins germains et cousines germaines"
            elif Ga <= len(_LEVEL_NAME):

                # %ss for plural

                rel_str = u"les %ss cousins et cousines" % _LEVEL_NAME[Ga -
                        2]
            else:

            # security

                rel_str = u"les cousins et cousines"
        elif Ga > 1 and Ga > Gb:

            # These are cousins in different generations with the second person
            # being in a higher generation from the common ancestor than the
            # first person.
            # use custom level for latin words and specific relation

            if Ga == 3 and Gb == 2:
                desc = u" (cousins germains d'un parent)"
                rel_str = u"les oncles et tantes à la mode de Bretagne" + \
                    desc
            elif Gb <= len(_LEVEL_NAME) and Ga - Gb < len(_REMOVED_LEVEL) and \
                Ga + Gb + 1 < len(_REMOVED_LEVEL):
                can = u" du %s au %s degré (canon)" % (_REMOVED_LEVEL[Gb],
                        _REMOVED_LEVEL[Ga])
                civ = u" et au %s degré (civil)" % _REMOVED_LEVEL[Ga + Gb +
                        1]
                rel_str = u"les oncles et tantes" + can + civ
            elif Ga < len(_LEVEL_NAME):
                rel_str = u"les grands-oncles et grands-tantes" + bygen % \
                    (Ga + 1)

        elif Gb > 1 and Gb > Ga:

            # These are cousins in different generations with the second person
            # being in a lower generation from the common ancestor than the
            # first person.
            # use custom level for latin words and specific relation

            if Ga == 2 and Gb == 3:
                info = u" (cousins issus d'un germain)"
                rel_str = u"les neveux et nièces à la mode de Bretagne" + \
                    info
            elif Ga <= len(_LEVEL_NAME) and Gb - Ga < len(_REMOVED_LEVEL) and \
                Ga + Gb + 1 < len(_REMOVED_LEVEL):
                can = u" du %s au %s degré (canon)" % (_REMOVED_LEVEL[Gb],
                        _REMOVED_LEVEL[Ga])
                civ = u" et au %s degré (civil)" % _REMOVED_LEVEL[Ga + Gb +
                        1]
                rel_str = u"les neveux et nièces" + can + civ
            elif Ga < len(_LEVEL_NAME):
                rel_str = u"les neveux et nièces" + bygen % Gb
            
        if in_law_b == True:
            rel_str = u"les conjoints pour %s" % rel_str
            
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
            inlaw = u""

        rel_str = u"un parent lointains%s" % inlaw
        bygen = u" par la %sème génération"
        if Ga == 0:

            # b is descendant of a

            if Gb == 0:
                rel_str = u"le même individu"
            elif gender_b == gen.lib.Person.MALE and Gb < len(_SON_LEVEL):

                # spouse of daughter

                if inlaw and Gb == 1 and not step:
                    rel_str = u"le gendre"
                else:
                    rel_str = self.get_son(Gb)
            elif gender_b == gen.lib.Person.FEMALE and Gb < len(_DAUGHTER_LEVEL):

                # spouse of son

                if inlaw and Gb == 1 and not step:
                    rel_str = u"la bru"
                else:
                    rel_str = self.get_daughter(Gb)
            elif Gb < len(_LEVEL_NAME) and gender_b == gen.lib.Person.MALE:

            # don't display inlaw

                rel_str = u"le descendant lointain (%dème génération)" % \
                    (Gb + 1)
            elif Gb < len(_LEVEL_NAME) and gender_b == gen.lib.Person.FEMALE:
                rel_str = u"la descendante lointaine (%dème génération)" % \
                    (Gb + 1)
            else:
                return self.get_child_unknown(Gb)
        elif Gb == 0:

            # b is parents/grand parent of a

            if gender_b == gen.lib.Person.MALE and Ga < len(_FATHER_LEVEL):

                # other spouse of father (new parent)

                if Ga == 1 and inlaw and self.STEP_SIB:
                    rel_str = u"le beau-père"
                elif Ga == 1 and inlaw:

                # father of spouse (family of spouse)

                    rel_str = u"le père du conjoint"
                else:
                    rel_str = self.get_father(Ga, inlaw)
            elif gender_b == gen.lib.Person.FEMALE and Ga < len(_MOTHER_LEVEL):

                # other spouse of mother (new parent)

                if Ga == 1 and inlaw and self.STEP_SIB:
                    rel_str = u"la belle-mère"
                elif Ga == 1 and inlaw:

                # mother of spouse (family of spouse)

                    rel_str = u"la mère du conjoint"
                else:
                    rel_str = self.get_mother(Ga, inlaw)
            elif Ga < len(_LEVEL_NAME) and gender_b == gen.lib.Person.MALE:
                rel_str = u"l'ascendant lointain%s (%dème génération)" % \
                    (inlaw, Ga + 1)
            elif Ga < len(_LEVEL_NAME) and gender_b == gen.lib.Person.FEMALE:
                rel_str = u"l'ascendante lointaine%s (%dème génération)" % \
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
                    rel_str = u"l'oncle lointain" + bygen % (Ga + 1)
                elif gender_b == gen.lib.Person.FEMALE:
                    rel_str = u"la tante lointaine" + bygen % (Ga + 1)
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
                    rel_str = u"le neveu lointain%s (%dème génération)" % \
                        (inlaw, Gb)
                elif gender_b == gen.lib.Person.FEMALE:
                    rel_str = u"la nièce lointaine%s (%dème génération)" % \
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
                rel_str = self.get_cousine(Ga - 1, 0, inlaw=inlaw)
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
                    desc = u" (cousin germain d'un parent)"
                    rel_str = u"l'oncle à la mode de Bretagne" + desc
                elif gender_b == gen.lib.Person.FEMALE:
                    desc = u" (cousine germaine d'un parent)"
                    rel_str = u"la tante à la mode de Bretagne" + desc
                elif gender_b == gen.lib.Person.UNKNOWN:
                    return self.get_sibling_unknown(Ga, inlaw)
                else:
                    return rel_str
            elif Gb <= len(_LEVEL_NAME) and Ga - Gb < len(_REMOVED_LEVEL) and \
                Ga + Gb + 1 < len(_REMOVED_LEVEL):
                can = u" du %s au %s degré (canon)" % (_REMOVED_LEVEL[Gb],
                        _REMOVED_LEVEL[Ga])
                civ = u" et au %s degré (civil)" % _REMOVED_LEVEL[Ga + Gb +
                        1]
                if gender_b == gen.lib.Person.MALE:
                    rel_str = u"l'oncle" + can + civ
                elif gender_b == gen.lib.Person.FEMALE:
                    rel_str = u"la tante" + can + civ
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
                info = u" (cousins issus d'un germain)"
                if gender_b == gen.lib.Person.MALE:
                    rel_str = u"le neveu à la mode de Bretagne" + info
                elif gender_b == gen.lib.Person.FEMALE:
                    rel_str = u"la nièce à la mode de Bretagne" + info
                elif gender_b == gen.lib.Person.UNKNOWN:
                    rel_str = self.get_sibling_unknown(Ga, inlaw)
                else:
                    return rel_str
            elif Ga <= len(_LEVEL_NAME) and Gb - Ga < len(_REMOVED_LEVEL) and \
                Ga + Gb + 1 < len(_REMOVED_LEVEL):
                can = u" du %s au %s degré (canon)" % (_REMOVED_LEVEL[Gb],
                        _REMOVED_LEVEL[Ga])
                civ = u" et au %s degré (civil)" % _REMOVED_LEVEL[Ga + Gb +
                        1]
                if gender_b == gen.lib.Person.MALE:
                    rel_str = u"le neveu" + can + civ
                if gender_b == gen.lib.Person.FEMALE:
                    rel_str = u"la nièce" + can + civ
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
            inlaw = u""

        if sib_type == self.NORM_SIB:
            if not inlaw:
                if gender_b == gen.lib.Person.MALE:
                    rel_str = u"le frère (germain)"
                elif gender_b == gen.lib.Person.FEMALE:
                    rel_str = u"la sœur (germaine)"
                else:
                    rel_str = u"le frère ou la sœur germain(e)"
            else:
                if gender_b == gen.lib.Person.MALE:
                    rel_str = u"le beau-frère"
                elif gender_b == gen.lib.Person.FEMALE:
                    rel_str = u"la belle-sœur"
                else:
                    rel_str = u"le beau-frère ou la belle-sœur"
        elif sib_type == self.UNKNOWN_SIB:
            if not inlaw:
                if gender_b == gen.lib.Person.MALE:
                    rel_str = u"le frère"
                elif gender_b == gen.lib.Person.FEMALE:
                    rel_str = u"la sœur"
                else:
                    rel_str = u"le frère ou la sœur"
            else:
                if gender_b == gen.lib.Person.MALE:
                    rel_str = u"le beau-frère"
                elif gender_b == gen.lib.Person.FEMALE:
                    rel_str = u"la belle-sœur"
                else:
                    rel_str = u"le beau-frère ou la belle-sœur"
        elif sib_type == self.HALF_SIB_MOTHER:

        # for descendants the "half" logic is reversed !

            if gender_b == gen.lib.Person.MALE:
                rel_str = u"le demi-frère consanguin"
            elif gender_b == gen.lib.Person.FEMALE:
                rel_str = u"la demi-sœur consanguine"
            else:
                rel_str = u"le demi-frère ou la demi-sœur consanguin(e)"
        elif sib_type == self.HALF_SIB_FATHER:

        # for descendants the "half" logic is reversed !

            if gender_b == gen.lib.Person.MALE:
                rel_str = u"le demi-frère utérin"
            elif gender_b == gen.lib.Person.FEMALE:
                rel_str = u"la demi-sœur utérine"
            else:
                rel_str = u"le demi-frère ou la demi-sœur utérin(e)"
        elif sib_type == self.STEP_SIB:
            if gender_b == gen.lib.Person.MALE:
                rel_str = u"le demi-frère"
            elif gender_b == gen.lib.Person.FEMALE:
                rel_str = u"la demi-sœur"
            else:
                rel_str = u"le demi-frère ou la demi-sœur"
        return rel_str

if __name__ == "__main__":

    # Test function. Call it as follows from the command line (so as to find
    #        imported modules):
    #    export PYTHONPATH=/path/to/gramps/src
    # python src/plugins/rel/rel_fr.py
    # (Above not needed here)

    """TRANSLATORS, copy this if statement at the bottom of your 
        rel_xx.py module, and test your work with:
        python src/plugins/rel/rel_xx.py
    """
    from Relationship import test
    RC = RelationshipCalculator()
    test(RC, True)

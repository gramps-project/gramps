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
from gen.plug import PluginManager

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------

# level est utilisé pour trouver/afficher le niveau de la génération :
# à la %sème génération

_level_name = [
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

# pour le degrè (canon et civil), limitation 20+20 ainsi que pour
# LE [premier] cousin

_removed_level = [
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

# listes volontairement limitées | small lists, use generation level if > [5]

_father_level = [u"", u"le père%s", u"le grand-père%s",
                 u"l'arrière-grand-père%s", u"le trisaïeul%s"]

_mother_level = [u"", u"la mère%s", u"la grand-mère%s",
                 u"l'arrière-grand-mère%s", u"la trisaïeule%s"]

_son_level = [u"", u"le fils%s", u"le petit-fils%s",
              u"l'arrière-petit-fils%s"]

_daughter_level = [u"", u"la fille%s", u"la petite-fille%s",
                   u"l'arrière-petite-fille%s"]

_sister_level = [u"", u"la sœur%s", u"la tante%s", u"la grand-tante%s",
                 u"l'arrière-grand-tante%s"]

_brother_level = [u"", u"le frère%s", u"l'oncle%s", u"le grand-oncle%s",
                  u"l'arrière-grand-oncle%s"]

_nephew_level = [u"", u"le neveu%s", u"le petit-neveu%s",
                 u"l'arrière-petit-neveu%s"]

_niece_level = [u"", u"la nièce%s", u"la petite-nièce%s",
                u"l'arrière-petite-nièce%s"]

# kinship report

_parents_level = [u"", u"les parents", u"les grands-parents",
                  u"les arrières-grands-parents", u"les trisaïeux"]

_children_level = [u"", u"les enfants", u"les petits-enfants",
                   u"les arrières-petits-enfants",
                   u"les arrières-arrières-petits-enfants"]

_siblings_level = [u"", u"les frères et les sœurs",
                   u"les oncles et les tantes",
                   u"les grands-oncles et les grands-tantes",
                   u"les arrières-grands-oncles et les arrières-grands-tantes"]

_nephews_nieces_level = [u"", u"les neveux et les nièces",
                         u"les petits-neveux et les petites-nièces",
                         u"les arrière-petits-neveux et les arrières-petites-nièces"]

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------


class RelationshipCalculator(Relationship.RelationshipCalculator):

    INLAW = u' (par alliance)'

    def __init__(self):
        Relationship.RelationshipCalculator.__init__(self)

# RelCalc tool - Status Bar

# de la personne active à l'ascendant commun Ga=[level]

    def get_cousin(self, level, removed, dir="", inlaw=""):
        if removed == 0 and level < len(_level_name):
            return u"le %s cousin%s" % (_removed_level[level - 1], inlaw)
        elif level < removed:
            rel_str = self.get_uncle(level - 1, inlaw)
        else:

            # limitation gen = 29

            return u"le cousin lointain, relié à la %s génération" % \
                _level_name[removed]

    def get_cousine(self, level, removed, dir="", inlaw=""):
        if removed == 0 and level < len(_level_name):
            return u"la %s cousine%s" % (_level_name[level - 1], inlaw)
        elif level < removed:
            rel_str = self.get_aunt(level - 1, inlaw)
        else:
            return u"la cousine lointaine, reliée à la %s génération" % \
                _level_name[removed]

    def get_parents(self, level):
        if level > len(_parents_level) - 1:
            return u"les ascendants lointains, à la %s génération" % \
                _level_name[level]
        else:
            return _parents_level[level]

    def get_father(self, level, inlaw=""):
        if level > len(_father_level) - 1:
            return u"l'ascendant lointain, à la %s génération" % \
                _level_name[level]
        else:
            return _father_level[level] % inlaw

    def get_mother(self, level, inlaw=""):
        if level > len(_mother_level) - 1:
            return u"l'ascendante lointaine, à la %s génération" % \
                _level_name[level]
        else:
            return _mother_level[level] % inlaw

    def get_parent_unknown(self, level, inlaw=""):
        if level > len(_level_name) - 1:
            return u"l'ascendant lointain, à la %s génération" % \
                _level_name[level]
        elif level == 1:
            return u"un parent%s" % inlaw
        else:
            return u"un parent lointain%s" % inlaw

    def get_son(self, level, inlaw=""):
        if level > len(_son_level) - 1:
            return u"le descendant lointain, à la %s génération" % \
                _level_name[level + 1]
        else:
            return _son_level[level] % inlaw

    def get_daughter(self, level, inlaw=""):
        if level > len(_daughter_level) - 1:
            return u"la descendante lointaine, à la %s génération" % \
                _level_name[level + 1]
        else:
            return _daughter_level[level] % inlaw

    def get_child_unknown(self, level, inlaw=""):
        if level > len(_level_name) - 1:
            return u"le descendant lointain, à la %s génération" % \
                _level_name[level + 1]
        elif level == 1:
            return u"un enfant%s" % inlaw
        else:
            return u"un descendant lointain%s" % inlaw

    def get_sibling_unknown(self, level, inlaw=""):
        return u"un parent lointain%s" % inlaw

    def get_uncle(self, level, inlaw=""):
        if level > len(_brother_level) - 1:
            return u"l'oncle lointain, relié à la %s génération" % \
                _level_name[level]
        else:
            return _brother_level[level] % inlaw

    def get_aunt(self, level, inlaw=""):
        if level > len(_sister_level) - 1:
            return u"la tante lointaine, reliée à la %s génération" % \
                _level_name[level]
        else:
            return _sister_level[level] % inlaw

    def get_nephew(self, level, inlaw=""):
        if level > len(_nephew_level) - 1:
            return u"le neveu lointain, à la %s génération" % _level_name[level]
        else:
            return _nephew_level[level] % inlaw

    def get_niece(self, level, inlaw=""):
        if level > len(_niece_level) - 1:
            return u"la nièce lointaine, à la %s génération" % \
                _level_name[level]
        else:
            return _niece_level[level] % inlaw

# kinship report

    def get_plural_relationship_string(self, Ga, Gb):
        """
        voir Relationship.py
        """

        rel_str = u"des parents lointains"
        gen = u" à la %sème génération"
        bygen = u" par la %sème génération"
        cmt = u" (frères ou sœurs d'un ascendant" + gen % Ga + ")"
        if Ga == 0:

            # These are descendants

            if Gb < len(_children_level):
                rel_str = _children_level[Gb]
            else:
                rel_str = u"les descendants" + gen % (Gb + 1)
        elif Gb == 0:

            # These are parents/grand parents

            if Ga < len(_parents_level):
                rel_str = _parents_level[Ga]
            else:
                rel_str = u"les ascendants" + gen % (Ga + 1)
        elif Gb == 1:

            # These are siblings/aunts/uncles

            if Ga < len(_siblings_level):
                rel_str = _siblings_level[Ga]
            else:
                rel_str = u"Les enfants d'un ascendant" + gen % (Ga + 1) + \
                    cmt
        elif Ga == 1:

            # These are nieces/nephews

            if Gb < len(_nephews_nieces_level):
                rel_str = _nephews_nieces_level[Gb - 1]
            else:
                rel_str = u"les neveux et les nièces" + gen % Gb
        elif Ga > 1 and Ga == Gb:

            # These are cousins in the same generation
            # use custom level for latin words

            if Ga == 2:
                rel_str = u"les cousins germains et cousines germaines"
            elif Ga <= len(_level_name):

                # %ss for plural

                rel_str = u"les %ss cousins et cousines" % _level_name[Ga -
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
            elif Gb <= len(_level_name) and Ga - Gb < len(_removed_level) and \
                Ga + Gb + 1 < len(_removed_level):
                can = u" du %s au %s degré (canon)" % (_removed_level[Gb],
                        _removed_level[Ga])
                civ = u" et au %s degré (civil)" % _removed_level[Ga + Gb +
                        1]
                rel_str = u"les oncles et tantes" + can + civ
            elif Ga < len(_level_name):
                rel_str = u"les grands-oncles et grands-tantes" + bygen % \
                    (Ga + 1)
            else:
                return rel_str
        elif Gb > 1 and Gb > Ga:

            # These are cousins in different generations with the second person
            # being in a lower generation from the common ancestor than the
            # first person.
            # use custom level for latin words and specific relation

            if Ga == 2 and Gb == 3:
                info = u" (cousins issus d'un germain)"
                rel_str = u"les neveux et nièces à la mode de Bretagne" + \
                    info
            elif Ga <= len(_level_name) and Gb - Ga < len(_removed_level) and \
                Ga + Gb + 1 < len(_removed_level):
                can = u" du %s au %s degré (canon)" % (_removed_level[Gb],
                        _removed_level[Ga])
                civ = u" et au %s degré (civil)" % _removed_level[Ga + Gb +
                        1]
                rel_str = u"les neveux et nièces" + can + civ
            elif Ga < len(_level_name):
                rel_str = u"les neveux et nièces" + bygen % Gb
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
            inlaw = u""

        rel_str = u"un parent lointains%s" % inlaw
        bygen = u" par la %sème génération"
        if Ga == 0:

            # b is descendant of a

            if Gb == 0:
                rel_str = u"le même individu"
            elif gender_b == gen.lib.Person.MALE and Gb < len(_son_level):

                # spouse of daughter

                if inlaw and Gb == 1 and not step:
                    rel_str = u"le gendre"
                else:
                    rel_str = self.get_son(Gb)
            elif gender_b == gen.lib.Person.FEMALE and Gb < len(_daughter_level):

                # spouse of son

                if inlaw and Gb == 1 and not step:
                    rel_str = u"la bru"
                else:
                    rel_str = self.get_daughter(Gb)
            elif Gb < len(_level_name) and gender_b == gen.lib.Person.MALE:

            # don't display inlaw

                rel_str = u"le descendant lointain (%dème génération)" % \
                    (Gb + 1)
            elif Gb < len(_level_name) and gender_b == gen.lib.Person.FEMALE:
                rel_str = u"la descendante lointaine (%dème génération)" % \
                    (Gb + 1)
            else:
                return self.get_child_unknown(Gb)
        elif Gb == 0:

            # b is parents/grand parent of a

            if gender_b == gen.lib.Person.MALE and Ga < len(_father_level):

                # other spouse of father (new parent)

                if Ga == 1 and inlaw and self.STEP_SIB:
                    rel_str = u"le beau-père"
                elif Ga == 1 and inlaw:

                # father of spouse (family of spouse)

                    rel_str = u"le père du conjoint"
                else:
                    rel_str = self.get_father(Ga, inlaw)
            elif gender_b == gen.lib.Person.FEMALE and Ga < len(_mother_level):

                # other spouse of mother (new parent)

                if Ga == 1 and inlaw and self.STEP_SIB:
                    rel_str = u"la belle-mère"
                elif Ga == 1 and inlaw:

                # mother of spouse (family of spouse)

                    rel_str = u"la mère du conjoint"
                else:
                    rel_str = self.get_mother(Ga, inlaw)
            elif Ga < len(_level_name) and gender_b == gen.lib.Person.MALE:
                rel_str = u"l'ascendant lointain%s (%dème génération)" % \
                    (inlaw, Ga + 1)
            elif Ga < len(_level_name) and gender_b == gen.lib.Person.FEMALE:
                rel_str = u"l'ascendante lointaine%s (%dème génération)" % \
                    (inlaw, Ga + 1)
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
                    rel_str = u"l'oncle lointain" + bygen % (Ga + 1)
                elif gender_b == gen.lib.Person.FEMALE:
                    rel_str = u"la tante lointaine" + bygen % (Ga + 1)
                elif gender_b == gen.lib.Person.UNKNOWN:
                    rel_str = self.get_sibling_unknown(Ga, inlaw)
                else:
                    return rel_str
        elif Ga == 1:

            # b is niece/nephew of a

            if gender_b == gen.lib.Person.MALE and Gb < len(_nephew_level):
                rel_str = self.get_nephew(Gb - 1, inlaw)
            elif gender_b == gen.lib.Person.FEMALE and Gb < len(_niece_level):
                rel_str = self.get_niece(Gb - 1, inlaw)
            else:
                if gender_b == gen.lib.Person.MALE:
                    rel_str = u"le neveu lointain%s (%dème génération)" % \
                        (inlaw, Gb)
                elif gender_b == gen.lib.Person.FEMALE:
                    rel_str = u"la nièce lointaine%s (%dème génération)" % \
                        (inlaw, Gb)
                elif gender_b == gen.lib.Person.UNKNOWN:
                    rel_str = self.get_sibling_unknown(Ga, inlaw)
                else:
                    return rel_str
        elif Ga == Gb:

            # a and b cousins in the same generation

            if gender_b == gen.lib.Person.MALE:
                rel_str = self.get_cousin(Ga - 1, 0, dir="", inlaw=inlaw)
            elif gender_b == gen.lib.Person.FEMALE:
                rel_str = self.get_cousine(Ga - 1, 0, dir="", inlaw=
                        inlaw)
            elif gender_b == gen.lib.Person.UNKNOWN:
                rel_str = self.get_sibling_unknown(Ga - 1, inlaw)
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
            elif Gb <= len(_level_name) and Ga - Gb < len(_removed_level) and \
                Ga + Gb + 1 < len(_removed_level):
                can = u" du %s au %s degré (canon)" % (_removed_level[Gb],
                        _removed_level[Ga])
                civ = u" et au %s degré (civil)" % _removed_level[Ga + Gb +
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
            elif Ga <= len(_level_name) and Gb - Ga < len(_removed_level) and \
                Ga + Gb + 1 < len(_removed_level):
                can = u" du %s au %s degré (canon)" % (_removed_level[Gb],
                        _removed_level[Ga])
                civ = u" et au %s degré (civil)" % _removed_level[Ga + Gb +
                        1]
                if gender_b == gen.lib.Person.MALE:
                    rel_str = u"le neveu" + can + civ
                if gender_b == gen.lib.Person.FEMALE:
                    rel_str = u"la nièce" + can + civ
                elif gender_b == gen.lib.Person.UNKNOWN:
                    rel_str = self.get_sibling_unknown(Ga, inlaw)
                else:
                    return rel_str
            elif Ga > len(_level_name):
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

        # Logique inversée ! Pourquoi ?

            if gender_b == gen.lib.Person.MALE:
                rel_str = u"le demi-frère consanguin"
            elif gender_b == gen.lib.Person.FEMALE:
                rel_str = u"la demi-sœur consanguine"
            else:
                rel_str = u"le demi-frère ou la demi-sœur consanguin(e)"
        elif sib_type == self.HALF_SIB_FATHER:

        # Logique inversée ! Pourquoi ?

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


#-------------------------------------------------------------------------
#
# Register this class with the Plugins system
#
#-------------------------------------------------------------------------

pmgr = PluginManager.get_instance()
pmgr.register_relcalc(RelationshipCalculator, [
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
    # python src/plugins/rel/rel_fr.py
    # (Above not needed here)

    """TRANSLATORS, copy this if statement at the bottom of your 
        rel_xx.py module, and test your work with:
        python src/plugins/rel/rel_xx.py
    """
    from Relationship import test
    rc = RelationshipCalculator()
    test(rc, True)

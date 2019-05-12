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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
"""
Slovak-specific classes for relationships.
"""

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------

from gramps.gen.lib import Person
import gramps.gen.relationship

#-------------------------------------------------------------------------
#
#GRAMPS 3.x - Slovak-specific terms by Lubo Vasko
#
#-------------------------------------------------------------------------

# hĺbka použitá pre označenie / zistenie vzťahov od genenácie :
# ku generácii,


_level_name = [ "prvého", "druhého", "tretieho", "štvrtého", "piateho", "šiesteho",
                "siedmeho", "ôsmeho", "deviateho", "desiateho", "jedenásteho", "dvanásteho",
                "trinásteho", "štrnásteho", "pätnásteho", "šestnásteho",
                "sedemnásteho", "osemnásteho", "devätnásteho", "dvadsiateho", "dvadsiatehoprvého", "dvadsiatehodruhého",
                "dvadsiatehotretieho", "dvadsiatehoštvrtého","dvadsiatehopiateho","dvadsiatehošiesteho","dvadsiatehosiedmeho",
                "dvadsiatehoôsmeho","dvadsiatehodeviateho","tridsiateho" ]


# vzdialení príbuzní

_removed_level = [ "prvého", "druhého", "tretieho", "štvrtého", "piateho", "šiesteho",
                "siedmeho", "ôsmeho", "deviateho", "desiateho", "jedenásteho", "dvanásteho",
                "trinásteho", "štrnásteho", "pätnásteho", "šestnásteho",
                "sedemnásteho", "osemnásteho", "devätnásteho", "dvadsiateho", "dvadsiatehoprvého", "dvadsiatehodruhého",
                "dvadsiatehotretieho", "dvadsiatehoštvrtého","dvadsiatehopiateho","dvadsiatehošiesteho","dvadsiatehosiedmeho",
                "dvadsiatehoôsmeho","dvadsiatehodeviateho","tridsiateho" ]


# small lists, use generation level if > [5]

_father_level = [ "", "otec%s", "starý otec%s", "prastarý otec%s", "prapredok%s", ]

_mother_level = [ "", "matka%s", "stará matka%s",
                  "prastará matka%s", "prapredok%s", ]

_son_level = [ "", "syn%s", "vnuk%s", "pravnuk%s", ]

_daughter_level = [ "", "dcéra%s", "vnučka%s",
                    "pravnučka%s", ]

_sister_level = [ "", "sestra%s", "teta%s", "prateta%s", "praprateta%s", ]

_brother_level = [ "", "brat%s", "strýko%s", "prastrýko%s", "praprastrýko%s", ]

_nephew_level = [ "", "synovec%s", "prasynovec%s", "praprasynovec%s", ]

_niece_level = [ "", "neter%s", "praneter%s", "prapraneter%s", ]

# kinship report

_parents_level = [ "", "rodičia", "starí rodičia",
                    "prastarí rodičia", "predkovia", ]

_children_level = [ "", "deti", "vnúčatá",
                    "pravnúčatá",
                    "pra-pravnúčatá", ]

_siblings_level = [ "", "bratia a sestry",
                    "strýkovia a tety",
                    "prastrýkovia a pratety",
                    "pra-prastrýkovia a pra-pratety",
                    ]

_nephews_nieces_level = [ "", "synovci a netere",
                          "prasynovci a pranetere",
                          "pra-prasynovci a pra-pranetere",
                        ]

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------

class RelationshipCalculator(gramps.gen.relationship.RelationshipCalculator):
    """
    RelationshipCalculator Class
    """

    INLAW = ' (m. zväzok)'


    def __init__(self):
        gramps.gen.relationship.RelationshipCalculator.__init__(self)


# od aktívnej osoby vzhľadom k spoločnému predkovi Ga=[level]
# pre vyhodnotenie vzťahov

    def get_cousin(self, level, removed, dir = '', inlaw=''):
        if removed == 0 and level < len(_level_name):
            return "bratranec %s %sstupňa" % (_removed_level[level-1],
                                        inlaw)
        elif (level) < (removed):
            rel_str = self.get_uncle(level-1, inlaw)
        else:
            # limitation gen = 29
            return "vzdialený bratranec, spojený s %s generáciou" % (
                        _level_name[removed])

    def get_cousine(self, level, removed, dir = '', inlaw=''):
        if removed == 0 and level < len(_level_name):
            return "sesternica %s %sstupňa" % (_level_name[level-1],
                                        inlaw)
        elif (level) < (removed):
            rel_str = self.get_aunt(level-1, inlaw)
        else:
            return "vzdialená sesternica, spojená s %s generáciou" % (
                        _level_name[removed])

    def get_parents(self, level):
        if level > len(_parents_level)-1:
            return "vzdialení predkovia z %s generácie" % (
                        _level_name[level])
        else:
            return _parents_level[level]

    def get_father(self, level, inlaw=''):
        if level > len(_father_level)-1:
            return "vzdialený predok z %s generácie" % (
                        _level_name[level])
        else:
            return _father_level[level] % inlaw

    def get_mother(self, level, inlaw=''):
        if level > len(_mother_level)-1:
            return "vzdialený príbuzný, predok z %s generácie" % (
                        _level_name[level])
        else:
            return _mother_level[level] % inlaw

    def get_parent_unknown(self, level, inlaw=''):
        if level > len(_level_name)-1:
            return "vzdialený príbuzný, predok z %s generácie" % (
                        _level_name[level])
        else:
            return "vzdialený príbuzný%s" % (inlaw)

    def get_son(self, level, inlaw=''):
        if level > len(_son_level)-1:
            return "vzdialený potomok z %s generácie" % (
                        _level_name[level+1])
        else:
            return _son_level[level] % (inlaw)

    def get_daughter(self, level, inlaw=''):
        if level > len(_daughter_level)-1:
            return "vzdialený potomok z %s generácie" % (
                        _level_name[level+1])
        else:
            return _daughter_level[level] % (inlaw)

    def get_child_unknown(self, level, inlaw=''):
        if level > len(_level_name)-1:
            return "vzdialený potomok z %s generácie" % (
                        _level_name[level+1])
        else:
            return "vzdialený potomok%s" % (inlaw)

    def get_sibling_unknown(self, level, inlaw=''):
        return "vzdialený príbuzný%s" % (inlaw)

    def get_uncle(self, level, inlaw=''):
        if level > len(_brother_level)-1:
            return "vzdialený strýko z %s generácie" % (
                        _level_name[level])
        else:
            return _brother_level[level] % (inlaw)

    def get_aunt(self, level, inlaw=''):
        if level > len(_sister_level)-1:
            return "vzdialená teta z %s generácie" % (
                        _level_name[level])
        else:
            return _sister_level[level] % (inlaw)

    def get_nephew(self, level, inlaw=''):
        if level > len(_nephew_level)-1:
            return "vzdialený synovec z %s generácie" % (
                        _level_name[level])
        else:
            return _nephew_level[level] % (inlaw)

    def get_niece(self, level, inlaw=''):
        if level > len(_niece_level)-1:
            return "vzdialená neter z %s generácie" % (
                        _level_name[level])
        else:
            return _niece_level[level] % (inlaw)



# kinship report

    def get_plural_relationship_string(self, Ga, Gb,
                                       reltocommon_a='', reltocommon_b='',
                                       only_birth=True,
                                       in_law_a=False, in_law_b=False):
        """
        see relationship.py
        """
        rel_str = "vzdialení príbuzní"
        gen = " z %s-ej generácie"
        bygen = " na %-u generáciu"
        cmt = " (bratia alebo sestry predka" + gen % (
                       Ga) + ")"
        if Ga == 0:
            # These are descendants
            if Gb < len(_children_level):
                rel_str = _children_level[Gb]
            else:
                rel_str = "potomkovia" + gen % (
                               Gb+1)
        elif Gb == 0:
            # These are parents/grand parents
            if Ga < len(_parents_level):
                rel_str = _parents_level[Ga]
            else:
                rel_str = "predkovia" + gen % (
                               Ga+1)
        elif Gb == 1:
            # These are siblings/aunts/uncles
            if Ga < len(_siblings_level):
                rel_str = _siblings_level[Ga]
            else:
                rel_str = "deti predka" + gen % (
                               Ga+1) + cmt
        elif Ga == 1:
            # These are nieces/nephews
            if Gb < len(_nephews_nieces_level):
                rel_str = _nephews_nieces_level[Gb-1]
            else:
                rel_str = "synovci a netere" + gen % (
                               Gb)
        elif Ga > 1 and Ga == Gb:
            # These are cousins in the same generation
            # use custom level for latin words
            if Ga == 2:
                rel_str = "vlastní bratranci a sesternice"
            elif Ga <= len(_level_name):
                # %ss for plural
                rel_str = " %ss bratranci a sesternice" % _level_name[Ga-2]
            # security
            else:
                rel_str = "bratranci a sesternice"
        elif Ga > 1 and Ga > Gb:
            # These are cousins in different generations with the second person
            # being in a higher generation from the common ancestor than the
            # first person.
            # use custom level for latin words and specific relation
            if Ga == 3 and Gb == 2:
                desc = " (vlastní bratranci niektorého z rodičov)"
                rel_str = "strýkovia a tety z ďalšieho kolena" + desc
            elif Gb <= len(_level_name) and (Ga-Gb) < len(_removed_level) and (Ga+Gb+1) < len(_removed_level):
                can = " z %s do %s stupňa (kan.)"  % (
                           _removed_level[Gb], _removed_level[Ga] )
                civ = " a do %s stupňa (civ.)" % ( _removed_level[Ga+Gb+1] )
                rel_str = "strýkovia a tety" + can + civ
            elif Ga < len(_level_name):
                rel_str = "prastrýkovia a pratety" + bygen % (
                               Ga+1)
        elif Gb > 1 and Gb > Ga:
            # These are cousins in different generations with the second person
            # being in a lower generation from the common ancestor than the
            # first person.
            # use custom level for latin words and specific relation
            if Ga == 2 and Gb == 3:
                info = " (potomok bratranca-sesternice)"
                rel_str = "synovci a netere z ďalšieho kolena" + info
            elif Ga <= len(_level_name) and (Gb-Ga) < len(_removed_level) and (Ga+Gb+1) < len(_removed_level):
                can = " z %s do %s stupňa (kan.)"  % (
                           _removed_level[Gb], _removed_level[Ga] )
                civ = " a do %s stupňa (civ.)" % ( _removed_level[Ga+Gb+1] )
                rel_str = "synovci a netere" + can + civ
            elif Ga < len(_level_name):
                rel_str = "synovci a netere" + bygen % (
                                Gb)
        if in_law_b == True:
            # TODO: Translate this!
            rel_str = "spouses of %s" % rel_str

        return rel_str


# quick report (missing on RelCalc tool - Status Bar)

    def get_single_relationship_string(self, Ga, Gb, gender_a, gender_b,
                                       reltocommon_a, reltocommon_b,
                                       only_birth=True,
                                       in_law_a=False, in_law_b=False):
        """
        see relationship.py
        """
        if only_birth:
            step = ''
        else:
            step = self.STEP

        if in_law_a or in_law_b :
            inlaw = self.INLAW
        else:
            inlaw = ''


        rel_str = "vzdialený príbuznýs%s" % (inlaw)
        bygen = " z %s generácie"
        if Ga == 0:
            # b is descendant of a
            if Gb == 0 :
                rel_str = 'tá istá osoba'
            elif gender_b == Person.MALE and Gb < len(_son_level):
                # spouse of daughter
                if inlaw and Gb == 1 and not step:
                    rel_str = "zať"
                else:
                    rel_str = self.get_son(Gb)
            elif gender_b == Person.FEMALE and Gb < len(_daughter_level):
                # spouse of son
                if inlaw and Gb == 1 and not step:
                    rel_str = "nevesta"
                else:
                    rel_str = self.get_daughter(Gb)
            # don't display inlaw
            elif Gb < len(_level_name) and gender_b == Person.MALE:
                rel_str = "vzdialený potomok (%d generácia)" % (
                               Gb+1)
            elif Gb < len(_level_name) and gender_b == Person.FEMALE:
                rel_str = "vzdialený potomok(žena) (%d generácia)" % (
                               Gb+1)
            else:
                return self.get_child_unknown(Gb)
        elif Gb == 0:
            # b is parents/grand parent of a
            if gender_b == Person.MALE and Ga < len(_father_level):
                # other spouse of father (new parent)
                if Ga == 1 and inlaw and self.STEP_SIB:
                    rel_str = "svokor"
                # father of spouse (family of spouse)
                elif Ga == 1 and inlaw:
                    rel_str = "otec partnera"
                else:
                    rel_str = self.get_father(Ga, inlaw)
            elif gender_b == Person.FEMALE and Ga < len(_mother_level):
                # other spouse of mother (new parent)
                if Ga == 1 and inlaw and self.STEP_SIB:
                    rel_str = "svokra"
                # mother of spouse (family of spouse)
                elif Ga == 1 and inlaw:
                    rel_str = "matka partnera"
                else:
                    rel_str = self.get_mother(Ga, inlaw)
            elif Ga < len(_level_name) and gender_b == Person.MALE:
                rel_str = "vzdialený predok%s (%d generácia)" % (
                               inlaw, Ga+1)
            elif Ga < len(_level_name) and gender_b == Person.FEMALE:
                rel_str = "vzdialený predok(žena)%s (%d generácia)" % (
                               inlaw, Ga+1)
            else:
                return self.get_parent_unknown(Ga, inlaw)
        elif Gb == 1:
            # b is sibling/aunt/uncle of a
            if gender_b == Person.MALE and Ga < len(_brother_level):
                rel_str = self.get_uncle(Ga, inlaw)
            elif gender_b == Person.FEMALE and Ga < len(_sister_level):
                rel_str = self.get_aunt(Ga, inlaw)
            else:
                # don't display inlaw
                if gender_b == Person.MALE:
                    rel_str = "vzdialený strýko" + bygen % (
                                   Ga+1)
                elif gender_b == Person.FEMALE:
                    rel_str = "vzdialená teta" + bygen % (
                                   Ga+1)
                elif gender_b == Person.UNKNOWN:
                    rel_str = self.get_sibling_unknown(Ga, inlaw)
                else:
                    return rel_str
        elif Ga == 1:
            # b is niece/nephew of a
            if gender_b == Person.MALE and Gb < len(_nephew_level):
                rel_str = self.get_nephew(Gb-1, inlaw)
            elif gender_b == Person.FEMALE and Gb < len(_niece_level):
                rel_str = self.get_niece(Gb-1, inlaw)
            else:
                if gender_b == Person.MALE:
                    rel_str = "vzdialený synovec%s (%d generácia)" %  (
                                   inlaw, Gb)
                elif gender_b == Person.FEMALE:
                    rel_str = "vzdialená neter%s (%d generácia)" %  (
                                   inlaw, Gb)
                elif gender_b == Person.UNKNOWN:
                    rel_str = self.get_sibling_unknown(Ga, inlaw)
                else:
                    return rel_str
        elif Ga == Gb:
            # a and b cousins in the same generation
            if gender_b == Person.MALE:
                rel_str = self.get_cousin(Ga-1, 0, dir = '',
                                     inlaw=inlaw)
            elif gender_b == Person.FEMALE:
                rel_str = self.get_cousine(Ga-1, 0, dir = '',
                                     inlaw=inlaw)
            elif gender_b == Person.UNKNOWN:
                rel_str = self.get_sibling_unknown(Ga-1, inlaw)
            else:
                return rel_str
        elif Ga > 1 and Ga > Gb:
            # These are cousins in different generations with the second person
            # being in a higher generation from the common ancestor than the
            # first person.
            if Ga == 3 and Gb == 2:
                if gender_b == Person.MALE:
                    desc = " (bratranec niektorého z rodičov)"
                    rel_str = "strýko z druhého kolena" + desc
                elif gender_b == Person.FEMALE:
                    desc = " (sesternica niektorého z rodičov)"
                    rel_str = "teta z druhého kolena" + desc
                elif gender_b == Person.UNKNOWN:
                    return self.get_sibling_unknown(Ga, inlaw)
                else:
                    return rel_str
            elif Gb <= len(_level_name) and (Ga-Gb) < len(_removed_level) and (Ga+Gb+1) < len(_removed_level):
                can = " z %s do %s stupňa (kan.)"  % (
                           _removed_level[Gb], _removed_level[Ga] )
                civ = " a do %s stupňa (civ.)" % ( _removed_level[Ga+Gb+1] )
                if gender_b == Person.MALE:
                    rel_str = "strýko" + can + civ
                elif gender_b == Person.FEMALE:
                    rel_str = "teta" + can + civ
                elif gender_b == Person.UNKNOWN:
                    rel_str = self.get_sibling_unknown(Ga, inlaw)
                else:
                    return rel_str
            else:
                if gender_b == Person.MALE:
                    rel_str = self.get_uncle(Ga, inlaw)
                elif gender_b == Person.FEMALE:
                    rel_str = self.get_aunt(Ga, inlaw)
                elif gender_b == Person.UNKNOWN:
                    rel_str = self.get_sibling_unknown(Ga, inlaw)
                else:
                    return rel_str
        elif Gb > 1 and Gb > Ga:
            # These are cousins in different generations with the second person
            # being in a lower generation from the common ancestor than the
            # first person.
            if Ga == 2 and Gb == 3:
                info = " (potomok bratranca/sesternice)"
                if gender_b == Person.MALE:
                    rel_str = "synovec z druhého kolena" + info
                elif gender_b == Person.FEMALE:
                    rel_str = "neter z druhého kolena" + info
                elif gender_b == Person.UNKNOWN:
                    rel_str = self.get_sibling_unknown(Ga, inlaw)
                else:
                    return rel_str
            elif Ga <= len(_level_name) and (Gb-Ga) < len(_removed_level) and (Ga+Gb+1) < len(_removed_level):
                can = " z %s do %s stupňa (kan.)"  % (
                           _removed_level[Gb], _removed_level[Ga] )
                civ = " a do %s stupňa (civ.)" % ( _removed_level[Ga+Gb+1] )
                if gender_b == Person.MALE:
                    rel_str = "synovec" + can + civ
                if gender_b == Person.FEMALE:
                    rel_str = "neter" + can + civ
                elif gender_b == Person.UNKNOWN:
                    rel_str = self.get_sibling_unknown(Ga, inlaw)
                else:
                    return rel_str
            elif Ga > len(_level_name):
                return rel_str
            else:
                if gender_b == Person.MALE:
                    rel_str = self.get_nephew(Ga, inlaw)
                elif gender_b ==Person.FEMALE:
                    rel_str = self.get_niece(Ga, inlaw)
                elif gender_b == Person.UNKNOWN:
                    rel_str = self.get_sibling_unknown(Ga, inlaw)
                else:
                    return rel_str
        return rel_str

# RelCalc tool - Status Bar

    def get_sibling_relationship_string(self, sib_type, gender_a, gender_b,
                                        in_law_a=False, in_law_b=False):

        if in_law_a or in_law_b :
            inlaw = self.INLAW
        else:
            inlaw = ''

        if sib_type == self.NORM_SIB:
            if not inlaw:
                if gender_b == Person.MALE:
                    rel_str = 'brat (vlastný)'
                elif gender_b == Person.FEMALE:
                    rel_str = 'sestra (vlastná)'
                else:
                    rel_str = 'vlastný brat alebo sestra'
            else:
                if gender_b == Person.MALE:
                    rel_str = "švagor"
                elif gender_b == Person.FEMALE:
                    rel_str = "švagriná"
                else:
                    rel_str = "švagor alebo švagriná"
        elif sib_type == self.UNKNOWN_SIB:
            if not inlaw:
                if gender_b == Person.MALE:
                    rel_str = 'brat'
                elif gender_b == Person.FEMALE:
                    rel_str = 'sestra'
                else:
                    rel_str = 'brat alebo sestra'
            else:
                if gender_b == Person.MALE:
                    rel_str = "švagor"
                elif gender_b == Person.FEMALE:
                    rel_str = "švagriná"
                else:
                    rel_str = "švagor alebo švagriná"
        # oznacenie vyberu spolocny otec, rev.
        elif sib_type == self.HALF_SIB_MOTHER:
            if gender_b == Person.MALE:
                rel_str = "nevlastný brat -spoloč.otec"
            elif gender_b == Person.FEMALE:
                rel_str = "nevlastná sestra -spoloč.otec"
            else:
                rel_str = "nevlastný brat alebo sestra -spoloč.otec"
        # oznacenie vyberu spolocna matka, rev.
        elif sib_type == self.HALF_SIB_FATHER:
            if gender_b == Person.MALE:
                rel_str = "nevlastný brat -spoloč.matka"
            elif gender_b == Person.FEMALE:
                rel_str = "nevlastná sestra -spoloč.matka"
            else:
                rel_str = "nevlastný brat alebo sestra -spoloč.matka"
        elif sib_type == self.STEP_SIB:
            if gender_b == Person.MALE:
                rel_str = "nevlastný brat"
            elif gender_b == Person.FEMALE:
                rel_str = "nevlastná sestra"
            else:
                rel_str = "nevlastný brat alebo sestra"
        return rel_str


if __name__ == "__main__":
    # Test function. Call it as follows from the command line (so as to find
    #        imported modules):
    #    export PYTHONPATH=/path/to/gramps/src
    # python src/plugins/rel/rel_sk.py
    # (Above not needed here)

    """TRANSLATORS, copy this if statement at the bottom of your
        rel_xx.py module, and test your work with:
        python src/plugins/rel/rel_xx.py
    """
    from gramps.gen.relationship import test
    RC = RelationshipCalculator()
    test(RC, True)

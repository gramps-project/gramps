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
# Czech-specific definitions of relationships 
#
#-------------------------------------------------------------------------

_level_name = [ "prvního", "druhého", "třetího", "čtvrtého", "pátého", "šestého",
                "sedmého", "osmého", "devátého", "desátého", "jedenáctého", "dvanáctého",
                "třináctého", "čtrnáctého", "patnáctého", "šestnáctého",
                "sedemnáctého", "osmnáctého", "devatenáctého", "dvacátého", "dvacátého prvního", "dvacátého druhého",
                "dvacátého třetího", "dvacátého čtvrtého","dvacátého pátého","dvacátého šestého","dvacátého sedmého",
                "dvacátého osmého","dvacátého devátého","třicátého" ]


_removed_level = [ "prvního", "druhého", "třetího", "čtvrtého", "pátého", "šestého",
                "sedmého", "osmého", "devátého", "desátého", "jedenáctého", "dvanáctého",
                "třináctého", "čtrnáctého", "patnáctého", "šestnáctého",
                "sedemnáctého", "osmnáctého", "devatenáctého", "dvacátého", "dvacátého prvního", "dvacátého druhého",
                "dvacátého třetího", "dvacátého čtvrtého","dvacátého pátého","dvacátého šestého","dvacátého sedmého",
                "dvacátého osmého","dvacátého devátého","třicátého" ]

# small lists, use generation level if > [5]

_father_level = [ "", "otec%s", "děd%s", "praděd%s", "pra-praděd%s", "prapředek%s", ]

_mother_level = [ "", "matka%s", "babička%s", 
                  "prababička%s", "pra-prababička%s", "prapředek%s", ]

_son_level = [ "", "syn%s", "vnuk%s", "pravnuk%s", "pra-pravnuk%s", ]

_daughter_level = [ "", "dcera%s", "vnučka%s", 
                    "pravnučka%s", "pra-pravnučka%s", ]

_sister_level = [ "", "sestra%s", "teta%s", "prateta%s", "pra-prateta%s", ]

_brother_level = [ "", "bratr%s", "strýc%s", "prastrýc%s", "pra-prastrýc%s", ]

_nephew_level =[ "", "synovec%s", "prasynovec%s", "pra-prasynovec%s", ]

_niece_level =[ "", "neteř%s", "praneteř%s", "pra-praneteř%s", ]

# kinship report

_parents_level = [ "", "rodiče", "prarodiče", 
                    "pra-prarodiče", "předkové", ]

_children_level = [ "", "děti", "vnoučata", 
                    "pravnoučata", 
                    "pra-pravnoučata", ]

_siblings_level = [ "", "bratři a sestry", 
                    "strýcové a tety", 
                    "prastrýcové a pratety", 
                    "pra-prastrýcové a pra-pratety", 
                    ]

_nephews_nieces_level = [ "", "synovci a neteře", 
                          "prasynovci a praneteře", 
                          "pra-prasynovci a pra-praneteře",
                        ]

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------

class RelationshipCalculator(Relationship.RelationshipCalculator):
   
    INLAW = ' (m. svazek)'


    def __init__(self):
        Relationship.RelationshipCalculator.__init__(self)


    def get_cousin(self, level, removed, dir = '', inlaw=''):
        if removed == 0 and level < len(_level_name):
            return "bratranec %s %sstupně" % (_removed_level[level-1],
                                        inlaw)
        elif (level) < (removed):
            rel_str = self.get_uncle(level-1, inlaw)
        else:
            # limitation gen = 29
            return "vzdálený bratranec %s generace" % (
                        _level_name[removed])

    def get_cousine(self, level, removed, dir = '', inlaw=''):
        if removed == 0 and level < len(_level_name):
            return "sestřenice %s %sstupně" % (_level_name[level-1],
                                        inlaw)
        elif (level) < (removed):
            rel_str = self.get_aunt(level-1, inlaw)
        else:
            return "vzdálená sestřenice %s generace" % (
                        _level_name[removed])

    def get_parents(self, level):
        if level > len(_parents_level)-1:
            return "vzdálení předci %s generace" % (
                        _level_name[level])
        else:
            return _parents_level[level]

    def get_father(self, level, inlaw=''):
        if level > len(_father_level)-1:
            return "vzdálený předek %s generace" % (
                        _level_name[level])
        else:
            return _father_level[level] % inlaw

    def get_mother(self, level, inlaw=''):
        if level > len(_mother_level)-1:
            return "vzdálený příbuzný, předek %s generacee" % (
                        _level_name[level])
        else:
            return _mother_level[level] % inlaw

    def get_parent_unknown(self, level, inlaw=''):
        if level > len(_level_name)-1:
            return "vzdálený příbuzný, předek %s generace" % (
                        _level_name[level])
        else:
            return "vzdálený příbuzný%s" % (inlaw)

    def get_son(self, level, inlaw=''):
        if level > len(_son_level)-1:
            return "vzdálený potomek %s generace" % (
                        _level_name[level+1])
        else:
            return _son_level[level] % (inlaw)

    def get_daughter(self, level, inlaw=''):
        if level > len(_daughter_level)-1:
            return "vzdálený potomek %s generace" % (
                        _level_name[level+1])
        else:
            return _daughter_level[level] % (inlaw)

    def get_child_unknown(self, level, inlaw=''):
        if level > len(_level_name)-1:
            return "vzdálený potomek %s generace" % (
                        _level_name[level+1])
        else:
            return "vzdálený potomek%s" % (inlaw)

    def get_sibling_unknown(self, level, inlaw=''):
        return "vzdálený příbuzný%s" % (inlaw)

    def get_uncle(self, level, inlaw=''):
        if level > len(_brother_level)-1:
            return "vzdálený strýc %s generace" % (
                        _level_name[level])
        else:
            return _brother_level[level] % (inlaw)

    def get_aunt(self, level, inlaw=''):
        if level > len(_sister_level)-1:
            return "vzdálená teta %s generace" % (
                        _level_name[level])
        else:
            return _sister_level[level] % (inlaw)

    def get_nephew(self, level, inlaw=''):
        if level > len(_nephew_level)-1:
            return "vzdálený synovec %s generace" % (
                        _level_name[level])
        else:
            return _nephew_level[level] % (inlaw)

    def get_niece(self, level, inlaw=''):
        if level > len(_niece_level)-1:
            return "vzdálená neteř %s generace" % (
                        _level_name[level])
        else:
            return _niece_level[level] % (inlaw)



# kinship report

    def get_plural_relationship_string(self, Ga, Gb):
        """
        see Relationship.py
        """
        rel_str = "vzdálení příbuzní"
        gen = " %s-té generace"
        bygen = " na %-tou generaci"
        cmt = " (bratři nebo sestry předka" + gen % (
                       Ga) + ")"
        if Ga == 0:
            # These are descendants
            if Gb < len(_children_level):
                rel_str = _children_level[Gb]
            else:
                rel_str = "potomci" + gen % (
                               Gb+1)
        elif Gb == 0:
            # These are parents/grand parents
            if Ga < len(_parents_level):
                rel_str = _parents_level[Ga]
            else:
                rel_str = "předci" + gen % (
                               Ga+1) 
        elif Gb == 1:
            # These are siblings/aunts/uncles
            if Ga < len(_siblings_level):
                rel_str = _siblings_level[Ga]
            else:
                rel_str = "děti předka" + gen % (
                               Ga+1) + cmt 
        elif Ga == 1:
            # These are nieces/nephews
            if Gb < len(_nephews_nieces_level):
                rel_str = _nephews_nieces_level[Gb-1]
            else:
                rel_str = "synovci a neteře" + gen % (
                               Gb)
        elif Ga > 1 and Ga == Gb:
            # These are cousins in the same generation
            # use custom level for latin words
            if Ga == 2:
                rel_str = "vlastní bratranci a sestřenice" 
            elif Ga <= len(_level_name):
                # %ss for plural
                rel_str = " %ss bratranci a sestřenice" % _level_name[Ga-2]
            # security    
            else:
                rel_str = "bratranci a sestřenice"
        elif Ga > 1 and Ga > Gb:
            # These are cousins in different generations with the second person 
            # being in a higher generation from the common ancestor than the 
            # first person.
            # use custom level for latin words and specific relation
            if Ga == 3 and Gb == 2:
                desc = " (vlastní bratranci některého z rodičů)"
                rel_str = "strýcové a tety z dalšího kolene" + desc
            elif Gb <= len(_level_name) and (Ga-Gb) < len(_removed_level) and (Ga+Gb+1) < len(_removed_level):
                can = " od %s do %s stupně (kan.)"  % (
                           _removed_level[Gb], _removed_level[Ga] )
                civ = " a do %s stupně (civ.)" % ( _removed_level[Ga+Gb+1] )
                rel_str = "strýcové a tety" + can + civ
            elif Ga < len(_level_name):
                rel_str = "prastrýcové a pratety" + bygen % (
                               Ga+1)
            else:
                return rel_str
        elif Gb > 1 and Gb > Ga:
            # These are cousins in different generations with the second person 
            # being in a lower generation from the common ancestor than the 
            # first person.
            # use custom level for latin words and specific relation
            if Ga == 2 and Gb == 3:
                info = " (potomek bratrance-sestřenice)"
                rel_str = "synovci a neteře z dalšího kolene" + info
            elif Ga <= len(_level_name) and (Gb-Ga) < len(_removed_level) and (Ga+Gb+1) < len(_removed_level):
                can = " od %s do %s stupně (kan.)"  % (
                           _removed_level[Gb], _removed_level[Ga] )
                civ = " a do %s stupně (civ.)" % ( _removed_level[Ga+Gb+1] )
                rel_str = "synovci a neteře" + can + civ
            elif Ga < len(_level_name):
                rel_str =  "synovci a neteře" + bygen % (
                                Gb)
            else:
                return rel_str
        return rel_str


# quick report (missing on RelCalc tool - Status Bar)

    def get_single_relationship_string(self, Ga, Gb, gender_a, gender_b,
                                       reltocommon_a, reltocommon_b,
                                       only_birth=True, 
                                       in_law_a=False, in_law_b=False):
        """
        see Relationship.py
        """
        if only_birth:
            step = ''
        else:
            step = self.STEP

        if in_law_a or in_law_b :
            inlaw = self.INLAW
        else:
            inlaw = ''      
        
        
        rel_str = "vzdálený příbuznýs%s" % (inlaw)
        bygen = " %s generace"
        if Ga == 0:
            # b is descendant of a
            if Gb == 0 :
                rel_str = 'stejná osoba'
            elif gender_b == gen.lib.Person.MALE and Gb < len(_son_level):
                # spouse of daughter
                if inlaw and Gb == 1 and not step:
                    rel_str = "zeť"
                else:
                    rel_str = self.get_son(Gb)
            elif gender_b == gen.lib.Person.FEMALE and Gb < len(_daughter_level):
                # spouse of son
                if inlaw and Gb == 1 and not step:
                    rel_str = "nevěsta"
                else:
                    rel_str = self.get_daughter(Gb)
            # don't display inlaw
            elif Gb < len(_level_name) and gender_b == gen.lib.Person.MALE:
                rel_str = "vzdálený potomek (%d generace)" % (
                               Gb+1)
            elif Gb < len(_level_name) and gender_b == gen.lib.Person.FEMALE:
                rel_str = "vzdálený potomek(žena) (%d generace)" % (
                               Gb+1)
            else:
                return self.get_child_unknown(Gb)
        elif Gb == 0:
            # b is parents/grand parent of a
            if gender_b == gen.lib.Person.MALE and Ga < len(_father_level):
                # other spouse of father (new parent)
                if Ga == 1 and inlaw and self.STEP_SIB:
                    rel_str = "švagr"
                # father of spouse (family of spouse)
                elif Ga == 1 and inlaw:
                    rel_str = "otec partnera"
                else:
                    rel_str = self.get_father(Ga, inlaw)
            elif gender_b == gen.lib.Person.FEMALE and Ga < len(_mother_level):
                # other spouse of mother (new parent)
                if Ga == 1 and inlaw and self.STEP_SIB:
                    rel_str = "švagrová"
                # mother of spouse (family of spouse)
                elif Ga == 1 and inlaw:
                    rel_str = "matka partnera"
                else:
                    rel_str = self.get_mother(Ga, inlaw)
            elif Ga < len(_level_name) and gender_b == gen.lib.Person.MALE:
                rel_str = "vzdálený předek%s (%d generace)" % (
                               inlaw, Ga+1)
            elif Ga < len(_level_name) and gender_b == gen.lib.Person.FEMALE:
                rel_str = "vzdálený předek(žena)%s (%d generace)" % (
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
                    rel_str = "vzdálený strýc" + bygen % (
                                   Ga+1)
                elif gender_b == gen.lib.Person.FEMALE:
                    rel_str = "vzdálená teta" + bygen % (
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
                    rel_str = "vzdálený synovec%s (%d generace)" %  (
                                   inlaw, Gb)
                elif gender_b == gen.lib.Person.FEMALE:
                    rel_str = "vzdálená neteř%s (%d generace)" %  (
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
                    desc = " (bratranec některého z rodičů)"
                    rel_str = "strýc z druhého kolene" + desc
                elif gender_b == gen.lib.Person.FEMALE: 
                    desc = " (sestřenice některého z rodičů)"
                    rel_str = "teta z druhého kolene" + desc
                elif gender_b == gen.lib.Person.UNKNOWN: 
                    return self.get_sibling_unknown(Ga, inlaw)
                else:
                    return rel_str
            elif Gb <= len(_level_name) and (Ga-Gb) < len(_removed_level) and (Ga+Gb+1) < len(_removed_level):
                can = " od %s do %s stupně (kan.)"  % (
                           _removed_level[Gb], _removed_level[Ga] )
                civ = " a do %s stupně (civ.)" % ( _removed_level[Ga+Gb+1] )
                if gender_b == gen.lib.Person.MALE:
                    rel_str = "strýc" + can + civ
                elif gender_b == gen.lib.Person.FEMALE:
                    rel_str = "teta" + can + civ
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
                info = " (potomek bratrance/sestřenice)"
                if gender_b == gen.lib.Person.MALE:   
                    rel_str = "synovec z druhého kolene" + info
                elif gender_b == gen.lib.Person.FEMALE:
                    rel_str = "neteř z druhého kolene" + info
                elif gender_b == gen.lib.Person.UNKNOWN:
                    rel_str = self.get_sibling_unknown(Ga, inlaw)
                else:
                    return rel_str  
            elif Ga <= len(_level_name) and (Gb-Ga) < len(_removed_level) and (Ga+Gb+1) < len(_removed_level):
                can = " od %s do %s stupně (kan.)"  % (
                           _removed_level[Gb], _removed_level[Ga] )
                civ = " a do %s stupně (civ.)" % ( _removed_level[Ga+Gb+1] )
                if gender_b == gen.lib.Person.MALE:
                    rel_str = "synovec" + can + civ
                if gender_b == gen.lib.Person.FEMALE:
                    rel_str = "neteř" + can + civ
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

# RelCalc tool - Status Bar

    def get_sibling_relationship_string(self, sib_type, gender_a, gender_b, 
                                        in_law_a=False, in_law_b=False):

        if in_law_a or in_law_b :
            inlaw = self.INLAW
        else:
            inlaw = ''
        
        if sib_type == self.NORM_SIB:
            if not inlaw:
                if gender_b == gen.lib.Person.MALE:
                    rel_str = 'brat (vlastní)'
                elif gender_b == gen.lib.Person.FEMALE:
                    rel_str = 'sestra (vlastní)'
                else:
                    rel_str = 'vlastní bratr nebo sestra'
            else:
                if gender_b == gen.lib.Person.MALE:
                    rel_str = "švagr"
                elif gender_b == gen.lib.Person.FEMALE:
                    rel_str = "švagrová"
                else:
                    rel_str = "švagr nebo švagrová"
        elif sib_type == self.UNKNOWN_SIB:
            if not inlaw:
                if gender_b == gen.lib.Person.MALE:
                    rel_str = 'bratr'
                elif gender_b == gen.lib.Person.FEMALE:
                    rel_str = 'sestra'
                else:
                    rel_str = 'bratr alebo sestra'
            else:
                if gender_b == gen.lib.Person.MALE:
                    rel_str = "švagr"
                elif gender_b == gen.lib.Person.FEMALE:
                    rel_str = "švagrová"
                else:
                    rel_str = "švagr nebo švagrová"
        elif sib_type == self.HALF_SIB_MOTHER:
            if gender_b == gen.lib.Person.MALE:
                rel_str = "nevlastní bratr -společný otec"
            elif gender_b == gen.lib.Person.FEMALE:
                rel_str = "nevlastní sestra -společný otec"
            else:
                rel_str = "nevlastní bratr nebo sestra - společný otec"
        elif sib_type == self.HALF_SIB_FATHER:
            if gender_b == gen.lib.Person.MALE:
                rel_str = "nevlastní bratr -společná matka"
            elif gender_b == gen.lib.Person.FEMALE:
                rel_str = "nevlastní sestra -společná matka"
            else:
                rel_str = "nevlastní bratr nebo sestra - společná matka"
        elif sib_type == self.STEP_SIB:
            if gender_b == gen.lib.Person.MALE:
                rel_str = "nevlastní bratr"
            elif gender_b == gen.lib.Person.FEMALE:
                rel_str = "nevlastní sestra"
            else:
                rel_str = "nevlastní bratr nebo sestra"
        return rel_str


#-------------------------------------------------------------------------
#
# Register this class with the Plugins system 
#
#-------------------------------------------------------------------------
pmgr = PluginManager.get_instance()
pmgr.register_relcalc(RelationshipCalculator, 
    ["cs", "CZ", "cs_CZ", "česky", "czech", "Czech", "cs_CZ.UTF8", "cs_CZ.UTF-8", "cs_CZ.utf-8", "cs_CZ.utf8"])


if __name__ == "__main__":
    # Test function. Call it as follows from the command line (so as to find
    #        imported modules):
    #    export PYTHONPATH=/path/to/gramps/src 
    # python src/plugins/rel/rel_cs.py 
    # (Above not needed here)
    
    """TRANSLATORS, copy this if statement at the bottom of your 
        rel_xx.py module, and test your work with:
        python src/plugins/rel_xx.py
    """
    from Relationship import test
    rc = RelationshipCalculator()
    test(rc, True)

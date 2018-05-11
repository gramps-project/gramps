# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2006  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2010       Andrew I Baznikin
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

# Czech terms added by Zdeněk Hataš. Based on rel_sk.py by  Lubo Vasko
"""
Czech-specific classes for relationships.
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
# Czech-specific definitions of relationships
#
#-------------------------------------------------------------------------

_level_name = [ "", "prvního", "druhého", "třetího", "čtvrtého", "pátého", "šestého",
                "sedmého", "osmého", "devátého", "desátého", "jedenáctého", "dvanáctého",
                "třináctého", "čtrnáctého", "patnáctého", "šestnáctého",
                "sedemnáctého", "osmnáctého", "devatenáctého", "dvacátého", "dvacátého prvního", "dvacátého druhého",
                "dvacátého třetího", "dvacátého čtvrtého","dvacátého pátého","dvacátého šestého","dvacátého sedmého",
                "dvacátého osmého","dvacátého devátého","třicátého" ]

_parents_level = [ "", "rodiče", "prarodiče", "praprarodiče",
                   "vzdálení příbuzní", ]

_father_level = [ "", "otec", "děd", "praděd", "prapředek", ]

_mother_level = [ "", "matka", "babička", "prababička", "prapředek", ]

_son_level = [ "", "syn", "vnuk", "pravnuk", ]

_daughter_level = [ "", "dcera", "vnučka", "pravnučka", ]

_sister_level = [ "", "sestra", "teta", "prateta", "praprateta", ]

_brother_level = [ "", "bratr", "strýc", "prastrýc", "praprastrýc", ]

_nephew_level = [ "", "synovec", "prasynovec", "praprasynovec", ]

_niece_level = [ "", "neteř", "praneteř", "prapraneteř", ]

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class RelationshipCalculator(gramps.gen.relationship.RelationshipCalculator):
    """
    RelationshipCalculator Class
    """

    def __init__(self):
        gramps.gen.relationship.RelationshipCalculator.__init__(self)

    def get_male_cousin(self, level):
        if level > len(_level_name)-1:
            return "vzdálený příbuzný"
        else:
            return "bratranec %s stupně" % (_level_name[level])

    def get_female_cousin(self, level):
        if level > len(_level_name)-1:
            return "vzdálená příbuzná"
        else:
            return "sestřenice %s stupně" % (_level_name[level])

    def get_parents(self, level):
        if level > len(_parents_level)-1:
            return "vzdálení příbuzní"
        else:
            return _parents_level[level]

    def get_father(self, level):
        if level > len(_father_level)-1:
            return "vzdálený příbuzný"
        else:
            return _father_level[level]

    def get_son(self, level):
        if level > len(_son_level)-1:
            return "vzdálený potomek"
        else:
            return _son_level[level]

    def get_mother(self, level):
        if level > len(_mother_level)-1:
            return "vzdálený předek"
        else:
            return _mother_level[level]

    def get_daughter(self, level):
        if level > len(_daughter_level)-1:
            return "vzdálený potomek"
        else:
            return _daughter_level[level]

    def get_aunt(self, level):
        if level > len(_sister_level)-1:
            return "vzdálený předek"
        else:
            return _sister_level[level]

    def get_uncle(self, level):
        if level > len(_brother_level)-1:
            return "vzdálený předek"
        else:
            return _brother_level[level]

    def get_nephew(self, level):
        if level > len(_nephew_level)-1:
            return "vzdálený potomek"
        else:
            return _nephew_level[level]

    def get_niece(self, level):
        if level > len(_niece_level)-1:
            return "vzdálený potomek"
        else:
            return _niece_level[level]

    def get_relationship(self, secondRel, firstRel, orig_person_gender, other_person_gender):
        """
        Return a string representing the relationshp between the two people,
        along with a list of common ancestors (typically father,mother)

        Special cases: relation strings "", "undefined" and "spouse".
        """

        common = ""
        if firstRel == 0:
            if secondRel == 0:
                return ('', common)
            elif other_person_gender == Person.MALE:
                return (self.get_father(secondRel), common)
            else:
                return (self.get_mother(secondRel), common)
        elif secondRel == 0:
            if other_person_gender == Person.MALE:
                return (self.get_son(firstRel), common)
            else:
                return (self.get_daughter(firstRel), common)
        elif firstRel == 1:
            if other_person_gender == Person.MALE:
                return (self.get_uncle(secondRel), common)
            else:
                return (self.get_aunt(secondRel), common)
        elif secondRel == 1:
            if other_person_gender == Person.MALE:
                return (self.get_nephew(firstRel-1), common)
            else:
                return (self.get_niece(firstRel-1), common)
        elif firstRel == secondRel == 2:
            if other_person_gender == Person.MALE:
                return ('vlastní bratranec', common)
            else:
                return ('vlastní sestřenice', common)
        elif firstRel == 3 and secondRel == 2:
            if other_person_gender == Person.MALE:
                return ('bratranec druhého stupně', common)
            else:
                return ('sestřenice druhého stupně', common)
        elif firstRel == 2 and secondRel == 3:
            if other_person_gender == Person.MALE:
                return ('bratranec druhého stupně', common)
            else:
                return ('sestřenice druhého stupně', common)
        else:
            if other_person_gender == Person.MALE:
                if firstRel+secondRel > len(_level_name)-1:
                    return (self.get_male_cousin(firstRel+secondRel), common)
                else:
                    return ('vzdálený bratranec', common)
            else:
                if firstRel+secondRel > len(_level_name)-1:
                    return (self.get_female_cousin(firstRel+secondRel), common)
                else:
                    return ('vzdálená sestřenice', common)

    def get_single_relationship_string(self, Ga, Gb, gender_a, gender_b,
                                       reltocommon_a, reltocommon_b,
                                       only_birth=True,
                                       in_law_a=False, in_law_b=False):
        return self.get_relationship(Ga, Gb, gender_a, gender_b)[0];

    def get_sibling_relationship_string(self, sib_type, gender_a, gender_b,
                                        in_law_a=False, in_law_b=False):
        return self.get_relationship(1, 1, gender_a, gender_b)[0];

if __name__ == "__main__":

    # Test function. Call it as follows from the command line (so as to find
    #        imported modules):
    #    export PYTHONPATH=/path/to/gramps/src
    # python src/plugins/rel/rel_cs.py
    # (Above not needed here)

    """TRANSLATORS, copy this if statement at the bottom of your
        rel_xx.py module, and test your work with:
        python src/plugins/rel/rel_xx.py
    """
    from gramps.gen.relationship import test
    RC = RelationshipCalculator()
    test(RC, True)

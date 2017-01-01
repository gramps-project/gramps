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

#
# Written by Egyeki Gergely <egeri@elte.hu>, 2004
"""
Specific classes for relationships.
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
# Shared constants
#
#-------------------------------------------------------------------------

_level = \
    ["", "", "másod", "harmad", "negyed", "ötöd", "hatod",
     "heted", "nyolcad", "kilenced", "tized", "tizenegyed", "tizenketted",
     "tizenharmad", "tizennegyed", "tizenötöd", "tizenhatod",
     "tizenheted", "tizennyolcad", "tizenkilenced", "huszad","huszonegyed"]


#-------------------------------------------------------------------------
#
# Specific relationship functions
#
#-------------------------------------------------------------------------
class RelationshipCalculator(gramps.gen.relationship.RelationshipCalculator):
    """
    RelationshipCalculator Class
    """

    def __init__(self):
        gramps.gen.relationship.RelationshipCalculator.__init__(self)


    def get_parents (self, level):
        if   level == 0: return ""
        elif level == 1: return "szülei"
        elif level == 2: return "nagyszülei"
        elif level == 3: return "dédszülei"
        elif level == 4: return "ükszülei"
        else: return "%d. szülei" % level

    def get_father (self, level):
        if   level == 0: return ""
        elif level == 1: return "apja"
        elif level == 2: return "nagyapja"
        elif level == 3: return "dédapja"
        elif level == 4: return "ükapja"
        else: return "%d. ükapja" % level

    def get_mother (self, level):
        if   level == 0: return ""
        elif level == 1: return "anyja"
        elif level == 2: return "nagyanyja"
        elif level == 3: return "dédanyja"
        elif level == 4: return "ükanyja"
        else: return "%d. ükanyja" % level

    def get_son (self, level):
        if   level == 0: return ""
        elif level == 1: return "fia"
        elif level == 2: return "unokája"
        elif level == 3: return "dédunokája"
        elif level == 4: return "ükunokája"
        else: return "%d. unokája" % level

    def get_daughter (self, level):
        if   level == 0: return ""
        elif level == 1: return "lánya"
        elif level <= len([level]): return self.get_son(level)

    def get_uncle (self, level):
        if   level == 0: return ""
        elif level == 1: return "testvére"
        elif level == 2: return "nagybátyja"
        else: return "%d. nagybátyja" % level

    def get_aunt (self, level):
        if   level == 0: return ""
        elif level == 1: return "testvére"
        elif level == 2: return "nagynénje"
        else: return "%d. nagynénje" % level

    def get_nephew (self, level):
        if   level == 0: return ""
        elif level == 1: return "unokája"
        else: return "%d. unokája" % level

    def get_niece(self, level):
        return self.get_nephew(level)

    def get_male_cousin (self, level):
        if   level == 0: return ""
        elif level == 1: return "unokatestvére"
        else: return "%d. unokatestvére" % level

    def get_female_cousin (self, level):
        return self.get_male_cousin(level)

    #----------------------------------------------
    #
    # brother and sister age differences
    #
    #----------------------------------------------

    def get_age_comp(self, orig_person, other_person):
        # in 3.X api we can't know persons age
        return 0


    def get_age_brother (self, level):
        if   level == 0  : return "testvére"
        elif level == 1  : return "öccse"
        else             : return "bátyja"

    def get_age_sister (self, level):
        if   level == 0  : return "testvére"
        elif level == 1  : return "húga"
        else             : return "nővére"

    #---------------------------------------------
    #
    # en: father-in-law, mother-in-law, son-in-law, daughter-in-law
    # hu: após, anyós, vő, meny
    #
    #---------------------------------------------

    # FIXME: is it still used?
    def is_fathermother_in_law(self, db, orig, other):
        for f in other.get_family_handle_list():
            family = db.get_family_from_handle(f)
            sp_id = None
            if family:
                if other == family.get_father_handle():
                    sp_id = family.get_mother_handle()
                elif other == family.get_mother_handle():
                    sp_id = family.get_father_handle()
                for g in orig.get_family_handle_list():
                    family = db.get_family_from_handle(g)
                    if family:
                        if sp_id in family.get_child_handle_list():
                            return 1
        return 0

    #------------------------------------------------------------------------
    #
    # hu: sógor, sógornő
    # en: brother-in-law, sister-in-law
    #
    #------------------------------------------------------------------------

    # FIXME: is it still used?
    def is_brothersister_in_law(self, db, orig, other):
        for f in orig.get_family_handle_list():
            family = db.get_family_from_handle(f)
            sp_id = None
            if family:
                if orig ==  family.get_father_handle():
                    sp_id = family.get_mother_handle()
                elif other == family.get_mother_handle():
                    sp_id = family.get_father_handler()

                p = other.get_main_parents_family_handle()
                family = db.get_family_from_handle(p)
                if family:
                    c = family.get_child_handle_list()
                    if (other.get_handle() in c) and (sp_id in c):
                        return 1
        return 0

    #-------------------------------------------------------------------------
    #
    # get_relationship
    #
    #-------------------------------------------------------------------------

    def get_relationship(self, secondRel, firstRel, orig_person, other_person, in_law_a, in_law_b):
        """
        returns a string representing the relationshp between the two people,
        along with a list of common ancestors (typically father,mother)
        """

        common = ""

        if in_law_a or in_law_a:
            if firstRel == 0 and secondRel == 0:
                if other_person == Person.MALE:
                    return ("apósa","")
                elif other_person == Person.FEMALE:
                    return ("anyósa","")
                else:
                    return ("apósa vagy anyósa","")

            elif secondRel == 0:
                if orig_person == Person.MALE:
                    return ("veje","")
                elif orig_person == Person.FEMALE:
                    return ("menye","")
                else:
                    return ("veje vagy menye","")

            elif firstRel == 1:
                if other_person == Person.MALE:
                    return ("sógora","")
                elif other_person == Person.FEMALE:
                    return ("sógornője","")
                else:
                    return ("sógora vagy sógornője","")

        if firstRel == 0:
            if secondRel == 0:
                return ('', common)
            elif other_person == Person.MALE:
                return (self.get_father(secondRel), common)
            else:
                return (self.get_mother(secondRel), common)

        elif secondRel == 0:
            if other_person == Person.MALE:
                return (self.get_son(firstRel), common)
            else:
                return (self.get_daughter(firstRel), common)

        elif firstRel == 1:
            if other_person == Person.MALE:
                if secondRel == 1:
                    return (self.get_age_brother(self.get_age_comp(orig_person, other_person)), common)
                else :return (self.get_uncle(secondRel), common)
            else:
                if secondRel == 1:
                    return (self.get_age_sister(self.get_age_comp(orig_person, other_person)), common)
                else :return (self.get_aunt(secondRel), common)

        elif secondRel == 1:
            if other_person == Person.MALE:
                return (self.get_nephew(firstRel-1), common)
            else:
                return (self.get_niece(firstRel-1), common)

        else:
            if other_person == Person.MALE:
                return (self.get_male_cousin(firstRel-1), common)
            else:
                return (self.get_female_cousin(firstRel-1), common)

    def get_single_relationship_string(self, Ga, Gb, gender_a, gender_b,
                                       reltocommon_a, reltocommon_b,
                                       only_birth=True,
                                       in_law_a=False, in_law_b=False):
        return self.get_relationship(Ga, Gb, gender_a, gender_b, in_law_a, in_law_b)[0]

    def get_sibling_relationship_string(self, sib_type, gender_a, gender_b,
                                        in_law_a=False, in_law_b=False):
        return self.get_relationship(1, 1, gender_a, gender_b, in_law_a, in_law_b)[0]

if __name__ == "__main__":

    # Test function. Call it as follows from the command line (so as to find
    #        imported modules):
    #    export PYTHONPATH=/path/to/gramps/src
    # python src/plugins/rel/rel_hu.py
    # (Above not needed here)

    """TRANSLATORS, copy this if statement at the bottom of your
        rel_xx.py module, and test your work with:
        python src/plugins/rel/rel_xx.py
    """
    from gramps.gen.relationship import test
    RC = RelationshipCalculator()
    test(RC, True)

# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2005  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2018       Robin van der Vliet
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
#
#
#-------------------------------------------------------------------------

_ordinal_level = [ "",
    "eerste", "tweede", "derde", "vierde", "vijfde",
    "zesde", "zevende", "achtste", "negende", "tiende",
    "elfde", "twaalfde", "dertiende", "veertiende", "vijftiende",
    "zestiende", "zeventiende", "achttiende", "negentiende", "twintigste",
    "eenentwintigste", "tweeëntwintigste", "drieëntwintigste", "vierentwintigste", "vijfentwintigste",
    "zesentwintigste", "zevenentwintigste", "achtentwintigste", "negenentwintigste", "dertigste",
    "eenendertigste", "tweeëndertigste", "drieëndertigste", "vierendertigste", "vijfendertigste",
    "zesendertigste", "zevenendertigste", "achtendertigste", "negenendertigste", "veertigste",
    "eenenveertigste", "tweeënveertigste", "drieënveertigste", "vierenveertigste", "vijfenveertigste",
    "zesenveertigste", "zevenenveertigste", "achtenveertigste", "negenenveertigste", "vijftigste" ]

_removed_level = [ "", "",
    "groot", "overgroot", "betovergroot", "oud", "oudgroot",
    "oudovergroot", "oudbetovergroot", "stam", "stamgroot", "stamovergroot",
    "stambetovergroot", "stamoud", "stamoudgroot", "stamoudovergroot", "stamoudbetovergroot",
    "edel", "edelgroot", "edelovergroot", "edelbetovergroot", "edeloud",
    "edeloudgroot", "edeloudovergroot", "edeloudbetovergroot", "edelstam", "edelstamgroot",
    "edelstamovergroot", "edelstambetovergroot", "edelstamoud", "edelstamoudgroot", "edelstamoudovergroot",
    "edelstamoudbetovergroot", "voor", "voorgroot", "voorovergroot", "voorbetovergroot",
    "vooroud", "vooroudgroot", "vooroudovergroot", "vooroudbetovergroot", "voorstam",
    "voorstamgroot", "voorstamovergroot", "voorstambetovergroot", "voorstamoud", "voorstamoudgroot",
    "voorstamoudovergroot", "voorstamoudbetovergroot", "vooredel" ]

_child_level = [ "", "",
    "klein", "achterklein", "achterachterklein" ]

_nibling_level = [ "", "",
    "achter", "achterachter", "achterachterachter" ]

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------

class RelationshipCalculator(gramps.gen.relationship.RelationshipCalculator):
    """
    RelationshipCalculator Class
    """

    #sibling strings
    STEP = "stief"
    HALF = "half"

    INLAW = "aangetrouwde "

    def __init__(self):
        gramps.gen.relationship.RelationshipCalculator.__init__(self)

    def get_parents(self, level):
        if level > len(_removed_level)-1:
            return "verre voorouders (%d generaties)" % level
        elif level > 4:
            return "%souders (%d generaties)" % (_removed_level[level], level)
        else:
            return "%souders" % _removed_level[level]

    def _get_father(self, level, step="", inlaw=""):
        """Internal Dutch method to create relation string
        """
        if level > len(_removed_level)-1:
            return "verre %s%svoorvader (%d generaties)" % (inlaw, step, level)
        elif level > 4:
            return "%s%s%svader (%d generaties)" % (inlaw, step, _removed_level[level], level)
        else:
            return "%s%s%svader" % (inlaw, step, _removed_level[level])

    def _get_son(self, level, step="", inlaw=""):
        """Internal Dutch method to create relation string
        """
        if level > len(_child_level)-1:
            return "verre %s%sachterkleinzoon (%d generaties)" % (inlaw, step, level)
        else:
            return "%s%s%szoon" % (inlaw, step, _child_level[level])

    def _get_mother(self, level, step="", inlaw=""):
        """Internal Dutch method to create relation string
        """
        if level > len(_removed_level)-1:
            return "verre %s%svoormoeder (%d generaties)" % (inlaw, step, level)
        elif level > 4:
            return "%s%s%smoeder (%d generaties)" % (inlaw, step, _removed_level[level], level)
        else:
            return "%s%s%smoeder" % (inlaw, step, _removed_level[level])

    def _get_daughter(self, level, step="", inlaw=""):
        """Internal Dutch method to create relation string
        """
        if level > len(_child_level)-1:
            return "verre %s%sachterkleindochter (%d generaties)" % (inlaw, step, level)
        else:
            return "%s%s%sdochter" % (inlaw, step, _child_level[level])

    def _get_parent_unknown(self, level, step="", inlaw=""):
        """Internal Dutch method to create relation string
        """
        if level > len(_removed_level)-1:
            return "verre %s%svoorouder (%d generaties)" % (inlaw, step, level)
        elif level > 4:
            return "%s%s%souder (%d generaties)" % (inlaw, step, _removed_level[level], level)
        else:
            return "%s%s%souder" % (inlaw, step, _removed_level[level])

    def _get_child_unknown(self, level, step="", inlaw=""):
        """Internal Dutch method to create relation string
        """
        if inlaw == "aangetrouwde ":
            #The word "kind" is grammatically neuter, so it has a different adjective.
            inlaw = "aangetrouwd "

        if level > len(_child_level)-1:
            return "ver %s%sachterkleinkind (%d generaties)" % (inlaw, step, level)
        else:
            return "%s%s%skind" % (inlaw, step, _child_level[level])

    def _get_aunt(self, level, removed, step="", inlaw=""):
        """Internal Dutch method to create relation string
        """
        if removed == 1 and level < len(_removed_level):
            if level > 4:
                return "%s%s%stante (%d generaties)" % (inlaw, step, _removed_level[level], level)
            else:
                return "%s%s%stante" % (inlaw, step, _removed_level[level])
        elif removed == 1:
            return "verre %s%stante (%d generaties)" % (inlaw, step, level)
        elif level > len(_removed_level)-1 and removed > len(_ordinal_level)-1:
            return "verre %s%stante (%d generaties, %d graden)" % (inlaw, step,
                                                            level, removed)
        elif level > len(_removed_level)-1:
            return "verre %s%stante van de %s graad (%d generaties)" % (inlaw,
                                        step, _ordinal_level[removed], level)
        else:
            if level > 4:
                return "%s%s%stante (%d generaties)" % (inlaw, step, _removed_level[level], level) \
                        + " " + _ordinal_level[removed] + " graad"
            else:
                return "%s%s%stante" % (inlaw, step, _removed_level[level]) \
                        + " " + _ordinal_level[removed] + " graad"

    def _get_uncle(self, level, removed, step="", inlaw=""):
        """Internal Dutch method to create relation string
        """
        if removed == 1 and level < len(_removed_level):
            if level > 4:
                return "%s%s%soom (%d generaties)" % (inlaw, step, _removed_level[level], level)
            else:
                return "%s%s%soom" % (inlaw, step, _removed_level[level])
        elif removed == 1:
            return "verre %s%soom (%d generaties)" % (inlaw, step, level)
        elif level > len(_removed_level)-1 and removed > len(_ordinal_level)-1:
            return "verre %s%soom (%d generaties, %d graden)" % (inlaw, step,
                                                            level, removed)
        elif level > len(_removed_level)-1:
            return "verre %s%soom van de %s graad (%d generaties)" % (inlaw,
                                        step, _ordinal_level[removed], level)
        else:
            if level > 4:
                return "%s%s%soom (%d generaties)" % (inlaw, step, _removed_level[level], level) \
                        + " " + _ordinal_level[removed] + " graad"
            else:
                return "%s%s%soom" % (inlaw, step, _removed_level[level]) \
                        + " " + _ordinal_level[removed] + " graad"

    def _get_sibling(self, level, step="", inlaw=""):
        """overwrite of English method to return unknown gender sibling
        """
        assert(level == 1)
        return self._get_male_cousin(0, step=step, inlaw=inlaw) + " of " \
                + self._get_female_cousin(0, step=step, inlaw=inlaw)

    def _get_nephew(self, level, removed=1, step="", inlaw=""):
        """Internal Dutch method to create relation string
        """
        if removed == 1 and level < len(_nibling_level):
            return "%s%s%sneef" % (inlaw, step, _nibling_level[level])
        elif removed == 1:
            return "verre %s%sneef (%d generaties)" % (inlaw, step, level)
        elif level > len(_nibling_level)-1 and removed > len(_ordinal_level) -1:
            return "verre %s%sneef (%d generaties, %d graden)" % (inlaw, step,
                                                                level, removed)
        elif level > len(_nibling_level)-1:
            return "verre %s%sneef van de %s graad (%d generaties)" % (inlaw, step,
                                                _ordinal_level[removed], level)
        else:
            return "%s%s%sneef" % (inlaw, step, _nibling_level[level]) \
                        + " " + _ordinal_level[removed] + " graad"

    def _get_niece(self, level, removed=1, step="", inlaw=""):
        """Internal Dutch method to create relation string
        """
        if removed == 1 and level < len(_nibling_level):
            return "%s%s%snicht" % (inlaw, step, _nibling_level[level])
        elif removed == 1:
            return "verre %s%snicht (%d generaties)" % (inlaw, step, level)
        elif level > len(_nibling_level)-1 and removed > len(_ordinal_level) -1:
            return "verre %s%snicht (%d generaties, %d graden)" % (inlaw, step,
                                                                level, removed)
        elif level > len(_nibling_level)-1:
            return "verre %s%snicht van de %s graad (%d generaties)" % (inlaw, step,
                                                _ordinal_level[removed], level)
        else:
            return "%s%s%snicht" % (inlaw, step, _nibling_level[level]) \
                        + " " + _ordinal_level[removed] + " graad"

    def _get_male_cousin(self, removed, step="", inlaw=""):
        """Specific Dutch thing, the nieces/nephews on same level are called
            going sideways in a branch as the nieces/newphews going downward
            from your brother/sisters. This used to be called "kozijn"
        """
        removed -= 1
        if removed > len(_ordinal_level)-1:
            return "verre %s%sneef (kozijn, %d graden)" % (inlaw, step,
                                                           removed)
        elif removed == 0:
            return "%s%sbroer" % (inlaw, step)
        else:
            return "%s%sneef (kozijn)" % (inlaw, step) \
                        + " " + _ordinal_level[removed] + " graad"

    def _get_female_cousin(self, removed, step="", inlaw=""):
        """Specific Dutch thing, the nieces/nephews on same level are called
            going sideways in a branch as the nieces/newphews going downward
            from your brother/sisters. This used to be called "kozijn"
        """
        removed -= 1
        if removed > len(_ordinal_level)-1:
            return "verre %s%snicht (kozijn, %d graden)" % (inlaw, step,
                                                           removed)
        elif removed == 0:
            return "%s%szus" % (inlaw, step)
        else:
            return "%s%snicht (kozijn)" % (inlaw, step) \
                        + " " + _ordinal_level[removed] + " graad"

    def get_single_relationship_string(self, Ga, Gb, gender_a, gender_b,
                                       reltocommon_a, reltocommon_b,
                                       only_birth=True,
                                       in_law_a=False, in_law_b=False):
        """
        Return a string representing the relationship between the two people,
        see english method, eg b is father of a
        """
        if only_birth:
            step = ""
        else:
            step = self.STEP

        if in_law_a or in_law_b :
            inlaw = self.INLAW
        else:
            inlaw = ""

        rel_str = "verre %s%sfamilie" % (inlaw, step)

        if Gb == 0:
            #b is ancestor
            if Ga == 0:
                rel_str = "zelfde persoon"
            elif Ga == 1 and inlaw and not step:
                if gender_b == Person.MALE:
                    rel_str = "schoonvader"
                elif gender_b == Person.FEMALE:
                    rel_str = "schoonmoeder"
                else:
                    rel_str = "schoonouder"
            elif gender_b == Person.MALE:
                rel_str = self._get_father(Ga, step, inlaw)
            elif gender_b == Person.FEMALE:
                rel_str = self._get_mother(Ga, step, inlaw)
            else:
                rel_str = self._get_parent_unknown(Ga, step, inlaw)
        elif Ga == 0:
            #a is descendant
            if Gb == 1 and inlaw and not step:
                if gender_b == Person.MALE:
                    rel_str = "schoonzoon"
                elif gender_b == Person.FEMALE:
                    rel_str = "schoondochter"
                else:
                    rel_str = "schoonkind"
            elif Gb == 1 and inlaw and step:
                #inlaw stepchild
                if gender_b == Person.MALE:
                    rel_str = "aangetrouwde stiefzoon"
                elif gender_b == Person.FEMALE:
                    rel_str = "aangetrouwde stiefdochter"
                else:
                    rel_str = "aangetrouwd stiefkind"
            elif gender_b == Person.MALE:
                rel_str = self._get_son(Gb, step, inlaw)
            elif gender_b == Person.FEMALE:
                rel_str = self._get_daughter(Gb, step, inlaw)
            else:
                rel_str = self._get_child_unknown(Gb, step, inlaw)
        elif Ga > Gb:
            #b is higher in the branch, in english uncle/aunt or
            #cousin up, in Dutch always 'oom/tante'
            if gender_b == Person.MALE:
                rel_str = self._get_uncle(Ga - Gb, Gb, step, inlaw)
            elif gender_b == Person.FEMALE:
                rel_str = self._get_aunt(Ga - Gb, Gb, step, inlaw)
            else:
                rel_str = self._get_uncle(Ga - Gb, Gb, step, inlaw) + " of " \
                        + self._get_aunt(Ga - Gb, Gb, step, inlaw)
        elif Ga < Gb:
            #b is lower in the branch, in english niece/nephew or
            #cousin down, in Dutch always 'neef/nicht'
            if gender_b == Person.MALE:
                rel_str = self._get_nephew(Gb - Ga, Ga, step, inlaw)
            elif gender_b == Person.FEMALE:
                rel_str = self._get_niece(Gb - Ga, Ga, step, inlaw)
            else:
                rel_str = self._get_nephew(Gb - Ga, Ga, step, inlaw) + " of " \
                        + self._get_niece(Gb - Ga, Ga, step, inlaw)
        else:
            # people on the same level Ga == Gb
            if gender_b == Person.MALE:
                rel_str = self._get_male_cousin(Ga, step, inlaw)
            elif gender_b == Person.FEMALE:
                rel_str = self._get_female_cousin(Ga, step, inlaw)
            else:
                rel_str = self._get_male_cousin(Ga, step, inlaw) + " of " \
                        + self._get_female_cousin(Ga, step, inlaw)

        return rel_str

    def get_sibling_relationship_string(self, sib_type, gender_a, gender_b,
                                        in_law_a=False, in_law_b=False):
        """
        Determine the string giving the relation between two siblings of
        type sib_type.
        Eg: b is the brother of a
        Here 'brother' is the string we need to determine
        This method gives more details about siblings than
        get_single_relationship_string can do.

        .. warning:: DON'T TRANSLATE THIS PROCEDURE IF LOGIC IS EQUAL IN YOUR
                     LANGUAGE, AND SAME METHODS EXIST (get_uncle, get_aunt,
                     get_sibling)
        """
        if sib_type == self.NORM_SIB or sib_type == self.UNKNOWN_SIB:
            typestr = ""
        elif sib_type == self.HALF_SIB_FATHER \
                or sib_type == self.HALF_SIB_MOTHER:
            typestr = self.HALF
        elif sib_type == self.STEP_SIB:
            typestr = self.STEP

        if in_law_a or in_law_b :
            inlaw = self.INLAW
        else:
            inlaw = ""

        if inlaw and not typestr:
            if gender_b == Person.MALE:
                rel_str = "schoonbroer"
            elif gender_b == Person.FEMALE:
                rel_str = "schoonzus"
            else:
                rel_str = "schoonbroer of -zus"
        else:
            if gender_b == Person.MALE:
                rel_str = self._get_male_cousin(1, typestr, inlaw)
            elif gender_b == Person.FEMALE:
                rel_str = self._get_female_cousin(1, typestr, inlaw)
            else:
                rel_str = self._get_male_cousin(1, typestr, inlaw) + " of " \
                        + self._get_female_cousin(1, typestr, inlaw)
        return rel_str


if __name__ == "__main__":
    # Test function. Call it as follows from the command line (so as to find
    #        imported modules):
    #    export PYTHONPATH=/path/to/gramps/src
    #    python src/plugins/rel/rel_nl.py

    """TRANSLATORS, copy this if statement at the bottom of your
        rel_xx.py module, and test your work with:
        python src/plugins/rel/rel_xx.py
    """
    from gramps.gen.relationship import test
    RC = RelationshipCalculator()
    test(RC, True)

# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2005  Donald N. Allingham
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

_removed_level = [ " ",
                " eerste",
                " tweede",
                " derde",
                " vierde",
                " vijfde",
                " zesde",
                " zevende",
                " achtste",
                " negende",
                " tiende",
                " elfde",
                " twaalfde",
                " dertiende",
                " veertiende",
                " vijftiende",
                " zestiende",
                " zeventiende",
                " achttiende",
                " negentiende",
                " twintigste",
                " eenentwintigste",
                " tweeëntwintigste",
                " drieëntwingste",
                " vierentwingste",
                " vijfentwintigste",
                " zesentwintigste",
                " zevenentwintigste",
                " achtentwintigste",
                " negenentwintigste",
                " dertigste" ]

_parents_level = [ "",
                   "ouders",
                   "grootouders",
                   "overgrootouders",
                   "betovergrootouders",
                   "oudouders",
                   "oudgrootouders",
                   "oudovergrootouders",
                   "oudbetovergrootouders",
                   "stamouders",
                   "stamgrootouders",        # gen 10
                   "stamovergrootouders",
                   "stambetovergrootouders",
                   "stamoudouders",
                   "stamoudgrootouders",
                   "stamoudovergrootouders",
                   "stamoudbetovergrootouders",
                   "edelouders",
                   "edelgrootoders",
                   "edelovergrootoudouders",
                   "edelbetovergrootouders", # gen 20
                   "edeloudouders",
                   "edeloudgrootouders",
                   "edeloudvergrootouders",
                   "edeloudbetovergrootouders",
                   "edelstamouders",
                   "edelstamgrootouders",
                   "edelstamovergrootouders",
                   "edelstambetovergrootouders",
                   "edelstamoudouders" ]

_father_level = [ "",
                  "%s%svader",
                  "%s%sgrootvader",
                  "%s%sovergrootvader",
                  "%s%sbetovergrootvader",
                  "%s%soudvader (generatie 5)",
                  "%s%soudgrootvader (generatie 6)",
                  "%s%soudovergrootvader (generatie 7)",
                  "%s%soudbetovergrootvader (generatie 8)",
                  "%s%sstamvader (generatie 9)",
                  "%s%sstamgrootvader (generatie 10)",
                  "%s%sstamovergrootvader (generatie 11)",
                  "%s%sstambetovergrootvader (generatie 12)",
                  "%s%sstamoudvader (generatie 13)",
                  "%s%sstamoudgrootvader (generatie 14)",
                  "%s%sstamoudovergrootvader (generatie 15)",
                  "%s%sstamoudbetovergrootvader (generatie 16)",
                  "%s%sedelvader (generatie 17)",
                  "%s%sedelgrootvader (generatie 18)",
                  "%s%sedelovergrootoudvader (generatie 19)",
                  "%s%sedelbetovergrootvader (generatie 20)",
                  "%s%sedeloudvader (generatie 21)",
                  "%s%sedeloudgrootvader (generatie 22)",
                  "%s%sedeloudvergrootvader (generatie 23)",
                  "%s%sedeloudbetovergrootvader (generatie 24)",
                  "%s%sedelstamvader (generatie 25)",
                  "%s%sedelstamgrootvader (generatie 26)",
                  "%s%sedelstamovergrootvader (generatie 27)",
                  "%s%sedelstambetovergrootvader (generatie 28)",
                  "%s%sedelstamoudvader (generatie 29)" ]

_mother_level = [ "",
                  "%s%smoeder",
                  "%s%sgrootmoeder",
                  "%s%sovergrootmoeder",
                  "%s%sbetovergrootmoeder",
                  "%s%soudmoeder (generatie 5)",
                  "%s%soudgrootmoeder (generatie 6)",
                  "%s%soudovergrootmoeder (generatie 7)",
                  "%s%soudbetovergrootmoeder (generatie 8)",
                  "%s%sstammoeder (generatie 9)",
                  "%s%sstamgrootmoeder (generatie 10)",
                  "%s%sstamovergrootmoeder (generatie 11)",
                  "%s%sstambetovergrootmoeder (generatie 12)",
                  "%s%sstamoudmoeder (generatie 13)",
                  "%s%sstamoudgrootmoeder (generatie 14)",
                  "%s%sstamoudovergrootmoeder (generatie 15)",
                  "%s%sstamoudbetovergrootmoeder (generatie 16)",
                  "%s%sedelmoeder (generatie 17)",
                  "%s%sedelgrootmoeder (generatie 18)",
                  "%s%sedelovergrootoudmoeder (generatie 19)",
                  "%s%sedelbetovergrootmoeder (generatie 20)",
                  "%s%sedeloudmoeder (generatie 21)",
                  "%s%sedeloudgrootmoeder (generatie 22)",
                  "%s%sedeloudvergrootmoeder (generatie 23)",
                  "%s%sedeloudbetovergrootmoeder (generatie 24)",
                  "%s%sedelstammoeder (generatie 25)",
                  "%s%sedelstamgrootmoeder (generatie 26)",
                  "%s%sedelstamovergrootmoeder (generatie 27)",
                  "%s%sedelstambetovergrootmoeder (generatie 28)",
                  "%s%sedelstamoudmoeder (generatie 29)" ]

_ouder_level = [ "",
                  "%s%souder ",
                  "%s%sgrootouder",
                  "%s%sovergrootouder",
                  "%s%sbetovergrootouder",
                  "%s%soudouder (generatie 5)",
                  "%s%soudgrootouder (generatie 6)",
                  "%s%soudovergrootouder (generatie 7)",
                  "%s%soudbetovergrootouder (generatie 8)",
                  "%s%sstamouder (generatie 9)",
                  "%s%sstamgrootouder (generatie 10)",
                  "%s%sstamovergrootouder (generatie 11)",
                  "%s%sstambetovergrootouder (generatie 12)",
                  "%s%sstamoudouder (generatie 13)",
                  "%s%sstamoudgrootouder (generatie 14)",
                  "%s%sstamoudovergrootouder (generatie 15)",
                  "%s%sstamoudbetovergrootouder (generatie 16)",
                  "%s%sedelouder (generatie 17)",
                  "%s%sedelgrootouder (generatie 18)",
                  "%s%sedelovergrootoudouder (generatie 19)",
                  "%s%sedelbetovergrootouder (generatie 20)",
                  "%s%sedeloudouder (generatie 21)",
                  "%s%sedeloudgrootouder (generatie 22)",
                  "%s%sedeloudvergrootouder (generatie 23)",
                  "%s%sedeloudbetovergrootouder (generatie 24)",
                  "%s%sedelstamouder (generatie 25)",
                  "%s%sedelstamgrootouder (generatie 26)",
                  "%s%sedelstamovergrootouder (generatie 27)",
                  "%s%sedelstambetovergrootouder (generatie 28)",
                  "%s%sedelstamoudouder (generatie 29)" ]

_son_level = [ "",
               "%s%szoon",
               "%s%skleinzoon",
               "%s%sachterkleinzoon",
               "%s%sachterachterkleinzoon",
               "%s%sachterachterachterkleinzoon"]

_daughter_level = [ "",
                    "%s%sdochter",
                    "%s%skleindochter",
                    "%s%sachterkleindochter",
                    "%s%sachterachterkleindochter",
                    "%s%sachterachterachterkleindochter"]

_kind_level = [ "",
                "%s%skind",
                "%s%skleinkind",
                "%s%sachterkleinkind",
                "%s%sachterachterkleinkind",
                "%s%sachterachterachterkleinkind"]

_nephew_level = [ "",
                  "%s%sneef",
                  "%s%sachterneef",
                  "%s%sachterachterneef" ]

_niece_level = [ "",
                 "%s%snicht",
                 "%s%sachternicht",
                 "%s%sachterachternicht"]
_aunt_level = [ "",
                "%s%stante",
                "%s%sgroottante",
                "%s%sovergroottante",
                "%s%sbetovergroottante",
                "%s%soudtante"]

_uncle_level = [ "",
                 "%s%soom",
                 "%s%sgrootoom",
                 "%s%sovergrootoom",
                 "%s%sbetovergrootoom",
                 "%s%soudoom"]
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
    STEP = 'stief'
    HALF = 'half'

    INLAW = 'aangetrouwde '

    def __init__(self):
        gramps.gen.relationship.RelationshipCalculator.__init__(self)

    def get_parents(self, level):
        if level > len(_parents_level)-1:
            return "verre voorouders (%d generaties)" % level
        else:
            return _parents_level[level]

    def _get_father(self, level, step='', inlaw=''):
        """Internal Dutch method to create relation string
        """
        if level > len(_father_level)-1:
            return "verre %s%svoorvader (%d generaties)" % (inlaw, step, level)
        else:
            return _father_level[level] % (inlaw, step)

    def _get_son(self, level, step='', inlaw=''):
        """Internal Dutch method to create relation string
        """
        if level < len(_son_level):
            return _son_level[level]  % (inlaw, step)
        else:
            return "verre %s%sachterkleinzoon (%d generaties)" % (inlaw,
                                                                  step, level)

    def _get_mother(self, level, step='', inlaw=''):
        """Internal Dutch method to create relation string
        """
        if level > len(_mother_level)-1:
            return "verre %s%svoormoeder (%d generaties)"  % (inlaw, step, level)
        else:
            return _mother_level[level] % (inlaw, step)

    def _get_daughter(self, level, step='', inlaw=''):
        """Internal Dutch method to create relation string
        """
        if level > len(_daughter_level)-1:
            return "verre %s%sachterkleindochter (%d generaties)" % (inlaw,
                                                                   step, level)
        else:
            return _daughter_level[level]  % (inlaw, step)

    def _get_parent_unknown(self, level, step='', inlaw=''):
        """Internal Dutch method to create relation string
        """
        if level > len(_ouder_level)-1:
            return "verre %s%svoorouder (%d generaties)"  % (inlaw, step, level)
        elif level == 1:
            return _mother_level[level] % (inlaw, step) + ' of ' + \
                    _father_level[level] % (inlaw, step)
        else:
            return _ouder_level[level] % (inlaw, step)

    def _get_child_unknown(self, level, step='', inlaw=''):
        """Internal Dutch method to create relation string
        """
        if level > len(_kind_level)-1:
            return "ver %s%sachterkleinkind (%d generaties)" % (inlaw, step,
                                                                level)
        else:
            return _kind_level[level]  % (inlaw, step)

    def _get_aunt(self, level, removed, step='', inlaw=''):
        """Internal Dutch method to create relation string
        """
        if removed == 1 and level < len(_aunt_level):
            return _aunt_level[level] % (inlaw, step)
        elif removed == 1:
            return "verre %s%stante (%d generaties)" % (inlaw, step, level)
        elif level > len(_aunt_level)-1 and removed > len(_removed_level) -1:
            return "verre %s%stante (%d generaties, %d graden)" % (inlaw, step,
                                                            level, removed)
        elif level > len(_aunt_level)-1:
            return "verre %s%stante van de%s graad (%d generaties)" % (inlaw,
                                        step, _removed_level[removed], level)
        else:
            return _aunt_level[level] % (inlaw, step) \
                        + _removed_level[removed] + " graad"

    def _get_uncle(self, level, removed, step='', inlaw=''):
        """Internal Dutch method to create relation string
        """
        if removed == 1 and level < len(_uncle_level):
            return _uncle_level[level] % (inlaw, step)
        elif removed == 1:
            return "verre %s%soom (%d generaties)" % (inlaw, step, level)
        elif level > len(_uncle_level)-1 and removed > len(_removed_level) -1:
            return "verre %s%soom (%d generaties, %d graden)" % (inlaw, step,
                                                            level, removed)
        elif level > len(_uncle_level)-1:
            return "verre %s%soom van de%s graad (%d generaties)" % (inlaw,
                                        step, _removed_level[removed], level)
        else:
            return _uncle_level[level] % (inlaw, step) \
                        + _removed_level[removed] + " graad"

    def _get_sibling(self, level, step='', inlaw=''):
        """overwrite of English method to return unknown gender sibling
        """
        assert(level == 1)
        return self._get_male_cousin(0, step=step, inlaw=inlaw) + ' of ' \
                + self._get_female_cousin(0, step=step, inlaw=inlaw)

    def _get_nephew(self, level, removed=1, step='', inlaw=''):
        """Internal Dutch method to create relation string
        """
        if removed == 1 and level < len(_nephew_level):
            return _nephew_level[level] % (inlaw, step)
        elif removed == 1:
            return "verre %s%sneef (%d generaties)" % (inlaw, step, level)
        elif level > len(_nephew_level)-1 and removed > len(_removed_level) -1:
            return "verre %s%sneef (%d generaties, %d graden)" % (inlaw, step,
                                                                level, removed)
        elif level > len(_nephew_level)-1:
            return "verre %s%sneef van de%s graad (%d generaties)" % (inlaw, step,
                                                _removed_level[removed], level)
        else:
            return _nephew_level[level] % (inlaw, step) \
                        + _removed_level[removed] + " graad"

    def _get_niece(self, level, removed=1, step='', inlaw=''):
        """Internal Dutch method to create relation string
        """
        if removed == 1 and level < len(_niece_level):
            return _niece_level[level] % (inlaw, step)
        elif removed == 1:
            return "verre %s%snicht (%d generaties)" % (inlaw, step, level)
        elif level > len(_niece_level)-1 and removed > len(_removed_level) -1:
            return "verre %s%snicht (%d generaties, %d graden)" % (inlaw, step,
                                                                level, removed)
        elif level > len(_niece_level)-1:
            return "verre %s%snicht van de%s graad (%d generaties)"% (inlaw,
                                        step, _removed_level[removed], level)
        else:
            return _niece_level[level] % (inlaw, step) \
                        + _removed_level[removed] + " graad"

    def _get_male_cousin(self, removed, step='', inlaw=''):
        """Specific Dutch thing, the nieces/nephews on same level are called
            going sideways in a branch as the nieces/newphews going downward
            from your brother/sisters. This used to be called "kozijn"
        """
        removed -= 1
        if removed > len(_removed_level)-1:
            return "verre %s%sneef (kozijn, %d graden)" % (inlaw, step,
                                                           removed)
        elif removed == 0:
            return "%s%sbroer" % (inlaw, step)
        else:
            return "%s%sneef (kozijn)" % (inlaw, step)  \
                        +_removed_level[removed] + " graad"

    def _get_female_cousin(self, removed, step='', inlaw=''):
        """Specific Dutch thing, the nieces/nephews on same level are called
            going sideways in a branch as the nieces/newphews going downward
            from your brother/sisters.  This used to be called "kozijn"
        """
        removed -= 1
        if removed > len(_removed_level)-1:
            return "verre %s%snicht (kozijn, %d graden)" % (inlaw, step,
                                                           removed)
        elif removed == 0:
            return "%s%szus"  % (inlaw, step)
        else:
            return "%s%snicht (kozijn)"  % (inlaw, step) \
                        + _removed_level[removed] + " graad"

    def get_single_relationship_string(self, Ga, Gb, gender_a, gender_b,
                                       reltocommon_a, reltocommon_b,
                                       only_birth=True,
                                       in_law_a=False, in_law_b=False):
        """
        Return a string representing the relationship between the two people,
        see english method, eg b is father of a
        """
        if only_birth:
            step = ''
        else:
            step = self.STEP

        if in_law_a or in_law_b :
            inlaw = self.INLAW
        else:
            inlaw = ''

        rel_str = "verre %s%sfamilie" % (inlaw, step)

        if Gb == 0:
            #b is ancestor
            if Ga == 0:
                rel_str = 'zelfde persoon'
            elif Ga == 1 and inlaw and not step:
                if gender_b == Person.MALE:
                    rel_str = 'schoonvader'
                elif gender_b == Person.FEMALE:
                    rel_str = 'schoonmoeder'
                else:
                    rel_str = 'schoonouder'
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
                    rel_str = 'schoonzoon'
                elif gender_b == Person.FEMALE:
                    rel_str = 'schoondochter'
                else:
                    rel_str = 'schoonzoon of -dochter'
            elif Gb == 1 and inlaw and step:
                #inlaw stepchild
                if gender_b == Person.MALE:
                    rel_str = 'aangetrouwde stiefzoon'
                elif gender_b == Person.FEMALE:
                    rel_str = 'aangetrouwde stiefdochter'
                else:
                    rel_str = 'aangetrouwde stiefzoon of dochter'
            elif gender_b == Person.MALE:
                rel_str = self._get_son(Gb, step, inlaw)
            elif gender_b == Person.FEMALE:
                rel_str = self._get_daughter(Gb, step, inlaw)
            else:
                rel_str = self._get_child_unknown(Gb, step, inlaw)
        elif Ga > Gb:
            #b is higher in the branch, in english uncle/aunt or
            #cousin up, in dutch always 'oom/tante'
            if gender_b == Person.MALE:
                rel_str = self._get_uncle(Ga - Gb, Gb, step, inlaw)
            else:
                rel_str = self._get_aunt(Ga - Gb, Gb, step, inlaw)
        elif Ga < Gb:
            #b is lower in the branch, in english niece/nephew or
            #cousin down, in dutch always 'neef/nicht'
            if gender_b == Person.MALE:
                rel_str = self._get_nephew(Gb - Ga, Ga, step, inlaw)
            else:
                rel_str = self._get_niece(Gb - Ga, Ga, step, inlaw)
        else:
            # people on the same level Ga == Gb
            if gender_b == Person.MALE:
                rel_str = self._get_male_cousin(Ga, step, inlaw)
            else:
                rel_str = self._get_female_cousin(Ga, step, inlaw)

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
            typestr = ''
        elif sib_type == self.HALF_SIB_FATHER \
                or sib_type == self.HALF_SIB_MOTHER:
            typestr = self.HALF
        elif sib_type == self.STEP_SIB:
            typestr = self.STEP

        if in_law_a or in_law_b :
            inlaw = self.INLAW
        else:
            inlaw = ''

        if inlaw and not typestr:
            if gender_b == Person.MALE:
                rel_str = 'schoonbroer'
            elif gender_b == Person.FEMALE:
                rel_str = 'schoonzus'
            else:
                rel_str = 'schoonzus/broer'
        else:
            if gender_b == Person.MALE:
                rel_str = self._get_male_cousin(1, typestr, inlaw)
            else:
                rel_str = self._get_female_cousin(1, typestr, inlaw)
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

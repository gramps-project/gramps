# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2006  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2008       Peter G. LAndgren
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

# Written by Alex Roitman, largely based on relationship.py by Don Allingham
# and on valuable input from Jens Arvidsson
# Updated to 3.0 by Peter Landgren 2007-12-30.
#
"""
Swedish-specific definitions of relationships
"""

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------

from gramps.gen.lib import Person
import gramps.gen.relationship

# -------------------------------------------------------------------------

_cousin_level = [
    "",
    "kusin",
    "tremänning",
    "fyrmänning",
    "femmänning",
    "sexmänning",
    "sjumänning",
    "åttamänning",
    "niomänning",
    "tiomänning",
    "elvammänning",
    "tolvmänning",
    "trettonmänning",
    "fjortonmänning",
    "femtonmänning",
    "sextonmänning",
    "sjuttonmänning",
    "artonmänning",
    "nittonmänning",
    "tjugomänning",
    "tjugoettmänning",
    "tjugotvåmänning",
    "tjugotremänning",
    "tjugofyramänning",
    "tjugofemmänning",
    "tjugoexmänning",
    "tjugosjumänning",
    "tjugoåttamänning",
    "tjugoniomänning",
    "trettiomänning",
]

_children_level = 20

_level_name = [
    "",
    "första",
    "andra",
    "tredje",
    "fjärde",
    "femte",
    "sjätte",
    "sjunde",
    "åttonde",
    "nionde",
    "tionde",
    "elfte",
    "tolfte",
    "trettonde",
    "fjortonde",
    "femtonde",
    "sextonde",
    "sjuttonde",
    "artonde",
    "nittonde",
    "tjugonde",
]


# -------------------------------------------------------------------------
#
#
#
# -------------------------------------------------------------------------
class RelationshipCalculator(gramps.gen.relationship.RelationshipCalculator):
    """
    RelationshipCalculator Class
    """

    # sibling strings
    STEP = "styv"
    HALF = "halv"
    # in-law string
    INLAW = "ingift "

    def __init__(self):
        gramps.gen.relationship.RelationshipCalculator.__init__(self)

    def _get_cousin(self, level, step, inlaw):
        if level > len(_cousin_level) - 1:
            return "avlägset släkt"
        else:
            result = inlaw + _cousin_level[level]
            # Indicate step relations) by adding ' [styv]'
            if step:
                result = result + " [styv]"
            return result

    def pair_up(self, rel_list, step):
        result = []
        item = ""
        for word in rel_list[:]:
            if not word:
                continue
            if word.replace(" [styv]", "") in _cousin_level:
                if item:
                    result.append(item)
                    item = ""
                result.append(word)
                continue
            if item:
                if word == "syster":
                    item = item[0:-1]
                    word = "ster"
                elif word == "dotter" and item == "bror":
                    item = "brors"
                result.append(item + word)
                item = ""
            else:
                item = word
        if item:
            result.append(item)
        gen_result = [item + "s" for item in result[0:-1]]
        gen_result = " ".join(gen_result + result[-1:])
        # Indicate step relations) by adding ' [styv]' if not already added.
        if len(rel_list) > 1 and step != "" and not gen_result.rfind(" [styv]"):
            gen_result = gen_result + " [styv]"
        return gen_result

    def _get_direct_ancestor(self, person_gender, rel_string, step, inlaw):
        result = []
        for rel in rel_string:
            if rel == "f":
                result.append("far")
            else:
                result.append("mor")
        if person_gender == Person.MALE:
            result[-1] = "far"
        if person_gender == Person.FEMALE:
            result[-1] = "mor"
        if person_gender == Person.UNKNOWN:
            result[-1] = "förälder"
        if step != "" and len(result) == 1:
            # Preceed with step prefix of father/mother
            result[0] = self.STEP + result[0]
        if inlaw != "":
            # Preceed with inlaw prefix
            result[-1] = "svär" + result[-1]
        if (
            len(result) > 1
            and len(result) % 2 == 0
            and (person_gender == Person.UNKNOWN or inlaw != "")
        ):
            # Correct string "-2" with genitive s and add a space to get
            # correct Swedish, if even number in result
            result[-2] = result[-2] + "s "
        return self.pair_up(result, step)

    def _get_direct_descendant(self, person_gender, rel_string, step, inlaw):
        result = []
        for ix in range(len(rel_string) - 2, -1, -1):
            if rel_string[ix] == "f":
                result.append("son")
            else:
                result.append("dotter")
        if person_gender == Person.MALE:
            result.append("son")
        elif person_gender == Person.FEMALE:
            result.append("dotter")
        else:
            if person_gender == Person.UNKNOWN and inlaw == "":
                result.append("barn")
            if person_gender == Person.UNKNOWN and inlaw != "":
                result.append("-son/dotter")
        if step != "" and len(result) == 1:
            result[0] = self.STEP + result[0]
        if inlaw != "":
            # Preceed with inlaw prefix
            result[-1] = "svär" + result[-1]
        if (
            len(result) > 1
            and len(result) % 2 == 0
            and (person_gender == Person.UNKNOWN or inlaw != "")
        ):
            # Correct string "-2" with genitive s and add a space to get
            # correct Swedish, if even number in result
            result[-2] = result[-2] + "s "
        return self.pair_up(result, step)

    def _get_ancestors_cousin(self, rel_string_long, rel_string_short, step, inlaw):
        result = []
        removed = len(rel_string_long) - len(rel_string_short)
        level = len(rel_string_short) - 1
        for ix in range(removed):
            if rel_string_long[ix] == "f":
                result.append("far")
            else:
                result.append("mor")
        if inlaw != "":
            inlaw = "s ingifta "
        result.append(self._get_cousin(level, step, inlaw))
        if step != "" and len(result) == 1:
            result[0] = self.STEP + result[0]
        return self.pair_up(result, step)

    def _get_cousins_descendant(
        self, person_gender, rel_string_long, rel_string_short, step, inlaw
    ):
        result = []
        removed = len(rel_string_long) - len(rel_string_short) - 1
        level = len(rel_string_short) - 1
        if level:
            result.append(self._get_cousin(level, step, inlaw))
        elif rel_string_long[removed] == "f":
            result.append("bror")
        else:
            result.append("syster")
        for ix in range(removed - 1, -1, -1):
            if rel_string_long[ix] == "f":
                result.append("son")
            else:
                result.append("dotter")
        if person_gender == Person.MALE:
            result.append("son")
        elif person_gender == Person.FEMALE:
            result.append("dotter")
        else:
            if person_gender == Person.UNKNOWN and inlaw == "":
                result.append("barn")
            if person_gender == Person.UNKNOWN and inlaw != "":
                result.append("-son/dotter")
        if step != "" and len(result) == 1:
            result[0] = self.STEP + result[0]
        if inlaw != "":
            # Preceed with inlaw prefix
            result[-1] = "svär" + result[-1]
        if (
            len(result) > 1
            and len(result) % 2 == 0
            and (person_gender == Person.UNKNOWN or inlaw != "")
        ):
            # Correct string "-2" with genitive s and add a space to get
            # correct Swedish, if even number in result
            result[-2] = result[-2] + "s "
        return self.pair_up(result, step)

    def _get_ancestors_brother(self, rel_string, person_gender, step, inlaw):
        result = []
        for ix in range(len(rel_string) - 1):
            if rel_string[ix] == "f":
                result.append("far")
            else:
                result.append("mor")
        result.append("bror")
        if person_gender == Person.UNKNOWN:
            result[-1] = "syskon"
        if step != "" and len(result) == 1:
            result[0] = self.STEP + result[0]
        if inlaw != "":
            # Preceed with inlaw prefix
            result[-1] = "svåger"
        if inlaw != "" and person_gender == Person.UNKNOWN:
            # Preceed with inlaw prefix
            result[-1] = "svåger/svägerska"
        if (
            len(result) > 1
            and len(result) % 2 == 0
            and (person_gender == Person.UNKNOWN or inlaw != "")
        ):
            # Correct string "-2" with genitive s and add a space to get
            # correct Swedish, if even number in result
            result[-2] = result[-2] + "s "
        return self.pair_up(result, step)

    def _get_ancestors_sister(self, rel_string, step, inlaw):
        result = []
        for ix in range(len(rel_string) - 1):
            if rel_string[ix] == "f":
                result.append("far")
            else:
                result.append("mor")
        result.append("syster")
        if step != "" and len(result) == 1:
            result[0] = self.STEP + result[0]
        if inlaw != "":
            # Preceed with inlaw prefix
            result[-1] = "svägerska"
        if len(result) > 1 and len(result) % 2 == 0 and inlaw != "":
            # Correct string "-2" with genitive s and add a space to get
            # correct Swedish, if even number in result
            result[-2] = result[-2] + "s "
        return self.pair_up(result, step)

    def get_sibling_relationship_string(
        self, sib_type, gender_a, gender_b, in_law_a=False, in_law_b=False
    ):
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
        elif sib_type == self.HALF_SIB_MOTHER or sib_type == self.HALF_SIB_FATHER:
            typestr = self.HALF
        elif sib_type == self.STEP_SIB:
            typestr = self.STEP

        if gender_b == Person.MALE:
            rel_str = "bror"
        elif gender_b == Person.FEMALE:
            rel_str = "syster"
        else:
            rel_str = "syskon"
        return typestr + rel_str

    # kinship report

    def _get_cousin_kinship(self, Ga):
        rel_str = self._get_cousin(Ga - 1, False, "")
        if Ga == 2:
            rel_str = rel_str + "er"
        else:
            rel_str = rel_str + "ar"
        return rel_str

    def get_plural_relationship_string(
        self,
        Ga,
        Gb,
        reltocommon_a="",
        reltocommon_b="",
        only_birth=True,
        in_law_a=False,
        in_law_b=False,
    ):
        """
        Provide a string that describes the relationsip between a person, and
        a group of people with the same relationship. E.g. "grandparents" or
        "children".

        Ga and Gb can be used to mathematically calculate the relationship.

        .. seealso::
            http://en.wikipedia.org/wiki/Cousin#Mathematical_definitions

        :param Ga: The number of generations between the main person and the
                   common ancestor.
        :type Ga: int
        :param Gb: The number of generations between the group of people and the
                   common ancestor
        :type Gb: int
        :param reltocommon_a: relation path to common ancestor or common
                              Family for person a.
                              Note that length = Ga
        :type reltocommon_a: str
        :param reltocommon_b: relation path to common ancestor or common
                              Family for person b.
                              Note that length = Gb
        :type reltocommon_b: str
        :param only_birth: True if relation between a and b is by birth only
                           False otherwise
        :type only_birth: bool
        :param in_law_a: True if path to common ancestors is via the partner
                         of person a
        :type in_law_a: bool
        :param in_law_b: True if path to common ancestors is via the partner
                         of person b
        :type in_law_b: bool
        :returns: A string describing the relationship between the person and
                  the group.
        :rtype: str
        """

        rel_str = "avlägsna släktingar"
        if Ga == 0:
            result = []
            # These are descendants
            if Gb < _children_level:
                for AntBarn in range(Gb):
                    result.append("barn")
                rel_str = self.pair_up(result, "")
            else:
                rel_str = "avlägsna ättlingar"
        elif Gb == 0:
            # These are parents/grand parents
            if Ga < len(_level_name):
                if Ga == 1:
                    rel_str = "föräldrar"
                else:
                    rel_str = (
                        "far- och morföräldrar i %s generationen" % _level_name[Ga]
                    )
            else:
                rel_str = "avlägsna förfäder"
        elif Gb == 1:
            # These are siblings/aunts/uncles
            if Ga < len(_level_name):
                if Ga == 1:
                    rel_str = "syskon"
                else:
                    rel_str = "förfäders syskon i %s generationen" % _level_name[Ga - 1]
            else:
                rel_str = "avlägsna farbröder/morbröder/fastrar/mostrar"
        elif Ga == 1:
            # These are nieces/nephews
            if Gb < len(_level_name):
                result = []
                result.append("syskonbarn")
                for AntBarn in range(Gb - 2):
                    result.append("barn")
                rel_str = self.pair_up(result, "")
            else:
                rel_str = "avlägsna brorsöner/systersöner/brorsdöttrar/systerdöttrar"
        elif Ga > 1 and Ga == Gb:
            # These are cousins in the same generation
            rel_str = self._get_cousin_kinship(Ga)
        elif Ga > 1 and Ga > Gb:
            # These are cousins in different generations with the second person
            # being in a higher generation from the common ancestor than the
            # first person.
            if Gb <= len(_level_name):
                rel_str = (
                    "förfäders "
                    + self._get_cousin_kinship(Ga)
                    + " i "
                    + _level_name[Gb]
                    + " generationen"
                )
            else:
                rel_str = "avlägsna kusiner"
        elif Gb > 1 and Gb > Ga:
            # These are cousins in different generations with the second person
            # being in a lower generation from the common ancestor than the
            # first person.
            if Ga <= len(_level_name):
                result = []
                result.append(self._get_cousin(Ga - 1, False, ""))
                for AntBarn in range(Gb - Ga):
                    result.append("barn")
                rel_str = self.pair_up(result, "")
            else:
                rel_str = "avlägsna kusiner"

        if in_law_b == True:
            rel_str = "makar till %s" % rel_str

        return rel_str

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
        Provide a string that describes the relationsip between a person, and
        another person. E.g. "grandparent" or "child".

        To be used as: 'person b is the grandparent of a', this will be in
        translation string:  'person b is the %(relation)s of a'

        Note that languages with gender should add 'the' inside the
        translation, so eg in french:  'person b est %(relation)s de a'
        where relation will be here: le grandparent

        Ga and Gb can be used to mathematically calculate the relationship.

        .. seealso::
            http://en.wikipedia.org/wiki/Cousin#Mathematical_definitions

        Some languages need to know the specific path to the common ancestor.
        Those languages should use reltocommon_a and reltocommon_b which is
        a string like 'mfmf'.

        The possible string codes are:

        =======================  ===========================================
        Code                     Description
        =======================  ===========================================
        REL_MOTHER               # going up to mother
        REL_FATHER               # going up to father
        REL_MOTHER_NOTBIRTH      # going up to mother, not birth relation
        REL_FATHER_NOTBIRTH      # going up to father, not birth relation
        REL_FAM_BIRTH            # going up to family (mother and father)
        REL_FAM_NONBIRTH         # going up to family, not birth relation
        REL_FAM_BIRTH_MOTH_ONLY  # going up to fam, only birth rel to mother
        REL_FAM_BIRTH_FATH_ONLY  # going up to fam, only birth rel to father
        =======================  ===========================================

        Prefix codes are stripped, so REL_FAM_INLAW_PREFIX is not present.
        If the relation starts with the inlaw of the person a, then 'in_law_a'
        is True, if it starts with the inlaw of person b, then 'in_law_b' is
        True.

        Also REL_SIBLING (# going sideways to sibling (no parents)) is not
        passed to this routine. The collapse_relations changes this to a
        family relation.

        Hence, calling routines should always strip REL_SIBLING and
        REL_FAM_INLAW_PREFIX before calling get_single_relationship_string()
        Note that only_birth=False, means that in the reltocommon one of the
        NOTBIRTH specifiers is present.

        The REL_FAM identifiers mean that the relation is not via a common
        ancestor, but via a common family (note that that is not possible for
        direct descendants or direct ancestors!). If the relation to one of the
        parents in that common family is by birth, then 'only_birth' is not
        set to False. The only_birth() method is normally used for this.

        :param Ga: The number of generations between the main person and the
                   common ancestor.
        :type Ga: int
        :param Gb: The number of generations between the other person and the
                   common ancestor.
        :type Gb: int
        :param gender_a: gender of person a
        :type gender_a: int gender
        :param gender_b: gender of person b
        :type gender_b: int gender
        :param reltocommon_a: relation path to common ancestor or common
                              Family for person a.
                              Note that length = Ga
        :type reltocommon_a: str
        :param reltocommon_b: relation path to common ancestor or common
                              Family for person b.
                              Note that length = Gb
        :type reltocommon_b: str
        :param in_law_a:  True if path to common ancestors is via the partner
                          of person a
        :type in_law_a: bool
        :param in_law_b: True if path to common ancestors is via the partner
                         of person b
        :type in_law_b: bool
        :param only_birth: True if relation between a and b is by birth only
                           False otherwise
        :type only_birth: bool
        :returns: A string describing the relationship between the two people
        :rtype: str

        .. note:: 1. the self.REL_SIBLING should not be passed to this routine,
                     so we should not check on it. All other self.
                  2. for better determination of siblings, use if Ga=1=Gb
                     get_sibling_relationship_string
        """
        if only_birth:
            step = ""
        else:
            step = self.STEP

        if in_law_a or in_law_b:
            inlaw = self.INLAW
        else:
            inlaw = ""
        rel_str = "avlägsen %s-släkting eller %s släkting" % (step, inlaw)
        if Ga == 0:
            # b is descendant of a
            if Gb == 0:
                rel_str = "samma person"
            else:
                rel_str = self._get_direct_descendant(
                    gender_b, reltocommon_b, step, inlaw
                )
        elif Gb == 0:
            # b is parents/grand parent of a
            rel_str = self._get_direct_ancestor(gender_b, reltocommon_a, step, inlaw)
        elif Gb == 1:
            # b is sibling/aunt/uncle of a
            # handles brother and unknown gender as second person,
            # shows up in "testing unknown cousins same generation"
            if gender_b == Person.MALE or gender_b == Person.UNKNOWN:
                rel_str = self._get_ancestors_brother(
                    reltocommon_a, gender_b, step, inlaw
                )
            elif gender_b == Person.FEMALE:
                rel_str = self._get_ancestors_sister(reltocommon_a, step, inlaw)
        elif Ga == Gb:
            # a and b cousins in the same generation
            rel_str = self._get_cousin(Ga - 1, step, inlaw)
        elif Ga > Gb:
            # These are cousins in different generations with the second person
            # being in a higher generation from the common ancestor than the
            # first person.
            rel_str = self._get_ancestors_cousin(
                reltocommon_a, reltocommon_b, step, inlaw
            )
        elif Gb > Ga:
            # These are cousins in different generations with the second person
            # being in a lower generation from the common ancestor than the
            # first person.
            rel_str = self._get_cousins_descendant(
                gender_b, reltocommon_b, reltocommon_a, step, inlaw
            )
        return rel_str


if __name__ == "__main__":
    # Test function. Call it as follows from the command line (so as to find
    #        imported modules):
    #    export PYTHONPATH=/path/to/gramps/src
    # python src/plugins/rel/rel_sv.py
    # (Above not needed here)

    """TRANSLATORS, copy this if statement at the bottom of your
    rel_xx.py module, and test your work with:
    python src/plugins/rel/rel_xx.py
    """
    from gramps.gen.relationship import test

    RC = RelationshipCalculator()
    test(RC, True)

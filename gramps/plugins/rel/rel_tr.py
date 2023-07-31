#
# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2006  Donald N. Allingham
# Copyright (C) 2021-2022  Bora Atıcı
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
# Written by Bora Atıcı <boratici.acc@gmail.com>, 2021
#
# --------------------------------------------------------------------------------
#
# Turkish relationship and kinship names
#
# --------------------------------------------------------------------------------
# kan bağı(blood ties)
# - haminne(parent's grandmother)
# - dede(grandfather), nine(grandmother) -> babaanne(father's mother),
#                                        -> anneanne(mother's mother)
# - baba/ata(father), anne/ana(mother)
# - kardeş(sibling), erkek kardeş(brother), kız kardeş(sister)
#                    abi(big brother)     , abla(big sister)
# - torun(grandchild)
# - -> amca(father's brother/uncle), dayı(mother's brother/uncle)
#   -> hala(father's sister/aunt)  , teyze(mother's sister/aunt)
# - kuzen/böle(only uncle and aunt's children/cousin)
# - yeğen(only sibling's children/nephew-niece)
#
# kayın(in-law)
# - kaynata/kayınbaba(father-in-law), kaynana/kayınvalide(mother-in-law)
# - -> kayınbirader/kayın(only spouse's brother/brother-in-law),
#   -> -> görümce(only husband's sister/sister-in-law)
#      -> baldız(only wife's sister/sister-in-law)
# - damat
# - gelin
# - enişte
# - yenge
# - bacanak
# - görümce
# - elti
# - babalık
# - analık
# - oğulluk
# - dünür
# - ebeveyn
# and much more. It will be added with future updates.
# --------------------------------------------------------------------------------
"""
Turkish-specific classes for relationships.
"""
# --------------------------------------------------------------------------------
#
# Gramps modules
#
# --------------------------------------------------------------------------------
from operator import le
from gramps.gen.lib import Person
import gramps.gen.relationship

# --------------------------------------------------------------------------------
#
# Shared constants
#
# --------------------------------------------------------------------------------
_level_name = [
    "",
    "",
    "ikinci derece",
    "üçüncü derece",
    "dördüncü derece",
    "beşinci derece",
    "altıncı derece",
    "yedinci derece",
    "sekizinci derece",
    "dokuzuncu derece",
    "onuncu derece",
    "on birinci",
    "on ikinci",
    "on üçüncü",
    "on dördüncü",
    "on beşinci",
    "on altıncı",
    "on yedinci",
    "on sekizinci",
    "on dokuzuncu",
    "yirminci",
    "yirmi birinci",
    "yirmi ikinci",
    "yirmi üçüncü",
    "yirmi dördüncü",
    "yirmi beşinci",
    "yirmi altıncı",
    "yirmi yedinci",
    "yirmi sekizinci",
    "yirmi dokuzuncu",
    "otuzuncu",
    "otuz birinci",
    "otuz ikinci",
    "otuz üçüncü",
    "otuz dördüncü",
    "otuz beşinci",
    "otuz altıncı",
    "otuz yedinci",
    "otuz sekizinci",
    "otuz dokuzuncu",
    "kırkıncı",
    "kırk birinci",
]

_level_name_male = _level_name

_level_name_female = _level_name

# --------------------------------------------------------------------------------
#
# Relationship levels
#
# --------------------------------------------------------------------------------
_parent_level = ["", "", "ebeveynlerinin", "büyük ebeveynlerinin"]

_son_level = [
    "",
    "oğlu",
    "torunu",
    "torununun oğlu",
    "torununun torunu",
    "torununun torununun oğlu",
    "torununun torununun torunu",
]

_daughter_level = [
    "",
    "kızı",
    "torunu",
    "torununun kızı",
    "torununun torunu",
    "torununun torununun kızı",
    "torununun torununun torunu",
]

_child_level = [
    "",
    "çocuğu",
    "torunu",
    "torununun çocuğu",
    "torununun torunu",
    "torununun torununun çocuğu",
    "torununun torununun torunu",
]

_father_level = [
    "",
    "babası",
    "dedesi",
    "büyük dedesi",
    "dedesinin dedesi",
    "dedesinin dedesinin babası",
    "dedesinin dedesinin dedesi",
]

_mother_level = [
    "",
    "annesi",
    "ninesi",
    "haminnesi",
    "büyük haminnesi",
    "ninesinin ninesinin annesi",
    "ninesinin ninesinin ninesi",
]

_uncle_level = [
    "",
    "erkek kardeş",
    "amca",
    "büyük amca",
]

_aunt_level = [
    "",
    "kız kardeş",
    "hala",
    "büyük hala",
]

# --------------------------------------------------------------------------------
#
# Relationship Classes
#
# --------------------------------------------------------------------------------


class RelationshipCalculator(gramps.gen.relationship.RelationshipCalculator):
    """
    RelationshipCalculator Class
    """

    def __init__(self):
        gramps.gen.relationship.RelationshipCalculator.__init__(self)

    def get_sword_distaff(self, level, reltocommon, gender=Person.UNKNOWN):
        """
        Generate relationships 'by male line' or 'by female line',
        specific for Turkish
        """
        if level <= 1:
            return ""

        by_line = ""
        for g in reltocommon:
            if by_line and by_line != g:
                by_line = ""
                break
            by_line = g

        if by_line == self.REL_FATHER and gender == Person.MALE:
            # By male line
            return "(erkek hattından) "
        elif by_line == self.REL_MOTHER and gender == Person.FEMALE:
            # By male line
            return "(kadın hattından) "
        elif reltocommon[0] == self.REL_FATHER:
            # From father's side
            return "(baba tarafından) "
        elif reltocommon[0] == self.REL_MOTHER:
            # From mother's side
            return "(anne tarafından) "
        else:
            return ""

    def get_son(self, level, inlaw=""):
        """
        Provides information how much male descendant is related to this person
        """
        # Define if the person is natural relative or in law
        if inlaw == "":
            t_inlaw = ""
        else:
            t_inlaw = "kayın "

        if level >= 0 and level < len(_son_level):
            return t_inlaw + _son_level[level]
        # else:
        # return t_inlaw + "%d" % (level + 1)

    def get_daughter(self, level, inlaw=""):
        """
        Provides information how much female descendant is related to this person
        """
        # Define if the person is natural relative or in law
        if inlaw == "":
            t_inlaw = ""
        else:
            t_inlaw = "kayın "

        if level >= 0 and level < len(_daughter_level):
            return t_inlaw + _daughter_level[level]
        # else:
        # return t_inlaw + "%d" % (level + 1)

    def get_child_unknown(self, level, inlaw=""):
        """
        Provides information how much descendant of unknown gender is related to this person
        """
        # Define if the person is natural relative or in law
        if inlaw == "":
            t_inlaw = ""
        else:
            t_inlaw = "kayın "

        if level >= 0 and level < len(_child_level):
            return t_inlaw + _child_level[level]
        # else:
        # return t_inlaw + "%d" % (level + 1)

    def get_father(self, level, reltocommon, inlaw=""):
        """
        Provides information how much male ancestor (for example father)
        is related to the given person
        """
        if inlaw == "":
            t_inlaw = ""
        else:
            t_inlaw = "kayın "

        if level >= 0 and level < len(_father_level):
            # If you know exact name of relationship - use it
            if level == 1:
                # Father
                return t_inlaw + _father_level[level]
            else:
                # Grandfather, Greatgrandfather, Greatgreatgrandfather
                return (
                    t_inlaw
                    + self.get_sword_distaff(level, reltocommon, Person.MALE)
                    + _father_level[level]
                )
        else:
            # For deep generations
            return (
                t_inlaw
                + "%s dedesi" % _level_name[level]
                + self.get_sword_distaff(level, reltocommon, Person.MALE)
            )

    def get_mother(self, level, reltocommon, inlaw=""):
        """
        Provides information how much female ancestor (for example mother)
        is related to the given person
        """
        if inlaw == "":
            t_inlaw = ""
        else:
            t_inlaw = "kayın "

        if level >= 0 and level < len(_mother_level):
            # If you know exact name of relationship - use it
            if level == 1:
                # Mother
                return t_inlaw + _mother_level[level]

            else:
                # Grandmother, Greatgrandmother, Greatgreatgrandmother
                return (
                    t_inlaw
                    + self.get_sword_distaff(level, reltocommon, Person.FEMALE)
                    + _mother_level[level]
                )
        else:
            # For deep generations
            #
            return (
                t_inlaw
                + "%s ninesi" % _level_name[level]
                + self.get_sword_distaff(level, reltocommon, Person.FEMALE)
            )

    def get_parent_unknown(self, level, reltocommon, inlaw=""):
        """
        Provides information how much an ancestor of unknown gender
        is related to the given person (unknown sex)
        """
        if inlaw == "":
            t_inlaw = ""
        else:
            t_inlaw = "kayın "

        if level == 1:
            return t_inlaw + "babası/annesi"
        else:
            return (
                t_inlaw
                + "%s dedesi/ninesi" % _level_name[level]
                + self.get_sword_distaff(level, reltocommon)
            )

    def get_uncle(self, level, reltocommon, inlaw=""):
        """
        Return uncle generation name
        """
        if reltocommon[0] == self.REL_FATHER:
            # from Father
            if level < len(_uncle_level):
                if level == 2:
                    return "amcası"
                elif level == 3:
                    return "(baba tarafından) büyük amcası"
                elif level == 4:
                    return "(baba tarafından) büyük büyük amcası"
            else:
                return "(baba tarafından) " + (_level_name[level - 1]) + " amcası"
        elif reltocommon[0] == self.REL_MOTHER:
            # from Mother
            if level < len(_uncle_level):
                if level == 2:
                    return "dayısı"
                elif level == 3:
                    return "(anne tarafından) büyük dayısı"
                elif level == 4:
                    return "(anne tarafından) büyük büyük dayısı"
            else:
                return "(anne tarafından) " + (_level_name[level - 1]) + " dayısı"
        else:
            if level == 2:
                return "amcası/dayısı"
            else:
                return (_level_name[level - 1]) + " amcası/dayısı"

    def get_aunt(self, level, reltocommon, inlaw=""):
        """
        Return aunt generation name
        """
        if reltocommon[0] == self.REL_FATHER:
            # from Father
            if level < len(_aunt_level):
                if level == 2:
                    return "halası"
                elif level == 3:
                    return "(baba tarafından) büyük halası"
                elif level == 4:
                    return "(baba tarafından) büyük büyük halası"
            else:
                return "(baba tarafından) %s halası" % _level_name[level - 1]
        elif reltocommon[0] == self.REL_MOTHER:
            # from Mother
            if level < len(_aunt_level):
                if level == 2:
                    return "teyzesi"
                elif level == 3:
                    return "(anne tarafından) büyük teyzesi"
                elif level == 4:
                    return "(anne tarafından) büyük büyük teyzesi"
            else:
                return "(anne tarafından) %s teyzesi" % _level_name[level - 1]
        else:
            if level == 2:
                return "teyzesi/halası"
            else:
                return "%s teyzesi/halası" % _level_name[level - 1]

    def get_uncle_aunt_unknown(self, level, reltocommon, inlaw=""):
        """
        Return uncle/aunt generation name when gender unknown
        """
        if reltocommon[0] == self.REL_FATHER:
            # from Father
            if level == 2:
                return "babasının kardeşi"
            elif level == 3:
                return "dedesi veya babaannesinin kardeşi"
            else:
                return (
                    "(baba tarafından) %s üstsoyunun kardeşi" % _level_name[level - 1]
                )
        elif reltocommon[0] == self.REL_MOTHER:
            # from Mother
            if level == 2:
                return "annesinin kardeşi"
            elif level == 3:
                return "dedesinin ve anneannesinin kardeşi"
            else:
                return (
                    "(anne tarafından) %s üstsoyunun kardeşi" % _level_name[level - 1]
                )
        else:
            if level == 2:
                return "ebeveynlerinin kardeşi"
            else:
                return "%s üstsoyunun kardeşi" % _level_name[level - 1]

    def get_nephew(self, level, reltocommon, inlaw=""):
        """
        Return nephew generation name
        """
        if inlaw == "":
            t_inlaw = ""
        else:
            t_inlaw = "kayın "

        if level == 2:
            if reltocommon[0] == self.REL_FATHER:
                # Brother's son
                return t_inlaw + "(erkek kardeşinden) yeğeni"
            elif reltocommon[0] == self.REL_MOTHER:
                # Sister's son
                return t_inlaw + "(kız kardeşinden) yeğeni"
            else:
                return t_inlaw + "(kardeşinden) yeğeni"
        elif level >= 2 and level <= 6:
            if reltocommon[level - 2] == self.REL_FATHER:
                # Brother's son generation
                if reltocommon[level - 3] == self.REL_FATHER:
                    # Son of brother son
                    return "erkek kardeşinin oğlunun " + self.get_son(
                        (level - 2), inlaw
                    )
                elif reltocommon[level - 3] == self.REL_MOTHER:
                    # Son of brother daughter
                    return "erkek kardeşinin kızının " + self.get_son(
                        (level - 2), inlaw
                    )
                else:
                    # Currently not used
                    return "erkek kardeşinin çocuğunun " + self.get_son(
                        (level - 2), inlaw
                    )
            elif reltocommon[level - 2] == self.REL_MOTHER:
                # Sister's son generation
                if reltocommon[level - 3] == self.REL_FATHER:
                    # Son of sister son
                    return "kız kardeşinin oğlunun " + self.get_son((level - 2), inlaw)
                elif reltocommon[level - 3] == self.REL_MOTHER:
                    # Son of sister daughter
                    return "kız kardeşinin kızının " + self.get_son((level - 2), inlaw)
                else:
                    # Currently not used
                    return "kız kardeşinin çocuğunun " + self.get_son(
                        (level - 2), inlaw
                    )
            else:
                return "kardeşinin çocuğunun " + self.get_son((level - 2), inlaw)
        else:
            if reltocommon[level - 2] == self.REL_FATHER:
                # Brother's son generation
                return t_inlaw + "erkek kardeşinin oğlunun %d kuşak torunu" % (level)
            elif reltocommon[level - 2] == self.REL_MOTHER:
                # Sister's son generation
                return t_inlaw + "kız kardeşinin oğlunun %d kuşak torunu" % (level)
            else:
                return t_inlaw + "kardeşinin oğlunun %d kuşak torunu" % (level)

    def get_niece(self, level, reltocommon, inlaw=""):
        """
        Return niece generation name
        """
        if inlaw == "":
            t_inlaw = ""
        else:
            t_inlaw = "kayın "

        if level == 2:
            if reltocommon[0] == self.REL_FATHER:
                # Brother's daughter
                return t_inlaw + "(erkek kardeşinden) yeğeni"
            elif reltocommon[0] == self.REL_MOTHER:
                # Sister's daughter
                return t_inlaw + "(kız kardeşinden) yeğeni"
            else:
                return t_inlaw + "(kardeşinden) yeğeni"
        elif level >= 2 and level <= 6:
            if reltocommon[level - 2] == self.REL_FATHER:
                # Brother's daughter generation
                if reltocommon[level - 3] == self.REL_FATHER:
                    # daughter of brother son
                    return "erkek kardeşinin oğlunun " + self.get_daughter(
                        (level - 2), inlaw
                    )
                elif reltocommon[level - 3] == self.REL_MOTHER:
                    # daughter of brother daughter
                    return "erkek kardeşinin kızının " + self.get_daughter(
                        (level - 2), inlaw
                    )
                else:
                    # Currently not used
                    return "erkek kardeşinin çocuğunun " + self.get_daughter(
                        (level - 2), inlaw
                    )
            elif reltocommon[level - 2] == self.REL_MOTHER:
                # Sister's daughter generation
                if reltocommon[level - 3] == self.REL_FATHER:
                    # daughter of sister son
                    return "kız kardeşinin oğlunun " + self.get_daughter(
                        (level - 2), inlaw
                    )
                elif reltocommon[level - 3] == self.REL_MOTHER:
                    # daughter of sister daughter
                    return "kız kardeşinin kızının " + self.get_daughter(
                        (level - 2), inlaw
                    )
                else:
                    # Currently not used
                    return "kız kardeşinin çocuğunun " + self.get_daughter(
                        (level - 2), inlaw
                    )
            else:
                return "kardeşinin çocuğunun " + self.get_daughter(level, inlaw)
        else:
            if reltocommon[level - 2] == self.REL_FATHER:
                # Brother's daughter generation
                return t_inlaw + "erkek kardeşinin kızının %d kuşak torunu" % (level)
            elif reltocommon[level - 2] == self.REL_MOTHER:
                # Sister's daughter generation
                return t_inlaw + "kız kardeşinin kızının %d kuşak torunu" % (level)
            else:
                return t_inlaw + "kardeşinin kızının %d kuşak torunu" % (level)

    def get_nephew_niece_unknown(self, level, reltocommon, inlaw=""):
        """
        Return nephew/niece generation name when gender unknown
        """
        if inlaw == "":
            t_inlaw = ""
        else:
            t_inlaw = "kayın "

        if reltocommon[level - 2] == self.REL_FATHER:
            # Brother's descendant
            return t_inlaw + "erkek kardeşinin " + _child_level[level - 1]
        elif reltocommon[level - 2] == self.REL_MOTHER:
            # Sister's descendant
            return t_inlaw + "kız kardeşinin " + _child_level[level - 1]
        else:
            return t_inlaw + "kardeşinin " + _child_level[level - 1]

    def get_level(self, level, gender):
        """
        Return level name depend of gender
        """
        if gender == Person.MALE:
            if level < len(_level_name_male):
                return _level_name_male[level]
            else:
                return "%d" % level
        elif gender == Person.FEMALE:
            if level < len(_level_name_female):
                return _level_name_female[level]
            else:
                return "%d" % level
        else:
            if level < len(_level_name):
                return _level_name[level]
            else:
                return "%d" % level

    def get_cousin_level(self, level, gender):
        """
        Return level name depend of gender
        """
        if gender == Person.MALE:
            if level < len(_level_name_male):
                return _level_name_male[level - 1]
            else:
                return "%d" % level
        elif gender == Person.FEMALE:
            if level < len(_level_name_female):
                return _level_name_female[level - 1]
            else:
                return "%d" % level
        else:
            if level < len(_level_name):
                return _level_name[level - 1]
            else:
                return "%d" % level

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

        Ga: The number of generations between the main person and the
            common ancestor.

        Gb: The number of generations between the other person and the
            common ancestor.

        gender_a : gender of person a

        gender_b : gender of person b

        reltocommon_a : relation path to common ancestor or common
                        Family for person a.
                        Note that length = Ga
        reltocommon_b : relation path to common ancestor or common
                        Family for person b.
                        Note that length = Gb

        in_law_a : True if path to common ancestors is via the partner
                          of person a

        in_law_b : True if path to common ancestors is via the partner
                          of person b

        only_birth : True if relation between a and b is by birth only
                            False otherwise

        more see in relationship.py get_single_relationship_string()
        """

        if only_birth:
            step = ""
        else:
            step = self.STEP

        if in_law_a or in_law_b:
            inlaw = self.INLAW
        else:
            inlaw = ""

        t_inlaw = ""

        # b is the same person as a
        if Ga == Gb == 0:
            rel_str = "aynı kişi"

        elif Ga == 0:
            # b is son/descendant of a

            if gender_b == Person.MALE:
                if inlaw and Gb == 1 and not step:
                    # Curretly not used.
                    rel_str = "damadı"
                else:
                    rel_str = self.get_son(Gb, inlaw)

            elif gender_b == Person.FEMALE:
                if inlaw and Gb == 1 and not step:
                    # Curretly not used.
                    rel_str = "gelini"
                else:
                    rel_str = self.get_daughter(Gb, inlaw)

            else:
                rel_str = self.get_child_unknown(Gb, inlaw)

        elif Gb == 0:
            # b is parent/grand parent of a

            if gender_b == Person.MALE:
                if inlaw and Gb == 1 and not step:
                    # Currently nod used.
                    rel_str = "kaynatası"
                else:
                    rel_str = self.get_father(Ga, reltocommon_a, inlaw)

            elif gender_b == Person.FEMALE:
                if inlaw and Gb == 1 and not step:
                    # Currently nod used.
                    rel_str = "kaynanası"
                else:
                    rel_str = self.get_mother(Ga, reltocommon_a, inlaw)

            else:
                rel_str = self.get_parent_unknown(Ga, reltocommon_a, inlaw)

        elif Ga == Gb == 1:
            # Family, brother/sister
            # not used, leave it just in case
            # because should be handled
            # by get_sibling_relationship_string
            # that called in parent RelationshipCalculator
            # see Relationship.py

            if gender_b == Person.MALE:
                if inlaw and not step:
                    rel_str = "erkek kardeşi"
                else:
                    # Currently nod used.
                    rel_str = "üvey erkek kardeşi"

            elif gender_b == Person.FEMALE:
                if inlaw and not step:
                    rel_str = "kız kardeşi"
                else:
                    # Currently nod used.
                    rel_str = "üvey kız kardeşi"
            else:
                rel_str = "kardeşi"

        elif Gb == 1 and Ga > 1:
            # b is aunt/uncle of a

            if gender_b == Person.MALE:
                rel_str = self.get_uncle(Ga, reltocommon_a, inlaw)
            elif gender_b == Person.FEMALE:
                rel_str = self.get_aunt(Ga, reltocommon_a, inlaw)
            else:
                rel_str = self.get_uncle_aunt_unknown(Ga, reltocommon_a, inlaw)

        elif Ga == 1 and Gb > 1:
            # b is niece/nephew of a

            if gender_b == Person.MALE:
                rel_str = self.get_nephew(Gb, reltocommon_b, inlaw)
            elif gender_b == Person.FEMALE:
                rel_str = self.get_niece(Gb, reltocommon_b, inlaw)
            else:
                rel_str = self.get_nephew_niece_unknown(Gb, reltocommon_b, inlaw)

        elif Ga > 1 and Gb > 1:
            # b is (cousin/far aunt/far  uncle/far niece/far nephew) of a

            if Ga > Gb:
                # b is far aunt/far  uncle of a
                level = Ga - Gb + 1
                if level >= 3:  # it is right or???
                    level_name = self.get_level(Gb + 1, gender_b)
                else:
                    level_name = self.get_level(Gb, gender_b)

                if gender_b == Person.MALE:
                    # b is far  uncle
                    if inlaw != "":
                        # Currently not used.
                        t_inlaw = " "
                    if level < len(_parent_level):
                        rel_str = t_inlaw + "%s kuzeni(kuşağı)" % (_parent_level[level])
                    else:
                        rel_str = t_inlaw + "%s üstsoyunun kuzeni(kuşağı)" % (
                            _level_name[level - 1]
                        )
                elif gender_b == Person.FEMALE:
                    # b is far aunt
                    if inlaw != "":
                        # Currently not used.
                        t_inlaw = " "
                    if level < len(_aunt_level):
                        rel_str = t_inlaw + "%s kuzeni(kuşağı)" % (_parent_level[level])
                    else:
                        rel_str = t_inlaw + "%s üstsoyunun kuzeni(kuşağı)" % (
                            _level_name[level - 1]
                        )
                else:
                    if inlaw != "":
                        # Currently not used.
                        t_inlaw = " "
                    if level == 2:
                        rel_str = t_inlaw + "%s kuzeni(kuşağı)" % (_parent_level[level])
                    else:
                        rel_str = t_inlaw + "%s üstsoyunun kuzeni(kuşağı)" % (
                            _level_name[level - 1]
                        )

            elif Ga < Gb:
                # b is far niece/far nephew of a
                level_name = self.get_level(Ga, gender_b)
                level = Gb - Ga + 1

                if gender_b == Person.MALE:
                    # b is far nephew
                    if level == 2:
                        rel_str = "%s yeğeni" % level_name
                    else:
                        rel_str = "%s yeğeninin %s" % (
                            level_name,
                            _son_level[level - 2],
                        )
                elif gender_b == Person.FEMALE:
                    # b is far niece
                    if level == 2:
                        rel_str = "%s yeğeni" % level_name
                    else:
                        rel_str = "%s yeğeninin %s" % (
                            level_name,
                            _daughter_level[level - 2],
                        )
                else:
                    if level == 2:
                        rel_str = "%s yeğeni" % level_name
                    else:
                        rel_str = "%s yeğeninin %s" % (
                            level_name,
                            _child_level[level - 2],
                        )

            else:  # Gb == Ga
                # b is cousin of a
                level_name = self.get_cousin_level(Ga, gender_b)
                if gender_b == Person.MALE:
                    if inlaw != "":
                        # Currently not used.
                        t_inlaw = " "
                    rel_str = t_inlaw + "%s kuzeni" % level_name
                elif gender_b == Person.FEMALE:
                    if inlaw != "":
                        # Currently not used.
                        t_inlaw = " "
                    rel_str = t_inlaw + "%s kuzeni" % level_name
                else:
                    if inlaw != "":
                        # Currently not used.
                        t_inlaw = " "
                    rel_str = t_inlaw + "%s kuzeni" % level_name

        else:
            # A program should never goes there, but...
            rel_str = "sonsuz ilişki derecesi"

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
        Generate a text with information, how far away is a group of persons
        from a main person
        """
        if Ga == Gb == 0:
            return "aynı kişi"
        if 0 == Ga:
            # These are descendants
            if 1 == Gb:
                return "çocukları"
            if 2 == Gb:
                return "torunları"
            if 3 == Gb:
                return "torunlarının çocukları"
            if 4 == Gb:
                return "torunlarının torunları"
            return "torunlarının torunlarından altsoya ait torunları"
        if 0 == Gb:
            # These are parents/grand parents
            if 1 == Ga:
                return "ebeveynleri"
            if 2 == Ga:
                return "dedeleri ve nineleri"
            if 3 == Ga:
                return "büyük dedeleri ve haminneleri"
            if 4 == Ga:
                return "büyük büyük dedeleri ve nineleri"
            return "büyük büyük dedeleri ve ninelerinden üstsoya ait ataları"
        if 1 == Ga == Gb:
            return "kardeşleri"
        if 1 == Gb and Ga > 1:
            return "ebeveynlerinin kardeşleri"
        if 1 < Gb and 1 == Ga:
            return "yeğenleri"
        if 1 < Ga and 1 < Gb:
            return "uzak akrabaları"
        return "arasındaki ilişki belirsiz"

    def get_sibling_relationship_string(
        self, sib_type, gender_a, gender_b, in_law_a=False, in_law_b=False
    ):
        if in_law_a or in_law_b:
            inlaw = self.INLAW
        else:
            inlaw = ""

        if sib_type == self.NORM_SIB:
            if not inlaw:
                if gender_b == Person.MALE:
                    rel_str = "erkek kardeşi"
                elif gender_b == Person.FEMALE:
                    rel_str = "kız kardeşi"
                else:
                    rel_str = "kardeşi"
            else:
                if gender_b == Person.MALE:
                    rel_str = "erkek kardeşi"
                elif gender_b == Person.FEMALE:
                    rel_str = "kız kardeşi"
                else:
                    rel_str = "kardeşi"
        elif sib_type == self.UNKNOWN_SIB:
            if not inlaw:
                if gender_b == Person.MALE:
                    rel_str = "erkek kardeşi"
                elif gender_b == Person.FEMALE:
                    rel_str = "kız kardeşi"
                else:
                    rel_str = "kardeşi"
            else:
                if gender_b == Person.MALE:
                    rel_str = "erkek kardeşi"
                elif gender_b == Person.FEMALE:
                    rel_str = "kız kardeşi"
                else:
                    rel_str = "kardeşi"
        else:
            rel_str = "arasındaki ilişki belirsiz"
        return rel_str


if __name__ == "__main__":
    # Test function. Call it as follows from the command line (so as to find
    #        imported modules):
    #    export PYTHONPATH=/path/to/gramps/src
    #    python src/plugins/rel/rel_tr.py

    """
    TRANSLATORS, copy this if statement at the bottom of your
    rel_xx.py module, and test your work with:
    python src/plugins/rel/rel_xx.py
    """
    from gramps.gen.relationship import test

    RC = RelationshipCalculator()
    test(RC, True)

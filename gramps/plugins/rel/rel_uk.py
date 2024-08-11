# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2005  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2013       Oleh Petriv <olehsbox[at]yahoo.com>
# Copyright (C) 2013       Fedir Zinchuk <fedikw[at]gmail.com>
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
# gramps/plugins/rel/rel_uk.py
# UA: Пояснення щодо родинних відносин див. relationship.py
# EN: Ukrainian relationship calculator. For more information see relationship.py

"""
Ukrainian-specific definitions of relationships
"""

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------

from gramps.gen.lib import Person
import gramps.gen.relationship

# -------------------------------------------------------------------------


# Relationship levels

_level_name = [
    "",
    "рідний(-на)",
    "двоюрідний(-на)",
    "троюрідний(-на)",
    "чотириюрідний(-на)",
    "п'ятиюрідний(-на)",
    "шестиюрідний(-на)",
    "семиюрідний(-на)",
    "восьмиюрідний(-на)",
    "дев'ятиюрідний(-на)",
    "десятиюрідний(-на)",
    "одинадцятиюрідний(-на)",
    "дванадцятиюрідний(-на)",
    "тринадцятиюрідний(-на)",
    "чотирнадцятиюрідний(-на)",
    "п'ятнадцятиюрідний(-на)",
    "шістнадцятиюрідний(-на)",
    "сімнадцятиюрідний(-на)",
    "вісімнадцятиюрідний(-на)",
    "дев'ятнадцятиюрідний(-на)",
    "двадцятиюрідний(-на)",
]
_level_name_male = [
    "",
    "рідний",
    "двоюрідний",
    "троюрідний",
    "чотириюрідний",
    "п'ятиюрідний",
    "шестиюрідний",
    "семиюрідний",
    "восьмиюрідний",
    "дев'ятиюрідний",
    "десятиюрідний",
    "одинадцятиюрідний",
    "дванадцятиюрідний",
    "тринадцятиюрідний",
    "чотирнадцятиюрідний",
    "п'ятнадцятиюрідний",
    "шістнадцятиюрідний",
    "сімнадцятиюрідний",
    "вісімнадцятиюрідний",
    "дев'ятнадцятиюрідний",
    "двадцятиюрідний",
]
_level_name_female = [
    "",
    "рідна",
    "двоюрідна",
    "троюрідна",
    "чотириюріднa",
    "п'ятиюрідна",
    "шестиюрідна",
    "семиюрідна",
    "восьмиюрідна",
    "дев'ятиюрідна",
    "десятиюрідна",
    "одинадцятиюрідна",
    "дванадцятиюрідна",
    "тринадцятиюрідна",
    "чотирнадцятиюрідна",
    "п'ятнадцятиюрідна",
    "шістнадцятиюрідна",
    "сімнадцятиюрідна",
    "вісімнадцятиюрідна",
    "дев'ятнадцятиюрідна",
    "двадцятиюрідна",
]

_son_level = [
    "",
    "син",
    "внук",
    "правнук",
    "праправнук",
]

_daughter_level = [
    "",
    "дочка",
    "онука",
    "правнучка",
    "праправнучка",
]

_father_level = [
    "",
    "батько",
    "дід",
    "прадід",
    "прапрадід",
]

_mother_level = [
    "",
    "мати",
    "баба",
    "прабаба",
    "прапрабаба",
]

_uncle_level = [
    "",
    "брат",  # not used, just for keep count
    "дядько",
    "дід",
    "прадід",
    "прапрадід",
]

_aunt_level = [
    "",
    "сестра",  # not used, just for keep count
    "тітка",
    "баба",
    "прабаба",
    "прапрабаба",
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

    def __init__(self):
        gramps.gen.relationship.RelationshipCalculator.__init__(self)

    def get_sword_distaff(self, level, reltocommon, gender=Person.UNKNOWN):
        """
        Generate relationships 'by male line' or 'by female line',
        specific for Ukraine
        """
        if level <= 1:
            return ""

        # test the relation line
        by_line = ""
        for g in reltocommon:
            if by_line and by_line != g:
                by_line = ""
                break
            by_line = g

        if by_line == self.REL_FATHER and gender == Person.MALE:
            # by male line
            return " по чоловічій лінії"
        elif by_line == self.REL_MOTHER and gender == Person.FEMALE:
            # by male line
            return " по жіночій лінії"
        elif reltocommon[0] == self.REL_FATHER:
            # From father's side
            return " по батькові"
        elif reltocommon[0] == self.REL_MOTHER:
            # From mother's side
            return " по матері"
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
            t_inlaw = "названий "

        if level >= 0 and level < len(_son_level):
            return t_inlaw + _son_level[level]
        else:
            return t_inlaw + "пра(пра)внук у %d поколінні" % (level + 1)

    def get_daughter(self, level, inlaw=""):
        """
        Provides information how much female descendant is related to this person
        """
        # Define if the person is natural relative or in law
        if inlaw == "":
            t_inlaw = ""
        else:
            t_inlaw = "названа "

        if level >= 0 and level < len(_daughter_level):
            return t_inlaw + _daughter_level[level]
        else:
            return t_inlaw + "пра(пра)внучка у %d поколінні" % (level + 1)

    def get_child_unknown(self, level, inlaw=""):
        """
        Provides information how much descendant of unknown gender is related to this person
        """
        # Define if the person is natural relative or in law
        if inlaw == "":
            t_inlaw = ""
        else:
            t_inlaw = "названий(на) "

        if level == 1:
            return t_inlaw + "внук(а)"
        else:
            return t_inlaw + "пра(пра)внук(а) у %d поколінні" % (level + 1)

    def get_father(self, level, reltocommon, inlaw=""):
        """
        Provides information how much male ancestor (for example father)
        is related to the given person
        """
        if inlaw == "":
            t_inlaw = ""
        else:
            t_inlaw = "названий "

        if level >= 0 and level < len(_father_level):
            # If you know exact name of relationship - use it
            if level == 1:
                # Father
                return t_inlaw + _father_level[level]
            else:
                # Grandfather, Greatgrandfather, Greatgreatgrandfather
                return (
                    t_inlaw
                    + _father_level[level]
                    + self.get_sword_distaff(level, reltocommon, Person.MALE)
                )
        else:
            # For deep generations
            return (
                t_inlaw
                + "пра(пра)дід у %d поколінні" % (level + 1)
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
            t_inlaw = "названа "

        if level >= 0 and level < len(_mother_level):
            # If you know exact name of relationship - use it
            if level == 1:
                # Mother
                return t_inlaw + _mother_level[level]

            else:
                # Grandmother, Greatgrandmother, Greatgreatgrandmother
                return (
                    t_inlaw
                    + _mother_level[level]
                    + self.get_sword_distaff(level, reltocommon, Person.FEMALE)
                )
        else:
            # For deep generations
            return (
                t_inlaw
                + "пра(пра)баба у %d поколінні" % (level + 1)
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
            t_inlaw = "названий "

        if level == 1:
            return t_inlaw + "батько/мати"
        else:
            return (
                t_inlaw
                + "пра(пра)- дід/баба у %d поколінні" % (level + 1)
                + self.get_sword_distaff(level, reltocommon)
            )

    def get_uncle(self, level, reltocommon, inlaw=""):
        """
        Return ancle generation name
        """

        if reltocommon[0] == self.REL_FATHER:
            # from Father
            if level < len(_uncle_level):
                if level == 2:
                    return _uncle_level[level] + " (стрийко)"
                else:
                    return "двоюрідний " + _uncle_level[level] + " по батькові"
            else:
                return "двоюрідний пра(пра)дід в %d поколінні по батькові" % (level)
        elif reltocommon[0] == self.REL_MOTHER:
            # from Mother
            if level < len(_uncle_level):
                if level == 2:
                    return _uncle_level[level] + " (вуйко)"
                else:
                    return "двоюрідний " + _uncle_level[level] + " по матері"
            else:
                return "двоюрідний пра(пра)дід в %d поколінні по матері" % (level)
        else:
            if level == 2:
                return "дядько (стрийко/вуйко)"
            else:
                return "двоюрідний пра(пра)дід в %d поколінні" % (level)

    def get_aunt(self, level, reltocommon, inlaw=""):
        """
        Return aunt generation name
        """

        if reltocommon[0] == self.REL_FATHER:
            # from Father
            if level < len(_aunt_level):
                if level == 2:
                    return _aunt_level[level] + " (стрийна)"
                else:
                    return "двоюрідна " + _aunt_level[level] + " по батькові"
            else:
                return "двоюрідна пра(пра)баба в %d поколінні по батькові" % (level)
        elif reltocommon[0] == self.REL_MOTHER:
            # from Mother
            if level < len(_aunt_level):
                if level == 2:
                    return _aunt_level[level] + " (вуйна)"
                else:
                    return "двоюрідна " + _aunt_level[level] + " по матері"
            else:
                return "двоюрідна пра(пра)баба в %d поколінні по матері" % (level)
        else:
            if level == 2:
                return "тітка (стрийна/вуйна)"
            else:
                return "двоюрідна пра(пра)баба в %d поколінні" % (level)

    def get_uncle_aunt_unknown(self, level, reltocommon, inlaw=""):
        """
        Return uncle/aunt generation name when gender unknown
        """

        if reltocommon[0] == self.REL_FATHER:
            # from Father
            if level == 2:
                return "дядько/тітка (стрийко)"
            else:
                return "двоюрідний дід/баба в %d поколінні по батькові" % (level)
        elif reltocommon[0] == self.REL_MOTHER:
            # from Mother
            if level == 2:
                return "дядько/тітка (вуйко)"
            else:
                return "двоюрідний дід/баба в %d поколінні по матері" % (level)
        else:
            if level == 2:
                return "дядько/тітка"
            else:
                return "двоюрідний дід/баба в %d поколінні" % (level)

    def get_nephew(self, level, reltocommon, inlaw=""):
        """
        Return nephew generation name
        """
        if inlaw == "":
            t_inlaw = ""
        else:
            t_inlaw = "названий "

        if level == 2:
            if reltocommon[0] == self.REL_FATHER:
                # Brother's son
                return t_inlaw + "небіж (братанець)"
            elif reltocommon[0] == self.REL_MOTHER:
                # Sister's son
                return t_inlaw + "небіж (сестринець)"
            else:
                return t_inlaw + "небіж (братанець/сестринець)"
        elif level >= 2 and level <= 6:
            if reltocommon[level - 2] == self.REL_FATHER:
                # Brother's son generation
                if reltocommon[level - 3] == self.REL_FATHER:
                    # Son of brother son
                    return self.get_son((level - 2), inlaw) + " небожа по брату"
                elif reltocommon[level - 3] == self.REL_MOTHER:
                    # Son of brother daughter
                    return self.get_son((level - 2), inlaw) + " небоги по брату"
                else:
                    return self.get_son((level - 2), inlaw) + " небожа/небоги по брату"
            elif reltocommon[level - 2] == self.REL_MOTHER:
                # Sister's son generation
                if reltocommon[level - 3] == self.REL_FATHER:
                    # Son of sister son
                    return self.get_son((level - 2), inlaw) + " небожа по сестрі"
                elif reltocommon[level - 3] == self.REL_MOTHER:
                    # Son of sister daughter
                    return self.get_son((level - 2), inlaw) + " небоги по сестрі"
                else:
                    return self.get_son((level - 2), inlaw) + " небожа/небоги по сестрі"
            else:
                return self.get_son((level - 2), inlaw) + " небожа/небоги"
        else:
            if reltocommon[level - 2] == self.REL_FATHER:
                # Brother's son generation
                return t_inlaw + "чоловічий нащадок у %d поколінні брата" % (level)
            elif reltocommon[level - 2] == self.REL_MOTHER:
                # Sister's son generation
                return t_inlaw + "чоловічий нащадок у %d поколінні сестри" % (level)
            else:
                return t_inlaw + "чоловічий нащадок у %d поколінні брата/сестри" % (
                    level
                )

    def get_niece(self, level, reltocommon, inlaw=""):
        """
        Return niece generation name
        """
        if inlaw == "":
            t_inlaw = ""
        else:
            t_inlaw = "названий "

        if level == 2:
            if reltocommon[0] == self.REL_FATHER:
                # Brother's daughter
                return t_inlaw + "небога (братанка)"
            elif reltocommon[0] == self.REL_MOTHER:
                # Sister's daughter
                return t_inlaw + "небога (сестрениця)"
            else:
                return t_inlaw + "небога (братанка/сестрениця)"
        elif level >= 2 and level <= 6:
            if reltocommon[level - 2] == self.REL_FATHER:
                # Brother's daughter generation
                if reltocommon[level - 3] == self.REL_FATHER:
                    # daughter of brother son
                    return self.get_daughter((level - 2), inlaw) + " небожа по брату"
                elif reltocommon[level - 3] == self.REL_MOTHER:
                    # daughter of brother daughter
                    return self.get_daughter((level - 2), inlaw) + " небоги по брату"
                else:
                    return (
                        self.get_daughter((level - 2), inlaw)
                        + " небожа/небоги по брату"
                    )
            elif reltocommon[level - 2] == self.REL_MOTHER:
                # Sister's daughter generation
                if reltocommon[level - 3] == self.REL_FATHER:
                    # daughter of sister son
                    return self.get_daughter((level - 2), inlaw) + " небожа по сестрі"
                elif reltocommon[level - 3] == self.REL_MOTHER:
                    # daughter of sister daughter
                    return self.get_daughter((level - 2), inlaw) + " небоги по сестрі"
                else:
                    return (
                        self.get_daughter((level - 2), inlaw)
                        + " небожа/небоги по сестрі"
                    )
            else:
                return self.get_daughter(level, inlaw) + " небожа/небоги"
        else:
            if reltocommon[level - 2] == self.REL_FATHER:
                # Brother's daughter generation
                return t_inlaw + "жіночий нащадок у %d поколінні брата" % (level)
            elif reltocommon[level - 2] == self.REL_MOTHER:
                # Sister's daughter generation
                return t_inlaw + "жіночий нащадок у %d поколінні сестри" % (level)
            else:
                return t_inlaw + "жіночий нащадок у %d поколінні брата/сестри" % (level)

    def get_nephew_niece_unknown(self, level, reltocommon, inlaw=""):
        """
        Return nephew/niece generation name when gender unknown
        """
        if inlaw == "":
            t_inlaw = ""
        else:
            t_inlaw = "названий "

        if reltocommon[level - 2] == self.REL_FATHER:
            # Brother's descendant
            return t_inlaw + "нащадок в %d поколінні брата" % (level)
        elif reltocommon[level - 2] == self.REL_MOTHER:
            # Sister's descendant
            return t_inlaw + "нащадок в %d поколінні сестри" % (level)
        else:
            return t_inlaw + "нащадок в %d поколінні брата aбо сестри" % (level)

    def get_level(self, level, gender):
        """
        Return level name depend of gender
        """
        if gender == Person.MALE:
            if level < len(_level_name_male):
                return _level_name_male[level]
            else:
                return "%d-юрідний" % level
        elif gender == Person.FEMALE:
            if level < len(_level_name_female):
                return _level_name_female[level]
            else:
                return "%d-юрідна" % level
        else:
            if level < len(_level_name):
                return _level_name[level]
            else:
                return "%d-юрідний(на)" % level

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
            common ancestor. (кількість поколінь між прямими родичами особи:
            сини, батьки, бабусі...)

        Gb: The number of generations between the other person and the
            common ancestor. (кількість поколінь між іншою особою
            і спільним предком)

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
            rel_str = "та сама особа"

        elif Ga == 0:
            # b is son/descendant of a

            if gender_b == Person.MALE:
                if inlaw and Gb == 1 and not step:
                    rel_str = "зять"
                else:
                    rel_str = self.get_son(Gb, inlaw)

            elif gender_b == Person.FEMALE:
                if inlaw and Gb == 1 and not step:
                    rel_str = "невістка"
                else:
                    rel_str = self.get_daughter(Gb, inlaw)

            else:
                rel_str = self.get_child_unknown(Gb, inlaw)

        elif Gb == 0:
            # b is parent/grand parent of a

            if gender_b == Person.MALE:
                if inlaw and Gb == 1 and not step:
                    rel_str = "тесть"
                else:
                    rel_str = self.get_father(Ga, reltocommon_a, inlaw)

            elif gender_b == Person.FEMALE:
                if inlaw and Gb == 1 and not step:
                    rel_str = "теща"
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
                    rel_str = "рідний брат"
                else:
                    rel_str = "напів рідний брат"

            elif gender_b == Person.FEMALE:
                if inlaw and not step:
                    rel_str = "рідна сестра"
                else:
                    rel_str = "напів рідна сестра"
            else:
                rel_str = "брат/сестра"

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
                        t_inlaw = "названий "
                    if level < len(_uncle_level):
                        rel_str = t_inlaw + "%s %s" % (level_name, _uncle_level[level])
                    else:
                        rel_str = t_inlaw + "%s пра(пра)дід в %d поколінні" % (
                            level_name,
                            (level),
                        )
                elif gender_b == Person.FEMALE:
                    # b is far aunt
                    if inlaw != "":
                        t_inlaw = "названа "
                    if level < len(_aunt_level):
                        rel_str = t_inlaw + "%s %s" % (level_name, _aunt_level[level])
                    else:
                        rel_str = t_inlaw + "%s пра(пра)баба в %d поколінні" % (
                            level_name,
                            (level),
                        )
                else:
                    if inlaw != "":
                        t_inlaw = "названий(на) "
                    if level == 2:
                        rel_str = t_inlaw + "%s дядько/тітка" % level_name
                    else:
                        rel_str = t_inlaw + "%s пра(пра)- дід/баба в %d поколінні" % (
                            level_name,
                            (level),
                        )

            elif Ga < Gb:
                # b is far niece/far nephew of a
                level_name = self.get_level(Ga, gender_b)
                level = Gb - Ga + 1

                if gender_b == Person.MALE:
                    # b is far nephew
                    if level == 2:
                        rel_str = "%s небіж" % level_name
                    else:
                        rel_str = "%s пра(пра)внук у %d поколінні" % (level_name, level)
                    # rel_str = "%s %s" % (level_name, self.get_nephew(level, reltocommon_b, inlaw))
                elif gender_b == Person.FEMALE:
                    # b is far niece
                    if level == 2:
                        rel_str = "%s небога" % level_name
                    else:
                        rel_str = "%s пра(пра)внучка у %d поколінні" % (
                            level_name,
                            level,
                        )
                    # rel_str = "%s %s"  % (level_name, self.get_niece(level, reltocommon_b, inlaw))
                else:
                    rel_str = "%s пра(пра)внук(а) у %d поколінні" % level
                    # rel_str = "%s %s" % (level_name, self.get_nephew_niece_unknown(level, reltocommon_b, inlaw))

            else:  # Gb == Ga
                # b is cousin of a
                level_name = self.get_level(Ga, gender_b)

                if gender_b == Person.MALE:
                    if inlaw != "":
                        t_inlaw = "названий "
                    rel_str = t_inlaw + "%s брат" % level_name
                elif gender_b == Person.FEMALE:
                    if inlaw != "":
                        t_inlaw = "названа "
                    rel_str = t_inlaw + "%s сестра" % level_name
                else:
                    if inlaw != "":
                        t_inlaw = "названий(на) "
                    rel_str = t_inlaw + "%s брат/сестра" % level_name

        else:
            # A program should never goes there, but...
            rel_str = "невизначений ступінь спорідненості"

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
            return "та сама особа"
        if 0 == Ga:
            # These are descendants
            if 1 == Gb:
                return "діти"
            if 2 == Gb:
                return "внуки"
            if 3 == Gb:
                return "правнуки"
            if 4 == Gb:
                return "праправнуки"
            return "прапрапра(n)внуки"
        if 0 == Gb:
            # These are parents/grand parents
            if 1 == Ga:
                return "батьки"
            if 2 == Ga:
                return "діди/баби"
            if 3 == Ga:
                return "прадіди/прабаби"
            if 4 == Ga:
                return "прапращури"
            return "прапрапра(n)щури"
        if 1 == Ga == Gb:
            return "батьки"
        if 1 == Gb and Ga > 1:
            return "дядьки (вуйки, стрийки) і тітки"
        if 1 < Gb and 1 == Ga:
            return "небожі по братові і сестрі"
        if 1 < Ga and 1 < Gb:
            return "дальня родина"
        return "відносини невідомі"

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
                    rel_str = "рідний брат"
                elif gender_b == Person.FEMALE:
                    rel_str = "рідна сестра"
                else:
                    rel_str = "рідний(а) брат або сестра"
            else:
                if gender_b == Person.MALE:
                    rel_str = "названий брат"
                elif gender_b == Person.FEMALE:
                    rel_str = "названа сестра"
                else:
                    rel_str = "названий(а) брат або сестра"
        elif sib_type == self.UNKNOWN_SIB:
            if not inlaw:
                if gender_b == Person.MALE:
                    rel_str = "брат"
                elif gender_b == Person.FEMALE:
                    rel_str = "сестра"
                else:
                    rel_str = "брат або сестра"
            else:
                if gender_b == Person.MALE:
                    rel_str = "швагро"
                elif gender_b == Person.FEMALE:
                    rel_str = "братова"
                else:
                    rel_str = "швагро або братова"
        elif sib_type == self.HALF_SIB_FATHER:
            if gender_b == Person.MALE:
                rel_str = "єдинокровний(напіврідний) брат"
            elif gender_b == Person.FEMALE:
                rel_str = "єдинокровна(напіврідна) сестра"
            else:
                rel_str = "напіврідний(а) брат/сестра"
        elif sib_type == self.HALF_SIB_MOTHER:
            if gender_b == Person.MALE:
                rel_str = "єдинокровний(напіврідний) брат"
            elif gender_b == Person.FEMALE:
                rel_str = "єдинокровна(напіврідна) сестра"
            else:
                rel_str = "напіврідний(а) брат/сестра"
        elif sib_type == self.STEP_SIB:
            if gender_b == Person.MALE:
                rel_str = "зведений брат"
            elif gender_b == Person.FEMALE:
                rel_str = "зведена сестра"
            else:
                rel_str = "зведений брат або сестра"
        else:
            rel_str = "невизначена ступінь родинних відносин"
        return rel_str


if __name__ == "__main__":
    # Test function. Call it as follows from the command line (so as to find
    #        imported modules):
    #    export PYTHONPATH=/path/to/gramps/src
    #    python src/plugins/rel/rel_pl.py

    """
    TRANSLATORS, copy this if statement at the bottom of your
    rel_xx.py module, and test your work with:
    python src/plugins/rel/rel_xx.py
    """
    from gramps.gen.relationship import test
    import signal
    import sys

    # If someone go out
    def goodby(signal, frame):
        print("No more Drink!")
        sys.exit(0)

    signal.signal(signal.SIGINT, goodby)
    # Run test
    RC = RelationshipCalculator()
    test(RC, True)

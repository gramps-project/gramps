# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2005  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2009-2010  Andrew I Baznikin
# Copyright (C) 2025       Petr E. Fedorov
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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

# Written by Alex Roitman, largely based on relationship.py by Don Allingham.
# Re-written from scratch by Petr E. Fedorov
"""
Russian-specific definitions of relationships
"""

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------

from gramps.gen.lib import Person
import gramps.gen.relationship

# -------------------------------------------------------------------------


_spouses = {  # by a gender of the spouse
    Person.MALE: ["муж", "мужа"],
    Person.FEMALE: ["жена", "жены"],
    Person.UNKNOWN: ["супруг/супруга", "супруга/супруги"],
}

_spouses_plural = ["супруги", "супругов"]


def _spouse_gender(gender):
    if gender == Person.MALE:
        gender = Person.FEMALE
    elif gender == Person.FEMALE:
        gender = Person.MALE
    else:
        gender = Person.UNKNOWN
    return gender


def _parent_gender(parent):
    if parent in (
        gramps.gen.relationship.RelationshipCalculator.REL_MOTHER,
        gramps.gen.relationship.RelationshipCalculator.REL_MOTHER_NOTBIRTH,
    ):
        return Person.FEMALE
    if parent in (
        gramps.gen.relationship.RelationshipCalculator.REL_FATHER,
        gramps.gen.relationship.RelationshipCalculator.REL_FATHER_NOTBIRTH,
    ):
        return Person.MALE
    return Person.UNKNOWN


# -------------------------------------------------------------------------
#
# Relative
#
# -------------------------------------------------------------------------
class Relative:
    """
    Relative is an abstract class that represents a relationship
    between to people defined by people's relative position in the
    family tree and some other parameters
    """

    NORM_SIB = gramps.gen.relationship.RelationshipCalculator.NORM_SIB
    HALF_SIB_MOTHER = gramps.gen.relationship.RelationshipCalculator.HALF_SIB_MOTHER
    HALF_SIB_FATHER = gramps.gen.relationship.RelationshipCalculator.HALF_SIB_FATHER
    STEP_SIB = gramps.gen.relationship.RelationshipCalculator.STEP_SIB
    UNKNOWN_SIB = gramps.gen.relationship.RelationshipCalculator.UNKNOWN_SIB

    step = {
        Person.MALE: ["неродной", "неродного"],
        Person.FEMALE: ["неродная", "неродной"],
        Person.UNKNOWN: ["неродной", "неродного"],
    }

    def __init__(self, gender_a, gender_b, in_law_a, in_law_b, only_birth):
        self.gender_a = gender_a
        self.gender_b = gender_b
        self.in_law_a = in_law_a
        self.in_law_b = in_law_b
        self.only_birth = only_birth

    def _get_designated_name(self, genitive=False):
        # pylint: disable=unused-argument
        return None

    def _get_descriptive_name(self, genitive=False):
        # pylint: disable=unused-argument
        return None

    def get_name(self, genitive):
        """
        Returns the name of the relationship.

        A relationship in Russian may have a designated name (i.e. 'тёща'-
        mother-in-law ) and may also be described in terms of the other
        relationships between people in the family tree (i.e.
        'мать жены'- mother of the wife)

        This method attempts to get these two names for the relationship and
        then returns them combined

        :param genitive: If False returns name in the nominative case, i.e.
                         'двоюродный брат'. Otherwise - in the genitive case
                         i.e. 'двоюродного брата'
        :type genitive: bool
        """

        # pylint: disable=assignment-from-none
        designated_name = self._get_designated_name(genitive)

        descriptive_name = self._get_descriptive_name(genitive)

        if designated_name is not None:
            if descriptive_name is not None and descriptive_name != designated_name:
                return f"{designated_name} ({descriptive_name})"
            return designated_name

        return descriptive_name  # may be None too

    def get_plural_name(self, genitive=False):
        """
        Returns the plural name of the relationship between people the
        family tree defined by Ga and Gb and some other parameters,
        i.e. 'братья и сёстры' or 'супруги двоюродных дядей и тёть'

        This method have different implementations for Direct-type
        relationships and for Collateral-type relationships (see below)

        :param genitive: If False returns the name in the nominative case, i.e.
                         'двоюродные братья и сёстры'. Otherwise - in the
                         genitive case i.e. 'двоюродных братьев и сестёр'
        :type genitive: bool
        """
        # pylint: disable=unused-argument
        return None


# -------------------------------------------------------------------------
#
# Direct
#
# -------------------------------------------------------------------------
class Direct(Relative):
    """
    Direct is an abstract class that represents direct relationships
    between to people defined by people's relative position in the
    family tree and some other parameters. 'Direct' means that one
    person in the relationship is an ancestor while the other is a descendant
    """

    special: dict[
        int, dict[bool, list[list[None] | dict[bool, list[str] | dict[int, list[str]]]]]
    ] = {}
    descriptive: dict[int, list[list[None | str]]] = {}
    descriptive_plurals: list[list[None | str]] = []

    prefixes = [
        None,  # брат, so no prefix ...
        None,  # сын/отец
        None,  # внук/дед
        None,  # правнук/прадед
        "дважды",  # дважды правнук/дважды прадед и т.д.
        "трижды",
        "четырежды",
        "пять раз",
        "шесть раз",
        "семь раз",
        "8 раз",
        "9 раз",
        "10 раз",
        "11 раз",
        "12 раз",
        "13 раз",
        "14 раз",
        "15 раз",
        "16 раз",
        "17 раз",
        "18 раз",
        "19 раз",
        "20 раз",
        "21 раз",
        "22 раза",
        "23 раза",
        "24 раза",
        "25 раз",
        "26 раз",
        "очень много раз",
    ]

    def __init__(self, level, gender_a, gender_b, in_law_a, in_law_b, only_birth):
        super().__init__(gender_a, gender_b, in_law_a, in_law_b, only_birth)
        self.level = level

    def _get_prefix(self, level):
        if level >= len(self.prefixes):
            return self.prefixes[-1]
        else:
            return self.prefixes[level]

    def _get_designated_name(self, genitive=False):
        """
        Returns a designated name for the Direct-type relationship, if any
        Otherwise returns None. Names of special relationships are kept in
        'special' instance (actually, class) variable defined in the concrete
        derived classes (Ancestor and Descendant)

        """
        try:
            # pylint: disable=no-member
            designated_name = self.special[self.gender_b][self.in_law_b][self.level]

            if isinstance(designated_name, dict):
                designated_name = designated_name[self.in_law_a]

                if isinstance(designated_name, dict):
                    designated_name = designated_name[self.gender_a]

            return designated_name[genitive]

        except (KeyError, IndexError):
            pass
        return None

    def _get_descriptive_name(self, genitive=False):
        """
        Returns a descriptive name for the Direct-type relationship, if any
        Otherwise returns None. Names of descriptive relationships are kept in
        'descriptive' instance (actually, class) variable defined in
        the concrete derived classes (Ancestor and Descendant)

        """
        try:

            if self.in_law_b:
                spouse_b = _spouses[self.gender_b][genitive] + " "
                # ... and gender_b is now the spouse's gender!
                gender_b = _spouse_gender(self.gender_b)

                genitive = True
            else:
                spouse_b = ""
                gender_b = self.gender_b

            if self.in_law_a:
                # genitive of spouse_a
                spouse_a = " " + _spouses[_spouse_gender(self.gender_a)][True]
            else:
                spouse_a = ""

            if self.only_birth is False:
                step = self.step[gender_b][genitive] + " "
            else:
                step = ""

            # pylint: disable=no-member
            if self.level >= len(self.descriptive[gender_b]) - 1:
                descriptive_name = self.descriptive[gender_b][-1][genitive].format(
                    self._get_prefix(self.level)
                )
            else:
                descriptive_name = self.descriptive[gender_b][self.level][genitive]

            return f"{spouse_b}{step}{descriptive_name}{spouse_a}"

        except (KeyError, IndexError):
            pass

        return None

    def get_plural_name(self, genitive=False):
        """
        Implements an abstract method Relative.get_plural_name() for
        Direct-type relationships, i.e. classes derived from Direct

        See Relative.get_pluarl_name() for more info
        """

        if self.in_law_b:
            spouse_b = _spouses_plural[genitive] + " "
            genitive = True
        else:
            spouse_b = ""

        if self.level >= len(self.descriptive_plurals) - 1:
            stereotyped_name = self.descriptive_plurals[-1][genitive].format(
                self._get_prefix(self.level)
            )
        else:
            stereotyped_name = self.descriptive_plurals[self.level][genitive]

        return f"{spouse_b}{stereotyped_name}"


# -------------------------------------------------------------------------
#
# Ancestor
#
# -------------------------------------------------------------------------
class Ancestor(Direct):
    """
    Ancestor is a concrete class that represents a relationship
    between the person and its ancestor
    """

    special = {
        Person.MALE: {  # gender_b is Person.MALE
            False: [  # in_law_b is False
                [None, None],
                {  # by in_law_a
                    True: {  # by gender_a
                        Person.MALE: ["тесть", "тестя"],
                        Person.FEMALE: ["свёкр", "свёкра"],
                    },
                },
            ],
            True: [  # in_law_b is True
                [None, None],
                {False: ["отчим", "отчима"]},  # by in_law_a
            ],
        },
        Person.FEMALE: {  # gender_b is Female
            False: [  # in_law_b is False
                [None, None],
                {  # by in_law_a
                    True: {  # by gender_a
                        Person.MALE: ["тёща", "тёщи"],
                        Person.FEMALE: ["свекровь", "свекрови"],
                    },
                },
            ],
            True: [  # in_law_b is True
                [None, None],
                {  # by in_law_a
                    False: ["мачеха", "мачехи"],
                },
            ],
        },
        Person.UNKNOWN: {  # gender_b is Unknown
            False: [  # in_law_b is False
                [None, None],
                {  # by in_law_a
                    True: {  # by gender_a
                        Person.MALE: ["тесть или тёща", "тестя или тёщи"],
                        Person.FEMALE: ["свёкр или свекровь", "свёкра или свекрови"],
                    },
                },
            ],
            True: [  # in_law_b is True
                [None, None],
                {  # by in_law_a
                    False: ["отчим или мачеха", "отчима или мачехи"],
                },
            ],
        },
    }

    descriptive_plurals = [
        [None, None],
        ["родители", "родителей"],
        ["дедушки и бабушки", "дедушек и бабушек"],
        ["прадедушки и прабабушки", "прадедушек и прабабушек"],
        ["{} прадедушки и прабабушки", "{} прадедушек и прабабушек"],
    ]

    descriptive = {
        Person.MALE: [
            [None, None],
            ["отец", "отца"],
            ["дедушка", "дедушки"],
            ["прадедушка", "прадедушки"],
            ["{} прадедушка", "{} прадедушки"],
        ],
        Person.FEMALE: [
            [None, None],
            ["мать", "матери"],
            ["бабушка", "бабушки"],
            ["прабабушка", "прабабушки"],
            ["{} прабабушка", "{} прабабушки"],
        ],
        Person.UNKNOWN: [
            [None, None],
            ["отец или мать", "отца или матери"],
            ["дедушка или бабушка", "дедушки или бабушки"],
            ["прадедушка или прабабушка", "прадедушки или прабабушки"],
            ["{} прадедушка или прабабушка", "{} прадедушки или прабабушки"],
        ],
    }


# -------------------------------------------------------------------------
#
# Descendant
#
# -------------------------------------------------------------------------
class Descendant(Direct):
    """
    Descendant is a concrete class that represents a relationship
    between the person and its descendant
    """

    special = {
        Person.MALE: {  # gender_b is Person.MALE
            True: [  # in_law_b is True
                [None, None],
                {
                    # in_law_a is False
                    False: ["зять", "зятя"]  # муж дочери
                },
            ],
            False: [  # in_law_b is False
                [None, None],
                {
                    # in_law_a is True
                    True: ["пасынок", "пасынка"]  # сын супруга
                },
            ],
        },
        Person.FEMALE: {  # gender_b is Person.FEMALE
            True: [  # in_law_b is True
                [None, None],
                {False: ["невестка", "невестки"]},  # жена сына
            ],
            False: [  # in_law_b is False
                [None, None],
                {
                    # in_law_a is True
                    True: ["падчерица", "падчерицы"]  # дочь супруга
                },
            ],
        },
        Person.UNKNOWN: {  # gender_b is Person.FEMALE
            True: [  # in_law_b is True
                [None, None],
                {
                    # in_law_a is False
                    False: ["зять или невестка", "зятя или невестки"]
                },
            ],
            False: [  # in_law_b is False
                [None, None],
                {
                    # in_law_a is True
                    True: ["пасынок или падчерица", "пасынка или падчерицы"]
                },
            ],
        },
    }

    descriptive = {
        Person.MALE: [
            [None, None],
            ["сын", "сына"],
            ["внук", "внука"],
            ["правнук", "правнука"],
            ["{} правнук", "{} правнука"],
        ],
        Person.FEMALE: [
            [None, None],
            ["дочь", "дочери"],
            ["внучка", "внучки"],
            ["правнучка", "правнучки"],
            ["{} правнучка", "{} правнучки"],
        ],
        Person.UNKNOWN: [
            [None, None],
            ["сын или дочь", "сына или дочери"],
            ["внук или внучка", "внука или внучки"],
            ["правнук или правнучка", "правнука или правнучки"],
            ["{} правнук или правнучкa", "{} правнука или правнучки"],
        ],
    }

    descriptive_plurals = [
        [None, None],
        ["дети", "детей"],
        ["внуки и внучки", "внуков и внучек"],
        ["правнуки и правнучки", "правнуков и правнучек"],
        ["{} правнуки и правнучки", "{} правнуков и правнучек"],
    ]


# -------------------------------------------------------------------------
#
# Collateral
#
# -------------------------------------------------------------------------
class Collateral(Relative):
    """
    Collateral is an abstract class that represents a relationship
    between two people who has common ancestor but neither of them is
    an ancestor of the other.
    """

    degrees = {
        Person.MALE: [
            ["", ""],
            ["двоюродный ", "двоюродного "],
            ["троюродный ", "троюродного "],
            ["четвероюродный ", "четвероюродного "],
            ["пятиюродный ", "пятиюродного "],
            ["шестиюродный ", "шестиюродного "],
            ["семиюродный ", "семиюродного "],
            ["восьмиюродный ", "восьмиюродного "],
            ["девятиюродный ", "девятиюродного "],
            ["десятиюродный ", "десятиюродного "],
            ["одиннацатиюродный ", "одиннацатиюродного "],
            ["двенадцатиюродный ", "двенадцатиюродного "],
            ["тринадцатиюродный ", "тринадцатиюродного "],
            ["четырнадцатиюродный ", "четырнадцатиюродного "],
            ["пятнадцатиюродный ", "пятнадцатиюродного "],
            ["шестнадцатиюродный ", "шестнадцатиюродного "],
            ["семнадцатиюродный ", "семнадцатиюродного "],
            ["восемнадцатиюродный ", "восемнадцатиюродного "],
            ["девятнадцатиюродный ", "девятнадцатиюродного "],
            ["двадцатиюродный ", "двадцатиюродного "],
            ["двадцатиодноюродный ", "двадцатиюродного "],
            ["двадцатидвухюродный ", "двадцатидвухюродного "],
            ["двадцатиютрехродный ", "двадцатитрехюродного "],
            ["двадцатичетырехюродный ", "двадцатичетырехюродного "],
            ["двадцатипятиюродный ", "двадцатипятиюродного "],
            ["двадцатишестиюродный ", "двадцатишестиюродного "],
            ["дальний многоюродный ", "дальнего многоюродного "],
        ],
        Person.FEMALE: [
            ["", ""],
            ["двоюродная ", "двоюродной "],
            ["троюродная ", "троюродной "],
            ["четвероюродная ", "четвероюродной "],
            ["пятиюродная ", "пятиюродной "],
            ["шестиюродная ", "шестиюродной "],
            ["семиюродная ", "семиюродной "],
            ["восьмиюродная ", "восьмиюродной "],
            ["девятиюродная ", "девятиюродной "],
            ["десятиюродная ", "десятиюродной "],
            ["одиннацатиюродная ", "одиннацатиюродной "],
            ["двенадцатиюродная ", "двенадцатиюродной "],
            ["тринадцатиюродная ", "тринадцатиюродной "],
            ["четырнадцатиюродная ", "четырнадцатиюродной "],
            ["пятнадцатиюродная ", "пятнадцатиюродной "],
            ["шестнадцатиюродная ", "шестнадцатиюродной "],
            ["семнадцатиюродная ", "семнадцатиюродной "],
            ["восемнадцатиюродная ", "восемнадцатиюродной "],
            ["девятнадцатиюродная ", "девятнадцатиюродной "],
            ["двадцатиюродная ", "двадцатиюродной "],
            ["двадцатиодноюродная ", "двадцатиюродной "],
            ["двадцатидвухюродная ", "двадцатидвухюродной "],
            ["двадцатиютрехродная ", "двадцатитрехюродной "],
            ["двадцатичетырехюродная ", "двадцатичетырехюродной "],
            ["двадцатипятиюродная ", "двадцатипятиюродной "],
            ["двадцатишестиюродная ", "двадцатишестиюродной "],
            ["дальняя многоюродная ", "дальней многоюродной "],
        ],
    }

    degrees_plural = [
        ["", ""],
        ["двоюродные ", "двоюродных "],
        ["троюродные ", "троюродных "],
        ["четвероюродные ", "четвероюродных "],
        ["пятиюродные ", "пятиюродных "],
        ["шестиюродные ", "шестиюродных "],
        ["семиюродные ", "семиюродных "],
        ["восьмиюродные ", "восьмиюродных "],
        ["девятиюродные ", "девятиюродных "],
        ["десятиюродные ", "десятиюродных "],
        ["одиннацатиюродные ", "одиннацатиюродных "],
        ["двенадцатиюродные ", "двенадцатиюродных "],
        ["тринадцатиюродные ", "тринадцатиюродных "],
        ["четырнадцатиюродные ", "четырнадцатиюродных "],
        ["пятнадцатиюродные ", "пятнадцатиюродных "],
        ["шестнадцатиюродные ", "шестнадцатиюродных "],
        ["семнадцатиюродные ", "семнадцатиюродных "],
        ["восемнадцатиюродные ", "восемнадцатиюродных "],
        ["девятнадцатиюродные ", "девятнадцатиюродных "],
        ["двадцатиюродные ", "двадцатиюродных "],
        ["двадцатиодноюродные ", "двадцатиюродных "],
        ["двадцатидвухюродные ", "двадцатидвухюродных "],
        ["двадцатиютрехродные ", "двадцатитрехюродных "],
        ["двадцатичетырехюродные ", "двадцатичетырехюродных "],
        ["двадцатипятиюродные ", "двадцатипятиюродных "],
        ["двадцатишестиюродные ", "двадцатишестиюродных "],
        ["дальние многоюродные ", "дальних многоюродных "],
    ]

    stereotyped_plurals: list[list[None | str]] = []

    def __init__(
        self,
        Ga,
        Gb,
        gender_a,
        gender_b,
        reltocommon_a,
        reltocommon_b,
        in_law_a=False,
        in_law_b=False,
        only_birth=True,
        sib_type=Relative.NORM_SIB,
    ):
        super().__init__(gender_a, gender_b, in_law_a, in_law_b, only_birth)

        self.Ga = Ga
        self.Gb = Gb
        self.reltocommon_a = reltocommon_a
        self.reltocommon_b = reltocommon_b
        self.sib_type = sib_type

        if Ga >= Gb:
            self.lvl = Ga - Gb
            self.dgr = Gb
        else:
            self.lvl = Gb - Ga
            self.dgr = Ga

    def _get_only_birth(self, relstr):
        for r in relstr:
            if r in (
                gramps.gen.relationship.RelationshipCalculator.REL_MOTHER_NOTBIRTH,
                gramps.gen.relationship.RelationshipCalculator.REL_FATHER_NOTBIRTH,
            ):
                return False
        return True

    def _get_special_name(self, genitive=False):
        # pylint: disable=unused-argument
        return None

    def _get_stereotyped_name(self, genitive=False):
        # pylint: disable=unused-argument
        return None

    def _get_descriptive_plural_name(self, genitive=False):
        # pylint: disable=unused-argument
        return None

    def _get_designated_name(self, genitive=False):
        """
        Some Collateral-type relations may have a special name (i.e. 'шурин')
        or a stereotyped name (i.e. 'брат жены'). Another (i.e. 'двоюродный
        брат жены') may have only a stereotyped name. Yet another does not
        have either of them. This method attempts to get both special and
        stereotyped names and combines them, if any

        Each class derived from Collateral defines its own version of
        self._get_special_name() and self._get_stereotyped_name() methods

        The term 'stereotyped' refers to the fact that names of many relations
        can be produced from the common stereotype, i.e. 'дядя','двоюродный
        дядя','троюродный дядя' etc)
        """

        # pylint: disable=assignment-from-none
        special_name = self._get_special_name(genitive)

        # pylint: disable=assignment-from-none
        stereotyped_name = self._get_stereotyped_name(genitive)

        if special_name is not None:
            if stereotyped_name is not None:
                if special_name != stereotyped_name:
                    return f"{special_name} ({stereotyped_name})"
            return special_name

        return stereotyped_name

    def get_plural_name(self, genitive=False):
        plural_name = self._get_stereotyped_plural_name(genitive)

        if plural_name is None:
            # pylint: disable=assignment-from-none
            plural_name = self._get_descriptive_plural_name(genitive)
        return plural_name

    def _get_stereotyped_plural_name(self, genitive=False):

        try:

            if self.in_law_b:
                spouse_b = _spouses_plural[genitive] + " "
                genitive = True
            else:
                spouse_b = ""

            if self.in_law_a:
                # genitive of spouse_a
                spouse_a = " " + _spouses_plural[True]
            else:
                spouse_a = ""

            degrees = self.degrees_plural

            stereotyped = self.stereotyped_plurals[self.lvl]
            if self.dgr >= len(degrees):
                degree = degrees[-1][genitive]
            else:
                degree = degrees[self.dgr - 1][genitive]

            stereotyped_name = stereotyped[genitive].format(degree)

            return f"{spouse_b}{stereotyped_name}{spouse_a}"

        except (KeyError, IndexError):
            pass

        return None


# -------------------------------------------------------------------------
#
# Sibling
#
# -------------------------------------------------------------------------
class Sibling(Collateral):
    """
    Sibling is a concrete class that represents a relationship
    between two people who has the same distance to their common ancestor, i.e.
    Ga = Gb
    """

    special = {
        Person.MALE: {  # gender_b is Male
            False: {  # in_law_b is False
                True: {  # in_law_a is True
                    # gender_a is Male
                    Person.MALE: ["шурин", "шурина"],  # брат жены
                    Person.FEMALE: ["деверь", "деверя"],  # брат мужа",
                },
            },
            True: {  # gender_b is Male, in_law_b is True
                # in_law_a is False
                False: ["зять", "зятя"],  # муж сестры",
                True: {  # in_law_a
                    # gender_a is Male
                    Person.MALE: ["свояк", "свояка"]  # муж сестры жены",
                },
            },
        },
        Person.FEMALE: {  # gender_b is Female
            False: {  # in_law_b is False, string's lists by Ga - Gb
                True: {  # in_law_a is True
                    # by gender_a
                    Person.MALE: ["свояченица", "свояченицы"],  # сестра жены",
                    Person.FEMALE: ["золовка", "золовки"],  # сестра мужа",
                },
            },
            True: {  # gender_b is Female, in_law_b is True
                # in_law_a is False
                False: ["невестка", "невестки"]  # жена брата",
            },
        },
    }

    stereotyped = {
        Person.MALE: [  # gender_b is Male
            ["{}брат", "{}брата"],
        ],
        Person.FEMALE: [  # gender_b is Female
            ["{}сестра", "{}сестры"],
        ],
        Person.UNKNOWN: [  # gender_b is Male
            ["{}брат или сестра", "{}брата или сестры"],
        ],
    }

    sibling_types = {
        Relative.HALF_SIB_FATHER: {
            Person.MALE: ["единокровный", "единокровного"],
            Person.FEMALE: ["единокровная", "единокровной"],
            Person.UNKNOWN: ["единокровный", "единокровного"],
        },
        Relative.HALF_SIB_MOTHER: {
            Person.MALE: ["единоутробный", "единоутробного"],
            Person.FEMALE: ["единоутробная", "единоутробной"],
            Person.UNKNOWN: ["единоутробный", "единоутробного"],
        },
        Relative.STEP_SIB: {
            Person.MALE: ["сводный", "сводного"],
            Person.FEMALE: ["сводная", "сводной"],
            Person.UNKNOWN: ["сводный", "сводного"],
        },
    }

    stereotyped_plurals = [
        ["{}братья и сёстры", "{}братьев и сестёр"],
    ]

    def _get_special_name(self, genitive=False):
        if self.Ga == 1 and self.Gb == 1:
            try:
                special_name = self.special[self.gender_b][self.in_law_b][self.in_law_a]
                if isinstance(special_name, dict):
                    special_name = special_name[self.gender_a][genitive]
                else:
                    special_name = special_name[genitive]
                return special_name
            except KeyError:
                pass
        return None

    def _get_stereotyped_name(self, genitive=False):
        try:

            if self.in_law_b:
                spouse_b = _spouses[self.gender_b][genitive] + " "
                # ... and gender_b is now the spouse's gender!
                gender_b = _spouse_gender(self.gender_b)

                genitive = True
            else:
                spouse_b = ""
                gender_b = self.gender_b

            if self.in_law_a:
                # genitive of spouse_a
                spouse_a = " " + _spouses[_spouse_gender(self.gender_a)][True]
            else:
                spouse_a = ""

            # if gender_b is Person.UNKNOWN then use
            # self.degrees[Person.MALE]
            degrees = self.degrees.get(gender_b, self.degrees[Person.MALE])

            stereotyped = self.stereotyped[gender_b][self.Ga - self.Gb]

            if self.Gb >= len(degrees):
                degree = degrees[-1][genitive]
            else:
                degree = degrees[self.Gb - 1][genitive]

            stereotyped_name = stereotyped[genitive].format(degree)

            if self.Ga == 1 and self.Gb == 1 and self.sib_type != self.UNKNOWN_SIB:
                try:
                    sibling_type = (
                        self.sibling_types[self.sib_type][gender_b][genitive] + " "
                    )
                except KeyError:
                    sibling_type = ""

                stereotyped_name = (
                    f"{spouse_b}{sibling_type}" f"{stereotyped_name}{spouse_a}"
                )
            else:
                if self.only_birth is False:
                    step = self.step[gender_b][genitive] + " "
                else:
                    step = ""
                stereotyped_name = f"{spouse_b}{step}" f"{stereotyped_name}{spouse_a}"

        except (KeyError, IndexError):
            stereotyped_name = None

        return stereotyped_name


# -------------------------------------------------------------------------
#
# Senior
#
# -------------------------------------------------------------------------
class Senior(Collateral):
    """
    Senior is a concrete class that represents a relationship
    between two people where the distance to their common ancestor
    of the first person is greather than the distance of the second, i.e.
    Ga > Gb
    """

    stereotyped = {
        Person.MALE: [  # gender_b is Male
            [None, None],
            ["{}дядя", "{}дяди"],
            ["{}великий дядя", "{}великого дяди"],
        ],
        Person.FEMALE: [  # gender_b is Female
            [None, None],
            ["{}тётя", "{}тёти"],
            ["{}великая тётя", "{}великой тёти"],
        ],
        Person.UNKNOWN: [  # gender_b is Male
            [None, None],
            ["{}дядя или тётя", "{}дяди или тёти"],
            ["{}великий дядя или тётя", "{}великого дяди или тёти"],
        ],
    }

    stereotyped_plurals = [
        [None, None],
        ["{}дяди и тёти", "{}дядей и тёть"],
        ["{}великие дяди и тёти", "{}великих дядей и тёть"],
    ]

    def _get_stereotyped_name(self, genitive=False):

        try:

            if self.in_law_b:
                spouse_b = _spouses[self.gender_b][genitive] + " "
                # ... and gender_b is now the spouse's gender!
                gender_b = _spouse_gender(self.gender_b)

                genitive = True
            else:
                spouse_b = ""
                gender_b = self.gender_b

            if self.in_law_a:
                # genitive of spouse_a
                spouse_a = " " + _spouses[_spouse_gender(self.gender_a)][True]
            else:
                spouse_a = ""

            # if gender_b is Person.UNKNOWN then use
            # self.degrees[Person.MALE]
            degrees = self.degrees.get(gender_b, self.degrees[Person.MALE])

            stereotyped = self.stereotyped[gender_b][self.Ga - self.Gb]

            if self.Gb >= len(degrees):
                degree = degrees[-1][genitive]
            else:
                degree = degrees[self.Gb - 1][genitive]

            stereotyped_name = stereotyped[genitive].format(degree)

            if self.only_birth is False:
                step = self.step[gender_b][genitive] + " "
            else:
                step = ""

            stereotyped_name = f"{spouse_b}{step}{stereotyped_name}{spouse_a}"

        except (KeyError, IndexError):
            stereotyped_name = None

        return stereotyped_name

    def _get_descriptive_name(self, genitive=False):

        if self.in_law_a:
            gender_a = _spouse_gender(self.gender_a)
            # genitive of spouse_a
            spouse_a = " " + _spouses[gender_a][True]
        else:
            spouse_a = ""
            gender_a = self.gender_a
        parent_gender = _parent_gender(self.reltocommon_a[-self.Gb - 1])
        whom = Ancestor(
            self.Ga - self.Gb,
            gender_a,
            parent_gender,
            False,
            False,
            self._get_only_birth(self.reltocommon_a[: -self.Gb]),
        ).get_name(True)

        who = Sibling(
            self.Gb,
            self.Gb,
            parent_gender,
            self.gender_b,
            self.reltocommon_a[-self.Gb :],
            self.reltocommon_b,
            False,
            self.in_law_b,
            self._get_only_birth(self.reltocommon_a[-self.Gb :])
            and self._get_only_birth(self.reltocommon_b),
            self.UNKNOWN_SIB,
        ).get_name(False)

        return f"{who} {whom}{spouse_a}"

    def _get_descriptive_plural_name(self, genitive=False):

        if self.in_law_a:
            spouse_a = " " + _spouses_plural[True]
        else:
            spouse_a = ""
        whom = Ancestor(
            self.Ga - self.Gb, Person.UNKNOWN, Person.UNKNOWN, False, False, True
        ).get_plural_name(True)
        who = Sibling(
            self.Gb,
            self.Gb,
            Person.UNKNOWN,
            Person.UNKNOWN,
            self.reltocommon_a[-self.Gb : -1],
            self.reltocommon_b[-self.Gb : -1],
            False,
            self.in_law_b,
            True,
            self.UNKNOWN_SIB,
        ).get_plural_name(genitive)

        return f"{who} {whom}{spouse_a}"


# -------------------------------------------------------------------------
#
# Junior
#
# -------------------------------------------------------------------------
class Junior(Collateral):
    """
    Junior is a concrete class that represents a relationship
    between two people where the distance to their common ancestor
    of the second person is greather than the distance of the first, i.e.
    Ga < Gb
    """

    stereotyped = {
        Person.MALE: [  # in_law_a is False
            [None, None],
            ["{}племянник", "{}племянника"],
            ["{}внучатый племянник", "{}внучатого племянника"],
        ],
        Person.FEMALE: [
            [None, None],
            ["{}племянница", "{}племянницы"],
            ["{}внучатая племянница", "{}внучатой племянницы"],
        ],
        Person.UNKNOWN: [  # in_law_a is False
            [None, None],
            ["{}племянник или племянница", "{}племянника или племянницы"],
            [
                "{}внучатый племянник или племянница",
                "{}внучатого племянника или племянницы",
            ],
        ],
    }

    stereotyped_plurals = [
        [None, None],
        ["{}племянники и племянницы", "{}племянников и племянниц"],
        ["{}внучатые племянники и племянницы", "{}внучатых племянников и племянниц"],
    ]

    def _get_stereotyped_name(self, genitive=False):

        try:

            if self.in_law_b:
                spouse_b = _spouses[self.gender_b][genitive] + " "
                # ... and gender_b is now the spouse's gender!
                gender_b = _spouse_gender(self.gender_b)

                genitive = True
            else:
                spouse_b = ""
                gender_b = self.gender_b

            if self.in_law_a:
                # genitive of spouse_a
                spouse_a = " " + _spouses[_spouse_gender(self.gender_a)][True]
            else:
                spouse_a = ""

            # if gender_b is Person.UNKNOWN then use
            # self.degrees[Person.MALE]
            degrees = self.degrees.get(gender_b, self.degrees[Person.MALE])

            stereotyped = self.stereotyped[gender_b][self.Gb - self.Ga]
            if self.Ga >= len(degrees):
                degree = degrees[-1][genitive]
            else:
                degree = degrees[self.Ga - 1][genitive]

            stereotyped_name = stereotyped[genitive].format(degree)

            if self.only_birth is False:
                step = self.step[gender_b][genitive] + " "
            else:
                step = ""

            stereotyped_name = f"{spouse_b}{step}{stereotyped_name}{spouse_a}"

        except (KeyError, IndexError):
            stereotyped_name = None

        return stereotyped_name

    def _get_descriptive_name(self, genitive=False):

        parent_gender = _parent_gender(self.reltocommon_b[-self.Ga - 1])

        whom = Sibling(
            self.Ga,
            self.Ga,
            self.gender_a,
            parent_gender,
            self.reltocommon_a,
            self.reltocommon_b[-self.Ga :],
            self.in_law_a,
            False,
            self._get_only_birth(self.reltocommon_a)
            and self._get_only_birth(self.reltocommon_b[-self.Ga :]),
            self.UNKNOWN_SIB,
        ).get_name(True)

        who = Descendant(
            self.Gb - self.Ga,
            parent_gender,
            self.gender_b,
            False,
            self.in_law_b,
            self._get_only_birth(self.reltocommon_b[: -self.Ga]),
        ).get_name(False)

        return f"{who} {whom}"

    def _get_descriptive_plural_name(self, genitive=False):

        # 'only_birth' is intentionally True in Sibling and Descendant!
        whom = Sibling(
            self.Ga,
            self.Ga,
            Person.UNKNOWN,
            Person.UNKNOWN,
            self.reltocommon_a[-self.Ga :],
            self.reltocommon_b[-self.Ga :],
            self.in_law_a,
            False,
            True,
            self.sib_type,
        ).get_plural_name(True)

        who = Descendant(
            self.Gb - self.Ga,
            Person.UNKNOWN,
            Person.UNKNOWN,
            False,
            True,
            self.in_law_b,
        ).get_plural_name(genitive)

        return f"{who} {whom}"


# -------------------------------------------------------------------------
#
# RelationshipCalculator
#
# -------------------------------------------------------------------------
class RelationshipCalculator(gramps.gen.relationship.RelationshipCalculator):
    """
    RelationshipCalculator Class
    """

    def __init__(self):
        super().__init__()
        self._Ga = None
        self._Gb = None
        self._gender_a = None
        self._gender_b = None
        self._in_law_a = None
        self._in_law_b = None
        self._reltocommon_a = None
        self._reltocommon_b = None
        self._only_birth = None
        self._in_law_a = None
        self._in_law_b = None
        self._sib_type = None

    def _get_cousin(self, level=None, removed=None, dir="", step="", inlaw=""):
        # pylint: disable=unused-argument, too-many-arguments

        if self._Ga > self._Gb:
            return Senior(
                self._Ga,
                self._Gb,
                self._gender_a,
                self._gender_b,
                self._reltocommon_a,
                self._reltocommon_b,
                self._in_law_a,
                self._in_law_b,
                self._only_birth,
                self._sib_type,
            ).get_name(False)
        elif self._Ga == self._Gb:
            return Sibling(
                self._Ga,
                self._Gb,
                self._gender_a,
                self._gender_b,
                self._reltocommon_a,
                self._reltocommon_b,
                self._in_law_a,
                self._in_law_b,
                self._only_birth,
                self._sib_type,
            ).get_name(False)
        else:
            return Junior(
                self._Ga,
                self._Gb,
                self._gender_a,
                self._gender_b,
                self._reltocommon_a,
                self._reltocommon_b,
                self._in_law_a,
                self._in_law_b,
                self._only_birth,
                self._sib_type,
            ).get_name(False)

    def _get_father(self, level, step="", inlaw=""):
        return Ancestor(
            level,
            self._gender_a,
            Person.MALE,
            self._in_law_a,
            self._in_law_b,
            self._only_birth,
        ).get_name(False)

    def _get_mother(self, level, step="", inlaw=""):
        return Ancestor(
            level,
            self._gender_a,
            Person.FEMALE,
            self._in_law_a,
            self._in_law_b,
            self._only_birth,
        ).get_name(False)

    def _get_parent_unknown(self, level, step="", inlaw=""):
        return Ancestor(
            level,
            self._gender_a,
            self._gender_b,
            self._in_law_a,
            self._in_law_b,
            self._only_birth,
        ).get_name(False)

    def _get_son(self, level, step="", inlaw=""):
        return Descendant(
            level,
            self._gender_a,
            Person.MALE,
            self._in_law_a,
            self._in_law_b,
            self._only_birth,
        ).get_name(False)

    def _get_daughter(self, level, step="", inlaw=""):
        return Descendant(
            level,
            self._gender_a,
            Person.FEMALE,
            self._in_law_a,
            self._in_law_b,
            self._only_birth,
        ).get_name(False)

    def _get_child_unknown(self, level, step="", inlaw=""):
        return Descendant(
            level,
            self._gender_a,
            self._gender_b,
            self._in_law_a,
            self._in_law_b,
            self._only_birth,
        ).get_name(False)

    def _get_aunt(self, level, step="", inlaw=""):
        if level > 1:
            return Senior(
                self._Ga,
                self._Gb,
                self._gender_a,
                Person.FEMALE,
                self._reltocommon_a,
                self._reltocommon_b,
                self._in_law_a,
                self._in_law_b,
                self._only_birth,
                self._sib_type,
            ).get_name(False)
        elif level == 1:
            return Sibling(
                self._Ga,
                self._Gb,
                self._gender_a,
                Person.FEMALE,
                self._reltocommon_a,
                self._reltocommon_b,
                self._in_law_a,
                self._in_law_b,
                self._only_birth,
                self._sib_type,
            ).get_name(False)

    def _get_uncle(self, level, step="", inlaw=""):
        if level > 1:
            return Senior(
                self._Ga,
                self._Gb,
                self._gender_a,
                Person.MALE,
                self._reltocommon_a,
                self._reltocommon_b,
                self._in_law_a,
                self._in_law_b,
                self._only_birth,
                self._sib_type,
            ).get_name(False)
        elif level == 1:
            return Sibling(
                self._Ga,
                self._Gb,
                self._gender_a,
                Person.MALE,
                self._reltocommon_a,
                self._reltocommon_b,
                self._in_law_a,
                self._in_law_b,
                self._only_birth,
                self._sib_type,
            ).get_name(False)

    def _get_sibling(self, level, step="", inlaw=""):
        return self._get_cousin()

    def _get_nephew(self, level, step="", inlaw=""):
        return Junior(
            self._Ga,
            self._Gb,
            self._gender_a,
            Person.MALE,
            self._reltocommon_a,
            self._reltocommon_b,
            self._in_law_a,
            self._in_law_b,
            self._only_birth,
            self._sib_type,
        ).get_name(False)

    def _get_niece(self, level, step="", inlaw=""):
        return Junior(
            self._Ga,
            self._Gb,
            self._gender_a,
            Person.FEMALE,
            self._reltocommon_a,
            self._reltocommon_b,
            self._in_law_a,
            self._in_law_b,
            self._only_birth,
            self._sib_type,
        ).get_name(False)

    # pylint: disable=too-many-arguments,too-many-positional-arguments
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
        self._Ga = Ga
        self._Gb = Gb
        self._gender_a = gender_a
        self._gender_b = gender_b
        self._reltocommon_a = reltocommon_a
        self._reltocommon_b = reltocommon_b
        self._only_birth = only_birth
        self._in_law_a = in_law_a
        self._in_law_b = in_law_b
        self._sib_type = self.UNKNOWN_SIB

        return super().get_single_relationship_string(
            Ga,
            Gb,
            gender_a,
            gender_b,
            reltocommon_a,
            reltocommon_b,
            only_birth,
            in_law_a,
            in_law_b,
        )

    def get_sibling_relationship_string(
        self, sib_type, gender_a, gender_b, in_law_a=False, in_law_b=False
    ):
        self._Ga = 1
        self._Gb = 1
        self._gender_a = gender_a
        self._gender_b = gender_b
        self._in_law_a = in_law_a
        self._in_law_b = in_law_b
        self._sib_type = sib_type

        return super().get_sibling_relationship_string(
            sib_type, gender_a, gender_b, in_law_a, in_law_b
        )

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
        if Ga == 0:
            return Descendant(
                Gb, Person.UNKNOWN, Person.UNKNOWN, in_law_a, in_law_b, only_birth
            ).get_plural_name()
        elif Gb == 0:
            return Ancestor(
                Ga, Person.UNKNOWN, Person.UNKNOWN, in_law_a, in_law_b, only_birth
            ).get_plural_name()
        elif Ga > Gb:
            return Senior(
                Ga,
                Gb,
                Person.UNKNOWN,
                Person.UNKNOWN,
                reltocommon_a,
                reltocommon_b,
                in_law_a,
                in_law_b,
                only_birth,
            ).get_plural_name()
        elif Ga == Gb:
            return Sibling(
                Ga,
                Gb,
                Person.UNKNOWN,
                Person.UNKNOWN,
                reltocommon_a,
                reltocommon_b,
                in_law_a,
                in_law_b,
                only_birth,
            ).get_plural_name()
        else:
            return Junior(
                Ga,
                Gb,
                Person.UNKNOWN,
                Person.UNKNOWN,
                reltocommon_a,
                reltocommon_b,
                in_law_a,
                in_law_b,
                only_birth,
            ).get_plural_name()


if __name__ == "__main__":
    # Test function. Call it as follows from the command line (so as to find
    #        imported modules):
    #    export PYTHONPATH=/path/to/gramps/src
    # python src/plugins/rel/rel_ru.py
    # (Above not needed here)

    from gramps.gen.relationship import test

    RC = RelationshipCalculator()
    test(RC, True)

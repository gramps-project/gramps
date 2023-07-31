# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2005  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2009-2010  Andrew I Baznikin
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

# Written by Alex Roitman, largely based on relationship.py by Don Allingham.
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

_parents_level = [
    "",
    "родители",
    "дедушки/бабушки",
    "прадедушки/прабабушки",
    "прапрадедушки/прапрабабушки (5 поколение)",
    "прапрапрадедушки/прапрапрабабушки (6 поколение)",
    "прапрапрапрадедушки/прапрапрапрабабушки (7 поколение)",
    "прапрапрапрапрадедушки/прапрапрапрапрабабушки (8 поколение)",
]

_male_cousin_level = [
    "",
    "двоюродный",
    "троюродный",
    "четвероюродный",
    "пятиюродный",
    "шестиюродный",
    "семиюродный",
    "восьмиюродный",
    "девятиюродный",
    "десятиюродный",
    "одиннацатиюродный",
    "двенадцатиюродный",
    "тринадцатиюродный",
    "четырнадцатиюродный",
    "пятнадцатиюродный",
    "шестнадцатиюродный",
    "семнадцатиюродный",
    "восемнадцатиюродный",
    "девятнадцатиюродный",
    "двадцатиюродный",
]

_female_cousin_level = [
    "",
    "двоюродная",
    "троюродная",
    "четвероюродная",
    "пятиюродная",
    "шестиюродная",
    "семиюродная",
    "восьмиюродная",
    "девятиюродная",
    "десятиюродная",
    "одиннацатиюродная",
    "двенадцатиюродная",
    "тринадцатиюродная",
    "четырнадцатиюродная",
    "пятнадцатиюродная",
    "шестнадцатиюродная",
    "семнадцатиюродная",
    "восемнадцатиюродная",
    "девятнадцатиюродная",
    "двадцатиюродная",
]

_cousin_level = [
    "",
    "двоюродные",
    "троюродные",
    "четвероюродные",
    "пятиюродные",
    "шестиюродные",
    "семиюродные",
    "восьмиюродные",
    "девятиюродные",
    "десятиюродные",
    "одиннацатиюродные",
    "двенадцатиюродные",
    "тринадцатиюродные",
    "четырнадцатиюродные",
    "пятнадцатиюродные",
    "шестнадцатиюродные",
    "семнадцатиюродные",
    "восемнадцатиюродные",
    "девятнадцатиюродные",
    "двадцатиюродные",
]

_junior_male_removed_level = [
    "брат",
    "племянник",
    "внучатый племянник",
    "правнучатый племянник",
    "праправнучатый племянник",
    "прапраправнучатый племянник",
    "прапрапраправнучатый племянник",
]

_junior_female_removed_level = [
    "сестра",
    "племянница",
    "внучатая племянница",
    "правнучатая племянница",
    "праправнучатая племянница",
    "прапраправнучатая племянница",
    "прапрапраправнучатая племянница",
]

_juniors_removed_level = [
    "братья/сестры",
    "племянники",
    "внучатые племянники",
    "правнучатые племянники",
    "праправнучатые племянники",
    "прапраправнучатые племянники",
    "прапрапраправнучатые племянники",
]

_senior_male_removed_level = [
    "",
    "дядя",
    "дед",
    "прадед",
    "прапрадед",
    "прапрапрадед",
    "прапрапрапрадед",
]

_senior_female_removed_level = [
    "",
    "тётя",
    "бабушка",
    "прабабушка",
    "прапрабабушка",
    "прапрапрабабушка",
    "прапрапрапрабабушка",
]

_seniors_removed_level = [
    "",
    "дяди/тёти",
    "дедушки/бабушки",
    "прадеды/прабабушки",
    "прапрадеды/прапрабабушки",
    "прапрапрадеды/прапрапрабабушки",
    "прапрапрапрадеды/прапрапрапрабабушки",
]

_father_level = [
    "",
    "отец",
    "дед",
    "прадед",
    "прапрадед",
    "прапрапрадед",
    "прапрапрапрадед",
]

_mother_level = [
    "",
    "мать",
    "бабушка",
    "прабабушка",
    "прапрабабушка",
    "прапрапрабабушка",
    "прапрапрапрабабушка",
]

_son_level = [
    "",
    "сын",
    "внук",
    "правнук",
    "праправнук",
    "прапраправнук",
    "прапрапраправнук",
]

_daughter_level = [
    "",
    "дочь",
    "внучка",
    "правнучка",
    "праправнучка",
    "прапраправнучка",
    "прапрапраправнучка",
]

_children_level = [
    "",
    "дети",
    "внуки",
    "правнуки",
    "праправнуки",
    "прапраправнуки",
    "прапрапраправнуки",
    "прапрапрапраправнуки",
]

_sister_level = [
    "",
    "сестра",
    "тётя",
    "двоюродная бабушка",
    "двоюродная прабабушка",
    "двоюродная прапрабабушка",
    "двоюродная прапрапрабабушка",
    "двоюродная прапрапрапрабабушка",
]

_brother_level = [
    "",
    "брат",
    "дядя",
    "двоюродный дед",
    "двоюродный прадед",
    "двоюродный прапрадед",
    "двоюродный прапрапрадед",
    "двоюродный прапрапрапрадед",
]

_siblings_level = [
    "",
    "братья/сестры",
    "дядьки/тётки",
    "двоюродные дедушки/бабушки",
    "двоюродные прадедушки/прабабушки",
    "двоюродные прапрадедушки/прапрабабушки (5 поколение)",
    "двоюродные прапрапрадедушки/прапрапрабабушки (6 поколение)",
    "двоюродные прапрапрапрадедушки/прапрапрапрабабушки (7 поколение)",
    "двоюродные прапрапрапрапрадедушки/прапрапрапрапрабабушки (8 поколение)",
]

_nephew_level = [
    "",
    "племянник",
    "внучатый племянник",
    "правнучатый племянник",
    "праправнучатый племянник",
    "прапраправнучатый племянник",
    "прапрапраправнучатый племянник",
]

_niece_level = [
    "",
    "племянница",
    "внучатая племянница",
    "правнучатая племянница",
    "праправнучатая племянница",
    "прапраправнучатая племянница",
    "прапрапраправнучатая племянница",
]

_nephews_nieces_level = [
    "",
    "братья/сестры",
    "племянники",
    "внучатые племянники",
    "правнучатые племянники",
    "праправнучатые племянники",
    "прапраправнучатые племянники",
    "прапрапраправнучатые племянники",
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

    def get_parents(self, level):
        if level > len(_parents_level) - 1:
            return "дальние родственники"
        else:
            return _parents_level[level]

    def get_junior_male_cousin(self, level, removed):
        if (
            removed > len(_junior_male_removed_level) - 1
            or level > len(_male_cousin_level) - 1
        ):
            return "дальний родственник"
        else:
            return "%s %s" % (
                _male_cousin_level[level],
                _junior_male_removed_level[removed],
            )

    def get_senior_male_cousin(self, level, removed):
        if (
            removed > len(_senior_male_removed_level) - 1
            or level > len(_male_cousin_level) - 1
        ):
            return "дальний родственник"
        else:
            return "%s %s" % (
                _male_cousin_level[level],
                _senior_male_removed_level[removed],
            )

    def get_junior_female_cousin(self, level, removed):
        if (
            removed > len(_junior_female_removed_level) - 1
            or level > len(_male_cousin_level) - 1
        ):
            return "дальняя родственница"
        else:
            return "%s %s" % (
                _female_cousin_level[level],
                _junior_female_removed_level[removed],
            )

    def get_senior_female_cousin(self, level, removed):
        if (
            removed > len(_senior_female_removed_level) - 1
            or level > len(_male_cousin_level) - 1
        ):
            return "дальняя родственница"
        else:
            return "%s %s" % (
                _female_cousin_level[level],
                _senior_female_removed_level[removed],
            )

    def get_father(self, level):
        if level > len(_father_level) - 1:
            return "дальний предок"
        else:
            return _father_level[level]

    def get_son(self, level):
        if level > len(_son_level) - 1:
            return "дальний потомок"
        else:
            return _son_level[level]

    def get_mother(self, level):
        if level > len(_mother_level) - 1:
            return "дальний предок"
        else:
            return _mother_level[level]

    def get_daughter(self, level):
        if level > len(_daughter_level) - 1:
            return "дальний потомок"
        else:
            return _daughter_level[level]

    def _get_aunt(self, level, step="", inlaw=""):
        if level > len(_sister_level) - 1:
            return "дальний предок в соседнем поколении"
        else:
            return _sister_level[level]

    def _get_uncle(self, level, step="", inlaw=""):
        if level > len(_brother_level) - 1:
            return "дальний предок в соседнем поколении"
        else:
            return _brother_level[level]

    def _get_sibling(self, level, step="", inlaw=""):
        """
        Sibling of unknown gender
        """
        return (
            self._get_uncle(level, step, inlaw)
            + " или "
            + self._get_aunt(level, step, inlaw)
        )

    def get_nephew(self, level):
        if level > len(_nephew_level) - 1:
            return "дальний потомок в соседнем поколении"
        else:
            return _nephew_level[level]

    def get_niece(self, level):
        if level > len(_niece_level) - 1:
            return "дальний потомок в соседнем поколении"
        else:
            return _niece_level[level]

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
        if Gb == 0:
            if Ga == 0:
                return "один человек"
            elif gender_b == Person.MALE:
                return self.get_father(Ga)
            else:
                return self.get_mother(Ga)
        elif Ga == 0:
            if gender_b == Person.MALE:
                return self.get_son(Gb)
            else:
                return self.get_daughter(Gb)
        elif Gb == 1:
            if gender_b == Person.MALE:
                return self._get_uncle(Ga)
            else:
                return self._get_aunt(Ga)
        elif Ga == 1:
            if gender_b == Person.MALE:
                return self.get_nephew(Gb - 1)
            else:
                return self.get_niece(Gb - 1)
        elif Ga > Gb:
            if gender_b == Person.MALE:
                return self.get_senior_male_cousin(Gb - 1, Ga - Gb)
            else:
                return self.get_senior_female_cousin(Gb - 1, Ga - Gb)
        else:
            if gender_b == Person.MALE:
                return self.get_junior_male_cousin(Ga - 1, Gb - Ga)
            else:
                return self.get_junior_female_cousin(Ga - 1, Gb - Ga)

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
        rel_str = "дальние родственники"
        if Ga == 0:
            # These are descendants
            if Gb < len(_children_level):
                rel_str = _children_level[Gb]
            else:
                rel_str = "дальние потомки"
        elif Gb == 0:
            # These are parents/grand parents
            if Ga < len(_parents_level):
                rel_str = _parents_level[Ga]
            else:
                rel_str = "дальние предки"
        elif Gb == 1:
            # These are siblings/aunts/uncles
            if Ga < len(_siblings_level):
                rel_str = _siblings_level[Ga]
            else:
                rel_str = "дальние дяди/тёти"
        elif Ga == 1:
            # These are nieces/nephews
            if Gb < len(_nephews_nieces_level):
                rel_str = _nephews_nieces_level[Gb]
            else:
                rel_str = "дальние племянники/племянницы"
        elif Ga > Gb:
            # These are cousins in different generations with the second person
            # being in a higher generation from the common ancestor than the
            # first person.
            if Gb <= len(_seniors_removed_level) and (Ga - Gb) < len(_cousin_level):
                rel_str = "%s %s" % (
                    _cousin_level[Gb - 1],
                    _seniors_removed_level[Ga - Gb],
                )
            else:
                rel_str = "(старшие) дальние родственники"
        else:
            # These are cousins in different generations with the second person
            # being in a lower generation from the common ancestor than the
            # first person.
            if Ga <= len(_juniors_removed_level) and (Gb - Ga) < len(_cousin_level):
                rel_str = "%s %s" % (
                    _cousin_level[Ga - 1],
                    _juniors_removed_level[Gb - Ga],
                )
            else:
                rel_str = "(младшие) дальние родственники"

        if in_law_b == True:
            # TODO: Translate this!
            rel_str = "spouses of %s" % rel_str

        return rel_str


# TODO: def get_sibling_relationship_string for Russian step and inlaw relations

if __name__ == "__main__":
    # Test function. Call it as follows from the command line (so as to find
    #        imported modules):
    #    export PYTHONPATH=/path/to/gramps/src
    # python src/plugins/rel/rel_ru.py
    # (Above not needed here)

    """TRANSLATORS, copy this if statement at the bottom of your
    rel_xx.py module, and test your work with:
    python src/plugins/rel/rel_xx.py
    """
    from gramps.gen.relationship import test

    RC = RelationshipCalculator()
    test(RC, True)

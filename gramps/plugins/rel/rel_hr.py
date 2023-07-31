# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
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
# plugins/rel/rel_hr.py
#
# Copyright (C) 2010 Josip (josip at pisoj dot com)

"""
Croatian-specific classes for calculating relationships and kinship names.
"""

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------

import gramps.gen.relationship

_PARENTS = [
    "",
    "otac i majka",
    "djedovi i bake",
    "pradjedovi i prabake",
    "%s pradjedovi i %s prabake",
]
_CHILDS = ["", "djeca", "unučad", "praunučad", "%s praunučad"]
_CHILDS_SP = [
    "",
    "snahe i zetovi",
    "prasnahe i prazetovi",
    "supružnici praunučadi",
    "supružnici %s praunučadi",
]


# -------------------------------------------------------------------------
#
# Class HrDeclination
#
# -------------------------------------------------------------------------
class HrDeclination:
    """
    Croatian declination system
    """

    numdcl = {
        1: "prv",
        2: "drug",
        3: "treć",
        4: "četvrt",
        5: "pet",
        6: "šest",
        7: "sedm",
        8: "osm",
        9: "devet",
        10: "deset",
        11: "jedanaest",
        12: "dvanaest",
        13: "trinaest",
        14: "četrnaest",
        15: "petnaest",
        16: "šestnaest",
        17: "sedamnaest",
        18: "osamnaest",
        19: "devetnaest",
        20: "dvadeset",
        30: "trideset",
        40: "četrdeset",
        50: "pedeset",
        60: "šesdeset",
        70: "sedamdeset",
        80: "osamdeset",
        90: "devedeset",
        (1, 1, 1): "i",
        (1, 1, 5): "i",
        (1, 2, 1): "i",
        (1, 2, 5): "i",
        (1, 1, 2): "og",
        (1, 1, 4): "og",
        (2, 1, 2): "og",
        (1, 1, 3): "om",
        (1, 1, 6): "om",
        (0, 1, 7): "om",
        (2, 1, 3): "om",
        (2, 1, 6): "om",
        (2, 2, 7): "om",
        (1, 1, 7): "im",
        (2, 1, 7): "im",
        (1, 2, 3): "im",
        (1, 2, 6): "im",
        (1, 2, 7): "im",
        (0, 2, 3): "im",
        (0, 2, 6): "im",
        (0, 2, 7): "im",
        (0, 1, 1): "a",
        (0, 1, 5): "a",
        (2, 2, 1): "a",
        (2, 2, 5): "a",
        (0, 1, 2): "e",
        (0, 1, 4): "e",
        (1, 2, 4): "e",
        (0, 2, 1): "e",
        (0, 2, 4): "e",
        (0, 2, 5): "e",
        (2, 1, 1): "o",
        (2, 1, 4): "o",
        (2, 1, 5): "o",
        (0, 1, 3): "oj",
        (0, 1, 6): "oj",
        (2, 2, 3): "oj",
        (2, 2, 6): "oj",
        (0, 2, 2): "ih",
        (1, 2, 2): "ih",
        (2, 2, 2): "ih",
        (2, 2, 4): "u",
    }

    def get_ordnum(self, num, gender, number, case):
        """
        Declination of ordinal numbers
        gender:   0 = feminine, 1 = masculine, 2 = neuter
        case:       1 = nominative, 2 = genitive, 3 = dative, 4 = accusative
                        5 = vocative, 6 = locative, 7 = instrumental
        number:   1 = single, 2 = plural
        :rtype: str
        """
        if 0 < num < 100:
            lres = []
            # lres.append(self.numdcl[(num / 100) * 100])
            if (num < 21) or (num % 10) == 0:
                lres.append(self.numdcl[num])
            else:
                lres.append(self.numdcl[(num % 10) * 10])
                lres.append(self.numdcl[(num % 10)])
            sufix = self.numdcl[(gender, number, case)]
            if num % 10 == 3:
                if gender != 0 and sufix != "oj":
                    sufix = sufix.replace("o", "e")
            lres[-1] += sufix
            res = " ".join(lres)
        else:
            res = str(num) + ". "
        return res


HRD = HrDeclination()
HRDN = HRD.get_ordnum


def _get_childs(level, inlaw):
    """children, grandchildren et."""
    if level < len(_CHILDS) - 1:
        if not inlaw:
            return _CHILDS[level]
        else:
            return _CHILDS_SP[level]
    else:
        if not inlaw:
            return "%s" % _CHILDS[4] % (HRDN(level - 2, 0, 1, 1))
        elif inlaw:
            return "%s" % _CHILDS_SP[4] % (HRDN(level - 2, 0, 2, 1))


def _get_parents(level):
    """parents, grandparents"""
    if level < 4:
        return _PARENTS[level]
    else:
        return "%s" % _PARENTS[4] % (HRDN(level - 2, 1, 1, 1), HRDN(level - 2, 0, 2, 1))


def _get_uncles(gen, inlaw):
    """in general: uncles, ants---"""
    if gen == 2:
        if not inlaw:
            return "stričevi, ujaci i tetke"
        else:
            return "strine, ujne i tetci"
    elif gen == 3:
        if not inlaw:
            return "prastričevi, praujaci i pratetke"
        else:
            return "prastrine, praujne i pratetci"
    else:
        if not inlaw:
            return "%s prastričevi, %s praujaci i %s pratetke" % (
                HRDN(gen - 2, 1, 2, 1),
                HRDN(gen - 2, 1, 2, 1),
                HRDN(gen - 2, 0, 2, 1),
            )
        else:
            return "prastrine, praujne i pratetci"


# -------------------------------------------------------------------------
#
#  CroatianRelationshipCalculator
#
# -------------------------------------------------------------------------


class RelationshipCalculator(gramps.gen.relationship.RelationshipCalculator):
    """
    RelationshipCalculator Class
    """

    def __init__(self):
        gramps.gen.relationship.RelationshipCalculator.__init__(self)

    def get_plural_relationship_string(
        self,
        gena,
        genb,
        reltocommon_a="",
        reltocommon_b="",
        only_birth=True,
        in_law_a=False,
        in_law_b=False,
    ):
        """returns kinship terms for groups of persons"""
        if not in_law_b:
            rel_str = "potomci %s generacije predaka u %s koljenu: " % (
                HRDN(gena, 0, 1, 2),
                HRDN(genb, 2, 1, 6),
            )
        elif in_law_b:
            rel_str = "supružnici potomaka %s generacije predaka u %s " "koljenu: " % (
                HRDN(gena, 0, 1, 2),
                HRDN(genb, 2, 1, 6),
            )
        if genb == 0:
            # These are ancestors
            rel_str = "%s generacija predaka: %s" % (
                HRDN(gena, 0, 1, 1),
                _get_parents(gena),
            )
        elif gena == 0:
            # These are descendants
            if not in_law_b:
                rel_str = "%s generacija potomaka: %s" % (
                    HRDN(genb, 0, 1, 1),
                    _get_childs(genb, in_law_b),
                )
            else:
                rel_str = "supružnici %s generacije potomaka: %s" % (
                    HRDN(genb, 0, 2, 1),
                    _get_childs(genb, in_law_b),
                )
        elif gena == 1 == genb:
            # These are siblings
            if not in_law_b:
                rel_str += "braća i sestre"
            else:
                rel_str = "supružnici braće i sestara"
        elif genb == 1:
            # These are aunts/uncles
            rel_str += _get_uncles(gena, in_law_b)
        return rel_str


if __name__ == "__main__":
    # Test function. Call it as follows from the command line (so as to find
    #        imported modules):
    #    export PYTHONPATH=/path/to/gramps/src
    # python src/plugins/rel/rel_ru.py
    from gramps.gen.relationship import test

    RC = RelationshipCalculator()
    test(RC, True)

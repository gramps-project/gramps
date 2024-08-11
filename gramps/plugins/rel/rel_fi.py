# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2005  Donald N. Allingham
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

# Written by Alex Roitman, largely based on relationship.py by Don Allingham
# and on valuable input from Eero Tamminen
"""
Specific classes for relationships.
"""

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------

from gramps.gen.lib import Person
import gramps.gen.relationship

# -------------------------------------------------------------------------
#
# Finnish-specific definitions of relationships
#
# -------------------------------------------------------------------------

_parents_level = [
    "",
    "vanhemmat",
    "isovanhemmat",
    "isoisovanhemmat",
    "isoisoisovanhemmat",
    "isoisoisoisovanhemmat",
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

    def get_cousin(self, level):
        if level == 0:
            return ""
        elif level == 1:
            return "serkku"
        elif level == 2:
            return "pikkuserkku"
        elif level > 2:
            return "%d. serkku" % level

    def get_cousin_genitive(self, level):
        if level == 0:
            return ""
        elif level == 1:
            return "serkun"
        elif level == 2:
            return "pikkuserkun"
        elif level > 2:
            return "%d. serkun" % level

    def get_parents(self, level):
        if level > len(_parents_level) - 1:
            return "kaukaiset esivanhemmat"
        else:
            return _parents_level[level]

    def get_direct_ancestor(self, person, rel_string):
        result = []
        for ix in range(len(rel_string) - 1):
            if rel_string[ix] == "f":
                result.append("isän")
            else:
                result.append("äidin")
        if person == Person.MALE:
            result.append("isä")
        else:
            result.append("äiti")
        return " ".join(result)

    def get_direct_descendant(self, person, rel_string):
        result = []
        for ix in range(len(rel_string) - 2, -1, -1):
            if rel_string[ix] == "f":
                result.append("pojan")
            elif rel_string[ix] == "m":
                result.append("tyttären")
            else:
                result.append("lapsen")
        if person == Person.MALE:
            result.append("poika")
        elif person == Person.FEMALE:
            result.append("tytär")
        else:
            result.append("lapsi")
        return " ".join(result)

    def get_ancestors_cousin(self, rel_string_long, rel_string_short):
        result = []
        removed = len(rel_string_long) - len(rel_string_short)
        level = len(rel_string_short) - 1
        for ix in range(removed):
            if rel_string_long[ix] == "f":
                result.append("isän")
            else:
                result.append("äidin")
        result.append(self.get_cousin(level))
        return " ".join(result)

    def get_cousins_descendant(self, person, rel_string_long, rel_string_short):
        result = []
        removed = len(rel_string_long) - len(rel_string_short) - 1
        level = len(rel_string_short) - 1
        if level:
            result.append(self.get_cousin_genitive(level))
        elif rel_string_long[removed] == "f":
            result.append("veljen")
        else:
            result.append("sisaren")
        for ix in range(removed - 1, -1, -1):
            if rel_string_long[ix] == "f":
                result.append("pojan")
            elif rel_string_long[ix] == "m":
                result.append("tyttären")
            else:
                result.append("lapsen")
        if person == Person.MALE:
            result.append("poika")
        elif person == Person.FEMALE:
            result.append("tytär")
        else:
            result.append("lapsi")
        return " ".join(result)

    def get_ancestors_brother(self, rel_string):
        result = []
        for ix in range(len(rel_string) - 1):
            if rel_string[ix] == "f":
                result.append("isän")
            else:
                result.append("äidin")
        result.append("veli")
        return " ".join(result)

    def get_ancestors_sister(self, rel_string):
        result = []
        for ix in range(len(rel_string) - 1):
            if rel_string[ix] == "f":
                result.append("isän")
            else:
                result.append("äidin")
        result.append("sisar")
        return " ".join(result)

    def get_relationship(self, secondRel, firstRel, orig_person, other_person):
        common = ""
        if not firstRel:
            if not secondRel:
                return ("", common)
            else:
                return (self.get_direct_ancestor(other_person, secondRel), common)
        elif not secondRel:
            return (self.get_direct_descendant(other_person, firstRel), common)
        elif len(firstRel) == 1:
            if other_person == Person.MALE:
                return (self.get_ancestors_brother(secondRel), common)
            else:
                return (self.get_ancestors_sister(secondRel), common)
        elif len(secondRel) >= len(firstRel):
            return (self.get_ancestors_cousin(secondRel, firstRel), common)
        else:
            return (
                self.get_cousins_descendant(other_person, firstRel, secondRel),
                common,
            )

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
        return self.get_relationship(reltocommon_a, reltocommon_b, gender_a, gender_b)[
            0
        ]

    def get_sibling_relationship_string(
        self, sib_type, gender_a, gender_b, in_law_a=False, in_law_b=False
    ):
        if gender_b == Person.MALE:
            return self.get_ancestors_brother("")
        else:
            return self.get_ancestors_sister("")


if __name__ == "__main__":
    # Test function. Call it as follows from the command line (so as to find
    #        imported modules):
    #    export PYTHONPATH=/path/to/gramps/src
    # python src/plugins/rel/rel_fi.py
    # (Above not needed here)

    """TRANSLATORS, copy this if statement at the bottom of your
    rel_xx.py module, and test your work with:
    python src/plugins/rel/rel_xx.py
    """
    from gramps.gen.relationship import test

    RC = RelationshipCalculator()
    test(RC, True)

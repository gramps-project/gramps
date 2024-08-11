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
# and on valuable input from Frode Jemtland
"""
Norwegian-Specific classes for relationships.
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
    "",  # brother/sister, fetter/kusine -- these are taken care of separately
    "tremenning",
    "firemenning",
    "femmenning",
    "seksmenning",
    "sjumenning",
    "åttemenning",
    "nimenning",
    "timenning",
    "ellevemenning",
    "tolvmenning",
    "tretenmenning",
    "fjortenmenning",
    "femtenmenning",
    "sekstenmenning",
    "syttenmenning",
    "attenmenning",
    "nittenmenning",
    "tjuemenning",
]

_cousin_terms = _cousin_level + ["fetter", "kusine"]


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
        if level == 0:
            return "forelder"
        else:
            return "ane i %d-te generationen" % (level + 1)

    def get_cousin(self, level):
        if level > len(_cousin_level) - 1:
            # FIXME: use Norwegian term term here,
            # UPDATED by Frode: unsure about the expretion "en fjern slektning", should it be just "fjern slektning".
            # Need to see it used in the program to get the understanding.
            return "en fjern slektning"
        else:
            return _cousin_level[level]

    def pair_up(self, rel_list):
        result = []
        item = ""
        for word in rel_list[:]:
            if not word:
                continue
            if word in _cousin_terms:
                if item:
                    result.append(item)
                    item = ""
                result.append(word)
                continue
            if item:
                if word == "sønne":
                    word = "sønn"
                result.append(item + word)
                item = ""
            else:
                item = word
        if item:
            result.append(item)
        gen_result = [item + "s" for item in result[0:-1]]
        return " ".join(gen_result + result[-1:])

    def get_direct_ancestor(self, person, rel_string):
        result = []
        for rel in rel_string:
            if rel == "f":
                result.append("far")
            else:
                result.append("mor")
        return self.pair_up(result)

    def get_direct_descendant(self, person, rel_string):
        result = []
        for ix in range(len(rel_string) - 2, -1, -1):
            if rel_string[ix] == "f":
                result.append("sønne")
            else:
                result.append("datter")
        if person == Person.MALE:
            result.append("sønn")
        else:
            result.append("datter")
        return self.pair_up(result)

    def get_ancestors_cousin(self, person, rel_string_long, rel_string_short):
        result = []
        removed = len(rel_string_long) - len(rel_string_short)
        level = len(rel_string_short) - 1
        for ix in range(removed):
            if rel_string_long[ix] == "f":
                result.append("far")
            else:
                result.append("mor")
        if level > 1:
            result.append(self.get_cousin(level))
        elif person == Person.MALE:
            result.append("fetter")
        else:
            result.append("kusine")
        main_string = self.get_two_way_rel(person, rel_string_short, rel_string_long)
        aux_string = self.pair_up(result)
        return "%s (%s)" % (main_string, aux_string)

    def get_cousins_descendant(self, person, rel_string_long, rel_string_short):
        result = []
        aux_string = ""
        removed = len(rel_string_long) - len(rel_string_short) - 1
        level = len(rel_string_short) - 1
        if level > 1:  # Cousin terms without gender
            result.append(self.get_cousin(level))
        elif level == 1:  # gender-dependent fetter/kusine
            if rel_string_long[removed] == "f":
                result.append("fetter")
            else:
                result.append("kusine")
        elif rel_string_long[removed] == "f":
            result.append("bror")
        else:
            result.append("søster")
        for ix in range(removed - 1, -1, -1):
            if rel_string_long[ix] == "f":
                result.append("sønn")
            else:
                result.append("datter")
        if person == Person.MALE:
            result.append("sønn")
        else:
            result.append("datter")
        main_string = self.get_two_way_rel(person, rel_string_long, rel_string_short)
        if level:
            aux_string = " (%s)" % self.pair_up(result)
        return "%s%s" % (main_string, aux_string)

    def get_ancestors_brother(self, rel_string):
        result = []
        for ix in range(len(rel_string) - 1):
            if rel_string[ix] == "f":
                result.append("far")
            else:
                result.append("mor")
        result.append("bror")
        return self.pair_up(result)

    def get_ancestors_sister(self, rel_string):
        result = []
        for ix in range(len(rel_string) - 1):
            if rel_string[ix] == "f":
                result.append("far")
            else:
                result.append("mor")
        result.append("søster")
        return self.pair_up(result)

    def get_two_way_rel(self, person, first_rel_string, second_rel_string):
        result = []
        for ix in range(len(second_rel_string) - 1):
            if second_rel_string[ix] == "f":
                result.append("far")
            else:
                result.append("mor")
        if len(first_rel_string) > 1:
            if first_rel_string[-2] == "f":
                result.append("bror")
            else:
                result.append("søster")
            for ix in range(len(first_rel_string) - 3, -1, -1):
                if first_rel_string[ix] == "f":
                    result.append("sønne")
                else:
                    result.append("datter")
            if person == Person.MALE:
                result.append("sønn")
            else:
                result.append("datter")
        else:
            if person == Person.MALE:
                result.append("bror")
            else:
                result.append("søster")
        return self.pair_up(result)

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
            return (
                self.get_ancestors_cousin(other_person, secondRel, firstRel),
                common,
            )
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
        return self.get_two_way_rel(gender_b, "", "")


if __name__ == "__main__":
    # Test function. Call it as follows from the command line (so as to find
    #        imported modules):
    #    export PYTHONPATH=/path/to/gramps/src
    # python src/plugins/rel/rel_no.py
    # (Above not needed here)

    """TRANSLATORS, copy this if statement at the bottom of your
    rel_xx.py module, and test your work with:
    python src/plugins/rel/rel_xx.py
    """
    from gramps.gen.relationship import test

    RC = RelationshipCalculator()
    test(RC, True)

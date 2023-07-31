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
# and on valuable input from Lars Kr. Lundin
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
# Danish-specific definitions of relationships
#
# -------------------------------------------------------------------------

_level_name = [
    "",
    "første",
    "anden",
    "tredje",
    "fjerde",
    "femte",
    "sjette",
    "syvende",
    "ottende",
    "niende",
    "tiende",
    "ellevte",
    "tolvte",
    "trettende",
    "fjortende",
    "femtende",
    "sekstende",
    "syttende",
    "attende",
    "nittende",
    "tyvende",
    "enogtyvende",
    "toogtyvende",
    "treogtyvende",
    "fireogtyvende",
    "femogtyvende",
    "seksogtyvende",
    "syvogtyvende",
    "otteogtyvende",
    "niogtyvende",
    "tredivte",
]

_parents_level = [
    "forældre",
    "bedsteforældre",
    "oldeforældre",
    "tipoldeforældre",
    "tiptipoldeforældre",
    "tiptiptipoldeforældre",
]

_father_level = [
    "",
    "faderen",
    "bedstefaderen",
    "oldefaderen",
    "tipoldefaderen",
]

_mother_level = [
    "",
    "moderen",
    "bedstemoderen",
    "oldemoderen",
    "tipoldemoderen",
]

_son_level = [
    "",
    "sønnen",
    "barnebarnet",
    "oldebarnet",
]

_daughter_level = [
    "",
    "datteren",
    "barnebarnet",
    "oldebarnet",
]

_sister_level = [
    "",
    "søsteren",
    "tanten",
    "grandtanten",
    "oldetanten",
]

_brother_level = [
    "",
    "broderen",
    "onklen",
    "grandonklen",
    "oldeonkel",
]

_nephew_level = [
    "",
    "nevøen",
    "næstsøskendebarnet",
    "broderens barnebarn",
]

_niece_level = [
    "",
    "niecen",
    "næstsøskendebarnet",
    "søsterens barnebarn",
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
            # return "fjern forfader"
            # Instead of "remote ancestors" using "tip (level) oldeforældre" here.
            return "tip (%d) oldeforældre" % level
        else:
            return _parents_level[level]

    def pair_up(self, rel_list):
        result = []
        item = ""
        for word in rel_list[:]:
            if not word:
                continue
            if item:
                if word == "søster":
                    item = item[0:-1]
                    word = "ster"
                elif word == "sønne":
                    word = "søn"
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
            result.append("søn")
        else:
            result.append("datter")
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
                result.append("søn")
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
        else:
            return (self.get_two_way_rel(other_person, firstRel, secondRel), common)

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
    # python src/plugins/rel/rel_da.py
    # (Above not needed here)

    """TRANSLATORS, copy this if statement at the bottom of your
    rel_xx.py module, and test your work with:
    python src/plugins/rel/rel_xx.py
    """
    from gramps.gen.relationship import test

    RC = RelationshipCalculator()
    test(RC, True)

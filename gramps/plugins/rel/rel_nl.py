# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2005  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2018       Robin van der Vliet
# Copyright (C) 2020       Jan Sparreboom
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

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------

from gramps.gen.lib import Person
import gramps.gen.relationship

# -------------------------------------------------------------------------
#
# Levels
#
# -------------------------------------------------------------------------

_ordinal_level = [
    "",
    "eerste",
    "tweede",
    "derde",
    "vierde",
    "vijfde",
    "zesde",
    "zevende",
    "achtste",
    "negende",
    "tiende",
    "elfde",
    "twaalfde",
    "dertiende",
    "veertiende",
    "vijftiende",
    "zestiende",
    "zeventiende",
    "achttiende",
    "negentiende",
    "twintigste",
    "eenentwintigste",
    "tweeëntwintigste",
    "drieëntwintigste",
    "vierentwintigste",
    "vijfentwintigste",
    "zesentwintigste",
    "zevenentwintigste",
    "achtentwintigste",
    "negenentwintigste",
    "dertigste",
    "eenendertigste",
    "tweeëndertigste",
    "drieëndertigste",
    "vierendertigste",
    "vijfendertigste",
    "zesendertigste",
    "zevenendertigste",
    "achtendertigste",
    "negenendertigste",
    "veertigste",
    "eenenveertigste",
    "tweeënveertigste",
    "drieënveertigste",
    "vierenveertigste",
    "vijfenveertigste",
    "zesenveertigste",
    "zevenenveertigste",
    "achtenveertigste",
    "negenenveertigste",
    "vijftigste",
]

_removed_level = [
    "",
    "",
    "groot",
    "overgroot",
    "betovergroot",
    "oud",
    "oudgroot",
    "oudovergroot",
    "oudbetovergroot",
    "stam",
    "stamgroot",
    "stamovergroot",
    "stambetovergroot",
    "stamoud",
    "stamoudgroot",
    "stamoudovergroot",
    "stamoudbetovergroot",
    "edel",
    "edelgroot",
    "edelovergroot",
    "edelbetovergroot",
    "edeloud",
    "edeloudgroot",
    "edeloudovergroot",
    "edeloudbetovergroot",
    "edelstam",
    "edelstamgroot",
    "edelstamovergroot",
    "edelstambetovergroot",
    "edelstamoud",
    "edelstamoudgroot",
    "edelstamoudovergroot",
    "edelstamoudbetovergroot",
    "voor",
    "voorgroot",
    "voorovergroot",
    "voorbetovergroot",
    "vooroud",
    "vooroudgroot",
    "vooroudovergroot",
    "vooroudbetovergroot",
    "voorstam",
    "voorstamgroot",
    "voorstamovergroot",
    "voorstambetovergroot",
    "voorstamoud",
    "voorstamoudgroot",
    "voorstamoudovergroot",
    "voorstamoudbetovergroot",
    "vooredel",
]

_child_level = ["", "", "klein", "achterklein", "achterachterklein"]

_nibling_level = ["", "", "achter", "achterachter", "achterachterachter"]

_parents_level = [
    "",
    "ouders",
    "grootouders",
    "overgrootouders",
    "betovergrootouders",
    "overgrootouders 5e graad",
    "overgrootouders 6e graad",
    "overgrootouders 7e graad",
    "overgrootouders 8e graad",
    "overgrootouders 9e graad",
    "overgrootouders 10e graad",
    "overgrootouders 11e graad",
    "overgrootouders 12e graad",
    "overgrootouders 13e graad",
    "overgrootouders 14e graad",
    "overgrootouders 15e graad",
    "overgrootouders 16e graad",
    "overgrootouders 17e graad",
    "overgrootouders 18e graad",
    "overgrootouders 19e graad",
    "overgrootouders 20e graad",
    "overgrootouders 21e graad",
    "overgrootouders 22e graad",
    "overgrootouders 23e graad",
    "overgrootouders 24e graad",
    "overgrootouders 25e graad",
    "overgrootouders 26e graad",
    "overgrootouders 27e graad",
    "overgrootouders 28e graad",
    "overgrootouders 29e graad",
    "overgrootouders 30e graad",
    "overgrootouders 31e graad",
    "overgrootouders 32e graad",
    "overgrootouders 33e graad",
    "overgrootouders 34e graad",
    "overgrootouders 35e graad",
    "overgrootouders 36e graad",
    "overgrootouders 37e graad",
    "overgrootouders 38e graad",
    "overgrootouders 39e graad",
    "overgrootouders 40e graad",
    "overgrootouders 41e graad",
    "overgrootouders 42e graad",
    "overgrootouders 43e graad",
    "overgrootouders 44e graad",
    "overgrootouders 45e graad",
    "overgrootouders 46e graad",
    "overgrootouders 47e graad",
    "overgrootouders 48e graad",
    "overgrootouders 49e graad",
    "overgrootouders 50e graad",
]

_siblings_level = [
    "",
    "broers en zussen",
    "ooms en tantes",
    "oudooms en -tantes",
    "overoudooms en -tantes",
    "overoudooms en -tantes 5e graad",
    "overoudooms en -tantes 6e graad",
    "overoudooms en -tantes 7e graad",
    "overoudooms en -tantes 8e graad",
    "overoudooms en -tantes 9e graad",
    "overoudooms en -tantes 10e graad",
    "overoudooms en -tantes 11e graad",
    "overoudooms en -tantes 12e graad",
    "overoudooms en -tantes 13e graad",
    "overoudooms en -tantes 14e graad",
    "overoudooms en -tantes 15e graad",
    "overoudooms en -tantes 16e graad",
    "overoudooms en -tantes 17e graad",
    "overoudooms en -tantes 18e graad",
    "overoudooms en -tantes 19e graad",
    "overoudooms en -tantes 20e graad",
    "overoudooms en -tantes 21e graad",
    "overoudooms en -tantes 22e graad",
    "overoudooms en -tantes 23e graad",
    "overoudooms en -tantes 24e graad",
    "overoudooms en -tantes 25e graad",
    "overoudooms en -tantes 26e graad",
    "overoudooms en -tantes 27e graad",
    "overoudooms en -tantes 28e graad",
    "overoudooms en -tantes 29e graad",
    "overoudooms en -tantes 30e graad",
    "overoudooms en -tantes 41e graad",
    "overoudooms en -tantes 42e graad",
    "overoudooms en -tantes 43e graad",
    "overoudooms en -tantes 44e graad",
    "overoudooms en -tantes 45e graad",
    "overoudooms en -tantes 46e graad",
    "overoudooms en -tantes 47e graad",
    "overoudooms en -tantes 48e graad",
    "overoudooms en -tantes 49e graad",
    "overoudooms en -tantes 50e graad",
]

_children_level = [
    "",
    "kinderen",
    "kleinkinderen",
    "achterkleinkinderen",
    "betachterkleinkinderen",
    "kleinkinderen 5e graad",
    "kleinkinderen 6e graad",
    "kleinkinderen 7e graad",
    "kleinkinderen 8e graad",
    "kleinkinderen 9e graad",
    "kleinkinderen 10e graad",
    "kleinkinderen 11e graad",
    "kleinkinderen 12e graad",
    "kleinkinderen 13e graad",
    "kleinkinderen 14e graad",
    "kleinkinderen 15e graad",
    "kleinkinderen 16e graad",
    "kleinkinderen 17e graad",
    "kleinkinderen 18e graad",
    "kleinkinderen 19e graad",
    "kleinkinderen 20e graad",
    "kleinkinderen 21e graad",
    "kleinkinderen 22e graad",
    "kleinkinderen 23e graad",
    "kleinkinderen 24e graad",
    "kleinkinderen 25e graad",
    "kleinkinderen 26e graad",
    "kleinkinderen 27e graad",
    "kleinkinderen 28e graad",
    "kleinkinderen 29e graad",
    "kleinkinderen 30e graad",
    "kleinkinderen 31e graad",
    "kleinkinderen 32e graad",
    "kleinkinderen 33e graad",
    "kleinkinderen 34e graad",
    "kleinkinderen 35e graad",
    "kleinkinderen 36e graad",
    "kleinkinderen 37e graad",
    "kleinkinderen 38e graad",
    "kleinkinderen 39e graad",
    "kleinkinderen 40e graad",
    "kleinkinderen 41e graad",
    "kleinkinderen 42e graad",
    "kleinkinderen 43e graad",
    "kleinkinderen 44e graad",
    "kleinkinderen 45e graad",
    "kleinkinderen 46e graad",
    "kleinkinderen 47e graad",
    "kleinkinderen 48e graad",
    "kleinkinderen 49e graad",
    "kleinkinderen 50e graad",
]

_nephews_nieces_level = [
    "",
    "broers en zussen",
    "neven en nichten",
    "achterneven en -nichten",
    "achterneven en -nichten 4e graad",
    "achterneven en -nichten 5e graad",
    "achterneven en -nichten 6e graad",
    "achterneven en -nichten 7e graad",
    "achterneven en -nichten 8e graad",
    "achterneven en -nichten 9e graad",
    "achterneven en -nichten 10e graad",
    "achterneven en -nichten 11e graad",
    "achterneven en -nichten 12e graad",
    "achterneven en -nichten 13e graad",
    "achterneven en -nichten 14e graad",
    "achterneven en -nichten 15e graad",
    "achterneven en -nichten 16e graad",
    "achterneven en -nichten 17e graad",
    "achterneven en -nichten 18e graad",
    "achterneven en -nichten 19e graad",
    "achterneven en -nichten 20e graad",
    "achterneven en -nichten 21e graad",
    "achterneven en -nichten 22e graad",
    "achterneven en -nichten 23e graad",
    "achterneven en -nichten 24e graad",
    "achterneven en -nichten 25e graad",
    "achterneven en -nichten 26e graad",
    "achterneven en -nichten 27e graad",
    "achterneven en -nichten 28e graad",
    "achterneven en -nichten 29e graad",
    "achterneven en -nichten 30e graad",
    "achterneven en -nichten 31e graad",
    "achterneven en -nichten 32e graad",
    "achterneven en -nichten 33e graad",
    "achterneven en -nichten 34e graad",
    "achterneven en -nichten 35e graad",
    "achterneven en -nichten 36e graad",
    "achterneven en -nichten 37e graad",
    "achterneven en -nichten 38e graad",
    "achterneven en -nichten 39e graad",
    "achterneven en -nichten 40e graad",
    "achterneven en -nichten 41e graad",
    "achterneven en -nichten 42e graad",
    "achterneven en -nichten 43e graad",
    "achterneven en -nichten 44e graad",
    "achterneven en -nichten 45e graad",
    "achterneven en -nichten 46e graad",
    "achterneven en -nichten 47e graad",
    "achterneven en -nichten 48e graad",
    "achterneven en -nichten 49e graad",
    "achterneven en -nichten 50e graad",
]

# -------------------------------------------------------------------------
#
# Relationship calculator Dutch version
#
# -------------------------------------------------------------------------


class RelationshipCalculator(gramps.gen.relationship.RelationshipCalculator):
    """
    RelationshipCalculator Class
    """

    # sibling strings
    STEP = "stief"
    HALF = "half"

    INLAW = "aangetrouwde "

    def __init__(self):
        gramps.gen.relationship.RelationshipCalculator.__init__(self)

    def get_parents(self, level):
        if level > len(_removed_level) - 1:
            return "verre voorouders (%d generaties)" % level
        elif level > 4:
            return "%souders (%d generaties)" % (_removed_level[level], level)
        else:
            return "%souders" % _removed_level[level]

    def _get_father(self, level, step="", inlaw=""):
        """Internal Dutch method to create relation string"""
        if level > len(_removed_level) - 1:
            return "verre %s%svoorvader (%d generaties)" % (inlaw, step, level)
        elif level > 4:
            return "%s%s%svader (%d generaties)" % (
                inlaw,
                step,
                _removed_level[level],
                level,
            )
        else:
            return "%s%s%svader" % (inlaw, step, _removed_level[level])

    def _get_son(self, level, step="", inlaw=""):
        """Internal Dutch method to create relation string"""
        if level > len(_child_level) - 1:
            return "verre %s%sachterkleinzoon (%d generaties)" % (inlaw, step, level)
        else:
            return "%s%s%szoon" % (inlaw, step, _child_level[level])

    def _get_mother(self, level, step="", inlaw=""):
        """Internal Dutch method to create relation string"""
        if level > len(_removed_level) - 1:
            return "verre %s%svoormoeder (%d generaties)" % (inlaw, step, level)
        elif level > 4:
            return "%s%s%smoeder (%d generaties)" % (
                inlaw,
                step,
                _removed_level[level],
                level,
            )
        else:
            return "%s%s%smoeder" % (inlaw, step, _removed_level[level])

    def _get_daughter(self, level, step="", inlaw=""):
        """Internal Dutch method to create relation string"""
        if level > len(_child_level) - 1:
            return "verre %s%sachterkleindochter (%d generaties)" % (inlaw, step, level)
        else:
            return "%s%s%sdochter" % (inlaw, step, _child_level[level])

    def _get_parent_unknown(self, level, step="", inlaw=""):
        """Internal Dutch method to create relation string"""
        if level > len(_removed_level) - 1:
            return "verre %s%svoorouder (%d generaties)" % (inlaw, step, level)
        elif level > 4:
            return "%s%s%souder (%d generaties)" % (
                inlaw,
                step,
                _removed_level[level],
                level,
            )
        else:
            return "%s%s%souder" % (inlaw, step, _removed_level[level])

    def _get_child_unknown(self, level, step="", inlaw=""):
        """Internal Dutch method to create relation string"""
        if inlaw == "aangetrouwde ":
            # The word "kind" is grammatically neuter, so it has a different adjective.
            inlaw = "aangetrouwd "

        if level > len(_child_level) - 1:
            return "ver %s%sachterkleinkind (%d generaties)" % (inlaw, step, level)
        else:
            return "%s%s%skind" % (inlaw, step, _child_level[level])

    def _get_aunt(self, level, removed, step="", inlaw=""):
        """Internal Dutch method to create relation string"""
        if removed == 1 and level < len(_removed_level):
            if level > 4:
                return "%s%s%stante (%d generaties)" % (
                    inlaw,
                    step,
                    _removed_level[level],
                    level,
                )
            else:
                return "%s%s%stante" % (inlaw, step, _removed_level[level])
        elif removed == 1:
            return "verre %s%stante (%d generaties)" % (inlaw, step, level)
        elif level > len(_removed_level) - 1 and removed > len(_ordinal_level) - 1:
            return "verre %s%stante (%d generaties, %d graden)" % (
                inlaw,
                step,
                level,
                removed,
            )
        elif level > len(_removed_level) - 1:
            return "verre %s%stante van de %s graad (%d generaties)" % (
                inlaw,
                step,
                _ordinal_level[removed],
                level,
            )
        else:
            if level > 4:
                return (
                    "%s%s%stante (%d generaties)"
                    % (inlaw, step, _removed_level[level], level)
                    + " "
                    + _ordinal_level[removed]
                    + " graad"
                )
            else:
                return (
                    "%s%s%stante" % (inlaw, step, _removed_level[level])
                    + " "
                    + _ordinal_level[removed]
                    + " graad"
                )

    def _get_uncle(self, level, removed, step="", inlaw=""):
        """Internal Dutch method to create relation string"""
        if removed == 1 and level < len(_removed_level):
            if level > 4:
                return "%s%s%soom (%d generaties)" % (
                    inlaw,
                    step,
                    _removed_level[level],
                    level,
                )
            else:
                return "%s%s%soom" % (inlaw, step, _removed_level[level])
        elif removed == 1:
            return "verre %s%soom (%d generaties)" % (inlaw, step, level)
        elif level > len(_removed_level) - 1 and removed > len(_ordinal_level) - 1:
            return "verre %s%soom (%d generaties, %d graden)" % (
                inlaw,
                step,
                level,
                removed,
            )
        elif level > len(_removed_level) - 1:
            return "verre %s%soom van de %s graad (%d generaties)" % (
                inlaw,
                step,
                _ordinal_level[removed],
                level,
            )
        else:
            if level > 4:
                return (
                    "%s%s%soom (%d generaties)"
                    % (inlaw, step, _removed_level[level], level)
                    + " "
                    + _ordinal_level[removed]
                    + " graad"
                )
            else:
                return (
                    "%s%s%soom" % (inlaw, step, _removed_level[level])
                    + " "
                    + _ordinal_level[removed]
                    + " graad"
                )

    def _get_sibling(self, level, step="", inlaw=""):
        """overwrite of English method to return unknown gender sibling"""
        assert level == 1
        return (
            self._get_male_cousin(0, step=step, inlaw=inlaw)
            + " of "
            + self._get_female_cousin(0, step=step, inlaw=inlaw)
        )

    def _get_nephew(self, level, removed=1, step="", inlaw=""):
        """Internal Dutch method to create relation string"""
        if removed == 1 and level < len(_nibling_level):
            return "%s%s%sneef" % (inlaw, step, _nibling_level[level])
        elif removed == 1:
            return "verre %s%sneef (%d generaties)" % (inlaw, step, level)
        elif level > len(_nibling_level) - 1 and removed > len(_ordinal_level) - 1:
            return "verre %s%sneef (%d generaties, %d graden)" % (
                inlaw,
                step,
                level,
                removed,
            )
        elif level > len(_nibling_level) - 1:
            return "verre %s%sneef van de %s graad (%d generaties)" % (
                inlaw,
                step,
                _ordinal_level[removed],
                level,
            )
        else:
            return (
                "%s%s%sneef" % (inlaw, step, _nibling_level[level])
                + " "
                + _ordinal_level[removed]
                + " graad"
            )

    def _get_niece(self, level, removed=1, step="", inlaw=""):
        """Internal Dutch method to create relation string"""
        if removed == 1 and level < len(_nibling_level):
            return "%s%s%snicht" % (inlaw, step, _nibling_level[level])
        elif removed == 1:
            return "verre %s%snicht (%d generaties)" % (inlaw, step, level)
        elif level > len(_nibling_level) - 1 and removed > len(_ordinal_level) - 1:
            return "verre %s%snicht (%d generaties, %d graden)" % (
                inlaw,
                step,
                level,
                removed,
            )
        elif level > len(_nibling_level) - 1:
            return "verre %s%snicht van de %s graad (%d generaties)" % (
                inlaw,
                step,
                _ordinal_level[removed],
                level,
            )
        else:
            return (
                "%s%s%snicht" % (inlaw, step, _nibling_level[level])
                + " "
                + _ordinal_level[removed]
                + " graad"
            )

    def _get_male_cousin(self, removed, step="", inlaw=""):
        """Specific Dutch thing, the nieces/nephews on same level are called
        going sideways in a branch as the nieces/newphews going downward
        from your brother/sisters. This used to be called "kozijn"
        """
        removed -= 1
        if removed > len(_ordinal_level) - 1:
            return "verre %s%sneef (kozijn, %d graden)" % (inlaw, step, removed)
        elif removed == 0:
            return "%s%sbroer" % (inlaw, step)
        else:
            return (
                "%s%sneef (kozijn)" % (inlaw, step)
                + " "
                + _ordinal_level[removed]
                + " graad"
            )

    def _get_female_cousin(self, removed, step="", inlaw=""):
        """Specific Dutch thing, the nieces/nephews on same level are called
        going sideways in a branch as the nieces/newphews going downward
        from your brother/sisters. This used to be called "kozijn"
        """
        removed -= 1
        if removed > len(_ordinal_level) - 1:
            return "verre %s%snicht (kozijn, %d graden)" % (inlaw, step, removed)
        elif removed == 0:
            return "%s%szus" % (inlaw, step)
        else:
            return (
                "%s%snicht (kozijn)" % (inlaw, step)
                + " "
                + _ordinal_level[removed]
                + " graad"
            )

    # NIEUW
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
        rel_str = "verre familie"
        if Ga == 0:
            # These are descendants
            if Gb < len(_children_level):
                rel_str = _children_level[Gb]
            else:
                rel_str = "verre afstammelingen"
        elif Gb == 0:
            # These are parents/grand parents
            if Ga < len(_parents_level):
                rel_str = _parents_level[Ga]
            else:
                rel_str = "verre voorouders"
        elif Gb == 1:
            # These are siblings/aunts/uncles
            if Ga < len(_siblings_level):
                rel_str = _siblings_level[Ga]
            else:
                rel_str = "verre ooms/tantes"
        elif Ga == 1:
            # These are nieces/nephews
            if Gb < len(_nephews_nieces_level):
                rel_str = _nephews_nieces_level[Gb]
            else:
                rel_str = "verre neven/nichten"
        elif Ga > 1 and Ga == Gb:
            # These are cousins in the same generation
            if Ga <= len(_ordinal_level):
                rel_str = "%s neven" % _ordinal_level[Ga - 1]
            else:
                rel_str = "verre neven"
        elif Ga > 1 and Ga > Gb:
            # These are cousins in different generations with the second person
            # being in a higher generation from the common ancestor than the
            # first person.
            if Gb <= len(_LEVEL_NAME) and (Ga - Gb) < len(_removed_level):
                rel_str = "%s neven%s (omhoog)" % (
                    _ordinal_level[Gb - 1],
                    _removed_level[Ga - Gb],
                )
            else:
                rel_str = "verre neven"
        elif Gb > 1 and Gb > Ga:
            # These are cousins in different generations with the second person
            # being in a lower generation from the common ancestor than the
            # first person.
            if Ga <= len(_LEVEL_NAME) and (Gb - Ga) < len(_removed_level):
                rel_str = "%s neven%s (omlaag)" % (
                    _ordinal_level[Ga - 1],
                    _removed_level[Gb - Ga],
                )
            else:
                rel_str = "verre neven"

        if in_law_b is True:
            rel_str = "echtgenoten van %s" % rel_str

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
        Return a string representing the relationship between the two people,
        see english method, eg b is father of a
        """
        if only_birth:
            step = ""
        else:
            step = self.STEP

        if in_law_a or in_law_b:
            inlaw = self.INLAW
        else:
            inlaw = ""

        rel_str = "verre %s%sfamilie" % (inlaw, step)

        if Gb == 0:
            # b is ancestor
            if Ga == 0:
                rel_str = "zelfde persoon"
            elif Ga == 1 and inlaw and not step:
                if gender_b == Person.MALE:
                    rel_str = "schoonvader"
                elif gender_b == Person.FEMALE:
                    rel_str = "schoonmoeder"
                else:
                    rel_str = "schoonouder"
            elif gender_b == Person.MALE:
                rel_str = self._get_father(Ga, step, inlaw)
            elif gender_b == Person.FEMALE:
                rel_str = self._get_mother(Ga, step, inlaw)
            else:
                rel_str = self._get_parent_unknown(Ga, step, inlaw)
        elif Ga == 0:
            # a is descendant
            if Gb == 1 and inlaw and not step:
                if gender_b == Person.MALE:
                    rel_str = "schoonzoon"
                elif gender_b == Person.FEMALE:
                    rel_str = "schoondochter"
                else:
                    rel_str = "schoonkind"
            elif Gb == 1 and inlaw and step:
                # inlaw stepchild
                if gender_b == Person.MALE:
                    rel_str = "aangetrouwde stiefzoon"
                elif gender_b == Person.FEMALE:
                    rel_str = "aangetrouwde stiefdochter"
                else:
                    rel_str = "aangetrouwd stiefkind"
            elif gender_b == Person.MALE:
                rel_str = self._get_son(Gb, step, inlaw)
            elif gender_b == Person.FEMALE:
                rel_str = self._get_daughter(Gb, step, inlaw)
            else:
                rel_str = self._get_child_unknown(Gb, step, inlaw)
        elif Ga > Gb:
            # b is higher in the branch, in english uncle/aunt or
            # cousin up, in Dutch always 'oom/tante'
            if gender_b == Person.MALE:
                rel_str = self._get_uncle(Ga - Gb, Gb, step, inlaw)
            elif gender_b == Person.FEMALE:
                rel_str = self._get_aunt(Ga - Gb, Gb, step, inlaw)
            else:
                rel_str = (
                    self._get_uncle(Ga - Gb, Gb, step, inlaw)
                    + " of "
                    + self._get_aunt(Ga - Gb, Gb, step, inlaw)
                )
        elif Ga < Gb:
            # b is lower in the branch, in english niece/nephew or
            # cousin down, in Dutch always 'neef/nicht'
            if gender_b == Person.MALE:
                rel_str = self._get_nephew(Gb - Ga, Ga, step, inlaw)
            elif gender_b == Person.FEMALE:
                rel_str = self._get_niece(Gb - Ga, Ga, step, inlaw)
            else:
                rel_str = (
                    self._get_nephew(Gb - Ga, Ga, step, inlaw)
                    + " of "
                    + self._get_niece(Gb - Ga, Ga, step, inlaw)
                )
        else:
            # people on the same level Ga == Gb
            if gender_b == Person.MALE:
                rel_str = self._get_male_cousin(Ga, step, inlaw)
            elif gender_b == Person.FEMALE:
                rel_str = self._get_female_cousin(Ga, step, inlaw)
            else:
                rel_str = (
                    self._get_male_cousin(Ga, step, inlaw)
                    + " of "
                    + self._get_female_cousin(Ga, step, inlaw)
                )

        return rel_str

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
        elif sib_type == self.HALF_SIB_FATHER or sib_type == self.HALF_SIB_MOTHER:
            typestr = self.HALF
        elif sib_type == self.STEP_SIB:
            typestr = self.STEP

        if in_law_a or in_law_b:
            inlaw = self.INLAW
        else:
            inlaw = ""

        if inlaw and not typestr:
            if gender_b == Person.MALE:
                rel_str = "schoonbroer"
            elif gender_b == Person.FEMALE:
                rel_str = "schoonzus"
            else:
                rel_str = "schoonbroer of -zus"
        else:
            if gender_b == Person.MALE:
                rel_str = self._get_male_cousin(1, typestr, inlaw)
            elif gender_b == Person.FEMALE:
                rel_str = self._get_female_cousin(1, typestr, inlaw)
            else:
                rel_str = (
                    self._get_male_cousin(1, typestr, inlaw)
                    + " of "
                    + self._get_female_cousin(1, typestr, inlaw)
                )
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

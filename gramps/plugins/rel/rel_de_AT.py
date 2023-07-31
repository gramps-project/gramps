# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2005  Donald N. Allingham
# Copyright (C) 2008       Stefan Siegel
# Copyright (C) 2008       Brian G. Matherly
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

# Original version written by Alex Roitman, largely based on relationship.py
# by Don Allingham and on valuable input from Dr. Martin Senftleben
# Modified by Joachim Breitner to not use „Großcousine“, in accordance with
# http://de.wikipedia.org/wiki/Verwandtschaftsbeziehung
# Rewritten from scratch for Gramps 3 by Stefan Siegel,
# loosely based on rel_fr.py
#
# some changes for Austrian terms:
# siebte -> siebente, Adoptivkind/-eltern -> Wahlkind/ -eltern, Schwippschwager -> Schwiegerschwager
"""
German-Austrian specific classes for relationships.
"""

# -------------------------------------------------------------------------
#
# standard python modules
#
# -------------------------------------------------------------------------

import re

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------

from gramps.gen.lib import Person
import gramps.gen.relationship

# -------------------------------------------------------------------------
#
#
#
# -------------------------------------------------------------------------

_ordinal = [
    "nullte",
    "erste",
    "zweite",
    "dritte",
    "vierte",
    "fünfte",
    "sechste",
    "siebente",
    "achte",
    "neunte",
    "zehnte",
    "elfte",
    "zwölfte",
]

_removed = [
    "",
    "",
    "Groß",
    "Urgroß",
    "Alt",
    "Altgroß",
    "Alturgroß",
    "Ober",
    "Obergroß",
    "Oberurgroß",
    "Stamm",
    "Stammgroß",
    "Stammurgroß",
    "Ahnen",
    "Ahnengroß",
    "Ahnenurgroß",
    "Urahnen",
    "Urahnengroß",
    "Urahnenurgroß",
    "Erz",
    "Erzgroß",
    "Erzurgroß",
    "Erzahnen",
    "Erzahnengroß",
    "Erzahnenurgroß",
]

_lineal_up = {
    "many": "%(p)sEltern%(s)s",
    "unknown": "%(p)sElter%(s)s",  # "Elter" sounds strange but is correct
    "male": "%(p)sVater%(s)s",
    "female": "%(p)sMutter%(s)s",
}
_lineal_down = {
    "many": "%(p)sKinder%(s)s",
    "unknown": "%(p)sKind%(s)s",
    "male": "%(p)sSohn%(s)s",
    "female": "%(p)sTochter%(s)s",
}
_collateral_up = {
    "many": "%(p)sOnkel und %(p)sTanten%(s)s",
    "unknown": "%(p)sOnkel oder %(p)sTante%(s)s",
    "male": "%(p)sOnkel%(s)s",
    "female": "%(p)sTante%(s)s",
}
_collateral_down = {
    "many": "%(p)sNeffen und %(p)sNichten%(s)s",
    "unknown": "%(p)sNeffe oder %(p)sNichte%(s)s",
    "male": "%(p)sNeffe%(s)s",
    "female": "%(p)sNichte%(s)s",
}
_collateral_same = {
    "many": "%(p)sCousins und %(p)sCousinen%(s)s",
    "unknown": "%(p)sCousin oder %(p)sCousine%(s)s",
    "male": "%(p)sCousin%(s)s",
    "female": "%(p)sCousine%(s)s",
}
_collateral_sib = {
    "many": "%(p)sGeschwister%(s)s",
    "unknown": "%(p)sGeschwisterkind%(s)s",
    "male": "%(p)sBruder%(s)s",
    "female": "%(p)sSchwester%(s)s",
}

_schwager = {
    "many": "%(p)sSchwager%(s)s",
    "unknown": "%(p)sSchwager%(s)s",
    "male": "%(p)sSchwager%(s)s",
    "female": "%(p)sSchwägerin%(s)s",
}
_schwiegerschwager = {
    "many": "%(p)sSchwiegerschwager%(s)s",
    "unknown": "%(p)sSchwiegerschwager%(s)s",
    "male": "%(p)sSchwiegerschwager%(s)s",
    "female": "%(p)sSchwiegerschwägerin%(s)s",
}

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

    def _make_roman(self, num):
        roman = ""
        for v, r in [
            (1000, "M"),
            (900, "CM"),
            (500, "D"),
            (400, "CD"),
            (100, "C"),
            (90, "XC"),
            (50, "L"),
            (40, "XL"),
            (10, "X"),
            (9, "IX"),
            (5, "V"),
            (4, "IV"),
            (1, "I"),
        ]:
            while num > v:
                num -= v
                roman += r
        return roman

    def _fix_caps(self, string):
        return re.sub(r"(?<=[^\s(/A-Z])[A-Z]", lambda m: m.group().lower(), string)

    def _removed_text(self, degree, removed):
        if (degree, removed) == (0, -2):
            return "Enkel"
        elif (degree, removed) == (0, -3):
            return "Urenkel"
        removed = abs(removed)
        if removed < len(_removed):
            return _removed[removed]
        else:
            return "(%s)" % self._make_roman(removed - 2)

    def _degree_text(self, degree, removed):
        if removed == 0:
            degree -= 1  # a cousin has same degree as his parent (uncle/aunt)
        if degree <= 1:
            return ""
        if degree < len(_ordinal):
            return " %sn Grades" % _ordinal[degree]
        else:
            return " %d. Grades" % degree

    def _gender_convert(self, gender):
        if gender == Person.MALE:
            return "male"
        elif gender == Person.FEMALE:
            return "female"
        else:
            return "unknown"

    def _get_relationship_string(
        self,
        Ga,
        Gb,
        gender,
        reltocommon_a="",
        reltocommon_b="",
        only_birth=True,
        in_law_a=False,
        in_law_b=False,
    ):
        common_ancestor_count = 0
        if reltocommon_a == "":
            reltocommon_a = self.REL_FAM_BIRTH
        if reltocommon_b == "":
            reltocommon_b = self.REL_FAM_BIRTH
        if reltocommon_a[-1] in [
            self.REL_MOTHER,
            self.REL_FAM_BIRTH,
            self.REL_FAM_BIRTH_MOTH_ONLY,
        ] and reltocommon_b[-1] in [
            self.REL_MOTHER,
            self.REL_FAM_BIRTH,
            self.REL_FAM_BIRTH_MOTH_ONLY,
        ]:
            common_ancestor_count += 1  # same female ancestor
        if reltocommon_a[-1] in [
            self.REL_FATHER,
            self.REL_FAM_BIRTH,
            self.REL_FAM_BIRTH_FATH_ONLY,
        ] and reltocommon_b[-1] in [
            self.REL_FATHER,
            self.REL_FAM_BIRTH,
            self.REL_FAM_BIRTH_FATH_ONLY,
        ]:
            common_ancestor_count += 1  # same male ancestor

        degree = min(Ga, Gb)
        removed = Ga - Gb

        if degree == 0 and removed < 0:
            # for descendants the "in-law" logic is reversed
            (in_law_a, in_law_b) = (in_law_b, in_law_a)

        rel_str = ""
        pre = ""
        post = ""

        if in_law_b and degree == 0:
            pre += "Stief"
        elif (not only_birth) or common_ancestor_count == 0:
            pre += "Stief-/Wahl"
        if in_law_a and (degree, removed) != (1, 0):
            # A "Schwiegerbruder" really is a "Schwager" (handled later)
            pre += "Schwieger"
        if degree != 0 and common_ancestor_count == 1:
            pre += "Halb"
        pre += self._removed_text(degree, removed)
        post += self._degree_text(degree, removed)
        if in_law_b and degree != 0 and (degree, removed) != (1, 0):
            # A "Bruder (angeheiratet)" also is a "Schwager" (handled later)
            post += " (angeheiratet)"

        if degree == 0:
            # lineal relationship
            if removed > 0:
                rel_str = _lineal_up[gender]
            elif removed < 0:
                rel_str = _lineal_down[gender]
            elif in_law_a or in_law_b:
                rel_str = "Partner"
            else:
                rel_str = "Proband"
        else:
            # collateral relationship
            if removed > 0:
                rel_str = _collateral_up[gender]
            elif removed < 0:
                rel_str = _collateral_down[gender]
            elif degree == 1:
                if in_law_a or in_law_b:
                    if in_law_a and in_law_b:
                        rel_str = _schwiegerschwager[gender]
                    else:
                        rel_str = _schwager[gender]
                else:
                    rel_str = _collateral_sib[gender]
            else:
                rel_str = _collateral_same[gender]
        return self._fix_caps(rel_str % {"p": pre, "s": post})

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
        return self._get_relationship_string(
            Ga, Gb, "many", reltocommon_a, reltocommon_b, only_birth, in_law_a, in_law_b
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
        return self._get_relationship_string(
            Ga,
            Gb,
            self._gender_convert(gender_b),
            reltocommon_a,
            reltocommon_b,
            only_birth,
            in_law_a,
            in_law_b,
        )

    def get_sibling_relationship_string(
        self, sib_type, gender_a, gender_b, in_law_a=False, in_law_b=False
    ):
        if sib_type in [self.NORM_SIB, self.UNKNOWN_SIB]:
            # the NORM_SIB translation is generic and suitable for UNKNOWN_SIB
            rel = self.REL_FAM_BIRTH
            only_birth = True
        elif sib_type == self.HALF_SIB_FATHER:
            rel = self.REL_FAM_BIRTH_FATH_ONLY
            only_birth = True
        elif sib_type == self.HALF_SIB_MOTHER:
            rel = self.REL_FAM_BIRTH_MOTH_ONLY
            only_birth = True
        elif sib_type == self.STEP_SIB:
            rel = self.REL_FAM_NONBIRTH
            only_birth = False
        return self._get_relationship_string(
            1,
            1,
            self._gender_convert(gender_b),
            rel,
            rel,
            only_birth,
            in_law_a,
            in_law_b,
        )


if __name__ == "__main__":
    # Test function. Call it as follows from the command line (so as to find
    #        imported modules):
    #    export PYTHONPATH=/path/to/gramps/src
    # python src/plugins/rel/rel_de.py
    # (Above not needed here)

    """TRANSLATORS, copy this if statement at the bottom of your
    rel_xx.py module, and test your work with:
    python src/plugins/rel/rel_xx.py
    """
    from gramps.gen.relationship import test

    rc = RelationshipCalculator()
    test(rc, True)

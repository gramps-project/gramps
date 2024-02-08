# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2005  Donald N. Allingham
# Copyright (C) 2023       Avi Markovitz
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
Hebrew-specific classes for relationships.
"""
# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------
import logging

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
import gramps.gen.relationship
from gramps.gen.lib import Person

MALE = Person.MALE
FEMALE = Person.FEMALE
UNKNOWN = Person.UNKNOWN

LOG = logging.getLogger("gen.relationship")
LOG.addHandler(logging.StreamHandler())

# -------------------------------------------------------------------------
#
#
#
# -------------------------------------------------------------------------

_LEVEL_NAME = [
    "",
    "מרמה ראשונה",
    "מרמה שניה",
    "מרמה שלישית",
    "מרמה רביעית",
    "מרמה חמישית",
    "מרמה שישית",
    "מרמה שביעית",
    "מרמה שמינית",
    "מרמה תשיעית",
    "מרמה עשירית",
    "מרמה אחת עשרה",
]

_REMOVED_LEVEL = [
    "",
    "מדרגה שניה",
    "פעמיים מדרגה שניה",
    "שלוש פעמים מדרגה שניה",
    "ארבע פעמים מדרגה שניה",
    "חמש פעמים מדרגה שניה",
    "שש פעמים מדרגה שניה",
    "שבע פעמים מדרגה שניה",
    "שמונה פעמים מדרגה שניה",
    "תשע פעמים מדרגה שניה",
    "עשר פעמים מדרגה שניה",
    "אחת עשרה פעמים מדרגה שניה",
]

_PARENTS_LEVEL = [
    "",
    "הורים",
    "סבים",
    "סבות",
    "סב גדול",
    "סבה גדולה",
    "סב וסבה גדולים",
    "סב וסבה מרמה שלישית",
    "סב וסבה מרמה רביעית",
    "סב וסבה מרמה חמישית",
    "סב וסבה מרמה שישית",
    "סב וסבה מרמה שביעית",
    "סב וסבה מרמה שמינית",
    "סב וסבה מרמה תשיעית",
    "סב וסבה מרמה עשירית",
    "סב וסבה מרמה אחת עשרה",
]

_FATHER_LEVEL = [
    "",
    "סב %(step)s %(inlaw)s",
    "סב גדול %(step)s %(inlaw)s",
    "סב מרמה שלישית %(step)s %(inlaw)s",
    "סב מרמה רביעית %(step)s %(inlaw)s",
    "סב מרמה חמישית %(step)s %(inlaw)s",
    "סב מרמה שישית %(step)s %(inlaw)s",
    "סב מרמה שביעית %(step)s %(inlaw)s",
    "סב מרמה שמינית %(step)s %(inlaw)s",
    "סב מרמה תשיעית %(step)s %(inlaw)s",
    "סב מרמה עשירית %(step)s %(inlaw)s",
    "סב מרמה אחת עשרה %(step)s %(inlaw)s",
]

_MOTHER_LEVEL = [
    "",
    "סבה %(step)s %(inlaw)s",
    "סבה גדולה %(step)s %(inlaw)s",
    "סבה מרמה שלישית %(step)s %(inlaw)s",
    "סבה מרמה רביעית %(step)s %(inlaw)s",
    "סבה מרמה חמישית %(step)s %(inlaw)s",
    "סבה מרמה שישית %(step)s %(inlaw)s",
    "סבה מרמה שביעית %(step)s %(inlaw)s",
    "סבה מרמה שמינית %(step)s %(inlaw)s",
    "סבה מרמה תשיעית %(step)s %(inlaw)s",
    "סבה מרמה עשירית %(step)s %(inlaw)s",
    "סבה מרמה אחת עשרה %(step)s %(inlaw)s",
]

_SON_LEVEL = [
    "",
    "בן %(step)s %(inlaw)s",
    "נכד %(step)s %(inlaw)s",
    "נין %(step)s %(inlaw)s",
    "חימש %(step)s %(inlaw)s",
    "נכד מרמה חמישית %(step)s %(inlaw)s",
    "נכד מרמה שישית %(step)s %(inlaw)s",
    "נכד מרמה שביעית %(step)s %(inlaw)s",
    "נכד מרמה שמינית %(step)s %(inlaw)s",
    "נכד מרמה תשיעית %(step)s %(inlaw)s",
    "נכד מרמה עשירית %(step)s %(inlaw)s",
    "נכד מרמה אחת עשרה %(step)s %(inlaw)s",
    "נכד רחוק %(step)s %(inlaw)s",
    "נכד רחוק %(step)s %(inlaw)s",
    "נכד רחוק %(step)s %(inlaw)s",
    "נכד רחוק %(step)s %(inlaw)s",
    "נכד רחוק %(step)s %(inlaw)s",
    "נכד רחוק %(step)s %(inlaw)s",
    "נכד רחוק %(step)s %(inlaw)s",
    "נכד רחוק %(step)s %(inlaw)s",
    "נכד רחוק %(step)s %(inlaw)s",
    "נכד רחוק %(step)s %(inlaw)s",
    "נכד רחוק %(step)s %(inlaw)s",
    "נכד רחוק %(step)s %(inlaw)s",
    "נכד רחוק %(step)s %(inlaw)s",
    "נכד רחוק %(step)s %(inlaw)s",
    "נכד רחוק %(step)s %(inlaw)s",
    "נכד רחוק %(step)s %(inlaw)s",
    "נכד רחוק %(step)s %(inlaw)s",
    "נכד רחוק %(step)s %(inlaw)s",
]

_DAUGHTER_LEVEL = [
    "",
    "בת %(step)s %(inlaw)s",
    "נכדה %(step)s %(inlaw)s",
    "נינה %(step)s %(inlaw)s",
    "חימשה %(step)s %(inlaw)s",
    "נכדה מרמה חמישית %(step)s %(inlaw)s",
    "נכדה מרמה שישית %(step)s %(inlaw)s",
    "נכדה מרמה שביעית %(step)s %(inlaw)s",
    "נכדה מרמה שמינית %(step)s %(inlaw)s",
    "נכדה מרמה תשיעית %(step)s %(inlaw)s",
    "נכדה מרמה עשירית %(step)s %(inlaw)s",
    "נכדה מרמה אחת עשרה %(step)s %(inlaw)s",
    "נכדה רחוקה %(step)s %(inlaw)s",
    "נכדה רחוקה %(step)s %(inlaw)s",
    "נכדה רחוקה %(step)s %(inlaw)s",
    "נכדה רחוקה %(step)s %(inlaw)s",
    "נכדה רחוקה %(step)s %(inlaw)s",
    "נכדה רחוקה %(step)s %(inlaw)s",
    "נכדה רחוקה %(step)s %(inlaw)s",
    "נכדה רחוקה %(step)s %(inlaw)s",
    "נכדה רחוקה %(step)s %(inlaw)s",
    "נכדה רחוקה %(step)s %(inlaw)s",
    "נכדה רחוקה %(step)s %(inlaw)s",
    "נכדה רחוקה %(step)s %(inlaw)s",
    "נכדה רחוקה %(step)s %(inlaw)s",
    "נכדה רחוקה %(step)s %(inlaw)s",
    "נכדה רחוקה %(step)s %(inlaw)s",
    "נכדה רחוקה %(step)s %(inlaw)s",
    "נכדה רחוקה %(step)s %(inlaw)s",
    "נכדה רחוקה %(step)s %(inlaw)s",
]

_SISTER_LEVEL = [
    "",
    "אחות %(step)s %(inlaw)s",
    "דודה %(step)s %(inlaw)s",
    "דודה גדולה %(step)s %(inlaw)s",
    "דודה מרמה שלישית %(step)s %(inlaw)s",
    "דודה מרמה רביעית %(step)s %(inlaw)s",
    "דודה מרמה חמישית %(step)s %(inlaw)s",
    "דודה מרמה שישית %(step)s %(inlaw)s",
    "דודה מרמה שביעית %(step)s %(inlaw)s",
    "דודה מרמה שמינית %(step)s %(inlaw)s",
    "דודה מרמה תשיעיתית %(step)s %(inlaw)s",
    "דודה מרמה עשירית %(step)s %(inlaw)s",
    "דודה מרמה אחת עשרה%(step)s %(inlaw)s",
]

_BROTHER_LEVEL = [
    "",
    "אח %(step)s %(inlaw)s",
    "דוד %(step)s %(inlaw)s",
    "דוד גדול %(step)s %(inlaw)s",
    "דוד מרמה שלישית %(step)s %(inlaw)s",
    "דוד מרמה רביעית %(step)s %(inlaw)s",
    "דוד מרמה חמישית %(step)s %(inlaw)s",
    "דוד מרמה שישית %(step)s %(inlaw)s",
    "דוד מרמה שביעית %(step)s %(inlaw)s",
    "דוד מרמה שמינית %(step)s %(inlaw)s",
    "דוד מרמה תשיעית %(step)s %(inlaw)s",
    "דוד מרמה עשירית %(step)s %(inlaw)s",
    "דוד מרמה אחת עשרה %(step)s %(inlaw)s",
]

_NEPHEW_LEVEL = [
    "",
    "אחיין %(step)s %(inlaw)s",
    "נכדן %(step)s %(inlaw)s",
    "אחיין גדול %(step)s %(inlaw)s",
    "אחיין מרמה שלישית %(step)s %(inlaw)s",
    "אחיין מרמה רביעית %(step)s %(inlaw)s",
    "אחיין מרמה חמישית %(step)s %(inlaw)s",
    "אחיין מרמה שישית %(step)s %(inlaw)s",
    "אחיין מרמה שביעית %(step)s %(inlaw)s",
    "אחיין מרמה שמינית %(step)s %(inlaw)s",
    "אחיין מרמה תשיעית %(step)s %(inlaw)s",
    "אחיין מרמה עשירית %(step)s %(inlaw)s",
    "אחיין מרמה אחת עשרה %(step)s %(inlaw)s",
]

_NIECE_LEVEL = [
    "",
    "אחיינית %(step)s %(inlaw)s",
    "נכדנית %(step)s %(inlaw)s",
    "אחיינית גדולה %(step)s %(inlaw)s",
    "אחיינית מרמה שלישית %(step)s %(inlaw)s",
    "אחיינית מרמה רביעית %(step)s %(inlaw)s",
    "אחיינית מרמה חמישית %(step)s %(inlaw)s",
    "אחיינית מרמה שישית %(step)s %(inlaw)s",
    "אחיינית מרמה שביעית %(step)s %(inlaw)s",
    "אחיינית מרמה שמינית %(step)s %(inlaw)s",
    "אחיינית מרמה תשיעית %(step)s %(inlaw)s",
    "אחיינית מרמה עשירית %(step)s %(inlaw)s",
    "אחיינית מרמה אחת עשרה %(step)s %(inlaw)s",
]

_CHILDREN_LEVEL = [
    "",
    "ילדים",
    "נכדים",
    "נינים",
    "חימשים",
    "נכדים מרמה חמישית",
    "נכדים מרמה שישית",
    "נכדים מרמה שביעית",
    "נכדים מרמה שמינית",
    "נכדים מרמה תשיעית",
    "נכדים מרמה עשירית",
    "נכדים מרמה אחת עשרה",
]

_SIBLINGS_LEVEL = [
    "",
    "אחאים",
    "דוד/דודה",
    "דוד/דודה גדולים",
    "דוד/דודה מרמה שלישית",
    "דוד/דודה מרמה רביעית",
    "דוד/דודה מרמה חמישית",
    "דוד/דודה מרמה שישית",
    "דוד/דודה מרמה שביעית",
    "דוד/דודה מרמה שמינית",
    "דוד/דודה מרמה תשיעית",
    "דוד/דודה מרמה עשירית",
    "דוד/דודה מרמה אחת עשרה",
]

_SIBLING_LEVEL = [
    "",
    "אחאים %(step)s %(inlaw)s",
    "דוד/דודה %(step)s %(inlaw)s",
    "דוד/דודה גדולים %(step)s %(inlaw)s",
    "דוד/דודה מרמה שלישית %(step)s %(inlaw)s",
    "דוד/דודה מרמה רביעית %(step)s %(inlaw)s",
    "דוד/דודה מרמה חמישית %(step)s %(inlaw)s",
    "דוד/דודה מרמה שישית %(step)s %(inlaw)s",
    "דוד/דודה מרמה שביעית %(step)s %(inlaw)s",
    "דוד/דודה מרמה שמינית %(step)s %(inlaw)s",
    "דוד/דודה מרמה תשיעית %(step)s %(inlaw)s",
    "דוד/דודה מרמה עשירית %(step)s %(inlaw)s",
    "דוד/דודה מרמה אחת עשרה %(step)s %(inlaw)s",
]

_NEPHEWS_NIECES_LEVEL = [
    "",
    "אחאים",
    "אחיין/אחיינית",
    "נכדן/נכדנית",
    "אחיין/אחיינית גדולים",
    "אחיין/אחיינית שלישית",
    "אחיין/אחיינית רביעית",
    "אחיין/אחיינית חמישית",
    "אחיין/אחיינית מרמה שישית",
    "אחיין/אחיינית מרמה שביעית",
    "אחיין/אחיינית מרמה שמינית",
    "אחיין/אחיינית מרמה תשיעית",
    "אחיין/אחיינית מרמה עשירית",
    "אחיין/אחיינית מרמה אחת עשרה",
]


# -------------------------------------------------------------------------
#
# RelationshipCalculator
#
# -------------------------------------------------------------------------
class RelationshipCalculator(gramps.gen.relationship.RelationshipCalculator):
    """
    The relationship calculator helps to determine the relationship between
    two people.
    """

    # sibling strings  for Hebrew we need four "step": male sing/plur, female sing/plur
    STEP = "שלוב"
    STEP_F = "שלובה"
    STEP_M = "שלוב"  # this is actually redundant if Can't make it "plural form".
    HALF = "למחצה"
    INLAW = "מחיתון"

    def __init__(self):
        gramps.gen.relationship.RelationshipCalculator.__init__(self)

    DIST_FATHER = "אב־קדמון רחוק %(step)s %(inlaw)s (%(level)d דורות)"

    def _get_father(self, level, step="", inlaw=""):
        """
        Internal english method to create relation string
        """
        if level > len(_FATHER_LEVEL) - 1:
            return self.DIST_FATHER % {"step": step, "inlaw": inlaw, "level": level}
        else:
            return _FATHER_LEVEL[level] % {"step": step, "inlaw": inlaw}

    DIST_SON = "בן רחוק %(step) %(inlaw)s (%(level)d דורות)"

    def _get_son(self, level, step="", inlaw=""):
        """
        Internal english method to create relation string
        """
        if level > len(_SON_LEVEL) - 1:
            return self.DIST_SON % {"step": step, "inlaw": inlaw, "level": level}
        else:
            return _SON_LEVEL[level] % {"step": step, "inlaw": inlaw}

    DIST_MOTHER = "אם־קדמונית רחוקה %(step)s %(inlaw) s(%(level)d דורות)"

    def _get_mother(self, level, step="", inlaw=""):
        """
        Internal english method to create relation string
        """
        if level > len(_MOTHER_LEVEL) - 1:
            return self.DIST_MOTHER % {"step": step, "inlaw": inlaw, "level": level}
        else:
            return _MOTHER_LEVEL[level] % {"step": step, "inlaw": inlaw}

    DIST_DAUGHTER = "בת רחוקה %(step) %(inlaw)s(%(level)d דורות)"

    def _get_daughter(self, level, step="", inlaw=""):
        """
        Internal english method to create relation string
        """
        if level > len(_DAUGHTER_LEVEL) - 1:
            return self.DIST_DAUGHTER % {"step": step, "inlaw": inlaw, "level": level}
        else:
            return _DAUGHTER_LEVEL[level] % {"step": step, "inlaw": inlaw}

    def _get_parent_unknown(self, level, step="", inlaw=""):
        """
        Internal english method to create relation string
        """
        if level < len(_LEVEL_NAME):
            return (
                "אב־קדמון %(step)s %(inlaw)s" % {"step": step, "inlaw": inlaw}
                + _LEVEL_NAME[level]
            )
        else:
            return "אב־קדמון רחוק %s %s (%d דורות)" % (step, inlaw, level)

    DIST_CHILD = "צאצא רחוק %(step)s (%(level)d דורות)"

    def _get_child_unknown(self, level, step="", inlaw=""):
        """
        Internal english method to create relation string
        """
        if level < len(_LEVEL_NAME):
            return (
                "צאצא %(step)s %(inlaw)s" % {"step": step, "inlaw": inlaw}
                + _LEVEL_NAME[level]
            )
        else:
            return self.DIST_CHILD % {"step": step, "level": level}

    DIST_AUNT = "דודה רחוקה %(step)s %(inlaw)s"

    def _get_aunt(self, level, step="", inlaw=""):
        """
        Internal english method to create relation string
        """
        if level > len(_SISTER_LEVEL) - 1:
            return self.DIST_AUNT % {"step": step, "inlaw": inlaw}
        else:
            return _SISTER_LEVEL[level] % {"step": step, "inlaw": inlaw}

    DIST_UNCLE = "דוד רחוק %(step)s %(inlaw)s"

    def _get_uncle(self, level, step="", inlaw=""):
        """
        Internal english method to create relation string
        """
        if level > len(_BROTHER_LEVEL) - 1:
            return self.DIST_UNCLE % {"step": step, "inlaw": inlaw}
        else:
            return _BROTHER_LEVEL[level] % {"step": step, "inlaw": inlaw}

    DIST_NEPHEW = "אחיין רחוק %(step)s %(inlaw)s"

    def _get_nephew(self, level, step="", inlaw=""):
        """
        Internal english method to create relation string
        """
        if level > len(_NEPHEW_LEVEL) - 1:
            return self.DIST_NEPHEW % {"step": step, "inlaw": inlaw}
        else:
            return _NEPHEW_LEVEL[level] % {"step": step, "inlaw": inlaw}

    DIST_NIECE = "אחיינית רחוקה %(step)s %(inlaw)s"

    def _get_niece(self, level, step="", inlaw=""):
        """
        Internal english method to create relation string
        """
        if level > len(_NIECE_LEVEL) - 1:
            return self.DIST_NIECE % {"step": step, "inlaw": inlaw}
        else:
            return _NIECE_LEVEL[level] % {"step": step, "inlaw": inlaw}

    def _get_cousin(self, level, removed, dir="", step="", inlaw=""):
        """
        Internal english method to create relation string
        """
        if removed == 0 and level < len(_LEVEL_NAME):
            return "בן־דוד %s %s %s" % (step, inlaw, _LEVEL_NAME[level])
        elif removed > len(_REMOVED_LEVEL) - 1 or level > len(_LEVEL_NAME) - 1:
            return "קרוב־משפחה רחוק %s %s" % (step, inlaw)
        else:
            return "בן־דוד/בת־דודה %s %s %s %s %s" % (
                step,
                inlaw,
                _LEVEL_NAME[level],
                _REMOVED_LEVEL[removed],
                dir,
            )

    DIST_SIB = "דוד/דודה רחוקים %(step)s %(inlaw)s"

    def _get_sibling(self, level, step="", inlaw=""):
        """
        Internal english method to create relation string
        """
        if level < len(_SIBLING_LEVEL):
            return _SIBLING_LEVEL[level] % {"step": step, "inlaw": inlaw}
        else:
            return self.DIST_SIB % {"step": step, "inlaw": inlaw}

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
        rel_str = "קרובי־משפחה רחוקים"
        if Ga == 0:
            # These are descendants
            if Gb < len(_CHILDREN_LEVEL):
                rel_str = _CHILDREN_LEVEL[Gb]
            else:
                rel_str = "צאצאים רחוקים"
        elif Gb == 0:
            # These are parents/grand parents
            if Ga < len(_PARENTS_LEVEL):
                rel_str = _PARENTS_LEVEL[Ga]
            else:
                rel_str = "אבות־קדמונים רחוקים"
        elif Gb == 1:
            # These are siblings/aunts/uncles
            if Ga < len(_SIBLINGS_LEVEL):
                rel_str = _SIBLINGS_LEVEL[Ga]
            else:
                rel_str = "דודים/דודות רחוקים"
        elif Ga == 1:
            # These are nieces/nephews
            if Gb < len(_NEPHEWS_NIECES_LEVEL):
                rel_str = _NEPHEWS_NIECES_LEVEL[Gb]
            else:
                rel_str = "אחיינים/אחייניות רחוקים"
        elif Ga > 1 and Ga == Gb:
            # These are cousins in the same generation
            if Ga <= len(_LEVEL_NAME):
                rel_str = "בני דודים %s  " % _LEVEL_NAME[Ga - 1]
            else:
                rel_str = "בני דודים רחוקים"
        elif Ga > 1 and Ga > Gb:
            # These are cousins in different generations with the second person
            # being in a higher generation from the common ancestor than the
            # first person.
            if Gb <= len(_LEVEL_NAME) and (Ga - Gb) < len(_REMOVED_LEVEL):
                rel_str = " %s %s (עולה)" % (
                    _LEVEL_NAME[Gb - 1],
                    _REMOVED_LEVEL[Ga - Gb],
                )
            else:
                rel_str = "בני דודים רחוקים"
        elif Gb > 1 and Gb > Ga:
            # These are cousins in different generations with the second person
            # being in a lower generation from the common ancestor than the
            # first person.
            if Ga <= len(_LEVEL_NAME) and (Gb - Ga) < len(_REMOVED_LEVEL):
                rel_str = " בני דודים%s %s (יורד)" % (
                    _LEVEL_NAME[Ga - 1],
                    _REMOVED_LEVEL[Gb - Ga],
                )
            else:
                rel_str = "בני דודים רחוקים"

        if in_law_b is True:
            rel_str = "זוג של %s" % rel_str

        return rel_str.strip()

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

        To be used as: 'person b is the grandparent of a', this will be in
        translation string:  'person b is the %(relation)s of a'

        Note that languages with gender should add 'the' inside the
        translation, so eg in french:  'person b est %(relation)s de a'
        where relation will be here: le grandparent

        Ga and Gb can be used to mathematically calculate the relationship.

        .. seealso::
            http://en.wikipedia.org/wiki/Cousin#Mathematical_definitions

        Some languages need to know the specific path to the common ancestor.
        Those languages should use reltocommon_a and reltocommon_b which is
        a string like 'mfmf'.

        The possible string codes are:

        =======================  ===========================================
        Code                     Description
        =======================  ===========================================
        REL_MOTHER               # going up to mother
        REL_FATHER               # going up to father
        REL_MOTHER_NOTBIRTH      # going up to mother, not birth relation
        REL_FATHER_NOTBIRTH      # going up to father, not birth relation
        REL_FAM_BIRTH            # going up to family (mother and father)
        REL_FAM_NONBIRTH         # going up to family, not birth relation
        REL_FAM_BIRTH_MOTH_ONLY  # going up to fam, only birth rel to mother
        REL_FAM_BIRTH_FATH_ONLY  # going up to fam, only birth rel to father
        =======================  ===========================================

        Prefix codes are stripped, so REL_FAM_INLAW_PREFIX is not present.
        If the relation starts with the inlaw of the person a, then 'in_law_a'
        is True, if it starts with the inlaw of person b, then 'in_law_b' is
        True.

        Also REL_SIBLING (# going sideways to sibling (no parents)) is not
        passed to this routine. The collapse_relations changes this to a
        family relation.

        Hence, calling routines should always strip REL_SIBLING and
        REL_FAM_INLAW_PREFIX before calling get_single_relationship_string()
        Note that only_birth=False, means that in the reltocommon one of the
        NOTBIRTH specifiers is present.

        The REL_FAM identifiers mean that the relation is not via a common
        ancestor, but via a common family (note that that is not possible for
        direct descendants or direct ancestors!). If the relation to one of the
        parents in that common family is by birth, then 'only_birth' is not
        set to False. The only_birth() method is normally used for this.

        :param Ga: The number of generations between the main person and the
                   common ancestor.
        :type Ga: int
        :param Gb: The number of generations between the other person and the
                   common ancestor.
        :type Gb: int
        :param gender_a: gender of person a
        :type gender_a: int gender
        :param gender_b: gender of person b
        :type gender_b: int gender
        :param reltocommon_a: relation path to common ancestor or common
                              Family for person a.
                              Note that length = Ga
        :type reltocommon_a: str
        :param reltocommon_b: relation path to common ancestor or common
                              Family for person b.
                              Note that length = Gb
        :type reltocommon_b: str
        :param in_law_a:  True if path to common ancestors is via the partner
                          of person a
        :type in_law_a: bool
        :param in_law_b: True if path to common ancestors is via the partner
                         of person b
        :type in_law_b: bool
        :param only_birth: True if relation between a and b is by birth only
                           False otherwise
        :type only_birth: bool
        :returns: A string describing the relationship between the two people
        :rtype: str

        .. note:: 1. the self.REL_SIBLING should not be passed to this routine,
                     so we should not check on it. All other self.
                  2. for better determination of siblings, use if Ga=1=Gb
                     get_sibling_relationship_string
        """
        if only_birth:
            step = ""
        else:
            if gender_b == MALE:
                step = self.STEP
            elif gender_b == FEMALE:
                step = self.STEP_F
            else:
                step = (
                    self.STEP
                )  # Change this as appropriate for other and unknown gender

        if in_law_a or in_law_b:
            inlaw = self.INLAW
        else:
            inlaw = ""

        rel_str = "קרוב־משפחה רחוק %s%s" % (step, inlaw)

        if Ga == 0:
            # b is descendant of a
            if Gb == 0:
                rel_str = "האדם"
            elif gender_b == MALE:
                rel_str = self._get_son(Gb, step, inlaw)
            elif gender_b == FEMALE:
                rel_str = self._get_daughter(Gb, step, inlaw)
            else:
                rel_str = self._get_child_unknown(Gb, step, inlaw)
        elif Gb == 0:
            # b is parents/grand parent of a
            if gender_b == MALE:
                rel_str = self._get_father(Ga, step, inlaw)
            elif gender_b == FEMALE:
                rel_str = self._get_mother(Ga, step, inlaw)
            else:
                rel_str = self._get_parent_unknown(Ga, step, inlaw)
        elif Gb == 1:
            # b is sibling/aunt/uncle of a
            if gender_b == MALE:
                rel_str = self._get_uncle(Ga, step, inlaw)
            elif gender_b == FEMALE:
                rel_str = self._get_aunt(Ga, step, inlaw)
            else:
                rel_str = self._get_sibling(Ga, step, inlaw)
        elif Ga == 1:
            # b is niece/nephew of a
            if gender_b == MALE:
                rel_str = self._get_nephew(Gb - 1, step, inlaw)
            elif gender_b == FEMALE:
                rel_str = self._get_niece(Gb - 1, step, inlaw)
            elif Gb < len(_NIECE_LEVEL) and Gb < len(_NEPHEW_LEVEL):
                rel_str = "%sאו %s" % (
                    self._get_nephew(Gb - 1, step, inlaw),
                    self._get_niece(Gb - 1, step, inlaw),
                )
            else:
                rel_str = "אחיין/אחיינית רחוקים %s %s" % (step, inlaw)
        elif Ga == Gb:
            # a and b cousins in the same generation
            rel_str = self._get_cousin(Ga - 1, 0, dir="", step=step, inlaw=inlaw)
        elif Ga > Gb:
            # These are cousins in different generations with the second person
            # being in a higher generation from the common ancestor than the
            # first person.
            rel_str = self._get_cousin(
                Gb - 1, Ga - Gb, dir=" (עולה)", step=step, inlaw=inlaw
            )
        elif Gb > Ga:
            # These are cousins in different generations with the second person
            # being in a lower generation from the common ancestor than the
            # first person.
            rel_str = self._get_cousin(
                Ga - 1, Gb - Ga, dir=" (יורד)", step=step, inlaw=inlaw
            )
        return rel_str.strip()

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
        elif sib_type == self.HALF_SIB_MOTHER or sib_type == self.HALF_SIB_FATHER:
            typestr = self.HALF
        elif sib_type == self.STEP_SIB:
            typestr = self.STEP

        if in_law_a or in_law_b:
            inlaw = self.INLAW
        else:
            inlaw = ""

        if gender_b == MALE:
            rel_str = self._get_uncle(1, typestr, inlaw)
        elif gender_b == FEMALE:
            rel_str = self._get_aunt(1, typestr, inlaw)
        else:
            rel_str = self._get_sibling(1, typestr, inlaw)
        return rel_str.strip()

    def get_partner_relationship_string(self, spouse_type, gender_a, gender_b):
        """
        Determine the string giving the relation between two partners of
        type spouse_type.
        Eg: b is the spouse of a
        Here 'spouse' is the string we need to determine

        .. warning:: DON'T TRANSLATE THIS PROCEDURE IF LOGIC IS EQUAL IN YOUR
                     LANGUAGE, AS GETTEXT IS ALREADY USED !
        """
        # english only needs gender of b, we don't guess if unknown like in old
        # procedure as that is stupid in present day cases!
        gender = gender_b

        if not spouse_type:
            return ""

        if spouse_type == self.PARTNER_MARRIED:
            if gender == MALE:
                return "בעל"
            elif gender == FEMALE:
                return "רעיה"
            else:
                return "זוג"
        elif spouse_type == self.PARTNER_EX_MARRIED:
            if gender == MALE:
                return "בעל לשעבר"
            elif gender == FEMALE:
                return "רעיה לשעבר"
            else:
                return "זוג לשעבר"
        elif spouse_type == self.PARTNER_UNMARRIED:
            if gender == MALE:
                return "שותף"
            elif gender == FEMALE:
                return "שותפה"
            else:
                return "שותף"
        elif spouse_type == self.PARTNER_EX_UNMARRIED:
            if gender == MALE:
                return "שותף לשעבר"
            elif gender == FEMALE:
                return "שותפה לשעבר"
            else:
                return "שותף לשעבר"
        elif spouse_type == self.PARTNER_CIVIL_UNION:
            if gender == MALE:
                return "שותף"
            elif gender == FEMALE:
                return "שותפה"
            else:
                return "שותף"
        elif spouse_type == self.PARTNER_EX_CIVIL_UNION:
            if gender == MALE:
                return "שותף קודם"
            elif gender == FEMALE:
                return "שותפה קודמת"
            else:
                return "שותף קודם"
        elif spouse_type == self.PARTNER_UNKNOWN_REL:
            if gender == MALE:
                return "שותף"
            elif gender == FEMALE:
                return "שותפה"
            else:
                return "שותף"
        else:
            # here we have spouse_type == self.PARTNER_EX_UNKNOWN_REL
            #   or other not catched types
            if gender == MALE:
                return "שותף קודם"
            elif gender == FEMALE:
                return "שותפה קודמת"
            else:
                return "שותף קודם"


if __name__ == "__main__":
    """
    TRANSLATORS, copy this if statement at the bottom of your
    rel_xx.py module, after adding: 'from Relationship import test'
    and test your work with:
    export PYTHONPATH=/path/to/gramps
    python gramps/plugins/rel/rel_xx.py

    See eg rel_fr.py at the bottom
    """
    from gramps.gen.relationship import test

    REL_CALC = RelationshipCalculator()
    test(REL_CALC, True)

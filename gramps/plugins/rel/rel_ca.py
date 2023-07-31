# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2007  Donald N. Allingham
# Copyright (C) 2008-2010  Brian G. Matherly
# Copyright (C) 2007-2010  Jerome Rapinat
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
# -------------------------------------------------------------------------
"""
Catalan-specific classes for relationships.
By Joan Creus
Based on rel_fr.py
Relationship names taken from:
http://www.scgenealogia.org/pdf/Denominacions%20dels%20Parentius.pdf
The only invented name is "cosinastre". Also, "besnetastre" and the like are
not explicitly in the dictionary, but "netastre" is.
"""

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------

from gramps.gen.lib import Person
import gramps.gen.relationship

# -------------------------------------------------------------------------

# level is used for generation level:
# at %th generation

_LEVEL_NAME = [
    "",
    "primer",
    "segon",
    "tercer",
    "quart",
    "cinquè",
    "sisè",
    "setè",
    "vuitè",
    "novè",
    "desè",
    "onzè",
    "dotzè",
    "tretzè",
    "catorzè",
    "quinzè",
    "setzè",
    "dissetè",
    "divuitè",
    "dinovè",
    "vintè",
    "vint-i-unè",
    "vint-i-dosè",
    "vint-i-tresè",
    "vint-i-quatrè",
    "vint-i-cinquè",
    "vint-i-sisè",
    "vint-i-setè",
    "vint-i-vuitè",
    "vint-i-novè",
    "trentè",
]

_LEVEL_NAME_F = [
    "",
    "primera",
    "segona",
    "tercera",
    "quarta",
    "cinquena",
    "sisena",
    "setena",
    "vuitena",
    "novena",
    "desena",
    "onzena",
    "dotzena",
    "tretzena",
    "catorzena",
    "quinzena",
    "setzena",
    "dissetena",
    "divuitena",
    "dinovena",
    "vintena",
    "vint-i-unena",
    "vint-i-dosena",
    "vint-i-tresena",
    "vint-i-quatrena",
    "vint-i-cinquena",
    "vint-i-sisena",
    "vint-i-setena",
    "vint-i-vuitena",
    "vint-i-novena",
    "trentena",
]

_LEVEL_NAME_P = [
    "",
    "",  # si són els primers no es posa mai
    "segons",
    "tercers",
    "quarts",
    "cinquens",
    "sisens",
    "setens",
    "vuitens",
    "novens",
    "desens",
    "onzens",
    "dotzens",
    "tretzens",
    "catorzens",
    "quinzens",
    "setzens",
    "dissetens",
    "divuitens",
    "dinovens",
    "vintens",
    "vint-i-unens",
    "vint-i-dosens",
    "vint-i-tresens",
    "vint-i-quatrens",
    "vint-i-cinquens",
    "vint-i-sisens",
    "vint-i-setens",
    "vint-i-vuitens",
    "vint-i-novens",
    "trentens",
]

# small lists, use generation level if > [5]
# the %s is for the inlaw string

_FATHER_LEVEL = [
    "",
    "el pare%s",
    "l'avi%s",
    "el besavi%s",
    "el rebesavi%s",
    "el quadravi%s",
]

_MOTHER_LEVEL = [
    "",
    "la mare%s",
    "l'àvia%s",
    "la besàvia%s",
    "la rebesàvia%s",
    "la quadràvia%s",
]

_MOTHER_LEVEL_STP = [
    "",
    "la madrastra%s",
    "l'aviastra%s",
    "la besaviastra%s",
    "la rebesaviastra%s",
    "la quadraviastra%s",
]

_FATHER_LEVEL_UNK = [
    "",
    "un dels pares%s",
    "un dels avis%s",
    "un dels besavis%s",
    "un dels rebesavis%s",
    "un dels quadravis%s",
]

_FATHER_LEVEL_STP = [
    "",
    "el padrastre%s",
    "l'aviastre%s",
    "el besaviastre%s",
    "el rebesaviastre%s",
    "el quadraviastre%s",
]

_FATHER_LEVEL_STPUNK = [
    "",
    "un dels padrastres%s",
    "un dels aviastres%s",
    "un dels besaviastres%s",
    "un dels rebesaviastres%s",
    "un dels quadraviastres%s",
]

_SON_LEVEL = [
    "",
    "el fill%s",
    "el nét%s",
    "el besnét%s",
    "el rebesnét%s",
    "el quadrinét%s",
]

_DAUGHTER_LEVEL = [
    "",
    "la filla%s",
    "la néta%s",
    "la besnéta%s",
    "la rebesnéta%s",
    "la quadrinéta%s",
]

_SON_LEVEL_UNK = [
    "",
    "un dels fills%s",
    "un dels néts%s",
    "un dels besnéts%s",
    "un dels rebesnéts%s",
    "un dels quadrinéts%s",
]

_SON_LEVEL_STP = [
    "",
    "el fillastre%s",
    "el netastre%s",
    "el besnetastre%s",
    "el rebesnetastre%s",
    "el quadrinetastre%s",
]

_SON_LEVEL_STPUNK = [
    "",
    "un dels fillastres%s",
    "un dels netastres%s",
    "un dels besnetastres%s",
    "un dels rebesnetastres%s",
    "un dels quadrinetastres%s",
]

_DAUGHTER_LEVEL_STP = [
    "",
    "la fillastra%s",
    "la netastra%s",
    "la besnetastra%s",
    "la rebesnetastra%s",
    "la quadrinetastra%s",
]

_BROTHER_LEVEL = [
    "",
    "el germà%s",
    "l'oncle%s",
    "el besoncle%s",
    "el rebesoncle%s",
    "el quadrioncle%s",
]

_SISTER_LEVEL = [
    "",
    "la germana%s",
    "la tia%s",
    "la bestia%s",
    "la rebestia%s",
    "la quadritia%s",
]

_BROTHER_LEVEL_UNK = [
    "",
    "un dels germans%s",
    "un dels oncles%s",
    "un dels besoncles%s",
    "un dels rebesoncles%s",
    "un dels quadrioncles%s",
]

_BROTHER_LEVEL_STP = [
    "",
    "el germanastre%s",
    "l'onclastre%s",
    "el besonclastre%s",
    "el rebesonclastre%s",
    "el quadrionclastre%s",
]

_BROTHER_LEVEL_STPUNK = [
    "",
    "un dels germanastres%s",
    "un dels onclastres%s",
    "un dels besonclastres%s",
    "un dels rebesonclastres%s",
    "un dels quadrionclastres%s",
]

_SISTER_LEVEL_STP = [
    "",
    "la germanastra%s",
    "la tiastra%s",
    "la bestiastra%s",
    "la rebestiastra%s",
    "la quadritiastra%s",
]

_NEPHEW_LEVEL = [
    "",
    "el nebot%s",
    "el besnebot%s",
    "el rebesnebot%s",
    "el quadrinebot%s",
]

_NIECE_LEVEL = [
    "",
    "la neboda%s",
    "la besneboda%s",
    "la rebesneboda%s",
    "la quadrineboda%s",
]

_NEPHEW_LEVEL_UNK = [
    "",
    "un dels nebots%s",
    "un dels besnebots%s",
    "un dels rebesnebots%s",
    "un dels quadrinebots%s",
]

_NEPHEW_LEVEL_STP = [
    "",
    "el nebodastre%s",
    "el besnebodastre%s",
    "el rebesnebodastre%s",
    "el quadrinebodastre%s",
]

_NEPHEW_LEVEL_STPUNK = [
    "",
    "un dels nebodastres%s",
    "un dels besnebodastres%s",
    "un dels rebesnebodastres%s",
    "un dels quadrinebodastres%s",
]

_NIECE_LEVEL_STP = [
    "",
    "la nebodastra%s",
    "la besnebodastra%s",
    "la rebesnebodastra%s",
    "la quadrinebodastra%s",
]

# kinship report

_PARENTS_LEVEL = [
    "",
    "Els pares",
    "Els avis",
    "Els besavis",
    "Els rebesavis",
    "Els quadravis",
]

_CHILDREN_LEVEL = [
    "",
    "Els fills",
    "Els néts",
    "Els besnéts",
    "Els rebesnéts",
    "Els quadrinéts",
]

_SIBLINGS_LEVEL = [
    "",
    "Els germans i les germanes",
    "Els oncles i les ties",
    "Els besoncles i les besties",
    "Els rebesoncles i les rebesties",
    "Els quadrioncles i les quadrities",
]

_NEPHEWS_NIECES_LEVEL = [
    "",
    "Els nebots i les nebodes",
    "Els besnebots i les besnebodes",
    "Els rebesnebots i les rebesnebodes",
    "Els quadrinebots i les quadrinebodes",
]

# -------------------------------------------------------------------------
#
#
#
# -------------------------------------------------------------------------

# from active person to common ancestor Ga=[level]


def _get_cosi(level, inlaw="", step=""):
    """
    cousins = same level, gender = male
    """
    if step == "":
        nom = "cosí"
    else:
        nom = "cosinastre"

    if level == 1:
        return "el %s germà%s" % (nom, inlaw)
    elif level < len(_LEVEL_NAME):
        return "el %s %s%s" % (nom, _LEVEL_NAME[level], inlaw)
    else:
        return "el %s %dè%s" % (nom, level, inlaw)


def _get_cosina(level, inlaw="", step=""):
    """
    cousins = same level, gender = female
    """
    if inlaw != "":  # polític -> política
        inlaw += "a"
    if step == "":
        nom = "cosina"
    else:
        nom = "cosinastra"

    if level == 1:
        return "la %s germana%s" % (nom, inlaw)
    elif level < len(_LEVEL_NAME):
        return "la %s %s%s" % (nom, _LEVEL_NAME_F[level], inlaw)
    else:
        return "la %s %dena%s" % (nom, level, inlaw)


def _get_cosi_unknown(level, inlaw="", step=""):
    """
    cousins = same level, gender = unknown
    """
    if inlaw != "":  # polític -> polítics
        inlaw += "s"
    if step == "":
        nom = "cosins"
    else:
        nom = "cosinastres"

    if level == 1:
        return "un dels %s germans%s" % (nom, inlaw)
    elif level < len(_LEVEL_NAME):
        return "un dels %s %s%s" % (nom, _LEVEL_NAME_P[level], inlaw)
    else:
        return "un dels %s %dens%s" % (nom, level, inlaw)


def _get_father(level, inlaw="", step=""):
    """
    ancestor, gender = male
    """
    if step == "":
        taula = _FATHER_LEVEL
        nom = "avi"
    else:
        taula = _FATHER_LEVEL_STP
        nom = "aviastre"

    if level < len(taula):
        return taula[level] % inlaw

    elif level <= len(_LEVEL_NAME):
        return "l'%s %s%s" % (nom, _LEVEL_NAME[level - 1], inlaw)
    else:
        # use numerical generation

        return "l'%s %dè%s" % (nom, (level - 1), inlaw)


def _get_mother(level, inlaw="", step=""):
    """
    ancestor, gender = female
    """
    if inlaw != "":
        inlaw += "a"
    if step == "":
        taula = _MOTHER_LEVEL
        nom = "àvia"
    else:
        taula = _MOTHER_LEVEL_STP
        nom = "aviastra"

    if level < len(taula):
        return taula[level] % inlaw

        # limitation gen = 30

    elif level <= len(_LEVEL_NAME_F):
        return "l'%s %s%s" % (nom, _LEVEL_NAME_F[level - 1], inlaw)
    else:
        # use numerical generation

        return "l'àvia %dena%s" % ((level - 1), inlaw)


def _get_parent_unknown(level, inlaw="", step=""):
    """
    unknown parent
    """
    if inlaw != "":
        inlaw += "s"

    if step == "":
        taula = _FATHER_LEVEL_UNK
        nom = "avis"
    else:
        taula = _FATHER_LEVEL_STPUNK
        nom = "aviastres"

    if level < len(taula):
        return taula[level] % inlaw

    elif level <= len(_LEVEL_NAME_P):
        return "un dels %s %s%s" % (nom, _LEVEL_NAME_P[level - 1], inlaw)
    else:
        # use numerical generation
        return "un dels %s %dens%s" % (nom, (level - 1), inlaw)


def _get_son(level, inlaw="", step=""):
    """
    descendant, gender = male
    """
    if step == "":
        taula = _SON_LEVEL
        nom = "nét"
    else:
        taula = _SON_LEVEL_STP
        nom = "netastre"

    if level < len(taula):
        return taula[level] % inlaw

    elif level <= len(_LEVEL_NAME):
        return "el %s %s%s" % (nom, _LEVEL_NAME[level - 1], inlaw)
    else:
        # use numerical generation

        return "el %s %dè%s" % (nom, (level - 1), inlaw)


def _get_sons(level, inlaw=""):
    """
    descendants for kinship report
    """
    if inlaw != "":  # polític -> polítics
        inlaw += "s"

    if inlaw != "" and level == 1:
        return "els gendres i les joves"
    elif level < len(_CHILDREN_LEVEL):
        return _CHILDREN_LEVEL[level] + inlaw
    elif level < len(_LEVEL_NAME_P) - 1:
        return "els néts" + _LEVEL_NAME_P[level - 1] + inlaw
    else:
        return "els néts %dens" % (level - 1) + inlaw


def _get_daughter(level, inlaw="", step=""):
    """
    descendant, gender = female
    """
    if step == "":
        taula = _DAUGHTER_LEVEL
        nom = "néta"
    else:
        taula = _DAUGHTER_LEVEL_STP
        nom = "netastra"

    if inlaw != "":
        inlaw += "a"
    if level < len(taula):
        return taula[level] % inlaw

    elif level <= len(_LEVEL_NAME_F):
        return "la %s %s%s" % (nom, _LEVEL_NAME_F[level - 1], inlaw)
    else:
        # use numerical generation

        return "la %s %dena%s" % (nom, (level - 1), inlaw)


def _get_child_unknown(level, inlaw="", step=""):
    """
    descendant, gender = unknown
    """
    if inlaw != "":
        inlaw += "s"
    if step == "":
        taula = _SON_LEVEL_UNK
        nom = "néts"
    else:
        taula = _SON_LEVEL_STPUNK
        nom = "netastres"

    if level < len(taula):
        return taula[level] % inlaw

    elif level <= len(_LEVEL_NAME_P):
        return "un dels %s %s%s" % (nom, _LEVEL_NAME_P[level - 1], inlaw)
    else:
        # use numerical generation

        return "un dels %s %dens%s" % (nom, (level - 1), inlaw)


def _get_sibling_unknown(level, inlaw="", step=""):
    """
    sibling of an ancestor, gender = unknown
    """
    if inlaw != "":
        inlaw += "s"
    if step == "":
        taula = _BROTHER_LEVEL_UNK
        nom = "oncles"
    else:
        taula = _BROTHER_LEVEL_STPUNK
        nom = "onclastres"

    if level < len(taula):
        return taula[level] % inlaw

    elif level <= len(_LEVEL_NAME_P):
        # limitation gen = 30

        return "un dels %s %s%s" % (nom, _LEVEL_NAME_P[level - 1], inlaw)
    else:
        # use numerical generation

        return "un dels %s %dens%s" % (nom, (level - 1), inlaw)


def _get_uncle(level, inlaw="", step=""):
    """
    sibling of an ancestor, gender = male
    """
    if step == "":
        taula = _BROTHER_LEVEL
        nom = "oncle"
    else:
        taula = _BROTHER_LEVEL_STP
        nom = "onclastre"

    if level < len(taula):
        return taula[level] % inlaw

    elif level <= len(_LEVEL_NAME):
        # limitation gen = 30

        return "l'%s %s%s" % (nom, _LEVEL_NAME[level - 1], inlaw)
    else:
        # use numerical generation

        return "l'%s %dè%s" % (nom, (level - 1), inlaw)


def _get_aunt(level, inlaw="", step=""):
    """
    sibling of an ancestor, gender = female
    """
    if step == "":
        taula = _SISTER_LEVEL
        nom = "tia"
    else:
        taula = _SISTER_LEVEL_STP
        nom = "tiastra"

    if inlaw != "":
        inlaw += "a"
    if level < len(taula):
        return taula[level] % inlaw

    elif level <= len(_LEVEL_NAME_F):
        return "la %s %s%s" % (nom, _LEVEL_NAME_F[level - 1], inlaw)
    else:
        # use numerical generation

        return "la %s %dena%s" % (nom, (level - 1), inlaw)


def _get_uncles(level, inlaw=""):
    """
    siblings for kinship report
    """
    if inlaw != "":
        inlaw += "s"

    if inlaw != "" and level == 1:
        return "els cunyats i les cunyades"
    elif level < len(_SIBLINGS_LEVEL):
        return "%s%s" % (_SIBLINGS_LEVEL[level], inlaw)
    elif level <= len(_LEVEL_NAME_P):
        return "els oncles i les ties %s%s" % (_LEVEL_NAME_P[level - 1], inlaw)
    else:
        # use numerical generation
        return "els oncles i les ties %dens%s" % ((level - 1), inlaw)


def _get_cosins(level, inlaw=""):
    """
    same generation level for kinship report
    """
    if inlaw != "":
        inlaw += "s"

    if level == 2:
        rel_str = "els cosins germans" + inlaw
    elif level <= len(_LEVEL_NAME_P):
        rel_str = "els cosins %s%s" % (_LEVEL_NAME_P[level - 1], inlaw)
    else:
        # security
        rel_str = "els cosins %dens%s" % ((level - 1), inlaw)

    return rel_str


def _get_nephew(level, inlaw="", step=""):
    """
    cousin of a descendant, gender = male
    """
    if step == "":
        taula = _NEPHEW_LEVEL
        nom = "nebot"
    else:
        taula = _NEPHEW_LEVEL_STP
        nom = "nebodastre"

    if level < len(taula):
        return taula[level] % inlaw

    elif level < len(_LEVEL_NAME):
        return "el %s %s%s" % (nom, _LEVEL_NAME[level], inlaw)
    else:
        # use numerical generation

        return "el %s %dè%s" % (nom, level, inlaw)


def _get_nephew_unk(level, inlaw="", step=""):
    """
    cousin of a descendant, gender = unknown
    """
    if inlaw != "":
        inlaw += "s"
    if step == "":
        taula = _NEPHEW_LEVEL_UNK
        nom = "nebots"
    else:
        taula = _NEPHEW_LEVEL_STPUNK
        nom = "nebodastres"

    if level < len(taula):
        return taula[level] % inlaw

    elif level < len(_LEVEL_NAME):
        return "un dels %s %s%s" % (nom, _LEVEL_NAME_P[level], inlaw)
    else:
        # use numerical generation

        return "un dels %s %dens%s" % (nom, level, inlaw)


def _get_niece(level, inlaw="", step=""):
    """
    cousin of a descendant, gender = female
    """
    if inlaw != "":
        inlaw += "a"
    if step == "":
        taula = _NIECE_LEVEL
        nom = "neboda"
    else:
        taula = _NIECE_LEVEL_STP
        nom = "nebodastra"

    if level < len(taula):
        return taula[level] % inlaw

    elif level < len(_LEVEL_NAME_F):
        return "la %s %s%s" % (nom, _LEVEL_NAME_F[level], inlaw)
    else:
        # use numerical generation

        return "la %s %dena%s" % (nom, level, inlaw)


def _get_nephews(level, inlaw=""):
    """
    cousin of a descendant, gender = male
    """
    if inlaw != "":
        inlaw += "s"
    if level <= len(_NEPHEWS_NIECES_LEVEL):
        # limitation gen = 30

        return "%s%s" % (_NEPHEWS_NIECES_LEVEL[level - 1], inlaw)
    elif level <= len(_LEVEL_NAME_P):
        return "els nebots i les nebodes %s%s" % (_LEVEL_NAME_P[level - 1], inlaw)
    else:
        # use numerical generation

        return "els nebots i les nebodes %dens%s" % ((level - 1), inlaw)


def _get_oncle_valencia(levela, levelb, inlaw="", step=""):
    """
    removed cousins, older generations
    """
    if levela <= levelb:
        return "error a _get_oncle_valencia"
    val_level = levela - levelb
    amplada = levelb - 1
    retorn = _get_uncle(val_level + 1, "", step)
    if amplada == 1:
        stramplada = ""
    else:
        stramplada = _LEVEL_NAME[amplada]
    return retorn + " valencià " + stramplada + inlaw


def _get_oncles_valencians(levela, levelb, inlaw=""):
    """
    removed cousins, older generations for kinship report
    """
    if inlaw != "":
        inlaw += "s"
    if levela <= levelb:
        return "error a _get_oncles_valencians"
    val_level = levela - levelb
    amplada = levelb - 1
    retorn = _get_uncles(val_level + 1, "")
    if amplada == 1:
        stramplada = ""
    else:
        stramplada = _LEVEL_NAME_P[amplada]
    return retorn + " valencians " + stramplada + inlaw


def _get_nebot_valencia(levela, levelb, inlaw="", step=""):
    """
    removed cousins, younger generations
    """
    if levelb <= levela:
        return "error a _get_nebot_valencia"
    val_level = levelb - levela
    amplada = levela - 1
    retorn = _get_nephew(val_level, "", step)
    if amplada == 1:
        stramplada = ""
    else:
        stramplada = _LEVEL_NAME[amplada]
    return retorn + " valencià " + stramplada + inlaw


def _get_nebots_valencians(levela, levelb, inlaw=""):
    """
    removed cousins, younger generations, for kinship report
    gender = male
    """
    if inlaw != "":
        inlaw += "s"
    if levelb <= levela:
        return "error a _get_nebots_valencians"
    val_level = levelb - levela
    amplada = levela - 1
    retorn = _get_nephews(val_level + 1, "")
    if amplada == 1:
        stramplada = ""
    else:
        stramplada = _LEVEL_NAME_P[amplada]
    return retorn + " valencians " + stramplada + inlaw


def _get_tia_valenciana(levela, levelb, inlaw="", step=""):
    """
    removed cousins, older generations
    gender = female
    """
    if inlaw != "":
        inlaw += "a"
    if levela <= levelb:
        return "error a _get_tia_valenciana"
    val_level = levela - levelb
    amplada = levelb - 1
    retorn = _get_aunt(val_level + 1, "", step)
    if amplada == 1:
        stramplada = ""
    else:
        stramplada = _LEVEL_NAME_F[amplada]
    return retorn + " valenciana " + stramplada + inlaw


def _get_neboda_valenciana(levela, levelb, inlaw="", step=""):
    """
    removed cousins, younger generations
    gender = female
    """
    if inlaw != "":
        inlaw += "a"
    if levelb <= levela:
        return "error a _get_neboda_valenciana"
    val_level = levelb - levela
    amplada = levela - 1
    retorn = _get_niece(val_level, "", step)
    if amplada == 1:
        stramplada = ""
    else:
        stramplada = _LEVEL_NAME_F[amplada]
    return retorn + " valenciana " + stramplada + inlaw


class RelationshipCalculator(gramps.gen.relationship.RelationshipCalculator):
    """
    RelationshipCalculator Class
    """

    INLAW = " polític"

    def __init__(self):
        gramps.gen.relationship.RelationshipCalculator.__init__(self)

    # kinship report

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
        see relationship.py
        """

        rel_str = "parents llunyans"
        # atgen = " de la %sena generació"
        # bygen = " per la %sena generació"
        # cmt = " (germans o germanes d'un avantpassat" + atgen % Ga + ")"

        if in_law_a or in_law_b:
            inlaw = self.INLAW
        else:
            inlaw = ""

        if Ga == 0:
            # These are descendants

            rel_str = _get_sons(Gb, inlaw)

        elif Gb == 0:
            # These are parents/grand parents

            if Ga < len(_PARENTS_LEVEL):
                rel_str = _PARENTS_LEVEL[Ga]
            elif Ga < len(_LEVEL_NAME_P) - 1:
                rel_str = "els avis " + _LEVEL_NAME_P[Ga - 1]
            else:
                rel_str = "els avis %dens" % (Ga - 1)

        elif Gb == 1:
            # These are siblings/aunts/uncles
            rel_str = _get_uncles(Ga, inlaw)

        elif Ga == 1:
            # These are nieces/nephews

            rel_str = _get_nephews(Gb, inlaw)

        elif Ga > 1:
            if Ga == Gb:
                # These are cousins in the same generation

                rel_str = _get_cosins(Ga, inlaw)
            elif Ga > Gb:
                # These are cousins in different generations with the second
                # person being in a higher generation from the common ancestor
                # than the first person.

                rel_str = _get_oncles_valencians(Ga, Gb, inlaw)

            elif Gb > Ga:
                # These are cousins in different generations with the second
                # person being in a higher generation from the common ancestor
                # than the first person.

                rel_str = _get_nebots_valencians(Ga, Gb, inlaw)

        else:
            rel_str = "Error in get_plural_relationship_string()"

        return rel_str

    # quick report (missing on RelCalc tool - Status Bar)

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
        see relationship.py
        """

        if only_birth:
            step = ""
        else:
            step = self.STEP

        if in_law_a or in_law_b:
            inlaw = self.INLAW
        else:
            inlaw = ""

        rel_str = "un parent llunyà%s" % inlaw
        # bygen = " per la %sena generació"
        if Ga == 0:
            # b is descendant of a

            if Gb == 0:
                rel_str = "la mateixa persona"
            elif gender_b == Person.MALE:
                # spouse of daughter

                if inlaw and Gb == 1 and not step:
                    rel_str = "el gendre"
                else:
                    rel_str = _get_son(Gb, inlaw, step)
            elif gender_b == Person.FEMALE:
                # spouse of son

                if inlaw and Gb == 1 and not step:
                    rel_str = "la jove"
                else:
                    rel_str = _get_daughter(Gb, inlaw, step)
            else:
                rel_str = _get_child_unknown(Gb, inlaw, step)
        elif Gb == 0:
            # b is parents/grand parent of a

            if gender_b == Person.MALE:
                # father of spouse (family of spouse)
                if Ga == 1 and inlaw and not step:
                    rel_str = "el sogre"

                else:
                    rel_str = _get_father(Ga, inlaw, step)
            elif gender_b == Person.FEMALE:
                # mother of spouse (family of spouse)
                if Ga == 1 and inlaw and not step:
                    rel_str = "la sogra"

                else:
                    rel_str = _get_mother(Ga, inlaw, step)
            else:
                rel_str = _get_parent_unknown(Ga, inlaw, step)
        elif Gb == 1:
            # b is sibling/aunt/uncle of a

            if inlaw and Ga == 1 and not step:
                if gender_b == Person.MALE:
                    rel_str = "el cunyat"
                elif gender_b == Person.FEMALE:
                    rel_str = "la cunyada"
                else:  # gender_b == Person.UNKNOWN:
                    rel_str = "un cunyat"

            elif gender_b == Person.MALE:
                rel_str = _get_uncle(Ga, inlaw, step)
            elif gender_b == Person.FEMALE:
                rel_str = _get_aunt(Ga, inlaw, step)
            else:
                rel_str = _get_sibling_unknown(Ga, inlaw, step)

        elif Ga == 1:
            # b is niece/nephew of a

            if gender_b == Person.MALE:
                rel_str = _get_nephew(Gb - 1, inlaw, step)
            elif gender_b == Person.FEMALE:
                rel_str = _get_niece(Gb - 1, inlaw, step)
            elif gender_b == Person.UNKNOWN:
                rel_str = _get_nephew_unk(Gb - 1, inlaw, step)
            else:
                # This should never get executed
                rel_str = "un nebot%s llunyà (%dena generació)" % (inlaw, Gb)
        elif Ga == Gb:
            # a and b cousins in the same generation

            if gender_b == Person.MALE:
                rel_str = _get_cosi(Ga - 1, inlaw, step)
            elif gender_b == Person.FEMALE:
                rel_str = _get_cosina(Ga - 1, inlaw, step)
            elif gender_b == Person.UNKNOWN:
                rel_str = _get_cosi_unknown(Ga - 1, inlaw, step)
            else:
                rel_str = "error in get_single_relationship_string()"
        elif Ga > 1 and Ga > Gb:
            # These are cousins in different generations with the second person
            # being in a higher generation from the common ancestor than the
            # first person.

            if gender_b == Person.MALE:
                rel_str = _get_oncle_valencia(Ga, Gb, inlaw, step)
            elif gender_b == Person.FEMALE:
                rel_str = _get_tia_valenciana(Ga, Gb, inlaw, step)
            else:
                rel_str = _get_oncle_valencia(Ga, Gb, inlaw, step)
        elif Gb > 1 and Gb > Ga:
            # These are cousins in different generations with the second person
            # being in a lower generation from the common ancestor than the
            # first person.
            if gender_b == Person.MALE:
                rel_str = _get_nebot_valencia(Ga, Gb, inlaw, step)
            elif gender_b == Person.FEMALE:
                rel_str = _get_neboda_valenciana(Ga, Gb, inlaw, step)
            else:
                rel_str = _get_nebot_valencia(Ga, Gb, inlaw, step)

        return rel_str

    # RelCalc tool - Status Bar

    def get_sibling_relationship_string(
        self, sib_type, gender_a, gender_b, in_law_a=False, in_law_b=False
    ):
        """
        voir relationship.py
        """

        if in_law_a or in_law_b:
            inlaw = self.INLAW
        else:
            inlaw = ""

        if sib_type == self.NORM_SIB:
            if not inlaw:
                if gender_b == Person.MALE:
                    rel_str = "el germà"
                elif gender_b == Person.FEMALE:
                    rel_str = "la germana"
                else:
                    rel_str = "el germà o germana"
            else:
                if gender_b == Person.MALE:
                    rel_str = "el cunyat"
                elif gender_b == Person.FEMALE:
                    rel_str = "la cunyada"
                else:
                    rel_str = "el cunyat o la cunyada"
        elif sib_type == self.UNKNOWN_SIB:
            if not inlaw:
                if gender_b == Person.MALE:
                    rel_str = "el germà"
                elif gender_b == Person.FEMALE:
                    rel_str = "la germana"
                else:
                    rel_str = "el germà o germana"
            else:
                if gender_b == Person.MALE:
                    rel_str = "el cunyat"
                elif gender_b == Person.FEMALE:
                    rel_str = "la cunyada"
                else:
                    rel_str = "el cunyat o la cunyada"
        elif (
            sib_type == self.HALF_SIB_MOTHER
            or sib_type == self.HALF_SIB_FATHER
            or sib_type == self.STEP_SIB
        ):
            if not inlaw:
                if gender_b == Person.MALE:
                    rel_str = "el germanastre"
                elif gender_b == Person.FEMALE:
                    rel_str = "la germanastra"
                else:
                    rel_str = "el germanastre o la germanastra"
            else:
                if gender_b == Person.MALE:
                    rel_str = "el cunyat"
                elif gender_b == Person.FEMALE:
                    rel_str = "la cunyada"
                else:
                    rel_str = "el cunyat o la cunyada"
        return rel_str


if __name__ == "__main__":
    # Test function. Call it as follows from the command line (so as to find
    #        imported modules):
    #    export PYTHONPATH=/path/to/gramps/src
    # python src/plugins/rel/rel_ca.py
    # (Above not needed here)

    # ""
    #   TRANSLATORS, copy this if statement at the bottom of your
    #   rel_xx.py module, and test your work with:
    #   python src/plugins/rel/rel_xx.py
    # ""
    from gramps.gen.relationship import test

    RC = RelationshipCalculator()
    test(RC, True)

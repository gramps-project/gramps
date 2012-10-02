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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# $Id$
#
#-------------------------------------------------------------------------
"""
Catalan-specific classes for relationships.
By Joan Creus
Based on rel_fr.py
Relationship names taken from:
http://www.scgenealogia.org/pdf/Denominacions%20dels%20Parentius.pdf
The only invented name is "cosinastre". Also, "besnetastre" and the like are
not explicitly in the dictionary, but "netastre" is.
"""
#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------

from gramps.gen.lib import Person
import gramps.gen.relationship

#-------------------------------------------------------------------------

# level is used for generation level:
# at %th generation

_LEVEL_NAME = [
    u"",
    u"primer",
    u"segon",
    u"tercer",
    u"quart",
    u"cinquè",
    u"sisè",
    U"setè",
    u"vuitè",
    u"novè",
    u"desè",
    u"onzè",
    u"dotzè",
    u"tretzè",
    u"catorzè",
    u"quinzè",
    u"setzè",
    u"dissetè",
    u"divuitè",
    u"dinovè",
    u"vintè",
    u"vint-i-unè",
    u"vint-i-dosè",
    u"vint-i-tresè",
    u"vint-i-quatrè",
    u"vint-i-cinquè",
    u"vint-i-sisè",
    u"vint-i-setè",
    u"vint-i-vuitè",
    u"vint-i-novè",
    u"trentè",
    ]

_LEVEL_NAME_F = [
    u"",
    u"primera",
    u"segona",
    u"tercera",
    u"quarta",
    u"cinquena",
    u"sisena",
    u"setena",
    u"vuitena",
    u"novena",
    u"desena",
    u"onzena",
    u"dotzena",
    u"tretzena",
    u"catorzena",
    u"quinzena",
    u"setzena",
    u"dissetena",
    u"divuitena",
    u"dinovena",
    u"vintena",
    u"vint-i-unena",
    u"vint-i-dosena",
    u"vint-i-tresena",
    u"vint-i-quatrena",
    u"vint-i-cinquena",
    u"vint-i-sisena",
    u"vint-i-setena",
    u"vint-i-vuitena",
    u"vint-i-novena",
    u"trentena",
    ]

_LEVEL_NAME_P = [
    u"",
    u"",        # si són els primers no es posa mai
    u"segons",
    u"tercers",
    u"quarts",
    u"cinquens",
    u"sisens",
    u"setens",
    u"vuitens",
    u"novens",
    u"desens",
    u"onzens",
    u"dotzens",
    u"tretzens",
    u"catorzens",
    u"quinzens",
    u"setzens",
    u"dissetens",
    u"divuitens",
    u"dinovens",
    u"vintens",
    u"vint-i-unens",
    u"vint-i-dosens",
    u"vint-i-tresens",
    u"vint-i-quatrens",
    u"vint-i-cinquens",
    u"vint-i-sisens",
    u"vint-i-setens",
    u"vint-i-vuitens",
    u"vint-i-novens",
    u"trentens",
    ]

# small lists, use generation level if > [5]
# the %s is for the inlaw string

_FATHER_LEVEL = [u"", u"el pare%s", u"l'avi%s",
                 u"el besavi%s", u"el rebesavi%s", u"el quadravi%s"]

_MOTHER_LEVEL = [u"", u"la mare%s", u"l'àvia%s",
                 u"la besàvia%s", u"la rebesàvia%s", u"la quadràvia%s"]

_MOTHER_LEVEL_STP = [u"", u"la madrastra%s", u"l'aviastra%s",
                 u"la besaviastra%s", u"la rebesaviastra%s",
                 u"la quadraviastra%s"]

_FATHER_LEVEL_UNK = [u"", u"un dels pares%s", u"un dels avis%s",
                     u"un dels besavis%s", u"un dels rebesavis%s",
                     u"un dels quadravis%s"]

_FATHER_LEVEL_STP = [u"", u"el padrastre%s", u"l'aviastre%s",
                     u"el besaviastre%s", u"el rebesaviastre%s",
                     u"el quadraviastre%s"]

_FATHER_LEVEL_STPUNK = [u"", u"un dels padrastres%s", u"un dels aviastres%s",
                        u"un dels besaviastres%s", u"un dels rebesaviastres%s",
                        u"un dels quadraviastres%s"]

_SON_LEVEL = [u"", u"el fill%s", u"el nét%s",
              u"el besnét%s", u"el rebesnét%s", u"el quadrinét%s"]

_DAUGHTER_LEVEL = [u"", u"la filla%s", u"la néta%s",
                   u"la besnéta%s", u"la rebesnéta%s", u"la quadrinéta%s"]

_SON_LEVEL_UNK = [u"", u"un dels fills%s", u"un dels néts%s",
                  u"un dels besnéts%s", u"un dels rebesnéts%s",
                  u"un dels quadrinéts%s"]

_SON_LEVEL_STP = [u"", u"el fillastre%s", u"el netastre%s",
                  u"el besnetastre%s", u"el rebesnetastre%s",
                  u"el quadrinetastre%s"]

_SON_LEVEL_STPUNK = [u"", u"un dels fillastres%s", u"un dels netastres%s",
                     u"un dels besnetastres%s", u"un dels rebesnetastres%s",
                     u"un dels quadrinetastres%s"]

_DAUGHTER_LEVEL_STP = [u"", u"la fillastra%s", u"la netastra%s",
                       u"la besnetastra%s", u"la rebesnetastra%s",
                       u"la quadrinetastra%s"]

_BROTHER_LEVEL = [u"", u"el germà%s", u"l'oncle%s", u"el besoncle%s",
                  u"el rebesoncle%s", u"el quadrioncle%s"]

_SISTER_LEVEL = [u"", u"la germana%s", u"la tia%s", u"la bestia%s",
                 u"la rebestia%s", u"la quadritia%s"]

_BROTHER_LEVEL_UNK = [u"", u"un dels germans%s", u"un dels oncles%s",
                      u"un dels besoncles%s", u"un dels rebesoncles%s",
                      u"un dels quadrioncles%s"]

_BROTHER_LEVEL_STP = [u"", u"el germanastre%s", u"l'onclastre%s",
                      u"el besonclastre%s", u"el rebesonclastre%s",
                      u"el quadrionclastre%s"]

_BROTHER_LEVEL_STPUNK = [u"", u"un dels germanastres%s",
                         u"un dels onclastres%s", u"un dels besonclastres%s",
                         u"un dels rebesonclastres%s",
                         u"un dels quadrionclastres%s"]

_SISTER_LEVEL_STP = [u"", u"la germanastra%s", u"la tiastra%s",
                     u"la bestiastra%s", u"la rebestiastra%s",
                     u"la quadritiastra%s"]

_NEPHEW_LEVEL = [u"", u"el nebot%s", u"el besnebot%s",
                 u"el rebesnebot%s", u"el quadrinebot%s"]

_NIECE_LEVEL = [u"", u"la neboda%s", u"la besneboda%s",
                u"la rebesneboda%s", u"la quadrineboda%s"]

_NEPHEW_LEVEL_UNK = [u"", u"un dels nebots%s", u"un dels besnebots%s",
                     u"un dels rebesnebots%s", u"un dels quadrinebots%s"]

_NEPHEW_LEVEL_STP = [u"", u"el nebodastre%s", u"el besnebodastre%s",
                     u"el rebesnebodastre%s", u"el quadrinebodastre%s"]

_NEPHEW_LEVEL_STPUNK = [u"", u"un dels nebodastres%s",
                        u"un dels besnebodastres%s",
                        u"un dels rebesnebodastres%s",
                        u"un dels quadrinebodastres%s"]

_NIECE_LEVEL_STP = [u"", u"la nebodastra%s", u"la besnebodastra%s",
                    u"la rebesnebodastra%s", u"la quadrinebodastra%s"]

# kinship report

_PARENTS_LEVEL = [u"", u"Els pares", u"Els avis",
                  u"Els besavis", u"Els rebesavis", u"Els quadravis"]

_CHILDREN_LEVEL = [u"", u"Els fills", u"Els néts",
                   u"Els besnéts",
                   u"Els rebesnéts", u"Els quadrinéts"]

_SIBLINGS_LEVEL = [u"", u"Els germans i les germanes",
                   u"Els oncles i les ties",
                   u"Els besoncles i les besties",
                   u"Els rebesoncles i les rebesties",
		   u"Els quadrioncles i les quadrities"]

_NEPHEWS_NIECES_LEVEL = [u"", u"Els nebots i les nebodes",
                         u"Els besnebots i les besnebodes",
                         u"Els rebesnebots i les rebesnebodes",
                         u"Els quadrinebots i les quadrinebodes"]

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------

# from active person to common ancestor Ga=[level]

def _get_cosi(level, inlaw="", step=""):
    """
    cousins = same level, gender = male
    """
    if step == "":
        nom = u"cosí"
    else:
        nom = u"cosinastre"

    if level == 1:
        return u"el %s germà%s" % (nom, inlaw)
    elif level < len(_LEVEL_NAME):
        return u"el %s %s%s" % (nom, _LEVEL_NAME[level], inlaw)
    else:
        return u"el %s %dè%s" % (nom, level, inlaw)

def _get_cosina(level, inlaw="", step=""):
    """
    cousins = same level, gender = female
    """
    if (inlaw != ""):		# polític -> política
        inlaw += "a"
    if step == "":
        nom = u"cosina"
    else:
        nom = u"cosinastra"

    if level == 1:
        return u"la %s germana%s" % (nom, inlaw)
    elif level < len(_LEVEL_NAME):
        return u"la %s %s%s" % (nom, _LEVEL_NAME_F[level], inlaw)
    else:
        return u"la %s %dena%s" % (nom, level, inlaw)

def _get_cosi_unknown(level, inlaw="", step=""):
    """
    cousins = same level, gender = unknown
    """
    if (inlaw != ""):		# polític -> polítics
        inlaw += "s"
    if step == "":
        nom = u"cosins"
    else:
        nom = u"cosinastres"

    if level == 1:
        return u"un dels %s germans%s" % (nom, inlaw)
    elif level < len(_LEVEL_NAME):
        return u"un dels %s %s%s" % (nom, _LEVEL_NAME_P[level], inlaw)
    else:
        return u"un dels %s %dens%s" % (nom, level, inlaw)

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

        return u"l'%s %s%s" % \
            (nom, _LEVEL_NAME[level-1], inlaw)
    else:

        # use numerical generation

        return u"l'%s %dè%s" % (nom, (level -1), inlaw)

def _get_mother(level, inlaw="", step=""):
    """
    ancestor, gender = female
    """
    if (inlaw != ""):
        inlaw += "a"
    if step == "":
        taula = _MOTHER_LEVEL
        nom = u"àvia"
    else:
        taula = _MOTHER_LEVEL_STP
        nom = u"aviastra"

    if level < len(taula) :
        return taula[level] % inlaw

        # limitation gen = 30

    elif level <= len(_LEVEL_NAME_F):

        return u"l'%s %s%s" % \
            (nom, _LEVEL_NAME_F[level-1], inlaw)
    else:

        # use numerical generation

        return u"l'àvia %dena%s" % ((level -1), inlaw)

def _get_parent_unknown(level, inlaw="", step=""):
    """
    unknown parent
    """
    if (inlaw != ""):
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

        return u"un dels %s %s%s" % \
            (nom, _LEVEL_NAME_P[level-1], inlaw)
    else:

        # use numerical generation
        return u"un dels %s %dens%s" % (nom, (level -1), inlaw)

def _get_son(level, inlaw="", step=""):
    """
    descendant, gender = male
    """
    if step == "":
        taula = _SON_LEVEL
        nom = u"nét"
    else:
        taula = _SON_LEVEL_STP
        nom = "netastre"

    if level < len(taula):
        return taula[level] % inlaw

    elif level <= len(_LEVEL_NAME):

        return u"el %s %s%s" % \
            (nom, _LEVEL_NAME[level-1], inlaw)
    else:

        # use numerical generation

        return u"el %s %dè%s" % (nom, (level -1), inlaw)

def _get_sons(level, inlaw=""):
    """
    descendants for kinship report
    """
    if (inlaw != ""):		# polític -> polítics
        inlaw += "s"

    if inlaw != "" and level == 1 :
        return u"els gendres i les joves"
    elif level < len(_CHILDREN_LEVEL):
        return _CHILDREN_LEVEL[level] + inlaw
    elif level < len(_LEVEL_NAME_P) - 1:
        return u"els néts" + _LEVEL_NAME_P[level - 1] + inlaw
    else:
        return u"els néts %dens" % (level - 1) + inlaw

def _get_daughter(level, inlaw="", step=""):
    """
    descendant, gender = female
    """
    if step == "":
        taula = _DAUGHTER_LEVEL
        nom = u"néta"
    else:
        taula = _DAUGHTER_LEVEL_STP
        nom = "netastra"

    if (inlaw != ""):
        inlaw += "a"
    if level < len(taula):
        return taula[level] % inlaw

    elif level <= len(_LEVEL_NAME_F):

        return u"la %s %s%s" % \
            (nom, _LEVEL_NAME_F[level-1], inlaw)
    else:

        # use numerical generation

        return u"la %s %dena%s" % (nom, (level -1), inlaw)

def _get_child_unknown(level, inlaw="", step=""):
    """
    descendant, gender = unknown
    """
    if (inlaw != ""):
        inlaw += "s"
    if step == "":
        taula = _SON_LEVEL_UNK
        nom = u"néts"
    else:
        taula = _SON_LEVEL_STPUNK
        nom = "netastres"

    if level < len(taula):
        return taula[level] % inlaw

    elif level <= len(_LEVEL_NAME_P):

        return u"un dels %s %s%s" % \
            (nom, _LEVEL_NAME_P[level-1], inlaw)
    else:

        # use numerical generation

        return u"un dels %s %dens%s" % (nom, (level -1), inlaw)

def _get_sibling_unknown(level, inlaw="", step=""):
    """
    sibling of an ancestor, gender = unknown
    """
    if (inlaw != ""):
        inlaw += "s"
    if step == "":
        taula = _BROTHER_LEVEL_UNK
        nom = "oncles"
    else:
        taula = _BROTHER_LEVEL_STPUNK
        nom = "onclastres"

    if level < len(taula):
        return (taula[level] % inlaw)

    elif level <= len(_LEVEL_NAME_P):

        # limitation gen = 30

        return u"un dels %s %s%s" % \
            (nom, _LEVEL_NAME_P[level-1], inlaw)
    else :

        # use numerical generation

        return u"un dels %s %dens%s" % \
            (nom, (level - 1), inlaw)

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
        return (taula[level] % inlaw)

    elif level <= len(_LEVEL_NAME):

        # limitation gen = 30

        return u"l'%s %s%s" % \
            (nom, _LEVEL_NAME[level-1], inlaw)
    else :

        # use numerical generation

        return u"l'%s %dè%s" % \
            (nom, (level - 1), inlaw)

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

    if (inlaw != ""):
        inlaw += "a"
    if level < len(taula):
        return (taula[level] % inlaw)

    elif level <= len(_LEVEL_NAME_F):

        return u"la %s %s%s" % \
            (nom, _LEVEL_NAME_F[level-1], inlaw)
    else :

        # use numerical generation

        return u"la %s %dena%s" % \
            (nom, (level - 1), inlaw)

def _get_uncles(level, inlaw=""):
    """
    siblings for kinship report
    """
    if (inlaw != ""):
        inlaw += "s"

    if inlaw != "" and level == 1 :
        return u"els cunyats i les cunyades"
    elif level < len(_SIBLINGS_LEVEL) :
        return u"%s%s" % \
            (_SIBLINGS_LEVEL[level], inlaw)
    elif level <= len(_LEVEL_NAME_P) :
        return u"els oncles i les ties %s%s" % \
            (_LEVEL_NAME_P[level-1], inlaw)
    else:
        # use numerical generation
        return u"els oncles i les ties %dens%s" % \
            ((level-1), inlaw)

def _get_cosins(level, inlaw=""):
    """
    same generation level for kinship report
    """
    if (inlaw != ""):
        inlaw += "s"

    if level == 2:
        rel_str = u"els cosins germans"+inlaw
    elif level <= len(_LEVEL_NAME_P):

        rel_str = u"els cosins %s%s" % (_LEVEL_NAME_P[level - 1], inlaw)
    else:
        # security
        rel_str = u"els cosins %dens%s" % ((level - 1), inlaw)

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
        return (taula[level] % inlaw)

    elif level < len(_LEVEL_NAME):

        return u"el %s %s%s" % \
            (nom, _LEVEL_NAME[level], inlaw)
    else :

        # use numerical generation

        return u"el %s %dè%s" % (nom, level, inlaw)

def _get_nephew_unk(level, inlaw="", step=""):
    """
    cousin of a descendant, gender = unknown
    """
    if (inlaw != ""):
        inlaw += "s"
    if step == "":
        taula = _NEPHEW_LEVEL_UNK
        nom = "nebots"
    else:
        taula = _NEPHEW_LEVEL_STPUNK
        nom = "nebodastres"

    if level < len(taula):
        return (taula[level] % inlaw)

    elif level < len(_LEVEL_NAME):

        return u"un dels %s %s%s" % \
            (nom, _LEVEL_NAME_P[level], inlaw)
    else :

        # use numerical generation

        return u"un dels %s %dens%s" % (nom, level, inlaw)

def _get_niece(level, inlaw="", step=""):
    """
    cousin of a descendant, gender = female
    """
    if (inlaw != ""):
        inlaw += "a"
    if step == "":
        taula = _NIECE_LEVEL
        nom = "neboda"
    else:
        taula = _NIECE_LEVEL_STP
        nom = "nebodastra"

    if level < len(taula):
        return (taula[level] % inlaw)

    elif level < len(_LEVEL_NAME_F):

        return u"la %s %s%s" % \
            (nom, _LEVEL_NAME_F[level], inlaw)
    else :

        # use numerical generation

        return u"la %s %dena%s" % (nom, level, inlaw)

def _get_nephews(level, inlaw=""):
    """
    cousin of a descendant, gender = male
    """
    if (inlaw != ""):
        inlaw += "s"
    if level <= len(_NEPHEWS_NIECES_LEVEL) :

        # limitation gen = 30

        return u"%s%s" % (_NEPHEWS_NIECES_LEVEL[level-1], inlaw)
    elif level <= len(_LEVEL_NAME_P) :

        return u"els nebots i les nebodes %s%s" % \
             (_LEVEL_NAME_P[level-1], inlaw)
    else:
        # use numerical generation

        return u"els nebots i les nebodes %dens%s" % \
             ((level-1), inlaw)

def _get_oncle_valencia(levela, levelb, inlaw="", step=""):
    """
    removed cousins, older generations
    """
    if levela <= levelb:
        return u"error a _get_oncle_valencia"
    val_level  = levela-levelb
    amplada    = levelb-1
    retorn     = _get_uncle(val_level+1, "", step)
    if amplada == 1:
        stramplada = ""
    else:
        stramplada = _LEVEL_NAME[amplada]
    return retorn+u" valencià "+ stramplada+inlaw

def _get_oncles_valencians(levela, levelb, inlaw=""):
    """
    removed cousins, older generations for kinship report
    """
    if (inlaw != ""):
        inlaw += "s"
    if levela <= levelb:
        return u"error a _get_oncles_valencians"
    val_level  = levela-levelb
    amplada    = levelb-1
    retorn     = _get_uncles(val_level+1, "")
    if amplada == 1:
        stramplada = ""
    else:
        stramplada = _LEVEL_NAME_P[amplada]
    return retorn+u" valencians "+ stramplada+inlaw

def _get_nebot_valencia(levela, levelb, inlaw="", step=""):
    """
    removed cousins, younger generations
    """
    if levelb <= levela:
        return u"error a _get_nebot_valencia"
    val_level  = levelb-levela
    amplada    = levela - 1
    retorn     = _get_nephew(val_level, "", step)
    if amplada == 1:
        stramplada = ""
    else:
        stramplada = _LEVEL_NAME[amplada]
    return retorn+u" valencià "+ stramplada+inlaw

def _get_nebots_valencians(levela, levelb, inlaw=""):
    """
    removed cousins, younger generations, for kinship report
    gender = male
    """
    if (inlaw != ""):
        inlaw += "s"
    if levelb <= levela:
        return u"error a _get_nebots_valencians"
    val_level  = levelb-levela
    amplada    = levela - 1
    retorn     = _get_nephews(val_level+1, "")
    if amplada == 1:
        stramplada = ""
    else:
        stramplada = _LEVEL_NAME_P[amplada]
    return retorn+u" valencians "+ stramplada+inlaw

def _get_tia_valenciana(levela, levelb, inlaw="", step=""):
    """
    removed cousins, older generations
    gender = female
    """
    if (inlaw != ""):
        inlaw += "a"
    if levela <= levelb:
        return u"error a _get_tia_valenciana"
    val_level  = levela-levelb
    amplada    = levelb-1
    retorn     = _get_aunt(val_level+1, "", step)
    if amplada == 1:
        stramplada = ""
    else:
        stramplada = _LEVEL_NAME_F[amplada]
    return retorn+u" valenciana "+ stramplada+inlaw

def _get_neboda_valenciana(levela, levelb, inlaw="", step=""):
    """
    removed cousins, younger generations
    gender = female
    """
    if (inlaw != ""):
        inlaw += "a"
    if levelb <= levela:
        return u"error a _get_neboda_valenciana"
    val_level  = levelb-levela
    amplada    = levela - 1
    retorn     = _get_niece(val_level, "", step)
    if amplada == 1:
        stramplada = ""
    else:
        stramplada = _LEVEL_NAME_F[amplada]
    return retorn+u" valenciana "+ stramplada+inlaw

class RelationshipCalculator(gramps.gen.relationship.RelationshipCalculator):
    """
    RelationshipCalculator Class
    """

    INLAW = u' polític'

    def __init__(self):
        gramps.gen.relationship.RelationshipCalculator.__init__(self)

# kinship report

    def get_plural_relationship_string(self, Ga, Gb,
                                       reltocommon_a='', reltocommon_b='',
                                       only_birth=True,
                                       in_law_a=False, in_law_b=False):
        """
        see relationship.py
        """

        rel_str = u"parents llunyans"
        #atgen = u" de la %sena generació"
        #bygen = u" per la %sena generació"
        #cmt = u" (germans o germanes d'un avantpassat" + atgen % Ga + ")"

        if in_law_a or in_law_b:
            inlaw = self.INLAW
        else:
            inlaw = u""

        if Ga == 0:

            # These are descendants

            rel_str = _get_sons(Gb, inlaw)

        elif Gb == 0:

            # These are parents/grand parents

            if Ga < len(_PARENTS_LEVEL):
                rel_str = _PARENTS_LEVEL[Ga]
            elif Ga < len(_LEVEL_NAME_P) -1:
                rel_str = u"els avis " + _LEVEL_NAME_P[Ga - 1]
            else:
                rel_str = u"els avis %dens" % (Ga - 1)

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
            inlaw = u""

        rel_str = u"un parent llunyà%s" % inlaw
        #bygen = u" per la %sena generació"
        if Ga == 0:

            # b is descendant of a

            if Gb == 0:
                rel_str = u"la mateixa persona"
            elif gender_b == Person.MALE:

                # spouse of daughter

                if inlaw and Gb == 1 and not step:
                    rel_str = u"el gendre"
                else:
                    rel_str = _get_son(Gb, inlaw, step)
            elif gender_b == Person.FEMALE:

                # spouse of son

                if inlaw and Gb == 1 and not step:
                    rel_str = u"la jove"
                else:
                    rel_str = _get_daughter(Gb, inlaw, step)
            else:
                rel_str = _get_child_unknown(Gb, inlaw, step)
        elif Gb == 0:

            # b is parents/grand parent of a

            if gender_b == Person.MALE:

                # father of spouse (family of spouse)
                if Ga == 1 and inlaw and not step:
                    rel_str = u"el sogre"

                else:
                    rel_str = _get_father(Ga, inlaw, step)
            elif gender_b == Person.FEMALE:

                # mother of spouse (family of spouse)
                if Ga == 1 and inlaw and not step:
                    rel_str = u"la sogra"

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
                else:			# gender_b == Person.UNKNOWN:
                    rel_str = "un cunyat"
		
            elif gender_b == Person.MALE :
                rel_str = _get_uncle(Ga, inlaw, step)
            elif gender_b == Person.FEMALE :
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
                rel_str = u"un nebot%s llunyà (%dena generació)" % (inlaw, Gb)
        elif Ga == Gb:

            # a and b cousins in the same generation

            if gender_b == Person.MALE:
                rel_str = _get_cosi(Ga - 1, inlaw, step)
            elif gender_b == Person.FEMALE:
                rel_str = _get_cosina(Ga - 1, inlaw, step)
            elif gender_b == Person.UNKNOWN:
                rel_str = _get_cosi_unknown(Ga-1, inlaw, step)
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

    def get_sibling_relationship_string(self, sib_type, gender_a,
            gender_b, in_law_a=False, in_law_b=False):
        """
        voir relationship.py
        """

        if in_law_a or in_law_b:
            inlaw = self.INLAW
        else:
            inlaw = u""

        if sib_type == self.NORM_SIB:
            if not inlaw:
                if gender_b == Person.MALE:
                    rel_str = u"el germà"
                elif gender_b == Person.FEMALE:
                    rel_str = u"la germana"
                else:
                    rel_str = u"el germà o germana"
            else:
                if gender_b == Person.MALE:
                    rel_str = u"el cunyat"
                elif gender_b == Person.FEMALE:
                    rel_str = u"la cunyada"
                else:
                    rel_str = u"el cunyat o la cunyada"
        elif sib_type == self.UNKNOWN_SIB:
            if not inlaw:
                if gender_b == Person.MALE:
                    rel_str = u"el germà"
                elif gender_b == Person.FEMALE:
                    rel_str = u"la germana"
                else:
                    rel_str = u"el germà o germana"
            else:
                if gender_b == Person.MALE:
                    rel_str = u"el cunyat"
                elif gender_b == Person.FEMALE:
                    rel_str = u"la cunyada"
                else:
                    rel_str = u"el cunyat o la cunyada"
        elif sib_type == self.HALF_SIB_MOTHER \
          or sib_type == self.HALF_SIB_FATHER \
	  or sib_type == self.STEP_SIB:

            if not inlaw:

                if gender_b == Person.MALE:
                    rel_str = u"el germanastre"
                elif gender_b == Person.FEMALE:
                    rel_str = u"la germanastra"
                else:
                    rel_str = u"el germanastre o la germanastra"
            else:
                if gender_b == Person.MALE:
                    rel_str = u"el cunyat"
                elif gender_b == Person.FEMALE:
                    rel_str = u"la cunyada"
                else:
                    rel_str = u"el cunyat o la cunyada"
        return rel_str

if __name__ == "__main__":

    # Test function. Call it as follows from the command line (so as to find
    #        imported modules):
    #    export PYTHONPATH=/path/to/gramps/src
    # python src/plugins/rel/rel_ca.py
    # (Above not needed here)

    #""
    #   TRANSLATORS, copy this if statement at the bottom of your 
    #   rel_xx.py module, and test your work with:
    #   python src/plugins/rel/rel_xx.py
    #""
    from gramps.gen.relationship import test
    RC = RelationshipCalculator()
    test(RC, True)

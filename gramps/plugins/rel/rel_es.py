# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2005  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2005-2012  Julio Sanchez
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any latr version.
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
#-------------------------------------------------------------------------
"""
Spanish-specific classes for relationships.
"""

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------

from gramps.gen.lib import Person
MALE = Person.MALE
FEMALE = Person.FEMALE
UNKNOWN = Person.UNKNOWN
import gramps.gen.relationship

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------

_level_name_male = [ "", "primero", "segundo", "tercero", "cuarto", "quinto",
                     "sexto", "séptimo", "octavo", "noveno", "décimo", "undécimo",
                     "duodécimo", "decimotercero", "decimocuarto", "decimoquinto",
                     "decimosexto", "decimoséptimo", "decimoctavo", "decimonono",
                     "vigésimo" ]

# Short forms (in apocope) used before names
_level_name_male_a = [ "", "primer", "segundo", "tercer", "cuarto", "quinto",
                       "sexto", "séptimo", "octavo", "noveno", "décimo", "undécimo",
                       "duodécimo", "decimotercer", "decimocuarto", "decimoquinto",
                       "decimosexto", "decimoséptimo", "decimoctavo", "decimonono",
                       "vigésimo" ]

_level_name_female = [ "", "primera", "segunda", "tercera", "cuarta", "quinta",
                       "sexta", "séptima", "octava", "novena", "décima", "undécima",
                       "duodécima", "decimotercera", "decimocuarta", "decimoquinta",
                       "decimosexta", "decimoséptima", "decimoctava", "decimonona",
                       "vigésima" ]

_level_name_plural = [ "", "primeros", "segundos", "terceros", "cuartos",
                       "quintos", "sextos", "séptimos", "octavos", "novenos",
                       "décimos", "undécimos", "duodécimos", "decimoterceros",
                       "decimocuartos", "decimoquintos", "decimosextos",
                       "decimoséptimos", "decimoctavos", "decimononos",
                       "vigésimos" ]

# This plugin tries to be flexible and expect little from the following
# tables.  Ancestors are named from the list for the first generations.
# When this list is not enough, ordinals are used based on the same idea,
# i.e. bisabuelo is 'segundo abuelo' and so on, that has been the
# traditional way in Spanish.  When we run out of ordinals we resort to
# N-ésimo notation, that is sort of understandable if in context.
# 'trastatarabuelo' is not in DRAE, but is well known
_parents_level = [ "", "padres",
                   "abuelos",
                   "bisabuelos",
                   "tatarabuelos",
                   "trastatarabuelos" ]

_father_level = [ "", "padre%(inlaw)s",
                  "abuelo%(inlaw)s",
                  "bisabuelo%(inlaw)s",
                  "tatarabuelo%(inlaw)s",
                  "trastatarabuelo%(inlaw)s"]

_mother_level = [ "", "madre%(inlaw)s",
                  "abuela%(inlaw)s",
                  "bisabuela%(inlaw)s",
                  "tatarabuela%(inlaw)s",
                  "trastatarabuela%(inlaw)s"]

# step-relationships can't be handled as in English
# Notice that the traditional lack of divorce in Catholic, Spanish-speaking, countries has resulted
# in a scarcity of terms to describe these relationships since only death of a spouse would let the
# other marry again. Divorce is common now, so these relationships abound, but history has left us
# without support in the language. So, in this case, we will be more liberal than in other cases and
# or coin a few new words or accept others that seem to have some use, but always patterned
# after the style of the well-documented cases, so that users can intuitively guess their meaning.
# Notice that "that relationship does not exist in Spanish" is not a valid objection. Once the Gramps
# core has computed a relationship, it *has* to be named *somehow*. The only alternative is to change
# the Gramps core so that it does not find relationships that cannot be named in Spanish.

_step_father_level = [ "", "padrastro%(inlaw)s",
                       "abuelastro%(inlaw)s" ]

_step_mother_level = [ "", "madrastra%(inlaw)s",
                       "abuelastra%(inlaw)s" ]

# Higher-order terms (after trastatarabuelo) on this list are not standard,
# but then there is no standard naming scheme at all for this in Spanish.
# Check http://www.genealogia-es.com/guia3.html that echoes a proposed
# scheme that has got some reception in the Spanish-language genealogy
# community. Uncomment these names if you want to use them.
#_parents_level = [ "", "padres", "abuelos", "bisabuelos", "tatarabuelos",
#                   "trastatarabuelos", "pentabuelos", "hexabuelos",
#                   "heptabuelos", "octabuelos", "eneabuelos", "decabuelos"]
#_father_level = [ "", "padre", "abuelo", "bisabuelo", "tatarabuelo",
#                  "trastatarabuelo", "pentabuelo", "hexabuelo",
#                  "heptabuelo", "octabuelo", "eneabuelo", "decabuelo"]
#_mother_level = [ "", "madre", "abuela", "bisabuela", "tatarabuela",
#                  "trastatarabuela", "pentabuela", "hexabuela",
#                  "heptabuela", "octabuela", "eneabuela", "decabuela"]

# DRAE defines cuadrinieto as well, with the same meaning as chozno
# trastataranieto is in use too, but is not in DRAE
# DRAE also registers bizchozno and bischozno, but prefers bichozno
_son_level = [ "", "hijo%(inlaw)s",
               "nieto%(inlaw)s",
               "bisnieto%(inlaw)s",
               "tataranieto%(inlaw)s",
               "chozno%(inlaw)s",
               "bichozno%(inlaw)s" ]

# Though "abuelastro" is in DRAE, "nietastro" isn't
_step_son_level = [ "", "hijastro%(inlaw)s",
                    "nietastro%(inlaw)s" ]

_daughter_level = [ "", "hija%(inlaw)s",
                    "nieta%(inlaw)s",
                    "bisnieta%(inlaw)s",
                    "tataranieta%(inlaw)s",
                    "chozna%(inlaw)s",
                    "bichozna%(inlaw)s" ]

_step_daughter_level = [ "", "hijastra%(inlaw)s",
                         "nietastra%(inlaw)s" ]

_sister_level = [ "", "hermana%(inlaw)s",
                  "tía%(inlaw)s",
                  "tía abuela%(inlaw)s",
                  "tía bisabuela%(inlaw)s",
                  "tía tatarabuela%(inlaw)s" ]

# Tiastro/tiastra aren't in DRAE
_step_sister_level = [ "", "hermanastra%(inlaw)s",
                       "tiastra%(inlaw)s",
                       "tía abuelastra%(inlaw)s" ]

_brother_level = [ "", "hermano%(inlaw)s",
                   "tío%(inlaw)s",
                   "tío abuelo%(inlaw)s",
                   "tío bisabuelo%(inlaw)s",
                   "tío tatarabuelo%(inlaw)s" ]

_step_brother_level = [ "", "hermanastro%(inlaw)s",
                        "tiastro%(inlaw)s",
                        "tío abuelastro%(inlaw)s" ]

_nephew_level = [ "", "sobrino%(inlaw)s",
                  "sobrino nieto%(inlaw)s",
                  "sobrino bisnieto%(inlaw)s",
                  "sobrino tataranieto%(inlaw)s",
                  "sobrino chozno%(inlaw)s",
                  "sobrino bichozno%(inlaw)s" ]

# Nether are sobrinastro/sobrinastra
_step_nephew_level = [ "", "sobrinastro%(inlaw)s",
                       "sobrino nietastro%(inlaw)s" ]

_niece_level = [ "", "sobrina%(inlaw)s",
                 "sobrina nieta%(inlaw)s",
                 "sobrina bisnieta%(inlaw)s",
                 "sobrina tataranieta%(inlaw)s",
                 "sobrina chozna%(inlaw)s",
                 "sobrina bichozna%(inlaw)s" ]

_step_niece_level = [ "", "sobrinastra%(inlaw)s",
                      "sobrina nietastra%(inlaw)s" ]

_children_level = [ "", "hijos",
                    "nietos",
                    "bisnietos",
                    "tataranietos",
                    "choznos",
                    "bichoznos" ]

_siblings_level = [ "",
    "hermanos/as",                         "tíos/tías",
    "tíos abuelos/tías abuelas",           "tíos bisabuelos/tías bisabuelas",
    "tíos tatarabuelos/tías tatarabuelas", "tíos trastatarabuelos/tías trastatarabuelas" ]

_nephews_nieces_level = [   "",
                            "hermanos/as",
                            "sobrinos/as",
                            "sobrinos nietos/sobrinas nietas",
                            "sobrinos bisnietos/sobrinas bisnietas",
                            "sobrinos tataranietos/sobrinas tataranietas",
                            "sobrinos choznos/sobrinas choznas",
                            "sobrinos bichoznos/sobrinas bichoznas" ]


#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class RelationshipCalculator(gramps.gen.relationship.RelationshipCalculator):
    """
    RelationshipCalculator Class
    """

    def __init__(self):
        gramps.gen.relationship.RelationshipCalculator.__init__(self)

    def _get_step_father(self, level, inlaw=''):
        """Internal spanish method to create relation string
        """
        if level < len(_step_father_level):
            return _step_father_level[level] % {'inlaw': inlaw}
        elif (level-1) < len(_level_name_male_a):
            return "%s abuelastro%s" % (_level_name_male_a[level-1],inlaw)
        else:
            return "%d-ésimo abuelastro%s" % (level-1,inlaw)

    def _get_father(self, level, step='', inlaw=''):
        """Internal spanish method to create relation string
        """
        if step:
            return self._get_step_father(level, inlaw)
        if inlaw and level == 1:
            return "suegro"
        if level < len(_father_level):
            return _father_level[level] % {'inlaw': inlaw}
        elif (level-1) < len(_level_name_male_a):
            return "%s abuelo%s" % (_level_name_male_a[level-1],inlaw)
        else:
            return "%d-ésimo abuelo%s" % (level-1,inlaw)

    def _get_step_son(self, level, inlaw=''):
        """Internal spanish method to create relation string
        """
        if level < len(_step_son_level):
            return _step_son_level[level] % {'inlaw': inlaw}
        elif (level-1) < len(_level_name_male_a):
            return "%s nietastro%s" % (_level_name_male_a[level-1],inlaw)
        else:
            return "%d-ésimo nietastro%s" % (level-1,inlaw)

    def _get_son(self, level, step='', inlaw=''):
        """Internal spanish method to create relation string
        """
        if step:
            return self._get_step_son(level, inlaw)
        if inlaw and level == 1:
            return "yerno"
        if level < len(_son_level):
            return _son_level[level] % {'inlaw': inlaw}
        elif (level-1) < len(_level_name_male_a):
            return "%s nieto%s" % (_level_name_male_a[level-1], inlaw)
        else:
            return "%d-ésimo nieto%s" % (level-1, inlaw)

    def _get_step_mother(self, level, inlaw=''):
        """Internal spanish method to create relation string
        """
        if level < len(_step_mother_level):
            return _step_mother_level[level] % {'inlaw': inlaw}
        elif (level-1) < len(_level_name_female):
            return "%s abuelastra%s" % (_level_name_female[level-1],inlaw)
        else:
            return "%d-ésima abuelastra%s" % (level-1,inlaw)

    def _get_mother(self, level, step='', inlaw=''):
        """Internal spanish method to create relation string
        """
        if step:
            return self._get_step_mother(level, inlaw)
        if inlaw and level == 1:
            return "suegra"
        if level < len(_mother_level):
            return _mother_level[level] % {'inlaw': inlaw}
        elif (level-1) < len(_level_name_female):
            return "%s abuela%s" % (_level_name_female[level-1],inlaw)
        else:
            return "%d-ésima abuela%s" % (level-1,inlaw)

    def _get_step_daughter(self, level, inlaw=''):
        """Internal spanish method to create relation string
        """
        if level < len(_step_daughter_level):
            return _step_daughter_level[level] % {'inlaw': inlaw}
        elif (level-1) < len(_level_name_female):
            return "%s nietastra%s" % (_level_name_female[level-1],inlaw)
        else:
            return "%d-ésima nietastra%s" % (level-1,inlaw)

    def _get_daughter(self, level, step='', inlaw=''):
        """Internal spanish method to create relation string
        """
        if step:
            return self._get_step_daughter(level, inlaw)
        if inlaw and level == 1:
            return "nuera"
        if level < len(_daughter_level):
            return _daughter_level[level] % {'inlaw': inlaw}
        elif (level-1) < len(_level_name_female):
            return "%s nieta%s" % (_level_name_female[level-1], inlaw)
        else:
            return "%d-ésima nieta%s" % (level-1, inlaw)

    def _get_parent_unknown(self, level, step='', inlaw=''):
        """Internal spanish method to create relation string
        """
        return "%s o %s" % (self._get_father(level,step,inlaw), self._get_mother(level,step,inlaw))

    def _get_child_unknown(self, level, step='', inlaw=''):
        """Internal spanish method to create relation string
        """
        return "%s o %s" % (self._get_son(level,step,inlaw), self._get_daughter(level,step,inlaw))

    def _get_step_aunt(self, level, inlaw=''):
        """Internal spanish method to create relation string
        """
        if level < len(_step_sister_level):
            return _step_sister_level[level] % {'inlaw': inlaw}
        elif (level-2) < len(_level_name_female):
            return "%s tía abuelastra%s" % (_level_name_female[level-2],inlaw)
        else:
            return "%d-ésima tia abuelastra%s" % (level-2,inlaw)

    def _get_aunt(self, level, step='', inlaw=''):
        """Internal spanish method to create relation string
        """
        if step:
            return self._get_step_aunt(level, inlaw)
        if inlaw and level == 1:
            return "cuñada"
        if level < len(_sister_level):
            return _sister_level[level] % {'inlaw': inlaw}
        elif (level-2) < len(_level_name_female):
            return "%s tía abuela%s" % (_level_name_female[level-2], inlaw)
        else:
            return "%d-ésima tía abuela%s" % (level-2, inlaw)

    def _get_distant_aunt(self, level, step, inlaw):
        if step:
            base = 'tiastra'
        else:
            base = 'tía'
        if level < len(_level_name_female):
            return "%s %s" % (base,_level_name_female[level])
        else:
            return "%s %d-ésima" % (base,level)

    def _get_step_uncle(self, level, inlaw=''):
        """Internal spanish method to create relation string
        """
        if level < len(_step_brother_level):
            return _step_brother_level[level] % {'inlaw': inlaw}
        elif (level-2) < len(_level_name_male_a):
            return "%s tío abuelastro%s" % (_level_name_male_a[level-2],inlaw)
        else:
            return "%d-ésimo tío abuelastro%s" % (level-2,inlaw)

    def _get_uncle(self, level, step='', inlaw=''):
        """Internal spanish method to create relation string
        """
        if step:
            return self._get_step_uncle(level, inlaw)
        if inlaw and level == 1:
            return "cuñado"
        if level < len(_brother_level):
            return _brother_level[level] % {'inlaw': inlaw}
        elif (level-2) < len(_level_name_male_a):
            return "%s tío abuelo%s" % (_level_name_male_a[level-2], inlaw)
        else:
            return "%d-ésimo tío abuelo%s" % (level-2, inlaw)

    def _get_distant_uncle(self, level, step='', inlaw=''):
        if step:
            base = 'tiastro'
        else:
            base = 'tío'
        if level < len(_level_name_male):
            return "%s %s" % (base,_level_name_male[level])
        else:
            return "%s %d-ésimo" % (base,level)

    def _get_step_nephew(self, level, inlaw=''):
        """Internal spanish method to create relation string
        """
        if level < len(_step_nephew_level):
            return _step_nephew_level[level] % {'inlaw': inlaw}
        elif (level-1) < len(_level_name_male_a):
            return "%s tío sobrinastro%s" % (_level_name_male_a[level-1],inlaw)
        else:
            return "%d-ésimo tío sobrinastro%s" % (level-1,inlaw)

    def _get_nephew(self, level, step='', inlaw=''):
        """Internal spanish method to create relation string
        """
        if step:
            return self._get_step_nephew(level, inlaw)
        if level < len(_nephew_level):
            return _nephew_level[level] % {'inlaw': inlaw}
        elif (level-1) < len(_level_name_male_a):
            return "%s sobrino nieto%s" % (_level_name_male_a[level-1], inlaw)
        else:
            return "%d-ésimo sobrino nieto%s" % (level-1, inlaw)

    def _get_distant_nephew(self, level, step, inlaw):
        if step:
            base = 'sobrinastro'
        else:
            base = 'sobrino'
        if level < len(_level_name_male):
            return "%s %s" % (base,_level_name_male[level])
        else:
            return "%s %d-ésimo" % (base,level)

    def _get_step_niece(self, level, inlaw=''):
        """Internal spanish method to create relation string
        """
        if level < len(_step_niece_level):
            return _step_niece_level[level] % {'inlaw': inlaw}
        elif (level-1) < len(_level_name_female):
            return "%s tía sobrinastra%s" % (_level_name_female[level-1],inlaw)
        else:
            return "%d-ésima tía sobrinastra%s" % (level-1,inlaw)

    def _get_niece(self, level, step='', inlaw=''):
        """Internal spanish method to create relation string
        """
        if step:
            return self._get_step_niece(level, inlaw)
        if level < len(_niece_level):
            return _niece_level[level] % {'inlaw': inlaw}
        elif (level-1) < len(_level_name_female):
            return "%s sobrina nieta%s" % (_level_name_female[level-1], inlaw)
        else:
            return "%d-ésima sobrina nieta%s" % (level-1, inlaw)

    def _get_distant_niece(self, level, step, inlaw):
        if step:
            base = 'sobrinastra'
        else:
            base = 'sobrina'
        if level < len(_level_name_female):
            return "%s %s" % (base,_level_name_female[level])
        else:
            return "%s %d-ésima" % (base,level)

    def _get_male_cousin(self, level, removed, lower=False, step='', inlaw='', gender_c=UNKNOWN):
        """Internal spanish method to create relation string
        """
        # primastro is an invention and is not backed by DRAE
        if step:
            prim="primastro"
        else:
            prim="primo"
        if removed == 0:
            if level == 1:
                return "%s hermano%s" % (prim, inlaw)
            elif level < len(_level_name_male):
                return "%s %s%s" % (prim,_level_name_male[level], inlaw)
            else:
                return "%s %d-ésimo%s" % (prim, level, inlaw)
        elif removed > 0 and lower:
            if gender_c == MALE:
                return "%s de un %s" % (self._get_son(removed,step,inlaw),
                                        self._get_male_cousin(level, 0, lower, step, inlaw, gender_c))
            elif gender_c == FEMALE:
                return "%s de una %s" % (self._get_son(removed,step,inlaw),
                                         self._get_female_cousin(level, 0, lower, step, inlaw, gender_c))
            else:
                return "%s de un %s" % (self._get_son(removed,step,inlaw),
                                        self._get_male_cousin(level, 0, lower, step, inlaw, gender_c))
        elif removed > 0 and not lower:
            if gender_c == MALE:
                return "%s de un %s" % (self._get_male_cousin(level, 0, lower, step, inlaw, gender_c),
                                        self._get_father(removed,step,inlaw))
            elif gender_c == FEMALE:
                return "%s de una %s" % (self._get_male_cousin(level, 0, lower, step, inlaw, gender_c),
                                         self._get_mother(removed,step,inlaw))
            else:
                return "%s de un %s" % (self._get_male_cousin(level, 0, lower, step, inlaw, gender_c),
                                        self._get_father(removed,step,inlaw))

        else:
            return "%s %scousin%s (%d-%d)" % (_level_name_male[level],
                                        step, inlaw,
                                        removed, lower)

    def _get_female_cousin(self, level, removed, lower=False, step='', inlaw='', gender_c=UNKNOWN):
        """Internal spanish method to create relation string
        """
        # primastra is an invention and is not real Spanish
        if step:
            prim="primastra"
        else:
            prim="prima"
        if removed == 0:
            if level == 1:
                return "%s hermana%s" % (prim, inlaw)
            elif level < len(_level_name_male):
                return "%s %s%s" % (prim,_level_name_female[level], inlaw)
            else:
                return "%s %d-ésima%s" % (prim, level, inlaw)
        elif removed > 0 and lower:
            if gender_c == MALE:
                return "%s de un %s" % (self._get_daughter(removed,step,inlaw),
                                        self._get_male_cousin(level, 0, lower, step, inlaw, gender_c))
            elif gender_c == FEMALE:
                return "%s de una %s" % (self._get_daughter(removed,step,inlaw),
                                         self._get_female_cousin(level, 0, lower, step, inlaw, gender_c))
            else:
                return "%s de un %s" % (self._get_daughter(removed,step,inlaw),
                                        self._get_male_cousin(level, 0, lower, step, inlaw, gender_c))
        elif removed > 0 and not lower:
            if gender_c == MALE:
                return "%s de un %s" % (self._get_female_cousin(level, 0, lower, step, inlaw, gender_c),
                                        self._get_father(removed,step,inlaw))
            elif gender_c == FEMALE:
                return "%s de una %s" % (self._get_female_cousin(level, 0, lower, step, inlaw, gender_c),
                                         self._get_mother(removed,step,inlaw))
            else:
                return "%s de un %s" % (self._get_female_cousin(level, 0, lower, step, inlaw, gender_c),
                                        self._get_father(removed,step,inlaw))

        else:
            return "%s %sprima%s (%d-%d)" % (_level_name_female[level],
                                        step, inlaw,
                                        removed, lower)

    def _get_sibling(self, level, step='', inlaw=''):
        """Internal spanish method to create relation string
        """
        # TBC: inlaw is inflicted, it is probably better to do away with this method
        # and do both calls from the caller (would need inlaw_MALE and inlaw_FEMALE,
        # but is feasible
        return "%s o %s" % (self._get_uncle(level,step,inlaw),self._get_aunt(level,step,inlaw))

    def get_plural_relationship_string(self, Ga, Gb,
                                       reltocommon_a='', reltocommon_b='',
                                       only_birth=True,
                                       in_law_a=False, in_law_b=False):
        """Spanish version of method to create relation string - check relationship.py
        """

        rel_str = "parientes lejanos"
        if Ga == 0:
            # These are descendants
            if Gb < len(_children_level):
                rel_str = _children_level[Gb]
            elif (Gb-1) < len(_level_name_plural):
                rel_str = "%s nietos" % (_level_name_plural[Gb-1])
            else:
                rel_str = "%d-ésimos nietos" % (Gb-1)
        elif Gb == 0:
            # These are parents/grand parents
            if Ga < len(_parents_level):
                rel_str = _parents_level[Ga]
            elif (Ga-1) < len(_level_name_plural):
                rel_str = "%s abuelos" % (_level_name_plural[Ga-1])
            else:
                rel_str = "%d-ésimos abuelos" % (Ga-1)
        elif Gb == 1:
            # These are siblings/aunts/uncles
            if Ga < len(_siblings_level):
                rel_str = _siblings_level[Ga]
            elif (Ga-1) < len(_level_name_plural):
                rel_str = "%s tíos abuelos" % (_level_name_plural[Ga-1])
            else:
                rel_str = "%s-ésimos tíos abuelos" % (Ga-1)
        elif Ga == 1:
            # These are nieces/nephews
            if Gb < len(_nephews_nieces_level):
                rel_str = _nephews_nieces_level[Gb]
            elif (Gb-1) < len(_level_name_plural):
                rel_str = "%s sobrinos nietos" % (_level_name_plural[Gb-1])
            else:
                rel_str = "%s-ésimos sobrinos nietos" % (Gb-1)
        elif Ga > 1 and Ga == Gb:
            # These are cousins in the same generation
            if Ga == 2:
                rel_str = "primos hermanos"
            elif (Ga-1) < len(_level_name_plural):
                rel_str = "primos %s" % (_level_name_plural[Ga-1])
            else:
                rel_str = "primos %d-ésimos" % (Ga-1)
        elif Ga == Gb+1:
            # These are distant uncles/aunts
            if Gb < len(_level_name_plural):
                rel_str = "tíos %s" % (_level_name_plural[Gb])
            else:
                rel_str = "tíos %d-ésimos" % (Gb)
        elif Ga+1 == Gb:
            # These are distant nephews/nieces
            if Gb-1 < len(_level_name_plural):
                rel_str = "sobrinos %s" % (_level_name_plural[Gb-1])
            else:
                rel_str = "sobrinos %d-ésimos" % (Gb-1)
        elif Ga > 1 and Ga > Gb:
            # These are cousins in different generations with the second person
            # being in a higher generation from the common ancestor than the
            # first person.
            rel_str = "%s de los %s" % (
                self.get_plural_relationship_string(0, Gb),
                self.get_plural_relationship_string(Ga, 0) )
        elif Gb > 1 and Gb > Ga:
            # These are cousins in different generations with the second person
            # being in a lower generation from the common ancestor than the
            # first person.
            rel_str = "%s de los %s" % (
                self.get_plural_relationship_string(0, Gb),
                self.get_plural_relationship_string(Ga, 0) )

        if in_law_b == True:
            rel_str = "cónyuges de los %s" % rel_str

        return rel_str

    def get_single_relationship_string(self, Ga, Gb, gender_a, gender_b,
                                       reltocommon_a, reltocommon_b,
                                       only_birth=True,
                                       in_law_a=False, in_law_b=False):
        """Spanish version of method to create relation string - check relationship.py
        """

        if only_birth:
            step = ''
        else:
            step = self.STEP

        if in_law_a or in_law_b :
            if gender_b == FEMALE:
                inlaw = ' política'
            else:
                inlaw = ' político'
        else:
            inlaw = ''

        rel_str = "%spariente%s lejano" % (step, inlaw)

        if Ga == 0:
            # b is descendant of a
            if Gb == 0 :
                rel_str = 'la misma persona'
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
                rel_str = self._get_nephew(Gb-1, step, inlaw)
            elif gender_b == FEMALE:
                rel_str = self._get_niece(Gb-1, step, inlaw)
            else:
                rel_str = "%s o %s" % (self._get_nephew(Gb-1, step, inlaw),
                                       self._get_niece(Gb-1, step, inlaw))
        elif Ga == Gb:
            # a and b cousins in the same generation
            if gender_b == MALE:
                rel_str = self._get_male_cousin(Ga-1, 0, lower=False, step=step,
                                              inlaw=inlaw)
            elif gender_b == FEMALE:
                rel_str = self._get_female_cousin(Ga-1, 0, lower=False, step=step,
                                              inlaw=inlaw)
            else:
                rel_str = "%s o %s" % (self._get_male_cousin(Ga-1, 0, step=step, inlaw=inlaw),
                                       self._get_female_cousin(Ga-1, 0, step=step, inlaw=inlaw))
        elif Ga == Gb+1:
            if gender_b == Person.MALE:
                rel_str = self._get_distant_uncle(Gb, step, inlaw)
            elif gender_b == Person.FEMALE:
                rel_str = self._get_distant_aunt(Gb, step, inlaw)
            else:
                rel_str = "%s o %s" % (self._get_distant_uncle(Gb, step, inlaw),
                                       self._get_distant_aunt(Gb, step, inlaw))
        elif Ga+1 == Gb:
            if gender_b == Person.MALE:
                rel_str = self._get_distant_nephew(Gb-1, step, inlaw)
            elif gender_b == Person.FEMALE:
                rel_str = self._get_distant_niece(Gb-1, step, inlaw)
            else:
                rel_str = "%s o %s" % (self._get_distant_nephew(Gb-1, step, inlaw),
                                       self._get_distant_niece(Gb-1, step, inlaw))
        elif Ga > Gb:
            # These are cousins in different generations with the second person
            # being in a higher generation from the common ancestor than the
            # first person.
            # We need to know the gender of the ancestor of the first person who is on
            # the same generation as the other person
            if reltocommon_a[Ga-Gb-1] == 'f':
                gender_c = MALE
            elif reltocommon_a[Ga-Gb-1] == 'm':
                gender_c = FEMALE
            else:
                gender_c = UNKNOWN
            if gender_b == MALE:
                rel_str = self._get_male_cousin(Gb-1, Ga-Gb, lower=False,
                                                step=step, inlaw=inlaw, gender_c=gender_c)
            elif gender_b == FEMALE:
                rel_str = self._get_female_cousin(Gb-1, Ga-Gb, lower=False,
                                                step=step, inlaw=inlaw, gender_c=gender_c)
            else:
                rel_str = "%s o %s" % (self._get_male_cousin(Gb-1, Ga-Gb, lower=False,
                                                             step=step, inlaw=inlaw),
                                       self._get_female_cousin(Gb-1, Ga-Gb, lower=False,
                                                               step=step, inlaw=inlaw))

        elif Gb > Ga:
            # These are cousins in different generations with the second person
            # being in a lower generation from the common ancestor than the
            # first person.
            # We need to know the gender of the person who is an ancestor of the second person and
            # is on the same generation that the first person
            if reltocommon_b[Gb-Ga-1] == 'f':
                gender_c = MALE
            elif reltocommon_b[Gb-Ga-1] == 'm':
                gender_c = FEMALE
            else:
                gender_c = UNKNOWN
            if gender_b == MALE:
                rel_str = self._get_male_cousin(Ga-1, Gb-Ga, lower=True,
                                                step=step, inlaw=inlaw, gender_c=gender_c)
            elif gender_b == FEMALE:
                rel_str = self._get_female_cousin(Ga-1, Gb-Ga, lower=True,
                                                step=step, inlaw=inlaw, gender_c=gender_c)
            else:
                rel_str = "%s o %s" % (self._get_male_cousin(Ga-1, Gb-Ga, lower=True,
                                                             step=step, inlaw=inlaw),
                                       self._get_female_cousin(Ga-1, Gb-Ga, lower=True,
                                                               step=step, inlaw=inlaw))

        return rel_str

    def get_sibling_relationship_string(self, sib_type, gender_a, gender_b,
                                        in_law_a=False, in_law_b=False):
        """
        """

        rel_str = ''
        if gender_b != FEMALE:
            if sib_type == self.NORM_SIB or sib_type == self.UNKNOWN_SIB:
                rel_str = 'hermano'
            elif sib_type == self.HALF_SIB_MOTHER \
                    or sib_type == self.HALF_SIB_FATHER:
                rel_str = 'medio hermano'
            elif sib_type == self.STEP_SIB:
                rel_str = 'hermanastro'
            if in_law_a or in_law_b :
                rel_str += ' político'

        if gender_b == UNKNOWN:
            rel_str += ' o '

        if gender_b != MALE:
            if sib_type == self.NORM_SIB or sib_type == self.UNKNOWN_SIB:
                rel_str += 'hermana'
            elif sib_type == self.HALF_SIB_MOTHER \
                    or sib_type == self.HALF_SIB_FATHER:
                rel_str += 'medio hermana'
            elif sib_type == self.STEP_SIB:
                rel_str += 'hermanastra'
            if in_law_a or in_law_b :
                rel_str += ' política'

        return rel_str

if __name__ == "__main__":

    # Test function. Call it as follows from the command line (so as to find
    #        imported modules):
    #    export PYTHONPATH=/path/to/gramps/src
    # python src/plugins/rel/rel_es.py
    # (Above not needed here)

    """TRANSLATORS, copy this if statement at the bottom of your
        rel_xx.py module, and test your work with:
        python src/plugins/rel/rel_xx.py
    """
    from gramps.gen.relationship import test
    RC = RelationshipCalculator()
    test(RC, True)

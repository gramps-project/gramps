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
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#
# -------------------------------------------------------------------------
"""
Spanish-specific classes for relationships.
"""

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------

from gramps.gen.lib import Person

MALE = Person.MALE
FEMALE = Person.FEMALE
UNKNOWN = Person.UNKNOWN
import gramps.gen.relationship

# ------------------------------------------------------------------
# Ordinal lists (male canonical forms, 1-based, index 0 is empty)
# Other genders are derived at module load time.
# ------------------------------------------------------------------

_ORD_FIRST_19_M = [
    "primero", "segundo", "tercero", "cuarto", "quinto", "sexto",
    "séptimo", "octavo", "noveno", "décimo",
    "undécimo", "duodécimo",
    "decimotercero", "decimocuarto", "decimoquinto", "decimosexto",
    "decimoséptimo", "decimoctavo", "decimonoveno"
]

_ORD_TENS_M = [
    "", "décimo", "vigésimo", "trigésimo", "cuadragésimo",
    "quincuagésimo", "sexagésimo", "septuagésimo",
    "octogésimo", "nonagésimo", "centésimo"
]

_ORD_UNITS_M = [
    "", "primero", "segundo", "tercero", "cuarto", "quinto",
    "sexto", "séptimo", "octavo", "noveno"
]


def _to_feminine(word):
    """Derive feminine ordinal from the masculine form.

    All Spanish masculine ordinals end in 'o' and form the feminine
    by replacing the final 'o' with 'a'. Multi-word forms like
    'vigésimo primero' become 'vigésima primera'.
    """
    if not word:
        return word
    parts = word.split()
    return " ".join(p[:-1] + "a" if p.endswith("o") else p for p in parts)


def _to_plural(word):
    """Derive plural ordinal from the masculine form.

    Spanish masculine ordinals form the plural by replacing the
    final 'o' with 'os'. Multi-word forms like 'vigésimo primero'
    become 'vigésimos primeros'.
    """
    if not word:
        return word
    parts = word.split()
    return " ".join(p[:-1] + "os" if p.endswith("o") else p for p in parts)


def _build_ordinals(first_19, tens, units):
    """Build ordinal list (0..100) from component word lists."""
    ords = [""]
    ords.extend(first_19)
    for t_idx in range(2, 10):
        ten = tens[t_idx]
        ords.append(ten)
        for u_idx in range(1, 10):
            ords.append(ten + " " + units[u_idx])
    ords.append(tens[10])
    return ords


# Build all three gender forms from the male canonical data
_ordinal_male = _build_ordinals(_ORD_FIRST_19_M, _ORD_TENS_M, _ORD_UNITS_M)
_ordinal_female = [_to_feminine(w) for w in _ordinal_male]
_ordinal_plural = [_to_plural(w) for w in _ordinal_male]

# ------------------------------------------------------------------
# Ancestor names (male canonical, index = generations above ego)
# Index 0 empty, 1 parent level (empty for male/female), 2+ explicit.
# Female/plural derived by transforming the last vowel.
# ------------------------------------------------------------------

_ancestor_male = [
    "",
    "",
    "abuelo",
    "bisabuelo",
    "tatarabuelo",
    "trastatarabuelo",
    "pentabuelo",
    "hexabuelo",
    "heptabuelo",
    "octabuelo",
    "eneabuelo",
    "decabuelo",
    "endecabuelo",
    "dodecabuelo",
]

_ancestor_female = [_to_feminine(w) for w in _ancestor_male]
_ancestor_plural = [
    "padres" if i == 1 else _to_plural(w) for i, w in enumerate(_ancestor_male)
]

# ------------------------------------------------------------------
# Descendant names (male canonical, index = generations below ego)
# Same derivation pattern as ancestors.
# ------------------------------------------------------------------

_descendant_male = [
    "",
    "",
    "nieto",
    "bisnieto",
    "tataranieto",
    "chozno",
    "bichozno",
    "hexanieto",
    "heptanieto",
    "octonieto",
    "eneanieto",
    "decanieto",
    "endecanieto",
    "dodecanieto",
]

_descendant_female = [_to_feminine(w) for w in _descendant_male]
_descendant_plural = [
    "hijos" if i == 1 else _to_plural(w) for i, w in enumerate(_descendant_male)
]

# ------------------------------------------------------------------
# Step transformations for the last lexical noun of a compound
# ------------------------------------------------------------------

_STEP_EXCEPTIONS_M = {
    "tío": "tiastro",
    "hermano": "hermanastro",
    "hijo": "hijastro",
    "sobrino": "sobrinastro",
    "primo": "primastro",
    "padre": "padrastro",
    "suegro": "suegrastro",
    "yerno": "yernastro",
    "cuñado": "cuñadastro",
    "concuñado": "concuñadastro",
    "consuegro": "consuegrastro",
}
_STEP_EXCEPTIONS_F = {
    "tía": "tiastra",
    "hermana": "hermanastra",
    "hija": "hijastra",
    "sobrina": "sobrinastra",
    "prima": "primastra",
    "madre": "madrastra",
    "suegra": "suegrastra",
    "nuera": "nuerastra",
    "cuñada": "cuñadastra",
    "concuñada": "concuñadastra",
    "consuegra": "consuegrastra",
}

# ------------------------------------------------------------------
# Partner type terms (for get_partner_relationship_string)
# Keys: spouse_type constant from RelationshipCalculator.
# Values: dict mapping MALE / FEMALE / UNKNOWN -> Spanish term.
# ------------------------------------------------------------------

_PARTNER_TERMS = {
    1: {MALE: "esposo", FEMALE: "esposa", UNKNOWN: "cónyuge"},
    5: {MALE: "exesposo", FEMALE: "exesposa", UNKNOWN: "excónyuge"},
    2: {MALE: "pareja", FEMALE: "pareja", UNKNOWN: "pareja"},
    6: {MALE: "expareja", FEMALE: "expareja", UNKNOWN: "expareja"},
    3: {MALE: "pareja de hecho", FEMALE: "pareja de hecho", UNKNOWN: "pareja de hecho"},
    7: {MALE: "expareja de hecho", FEMALE: "expareja de hecho", UNKNOWN: "expareja de hecho"},
    4: {MALE: "pareja", FEMALE: "pareja", UNKNOWN: "pareja"},
}


def _get_ordinal(n, gender):
    """Return the ordinal adjective for number n in the given gender.

    n=1 returns '' (sibling case, no ordinal displayed).
    n=2 returns 'segundo/a', etc.
    For n beyond 100 returns '{n}-ésimo/a'.
    """
    if n <= 1:
        return ""
    if gender == MALE:
        lst = _ordinal_male
    elif gender == FEMALE:
        lst = _ordinal_female
    else:
        lst = _ordinal_plural
    if n < len(lst):
        return lst[n]
    if gender == MALE:
        return "%d-ésimo" % n
    elif gender == FEMALE:
        return "%d-ésima" % n
    else:
        return "%d-ésimos" % n


def _apocopate(word):
    """Apply Spanish apocope to masculine ordinals before a masculine noun.

    primero -> primer, tercero -> tercer, decimotercero -> decimotercer,
    vigésimo primero -> vigésimo primer, trigésimo tercero -> trigésimo tercer.
    Handles both single words and compound forms.
    """
    if not word:
        return word
    parts = word.split()
    result = []
    for p in parts:
        if p == "primero":
            result.append("primer")
        elif p == "tercero":
            result.append("tercer")
        elif p.endswith("primero"):
            result.append(p[:-7] + "primer")
        elif p.endswith("tercero"):
            result.append(p[:-7] + "tercer")
        else:
            result.append(p)
    return " ".join(result)


def _pick_gender(word_m, word_f, gender):
    """Select male or female word based on gender."""
    return word_m if gender == MALE else word_f


def _add_inlaw(term, inlaw, gender):
    """Append 'político/política' suffix if inlaw is True."""
    if not inlaw:
        return term
    return term + (" política" if gender == FEMALE else " político")


# ------------------------------------------------------------------
# Ancestor/descendant lookup helpers
# Each comes in three variants:
#   _name(n, gender)  -> full term with ordinal fallback
#   _base(n, gender)  -> just the noun part (for compounds)
#   _level_ord(n, gender) -> just the level ordinal (for tío prefix)
# ------------------------------------------------------------------


def _get_ancestor_name(n, gender):
    """Return the full ancestor noun for n generations above ego.

    n=1 returns '' (parent level).
    n=2 returns 'abuelo/a', n=3 'bisabuelo/a', etc.
    For n beyond stored list returns ordinal + 'abuelo/a' with apocope.
    """
    if n <= 1:
        return ""
    lst = _ancestor_male if gender == MALE else (
        _ancestor_female if gender == FEMALE else _ancestor_plural)
    base = "abuelo" if gender == MALE else ("abuela" if gender == FEMALE else "abuelos")
    if n < len(lst) and lst[n]:
        return lst[n]
    ord_word = _get_ordinal(n - 1, gender)
    if gender == MALE:
        ord_word = _apocopate(ord_word)
    return "%s %s" % (ord_word, base)


def _get_ancestor_base(n, gender):
    """Return just the base ancestor noun without any ordinal.

    Used as the middle part in tío/a compounds like 'tío pentabuelo'.
    """
    if n <= 1:
        return ""
    lst = _ancestor_male if gender == MALE else (
        _ancestor_female if gender == FEMALE else _ancestor_plural)
    base = "abuelo" if gender == MALE else ("abuela" if gender == FEMALE else "abuelos")
    if n < len(lst) and lst[n]:
        return lst[n]
    return base


def _get_ancestor_level_ordinal(n, gender):
    """Return the apocopated level ordinal for ancestor level n.

    Returns '' if the level has an explicit term in the list.
    Used as the leading ordinal in uncle/aunt compounds: 'quinto tío abuelo'.
    """
    if n <= 1:
        return ""
    lst = _ancestor_male if gender == MALE else (
        _ancestor_female if gender == FEMALE else _ancestor_plural)
    if n < len(lst) and lst[n]:
        return ""
    ord_word = _get_ordinal(n - 1, gender)
    return _apocopate(ord_word) if gender == MALE else ord_word


def _get_descendant_name(n, gender):
    """Return the full descendant noun for n generations below ego.

    n=1 returns '' (child level).
    n=2 returns 'nieto/a', n=3 'bisnieto/a', etc.
    """
    if n <= 1:
        return ""
    lst = _descendant_male if gender == MALE else (
        _descendant_female if gender == FEMALE else _descendant_plural)
    base = "nieto" if gender == MALE else ("nieta" if gender == FEMALE else "nietos")
    if n < len(lst) and lst[n]:
        return lst[n]
    ord_word = _get_ordinal(n - 1, gender)
    if gender == MALE:
        ord_word = _apocopate(ord_word)
    return "%s %s" % (ord_word, base)


def _get_descendant_base(n, gender):
    """Return just the base descendant noun without any ordinal.

    Used in sobrino/a compounds like 'sobrino nieto sexto'.
    """
    if n <= 1:
        return ""
    lst = _descendant_male if gender == MALE else (
        _descendant_female if gender == FEMALE else _descendant_plural)
    base = "nieto" if gender == MALE else ("nieta" if gender == FEMALE else "nietos")
    if n < len(lst) and lst[n]:
        return lst[n]
    return base


def _get_descendant_level_ordinal(n, gender):
    """Return ordinal for descendant level n (no apocope, goes at end)."""
    if n <= 1:
        return ""
    lst = _descendant_male if gender == MALE else (
        _descendant_female if gender == FEMALE else _descendant_plural)
    if n < len(lst) and lst[n]:
        return ""
    ord_word = _get_ordinal(n - 1, gender)
    return ord_word


# ------------------------------------------------------------------
# Low-level helpers
# ------------------------------------------------------------------


def _step_form(word, gender):
    """Apply the -astro/-astra suffix to a word."""
    exc = _STEP_EXCEPTIONS_M if gender == MALE else _STEP_EXCEPTIONS_F
    if word in exc:
        return exc[word]
    if word.endswith("o"):
        return word[:-1] + "astro"
    if word.endswith("a"):
        return word[:-1] + "astra"
    if word.endswith("os"):
        return word[:-1] + "astros"
    if word.endswith("as"):
        return word[:-1] + "astras"
    return word


def _has_family_marker(reltocommon):
    """Check if a reltocommon string indicates a common-family connection.

    Family markers ('a', 'A', 'b', 'c') mean the two persons share a
    common FAMILY (e.g. their children are married) rather than a common
    blood ancestor. Used to detect consuegro relations.
    """
    return bool(set(reltocommon) & {'a', 'A', 'b', 'c'})


def _pluralize_gender(word):
    """Apply gender-disjunctive suffixes to each part of a plural word.

    'tíos/tías' -> 'tíos/as', 'abuelos' -> 'abuelos/as',
    'sobrinos/as' -> 'sobrinos/as', 'segundos' -> 'segundos/as',
    'vigésimos segundos' -> 'vigésimos/as segundos/as'.
    """
    if not word:
        return word
    parts = word.split()
    result = []
    for p in parts:
        if "/" in p:
            result.append(p.split("/")[0] + "/as")
        elif p.endswith("os"):
            result.append(p + "/as")
        else:
            result.append(p)
    return " ".join(result)


def _build_simple_term(base_name, step, inlaw, gender):
    """Build a simple (non-compound) relationship term with step/inlaw."""
    term = base_name
    if step:
        term = _step_form(term, gender)
    return _add_inlaw(term, inlaw, gender)


# ------------------------------------------------------------------
# Compound builders for lateral relationship types
# Each follows a specific word order established by Spanish convention.
# ------------------------------------------------------------------


def _build_tio(vertical, lateral, gender_b, step, inlaw):
    """Build 'tío/tía + ancestor_base + lateral_ordinal' compound.

    Order: level_ordinal + tío/tía + base + lateral_ordinal
    Example: 'quinto tío abuelo tercero'
    """
    if gender_b == MALE:
        prefix = "tío"
    elif gender_b == FEMALE:
        prefix = "tía"
    else:
        return "%s o %s" % (
            _build_tio(vertical, lateral, MALE, step, inlaw),
            _build_tio(vertical, lateral, FEMALE, step, inlaw),
        )

    base = _get_ancestor_base(vertical, gender_b)
    level_ord = _get_ancestor_level_ordinal(vertical, gender_b)
    lateral_ord = _get_ordinal(lateral, gender_b)

    parts = []
    if step:
        if base:
            base = _step_form(base, gender_b)
        else:
            prefix = _step_form(prefix, gender_b)

    if level_ord:
        parts.append(level_ord)
    parts.append(prefix)
    if base:
        parts.append(base)
    if lateral_ord:
        parts.append(lateral_ord)

    return _add_inlaw(" ".join(parts), inlaw, gender_b)


def _build_sobrino(vertical, lateral, gender_b, step, inlaw):
    """Build 'sobrino/a + descendant_base + ordinal' compound.

    Order: sobrino/a + base + ordinal
    Example: 'sobrino nieto segundo', 'sobrino nieto sexto'
    """
    if gender_b == MALE:
        prefix = "sobrino"
    elif gender_b == FEMALE:
        prefix = "sobrina"
    else:
        return "%s o %s" % (
            _build_sobrino(vertical, lateral, MALE, step, inlaw),
            _build_sobrino(vertical, lateral, FEMALE, step, inlaw),
        )

    base = _get_descendant_base(vertical, gender_b)
    lateral_ord = _get_ordinal(lateral, gender_b)
    desc_ord = _get_descendant_level_ordinal(vertical, gender_b)

    parts = [prefix]
    if step:
        if base:
            base = _step_form(base, gender_b)
        else:
            parts = [_step_form(prefix, gender_b)]

    if base:
        parts.append(base)
    # Only one ordinal at the end: lateral (cousin degree) takes precedence
    ord_word = lateral_ord if lateral > 1 else desc_ord
    if ord_word:
        parts.append(ord_word)

    return _add_inlaw(" ".join(parts), inlaw, gender_b)


def _build_cousin(level, gender_b, step, inlaw):
    """Build 'primo/a + ordinal' for same-generation cousins.

    level=1 returns 'primo hermano' / 'prima hermana'.
    """
    if gender_b == MALE:
        prefix = "primo"
    elif gender_b == FEMALE:
        prefix = "prima"
    else:
        return "%s o %s" % (
            _build_cousin(level, MALE, step, inlaw),
            _build_cousin(level, FEMALE, step, inlaw),
        )

    if step:
        prefix = _step_form(prefix, gender_b)

    if level == 1:
        rel = "%s hermana" % prefix if gender_b == FEMALE else "%s hermano" % prefix
    else:
        ord_word = _get_ordinal(level, gender_b)
        rel = "%s %s" % (prefix, ord_word)

    return _add_inlaw(rel, inlaw, gender_b)


# ------------------------------------------------------------------
# RelationshipCalculator
# ------------------------------------------------------------------


class RelationshipCalculator(gramps.gen.relationship.RelationshipCalculator):
    """
    RelationshipCalculator Class
    """

    def __init__(self):
        gramps.gen.relationship.RelationshipCalculator.__init__(self)

    def _get_rel_for_gender(self, Ga, Gb, gender, step, in_law_a, in_law_b,
                            is_family_connection=False):
        """Build relationship string for a specific gender (MALE or FEMALE)."""

        inlaw = in_law_a or in_law_b

        # In-law special terms for level-1 relationships (suegro, yerno, cuñado)
        if inlaw:
            if Ga == 1 and Gb == 0:
                term = _pick_gender("suegro", "suegra", gender)
                return _step_form(term, gender) if step else term
            if Ga == 0 and Gb == 1:
                term = _pick_gender("yerno", "nuera", gender)
                return _step_form(term, gender) if step else term
            if Ga == 1 and Gb == 1:
                if in_law_a and in_law_b:
                    term = _pick_gender("concuñado", "concuñada", gender)
                else:
                    term = _pick_gender("cuñado", "cuñada", gender)
                return _step_form(term, gender) if step else term

        # Consuegro: connected through children's marriage (family markers
        # in reltocommon), not through a common blood ancestor.
        if Ga == 1 and Gb == 1 and not inlaw and is_family_connection:
            term = _pick_gender("consuegro", "consuegra", gender)
            return _step_form(term, gender) if step else term

        if Ga == 0:
            if Gb <= 1:
                term = _pick_gender("hijo", "hija", gender)
                return _build_simple_term(term, step, inlaw, gender)
            term = _get_descendant_name(Gb, gender)
            if step:
                term = _step_form(term, gender)
            return _add_inlaw(term, inlaw, gender)

        if Gb == 0:
            if Ga <= 1:
                term = _pick_gender("padre", "madre", gender)
                return _build_simple_term(term, step, inlaw, gender)
            term = _get_ancestor_name(Ga, gender)
            if step:
                term = _step_form(term, gender)
            return _add_inlaw(term, inlaw, gender)

        # Sibling: handles Ga=Gb=1
        if Gb == 1 and Ga == 1:
            return _build_simple_term(
                _pick_gender("hermano", "hermana", gender), step, inlaw, gender
            )

        # Uncle/aunt: Ga >= 2, Gb = 1
        if Gb == 1:
            return _build_tio(Ga - 1, 1, gender, step, inlaw)

        # Nephew/niece: Ga = 1, Gb >= 2
        if Ga == 1:
            return _build_sobrino(Gb - 1, 1, gender, step, inlaw)

        # Cousins same generation
        if Ga == Gb:
            return _build_cousin(Ga - 1, gender, step, inlaw)

        # Distant uncle/aunt
        if Ga > Gb:
            return _build_tio(Ga - Gb, Gb, gender, step, inlaw)

        # Distant nephew/niece
        if Gb > Ga:
            return _build_sobrino(Gb - Ga, Ga, gender, step, inlaw)

        return "pariente lejano"

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
        """Spanish version of get_single_relationship_string.

        Implements a unified programmatic model:
        - Ga=0: direct descendant of ego
        - Gb=0: direct ancestor of ego
        - Ga=Gb: same-generation cousins
        - Ga>Gb: tio/a type relation
        - Gb>Ga: sobrino/a type relation
        """

        step = "" if only_birth else self.STEP

        if Ga == 0 and Gb == 0:
            return "la misma persona"

        # Detect if the common connection is a family (consuegro) rather
        # than a blood ancestor. Family markers ('a'/'A'/'b'/'c') appear
        # in reltocommon when relations are collapsed through marriage.
        family_connection = _has_family_marker(reltocommon_a) or \
                            _has_family_marker(reltocommon_b)

        if gender_b == MALE:
            return self._get_rel_for_gender(
                Ga, Gb, MALE, step, in_law_a, in_law_b, family_connection
            )
        if gender_b == FEMALE:
            return self._get_rel_for_gender(
                Ga, Gb, FEMALE, step, in_law_a, in_law_b, family_connection
            )
        return "%s o %s" % (
            self._get_rel_for_gender(
                Ga, Gb, MALE, step, in_law_a, in_law_b, family_connection),
            self._get_rel_for_gender(
                Ga, Gb, FEMALE, step, in_law_a, in_law_b, family_connection),
        )

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
        """Spanish version of get_plural_relationship_string."""

        PLURAL_KEY = "PLURAL"

        if Ga == 0:
            if Gb < len(_descendant_plural) and _descendant_plural[Gb]:
                rel_str = _descendant_plural[Gb]
            elif (Gb - 1) < len(_ordinal_plural):
                rel_str = "%s nietos" % _ordinal_plural[Gb - 1]
            else:
                rel_str = "%d-ésimos nietos" % (Gb - 1)
            rel_str = _pluralize_gender(rel_str)

        elif Gb == 0:
            if Ga < len(_ancestor_plural) and _ancestor_plural[Ga]:
                rel_str = _ancestor_plural[Ga]
            elif (Ga - 1) < len(_ordinal_plural):
                rel_str = "%s abuelos" % _ordinal_plural[Ga - 1]
            else:
                rel_str = "%d-ésimos abuelos" % (Ga - 1)
            rel_str = _pluralize_gender(rel_str)

        elif Ga == Gb:
            if Ga == 1 and (in_law_a or in_law_b):
                rel_str = "concuñados" if (in_law_a and in_law_b) else "cuñados"
            elif Ga == 1 and (_has_family_marker(reltocommon_a) or
                              _has_family_marker(reltocommon_b)):
                rel_str = "consuegros"
            elif Ga == 1:
                rel_str = "hermanos/as"
            elif Ga == 2:
                rel_str = "primos/as hermanos/as"
            elif (Ga - 1) < len(_ordinal_plural):
                rel_str = "primos/as %s" % _pluralize_gender(_ordinal_plural[Ga - 1])
            else:
                rel_str = "primos/as %d-ésimos/as" % (Ga - 1)

        elif Ga > Gb:
            base = _get_ancestor_base(Ga - Gb, PLURAL_KEY)
            level_ord = _get_ancestor_level_ordinal(Ga - Gb, PLURAL_KEY)
            lateral_ord = _get_ordinal(Gb, PLURAL_KEY)
            parts = []
            if level_ord:
                parts.append(_pluralize_gender(level_ord))
            parts.append("tíos/as")
            if base:
                parts.append(_pluralize_gender(base))
            if lateral_ord:
                parts.append(_pluralize_gender(lateral_ord))
            rel_str = " ".join(parts)

        elif Gb > Ga:
            base = _get_descendant_base(Gb - Ga, PLURAL_KEY)
            lateral_ord = _get_ordinal(Ga, PLURAL_KEY)
            parts = ["sobrinos/as"]
            if base:
                parts.append(_pluralize_gender(base))
            if lateral_ord:
                parts.append(_pluralize_gender(lateral_ord))
            rel_str = " ".join(parts)

        else:
            rel_str = "parientes lejanos"

        if in_law_b:
            rel_str = "cónyuges de los %s" % rel_str

        return rel_str

    def get_sibling_relationship_string(
        self, sib_type, gender_a, gender_b, in_law_a=False, in_law_b=False
    ):
        """Spanish version of get_sibling_relationship_string."""

        inlaw = in_law_a or in_law_b
        rel_str = ""

        if gender_b != FEMALE:
            if sib_type == self.NORM_SIB or sib_type == self.UNKNOWN_SIB:
                rel_str = "hermano"
            elif sib_type in (self.HALF_SIB_MOTHER, self.HALF_SIB_FATHER):
                rel_str = "medio hermano"
            elif sib_type == self.STEP_SIB:
                rel_str = "hermanastro"
            if inlaw:
                rel_str += " político"

        if gender_b == UNKNOWN:
            rel_str += " o "

        if gender_b != MALE:
            if sib_type == self.NORM_SIB or sib_type == self.UNKNOWN_SIB:
                rel_str += "hermana"
            elif sib_type in (self.HALF_SIB_MOTHER, self.HALF_SIB_FATHER):
                rel_str += "medio hermana"
            elif sib_type == self.STEP_SIB:
                rel_str += "hermanastra"
            if inlaw:
                rel_str += " política"

        return rel_str

    def get_partner_relationship_string(self, spouse_type, gender_a, gender_b):
        """Spanish version of get_partner_relationship_string.

        Uses a declarative lookup table (_PARTNER_TERMS) instead of
        if/elif chains.
        """
        if not spouse_type:
            return ""
        entry = _PARTNER_TERMS.get(spouse_type)
        if entry is None:
            return _pick_gender("expareja", "expareja", gender_b)
        return entry.get(gender_b, entry.get(MALE, "expareja"))


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

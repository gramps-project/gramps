# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2005  Donald N. Allingham
# Copyright (C) 2008       Stefan Siegel
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

# Original version written by Alex Roitman, largely based on Relationship.py
# by Don Allingham and on valuable input from Dr. Martin Senftleben
# Modified by Joachim Breitner to not use „Großcousine“, in accordance with
# http://de.wikipedia.org/wiki/Verwandtschaftsbeziehung
# Rewritten from scratch for GRAMPS 3 by Stefan Siegel,
# loosely based on rel_fr.py

#-------------------------------------------------------------------------
#
# standard python modules
#
#-------------------------------------------------------------------------

import re

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------

import gen.lib
import Relationship
from PluginUtils import register_relcalc

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------

_ordinal = [ u'nullte',
    u'erste', u'zweite', u'dritte', u'vierte', u'fünfte', u'sechste',
    u'siebte', u'achte', u'neunte', u'zehnte', u'elfte', u'zwölfte',
]

_removed = [ u'',
    u'', u'Groß', u'Urgroß',
    u'Alt', u'Altgroß', u'Alturgroß',
    u'Ober', u'Obergroß', u'Oberurgroß',
    u'Stamm', u'Stammgroß', u'Stammurgroß',
    u'Ahnen', u'Ahnengroß', u'Ahnenurgroß',
    u'Urahnen', u'Urahnengroß', u'Urahnenurgroß',
    u'Erz', u'Erzgroß', u'Erzurgroß',
    u'Erzahnen', u'Erzahnengroß', u'Erzahnenurgroß',
]

_lineal_up = {
    'many':    u'%(p)sEltern%(s)s',
    'unknown': u'%(p)sElter%(s)s', # "Elter" sounds strange but is correct
    'male':    u'%(p)sVater%(s)s',
    'female':  u'%(p)sMutter%(s)s',
}
_lineal_down = {
    'many':    u'%(p)sKinder%(s)s',
    'unknown': u'%(p)sKind%(s)s',
    'male':    u'%(p)sSohn%(s)s',
    'female':  u'%(p)sTochter%(s)s',
}
_collateral_up = {
    'many':    u'%(p)sOnkel und %(p)sTanten%(s)s',
    'unknown': u'%(p)sOnkel oder %(p)sTante%(s)s',
    'male':    u'%(p)sOnkel%(s)s',
    'female':  u'%(p)sTante%(s)s',
}
_collateral_down = {
    'many':    u'%(p)sNeffen und %(p)sNichten%(s)s',
    'unknown': u'%(p)sNeffe oder %(p)sNichte%(s)s',
    'male':    u'%(p)sNeffe%(s)s',
    'female':  u'%(p)sNichte%(s)s',
}
_collateral_same = {
    'many':    u'%(p)sCousins und %(p)sCousinen%(s)s',
    'unknown': u'%(p)sCousin oder %(p)sCousine%(s)s',
    'male':    u'%(p)sCousin%(s)s',
    'female':  u'%(p)sCousine%(s)s',
}
_collateral_sib = {
    'many':    u'%(p)sGeschwister%(s)s',
    'unknown': u'%(p)sGeschwisterkind%(s)s',
    'male':    u'%(p)sBruder%(s)s',
    'female':  u'%(p)sSchwester%(s)s',
}

_schwager = {
    'many':    u'%(p)sSchwager%(s)s',
    'unknown': u'%(p)sSchwager%(s)s',
    'male':    u'%(p)sSchwager%(s)s',
    'female':  u'%(p)sSchwägerin%(s)s',
}
_schwippschwager = {
    'many':    u'%(p)sSchwippschwager%(s)s',
    'unknown': u'%(p)sSchwippschwager%(s)s',
    'male':    u'%(p)sSchwippschwager%(s)s',
    'female':  u'%(p)sSchwippschwägerin%(s)s',
}

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------

class RelationshipCalculator(Relationship.RelationshipCalculator):
    def __init__(self):
        Relationship.RelationshipCalculator.__init__(self)

    def _make_roman(self, num):
        roman = ''
        for v, r in [(1000, u'M'), (900, u'CM'), (500, u'D'), (400, u'CD'),
                     ( 100, u'C'), ( 90, u'XC'), ( 50, u'L'), ( 40, u'XL'),
                     (  10, u'X'), (  9, u'IX'), (  5, u'V'), (  4, u'IV'),
                     (   1, u'I')]:
            while num > v:
                num -= v
                roman += r
        return roman

    def _fix_caps(self, string):
        return re.sub(r'(?<=[^\s(/A-Z])[A-Z]', lambda m: m.group().lower(), string)

    def _removed_text(self, degree, removed):
        if (degree, removed) == (0, -2):
            return u'Enkel'
        elif (degree, removed) == (0, -3):
            return u'Urenkel'
        removed = abs(removed)
        if removed < len(_removed):
            return _removed[removed]
        else:
            return u'(%s)' % self._make_roman(removed-2)

    def _degree_text(self, degree, removed):
        if removed == 0:
            degree -= 1  # a cousin has same degree as his parent (uncle/aunt)
        if degree <= 1:
            return u''
        if degree < len(_ordinal):
            return u' %sn Grades' % _ordinal[degree]
        else:
            return u' %d. Grades' % degree

    def _gender_convert(self, gender):
        if gender == gen.lib.Person.MALE:
            return 'male'
        elif gender == gen.lib.Person.FEMALE:
            return 'female'
        else:
            return 'unknown'

    def _get_relationship_string(self, Ga, Gb, gender,
                                 reltocommon_a='', reltocommon_b='',
                                 only_birth=True,
                                 in_law_a=False, in_law_b=False):
        common_ancestor_count = 0
        if reltocommon_a == '':
            reltocommon_a = self.REL_FAM_BIRTH
        if reltocommon_b == '':
            reltocommon_b = self.REL_FAM_BIRTH
        if reltocommon_a[-1] in [self.REL_MOTHER, self.REL_FAM_BIRTH,
                                 self.REL_FAM_BIRTH_MOTH_ONLY] and \
           reltocommon_b[-1] in [self.REL_MOTHER, self.REL_FAM_BIRTH,
                                 self.REL_FAM_BIRTH_MOTH_ONLY]:
            common_ancestor_count += 1  # same female ancestor
        if reltocommon_a[-1] in [self.REL_FATHER, self.REL_FAM_BIRTH,
                                 self.REL_FAM_BIRTH_FATH_ONLY] and \
           reltocommon_b[-1] in [self.REL_FATHER, self.REL_FAM_BIRTH,
                                 self.REL_FAM_BIRTH_FATH_ONLY]:
            common_ancestor_count += 1  # same male ancestor

        degree = min(Ga, Gb)
        removed = Ga-Gb

        if degree == 0 and removed < 0:
            # for descendants the "in-law" logic is reversed
            (in_law_a, in_law_b) = (in_law_b, in_law_a) 

        rel_str = u''
        pre = u''
        post = u''

        if in_law_b and degree == 0:
            pre += u'Stief'
        elif (not only_birth) or common_ancestor_count == 0:
            pre += u'Stief-/Adoptiv'
        if in_law_a and (degree, removed) != (1, 0):
            # A "Schwiegerbruder" really is a "Schwager" (handled later)
            pre += u'Schwieger'
        if degree != 0 and common_ancestor_count == 1:
            pre += u'Halb'
        pre += self._removed_text(degree, removed)
        post += self._degree_text(degree, removed)
        if in_law_b and degree != 0 and (degree, removed) != (1, 0):
            # A "Bruder (angeheiratet)" also is a "Schwager" (handled later)
            post += u' (angeheiratet)'

        if degree == 0:
            # lineal relationship
            if removed > 0:
                rel_str = _lineal_up[gender]
            elif removed < 0:
                rel_str = _lineal_down[gender]
            else:
                rel_str = u'Proband'
        else:
            # collateral relationship
            if removed > 0:
                rel_str = _collateral_up[gender]
            elif removed < 0:
                rel_str = _collateral_down[gender]
            elif degree == 1:
                if in_law_a or in_law_b:
                    if in_law_a and in_law_b:
                        rel_str = _schwippschwager[gender]
                    else:
                        rel_str = _schwager[gender]
                else:
                    rel_str = _collateral_sib[gender]
            else:
                rel_str = _collateral_same[gender]
        return self._fix_caps(rel_str % {'p': pre, 's': post})

    def get_plural_relationship_string(self, Ga, Gb):
        return self._get_relationship_string(Ga, Gb, 'many')

    def get_single_relationship_string(self, Ga, Gb, gender_a, gender_b,
                                       reltocommon_a, reltocommon_b,
                                       only_birth=True,
                                       in_law_a=False, in_law_b=False):
        return self._get_relationship_string(Ga, Gb,
                                             self._gender_convert(gender_b),
                                             reltocommon_a, reltocommon_b,
                                             only_birth, in_law_a, in_law_b)

    def get_sibling_relationship_string(self, sib_type, gender_a, gender_b, 
                                        in_law_a=False, in_law_b=False):
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
        return self._get_relationship_string(1, 1,
                                             self._gender_convert(gender_b),
                                             rel, rel,
                                             only_birth, in_law_a, in_law_b)

#-------------------------------------------------------------------------
#
# Register this class with the Plugins system 
#
#-------------------------------------------------------------------------

register_relcalc(RelationshipCalculator,
    ["de","DE","de_DE","deutsch","Deutsch","de_DE.UTF8","de_DE@euro","de_DE.UTF8@euro",
            "german","German", "de_DE.UTF-8", "de_DE.utf-8", "de_DE.utf8"])

if __name__ == "__main__":
    # Test function. Call it as follows from the command line (so as to find
    #        imported modules):
    #    export PYTHONPATH=/path/to/gramps/src 
    # python src/plugins/rel_fr.py 
    # (Above not needed here)

    """TRANSLATORS, copy this if statement at the bottom of your 
        rel_xx.py module, and test your work with:
        python src/plugins/rel_xx.py
    """
    from Relationship import test
    rc = RelationshipCalculator()
    test(rc, True)

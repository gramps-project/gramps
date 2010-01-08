# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2005  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2009-2010  Andrew I Baznikin
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

# $Id:rel_ru.py 9912 2008-01-22 09:17:46Z acraphae $

# Written by Alex Roitman, largely based on Relationship.py by Don Allingham.
"""
Russian-specific definitions of relationships
"""
#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------

import gen.lib
import Relationship

#-------------------------------------------------------------------------

_parents_level = [
  u"",
  u"родители",
  u"дедушки/бабушки",
  u"прадедушки/прабабушки",
  u"прапрадедушки/прапрабабушки (5 поколение)",
  u"прапрапрадедушки/прапрапрабабушки (6 поколение)",
  u"прапрапрапрадедушки/прапрапрапрабабушки (7 поколение)",
  u"прапрапрапрапрадедушки/прапрапрапрапрабабушки (8 поколение)",
  ]

_male_cousin_level = [ 
  u"", 
  u"двоюродный", 
  u"троюродный", 
  u"четвероюродный",
  u"пятиюродный", 
  u"шестиюродный", 
  u"семиюродный", 
  u"восьмиюродный",
  u"девятиюродный", 
  u"десятиюродный", 
  u"одиннацатиюродный", 
  u"двенадцатиюродный", 
  u"тринадцатиюродный", 
  u"четырнадцатиюродный", 
  u"пятнадцатиюродный", 
  u"шестнадцатиюродный", 
  u"семнадцатиюродный", 
  u"восемнадцатиюродный", 
  u"девятнадцатиюродный", 
  u"двадцатиюродный", 
  ]

_female_cousin_level = [ 
  u"", 
  u"двоюродная", 
  u"троюродная", 
  u"четвероюродная",
  u"пятиюродная", 
  u"шестиюродная", 
  u"семиюродная", 
  u"восьмиюродная",
  u"девятиюродная", 
  u"десятиюродная", 
  u"одиннацатиюродная", 
  u"двенадцатиюродная", 
  u"тринадцатиюродная", 
  u"четырнадцатиюродная", 
  u"пятнадцатиюродная", 
  u"шестнадцатиюродная", 
  u"семнадцатиюродная", 
  u"восемнадцатиюродная", 
  u"девятнадцатиюродная", 
  u"двадцатиюродная", 
  ]

_cousin_level = [ 
  u"",
  u"двоюродные", 
  u"троюродные", 
  u"четвероюродные",
  u"пятиюродные", 
  u"шестиюродные", 
  u"семиюродные", 
  u"восьмиюродные",
  u"девятиюродные", 
  u"десятиюродные",
  u"одиннацатиюродные", 
  u"двенадцатиюродные",
  u"тринадцатиюродные", 
  u"четырнадцатиюродные", 
  u"пятнадцатиюродные", 
  u"шестнадцатиюродные", 
  u"семнадцатиюродные", 
  u"восемнадцатиюродные", 
  u"девятнадцатиюродные", 
  u"двадцатиюродные", 
  ]

_junior_male_removed_level = [ 
  u"брат", 
  u"племянник", 
  u"внучатый племянник", 
  u"правнучатый племянник", 
  u"праправнучатый племянник", 
  u"прапраправнучатый племянник", 
  u"прапрапраправнучатый племянник", 
  ]

_junior_female_removed_level = [ 
  u"сестра", 
  u"племянница", 
  u"внучатая племянница", 
  u"правнучатая племянница", 
  u"праправнучатая племянница", 
  u"прапраправнучатая племянница", 
  u"прапрапраправнучатая племянница", 
  ]

_juniors_removed_level = [ 
  u"братя/сестры", 
  u"племянники", 
  u"внучатые племянники", 
  u"правнучатые племянники", 
  u"праправнучатые племянники", 
  u"прапраправнучатые племянники", 
  u"прапрапраправнучатые племянники", 
  ]

_senior_male_removed_level = [ 
  u"", 
  u"дядя", 
  u"дед", 
  u"прадед", 
  u"прапрадед", 
  u"прапрапрадед", 
  u"прапрапрапрадед", 
  ]

_senior_female_removed_level = [ 
  u"", 
  u"тётка", 
  u"бабка", 
  u"прабабка", 
  u"прапрабабка", 
  u"прапрапрабабка", 
  u"прапрапрапрабабка", 
  ]

_seniors_removed_level = [ 
  u"", 
  u"дядьки/тётки", 
  u"дедушки/бабушки", 
  u"прадеды/прабабушки", 
  u"прапрадеды/прапрабабушки", 
  u"прапрапрадеды/прапрапрабабушки", 
  u"прапрапрапрадеды/прапрапрабабушки", 
  ]

_father_level = [ 
  u"", 
  u"отец", 
  u"дед", 
  u"прадед", 
  u"прапрадед", 
  u"прапрапрадед", 
  u"прапрапрапрадед", 
  ]

_mother_level = [ 
   u"", 
   u"мать", 
   u"бабка", 
   u"прабабка", 
   u"прапрабабка", 
   u"прапрапрабабка", 
   u"прапрапрапрабабка", 
   ]

_son_level = [ 
  u"", 
  u"сын", 
  u"внук", 
  u"правнук", 
  u"праправнук", 
  u"прапраправнук", 
  u"прапрапраправнук", 
  ]

_daughter_level = [ 
  u"", 
  u"дочь", 
  u"внучка", 
  u"правнучка", 
  u"праправнучка", 
  u"прапраправнучка", 
  u"прапрапраправнучка", 
  ]

_children_level = [ 
 u"", 
 u"дети", 
 u"внуки", 
 u"правнуки", 
 u"праправнуки", 
 u"прапраправнуки", 
 u"прапрапраправнуки", 
 u"прапрапрапраправнуки",
 ]

_sister_level = [ 
  u"", 
  u"сестра", 
  u"тётка", 
  u"двоюродная бабка", 
  u"двоюродная прабабка", 
  u"двоюродная прапрабабка", 
  u"двоюродная прапрапрабабка", 
  u"двоюродная прапрапрапрабабка", 
  ]

_brother_level = [ 
  u"", 
  u"брат", 
  u"дядя", 
  u"двоюродный дед", 
  u"двоюродный прадед", 
  u"двоюродный прапрадед", 
  u"двоюродный прапрапрадед", 
  u"двоюродный прапрапрапрадед", 
  ]

_siblings_level = [ 
  u"", 
  u"братья/сестры", 
  u"дядьки/тётки", 
  u"двоюродные дедушки/бабушки", 
  u"двоюродные прадедеды/прабабушки", 
  u"двоюродные прапрадедушки/прапрабабушки (5 поколение)", 
  u"двоюродные прапрапрадедушки/прапрапрабабушки (6 поколение)",
  u"двоюродные прапрапрапрадедушки/прапрапрапрабабушки (7 поколение)",
  u"двоюродные прапрапрапрапрадедушки/прапрапрапрапрабабушки (8 поколение)",
  ]

_nephew_level = [ 
  u"", 
  u"племянник", 
  u"внучатый племянник", 
  u"правнучатый племянник", 
  u"праправнучатый племянник", 
  u"прапраправнучатый племянник", 
  u"прапрапраправнучатый племянник", 
  ]

_niece_level = [ 
  u"", 
  u"племянница", 
  u"внучатая племянница", 
  u"правнучатая племянница", 
  u"праправнучатая племянница", 
  u"прапраправнучатая племянница", 
  u"прапрапраправнучатая племянница", 
  ]

_nephews_nieces_level = [
  u"", 
  u"братья/сестры", 
  u"племянники", 
  u"внучатый племянники", 
  u"правнучатый племянники", 
  u"праправнучатый племянники", 
  u"прапраправнучатый племянники", 
  u"прапрапраправнучатый племянники", 
  ]

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class RelationshipCalculator(Relationship.RelationshipCalculator):
    """
    RelationshipCalculator Class
    """

    def __init__(self):
        Relationship.RelationshipCalculator.__init__(self)

    def get_parents(self, level):
        if level > len(_parents_level)-1:
            return u"дальние родственники"
        else:
            return _parents_level[level]

    def get_junior_male_cousin(self, level, removed):
        if removed > len(_junior_male_removed_level)-1 or \
        level > len(_male_cousin_level)-1:
            return u"дальний родственник"
        else:
            return u"%s %s" % (_male_cousin_level[level], _junior_male_removed_level[removed])

    def get_senior_male_cousin(self, level, removed):
        if removed > len(_senior_male_removed_level)-1 or \
        level > len(_male_cousin_level)-1:
            return u"дальний родственник"
        else:
            return u"%s %s" % (_male_cousin_level[level], _senior_male_removed_level[removed])

    def get_junior_female_cousin(self, level, removed):
        if removed > len(_junior_female_removed_level)-1 or \
        level > len(_male_cousin_level)-1:
            return u"дальняя родственница"
        else:
            return u"%s %s" % (_female_cousin_level[level], _junior_female_removed_level[removed])

    def get_senior_female_cousin(self, level, removed):
        if removed > len(_senior_female_removed_level)-1 or \
        level > len(_male_cousin_level)-1:
            return u"дальняя родственница"
        else:
            return u"%s %s" % (_female_cousin_level[level], _senior_female_removed_level[removed])

    def get_father(self, level):
        if level > len(_father_level)-1:
            return u"дальний предок"
        else:
            return _father_level[level]

    def get_son(self, level):
        if level > len(_son_level)-1:
            return u"дальний потомок"
        else:
            return _son_level[level]

    def get_mother(self, level):
        if level > len(_mother_level)-1:
            return u"дальний предок"
        else:
            return _mother_level[level]

    def get_daughter(self, level):
        if level > len(_daughter_level)-1:
            return u"дальний потомок"
        else:
            return _daughter_level[level]

    def _get_aunt(self, level, step='', inlaw=''):
        if level > len(_sister_level)-1:
            return u"дальний предок"
        else:
            return _sister_level[level]

    def _get_uncle(self, level, step='', inlaw=''):
        if level > len(_brother_level)-1:
            return u"дальний предок"
        else:
            return _brother_level[level]

    def _get_sibling(self, level, step='', inlaw=''):
        """
        Sibling of unknown gender
        """
        return self._get_uncle(level, step, inlaw) + u" или u" + self._get_aunt(level, step, inlaw)

    def get_nephew(self, level):
        if level > len(_nephew_level)-1:
            return u"дальний потомок"
        else:
            return _nephew_level[level]

    def get_niece(self, level):
        if level > len(_niece_level)-1:
            return u"дальний потомок"
        else:
            return _niece_level[level]

    def get_single_relationship_string(self, Ga, Gb, gender_a, gender_b,
                                       reltocommon_a, reltocommon_b,
                                       only_birth=True, 
                                       in_law_a=False, in_law_b=False):

        if Gb == 0:
            if Ga == 0:
                return ('один человек')
            elif gender_b == gen.lib.Person.MALE:
                return (self.get_father(Ga))
            else:
                return (self.get_mother(Ga))
        elif Ga == 0:
            if gender_b == gen.lib.Person.MALE:
                return (self.get_son(Gb))
            else:
                return (self.get_daughter(Gb))
        elif Gb == 1:
            if gender_b == gen.lib.Person.MALE:
                return (self._get_uncle(Ga))
            else:
                return (self._get_aunt(Ga))
        elif Ga == 1:
            if gender_b == gen.lib.Person.MALE:
                return (self.get_nephew(Gb-1))
            else:
                return (self.get_niece(Gb-1))
        elif Ga > Gb:
            if gender_b == gen.lib.Person.MALE:
                return (self.get_senior_male_cousin(Gb-1, Ga-Gb))
            else:
                return (self.get_senior_female_cousin(Gb-1, Ga-Gb))
        else:
            if gender_b == gen.lib.Person.MALE:
                return (self.get_junior_male_cousin(Ga-1, Gb-Ga))
            else:
                return (self.get_junior_female_cousin(Ga-1, Gb-Ga))


    def get_plural_relationship_string(self, Ga, Gb):
        rel_str = u"дальние родственники"
        if Ga == 0:
            # These are descendants
            if Gb < len(_children_level):
                rel_str = _children_level[Gb]
            else:
                rel_str = u"дальние потомки"
        elif Gb == 0:
            # These are parents/grand parents
            if Ga < len(_parents_level):
                rel_str = _parents_level[Ga]
            else:
                rel_str = u"дальние предки"
        elif Gb == 1:
            # These are siblings/aunts/uncles
            if Ga < len(_siblings_level):
                rel_str = _siblings_level[Ga]
            else:
                rel_str = u"дальние дяди/тёти"
        elif Ga == 1:
            # These are nieces/nephews
            if Gb < len(_nephews_nieces_level):
                rel_str = _nephews_nieces_level[Gb]
            else:
                rel_str = u"дальние племянники/племянницы"
        elif Ga > Gb:
            # These are cousins in different generations with the second person 
            # being in a higher generation from the common ancestor than the 
            # first person.
            if Gb <= len(_seniors_removed_level) and (Ga-Gb) < len(_cousin_level):
                rel_str = u"%s %s" % ( _cousin_level[Gb-1], 
                                                  _seniors_removed_level[Ga-Gb] )
            else:
                rel_str =  u"(старшие) дальние родственники"
        else:
            # These are cousins in different generations with the second person 
            # being in a lower generation from the common ancestor than the 
            # first person.
            if Ga <= len(_juniors_removed_level) and (Gb-Ga) < len(_cousin_level):
                rel_str = u"%s %s" % ( _cousin_level[Ga-1], 
                                                    _juniors_removed_level[Gb-Ga] )
            else:
                rel_str =  u"(младшие) дальние родственники"
        return rel_str

# TODO: def get_sibling_relationship_string for Russian step and inlaw relations

if __name__ == "__main__":

    # Test function. Call it as follows from the command line (so as to find
    #        imported modules):
    #    export PYTHONPATH=/path/to/gramps/src
    # python src/plugins/rel/rel_ru.py
    # (Above not needed here)

    """TRANSLATORS, copy this if statement at the bottom of your 
        rel_xx.py module, and test your work with:
        python src/plugins/rel/rel_xx.py
    """
    from Relationship import test
    RC = RelationshipCalculator()
    test(RC, True)

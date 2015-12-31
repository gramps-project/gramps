# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2005  Donald N. Allingham
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

# Rewritten in 2008 for 3.x version by Łukasz Rymarczyk
# Written in 2007 by Piotr Czubaszek, largely based on rel_de.py by Alex Roitman.

# PL: Po objaśnienia oznaczania relacji zobacz relationship.py
# EN: For more information see relationship.py
#
"""
Polish-specific definitions of relationships.
"""

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------

from gramps.gen.lib import Person
import gramps.gen.relationship

#-------------------------------------------------------------------------


# określa liczebnik porządkowy

_level_name = [ "pierwszego", "drugiego", "trzeciego", "czwartego", "piątego",
    "szóstego", "siódmego", "ósmego", "dziewiątego", "dziesiątego",
    "jedenastego", "dwunastego","trzynastego", "czternastego", "piętnastego",
    "szesnastego", "siedemnastego", "osiemnastego","dziewiętnastego", "dwudziestego", ]


_father_level = [ "",
  "ojciec",
  "dziadek",
  "pradziadek",
  "prapradziadek",
  "praprapradziadek",
  "prapraprapradziadek",
  "praprapraprapradziadek",
  "prapraprapraprapradziadek",
  "praprapraprapraprapradziadek",
  "prapraprapraprapraprapradziadek",
]


_mother_level = [ "",
  "matka",
  "babcia",
  "prababcia",
  "praprababcia",
  "prapraprababcia",
  "praprapraprababcia",
  "prapraprapraprababcia",
  "praprapraprapraprababcia",
  "prapraprapraprapraprababcia",
  "praprapraprapraprapraprababcia",
]

_son_level = [ "",
  "syn",
  "wnuk",
  "prawnuk",
  "praprawnuk",
  "prapraprauwnuk",
  "praprapraprauwnuk",
  "prapraprapraprawnuk",
  "praprapraprapraprawnuk",
  "prapraprapraprapraprawnuk",
  "praprapraprapraprapraprawnuk",
]

_daughter_level = [ "",
  "córka",
  "wnuczka",
  "prawnuczka",
  "praprawnuczka",
  "prapraprauwnuczka",
  "praprapraprauwnuczka",
  "prapraprapraprawnuczka",
  "praprapraprapraprawnuczka",
  "prapraprapraprapraprawnuczka",
  "praprapraprapraprapraprawnuczka",
]

_sister_level_of_male = [ "", "siostra", "ciotka stryjeczna",
  "babcia stryjeczna",
  "prababcia stryjeczna",
  "praprababcia stryjeczna",
  "prapraprababcia stryjeczna",
  "praprapraprababcia stryjeczna",
  "prapraprapraprababcia stryjeczna",
  "praprapraprapraprababcia stryjeczna",
  "prapraprapraprapraprababcia stryjeczna",
  "praprapraprapraprapraprababcia stryjeczna",
]

_sister_level_of_female = [ "", "siostra", "ciotka",
  "babcia cioteczna",
  "prababcia cioteczna",
  "praprababcia cioteczna",
  "prapraprababcia cioteczna",
  "praprapraprababcia cioteczna",
  "prapraprapraprababcia cioteczna",
  "praprapraprapraprababcia cioteczna",
  "prapraprapraprapraprababcia cioteczna",
  "praprapraprapraprapraprababcia cioteczna",
]

_brother_level_of_male = [ "", "brat", "stryj",
  "dziadek stryjeczny",
  "pradziadek stryjeczny",
  "prapradziadek stryjeczny",
  "praprapradziadek stryjeczny",
  "prapraprapradziadek stryjeczny",
  "praprapraprapradziadek stryjeczny",
  "prapraprapraprapradziadek stryjeczny",
  "praprapraprapraprapradziadek stryjeczny",
  "prapraprapraprapraprapradziadek stryjeczny",
]

_brother_level_of_female = [ "", "brat", "wuj",
  "dziadek cioteczny",
  "pradziadek cioteczny",
  "prapradziadek cioteczny",
  "praprapradziadek cioteczny",
  "prapraprapradziadek cioteczny",
  "praprapraprapradziadek cioteczny",
  "prapraprapraprapradziadek cioteczny",
  "praprapraprapraprapradziadek cioteczny",
  "prapraprapraprapraprapradziadek cioteczny",
]

_nephew_level_of_brothers_son = [ "", "bratanek",
  "syn bratanka",
  "wnuk bratanka",
  "prawnuk bratanka",
  "praprawnuk bratanka",
  "prapraprawnuk bratanka",
  "praprapraprawnuk bratanka",
  "prapraprapraprawnuk bratanka",
  "praprapraprapraprawnuk bratanka",
  "prapraprapraprapraprawnuk bratanka",
]

_nephew_level_of_brothers_daughter = [ "", "bratanica",
  "syn bratanicy",
  "wnuk bratanicy",
  "prawnuk bratanicy",
  "praprawnuk bratanicy",
  "prapraprawnuk bratanicy",
  "praprapraprawnuk bratanicy",
  "prapraprapraprawnuk bratanicy",
  "praprapraprapraprawnuk bratanicy",
  "prapraprapraprapraprawnuk bratanicy",
  "praprapraprapraprapraprawnuk bratanicy",
]

_nephew_level_of_sisters_son = [ "", "siostrzeniec",
  "syn siostrzeńca",
  "wnuk siostrzeńca",
  "prawnuk siostrzeńca",
  "praprawnuk siostrzeńca",
  "prapraprawnuk siostrzeńca",
  "praprapraprawnuk siostrzeńca",
  "prapraprapraprawnuk siostrzeńca",
  "praprapraprapraprawnuk siostrzeńca",
  "prapraprapraprapraprawnuk siostrzeńca",
]

_nephew_level_of_sisters_daughter = [ "", "siostrzenica",
  "syn siostrzenicy",
  "wnuk siostrzenicy",
  "prawnuk siostrzenicy",
  "praprawnuk siostrzenicy",
  "prapraprawnuk siostrzenicy",
  "praprapraprawnuk siostrzenicy",
  "prapraprapraprawnuk siostrzenicy",
  "praprapraprapraprawnuk siostrzenicy",
  "prapraprapraprapraprawnuk siostrzenicy",
]

_niece_level_of_brothers_son = [ "", "bratanica",
  "córka bratanka",
  "wnuczka bratanka",
  "prawnuczka bratanka",
  "praprawnuczka bratanka",
  "prapraprawnuczka bratanka",
  "praprapraprawnuczka bratanka",
  "prapraprapraprawnuczka bratanka",
  "praprapraprapraprawnuczka bratanka",
]

_niece_level_of_brothers_daughter = [ "", "bratanica",
  "córka bratanicy",
  "wnuczka bratanicy",
  "prawnuczka bratanicy",
  "praprawnuczka bratanicy",
  "prapraprawnuczka bratanicy",
  "praprapraprawnuczka bratanicy",
  "prapraprapraprawnuczka bratanicy",
  "praprapraprapraprawnuczka bratanicy",
]

_niece_level_of_sisters_son = [ "", "siostrzenica",
  "córka siostrzeńca",
  "wnuczka siostrzeńca",
  "prawnuczka siostrzeńca",
  "praprawnuczka siostrzeńca",
  "prapraprawnuczka siostrzeńca",
  "praprapraprawnuczka siostrzeńca",
  "prapraprapraprawnuczka siostrzeńca",
  "praprapraprapraprawnuczka siostrzeńca",
]

_niece_level_of_sisters_daughter = [ "", "siostrzenica",
  "córka siostrzenicy",
  "wnuczka siostrzenicy",
  "prawnuczka siostrzenicy",
  "praprawnuczka siostrzenicy",
  "prapraprawnuczka siostrzenicy",
  "praprapraprawnuczka siostrzenicy",
  "prapraprapraprawnuczka siostrzenicy",
  "praprapraprapraprawnuczka siostrzenicy",
]

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

    def get_son(self, level, inlaw=''):
        """
        Podaje tekst zawierający informację, jak bardzo potomek męski
        (np. syn) jest spokrewniony do danej osoby
        """

        # Określ, czy osoba jest przybraną, czy rodzoną
        if inlaw == '':
            t_inlaw = ""
        else:
            t_inlaw = "przybrany "

        # TODO: dodać rozpoznawanie pasierb/pasierbica
        if level >= 0 and level < len(_son_level):
            return t_inlaw +_son_level[level]

        elif level >= len(_son_level) and (level - 1) < len(_level_name):
            return t_inlaw + \
                "potomek męski %s pokolenia" % _level_name[level - 1]

        else:
            return t_inlaw + \
                "potomek męski w %d pokoleniu" % level



    def get_daughter(self, level, inlaw=''):
        """
        Podaje tekst zawierający informację, jak bardzo potomek żeński
        (np. córka) jest spokrewniony do danej osoby
        """

        # Określ, czy osoba jest przybraną, czy rodzoną
        #   + stwórz obie formy (męską i żeńską)
        if inlaw == '':
            t_inlaw = ""
            t_inlawM = ""
        else:
            t_inlaw = "przybrana "
            t_inlawM = "przybrany "

        # TODO: dodać rozpoznawanie pasierb/pasierbica
        if level >= 0 and level < len(_daughter_level):
            return t_inlaw + _daughter_level[level]

        elif level >= len(_daughter_level) and (level - 1) < len(_level_name):
            return t_inlawM + \
                    "potomek żeński %s pokolenia" % _level_name[level - 1]
        else:
            return t_inlawM + \
                    "potomek żeński w %d pokoleniu" % level


    def get_child_unknown(self, level, inlaw=''):
        """
        Podaje tekst zawierający informację, jak bardzo potomek
        o nieokreślonej płci jest spokrewniony dodanej osoby
        """

        # Określ, czy osoba jest przybraną, czy rodzoną
        if inlaw == '':
            t_inlaw = ""
        else:
            t_inlaw = "przybrany "

        if level == 1:
            if inlaw == '' :
                return "dziecko"
            else:
                return "przybrane dziecko"

        elif level >= 1 and  (level - 1) < len(_level_name):
            return t_inlaw + "potomek %s pokolenia" %  _level_name[level - 1]

        else:
            return t_inlaw + "potomek w %d pokoleniu" % level


    def get_sword_distaff(self, level, reltocommon, spacebefore = ""):
        """
        PL: Generuje relację po mieczu/po kądzieli
        EN: Generate relation 'by sword' or 'by distaff', polish specific
        """
        if level <= 1:
            return ""

        elif level == 2:
            # dziadek/babcia

            if reltocommon[0] == self.REL_FATHER:
                # ze strony rodzonego ojca
                return spacebefore + "po mieczu"
            elif reltocommon[0] == self.REL_MOTHER:
                # ze strony rodzonej matki
                return spacebefore + "po kądzieli"
            else:
                # relacja inna niż rodzona
                return ""

        elif level == 3:
            # pradziadek/prababcia

            if (reltocommon[0] == self.REL_FATHER) \
                & (reltocommon[1] == self.REL_FATHER):
                # pradziadek od dziadka ze strony ojca
                return spacebefore + "podwójnego miecza"

            elif (reltocommon[0] == self.REL_FATHER) \
                & (reltocommon[1] == self.REL_MOTHER):
                # pradziadek od babci ze strony ojca
                return spacebefore + "raz po mieczu, dalej po kądzieli"

            elif (reltocommon[0] == self.REL_MOTHER) \
                & (reltocommon[1] == self.REL_FATHER):
                # pradziadek od dziadka ze strony matki
                return spacebefore + "raz po kądzieli, dalej po mieczu"

            elif (reltocommon[0] == self.REL_MOTHER) \
                & (reltocommon[1] == self.REL_MOTHER):
                # pradziadek od babci ze strony matki
                return spacebefore + "podwójnej kądzieli"

            else:
                # relacja inna niż rodzona
                return ""

        elif level == 4:
            # prapradziadek/praprababcia

            if (reltocommon[0] == self.REL_FATHER) \
                & (reltocommon[1] == self.REL_FATHER) \
                & (reltocommon[2] == self.REL_FATHER):
                # tzw. linia męska
                return spacebefore + "potrójnego miecza"

            if (reltocommon[0] == self.REL_FATHER) \
                & (reltocommon[1] == self.REL_FATHER) \
                & (reltocommon[2] == self.REL_FATHER):
                # tzw. linia żeńska
                return spacebefore + "potrójnego miecza"

            else:
                return ""

        else:
            return ""



    def get_father(self, level, reltocommon, inlaw=''):
        """
        Podaje tekst zawierający informację, jak bardzo przodek męski
        (np. ojciec) jest spokrewniony do danej osoby
        """
        if inlaw == '':
            t_inlaw = ""
        else:
            t_inlaw = "przybrany "

        if level >= 0 and level < len(_father_level):
            # Jeśli znasz bezpośrednią nazwę relacji, to ją zastosuj

            if level == 1:
                # ojciec
                return t_inlaw + _father_level[level]

            elif (level >= 2) & (level <= 4):
                # dziadek, pradziadek, prapradziadek
                return t_inlaw + _father_level[level] \
                    + self.get_sword_distaff(level, reltocommon, ' ')

            else:
                return t_inlaw + _father_level[level]

        elif level >= len(_father_level) and (level - 1) < len(_level_name):
            # jeśli istnieje liczebnik dla danej liczby
            return t_inlaw + \
                    "przodek męski %s pokolenia" % (_level_name[level - 1])

        else:
            # dla pozostałych przypadków wypisz relację liczbowo
            return t_inlaw + \
                    "przodek męski w %d pokoleniu" % level


    def get_mother(self, level, reltocommon, inlaw=''):
        """
        Podaje tekst zawierający informację, jak bardzo przodek żeński
        (np. matka) jest spokrewniony do danej osoby
        """

        if inlaw == '':
            t_inlaw = ""
        else:
            t_inlaw = "przybrana "

        if level >= 0 and level < len(_mother_level):
            # Jeśli znasz bezpośrednią nazwę relacji, to ją zastosuj

            if level == 1:
                # matka
                return t_inlaw + _mother_level[level]

            elif (level >= 2) & (level <= 4):
                # babcia, prababcia, praprababcia
                return t_inlaw + _mother_level[level] \
                    + self.get_sword_distaff(level, reltocommon, ' ')

            else:
                return t_inlaw + _mother_level[level]

        elif level >= len(_mother_level) and (level - 1) < len(_level_name):
            # jeśli istnieje liczebnik dla danej liczby
            return t_inlaw + \
                    "przodek żeński %s pokolenia" % (_level_name[level - 1])

        else:
            # dla pozostałych przypadków wypisz relację liczbowo
            return t_inlaw +"przodek żeński w %d pokoleniu" % level



    def get_parent_unknown(self, level, inlaw=''):
        """
        Podaje tekst zawierający informację, jak bardzo przodek
        o nieokreślonej płci jest spokrewniony dodanej osoby
        """

        if inlaw == '':
            t_inlaw = ""
        else:
            t_inlaw = "przybrany "

        if level == 1:
            return t_inlaw + "rodzic"

        elif level > 1 and (level - 1) < len(_level_name):
            if (level >= 2) & (level <= 4):
                # babcia, prababcia, praprababcia
                # (albo dziadek, pradziadek, prapradziadek)
                tmp = t_inlaw +\
                    "przodek %s pokolenia" % (_level_name[level - 1])
                # TODO: try to recognize a gender...
                return tmp
                # +  self.get_sword_distaff(level, reltocommon, ' ')
            else:
                return t_inlaw + \
                   "przodek %s pokolenia" % (_level_name[level - 1])
        else:
            return t_inlaw +"przodek w %d pokoleniu" % level


    def get_single_relationship_string(self, Ga, Gb, gender_a, gender_b,
                                       reltocommon_a, reltocommon_b,
                                       only_birth=True,
                                       in_law_a=False, in_law_b=False):
        """
        Provide a string that describes the relationsip between a person, and
        another person. E.g. "grandparent" or "child".
        """

        if only_birth:
            step = ''
        else:
            step = self.STEP

        if in_law_a or in_law_b :
            inlaw = self.INLAW
        else:
            inlaw = ''


        # b is the same person as a
        if Ga == Gb == 0:
            rel_str = 'ta sama osoba'

        elif Ga == 0:
            # b is son/descendant of a

            if gender_b == Person.MALE:
                if inlaw and Gb == 1 and not step:
                    rel_str = "zięć"
                else:
                    rel_str = self.get_son(Gb, inlaw)

            elif gender_b == Person.FEMALE:
                if inlaw and Gb == 1 and not step:
                    rel_str = "synowa"
                else:
                    rel_str = self.get_daughter(Gb, inlaw)

            else:
                rel_str = self.get_child_unknown(Gb, inlaw)


        elif Gb == 0:
            # b is parent/grand parent of a

            if gender_b == Person.MALE:
                if inlaw and Gb == 1 and not step:
                    # TODO: znaleźć odpowiedniki w zależności czy to syn/córka
                    rel_str = "teść"
                else:
                    rel_str = self.get_father(Ga, reltocommon_a, inlaw)

            elif gender_b == Person.FEMALE:
                if inlaw and Gb == 1 and not step:
                    # TODO: znaleźć odpowiedniki w zależności czy to syn/córka
                    rel_str = "teściowa"
                else:
                    rel_str = self.get_mother(Ga, reltocommon_a, inlaw)

            else:
                rel_str = self.get_parent_unknown(Ga, inlaw)


        elif Ga == Gb == 1:
            # rodzeństwo
            if gender_b == Person.MALE:
                if inlaw and not step:
                    rel_str = "brat przyrodni"
                else:
                    rel_str = "brat rodzony"

            elif gender_b == Person.FEMALE:
                if inlaw and not step:
                    rel_str = "siostra przyrodnia"
                else:
                    rel_str = "siostra rodzony"
            else:
                rel_str = "brat/siostra"

        elif Gb == 1 and Ga > 1:

            # Przyjmij, że nie rozróżniamy osób prawnie i nieprawnie przybranych...

            if Ga == 2:
                # rodzeństwo rodziców

                # brat ojca, czyli stryj
                if (gender_b == Person.MALE) \
                    & (reltocommon_a[0] == self.REL_FATHER):
                    rel_str = "stryj"

                # siostra ojca, czyli ciotka ???
                elif (gender_b == Person.FEMALE) \
                    & (reltocommon_a[0] == self.REL_FATHER):
                    rel_str = "ciotka (tzw. stryjna)"

                # brat matki, czyli wuj/wujek
                elif (gender_b == Person.MALE) \
                    & (reltocommon_a[0] == self.REL_MOTHER):
                    rel_str = "wuj (wujek)"

                # siostra matki, czyli ciotka
                elif (gender_b == Person.FEMALE) \
                    & (reltocommon_a[0] == self.REL_MOTHER):
                    rel_str = "ciotka"

                else:
                    rel_str = "brat lub siostra rodzica"

            elif Ga == 3:
                # rodzeństwo dziadków rodziców osoby sprawdzanej

                # rodzeństwo dziadka po mieczu (ojca ojca)
                if (reltocommon_a[0] == self.REL_FATHER) \
                    & (reltocommon_a[1] == self.REL_FATHER):

                    if  (gender_b == Person.MALE):
                        rel_str = "dziadek stryjeczny (tzw przestryj, stary stryj)"
                    elif (gender_b == Person.FEMALE):
                        rel_str = "babcia stryjeczna"
                    else:
                        rel_str = "rodzeństwo przodka w 2 pokoleniu"

                # rodzeństwo babki po mieczu (matki ojca)
                elif (reltocommon_a[0] == self.REL_FATHER) \
                    & (reltocommon_a[1] == self.REL_MOTHER):

                    # TODO: Należy sprawdzić, czy w staropolszczyźnie nie ma
                    #            dokładniejszych określeń dla tego typu relacji
                    # TODO: EN: Try to check, whether in old polish language
                    #      are more specific word for this kind of relation
                    if  (gender_b == Person.MALE):
                        rel_str = "dziadek stryjeczny (tzw przestryj, stary stryj)"
                    elif (gender_b == Person.FEMALE):
                        rel_str = "babcia stryjeczna"
                    else:
                        rel_str = "rodzeństwo przodka w 2 pokoleniu"

                # rodzeństwo dziadka po kądzieli (ojca matki)
                elif (reltocommon_a[0] == self.REL_MOTHER) \
                    & (reltocommon_a[1] == self.REL_FATHER):

                    # TODO: Należy sprawdzić, czy w staropolszczyźnie nie ma
                    #            dokładniejszych określeń dla tego typu relacji
                    # TODO: EN: Try to check, whether in old polish language
                    #      are more specific word for this kind of relation
                    if  (gender_b == Person.MALE):
                        rel_str = "dziadek cioteczny (starop. prapociot)"
                    elif (gender_b == Person.FEMALE):
                        rel_str = "babcia cioteczna (starop. praciota)"
                    else:
                        rel_str = "rodzeństwo przodka w 2 pokoleniu"


                # rodzeństwo babki po kądzieli (matki matki)
                elif (reltocommon_a[0] == self.REL_MOTHER) \
                    & (reltocommon_a[1] == self.REL_MOTHER):

                    # TODO: Należy sprawdzić, czy w staropolszczyźnie nie ma
                    #           dokładniejszych określeń dla tego typu relacji
                    # TODO: EN: Try to check, whether in old polish language
                    #      are more specific word for this kind of relation
                    if  (gender_b == Person.MALE):
                        rel_str = "dziadek cioteczny (starop. prapociot)"
                    elif (gender_b == Person.FEMALE):
                        rel_str = "babcia cioteczna  (starop. praciota)"
                    else:
                        rel_str = "rodzeństwo przodka w 2 pokoleniu"

                else:
                    if  (gender_b == Person.MALE):
                        rel_str = "rodzeństwo dziadka"
                    elif (gender_b == Person.FEMALE):
                        rel_str = "rodzeństwo babci"
                    else:
                        rel_str = "rodzeństwo przodka w 2 pokoleniu"

            elif Ga > 3:
                # pradziadkowie...  (grandparents)

                if (gender_b == Person.MALE) \
                    & (reltocommon_a[0] == self.REL_FATHER):

                    if Ga >= 0 and Ga < len(_brother_level_of_male):
                        rel_str = _brother_level_of_male[Ga]
                    else:
                        rel_str = "rodzeństwo przodka męskiego %d pokolenia" % Ga

                elif (gender_b == Person.FEMALE) \
                    & (reltocommon_a[0] == self.REL_FATHER):
                    if Ga >= 0 and Ga < len(_sister_level_of_male):
                        rel_str = _sister_level_of_male[Ga]
                    else:
                        rel_str = "rodzeństwo przodka żeńskiego %d pokolenia" % Ga

                elif (gender_b == Person.MALE) \
                    & (reltocommon_a[0] == self.REL_MOTHER):

                    if Ga >= 0 and Ga < len(_brother_level_of_female):
                        rel_str = _brother_level_of_male[Ga]
                    else:
                        rel_str = "rodzeństwo przodka męskiego %d pokolenia" % Ga

                elif (gender_b == Person.FEMALE) \
                    & (reltocommon_a[0] == self.REL_MOTHER):
                    if Ga >= 0 and Ga < len(_sister_level_of_female):
                        rel_str = _sister_level_of_male[Ga]
                    else:
                        rel_str = "rodzeństwo przodka żeńskiego %d pokolenia" % Ga

                else:
                    rel_str = "rodzeństwo przodka %d pokolenia" % Ga
            else:
                # A program should never goes there, but...
                rel_str = "Relacja nie określona"

        elif Ga  ==1 and Gb > 1:

            # syn brata
            if (gender_b == Person.MALE) \
                & (reltocommon_b[0] == self.REL_FATHER):
                    if Gb < len(_nephew_level_of_brothers_son):
                        rel_str = _nephew_level_of_brothers_son[Gb]
                    else:
                        rel_str = "męski potomek w %d pokoleniu brata" % Gb

            # córka brata
            elif (gender_b == Person.FEMALE) \
                & (reltocommon_b[0] == self.REL_FATHER):
                    if Gb < len(_nephew_level_of_brothers_daughter):
                        rel_str = _nephew_level_of_brothers_daughter[Gb]
                    else:
                        rel_str = "żeński potomek w %d pokoleniu brata" % Gb

            # syn siostry
            if (gender_b == Person.MALE) \
                & (reltocommon_b[0] == self.REL_MOTHER):
                    if Gb < len(_nephew_level_of_sisters_son):
                        rel_str = _nephew_level_of_sisters_son[Gb]
                    else:
                        rel_str = "męski potomek w %d pokoleniu brata" % Gb

            # córka siostry
            elif (gender_b == Person.FEMALE) \
                & (reltocommon_b[0] == self.REL_MOTHER):
                    if Gb < len(_nephew_level_of_sisters_daughter):
                        rel_str = _nephew_level_of_sisters_daughter[Gb]
                    else:
                        rel_str = "żeński potomek w %d pokoleniu brata" % Gb

            # potomek brata
            elif (reltocommon_b[0] == self.REL_FATHER):
                rel_str = "potomek w %d pokoleniu brata" % Gb

            # potomek brata
            elif (reltocommon_b[0] == self.REL_MOTHER):
                rel_str = "potomek w %d pokoleniu brata" % Gb

            else :
                rel_str = "potomek w %d pokoleniu rodzeństwa" % Gb

        elif Ga > 1 and Gb > 1:
            if (gender_b == Person.MALE):
                if Ga == 2 and Gb == 2:
                    rel_str = "kuzyn"
                else:
                    rel_str = "daleki kuzyn (%d. stopień pokrewieństwa)" % (Ga+Gb)

            elif (gender_b == Person.FEMALE):
                if Ga == 2 and Gb == 2:
                    rel_str = "kuzynka"
                else:
                    rel_str = "daleka kuzynka (%d. stopień pokrewieństwa)" % (Ga+Gb)

            else:
                if Ga == 2 and Gb == 2:
                    rel_str = "kuzyn(ka)"
                else:
                    rel_str = "daleki członek rodziny (%d. stopień pokrewieństwa)" % (Ga+Gb)

        else:
            # A program should never goes there, but...
            rel_str = "nieokreślony stopień pokrewieństwa"

        return rel_str

    def get_plural_relationship_string(self, Ga, Gb,
                                       reltocommon_a='', reltocommon_b='',
                                       only_birth=True,
                                       in_law_a=False, in_law_b=False):
        """
        Generate a text with information, how far away is a group of persons
        from a main person
        """

        if Ga == Gb == 0:
            return 'ta sama osoba'
        if 0 == Ga:
            if 1 == Gb:
                return 'Dzieci'
            if 2 == Gb:
                return 'Wnuki'
            if 3 == Gb:
                return 'Prawnuki'
            if 4 == Gb:
                return 'Praprawnuki'
            return 'Praprapra(n)wnuki'
        if 0 == Gb:
            if 1 == Ga:
                return 'Rodzice'
            if 2 == Ga:
                return 'Dziadkowie'
            if 3 == Ga:
                return 'Pradziadkowie'
            if 4 == Ga:
                return 'Praprapradziadkowie'
            return 'Praprapra(n)dziadkowie'
        if 1 == Ga == Gb:
            return 'Rodzeństwo'
        if 1 == Gb and Ga > 1:
            return 'Wujowie/stryjowie i ciocie'
        if 1 < Gb and 1 == Ga:
            return 'bratankowie(ice)/siostrzeńcy(nice)'
        if 1 < Ga and 1 < Gb:
            return 'dalsza rodzina'
        return 'relacja nieznana'

    def get_sibling_relationship_string(self, sib_type, gender_a, gender_b,
                                        in_law_a=False, in_law_b=False):

        if in_law_a or in_law_b :
            inlaw = self.INLAW
        else:
            inlaw = ''

        if sib_type == self.NORM_SIB:
            if not inlaw:
                if gender_b == Person.MALE:
                    rel_str = 'brat (rodzony)'
                elif gender_b == Person.FEMALE:
                    rel_str = 'siostra (rodzona)'
                else:
                    rel_str = 'brat lub siostra (rodzeni)'
            else:
                if gender_b == Person.MALE:
                    # TODO: znaleźć odpowiednik
                    rel_str = "brat (pasierb)"
                elif gender_b == Person.FEMALE:
                    # TODO: znaleźć odpowiednik
                    rel_str = "siostra (pasierbica)"
                else:
                    # TODO: znaleźć odpowiednik
                    rel_str = "brat lub siostra (pasierb/pasierbica)"
        elif sib_type == self.UNKNOWN_SIB:
            if not inlaw:
                if gender_b == Person.MALE:
                    rel_str = 'brat'
                elif gender_b == Person.FEMALE:
                    rel_str = 'siostra'
                else:
                    rel_str = 'brat lub siostra'
            else:
                if gender_b == Person.MALE:
                    # TODO: znaleźć odpowiednik
                    rel_str = "brat (brat/szwagier)"
                elif gender_b == Person.FEMALE:
                    # TODO: znaleźć odpowiednik
                    rel_str = "siostra (bratowa/szwagierka)"
                else:
                    # TODO: znaleźć odpowiednik
                    rel_str = "brat lub siostra (szwagier/szagierka)"
        elif sib_type == self.HALF_SIB_FATHER:
                if gender_b == Person.MALE:
                    rel_str = "brat przyrodni"
                elif gender_b == Person.FEMALE:
                    rel_str = "siostra przyrodnia"
                else:
                    rel_str = "brat/siostra przyrodni"
        elif sib_type == self.HALF_SIB_MOTHER:
                if gender_b == Person.MALE:
                    rel_str = "brat przyrodni"
                elif gender_b == Person.FEMALE:
                    rel_str = "siostra przyrodnia"
                else:
                    rel_str = "brat/siostra przyrodni"
        elif sib_type == self.STEP_SIB:
                if gender_b == Person.MALE:
                    rel_str = "brat przyrodni"
                elif gender_b == Person.FEMALE:
                    rel_str = "siostra przyrodnia"
                else:
                    rel_str = "brat lub siostra przyrodnia"
        else:
            rel_str = "nieokreślona relacja rodzeństwa"
        return rel_str


if __name__ == "__main__":
    # Test function. Call it as follows from the command line (so as to find
    #        imported modules):
    #    export PYTHONPATH=/path/to/gramps/src
    #    python src/plugins/rel/rel_pl.py

    """TRANSLATORS, copy this if statement at the bottom of your
        rel_xx.py module, and test your work with:
        python src/plugins/rel/rel_xx.py
    """
    from gramps.gen.relationship import test
    RC = RelationshipCalculator()
    test(RC, True)

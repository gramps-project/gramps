# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2005  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2010       lcc & Robert Jerome
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

# Portuguese version by Duarte Loreto <happyguy_pt@hotmail.com>, 2007.
# Based on the Spanish version by Julio Sanchez <julio.sanchez@gmail.com>
"""
Specific classes for relationships.
"""

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------

from gramps.gen.lib import Person
import gramps.gen.relationship

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------

_level_name_male = [ "", "primeiro", "segundo", "terceiro", "quarto", "quinto",
                "sexto", "sétimo", "oitavo", "nono", "décimo", "décimo-primeiro",
                "décimo-segundo", "décimo-terceiro", "décimo-quarto", "décimo-quinto",
                "décimo-sexto", "décimo-sétimo", "décimo-oitavo", "décimo-nono",
                "vigésimo"]

# Short forms (in apocope) used before names
_level_name_male_a = [ "", "primeiro", "segundo", "terceiro", "quarto", "quinto",
                "sexto", "sétimo", "oitavo", "nono", "décimo", "décimo-primeiro",
                "décimo-segundo", "décimo-terceiro", "décimo-quarto", "décimo-quinto",
                "décimo-sexto", "décimo-sétimo", "décimo-oitavo", "décimo-nono",
                "vigésimo"]

_level_name_female = [ "", "primeira", "segunda", "terceira", "quarta", "quinta",
                "sexta", "sétima", "oitava", "nona", "décima", "décima-primeira",
                "décima-segunda", "décima-terceira", "décima-quarta", "décima-quinta",
                "décima-sexta", "décima-sétima", "décima-oitava", "décima-nona",
                "vigésima"]

_level_name_plural = [ "", "primeiros", "segundos", "terceiros", "quartos",
                "quintos", "sextos", "sétimos", "oitavos", "nonos",
                "décimos", "décimos-primeiros", "décimos-segundos", "décimos-terceiros",
                "décimos-quartos", "décimos-quintos", "décimos-sextos",
                "décimos-sétimos", "décimos-oitavos", "décimos-nonos",
                "vigésimos"]

# This plugin tries to be flexible and expect little from the following
# tables.  Ancestors are named from the list for the first generations.
# When this list is not enough, ordinals are used based on the same idea,
# i.e. bisavô is 'segundo avô' and so on, that has been the
# traditional way in Portuguese.  When we run out of ordinals we resort to
# Nº notation, that is sort of understandable if in context.
# There is a specificity for pt_BR where they can use "tataravô" instead
# of "tetravô", being both forms correct for pt_BR but just "tetravô"
# correct for pt. Translation keeps "tetravô".
_parents_level = [ "", "pais", "avós", "bisavós", "trisavós",
                   "tetravós", "pentavós", "hexavós", "heptavós", "octavós"]

_father_level = [ "", "pai", "avô", "bisavô", "trisavô",
                  "tetravô", "pentavô", "hexavô", "heptavô", "octavô"]

_mother_level = [ "", "mãe", "avó", "bisavó", "trisavó",
                  "tetravó", "pentavó", "hexavó", "heptavó", "octavó"]

# Higher-order terms (after "tetravô") are not standard in Portuguese.
# Check http://www.geneall.net/P/forum_msg.php?id=136774 that states
# that although some people may use other greek-prefixed forms for
# higher levels, both pt and pt_BR correct form is to use, after
# "tetravô", the "quinto avô", "sexto avô", etc.

_son_level = [ "", "filho", "neto", "bisneto",
               "trineto", "tetraneto", "pentaneto", "hexaneto", "heptaneto", "octaneto"]

_daughter_level = [ "", "filha", "neta", "bisneta",
                    "trineta", "tetraneta", "pentaneta", "hexaneta", "heptaneta", "octaneta"]

_sister_level = [ "", "irmã", "tia", "tia avó", "tia bisavó", "tia trisavó", "tia tetravó",
                  "tia pentavó", "tia hexavó", "tia heptavó", "tia octavó"]

_brother_level = [ "", "irmão", "tio", "tio avô", "tio bisavô", "tio trisavô",
                   "tio tetravô", "tio pentavô", "tio hexavô", "tio heptavô", "tio octavô"]

_nephew_level = [ "", "sobrinho", "sobrinho neto", "sobrinho bisneto", "sobrinho trineto",
                  "sobrinho tetraneto", "sobrinho pentaneto", "sobrinho hexaneto",
                  "sobrinho heptaneto", "sobrinho octaneto"]

_niece_level = [ "", "sobrinha", "sobrinha neta", "sobrinha bisneta", "sobrinha trineta",
                 "sobrinha tetraneta", "sobrinha pentaneta", "sobrinha hexaneta",
                 "sobrinha heptaneta", "sobrinha octaneta"]

# Relatório de Parentesco

_PARENTS_LEVEL = ["", "pais", "avós", "bisavós", "tetravós",
                  "pentavós", "hexavós", "heptavós", "octavós"]

_CHILDREN_LEVEL = ["", "filhos", "netos", "bisnetos", "trinetos",
                   "tetranetos", "pentanetos", "hexanetos", "heptanetos"
                   "octanetos"]

_SIBLINGS_LEVEL = ["", "irmãos e irmãs", "tios e tias","tios avôs e tias avós",
                   "tios bisavôs e tias bisavós", "tios trisavôs e tias trisavós",
                   "tios tetravôs e tias tetravós", "tios pentavôs e tias pentavós",
                   "tios hexavôs e tias hexavós", "tios heptavôs e tias heptavós"
                   "tios octavôs e tias octavós"]

_NEPHEWS_NIECES_LEVEL = ["", "sobrinhos e sobrinhas",
                         "sobrinhos netos e sobrinhas netas",
                         "sobrinhos bisnetos e sobrinhas bisnetas",
                         "sobrinhos trinetos e sobrinhas trinetas"
                         "sobrinhos tetranetos e sobrinhas tetranetas"
                         "sobrinhos pentanetos e sobrinhas pentanetas"
                         "sobrinhos hexanetos e sobrinhas hexanetas"
                         "sobrinhos heptanetos e sobrinhas heptanetas"
                         "sobrinhos octanetos e sobrinhas octanetas"
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

    def get_male_cousin(self, level):
        if level < len(_level_name_male):
            return "%s primo" % (_level_name_male[level])
        else:
            return "%dº primo" % level

    def get_female_cousin(self, level):
        if level < len(_level_name_female):
            return "%s prima" % (_level_name_female[level])
        else:
            return "%dª prima" % level

    def get_distant_uncle(self, level):
        if level < len(_level_name_male):
            return "%s tio" % (_level_name_male[level])
        else:
            return "%dº tio" % level

    def get_distant_aunt(self, level):
        if level < len(_level_name_female):
            return "%s tia" % (_level_name_female[level])
        else:
            return "%dª tia" % level

    def get_distant_nephew(self, level):
        if level < len(_level_name_male):
            return "%s sobrinho" % (_level_name_male[level])
        else:
            return "%dº sobrinho" % level

    def get_distant_niece(self, level):
        if level < len(_level_name_female):
            return "%s sobrinha" % (_level_name_female[level])
        else:
            return "%dª sobrinha" % level

    def get_male_relative(self, level1, level2):
        if level1 < len(_level_name_male_a):
            level1_str = _level_name_male_a[level1]
        else:
            level1_str = "%dº" % level1
        if level2 < len(_level_name_male_a):
            level2_str = _level_name_male_a[level2]
        else:
            level2_str = "%dº" % level2
        level = level1 + level2
        if level < len(_level_name_male_a):
            level_str = _level_name_male_a[level]
        else:
            level_str = "%dº" % level
        return "parente em %s grau (%s com %s)" % (level_str, level1_str, level2_str)

    def get_female_relative(self, level1, level2):
        return self.get_male_relative(level1, level2)

    def get_parents(self, level):
        if level < len(_parents_level):
            return _parents_level[level]
        elif (level-1) < len(_level_name_plural):
            return "%s avós" % (_level_name_plural[level-1])
        else:
            return "%dº avós" % (level-1)

    def get_father(self, level):
        if level < len(_father_level):
            return _father_level[level]
        elif (level-1) < len(_level_name_male_a):
            return "%s avô" % (_level_name_male_a[level-1])
        else:
            return "%dº avô" % (level-1)

    def get_son(self, level):
        if level < len(_son_level):
            return _son_level[level]
        elif (level-1) < len(_level_name_male_a):
            return "%s neto" % (_level_name_male_a[level-1])
        else:
            return "%dº neto" % (level-1)

    def get_mother(self, level):
        if level < len(_mother_level):
            return _mother_level[level]
        elif (level-1)<len(_level_name_female):
            return "%s avó" % (_level_name_female[level-1])
        else:
            return "%dª avó" % (level-1)

    def get_daughter(self, level):
        if level < len(_daughter_level):
            return _daughter_level[level]
        elif (level-1) < len(_level_name_female):
            return "%s neta" % (_level_name_female[level-1])
        else:
            return "%dª neta" % (level-1)

    def get_aunt(self, level):
        if level < len(_sister_level):
            return _sister_level[level]
        elif (level-2) < len(_level_name_female):
            return "%s tia avó" % (_level_name_female[level-2])
        else:
            return "%dª tia avó" % (level-2)

    def get_uncle(self, level):
        if level < len(_brother_level):
            return _brother_level[level]
        elif (level-2) < len(_level_name_male_a):
            return "%s tio avô" % (_level_name_male_a[level-2])
        else:
            return "%dº tio avô" % (level-2)

    def get_nephew(self, level):
        if level < len(_nephew_level):
            return _nephew_level[level]
        elif (level-1) < len(_level_name_male_a):
            return "%s sobrinho neto" % (_level_name_male_a[level-1])
        else:
            return "%dº sobrinho neto" % (level-1)

    def get_niece(self, level):
        if level < len(_niece_level):
            return _niece_level[level]
        elif (level-1) < len(_level_name_female):
            return "%s sobrinha neta" % (_level_name_female[level-1])
        else:
            return "%dª sobrinha neta" % (level-1)

    def get_relationship(self, secondRel, firstRel, orig_person_gender, other_person_gender):
        """
        returns a string representing the relationship between the two people,
        along with a list of common ancestors (typically father, mother)
        """

        common = ""
        if firstRel == 0:
            if secondRel == 0:
                return ('', common)
            elif other_person_gender == Person.MALE:
                return (self.get_father(secondRel), common)
            else:
                return (self.get_mother(secondRel), common)
        elif secondRel == 0:
            if other_person_gender == Person.MALE:
                return (self.get_son(firstRel), common)
            else:
                return (self.get_daughter(firstRel), common)
        elif firstRel == 1:
            if other_person_gender == Person.MALE:
                return (self.get_uncle(secondRel), common)
            else:
                return (self.get_aunt(secondRel), common)
        elif secondRel == 1:
            if other_person_gender == Person.MALE:
                return (self.get_nephew(firstRel-1), common)
            else:
                return (self.get_niece(firstRel-1), common)
        elif firstRel == secondRel == 2:
            if other_person_gender == Person.MALE:
                return ('primo irmão', common)
            else:
                return ('prima irmã', common)
        elif firstRel == secondRel:
            if other_person_gender == Person.MALE:
                return (self.get_male_cousin(firstRel-1), common)
            else:
                return (self.get_female_cousin(firstRel-1), common)
        elif firstRel == secondRel+1:
            if other_person_gender == Person.MALE:
                return (self.get_distant_nephew(secondRel), common)
            else:
                return (self.get_distant_niece(secondRel), common)
        elif firstRel+1 == secondRel:
            if other_person_gender == Person.MALE:
                return (self.get_distant_uncle(firstRel), common)
            else:
                return (self.get_distant_aunt(firstRel), common)
        else:
            if other_person_gender == Person.MALE:
                return (self.get_male_relative(firstRel, secondRel), common)
            else:
                return (self.get_female_relative(firstRel, secondRel), common)

    def get_single_relationship_string(self, Ga, Gb, gender_a, gender_b,
                                       reltocommon_a, reltocommon_b,
                                       only_birth=True,
                                       in_law_a=False, in_law_b=False):
        return self.get_relationship(Ga, Gb, gender_a, gender_b)[0];

    def get_sibling_relationship_string(self, sib_type, gender_a, gender_b,
                                        in_law_a=False, in_law_b=False):
        return self.get_relationship(1, 1, gender_a, gender_b)[0];

    # Relatório de parentesco

    def get_plural_relationship_string(self, Ga, Gb,
                                       reltocommon_a='', reltocommon_b='',
                                       only_birth=True,
                                       in_law_a=False, in_law_b=False):
        """
        Cria o objecto KinshipReport que produz o relatório.
        Os argumentos são:
        database        - a instância do banco de dados GRAMPS
        options_class   - instância da classe das opções para este relatório
        O presente relatório tem os seguintes parâmetros (variáveis de classe)
        que entram na classe de opções.
        maxdescend    - Máximo gerações de descendentes para incluir.
        maxascend     - Máximo de gerações ancestrais para incluir.
        incspouses    - Se deseja incluir cônjuges.
        inccousins    - Se deseja incluir primos.
        incaunts      - Se deseja incluir tios / sobrinhos.
        pid           - A identificação Gramps da pessoa central para o relatório.

        Preenche um mapa das matrizes contendo os descendentes
        da pessoa falecida. Esta função chama a si mesma recursivamente até
        atingir max_descend.
        Parâmetros:

        :param person_handle: o identificador da próxima pessoa
        :param Ga: O número de gerações, desde a pessoa principal até o
                   ancestral comum. É incrementado quando subir as gerações, e
                   deixado inalterado quando descer as gerações.
        :param Gb: O número de gerações desta pessoa (person_handle) até o
                   ancestral comum. É incrementado quando descer as
                   gerações and posto a zero quando subir as gerações.
        :param skip_handle: Identificador opcional para pular quando descer.
                            Isso é útil para pular o descendente que trouxe
                            essa generação em primeiro lugar.

        Preenche um mapa das matrizes contendo os ancestrais
        da pessoa falecida. Esta função chama a si mesma recursivamente até
        atingir max_ascend.
        Parâmetros:

        :param person_handle: o identificador da próxima pessoa
        :param Ga: O número de gerações, desde a pessoa principal até o
                   ancestral comum. É incrementado quando subir as gerações, e
                   deixado inalterado quando descer as gerações.
        :param Gb: O número de gerações desta pessoa (person_handle) até o
                   ancestral comum. É incrementado quando descer as
                   gerações and posto a zero quando subir as gerações.
        """

        rel_str = "???"

        if Ga == 0:

            # These are descendants

            if Gb < len(_CHILDREN_LEVEL):
                rel_str = _CHILDREN_LEVEL[Gb]
            else:
                rel_str = "descendentes"
        elif Gb == 0:

            # These are parents/grand parents

            if Ga < len(_PARENTS_LEVEL):
                rel_str = _PARENTS_LEVEL[Ga]
            else:
                rel_str = "ancestrais"
        elif Gb == 1:

            # These are siblings/aunts/uncles

            if Ga < len(_SIBLINGS_LEVEL):
                rel_str = _SIBLINGS_LEVEL[Ga]
            else:
                rel_str = "filhos dos ancestrais"
        elif Ga == 1:

            # These are nieces/nephews

            if Gb < len(_NEPHEWS_NIECES_LEVEL):
                rel_str = _NEPHEWS_NIECES_LEVEL[Gb - 1]
            else:
                rel_str = "sobrinhos sobrinhas"
        elif Ga > 1 and Ga == Gb:

            # These are cousins in the same generation

            if Ga == 2:
                rel_str = "primos e primas"
            elif Ga <= len(_level_name_plural):
                rel_str = "%s primos e primas" % _level_name_plural[Ga -
                        2]
            else:

            # security

                rel_str = "primos e primas"

        if in_law_b == True:
            rel_str = "cônjuges dos %s" % rel_str

        return rel_str

if __name__ == "__main__":

    # Test function. Call it as follows from the command line (so as to find
    #        imported modules):
    #    export PYTHONPATH=/path/to/gramps/src
    # python src/plugins/rel/rel_pt.py
    # (Above not needed here)

    """TRANSLATORS, copy this if statement at the bottom of your
        rel_xx.py module, and test your work with:
        python src/plugins/rel/rel_xx.py
    """
    from gramps.gen.relationship import test
    RC = RelationshipCalculator()
    test(RC, True)

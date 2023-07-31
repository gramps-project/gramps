#                                                     -*- python -*-
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

#
# Written by Lorenzo Cappelletti <lorenzo.cappelletti@email.it>, 2003
#            Benny Malengier <benny.malengier@gramps-project.org, 2007
#            Maria-Cristina Ciocci <see above>, 2007
#
"""
Italian-Specific classes for relationships.
"""

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------

from gramps.gen.lib import Person
import gramps.gen.relationship

# -------------------------------------------------------------------------
#
# Shared constants
#
# -------------------------------------------------------------------------

_level = [
    "",
    "prim%(gen)s",
    "second%(gen)s",
    "terz%(gen)s",
    "quart%(gen)s",
    "quint%(gen)s",
    "sest%(gen)s",
    "settim%(gen)s",
    "ottav%(gen)s",
    "non%(gen)s",
    "decim%(gen)s",
    "undicesim%(gen)s",
    "dodicesim%(gen)s",
    "tredicesim%(gen)s",
    "quattordicesim%(gen)s",
    "quindicesim%(gen)s",
    "sedicesim%(gen)s",
    "diciasettesim%(gen)s",
    "diciottesim%(gen)s",
    "diciannovesim%(gen)s",
    "ventesim%(gen)s",
]

_level_m = [
    "",
    "primo",
    "secondo",
    "terzo",
    "quarto",
    "quinto",
    "sesto",
    "settimo",
    "ottavo",
    "nono",
    "decimo",
    "undicesimo",
    "dodicesimo",
    "tredicesimo",
    "quattordicesimo",
    "quindicesimo",
    "sedicesimo",
    "diciasettesimo",
    "diciottesimo",
    "diciannovesimo",
    "ventesimo",
]

_level_f = [
    "",
    "prima",
    "seconda",
    "terza",
    "quarta",
    "quinta",
    "sesta",
    "settima",
    "ottava",
    "nona",
    "decima",
    "undicesima",
    "dodicesima",
    "tredicesima",
    "quattordicesima",
    "quindicesima",
    "sedicesima",
    "diciasettesima",
    "diciottesima",
    "diciannovesima",
    "ventesima",
]

_father_level = [
    "",
    "il padre%(step)s%(inlaw)s",
    "il nonno%(step)s%(inlaw)s",
    "il bisnonno%(step)s%(inlaw)s",
    "il trisnonno%(step)s%(inlaw)s",
]

_mother_level = [
    "",
    "la madre%(step)s%(inlaw)s",
    "la nonna%(step)s%(inlaw)s",
    "la bisnonna%(step)s%(inlaw)s",
    "la trisnonna%(step)s%(inlaw)s",
]

_son_level = [
    "",
    "il figlio%(step)s%(inlaw)s",
    "il nipote%(step)s%(inlaw)s diretto",
    "il pronipote%(step)s%(inlaw)s diretto",
]

_daughter_level = [
    "",
    "la figlia%(step)s%(inlaw)s",
    "la nipote%(step)s%(inlaw)s diretta",
    "la pronipote%(step)s%(inlaw)s diretta",
]

_brother_level = [
    "",
    "il fratello%(step)s%(inlaw)s",
    "lo zio%(step)s%(inlaw)s",
    "il prozio%(step)s%(inlaw)s",
]

_sister_level = [
    "",
    "la sorella%(step)s%(inlaw)s",
    "la zia%(step)s%(inlaw)s",
    "la prozia%(step)s%(inlaw)s",
]

_nephew_level = ["", "il nipote%(step)s%(inlaw)s", "il pronipote%(step)s%(inlaw)s"]

_niece_level = ["", "la nipote%(step)s%(inlaw)s", "la pronipote%(step)s%(inlaw)s"]


# -------------------------------------------------------------------------
#
#
#
# -------------------------------------------------------------------------
class RelationshipCalculator(gramps.gen.relationship.RelationshipCalculator):
    """
    RelationshipCalculator Class
    """

    INLAW = " acquisit%(gen)s"

    STEP = " adottiv%(gen)s"

    def __init__(self):
        gramps.gen.relationship.RelationshipCalculator.__init__(self)

    # -------------------------------------------------------------------------
    #
    # Specific relationship functions
    #
    # To be honest, I doubt that this relationship naming method is widely
    # spread... If you know of a rigorous, italian naming convention,
    # please, drop me an email.
    #
    # -------------------------------------------------------------------------

    def __gen_suffix(self, gender):
        if gender == Person.MALE:
            return "o"
        return "a"

    def get_parents(self, level):
        if level > len(_level) - 1:
            return "remote ancestors"
        else:
            return "%si genitori" % _level[level]

    def get_father(self, level, step="", inlaw=""):
        gen = "o"

        if level < len(_father_level):
            return _father_level[level] % {"step": step, "inlaw": inlaw} % {"gen": gen}
        elif level < len(_level):
            return (
                "il nonno%(step)s%(inlaw)s della %(level_f)s generazione"
                % {"level_f": _level_f[level], "step": step, "inlaw": inlaw}
                % {"gen": gen}
            )
        else:
            return (
                "l'avo%(step)s%(inlaw)s (%(level)d generazioni)"
                % {"step": step, "inlaw": inlaw, "level": level}
                % {"gen": gen}
            )

    def get_mother(self, level, step="", inlaw=""):
        gen = "a"

        if level < len(_father_level):
            return _mother_level[level] % {"step": step, "inlaw": inlaw} % {"gen": gen}
        elif level < len(_level):
            return (
                "la nonna%(step)s%(inlaw)s della %(level_f)s generazione"
                % {"level_f": _level_f[level], "step": step, "inlaw": inlaw}
                % {"gen": gen}
            )
        else:
            return (
                "l'ava%(step)s%(inlaw)s (%(level)d generazioni)"
                % {"step": step, "inlaw": inlaw, "level": level}
                % {"gen": gen}
            )

    def get_parent_unknown(self, level, step="", inlaw=""):
        gen = "o/a"

        if level == 1:
            return (
                "uno dei genitori%(step)s%(inlaw)s"
                % {"step": step, "inlaw": inlaw}
                % {"gen": gen}
            )
        elif level < len(_father_level):
            return _mother_level[level] % {"step": step, "inlaw": inlaw} % {"gen": gen}
        elif level < len(_level):
            return (
                "nonno/a%(step)s%(inlaw)s della %(level_f)s generazione"
                % {"level_f": _level_f[level], "step": step, "inlaw": inlaw}
                % {"gen": gen}
            )
        else:
            return (
                "l'ava%(step)s%(inlaw)s (%(level)d generazioni)"
                % {"step": step, "inlaw": inlaw, "level": level}
                % {"gen": gen}
            )

    def get_son(self, level, step="", inlaw=""):
        gen = "o"
        if level < len(_son_level):
            return _son_level[level] % {"step": step, "inlaw": inlaw} % {"gen": gen}
        elif level < len(_level):
            return (
                "il nipote%(step)s%(inlaw)s diretto della %(level_f)s generazione"
                % {"level_f": _level_f[level], "step": step, "inlaw": inlaw}
                % {"gen": gen}
            )
        else:
            return (
                "il discendente%(step)s%(inlaw)s diretto (%(level)d generazioni)"
                % {"step": step, "inlaw": inlaw, "level": level}
                % {"gen": gen}
            )

    def get_daughter(self, level, step="", inlaw=""):
        gen = "a"
        if level < len(_daughter_level):
            return (
                _daughter_level[level] % {"step": step, "inlaw": inlaw} % {"gen": gen}
            )
        elif level < len(_level):
            return (
                "la nipote%(step)s%(inlaw)s diretta della %(level_f)s generazione"
                % {"level_f": _level_f[level], "step": step, "inlaw": inlaw}
                % {"gen": gen}
            )
        else:
            return (
                "la discendente%(step)s%(inlaw)s diretta (%(level)d generazioni)"
                % {"step": step, "inlaw": inlaw, "level": level}
                % {"gen": gen}
            )

    def get_uncle(self, level, step="", inlaw=""):
        gen = "o"
        if level < len(_brother_level):
            return _brother_level[level] % {"step": step, "inlaw": inlaw} % {"gen": gen}
        elif level < len(_level):
            return (
                "lo zio%(step)s%(inlaw)s della %(level_f)s generazione"
                % {"level_f": _level_f[level], "step": step, "inlaw": inlaw}
                % {"gen": gen}
            )
        else:
            return (
                "uno zio%(step)s%(inlaw)s lontano (%(level)d generazioni)"
                % {"step": step, "inlaw": inlaw, "level": level}
                % {"gen": gen}
            )

    def get_aunt(self, level, step="", inlaw=""):
        gen = "a"
        if level < len(_brother_level):
            return _sister_level[level] % {"step": step, "inlaw": inlaw} % {"gen": gen}
        elif level < len(_level):
            return (
                "la zia%(step)s%(inlaw)s della %(level_f)s generazione"
                % {"level_f": _level_f[level], "step": step, "inlaw": inlaw}
                % {"gen": gen}
            )
        else:
            return (
                "una zia%(step)s%(inlaw)s lontana (%(level)d generazioni)"
                % {"step": step, "inlaw": inlaw, "level": level}
                % {"gen": gen}
            )

    def get_nephew(self, level, step="", inlaw=""):
        gen = "o"
        if level < len(_nephew_level):
            return _nephew_level[level] % {"step": step, "inlaw": inlaw} % {"gen": gen}
        elif level < len(_level):
            return "il nipote%(step)s%(inlaw)s " "della %(level_f)s generazione" % {
                "level_f": _level_f[level],
                "step": step,
                "inlaw": inlaw,
            } % {"gen": gen}
        else:
            return "un nipote%(step)s%(inlaw)s lontano (" "%(level)d generazioni)" % {
                "step": step,
                "inlaw": inlaw,
                "level": level,
            } % {"gen": gen}

    def get_niece(self, level, step="", inlaw=""):
        gen = "a"
        if level < len(_nephew_level):
            return _niece_level[level] % {"step": step, "inlaw": inlaw} % {"gen": gen}
        elif level < len(_level):
            return "la nipote%(step)s%(inlaw)s " "della %(level_f)s generazione" % {
                "level_f": _level_f[level],
                "step": step,
                "inlaw": inlaw,
            } % {"gen": gen}
        else:
            return "una nipote%(step)s%(inlaw)s lontana (" "%(level)d generazioni)" % {
                "step": step,
                "inlaw": inlaw,
                "level": level,
            } % {"gen": gen}

    def get_male_cousin(self, levelA, levelB, step="", inlaw=""):
        gen = "o"
        return (
            "il cugino%(step)s%(inlaw)s di %(level)d° grado"
            "(%(levA)d-%(levB)d)"
            % {
                "level": levelA + levelB - 1,
                "step": step,
                "inlaw": inlaw,
                "levA": levelA,
                "levB": levelB,
            }
            % {"gen": gen}
        )

    def get_female_cousin(self, levelA, levelB, step="", inlaw=""):
        gen = "a"
        return (
            "la cugina%(step)s%(inlaw)s di %(level)d° grado"
            "(%(levA)d-%(levB)d)"
            % {
                "level": levelA + levelB - 1,
                "step": step,
                "inlaw": inlaw,
                "levA": levelA,
                "levB": levelB,
            }
            % {"gen": gen}
        )

    # -------------------------------------------------------------------------
    #
    # get_relationship
    #
    # -------------------------------------------------------------------------

    def get_relationship(self, db, orig_person, other_person):
        """
        returns a string representing the relationshp between the two people,
        along with a list of common ancestors (typically father, mother)
        """

        if orig_person is None:
            return ("non definito", [])

        if orig_person.get_handle() == other_person.get_handle():
            return ("", [])

        is_spouse = self.is_spouse(db, orig_person, other_person)
        if is_spouse:
            return (is_spouse, [])

        # get_relationship_distance changed, first data is relation to
        # orig person, apperently secondRel in this function
        (secondRel, firstRel, common) = self.get_relationship_distance_new(
            db, orig_person, other_person
        )

        if isinstance(common, str):
            return (common, [])
        elif common:
            person_handle = common[0]
        else:
            return ("", [])

        firstRel = len(firstRel)
        secondRel = len(secondRel)

        if firstRel == 0:
            if secondRel == 0:
                return ("", common)
            elif other_person.get_gender() == Person.MALE:
                return (self.get_father(secondRel), common)
            else:
                return (self.get_mother(secondRel), common)
        elif secondRel == 0:
            if other_person.get_gender() == Person.MALE:
                return (self.get_son(firstRel), common)
            else:
                return (self.get_daughter(firstRel), common)
        elif firstRel == 1:
            if other_person.get_gender() == Person.MALE:
                return (self.get_uncle(secondRel), common)
            else:
                return (self.get_aunt(secondRel), common)
        elif secondRel == 1:
            if other_person.get_gender() == Person.MALE:
                return (self.get_nephew(firstRel - 1), common)
            else:
                return (self.get_niece(firstRel - 1), common)
        else:
            if other_person.get_gender() == Person.MALE:
                return (self.get_male_cousin(firstRel - 1, secondRel - 1), common)
            else:
                return (self.get_female_cousin(firstRel - 1, secondRel - 1), common)

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
        See Comment in Relationship Class (relationship.py)
        """

        if only_birth:
            step = ""
        else:
            step = self.STEP

        if in_law_a or in_law_b:
            inlaw = self.INLAW
        else:
            inlaw = ""

        if gender_b == Person.MALE:
            rel_str = "un parente%s%s lontano" % (step, inlaw) % {"gen": "o"}
        elif gender_b == Person.FEMALE:
            rel_str = "una parente%s%s lontana" % (step, inlaw) % {"gen": "a"}
        else:
            rel_str = "uno dei parenti%s%s lontani" % (step, inlaw) % {"gen": "i"}

        if Gb == 0:
            if Ga == 0:
                rel_str = "la stessa persona"
            elif Ga == 1 and inlaw and not step:
                if gender_b == Person.MALE:
                    rel_str = "il suocero"
                elif gender_b == Person.FEMALE:
                    rel_str = "la suocera"
                else:
                    rel_str = "uno dei suoceri"
            elif Ga == 1 and not inlaw and step:
                if gender_b == Person.MALE:
                    rel_str = "il patrigno"
                elif gender_b == Person.FEMALE:
                    rel_str = "la matrigna"
                else:
                    rel_str = "uno dei genitori adottivi"
            elif gender_b == Person.MALE:
                rel_str = self.get_father(Ga, step, inlaw)
            elif gender_b == Person.FEMALE:
                rel_str = self.get_mother(Ga, step, inlaw)
            else:
                rel_str = self.get_parent_unknown(Ga, step, inlaw)
        elif Ga == 0:
            if Gb == 1 and inlaw and not step:
                if gender_b == Person.MALE:
                    rel_str = "il genero"
                elif gender_b == Person.FEMALE:
                    rel_str = "la nuora"
                else:
                    rel_str = "genero/nuora"
            elif gender_b == Person.MALE:
                rel_str = self.get_son(Gb, step, inlaw)
            else:
                rel_str = self.get_daughter(Gb, step, inlaw)
        elif Gb == 1:
            if Ga == 1 and inlaw and not step:
                if gender_b == Person.MALE:
                    rel_str = "il cognato"
                elif gender_b == Person.FEMALE:
                    rel_str = "la cognata"
                else:
                    rel_str = "il cognato/a"
            if gender_b == Person.MALE:
                rel_str = self.get_uncle(Ga, step, inlaw)
            else:
                rel_str = self.get_aunt(Ga, step, inlaw)
        elif Ga == 1:
            if gender_b == Person.MALE:
                rel_str = self.get_nephew(Gb - 1, step, inlaw)
            else:
                rel_str = self.get_niece(Gb - 1, step, inlaw)
        else:
            if gender_b == Person.MALE:
                rel_str = self.get_male_cousin(Gb - 1, Ga - 1, step, inlaw)
            else:
                rel_str = self.get_female_cousin(Gb - 1, Ga - 1, step, inlaw)
        return rel_str

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
        if in_law_a or in_law_b:
            inlaw = self.INLAW
        else:
            inlaw = ""

        if sib_type == self.NORM_SIB or sib_type == self.UNKNOWN_SIB:
            if not inlaw:
                if gender_b == Person.MALE:
                    rel_str = self.get_uncle(1, "", "")
                else:
                    rel_str = self.get_aunt(1, "", "")
            else:
                if gender_b == Person.MALE:
                    rel_str = "il cognato"
                elif gender_b == Person.FEMALE:
                    rel_str = "la cognata"
                else:
                    rel_str = "il cognato/a"
        elif (
            sib_type == self.HALF_SIB_FATHER
            or sib_type == self.HALF_SIB_MOTHER
            or sib_type == self.STEP_SIB
        ):
            # Italian has no difference between half and step sibling!
            if not inlaw:
                if gender_b == Person.MALE:
                    rel_str = "il fratellastro"
                elif gender_b == Person.FEMALE:
                    rel_str = "la sorellastra"
                else:
                    rel_str = "il fratellastro/sorellastra"
            else:
                if gender_b == Person.MALE:
                    rel_str = "il fratellastro acquisito"
                elif gender_b == Person.FEMALE:
                    rel_str = "la sorellastra acquisita"
                else:
                    rel_str = "il fratellastro/sorellastra acquisito/a"

        return rel_str


if __name__ == "__main__":
    # Test function. Call it as follows from the command line (so as to find
    #        imported modules):
    #    export PYTHONPATH=/path/to/gramps/src
    #    python src/plugins/rel/rel_it.py

    """TRANSLATORS, copy this if statement at the bottom of your
    rel_xx.py module, and test your work with:
    python src/plugins/rel/rel_xx.py
    """
    from gramps.gen.relationship import test

    RC = RelationshipCalculator()
    test(RC, True)

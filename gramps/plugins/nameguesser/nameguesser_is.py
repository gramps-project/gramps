#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2025 Christina Rauscher
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


from gramps.gen.lib import (
    Name,
    Surname,
    FamilyRelType,
)
from gramps.gen.lib.nameorigintype import NameOriginType
import gramps.gen.nameguesser
from gramps.gen.utils.db import preset_name


# -------------------------------------------------------------------------
#
# NameGuesser
#
# -------------------------------------------------------------------------
class NameGuesser(gramps.gen.nameguesser.NameGuesser):
    """
    The name guesser guesses the names of a person based on their relationships.
    """

    def fathers_name_from_child(self, db, family):
        """
        Get father's given name from child's surname.
        """
        name = Name()
        name.add_surname(Surname())
        name.set_primary_surname(0)
        # for each child, find one with a non-matronymic last name
        for ref in family.get_child_ref_list():
            child = db.get_person_from_handle(ref.ref)
            if child:
                child_name = child.get_primary_name()
                child_surname_list = child_name.get_surname_list()
                for child_surname in child_surname_list:
                    if int(child_surname.get_origintype()) != NameOriginType.MATRONYMIC:
                        surname = child_surname.get_surname()
                        father_given_name = ""
                        if surname.endswith("sson"):
                            father_given_name = surname.replace("sson", "")
                        elif surname.endswith("sdóttir"):
                            father_given_name = surname.replace("sdóttir", "")
                        elif surname.endswith("sdottir"):
                            father_given_name = surname.replace("sdottir", "")
                        if len(father_given_name) > 0:
                            name.set_first_name(father_given_name)
                            return name

        return name

    def mothers_name_from_child(self, db, family):
        """
        If child's surname is matronymic, guess mother's given name based on the child's surname.
        """
        name = Name()
        name.add_surname(Surname())
        name.set_primary_surname(0)
        # for each child, find one with a matronymic last name
        for ref in family.get_child_ref_list():
            child = db.get_person_from_handle(ref.ref)
            if child:
                child_name = child.get_primary_name()
                child_surname_list = child_name.get_surname_list()
                for child_surname in child_surname_list:
                    if (
                        child_surname.get_origintype().value
                        == NameOriginType.MATRONYMIC
                    ):
                        matronymic_surname = child_surname.get_surname()
                        mother_given_name = ""
                        if matronymic_surname.endswith("sson"):
                            mother_given_name = matronymic_surname.replace("sson", "")
                        elif matronymic_surname.endswith("sdóttir"):
                            mother_given_name = matronymic_surname.replace(
                                "sdóttir", ""
                            )
                        elif matronymic_surname.endswith("sdottir"):
                            mother_given_name = matronymic_surname.replace(
                                "sdottir", ""
                            )
                        if len(mother_given_name) > 0:
                            name.set_first_name(mother_given_name)
                            return name

        return name

    def childs_name(self, db, family):
        """
        Child's family name is the father's given name + "sson" or "dóttir"
        We don't know the gender of the child at this point, so it defaults to "sson".
        """
        name = Name()
        name.add_surname(Surname())
        name.set_primary_surname(0)

        father_handle = family.get_father_handle()
        father = db.get_person_from_handle(father_handle) if father_handle else None
        mother_handle = family.get_mother_handle()
        mother = db.get_person_from_handle(mother_handle) if mother_handle else None

        if not father and not mother:
            return name
        if not father:
            mother_name = mother.get_primary_name()
            mother_given_name = mother_name.get_first_name()
            if mother_given_name and len(mother_given_name) > 0:
                matronymic = Surname()
                matronymic.set_origintype(NameOriginType.MATRONYMIC)
                if mother_given_name.endswith("s"):
                    matronymic.set_surname(mother_given_name + "son")
                else:
                    matronymic.set_surname(mother_given_name + "sson")
                name.set_surname_list([matronymic])
        else:
            father_name = father.get_primary_name()
            father_given_name = father_name.get_first_name()

            if father_given_name and len(father_given_name) > 0:
                patronymic = Surname()
                patronymic.set_origintype(NameOriginType.PATRONYMIC)
                if father_given_name.endswith("s"):
                    patronymic.set_surname(father_given_name + "son")
                else:
                    patronymic.set_surname(father_given_name + "sson")

                name.set_surname_list([patronymic])

        return name

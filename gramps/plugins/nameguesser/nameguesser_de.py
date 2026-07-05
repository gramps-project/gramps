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
from gramps.gen.utils.db import (
    preset_name,
)
import gramps.gen.nameguesser


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
        If family is not unmarried, get the surname from a child. Else, return empty name.
        """
        name = Name()
        # the editor requires a surname
        name.add_surname(Surname())
        name.set_primary_surname(0)
        if family.get_relationship() != FamilyRelType.UNMARRIED:
            # for each child, find one with a last name
            for ref in family.get_child_ref_list():
                child = db.get_person_from_handle(ref.ref)
                if child:
                    preset_name(child, name)
                    return name
        return name

    def mothers_name_from_child(self, db, family):
        """
        If family is unmarried, get the surname from a child. Else, return empty name.
        """
        name = Name()
        # the editor requires a surname
        name.add_surname(Surname())
        name.set_primary_surname(0)
        if family.get_relationship() == FamilyRelType.UNMARRIED:
            # for each child, find one with a last name
            for ref in family.get_child_ref_list():
                child = db.get_person_from_handle(ref.ref)
                if child:
                    preset_name(child, name)
                    return name
        return name

    def childs_name(self, db, family):
        """
        If family is unmarried, child inherits name from mother. Otherwise, child inherits name from father.
        """
        name = Name()
        name.add_surname(Surname())
        name.set_primary_surname(0)

        if family.get_relationship() == FamilyRelType.UNMARRIED:
            mother_handle = family.get_mother_handle()
            if mother_handle:
                mother = db.get_person_from_handle(mother_handle)
                preset_name(mother, name)
        else:
            father_handle = family.get_father_handle()
            if father_handle:
                father = db.get_person_from_handle(father_handle)
                preset_name(father, name)

        return name

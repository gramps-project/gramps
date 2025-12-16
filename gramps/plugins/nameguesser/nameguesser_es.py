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
        Usually, the child's first surname is the father's surname.
        """
        name = Name()
        # the editor requires a surname
        surname = Surname()
        # for each child, find one with a last name
        for ref in family.get_child_ref_list():
            child = db.get_person_from_handle(ref.ref)
            if child:
                child_name = child.get_primary_name()
                surname_list = child_name.get_surname_list()
                if len(surname_list) > 0:
                    surname = surname_list[0]
                    # set surname to patrilineal because he probably gave his patrilineal surname to his child
                    surname.origintype = NameOriginType(NameOriginType.PATRILINEAL)
        name.add_surname(surname)
        name.set_primary_surname(0)
        return name

    def mothers_name_from_child(self, db, family):
        """
        Usually, the child's second surname is the mother's surname.
        """
        name = Name()
        # the editor requires a surname
        surname = Surname()
        # for each child, find one with a last name
        for ref in family.get_child_ref_list():
            child = db.get_person_from_handle(ref.ref)
            if child:
                child_name = child.get_primary_name()
                surname_list = child_name.get_surname_list()
                if len(surname_list) > 1:
                    surname = surname_list[1]
                    # set surname to patrilineal because she probably gave her patrilineal surname to her child
                    surname.origintype = NameOriginType(NameOriginType.PATRILINEAL)
        name.add_surname(surname)
        name.set_primary_surname(0)
        return name

    def childs_name(self, db, family):
        """
        Child inherits name from father and mother
        """
        name = Name()
        # the editor requires a surname
        name.add_surname(Surname())
        name.set_primary_surname(0)
        if family:
            father_handle = family.get_father_handle()
            father = db.get_person_from_handle(father_handle) if father_handle else None
            mother_handle = family.get_mother_handle()
            mother = db.get_person_from_handle(mother_handle) if mother_handle else None
            if not father and not mother:
                return name
            if not father:
                preset_name(mother, name)
                return name
            if not mother:
                preset_name(father, name)
                return name
            # we take first surname, and keep that
            mothername = Name()
            fathername = Name()
            preset_name(mother, mothername)
            preset_name(father, fathername)
            mothersurname = mothername.get_surname_list()[0]
            mothersurname.set_primary(False)
            mothersurname.origintype = NameOriginType(NameOriginType.MATRILINEAL)
            fathersurname = fathername.get_surname_list()[0]
            fathersurname.set_primary(True)
            fathersurname.origintype = NameOriginType(NameOriginType.PATRILINEAL)
            name.set_surname_list([fathersurname, mothersurname])
            return name
        else:
            return name

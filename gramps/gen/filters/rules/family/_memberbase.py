#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2006  Donald N. Allingham
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

"""
Set of wrappers for family filter rules based on personal rules.

Any rule that matches family based on personal rule applied
to father, mother, or any child, just needs to do two things:
> Set the class attribute 'base_class' to the personal rule
> Set apply method to be an appropriate wrapper below
Example:
in the class body, outside any method:
>    base_class = SearchName
>    apply = child_base
"""

# -------------------------------------------------------------------------
#
# Typing modules
#
# -------------------------------------------------------------------------

from gramps.gen.lib import Family
from gramps.gen.db import Database

from typing import Type, TypeVar

T = TypeVar("T")

def get_father_base(base_class) -> Type[T]:
    class FatherBase(base_class):
        def apply_to_one(self, db: Database, family: Family) -> bool: # type: ignore[override]
            father_handle = family.father_handle
            if father_handle:
                father = db.get_person_from_handle(father_handle)
                if father:
                    return super().apply_to_one(db, father)
                else:
                    return False
            return False
    return FatherBase


def get_child_base(base_class) -> Type[T]:
    class ChildBase(base_class):
        def apply_to_one(self, db: Database, family: Family) -> bool: # type: ignore[override]
            for child_ref in family.child_ref_list:
                child = db.get_person_from_handle(child_ref.ref)
                if super().apply_to_one(db, child):
                    return True
            return False
    return ChildBase


def get_mother_base(base_class) -> Type[T]:
    class MotherBase(base_class):
        def apply_to_one(self, db: Database, family: Family) -> bool: # type: ignore[override]
            mother_handle = family.mother_handle
            if mother_handle:
                mother = db.get_person_from_handle(mother_handle)
                if mother:
                    return super().apply_to_one(db, mother)
                else:
                    return False
            return False
    return MotherBase

#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2010  Michiel D. Nauta
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
Provide merge capabilities for families.
"""

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ..db import DbTxn
from ..const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext
from ..errors import MergeError
from . import MergePersonQuery


# -------------------------------------------------------------------------
#
# MergeFamilyQuery
#
# -------------------------------------------------------------------------
class MergeFamilyQuery:
    """
    Create database query to merge two families.
    """

    def __init__(self, database, phoenix, titanic, phoenix_fh=None, phoenix_mh=None):
        self.database = database
        self.phoenix = phoenix
        self.titanic = titanic
        if phoenix_fh is None:
            self.phoenix_fh = self.phoenix.get_father_handle()
        else:
            self.phoenix_fh = phoenix_fh
        if phoenix_mh is None:
            self.phoenix_mh = self.phoenix.get_mother_handle()
        else:
            self.phoenix_mh = phoenix_mh

        if self.phoenix.get_father_handle() == self.phoenix_fh:
            self.titanic_fh = self.titanic.get_father_handle()
            self.father_swapped = False
        else:
            assert self.phoenix_fh == self.titanic.get_father_handle()
            self.titanic_fh = self.phoenix.get_father_handle()
            self.father_swapped = True
        if self.phoenix.get_mother_handle() == self.phoenix_mh:
            self.titanic_mh = self.titanic.get_mother_handle()
            self.mother_swapped = False
        else:
            assert self.phoenix_mh == self.titanic.get_mother_handle()
            self.titanic_mh = self.phoenix.get_mother_handle()
            self.mother_swapped = True

    def merge_person(self, phoenix_person, titanic_person, parent, trans):
        """
        Merge two persons even if they are None; no families are merged!
        """
        new_handle = self.phoenix.get_handle()
        old_handle = self.titanic.get_handle()

        if parent == "father":
            swapped = self.father_swapped
            family_add_person_handle = (
                self.phoenix if swapped else self.titanic
            ).set_father_handle
        elif parent == "mother":
            swapped = self.mother_swapped
            family_add_person_handle = (
                self.phoenix if swapped else self.titanic
            ).set_mother_handle
        else:
            raise ValueError(_("A parent should be a father or mother."))

        if phoenix_person is None:
            if titanic_person is not None:
                raise MergeError(
                    """When merging people where one person """
                    """doesn't exist, that "person" must be the person that """
                    """will be deleted from the database."""
                )
            return
        elif titanic_person is None:
            if swapped:
                if any(
                    childref.get_reference_handle() == phoenix_person.get_handle()
                    for childref in self.phoenix.get_child_ref_list()
                ):
                    raise MergeError(
                        _(
                            "A parent and child cannot be merged. "
                            "To merge these people, you must first break the "
                            "relationship between them."
                        )
                    )

                phoenix_person.add_family_handle(new_handle)
                family_add_person_handle(phoenix_person.get_handle())
                self.database.commit_family(self.phoenix, trans)
            else:
                if any(
                    childref.get_reference_handle() == phoenix_person.get_handle()
                    for childref in self.titanic.get_child_ref_list()
                ):
                    raise MergeError(
                        _(
                            "A parent and child cannot be merged. "
                            "To merge these people, you must first break the "
                            "relationship between them."
                        )
                    )

                phoenix_person.add_family_handle(old_handle)
                family_add_person_handle(phoenix_person.get_handle())
                self.database.commit_family(self.titanic, trans)

            self.database.commit_person(phoenix_person, trans)
        else:
            query = MergePersonQuery(self.database, phoenix_person, titanic_person)
            query.execute(family_merger=False, trans=trans)

    def execute(self):
        """
        Merges two families into a single family.
        """
        new_handle = self.phoenix.get_handle()
        old_handle = self.titanic.get_handle()

        with DbTxn(_("Merge Family"), self.database) as trans:
            # commit family in case Phoenix GrampsID, relationship has changed
            self.database.commit_family(self.phoenix, trans)
            if self.phoenix_fh != self.titanic_fh:
                if self.phoenix_fh:
                    phoenix_father = self.database.get_person_from_handle(
                        self.phoenix_fh
                    )
                else:
                    phoenix_father = None
                if self.titanic_fh:
                    titanic_father = self.database.get_person_from_handle(
                        self.titanic_fh
                    )
                else:
                    titanic_father = None
                self.merge_person(phoenix_father, titanic_father, "father", trans)

            if self.phoenix_mh != self.titanic_mh:
                if self.phoenix_mh:
                    phoenix_mother = self.database.get_person_from_handle(
                        self.phoenix_mh
                    )
                else:
                    phoenix_mother = None
                if self.titanic_mh:
                    titanic_mother = self.database.get_person_from_handle(
                        self.titanic_mh
                    )
                else:
                    titanic_mother = None
                self.merge_person(phoenix_mother, titanic_mother, "mother", trans)
            # Reload families from db in case the merge_person above changed
            # them
            self.phoenix = self.database.get_family_from_handle(new_handle)
            self.titanic = self.database.get_family_from_handle(old_handle)

            if self.phoenix_fh:
                phoenix_father = self.database.get_person_from_handle(self.phoenix_fh)
            else:
                phoenix_father = None
            if self.phoenix_mh:
                phoenix_mother = self.database.get_person_from_handle(self.phoenix_mh)
            else:
                phoenix_mother = None
            self.phoenix.merge(self.titanic)
            self.database.commit_family(self.phoenix, trans)
            for childref in self.titanic.get_child_ref_list():
                child = self.database.get_person_from_handle(
                    childref.get_reference_handle()
                )
                if new_handle in child.parent_family_list:
                    child.remove_handle_references("Family", [old_handle])
                else:
                    child.replace_handle_reference("Family", old_handle, new_handle)
                self.database.commit_person(child, trans)
            if phoenix_father:
                phoenix_father.remove_family_handle(old_handle)
                self.database.commit_person(phoenix_father, trans)
            if phoenix_mother:
                phoenix_mother.remove_family_handle(old_handle)
                self.database.commit_person(phoenix_mother, trans)
            # replace the family in lds ordinances and notes
            for ref_obj, ref_handle in self.database.find_backlink_handles(
                old_handle, ["Person", "Note"]
            ):
                if ref_handle in (self.titanic_fh, self.titanic_mh):
                    continue
                obj = self.database.method("get_%s_from_handle", ref_obj)(ref_handle)
                assert obj.has_handle_reference("Family", old_handle)
                obj.replace_handle_reference("Family", old_handle, new_handle)
                if ref_handle != old_handle:
                    self.database.method("commit_%s", ref_obj)(obj, trans)

            self.database.remove_family(old_handle, trans)

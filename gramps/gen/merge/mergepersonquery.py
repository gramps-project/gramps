#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2010       Michiel D. Nauta
# Copyright (C) 2010       Jakim Friant
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
Provide merge capabilities for persons.
"""

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ..db import DbTxn
from ..const import GRAMPS_LOCALE as glocale
from ..errors import MergeError

_ = glocale.translation.sgettext


# -------------------------------------------------------------------------
#
# MergePersonQuery
#
# -------------------------------------------------------------------------
class MergePersonQuery:
    """
    Create database query to merge two persons.
    """

    def __init__(self, database, phoenix, titanic):
        self.database = database
        self.phoenix = phoenix
        self.titanic = titanic
        if self.check_for_spouse(self.phoenix, self.titanic):
            raise MergeError(
                _(
                    "Spouses cannot be merged. To merge these "
                    "people, you must first break the relationship"
                    " between them."
                )
            )
        if self.check_for_child(self.phoenix, self.titanic):
            raise MergeError(
                _(
                    "A parent and child cannot be merged. To merge "
                    "these people, you must first break the relatio"
                    "nship between them."
                )
            )

    def check_for_spouse(self, person1, person2):
        """Return if person1 and person2 are spouses of eachother."""
        fs1 = set(person1.get_family_handle_list())
        fs2 = set(person2.get_family_handle_list())
        return len(fs1.intersection(fs2)) != 0

    def check_for_child(self, person1, person2):
        """Return if person1 and person2 have a child-parent relationship."""
        fs1 = set(person1.get_family_handle_list())
        fp1 = set(person1.get_parent_family_handle_list())
        fs2 = set(person2.get_family_handle_list())
        fp2 = set(person2.get_parent_family_handle_list())
        return len(fs1.intersection(fp2)) != 0 or len(fs2.intersection(fp1))

    def merge_families(self, main_family_handle, family, trans):
        """
        Merge content of family into the family with handle main_family_handle.
        """
        new_handle = self.phoenix.get_handle() if self.phoenix else None
        old_handle = self.titanic.get_handle() if self.titanic else None
        family_handle = family.get_handle()
        main_family = self.database.get_family_from_handle(main_family_handle)
        main_family.merge(family)
        for childref in family.get_child_ref_list():
            child = self.database.get_person_from_handle(
                childref.get_reference_handle()
            )
            if main_family_handle in child.parent_family_list:
                child.remove_handle_references("Family", [family_handle])
            else:
                child.replace_handle_reference(
                    "Family", family_handle, main_family_handle
                )
            self.database.commit_person(child, trans)
        if self.phoenix:
            self.phoenix.remove_family_handle(family_handle)
            self.database.commit_person(self.phoenix, trans)
        family_father_handle = family.get_father_handle()
        spouse_handle = (
            family.get_mother_handle()
            if new_handle == family_father_handle
            else family_father_handle
        )
        if spouse_handle:
            spouse = self.database.get_person_from_handle(spouse_handle)
            if spouse:
                spouse.remove_family_handle(family_handle)
                self.database.commit_person(spouse, trans)
        # replace the family in lds ordinances
        for ref_obj, ref_handle in self.database.find_backlink_handles(
            family_handle, ["Person", "Note"]
        ):
            if ref_handle == old_handle:
                continue
            obj = self.database.method("get_%s_from_handle", ref_obj)(ref_handle)
            assert obj.has_handle_reference("Family", family_handle)
            obj.replace_handle_reference("Family", family_handle, main_family_handle)
            self.database.method("commit_%s", ref_obj)(obj, trans)
        self.database.remove_family(family_handle, trans)
        self.database.commit_family(main_family, trans)

    def execute(self, family_merger=True, trans=None):
        """
        Merges two persons into a single person.
        """
        if trans is None:
            with DbTxn(_("Merge Person"), self.database) as trans:
                return self.__execute(family_merger, trans)
        else:
            return self.__execute(family_merger, trans)

    def __execute(self, family_merger, trans):
        """
        Merges two persons into a single person; trans is compulsory.
        Returns True if all went well, False if we did not complete a full
                family merge, because of complex families
        """
        new_handle = self.phoenix.get_handle()
        old_handle = self.titanic.get_handle()

        self.phoenix.merge(self.titanic)
        self.database.commit_person(self.phoenix, trans)

        for ref_obj, handle in self.database.find_backlink_handles(
            old_handle, ["Person", "Note"]
        ):
            obj = self.database.method("get_%s_from_handle", ref_obj)(handle)
            assert obj.has_handle_reference("Person", old_handle)
            obj.replace_handle_reference("Person", old_handle, new_handle)
            if handle != old_handle:
                self.database.method("commit_%s", ref_obj)(obj, trans)

        for family_handle in self.phoenix.get_parent_family_handle_list():
            family = self.database.get_family_from_handle(family_handle)
            if family.has_handle_reference("Person", old_handle):
                family.replace_handle_reference("Person", old_handle, new_handle)
                self.database.commit_family(family, trans)

        family_merge_guard = False
        parent_list = []
        parent_list_orig = []
        family_merge_ok = True
        family_handle_list = self.phoenix.get_family_handle_list()[:]
        for family_handle in family_handle_list:
            family = self.database.get_family_from_handle(family_handle)
            parents = (family.get_father_handle(), family.get_mother_handle())
            parent_list_orig.append(parents)
            if family.has_handle_reference("Person", old_handle):
                family.replace_handle_reference("Person", old_handle, new_handle)
                if family_merger and parent_list_orig.count(parents) > 1:
                    # A person with multiple relations with the same spouse is
                    # about to be merged. This is beyond the capabilities of
                    # the merge routine. The family merge is skipped.
                    family_merge_ok = False
                parents = (family.get_father_handle(), family.get_mother_handle())
                # prune means merging families in this case.
                if family_merger and parents in parent_list and family_merge_ok:
                    # also merge when father_handle or mother_handle == None!
                    if family_merge_guard:
                        # Multiple families get merged.
                        # This is unusual, the merge is skipped.
                        family_merge_ok = False
                    else:
                        idx = parent_list.index(parents)
                        main_family_handle = family_handle_list[idx]
                        self.merge_families(main_family_handle, family, trans)
                        family_merge_guard = True
                        continue
                self.database.commit_family(family, trans)
            parent_list.append(parents)

        hp_hdl = self.database.get_default_handle()
        if (
            hp_hdl in (self.phoenix.get_handle(), self.titanic.get_handle())
            and hp_hdl != self.phoenix.get_handle()
        ):
            self.database.set_default_person_handle(self.phoenix.get_handle())

        self.database.remove_person(old_handle, trans)
        return family_merge_ok

#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2011       Robert Cheramy
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

#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
from ....const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from .. import Rule

#-------------------------------------------------------------------------
#
# RelatedWith
#
#-------------------------------------------------------------------------
class IsRelatedWith(Rule):
    """Rule that checks if a person is related to a specified person"""

    labels = [ _('ID:') ]
    name = _('People related to <Person>')
    category = _("Relationship filters")
    description = _("Matches people related to a specified person")

    def prepare(self, db, user):
        """prepare so the rule can be executed efficiently
           we build the list of people related to <person> here,
           so that apply is only a check into this list
        """
        self.db = db

        self.relatives = []
        self.add_relative(db.get_person_from_gramps_id(self.list[0]))

    def reset(self):
        self.relatives = []

    def apply(self, db, person):
        return person.handle in self.relatives


    def add_relative(self, start):
        """Non-recursive function that scans relatives and add them to self.relatives"""
        if not(start):
            return

        expand = [start]
        relatives = {}

        while expand:
            person = expand.pop()
            # Add the relative to the list
            if person is None or (person.handle in relatives):
                continue
            relatives[person.handle] = True

            for family_handle in person.get_parent_family_handle_list():
                family = self.db.get_family_from_handle(family_handle)
                if family:
            # Check Parents
                    for parent_handle in (family.get_father_handle(), family.get_mother_handle()):
                        if parent_handle:
                            expand.append(self.db.get_person_from_handle(parent_handle))
            # Check Sibilings
                    for child_ref in family.get_child_ref_list():
                        expand.append(self.db.get_person_from_handle(child_ref.ref))

            for family_handle in person.get_family_handle_list():
                family = self.db.get_family_from_handle(family_handle)
                if family:
            # Check Spouse
                    for parent_handle in (family.get_father_handle(), family.get_mother_handle()):
                        if parent_handle:
                            expand.append(self.db.get_person_from_handle(parent_handle))
            # Check Children
                    for child_ref in family.get_child_ref_list():
                        expand.append(self.db.get_person_from_handle(child_ref.ref))

        self.relatives = list(relatives.keys())
        return

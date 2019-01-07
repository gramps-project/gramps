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

#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
from ....const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
try:
    set()
except NameError:
    from sets import Set as set

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from .. import Rule

#-------------------------------------------------------------------------
#
# IsDescendantFamilyOf
#
#-------------------------------------------------------------------------
class IsDescendantFamilyOf(Rule):
    """Rule that checks for a person that is a descendant or the spouse
    of a descendant of a specified person"""

    labels = [ _('ID:'), _('Inclusive:') ]
    name = _('Descendant family members of <person>')
    category = _('Descendant filters')
    description = _("Matches people that are descendants or the spouse "
                    "of a descendant of a specified person")

    def prepare(self, db, user):
        self.db = db
        self.matches = set()
        self.root_person = db.get_person_from_gramps_id(self.list[0])
        self.add_matches(self.root_person)
        try:
            if int(self.list[1]):
                inclusive = True
            else:
                inclusive = False
        except IndexError:
            inclusive = True
        if not inclusive:
            self.exclude()

    def reset(self):
        self.matches = set()

    def apply(self,db,person):
        return person.handle in self.matches

    def add_matches(self,person):
        if not person:
            return

        # Add self
        expand = [person]

        while expand:
            person = expand.pop(0)
            if person is None or person.handle in self.matches:
                # if we have been here before, skip
                continue
            self.matches.add(person.handle)
            for family_handle in person.get_family_handle_list():
                family = self.db.get_family_from_handle(family_handle)
                if family:
                    # Add every child recursively
                    for child_ref in family.get_child_ref_list():
                        if child_ref:
                            expand.append(self.db.get_person_from_handle(child_ref.ref))
                    # Add spouse
                    if person.handle == family.get_father_handle():
                        spouse_handle = family.get_mother_handle()
                    else:
                        spouse_handle = family.get_father_handle()
                    self.matches.add(spouse_handle)

    def exclude(self):
        # This removes root person and his/her spouses from the matches set
        if not self.root_person: return
        self.matches.remove(self.root_person.handle)
        for family_handle in self.root_person.get_family_handle_list():
            family = self.db.get_family_from_handle(family_handle)
            if family:
                if self.root_person.handle == family.get_father_handle():
                    spouse_handle = family.get_mother_handle()
                else:
                    spouse_handle = family.get_father_handle()
                self.matches.remove(spouse_handle)

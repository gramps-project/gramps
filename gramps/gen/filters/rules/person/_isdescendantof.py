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

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
from ....const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from .. import Rule


# -------------------------------------------------------------------------
#
# IsDescendantOf
#
# -------------------------------------------------------------------------
class IsDescendantOf(Rule):
    """Rule that checks for a person that is a descendant
    of a specified person"""

    labels = [_("ID:"), _("Inclusive:")]
    name = _("Descendants of <person>")
    category = _("Descendant filters")
    description = _("Matches all descendants for the specified person")

    def prepare(self, db, user):
        self.db = db
        self.map = set()
        try:
            first = False if int(self.list[1]) else True
        except IndexError:
            first = True
        try:
            root_person = db.get_person_from_gramps_id(self.list[0])
            self.init_list(root_person, first)
        except:
            pass

    def reset(self):
        self.map.clear()

    def apply(self, db, person):
        return person.handle in self.map

    def init_list(self, person, first):
        if not person or person.handle in self.map:
            # if we have been here before, skip
            return
        if not first:
            self.map.add(person.handle)

        for fam_id in person.get_family_handle_list():
            fam = self.db.get_family_from_handle(fam_id)
            if fam:
                for child_ref in fam.get_child_ref_list():
                    self.init_list(self.db.get_person_from_handle(child_ref.ref), 0)

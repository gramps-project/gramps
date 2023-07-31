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
# IsAncestorOf
#
# -------------------------------------------------------------------------
class IsAncestorOf(Rule):
    """Rule that checks for a person that is an ancestor of a specified person"""

    labels = [_("ID:"), _("Inclusive:")]
    name = _("Ancestors of <person>")
    category = _("Ancestral filters")
    description = _("Matches people that are ancestors of a specified person")

    def prepare(self, db, user):
        """Assume that if 'Inclusive' not defined, assume inclusive"""
        self.db = db
        self.map = set()
        try:
            first = 0 if int(self.list[1]) else 1
        except IndexError:
            first = 1
        try:
            root_person = db.get_person_from_gramps_id(self.list[0])
            self.init_ancestor_list(db, root_person, first)
        except:
            pass

    def reset(self):
        self.map.clear()

    def apply(self, db, person):
        return person.handle in self.map

    def init_ancestor_list(self, db, person, first):
        if not person:
            return
        if person.handle in self.map:
            return
        if not first:
            self.map.add(person.handle)
        fam_id = person.get_main_parents_family_handle()
        if fam_id:
            fam = db.get_family_from_handle(fam_id)
            if fam:
                f_id = fam.get_father_handle()
                m_id = fam.get_mother_handle()

                if f_id:
                    self.init_ancestor_list(db, db.get_person_from_handle(f_id), 0)
                if m_id:
                    self.init_ancestor_list(db, db.get_person_from_handle(m_id), 0)

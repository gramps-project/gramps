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

try:
    set()
except:
    from sets import Set as set

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from .. import Rule


# -------------------------------------------------------------------------
#
# IsLessThanNthGenerationAncestorOfBookmarked
#
# -------------------------------------------------------------------------
class IsLessThanNthGenerationAncestorOfBookmarked(Rule):
    # Submitted by Wayne Bergeron
    """Rule that checks for a person that is an ancestor of bookmarked persons
    not more than N generations away"""

    labels = [_("Number of generations:")]
    name = _("Ancestors of bookmarked people not more " "than <N> generations away")
    category = _("Ancestral filters")
    description = _(
        "Matches ancestors of the people on the bookmark list "
        "not more than N generations away"
    )

    def prepare(self, db, user):
        self.db = db
        bookmarks = db.get_bookmarks().get()
        self.map = set()
        if len(bookmarks) == 0:
            self.apply = lambda db, p: False
        else:
            self.bookmarks = set(bookmarks)
            self.apply = self.apply_real
            for self.bookmarkhandle in self.bookmarks:
                self.init_ancestor_list(self.bookmarkhandle, 1)

    def init_ancestor_list(self, handle, gen):
        #        if p.get_handle() in self.map:
        #            loop_error(self.orig,p)
        if not handle or handle in self.map:
            # if been here already, skip
            return
        if gen:
            self.map.add(handle)
            if gen >= int(self.list[0]):
                return

        p = self.db.get_person_from_handle(handle)
        fam_id = p.get_main_parents_family_handle()
        if not fam_id:
            return
        fam = self.db.get_family_from_handle(fam_id)
        if fam:
            f_id = fam.get_father_handle()
            m_id = fam.get_mother_handle()

            if f_id:
                self.init_ancestor_list(f_id, gen + 1)
            if m_id:
                self.init_ancestor_list(m_id, gen + 1)

    def apply_real(self, db, person):
        return person.handle in self.map

    def reset(self):
        self.map.clear()

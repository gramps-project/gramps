#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Ian Davis
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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

from ....const import GRAMPS_LOCALE as glocale
from .. import Rule
from ....db import Database

_ = glocale.translation.gettext


# -------------------------------------------------------------------------
#
# HasDNATestWithTag
#
# -------------------------------------------------------------------------
class HasDNATestWithTag(Rule):
    """Rule that checks for a person with a DNA test that has a given tag."""

    labels = [_("Tag:")]
    name = _("People with a DNA test with the <tag>")
    description = _("Matches people linked to a DNA test that has the given tag")
    category = _("DNA test filters")

    def prepare(self, db: Database, user):
        self.person_handles: set[str] = set()
        tag = db.get_tag_from_name(self.list[0])
        if tag is None:
            return
        for dnatest in db.iter_dnatests():
            if dnatest.person_handle and tag.handle in dnatest.tag_list:
                self.person_handles.add(dnatest.person_handle)

    def apply_to_one(self, db: Database, person) -> bool:
        return person.handle in self.person_handles

#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2007  Donald N. Allingham
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
from ._matchesfilter import MatchesFilter


# -------------------------------------------------------------------------
#
# IsSpouseOfFilterMatch
#
# -------------------------------------------------------------------------
class IsSpouseOfFilterMatch(Rule):
    """Rule that checks for a person married to someone matching
    a filter"""

    labels = [_("Filter name:")]
    name = _("Spouses of <filter> match")
    description = _("Matches people married to anybody matching a filter")
    category = _("Family filters")

    def prepare(self, db, user):
        self.filt = MatchesFilter(self.list)
        self.filt.requestprepare(db, user)

    def apply(self, db, person):
        for family_handle in person.get_family_handle_list():
            family = db.get_family_from_handle(family_handle)
            if family:
                for spouse_id in [
                    family.get_father_handle(),
                    family.get_mother_handle(),
                ]:
                    if not spouse_id:
                        continue
                    if spouse_id == person.handle:
                        continue
                    if self.filt.apply(db, db.get_person_from_handle(spouse_id)):
                        return True
        return False

    def reset(self):
        self.filt.requestreset()

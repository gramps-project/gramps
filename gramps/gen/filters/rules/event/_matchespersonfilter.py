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
from .. import MatchesFilterBase


# -------------------------------------------------------------------------
#
# Typing modules
#
# -------------------------------------------------------------------------
from ....lib import Event
from ....db import Database


# -------------------------------------------------------------------------
#
# MatchesFilter
#
# -------------------------------------------------------------------------
class MatchesPersonFilter(MatchesFilterBase):
    """
    Rule that checks against another filter.

    This is a base rule for subclassing by specific objects.
    Subclasses need to define the namespace class attribute.

    """

    labels = [_("Person filter name:"), _("Include Family events:")]
    name = _("Events of persons matching the <person filter>")
    description = _(
        "Matches events of persons matched by the specified " "person filter name"
    )
    category = _("General filters")

    # we want to have this filter show person filters
    namespace = "Person"

    def prepare(self, db: Database, user):
        MatchesFilterBase.prepare(self, db, user)

        try:
            if int(self.list[1]):
                self.MPF_famevents = True
            else:
                self.MPF_famevents = False
        except IndexError:
            self.MPF_famevents = False

    def apply_to_one(self, db: Database, event: Event) -> bool:
        filt = self.find_filter()
        if filt:
            for classname, handle in db.find_backlink_handles(event.handle, ["Person"]):
                person = db.method("get_%_from_handle", classname)(handle)
                if filt.apply_to_one(db, person):
                    return True
            if self.MPF_famevents:
                # also include if family event of the person
                for classname, handle in db.find_backlink_handles(
                    event.handle, ["Family"]
                ):
                    family = db.get_family_from_handle(handle)
                    father = (
                        db.get_person_from_handle(family.father_handle)
                        if family
                        else None
                    )
                    if father and filt.apply_to_one(db, father):
                        return True
                    mother = db.get_person_from_handle(family.mother_handle)
                    if family.mother_handle and filt.apply_to_one(db, mother):
                        return True

        return False

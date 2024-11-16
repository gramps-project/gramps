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

    def prepare(self, db, user):
        MatchesFilterBase.prepare(self, db, user)

        try:
            if int(self.list[1]):
                self.MPF_famevents = True
            else:
                self.MPF_famevents = False
        except IndexError:
            self.MPF_famevents = False

    def apply_to_one(self, db, event_data):
        filt = self.find_filter()
        if filt:
            for classname, handle in db.find_backlink_handles(
                event_data["handle"], ["Person"]
            ):
                data = db.get_raw_person_data(handle)
                if filt.apply_to_one(db, data):
                    return True
            if self.MPF_famevents:
                # also include if family event of the person
                for classname, handle in db.find_backlink_handles(
                    event_data["handle"], ["Family"]
                ):
                    family_data = db.get_raw_family_data(handle)
                    if family_data["father_handle"]:
                        father_data = db.get_raw_person_data(
                            family_data["father_handle"]
                        )
                        if filt.apply_to_one(db, father_data):
                            return True
                    if family_data["mother_handle"]:
                        mother_data = db.get_raw_person_data(
                            family_data["mother_handle"]
                        )
                        if filt.apply_to_one(db, mother_data):
                            return True

        return False

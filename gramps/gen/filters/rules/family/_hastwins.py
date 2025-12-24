#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2013    Nick Hall
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

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from .. import Rule
from ....lib.childreftype import ChildRefType
from ....const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext


# -------------------------------------------------------------------------
#
# Typing modules
#
# -------------------------------------------------------------------------
from typing import cast

from ....lib import Family
from ....db import Database
from ....types import PersonHandle, EventHandle


# -------------------------------------------------------------------------
#
# HasTwins
#
# -------------------------------------------------------------------------
class HasTwins(Rule):
    """Rule that checks for a family with twins"""

    name = _("Families with twins")
    description = _("Matches families with twins")
    category = _("Child filters")

    def apply_to_one(self, db: Database, family: Family) -> bool:
        date_list = []
        for childref in family.child_ref_list:
            if int(childref.mrel.value) == ChildRefType.BIRTH:
                if childref.ref:
                    child = db.get_person_from_handle(cast(PersonHandle, childref.ref))
                    if child and 0 <= child.birth_ref_index < len(child.event_ref_list):
                        birthref = child.event_ref_list[child.birth_ref_index]
                        if birthref and birthref.ref:
                            birth = db.get_event_from_handle(
                                cast(EventHandle, birthref.ref)
                            )
                            sortval = birth.date.sortval
                            if sortval != 0:
                                if sortval in date_list:
                                    return True
                                else:
                                    date_list.append(sortval)
        return False

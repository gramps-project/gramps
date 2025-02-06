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
# Typing modules
#
# -------------------------------------------------------------------------
from ....lib import Person
from ....db import Database


# -------------------------------------------------------------------------
# "People without a birth date"
# -------------------------------------------------------------------------
class NoBirthdate(Rule):
    """People without a birth date"""

    name = _("People without a known birth date")
    description = _("Matches people without a known birthdate")
    category = _("General filters")

    def apply_to_one(self, db: Database, person: Person) -> bool:
        if 0 <= person.birth_ref_index < len(person.event_ref_list):
            birth_ref = person.event_ref_list[person.birth_ref_index]
            if not birth_ref:
                return True
            birth = db.get_event_from_handle(birth_ref.ref)
            if birth:
                birth_obj = birth.date
                if not birth_obj:
                    return True
                if birth_obj.sortval == 0:
                    return True
            return False
        else:
            return True

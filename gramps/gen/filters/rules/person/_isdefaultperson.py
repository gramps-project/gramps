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
from typing import Set
from ....lib import Person
from ....db import Database
from ....user import User


# -------------------------------------------------------------------------
#
# IsDefaultPerson
#
# -------------------------------------------------------------------------
class IsDefaultPerson(Rule):
    """Rule that checks for a default person in the database"""

    name = _("Home Person")
    category = _("General filters")
    description = _("Matches the Home Person")

    def prepare(self, db: Database, user: User):
        self.selected_handles: Set[str] = set()
        p: Person = db.get_default_person()
        if p:
            self.selected_handles.add(p.handle)

    def apply_to_one(self, db: Database, person: Person) -> bool:
        return person.handle in self.selected_handles

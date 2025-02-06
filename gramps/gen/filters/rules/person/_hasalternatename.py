#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2010  Gramps
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
# gen.filters.rules/Person/_HasAlternateName.py

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
#
# HasAlternateName
#
# -------------------------------------------------------------------------
class HasAlternateName(Rule):
    """Rule that checks an alternate name"""

    name = _("People with an alternate name")
    description = _("Matches people with an alternate name")
    category = _("General filters")

    def apply_to_one(self, db: Database, person: Person) -> bool:
        return True if person.alternate_names else False

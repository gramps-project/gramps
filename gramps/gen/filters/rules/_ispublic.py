#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2006  Donald N. Allingham
# Copyright (C) 2011       Doug Blank <doug.blank@gmail.com>
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
# Gramps modules
#
# -------------------------------------------------------------------------
from . import Rule
from ...const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext


# -------------------------------------------------------------------------
#
# Typing modules
#
# -------------------------------------------------------------------------
from ...lib.primaryobj import PrimaryObject
from ...db import Database


# -------------------------------------------------------------------------
# "People marked public"
# -------------------------------------------------------------------------
class IsPublic(Rule):
    """Objects not marked private."""

    name = "Objects not marked private"
    description = "Matches objects that are not indicated as private"
    category = _("General filters")

    def apply_to_one(self, db: Database, obj: PrimaryObject) -> bool:
        return not obj.private

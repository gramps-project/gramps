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
# IncompleteNames
#
# -------------------------------------------------------------------------
class IncompleteNames(Rule):
    """People with incomplete names"""

    name = _("People with incomplete names")
    description = _("Matches people with firstname or lastname missing")
    category = _("General filters")

    def apply(self, db, person):
        for name in [person.get_primary_name()] + person.get_alternate_names():
            if name.get_first_name().strip() == "":
                return True
            if name.get_surname_list():
                for surn in name.get_surname_list():
                    if surn.get_surname().strip() == "":
                        return True
            else:
                return True
        return False

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
from ....lib.childreftype import ChildRefType


# -------------------------------------------------------------------------
# "People who were adopted"
# -------------------------------------------------------------------------
class HaveAltFamilies(Rule):
    """People who were adopted"""

    name = _("Adopted people")
    description = _("Matches people who were adopted")
    category = _("Family filters")

    def apply(self, db, person):
        for fhandle in person.get_parent_family_handle_list():
            family = db.get_family_from_handle(fhandle)
            if family:
                ref = [
                    ref
                    for ref in family.get_child_ref_list()
                    if ref.ref == person.handle
                ]
                if (
                    ref[0].get_father_relation() == ChildRefType.ADOPTED
                    or ref[0].get_mother_relation() == ChildRefType.ADOPTED
                ):
                    return True
        return False

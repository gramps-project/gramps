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
# gen.filters.rules/Person/_HasNameType.py

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
from ....lib.nametype import NameType


# -------------------------------------------------------------------------
#
# HasNameType
#
# -------------------------------------------------------------------------
class HasNameType(Rule):
    """Rule that checks the type of name"""

    labels = [_("Name type:")]
    name = _("People with the <Name type>")
    description = _("Matches people with a type of name")
    category = _("General filters")

    def apply(self, db, person):
        if not self.list[0]:
            return False
        for name in [person.get_primary_name()] + person.get_alternate_names():
            specified_type = NameType()
            specified_type.set_from_xml_str(self.list[0])
            if name.get_type() == specified_type:
                return True
        return False

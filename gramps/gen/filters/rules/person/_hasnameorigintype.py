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
# gen.filters.rules/Person/_HasNameOriginType.py

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
from ....lib.nameorigintype import NameOriginType


# -------------------------------------------------------------------------
#
# HasNameOriginType
#
# -------------------------------------------------------------------------
class HasNameOriginType(Rule):
    """Rule that checks the type of Surname origin"""

    labels = [_("Surname origin type:")]
    name = _("People with the <Surname origin type>")
    description = _("Matches people with a surname origin")
    category = _("General filters")

    def apply(self, db, person):
        if not self.list[0]:
            return False
        for name in [person.get_primary_name()] + person.get_alternate_names():
            for surname in name.get_surname_list():
                specified_type = NameOriginType()
                specified_type.set_from_xml_str(self.list[0])
                if surname.get_origintype() == specified_type:
                    return True
        return False

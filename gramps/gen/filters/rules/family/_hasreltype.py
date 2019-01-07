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

#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
from ....const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from ....lib.familyreltype import FamilyRelType
from .. import Rule

#-------------------------------------------------------------------------
#
# HasAttribute
#
#-------------------------------------------------------------------------
class HasRelType(Rule):
    """Rule that checks for a person with a particular personal attribute"""

    labels = [ _('Relationship type:') ]
    name = _('Families with the relationship type')
    description = _("Matches families with the relationship type "
                    "of a particular value")
    category = _('General filters')

    def prepare(self, db, user):
        if self.list[0]:
            self.rtype = FamilyRelType()
            self.rtype.set_from_xml_str(self.list[0])
        else:
            self.rtype = None

    def apply(self, db, family):
        if self.rtype:
            if self.rtype.is_custom() and self.use_regex:
                if self.regex[0].search(str(family.get_relationship())) is None:
                    return False
            elif self.rtype != family.get_relationship():
                return False
        return True

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
from .. import Rule

#-------------------------------------------------------------------------
#
# HasFamilyAttribute
#
#-------------------------------------------------------------------------
class HasFamilyAttribute(Rule):
    """Rule that checks for a person with a particular family attribute"""

    labels = [ _('Family attribute:'), _('Value:') ]
    name = _('People with the family <attribute>')
    description = _("Matches people with the family attribute "
                    "of a particular value")
    category = _('General filters')
    allow_regex = True

    def apply(self,db,person):
        if not self.list[0]:
            return False
        for f_id in person.get_family_handle_list():
            f = db.get_family_from_handle(f_id)
            if not f:
                continue
            for attr in f.get_attribute_list():
                if attr:
                    name_match = self.list[0] == attr.get_type()
                    value_match = self.match_substring(1, attr.get_value())
                    if name_match and value_match:
                        return True
        return False

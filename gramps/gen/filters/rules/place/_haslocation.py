#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2012       Nick Hall
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from .. import Rule

from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.get_translation().gettext

#-------------------------------------------------------------------------
#
# HasLocation
#
#-------------------------------------------------------------------------
class HasLocation(Rule):
    """Rule that checks if a Place is at a specified Location"""

    labels      = [ _('Location:') ]
    name        = _('Place at <Location>')
    description = _("Matches places at a specified Location")
    category    = _('General filters')

    def prepare(self, db):
        self.children = []
        to_do = [self.list[0]]
        while to_do:
            for child in db.find_location_child_handles(to_do.pop()):
                to_do.append(child)
                self.children.append(child)

    def apply(self, db, obj):
        """
        apply the rule on the obj.
        return true if the rule passes, false otherwise.
        """
        return obj.get_main_location() in self.children

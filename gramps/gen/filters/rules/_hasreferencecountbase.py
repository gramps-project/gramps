#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007  Stephane Charette
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
from ...const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from . import Rule

#-------------------------------------------------------------------------
# "Objects with a certain reference count"
#-------------------------------------------------------------------------
class HasReferenceCountBase(Rule):
    """Objects with a reference count of <count>."""

    labels = [ _('Reference count must be:'), _('Reference count:')]
    name = 'Objects with a reference count of <count>'
    description = "Matches objects with a certain reference count"
    category = _('General filters')


    def prepare(self, db, user):
        # things we want to do just once, not for every handle
        if  self.list[0] == 'less than':
            self.count_type = 0
        elif self.list[0] == 'greater than':
            self.count_type = 2
        else:
            self.count_type = 1 # "equal to"

        self.userSelectedCount = int(self.list[1])


    def apply(self, db, obj):
        handle = obj.get_handle()
        count = 0
        for item in db.find_backlink_handles(handle):
            count += 1

        if self.count_type == 0:     # "less than"
            return count < self.userSelectedCount
        elif self.count_type == 2:   # "greater than"
            return count > self.userSelectedCount
        # "equal to"
        return count == self.userSelectedCount


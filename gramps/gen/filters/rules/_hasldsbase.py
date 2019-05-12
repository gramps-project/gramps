#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2008  Brian G. Matherly
# Copyright (C) 2008  Jerome Rapinat
# Copyright (C) 2008  Benny Malengier
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
# gen.filters.rules/_HasLDSBase.py

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
#
# HasLDSBase
#
#-------------------------------------------------------------------------
class HasLDSBase(Rule):
    """Rule that checks for object with a LDS event"""

    labels = [  _('Number of instances:'), _('Number must be:')]
    name = 'Objects with LDS events'
    description = "Matches objects with LDS events"
    category = _('General filters')

    def prepare(self, db, user):
        # things we want to do just once, not for every handle
        if  self.list[1] == 'less than':
            self.count_type = 0
        elif self.list[1] == 'greater than':
            self.count_type = 2
        else:
            self.count_type = 1 # "equal to"

        self.userSelectedCount = int(self.list[0])

    def apply(self, db, obj):
        count = len( obj.get_lds_ord_list())
        if self.count_type == 0:     # "less than"
            return count < self.userSelectedCount
        elif self.count_type == 2:   # "greater than"
            return count > self.userSelectedCount
        # "equal to"
        return count == self.userSelectedCount

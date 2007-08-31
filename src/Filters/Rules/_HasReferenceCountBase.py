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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from Filters.Rules._Rule import Rule

#-------------------------------------------------------------------------
# "Objects with a certain reference count"
#-------------------------------------------------------------------------
class HasReferenceCountBase(Rule):
    """Objects with a reference count of <count>"""

    labels      = [ _('Reference count must be:'), _('Reference count:')]
    name        = _('Objects with a reference count of <count>')
    description = _("Matches objects with a certain reference count")
    category    = _('General filters')


    def prepare(self,db):
        # things we want to do just once, not for every handle
        if  self.list[0] == _('lesser than'):
            self.countType = 0
        elif self.list[0] == _('greater than'):
            self.countType = 2
        else:
            self.countType = 1 # "equal to"

        self.userSelectedCount = int(self.list[1])


    def apply(self,db,object):
        handle = object.get_handle()
        count = 0
        for item in db.find_backlink_handles(handle):
            count += 1

        if self.countType == 0:     # "lesser than"
            return count < self.userSelectedCount
        elif self.countType == 2:   # "greater than"
            return count > self.userSelectedCount
        # "equal to"
        return count == self.userSelectedCount


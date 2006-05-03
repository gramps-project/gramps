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
from Filters import SystemFilters, CustomFilters
from _Rule import Rule

#-------------------------------------------------------------------------
#
# MatchesFilter
#
#-------------------------------------------------------------------------
class MatchesFilter(Rule):
    """Rule that checks against another filter"""

    labels      = [_('Filter name:')]
    name        = _('People matching the <filter>')
    description = _("Matches people macthed by the specified filter name")
    category    = _('General filters')

    def prepare(self,db):
        for filt in SystemFilters.get_filters():
            if filt.get_name() == self.list[0]:
                for rule in filt.flist:
                    rule.prepare(db)
        for filt in CustomFilters.get_filters():
            if filt.get_name() == self.list[0]:
                for rule in filt.flist:
                    rule.prepare(db)

    def reset(self):
        for filt in SystemFilters.get_filters():
            if filt.get_name() == self.list[0]:
                for rule in filt.flist:
                    rule.reset()
        for filt in CustomFilters.get_filters():
            if filt.get_name() == self.list[0]:
                for rule in filt.flist:
                    rule.reset()

    def apply(self,db,person):
        for filt in SystemFilters.get_filters():
            if filt.get_name() == self.list[0]:
                return filt.check(db,person.handle)
        for filt in CustomFilters.get_filters():
            if filt.get_name() == self.list[0]:
                return filt.check(db,person.handle)
        return False

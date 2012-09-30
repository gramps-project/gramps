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
from ...ggettext import gettext as _

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from .. import CustomFilters
from . import Rule

#-------------------------------------------------------------------------
#
# MatchesFilter
#
#-------------------------------------------------------------------------
class MatchesFilterBase(Rule):
    """
    Rule that checks against another filter.

    This is a base rule for subclassing by specific objects.
    Subclasses need to define the namespace class attribute.
    
    """

    labels      = [_('Filter name:')]
    name        = 'Objects matching the <filter>'
    description = "Matches objects matched by the specified filter name"
    category    = _('General filters')

    def prepare(self, db):
        if CustomFilters:
            filters = CustomFilters.get_filters_dict(self.namespace)
            if self.list[0] in filters:
                filt = filters[self.list[0]]
                for rule in filt.flist:
                    rule.requestprepare(db)

    def reset(self):
        if CustomFilters:
            filters = CustomFilters.get_filters_dict(self.namespace)
            if self.list[0] in filters:
                filt = filters[self.list[0]]
                for rule in filt.flist:
                    rule.requestreset()

    def apply(self, db, obj):
        if CustomFilters:
            filters = CustomFilters.get_filters_dict(self.namespace)
            if self.list[0] in filters:
                filt = filters[self.list[0]]
                return filt.check(db, obj.handle)
        return False
    
    def find_filter(self):
        """
        Return the selected filter or None.
        """
        if CustomFilters:
            filters = CustomFilters.get_filters_dict(self.namespace)
            if self.list[0] in filters:
                return filters[self.list[0]]
        return None

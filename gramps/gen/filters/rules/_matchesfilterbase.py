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
import logging
LOG = logging.getLogger(".filter")

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
# we need global variableCustomFilters, so we need to query gramps.gen.filters
# when we need this variable, not import it at the start!
import gramps.gen.filters
from . import Rule
from ...const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

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
    labels = [_('Filter name:')]
    name = 'Objects matching the <filter>'
    description = "Matches objects matched by the specified filter name"
    category = _('General filters')

    def prepare(self, db, user):
        if gramps.gen.filters.CustomFilters:
            filters = gramps.gen.filters.CustomFilters.get_filters_dict(self.namespace)
            if self.list[0] in filters:
                filt = filters[self.list[0]]
                for rule in filt.flist:
                    rule.requestprepare(db, user)
            else:
                LOG.warning(_("Can't find filter %s in the defined custom filters")
                                    % self.list[0])
        else:
            LOG.warning(_("Can't find filter %s in the defined custom filters")
                                    % self.list[0])

    def reset(self):
        if gramps.gen.filters.CustomFilters:
            filters = gramps.gen.filters.CustomFilters.get_filters_dict(self.namespace)
            if self.list[0] in filters:
                filt = filters[self.list[0]]
                for rule in filt.flist:
                    rule.requestreset()

    def apply(self, db, obj):
        if gramps.gen.filters.CustomFilters:
            filters = gramps.gen.filters.CustomFilters.get_filters_dict(self.namespace)
            if self.list[0] in filters:
                filt = filters[self.list[0]]
                return filt.check(db, obj.handle)
        return False

    def find_filter(self):
        """
        Return the selected filter or None.
        """
        if gramps.gen.filters.CustomFilters:
            filters = gramps.gen.filters.CustomFilters.get_filters_dict(self.namespace)
            if self.list[0] in filters:
                return filters[self.list[0]]
        return None

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

# $Id: _MatchesFilter.py 6932 2006-06-21 16:30:35Z dallingham $

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
import Filters
from _Rule import Rule

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
    name        = _('Objects matching the <filter>')
    description = _("Matches objects matched by the specified filter name")
    category    = _('General filters')

    def prepare(self,db):
	if Filters.SystemFilters:
	    for filt in Filters.SystemFilters.get_filters(self.namespace):
		if filt.get_name() == self.list[0]:
		    for rule in filt.flist:
			rule.prepare(db)
	if Filters.CustomFilters:
	    for filt in Filters.CustomFilters.get_filters(self.namespace):
		if filt.get_name() == self.list[0]:
		    for rule in filt.flist:
			rule.prepare(db)

    def reset(self):
	if Filters.SystemFilters:
	    for filt in Filters.SystemFilters.get_filters(self.namespace):
		if filt.get_name() == self.list[0]:
		    for rule in filt.flist:
			rule.reset()
	if Filters.CustomFilters:
	    for filt in Filters.CustomFilters.get_filters(self.namespace):
		if filt.get_name() == self.list[0]:
		    for rule in filt.flist:
			rule.reset()

    def apply(self,db,obj):
	if Filters.SystemFilters:
	    for filt in Filters.SystemFilters.get_filters(self.namespace):
		if filt.get_name() == self.list[0]:
		    return filt.check(db,obj.handle)
	if Filters.CustomFilters:
	    for filt in Filters.CustomFilters.get_filters(self.namespace):
		if filt.get_name() == self.list[0]:
		    return filt.check(db,obj.handle)
        return False
    
    def find_filter(self):
        ''' helper function that can be usefull, returning the filter
            selected or None
        '''
        if Filters.SystemFilters:
            for filt in Filters.SystemFilters.get_filters(self.namespace):
                if filt.get_name() == self.list[0]:
                    return filt
        if Filters.CustomFilters:
            for filt in Filters.CustomFilters.get_filters(self.namespace):
                if filt.get_name() == self.list[0]:
                    return filt
        return None

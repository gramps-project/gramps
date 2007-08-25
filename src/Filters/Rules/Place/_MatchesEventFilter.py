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
from Filters.Rules._MatchesFilterBase import MatchesFilterBase

#-------------------------------------------------------------------------
#
# MatchesFilter
#
#-------------------------------------------------------------------------
class MatchesEventFilter(MatchesFilterBase):
    """
    Rule that checks against another filter.

    This is a base rule for subclassing by specific objects.
    Subclasses need to define the namespace class attribute.
    """

    labels      = [_('Event filter name:')]
    name        = _('Places of events matching the <event filter>')
    description = _("Matches places where events happened that match the "
                    "specified event filter name")
    category    = _('General filters')
    # we want to have this filter show event filters
    namespace   = 'Event'


    def apply(self,db,event):
        filt = self.find_filter()
        if filt:
            for (classname, handle) in db.find_backlink_handles(event.get_handle(), ['Event']):
                if filt.check(db, handle):
                    return True
        return False

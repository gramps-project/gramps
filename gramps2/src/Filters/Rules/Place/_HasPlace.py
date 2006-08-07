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
from Filters.Rules._Rule import Rule

#-------------------------------------------------------------------------
#
# HasEvent
#
#-------------------------------------------------------------------------
class HasPlace(Rule):
    """Rule that checks for a place with a particular value"""


    labels      = [ _('Name:'), 
                    _('Church Parish:'), 
                    _('ZIP/Postal Code:'),
                    _('City:'), 
                    _('County:'), 
                    _('State:'), 
                    _('Country:'), 
                    ]
    name        = _('Places matching parameters')
    description = _("Matches places with particular parameters")
    category    = _('General filters')

    def apply(self,db,place):
        if not self.match_substring(0,place.get_title()):
            return False

        for loc in [place.main_loc] + place.alt_loc:
            if not loc:
                # Empty mail locaiton does not contradict any parameters
                return True

            if not self.match_substring(1,loc.get_parish()):
                continue

            if not self.match_substring(2,loc.get_postal_code()):
                continue

            if not self.match_substring(3,loc.get_city()):
                continue

            if not self.match_substring(4,loc.get_county()):
                continue

            if not self.match_substring(5,loc.get_state()):
                continue

            if not self.match_substring(6,loc.get_country()):
                continue

            return True

        return False

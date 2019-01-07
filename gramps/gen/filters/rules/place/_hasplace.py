#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2006  Donald N. Allingham
# Copyright (C) 2008       Gary Burton
# Copyright (C) 2010       Nick Hall
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
from ....const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from .. import Rule
from ....lib import PlaceType
from ....utils.location import get_locations

#-------------------------------------------------------------------------
#
# HasPlace
#
#-------------------------------------------------------------------------
class HasPlace(Rule):
    """Rule that checks for a place with a particular value"""

    labels = [ _('Title:'),
                    _('Street:'),
                    _('Locality:'),
                    _('City:'),
                    _('County:'),
                    _('State:'),
                    _('Country:'),
                    _('ZIP/Postal Code:'),
                    _('Church Parish:'),
                    ]
    name = _('Places matching parameters')
    description = _("Matches places with particular parameters")
    category = _('General filters')
    allow_regex = True

    TYPE2FIELD = {PlaceType.STREET: 1,
                  PlaceType.LOCALITY: 2,
                  PlaceType.CITY: 3,
                  PlaceType.COUNTY: 4,
                  PlaceType.STATE: 5,
                  PlaceType.COUNTRY: 6,
                  PlaceType.PARISH: 8}

    def apply(self, db, place):
        if not self.match_substring(0, place.get_title()):
            return False

        if not self.match_substring(7, place.get_code()):
            return False

        # If no location data was given then we're done: match
        if not any(self.list[1:7] + [self.list[8]]):
            return True

        for location in get_locations(db, place):
            if self.check(location):
                return True

        return False

    def check(self, location):
        """
        Check each location for a match.
        """
        for place_type, field in self.TYPE2FIELD.items():
            name_list = location.get(place_type, [''])
            if not self.match_name(field, name_list):
                return False
        return True

    def match_name(self, field, name_list):
        """
        Match any name in a list of names.
        """
        for name in name_list:
            if self.match_substring(field, name):
                return True
        return False
